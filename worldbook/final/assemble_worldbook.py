#!/usr/bin/env python3
"""Assemble the runtime Shuchiin University + Stand worldbook.

The modular JSON files are the source of truth. The assembler preserves their
IDs, ordering, enable states and trigger metadata, and only removes project-
layer migration text that should never leak into the in-world runtime.

Usage:
    python assemble_worldbook.py

Output:
    辉夜大小姐_秀知院大学_character_book_v1.0.json
"""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "manifest.json"
OUTPUT = ROOT / "辉夜大小姐_秀知院大学_character_book_v1.0.json"

PROHIBITED_RUNTIME_MARKERS = (
    "授权母卡",
    "旧母卡",
    "原卡",
    "本世界书",
    "正式运行",
    "运行时",
    "升学重映射",
    "自动迁移",
    "世界线:秀知院大学AU",
    "秀知院大学AU",
    "（成年人）",
)

ANTI_STAND_MARKERS = (
    "不存在能够直接突破现实规律的超自然力量",
    "不存在魔法、修仙、异能",
    "绝对的现代日常唯物世界观",
    "拦截一切超自然力量",
    "任何超常现象都必须用“巧合”",
)


def sanitize_entry(source: dict) -> dict:
    entry = copy.deepcopy(source)
    content = entry.get("content", "")

    # Character entries keep only facts that exist inside the world.
    content = re.sub(r"(?m)^世界线:[^\n]*\n", "", content)
    content = re.sub(r"(?m)^(年龄:\s*\d+\s*岁)[（(]成年人[）)]\s*$", r"\1", content)
    entry["content"] = content
    entry["comment"] = entry.get("comment", "").replace("(多选一)", "")
    return entry


def assert_runtime_text_is_in_world(entries: list[dict]) -> None:
    failures: list[str] = []
    for entry in entries:
        content = entry.get("content", "")
        for marker in PROHIBITED_RUNTIME_MARKERS:
            if marker in content:
                failures.append(f"entry {entry.get('id')}: project marker {marker}")
        for marker in ANTI_STAND_MARKERS:
            if marker in content:
                failures.append(f"entry {entry.get('id')}: anti-Stand legacy rule {marker}")
    if failures:
        raise RuntimeError("runtime worldbook validation failed: " + "; ".join(failures))


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    entries: list[dict] = []

    for filename in manifest["assembly_order"]:
        module = json.loads((ROOT / filename).read_text(encoding="utf-8"))
        entries.extend(sanitize_entry(entry) for entry in module["entries"])

    ids = [entry["id"] for entry in entries]
    if len(entries) != manifest["runtime_entry_count"]:
        raise RuntimeError(f"entry count mismatch: {len(entries)}")
    if len(ids) != len(set(ids)):
        raise RuntimeError("duplicate entry id detected")
    if sorted(ids) != list(range(manifest["runtime_entry_count"])):
        raise RuntimeError("entry id coverage mismatch")

    entries.sort(key=lambda item: item["id"])
    assert_runtime_text_is_in_world(entries)

    payload = {
        "name": "辉夜大小姐想让我告白 - 秀知院大学 × 替身 v1.0",
        "description": "以东京秀知院大学为核心舞台的成年青春群像、恋爱头脑战与真实替身能力世界。",
        "scan_depth": 2,
        "token_budget": 0,
        "recursive_scanning": False,
        "extensions": {},
        "entries": entries,
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"PASS: {len(entries)} entries -> {OUTPUT.name}")
    print("PASS: no project-layer migration markers")
    print("PASS: no legacy anti-Stand worldview rules")


if __name__ == "__main__":
    main()
