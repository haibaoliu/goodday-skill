#!/usr/bin/env python3
"""Brain query scanner — deterministic search + contradiction candidate detection.

Handles keyword search, type/date filtering, frontmatter parsing, Facts table
extraction, candidate contradiction pair detection, and Book Mirror context
collection.  The LLM consumes the structured output and makes semantic decisions
(relevance ranking, contradiction judgment, result summarization).

Usage:
  python brain_query.py search <keyword> [--type people|reflections|patterns|...] [--recent-days 14]
  python brain_query.py contradictions [--brain-dir ~/.hermes/brain]
  python brain_query.py context [--brain-dir ~/.hermes/brain] [--keyword <theme>] [--recent-days 14]
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
    exclude = {"BRAIN_FORMAT.md", "USER.md", "SOUL.md", "README.md"}
    return [f for f in brain.rglob("*.md") if f.name not in exclude]


def _parse_frontmatter(path: Path) -> dict[str, Any] | None:
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


def _read_body(path: Path) -> str:
    """Return page body text (everything after frontmatter)."""
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return ""
    if text.startswith("---"):
        parts = text.split("---", 2)
        return parts[2] if len(parts) >= 3 else text
    return text


def _extract_facts(text: str) -> list[dict]:
    """Extract Facts table rows from markdown.

    Looks for markdown tables or `### Facts` sections with bullet lists.
    """
    facts: list[dict] = []

    # Pattern 1: Markdown table rows (| key | value | source | confidence |)
    table_rows = re.findall(
        r"\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|",
        text,
    )
    for row in table_rows:
        if len(row) >= 4 and not any(
            h in row[0].lower() for h in ("key", "fact", "---", "属性")
        ):
            facts.append({
                "key": row[0].strip(),
                "value": row[1].strip(),
                "source": row[2].strip(),
                "confidence": row[3].strip(),
            })

    # Pattern 2: Bullet list under ### Facts
    facts_section = re.search(
        r"(?:###?\s*Facts?|##?\s*事实)[\s\S]*?(?=\n##|\n---|\Z)", text
    )
    if facts_section:
        bullets = re.findall(
            r"[-*]\s+\*\*(.+?)\*\*:\s*(.+?)(?:\s*\((.+?)\))?\s*$",
            facts_section.group(0),
            re.MULTILINE,
        )
        for b in bullets:
            facts.append({
                "key": b[0].strip(),
                "value": b[1].strip(),
                "source": b[2].strip() if len(b) > 2 and b[2] else "brain page",
                "confidence": "high",
            })

    return facts


# ── commands ─────────────────────────────────────────────────────────


def _cmd_search(
    brain: Path,
    keyword: str,
    page_type: str | None = None,
    recent_days: int | None = None,
) -> dict:
    """Keyword search across brain pages with optional filters."""
    pages = _find_pages(brain)
    results: list[dict] = []
    kw_lower = keyword.lower()

    for page in pages:
        # Type filter
        if page_type:
            try:
                cat = str(page.relative_to(brain)).split("/")[0]
            except ValueError:
                cat = "root"
            if cat != page_type:
                continue

        # Date filter
        if recent_days:
            age = (datetime.now() - datetime.fromtimestamp(page.stat().st_mtime)).days
            if age > recent_days:
                continue

        # Content match
        try:
            text = page.read_text(encoding="utf-8")
        except Exception:
            continue
        if kw_lower not in text.lower():
            continue

        fm = _parse_frontmatter(page)
        rel = str(page.relative_to(brain))
        cat = rel.split("/")[0] if "/" in rel else "root"

        # Find matching lines for context
        match_lines: list[str] = []
        for i, line in enumerate(text.split("\n")):
            if kw_lower in line.lower():
                match_lines.append(f"L{i+1}: {line.strip()[:120]}")

        results.append({
            "path": rel,
            "category": cat,
            "title": (fm or {}).get("title", page.stem),
            "type": (fm or {}).get("type", "unknown"),
            "date": (fm or {}).get("date", ""),
            "tags": (fm or {}).get("tags", []),
            "match_lines": match_lines[:5],  # top 5 matches
        })

    # Sort by recency (date descending)
    results.sort(key=lambda r: r.get("date") or "", reverse=True)

    return {
        "query": keyword,
        "filters": {"type": page_type, "recent_days": recent_days},
        "total_matches": len(results),
        "results": results,
    }


def _cmd_contradictions(brain: Path) -> dict:
    """Detect candidate contradiction pairs across brain pages.

    Finds pages with overlapping fact keys (same subject, different values)
    and surfaces them for LLM judgment.
    """
    pages = _find_pages(brain)

    # Collect all facts, grouped by normalized key
    facts_by_key: dict[str, list[dict]] = {}

    for page in pages:
        body = _read_body(page)
        facts = _extract_facts(body)
        for f in facts:
            key = f["key"].lower().strip().rstrip("s")  # normalize: singular/plural
            facts_by_key.setdefault(key, []).append({
                **f,
                "page": str(page.relative_to(brain)),
                "page_title": (_parse_frontmatter(page) or {}).get("title", page.stem),
            })

    # Find keys with multiple distinct values
    candidates: list[dict] = []
    for key, entries in facts_by_key.items():
        if len(entries) < 2:
            continue
        # Group by value
        values: dict[str, list[dict]] = {}
        for e in entries:
            val_norm = e["value"].lower().strip()
            values.setdefault(val_norm, []).append(e)

        if len(values) >= 2:
            candidate = {
                "key": key,
                "groups": [],
                "conflict_likelihood": "low" if len(entries) <= 2 else "medium",
            }
            for val, group in values.items():
                candidate["groups"].append({
                    "value": val,
                    "count": len(group),
                    "sources": [
                        {
                            "page": g["page"],
                            "page_title": g.get("page_title", ""),
                            "source": g.get("source", ""),
                            "confidence": g.get("confidence", "unknown"),
                        }
                        for g in group
                    ],
                })

            # Bump likelihood if confidences differ significantly
            confidences = {g.get("confidence", "unknown") for e in entries for g in [e]}
            if "high" in confidences and ("low" in confidences or "medium" in confidences):
                candidate["conflict_likelihood"] = "high"

            candidates.append(candidate)

    # Sort by likelihood
    candidates.sort(key=lambda c: {"high": 0, "medium": 1, "low": 2}.get(c["conflict_likelihood"], 3))

    return {
        "total_facts": sum(len(v) for v in facts_by_key.values()),
        "unique_keys": len(facts_by_key),
        "candidates": candidates,
        "summary": f"{len(candidates)} candidate contradictions ({sum(1 for c in candidates if c['conflict_likelihood']=='high')} high likelihood)",
    }


def _cmd_context(
    brain: Path,
    keyword: str | None = None,
    recent_days: int = 14,
) -> dict:
    """Collect Book Mirror context: USER.md, SOUL.md, recent reflections, people."""
    context: dict[str, Any] = {
        "user": "",
        "soul": "",
        "recent_reflections": [],
        "related_pages": [],
        "people": [],
        "stats": {},
    }

    # USER.md and SOUL.md
    for name in ("USER.md", "SOUL.md"):
        path = brain / name
        if path.exists():
            try:
                context[name.lower().replace(".md", "")] = path.read_text(encoding="utf-8")
            except Exception:
                pass

    # Recent reflections
    reflections_dir = brain / "reflections"
    if reflections_dir.is_dir():
        cutoff = datetime.now() - timedelta(days=recent_days)
        for f in sorted(reflections_dir.glob("*.md"), reverse=True):
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            if mtime < cutoff:
                continue
            fm = _parse_frontmatter(f)
            try:
                body = f.read_text(encoding="utf-8")
            except Exception:
                body = ""
            context["recent_reflections"].append({
                "path": str(f.relative_to(brain)),
                "title": (fm or {}).get("title", f.stem),
                "date": (fm or {}).get("date", ""),
                "content": body[:2000],  # truncate
            })
        context["stats"]["reflections_count"] = len(context["recent_reflections"])

    # Keyword-related pages
    if keyword:
        kw_lower = keyword.lower()
        for page in _find_pages(brain):
            if page.name in ("USER.md", "SOUL.md"):
                continue
            try:
                text = page.read_text(encoding="utf-8")
            except Exception:
                continue
            if kw_lower in text.lower():
                rel = str(page.relative_to(brain))
                context["related_pages"].append({
                    "path": rel,
                    "title": (_parse_frontmatter(page) or {}).get("title", page.stem),
                    "content": text[:1500],
                })
                if len(context["related_pages"]) >= 10:
                    break
        context["stats"]["related_pages_count"] = len(context["related_pages"])

    # People pages
    people_dir = brain / "people"
    if people_dir.is_dir():
        for f in sorted(people_dir.glob("*.md")):
            fm = _parse_frontmatter(f)
            try:
                body = f.read_text(encoding="utf-8")
            except Exception:
                body = ""
            context["people"].append({
                "path": str(f.relative_to(brain)),
                "name": (fm or {}).get("title", f.stem),
                "content": body[:1500],
            })
        context["stats"]["people_count"] = len(context["people"])

    return context


# ── main ─────────────────────────────────────────────────────────────


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Brain query scanner")
    sub = parser.add_subparsers(dest="command", required=True)

    # search
    p_search = sub.add_parser("search", help="Keyword search")
    p_search.add_argument("keyword")
    p_search.add_argument("--brain-dir", default=os.path.expanduser("~/.hermes/brain"))
    p_search.add_argument("--type", dest="page_type")
    p_search.add_argument("--recent-days", type=int)

    # contradictions
    p_contra = sub.add_parser("contradictions", help="Detect fact contradictions")
    p_contra.add_argument("--brain-dir", default=os.path.expanduser("~/.hermes/brain"))

    # context
    p_ctx = sub.add_parser("context", help="Collect Book Mirror context")
    p_ctx.add_argument("--brain-dir", default=os.path.expanduser("~/.hermes/brain"))
    p_ctx.add_argument("--keyword")
    p_ctx.add_argument("--recent-days", type=int, default=14)

    args = parser.parse_args()
    brain = Path(args.brain_dir).expanduser().resolve()

    if not brain.is_dir():
        print(json.dumps({"error": f"Brain directory not found: {brain}"}))
        sys.exit(1)

    if args.command == "search":
        result = _cmd_search(brain, args.keyword, args.page_type, args.recent_days)
    elif args.command == "contradictions":
        result = _cmd_contradictions(brain)
    elif args.command == "context":
        result = _cmd_context(brain, args.keyword, args.recent_days)
    else:
        result = {"error": f"Unknown command: {args.command}"}

    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
