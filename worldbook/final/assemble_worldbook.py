#!/usr/bin/env python3
"""Assemble the modular Kaguya-sama Shuchiin University AU worldbook.

Usage:
    python assemble_worldbook.py

Output:
    辉夜大小姐_秀知院大学AU_character_book_v1.0.json
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "manifest.json"
OUTPUT = ROOT / "辉夜大小姐_秀知院大学AU_character_book_v1.0.json"


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    entries: list[dict] = []

    for filename in manifest["assembly_order"]:
        module = json.loads((ROOT / filename).read_text(encoding="utf-8"))
        entries.extend(module["entries"])

    ids = [entry["id"] for entry in entries]
    if len(entries) != manifest["runtime_entry_count"]:
        raise RuntimeError(f"entry count mismatch: {len(entries)}")
    if len(ids) != len(set(ids)):
        raise RuntimeError("duplicate entry id detected")
    if sorted(ids) != list(range(manifest["runtime_entry_count"])):
        raise RuntimeError("entry id coverage mismatch")

    entries.sort(key=lambda item: item["id"])
    payload = {
        "name": "辉夜大小姐想让我告白 - 秀知院大学AU v1.0",
        "description": "授权母卡派生；正式运行舞台为秀知院大学AU，具名在校学生均为18岁以上成年人。",
        "scan_depth": 2,
        "token_budget": 0,
        "recursive_scanning": False,
        "extensions": {},
        "entries": entries,
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"PASS: {len(entries)} entries -> {OUTPUT.name}")


if __name__ == "__main__":
    main()
