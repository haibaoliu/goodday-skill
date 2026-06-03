#!/usr/bin/env python3
"""Brain health scanner — deterministic state gathering for brain-maintain.

Produces a structured JSON health report covering orphans, broken back-links,
frontmatter integrity, stale content, page stats, and pattern candidates.
The LLM consumes this report and makes semantic decisions (which orphans to
link/delete, which candidates constitute a real pattern, etc.).

Usage:
  python brain_health.py [--brain-dir ~/.hermes/brain] [--stale-days 90] [--recent-days 7]
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

# ── helpers ──────────────────────────────────────────────────────────


def _find_pages(brain: Path) -> list[Path]:
    """Return all .md pages, excluding system files."""
    exclude = {"BRAIN_FORMAT.md", "USER.md", "SOUL.md", "README.md"}
    pages: list[Path] = []
    for f in brain.rglob("*.md"):
        if f.name not in exclude:
            pages.append(f)
    return pages


def _parse_frontmatter(path: Path) -> dict[str, Any] | None:
    """Extract YAML frontmatter as a dict. Returns None if missing/malformed."""
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return None
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    try:
        import yaml as _yaml
        return _yaml.safe_load(parts[1]) or {}
    except Exception:
        return {}


def _slug(path: Path) -> str:
    return path.stem


def _age_days(path: Path) -> int:
    mtime = path.stat().st_mtime
    return int((datetime.now() - datetime.fromtimestamp(mtime)).total_seconds() / 86400)


def _extract_links(text: str) -> set[str]:
    """Extract wikilink-style [[target]] and markdown [text](target) references."""
    refs: set[str] = set()
    # [[Page Name]] or [[Page Name|alias]]
    for m in re.finditer(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", text):
        refs.add(m.group(1).strip().lower().replace(" ", "-"))
    # [text](path/to/page.md)
    for m in re.finditer(r"\[([^\]]*)\]\(([^)]+\.md)\)", text):
        target = Path(m.group(2)).stem.lower()
        refs.add(target)
    # [text](../category/page.md)
    for m in re.finditer(r"\[([^\]]*)\]\(\.\./([^)]+\.md)\)", text):
        target = Path(m.group(2)).stem.lower()
        refs.add(target)
    return refs


# ── checks ───────────────────────────────────────────────────────────


def _check_orphans(brain: Path, pages: list[Path]) -> list[dict]:
    """Find pages not referenced by any other page."""
    # Build reference map: which pages reference which slugs
    all_slugs = {_slug(p): str(p) for p in pages if _slug(p)}
    referencers: dict[str, set[str]] = {s: set() for s in all_slugs}

    for page in pages:
        try:
            text = page.read_text(encoding="utf-8")
        except Exception:
            continue
        source_slug = _slug(page)
        refs = _extract_links(text)
        for ref in refs:
            if ref in referencers and ref != source_slug:
                referencers[ref].add(source_slug)

    orphans: list[dict] = []
    for slug, path in sorted(all_slugs.items()):
        if not referencers.get(slug):
            orphans.append({
                "slug": slug,
                "path": str(path),
                "category": str(Path(path).parent.relative_to(brain)),
                "age_days": _age_days(Path(path)),
            })
    return orphans


def _check_backlinks(brain: Path, pages: list[Path], recent_days: int) -> list[dict]:
    """Check recent pages for missing back-links from mentioned entities."""
    cutoff = datetime.now() - timedelta(days=recent_days)
    issues: list[dict] = []

    for page in pages:
        mtime = datetime.fromtimestamp(page.stat().st_mtime)
        if mtime < cutoff:
            continue
        slug = _slug(page)
        try:
            text = page.read_text(encoding="utf-8")
        except Exception:
            continue
        refs = _extract_links(text)
        fm = _parse_frontmatter(page)

        # Check if referenced pages have a back-link to this page
        for ref in refs:
            ref_path = brain / f"{ref}.md"
            if not ref_path.exists():
                # Try subdirectory search
                candidates = list(brain.rglob(f"{ref}.md"))
                if not candidates:
                    continue
                ref_path = candidates[0]
            try:
                ref_text = ref_path.read_text(encoding="utf-8")
            except Exception:
                continue
            ref_links = _extract_links(ref_text)
            if slug not in ref_links:
                issues.append({
                    "source": str(page.relative_to(brain)),
                    "source_slug": slug,
                    "mentions": ref,
                    "target": str(ref_path.relative_to(brain)),
                    "has_backlink": False,
                })

        # Also check links: field in frontmatter
        if fm and fm.get("links"):
            for link in (fm["links"] if isinstance(fm["links"], list) else []):
                link_target = Path(str(link)).stem
                link_path = brain / f"{link_target}.md"
                candidates = list(brain.rglob(f"{link_target}.md"))
                if not candidates:
                    continue
                link_path = candidates[0]
                try:
                    link_text = link_path.read_text(encoding="utf-8")
                except Exception:
                    continue
                link_links = _extract_links(link_text)
                if slug not in link_links:
                    # Avoid duplicate entries
                    if not any(i["target"] == str(link_path.relative_to(brain)) and i["source_slug"] == slug for i in issues):
                        issues.append({
                            "source": str(page.relative_to(brain)),
                            "source_slug": slug,
                            "mentions": link_target,
                            "target": str(link_path.relative_to(brain)),
                            "has_backlink": False,
                            "via": "frontmatter.links",
                        })

    return issues


def _check_frontmatter(pages: list[Path], brain: Path) -> list[dict]:
    """Check frontmatter integrity on all pages."""
    issues: list[dict] = []
    for page in pages:
        fm = _parse_frontmatter(page)
        rel = str(page.relative_to(brain))
        if fm is None:
            issues.append({
                "path": rel,
                "issue": "missing_frontmatter",
            })
            continue
        missing_fields = []
        for field in ("title", "type", "date", "tags"):
            if field not in fm or not fm[field]:
                missing_fields.append(field)
        if missing_fields:
            issues.append({
                "path": rel,
                "issue": "incomplete_frontmatter",
                "missing_fields": missing_fields,
            })
    return issues


def _check_stale(brain: Path, pages: list[Path], stale_days: int) -> list[dict]:
    """Find pages not updated in stale_days days."""
    stale: list[dict] = []
    for page in pages:
        age = _age_days(page)
        if age > stale_days:
            fm = _parse_frontmatter(page)
            page_type = (fm or {}).get("type", "unknown")
            if page_type in ("pattern", "concept"):
                stale.append({
                    "path": str(page.relative_to(brain)),
                    "slug": _slug(page),
                    "age_days": age,
                    "type": page_type,
                })
    return sorted(stale, key=lambda x: x["age_days"], reverse=True)


def _check_pattern_candidates(brain: Path) -> list[dict]:
    """Scan reflections/ for themes with >=3 occurrences across >=7 days."""
    reflections_dir = brain / "reflections"
    if not reflections_dir.is_dir():
        return []

    # Collect all reflections
    refl_files = list(reflections_dir.glob("*.md"))
    if len(refl_files) < 3:
        return []

    # Extract tags and themes from each reflection
    theme_groups: dict[str, list[dict]] = {}
    for f in refl_files:
        fm = _parse_frontmatter(f)
        if not fm:
            continue
        tags = fm.get("tags") or []
        title = fm.get("title") or _slug(f)
        date_str = fm.get("date") or ""
        mtime = f.stat().st_mtime
        mdate = datetime.fromtimestamp(mtime)

        for tag in (tags if isinstance(tags, list) else [tags]):
            tag = str(tag).lower().strip()
            if not tag or tag in ("reflection",):
                continue
            theme_groups.setdefault(tag, []).append({
                "slug": _slug(f),
                "title": str(title),
                "date": date_str,
                "timestamp": mdate.isoformat(),
                "path": str(f.relative_to(brain)),
            })

    # Find candidates: >=3 occurrences, >=7 day span
    candidates: list[dict] = []
    for tag, items in theme_groups.items():
        if len(items) < 3:
            continue
        dates = [datetime.fromisoformat(i["timestamp"]) for i in items]
        span = (max(dates) - min(dates)).days
        if span >= 7:
            candidates.append({
                "theme": tag,
                "count": len(items),
                "span_days": span,
                "sources": sorted(items, key=lambda x: x["timestamp"]),
            })

    return sorted(candidates, key=lambda x: x["count"], reverse=True)


def _page_stats(brain: Path, pages: list[Path]) -> dict:
    """Count pages by top-level directory."""
    stats: dict[str, int] = {}
    for page in pages:
        try:
            cat = str(page.relative_to(brain)).split("/")[0]
        except ValueError:
            cat = "root"
        stats[cat] = stats.get(cat, 0) + 1
    total = sum(stats.values())
    return {
        "total": total,
        "by_category": dict(sorted(stats.items())),
    }


# ── main ─────────────────────────────────────────────────────────────


def run(brain_dir: str, stale_days: int = 90, recent_days: int = 7) -> dict:
    brain = Path(brain_dir).expanduser().resolve()
    if not brain.is_dir():
        return {"error": f"Brain directory not found: {brain}"}

    pages = _find_pages(brain)

    report: dict[str, Any] = {
        "brain": str(brain),
        "generated": datetime.now().isoformat(),
        "stats": _page_stats(brain, pages),
        "orphans": _check_orphans(brain, pages),
        "backlink_issues": _check_backlinks(brain, pages, recent_days),
        "frontmatter_issues": _check_frontmatter(pages, brain),
        "stale_content": _check_stale(brain, pages, stale_days),
        "pattern_candidates": _check_pattern_candidates(brain),
        "summary": {},
    }

    # Summary
    report["summary"] = {
        "total_pages": report["stats"]["total"],
        "orphans": len(report["orphans"]),
        "backlink_issues": len(report["backlink_issues"]),
        "frontmatter_issues": len(report["frontmatter_issues"]),
        "stale_items": len(report["stale_content"]),
        "pattern_candidates": len(report["pattern_candidates"]),
        "health_score": "healthy" if (
            len(report["orphans"]) == 0
            and len(report["backlink_issues"]) <= 2
            and len(report["frontmatter_issues"]) == 0
        ) else "needs_attention",
    }

    return report


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Brain health scanner")
    parser.add_argument("--brain-dir", default=os.path.expanduser("~/.hermes/brain"))
    parser.add_argument("--stale-days", type=int, default=90)
    parser.add_argument("--recent-days", type=int, default=7)
    parser.add_argument("--json", action="store_true", default=True,
                        help="Output JSON (default)")
    parser.add_argument("--summary", action="store_true",
                        help="Output summary only")
    args = parser.parse_args()

    result = run(args.brain_dir, args.stale_days, args.recent_days)

    if args.summary:
        print(json.dumps(result.get("summary", {}), indent=2, ensure_ascii=False))
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
