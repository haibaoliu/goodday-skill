#!/usr/bin/env python3
"""UNCHANGED-bias filter for cron job outputs.

Compares structured JSON output against a stored state file, tagging each
item as new/changed/unchanged/dropped.  Cron agents can then skip LLM
regeneration for UNCHANGED items — saving ~80%+ of token work.

Usage (from a cron script or pipeline):

    # Input: JSON array of {id, ...fields} or {items: [{id, ...}]}
    python unchanged_filter.py \
        --state ~/.hermes/cron/myjob_state.json \
        --id-field full_name \
        < input.json > output.json

The output wraps items with _status and _prev_summary fields.
"""

import hashlib
import json
import os
import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import Any


def _hash_item(item: dict, fields: list[str] | None) -> str:
    """Stable content hash for a data item."""
    if fields:
        parts = [str(item.get(f, "")) for f in fields]
    else:
        parts = [json.dumps(item, sort_keys=True, default=str)]
    return hashlib.md5("|".join(parts).encode()).hexdigest()[:12]


def _load_state(path: Path) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"items": {}}


def _save_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def filter_items(
    items: list[dict],
    id_field: str,
    hash_fields: list[str] | None,
    state_path: Path,
    summary_field: str = "summary",
) -> dict:
    """Tag items with UNCHANGED bias and return categorized output."""
    prev = _load_state(state_path).get("items", {})
    new_state: dict[str, dict] = {}

    new: list[dict] = []
    changed: list[dict] = []
    unchanged: list[dict] = []

    for item in items:
        item_id = str(item.get(id_field, ""))
        if not item_id:
            continue
        h = _hash_item(item, hash_fields)
        item["_hash"] = h

        prev_entry = prev.get(item_id)
        if prev_entry is None:
            item["_status"] = "new"
            new.append(item)
        elif prev_entry.get("hash") == h:
            item["_status"] = "unchanged"
            item["_prev_summary"] = prev_entry.get(summary_field, "")
            unchanged.append(item)
        else:
            item["_status"] = "changed"
            item["_prev_summary"] = prev_entry.get(summary_field, "")
            changed.append(item)

        new_state[item_id] = {"hash": h}

    # Dropped items
    current_ids = {str(i.get(id_field, "")) for i in items}
    dropped = [
        {"id": iid, "_prev_summary": prev_entry.get(summary_field, "")}
        for iid, prev_entry in prev.items()
        if iid not in current_ids
    ]

    _save_state(state_path, {"items": new_state, "last_run": ""})

    total = len(items)
    return {
        "stats": {
            "total": total,
            "new": len(new),
            "changed": len(changed),
            "unchanged": len(unchanged),
            "dropped": len(dropped),
            "llm_work_needed": len(new) + len(changed),
            "llm_work_skipped": len(unchanged),
            "savings_pct": round(len(unchanged) / max(total, 1) * 100),
        },
        "new": new,
        "changed": changed,
        "unchanged": unchanged,
        "dropped": dropped,
    }


def main() -> None:
    parser = ArgumentParser(description="UNCHANGED-bias filter for cron outputs")
    parser.add_argument("--state", required=True, help="Path to state file (JSON)")
    parser.add_argument("--id-field", default="id", help="Field used as unique ID (default: id)")
    parser.add_argument("--hash-fields", nargs="*", help="Fields to hash (default: all)")
    parser.add_argument("--summary-field", default="summary", help="Field storing LLM summary for reuse")
    args = parser.parse_args()

    raw = json.load(sys.stdin)

    # Accept both array and {items: [...]} formats
    if isinstance(raw, list):
        items = raw
    elif isinstance(raw, dict):
        items = raw.get("items", raw.get("repos", raw.get("results", [])))
    else:
        print(json.dumps({"error": "Expected JSON array or {items: [...]} dict"}))
        sys.exit(1)

    result = filter_items(
        items=items,
        id_field=args.id_field,
        hash_fields=args.hash_fields or None,
        state_path=Path(os.path.expanduser(args.state)),
        summary_field=args.summary_field,
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
