#!/usr/bin/env python3
from __future__ import annotations

import base64
import copy
import hashlib
import json
import struct
import zlib
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
BUSINESS_BOOK = ROOT / "build/worldbook/辉夜大小姐_秀知院大学_替身版_worldbook_v1.0.0.json"
FIRST_MES = ROOT / "source/extracted/opening/first_mes.md"
ALT_MES = ROOT / "source/extracted/opening/alternate_01_safe.md"
COVER_WEBP = ROOT / "mvu/media/cover/kaguya_jojo_cover.webp"
OUT_DIR = ROOT / "build/card"
OUT_JSON = OUT_DIR / "辉夜大小姐_秀知院大学_替身版_v1.0.0-candidate1.json"
OUT_PNG = OUT_DIR / "辉夜大小姐_秀知院大学_替身版_v1.0.0-candidate1.png"
OUT_COMPAT = OUT_DIR / "辉夜大小姐_秀知院大学_替身版_v1.0.0-candidate1-compat-dual.png"
OUT_QA = OUT_DIR / "CARD_ASSEMBLY_candidate1_QA.json"
COVER_PNG = OUT_DIR / "_cover_candidate1.png"
RUNTIME_REF = "8870c98f6eb9350cdce697126978bb0021ae01a9"
RUNTIME_URL = "https://testingcf.jsdelivr.net/gh/3086013261qq-hue/Kaguya-sama-Love-Is-War-Sandbox@" + RUNTIME_REF + "/modules/kaguya-verdict-mvu/src/statusbar.mjs"
PNG_SIG = b"\x89PNG\r\n\x1a\n"
CARD_KEYS = {b"chara", b"ccv3"}

def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()

def adapt_opening(text: str) -> str:
    replacements = [("秀知院学园", "秀知院大学"), ("男高中生", "男大学生"), ("桌游部", "桌游研究会"), ("新部员", "新会员"), ("转入秀知院的普通混院（纯点子）学生", "就读秀知院大学的普通混院学生"), ("阴沉少年（石上优）", "阴沉大学生（石上优）"), ("超精英贵族学校", "超精英贵族大学"), ("少男少女", "青年男女")]
    for old, new in replacements: text = text.replace(old, new)
    return text

def tech_ext(position: int, depth: int) -> dict:
    return {"position": position, "depth": depth, "role": 0, "probability": 100, "useProbability": True, "scan_depth": None, "prevent_recursion": True, "exclude_recursion": True, "group": "", "group_override": False, "group_weight": 100}

def tech_entry(entry_id: int, comment: str, content: str, order: int, *, enabled: bool, position: str) -> dict:
    return {"id": entry_id, "keys": [], "secondary_keys": [], "comment": comment, "content": content.strip(), "constant": True, "selective": False, "insertion_order": order, "enabled": enabled, "position": position, "use_regex": True, "extensions": tech_ext(4 if position == "at_depth" else 1, 0 if position == "at_depth" else 4)}

def make_script(name: str, sid: str, content: str, info: str) -> dict:
    return {"type": "script", "enabled": True, "name": name, "id": sid, "content": content.strip() + "\n", "info": info, "button": {"enabled": False, "buttons": []}, "data": {}, "export_with": {"data": True, "button": False}}

def build_card() -> dict:
    business = json.loads(BUSINESS_BOOK.read_text(encoding="utf-8"))
    entries = copy.deepcopy(business["entries"])
    if len(entries) != 158: raise RuntimeError(f"business worldbook entry count {len(entries)} != 158")
    max_id = max(int(e.get("id", 0)) for e in entries)
    update_rules = '''---
变量更新规则:
  总则:
    - 本卡MVU只有一个模型可写业务字段：today_verdict。
    - 音乐曲目、播放进度、锁屏页码、B站视频状态全部属于前端临时状态，禁止写入MVU。
    - 咩咩预设原生玩家状态、人物好感、信任、关系与当前时间不复制进stat_data。
  today_verdict:
    check:
      - 默认值为“今日，胜负未定。”
      - 只有当本轮确实完成了一个具有明确目标的恋爱头脑战、社交对决、比赛、赌约或替身战阶段，并已经足以形成片尾式胜负判定时才更新。
      - 胜负按参与者真正想达成的目标判断，不按谁战力更强、谁说话更帅或谁最后出手判断。
      - 替身战的肉体胜负不自动等于恋爱或社交胜负；若双方都没达成目的，可以写“今日，无胜者。”；若双方都因自己的目标失败，可写“双败”。
      - 常用句式为“今日，是X的败北。”、“今日，是X与Y的双败。”、“今日，无胜者。”；可按实际人物和事件自然变化，但保持简洁、像动画片尾判定。
      - 如果本轮没有新的完整胜负结论，保持当前值，不为了每轮都有变化而强行重置或改写。'''
    output_format = '''---
变量输出格式:
  rule:
    - 每条回复的末尾只输出一个 <UpdateVariable>，里面先写 <Analysis>，再写 <JSONPatch>
    - <JSONPatch> 必须是合法 JSON 数组；路径用 / 分隔，不带 stat_data 前缀
    - 本卡只允许模型更新 /today_verdict
    - 只有新胜负已经真正成立且判定文本发生变化时才 replace /today_verdict
    - 没有新胜负时输出空数组 []
    - 不得创建音乐、视频、锁屏页码、播放进度、好感、信任、日期等第二套变量
  format: |-
    <UpdateVariable>
    <Analysis>一句话记录本轮已经实际成立的胜负事实；不要输出推理链。</Analysis>
    <JSONPatch>
    []
    </JSONPatch>
    </UpdateVariable>'''
    variable_list = '''---
<status_current_variable>
{{format_message_variable::stat_data}}
</status_current_variable>

- 不在正文里输出 <status_current_variable>；它只用于读取当前MVU变量。
- `today_verdict`：唯一持久业务字段，保存最近一次已经成立的“今日胜负”片尾判定。
- 默认：`今日，胜负未定。`
- 音乐、视频锁屏与播放器状态全部由前端维护，不进入stat_data。
- 玩家状态与人物关系继续读取咩咩预设本轮 `<status>` / `<affinity>`，不要建立副本。'''
    tech = [tech_entry(max_id + 1, "[mvu_update]变量更新规则", update_rules, 902, enabled=True, position="at_depth"), tech_entry(max_id + 2, "[mvu_update]变量输出格式", output_format, 901, enabled=True, position="at_depth"), tech_entry(max_id + 3, "变量列表", variable_list, 900, enabled=True, position="at_depth"), tech_entry(max_id + 4, "[initvar]变量初始化勿开", "today_verdict: 今日，胜负未定。", 899, enabled=False, position="after_char")]
    entries.extend(tech)
    if len(entries) != 162: raise RuntimeError("final worldbook entry count mismatch")
    business["name"] = "辉夜大小姐想让我告白｜秀知院大学 × 替身｜咩咩全栈世界书 v1.0.0"
    business["description"] = "秀知院大学成年青春群像、恋爱头脑战、真实替身体系与极简败北判定MVU。"
    business["entries"] = entries
    mvu_core = "import 'https://testingcf.jsdelivr.net/gh/MagicalAstrogy/MagVarUpdate/artifact/bundle.js';"
    mvu_zod = '''// 《辉夜大小姐》秀知院大学 × 替身｜MVU Schema
// z 与 _ 由酒馆助手提供；不要额外 import。
import { registerMvuSchema } from 'https://testingcf.jsdelivr.net/gh/StageDog/tavern_resource/dist/util/mvu_zod.js';

export const Schema = z.object({
  today_verdict: z.string().prefault('今日，胜负未定。'),
}).prefault({
  today_verdict: '今日，胜负未定。',
});

$(() => { registerMvuSchema(Schema); });'''
    scripts = [make_script("MVU", "mvu-core", mvu_core, "MagVarUpdate 变量系统底座；咩咩全栈原生导入，勿删。"), make_script("MVU ZOD", "mvu-zod-schema", mvu_zod, "唯一持久业务字段：today_verdict。"), make_script("变量状态栏", "mvu-statusbar", f"import '{RUNTIME_URL}';", "最新合法AI楼层挂载双视频锁屏、败北竖条与Awake单实例播放器。")]
    regex_scripts = [{"id": "mvu-hide-update-block", "scriptName": "[MVU]去除变量更新显示", "findRegex": r"/<UpdateVariable>\s*[\s\S]*?<\/UpdateVariable>\s*/gi", "replaceString": "", "trimStrings": [], "placement": [2], "disabled": False, "markdownOnly": True, "promptOnly": False, "runOnEdit": True, "substituteRegex": 0, "minDepth": None, "maxDepth": None}, {"id": "mvu-hide-placeholder", "scriptName": "[MVU]去除正文底部占位符", "findRegex": r"/<StatusPlaceHolderImpl\s*\/?>/gi", "replaceString": "", "trimStrings": [], "placement": [1, 2], "disabled": False, "markdownOnly": True, "promptOnly": True, "runOnEdit": True, "substituteRegex": 0, "minDepth": None, "maxDepth": None}]
    first_mes = adapt_opening(FIRST_MES.read_text(encoding="utf-8")).strip()
    alt = adapt_opening(ALT_MES.read_text(encoding="utf-8")).strip()
    if any(x in first_mes + "\n" + alt for x in ["秀知院学园", "男高中生", "桌游部", "超精英贵族学校"]): raise RuntimeError("opening still contains legacy high-school wording")
    return {"spec": "chara_card_v3", "spec_version": "3.0", "data": {"name": "辉夜大小姐想让我告白｜秀知院大学 × 替身", "description": "《辉夜大小姐想让我告白》授权同人角色卡。舞台为秀知院大学，恋爱头脑战与JOJO替身体系在同一世界内真实并存。", "personality": "", "scenario": "秀知院大学。豪门、学生会、社团、学业与恋爱头脑战照常运转，而替身使者之间的吸引、能力情报战与JOJO式对峙已经成为这个世界真实的一部分。", "first_mes": first_mes, "mes_example": "", "creator_notes": "基于 SheepSheep（咩咩）原卡授权改造。正式版方向：秀知院大学 × 替身；咩咩制卡·全栈 v1.0.0；极简“今日败北”MVU；Awake为主打歌；双B站视频锁屏。真实Android/SillyTavern实机验收尚待用户导入测试。", "system_prompt": "", "post_history_instructions": "", "alternate_greetings": [alt], "tags": ["辉夜大小姐想让我告白", "秀知院大学", "JOJO", "替身", "MVU"], "creator": "SheepSheep", "character_version": "v1.0.0-candidate1", "extensions": {"fav": False, "talkativeness": "0.5", "world": business["name"], "depth_prompt": {"prompt": "", "depth": 4, "role": "system"}, "regex_scripts": regex_scripts, "tavern_helper": {"scripts": scripts, "variables": {}}}, "character_book": business}}

def read_chunks(raw: bytes):
    if not raw.startswith(PNG_SIG): raise ValueError("not PNG")
    off, out = 8, []
    while off < len(raw):
        if off + 12 > len(raw): raise ValueError("truncated PNG")
        n = struct.unpack(">I", raw[off:off + 4])[0]; typ = raw[off + 4:off + 8]; data = raw[off + 8:off + 8 + n]; crc = struct.unpack(">I", raw[off + 8 + n:off + 12 + n])[0]
        if (zlib.crc32(typ + data) & 0xFFFFFFFF) != crc: raise ValueError(f"PNG CRC error {typ!r}")
        out.append((typ, data)); off += 12 + n
    if not out or out[-1][0] != b"IEND": raise ValueError("PNG missing IEND")
    return out

def make_chunk(typ: bytes, data: bytes) -> bytes: return struct.pack(">I", len(data)) + typ + data + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
def compact_json(obj) -> bytes: return json.dumps(obj, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
def text_payload(key: str, obj) -> bytes: return key.encode("latin-1") + b"\0" + base64.b64encode(compact_json(obj))
def v2_from_v3(card: dict) -> dict:
    data = dict(card["data"])
    for k in ("nickname", "creator_notes_multilingual", "source", "group_only_greetings", "creation_date", "modification_date", "assets"): data.pop(k, None)
    return {"spec": "chara_card_v2", "spec_version": "2.0", "data": data}

def write_card_png(image_path: Path, card: dict, output_path: Path, mode: str) -> dict:
    chunks = read_chunks(image_path.read_bytes()); kept, removed = [], []
    for typ, data in chunks:
        if typ == b"tEXt" and b"\0" in data and data.split(b"\0", 1)[0] in CARD_KEYS: removed.append(data.split(b"\0", 1)[0].decode("latin-1")); continue
        kept.append((typ, data))
    inserts = [(b"tEXt", text_payload("ccv3", card))] if mode == "compact-v3" else [(b"tEXt", text_payload("chara", v2_from_v3(card))), (b"tEXt", text_payload("ccv3", card))]
    raw = bytearray(PNG_SIG)
    for typ, data in kept:
        if typ == b"IEND":
            for ityp, idata in inserts: raw += make_chunk(ityp, idata)
        raw += make_chunk(typ, data)
    output_path.write_bytes(raw)
    found = {}
    for typ, data in read_chunks(output_path.read_bytes()):
        if typ == b"tEXt" and b"\0" in data:
            key, val = data.split(b"\0", 1)
            if key in CARD_KEYS: found[key.decode()] = json.loads(base64.b64decode(val).decode("utf-8"))
    if mode == "compact-v3": assert set(found) == {"ccv3"} and found["ccv3"] == card
    else: assert set(found) == {"chara", "ccv3"} and found["ccv3"] == card and found["chara"] == v2_from_v3(card)
    return {"mode": mode, "bytes": output_path.stat().st_size, "sha256": sha256_bytes(output_path.read_bytes()), "payloads": sorted(found), "roundtrip_ok": True, "removed_old_payloads": removed}

def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    card = build_card(); OUT_JSON.write_text(json.dumps(card, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with Image.open(COVER_WEBP) as im: im.convert("RGB").save(COVER_PNG, format="PNG", optimize=True)
    compact_report = write_card_png(COVER_PNG, card, OUT_PNG, "compact-v3"); dual_report = write_card_png(COVER_PNG, card, OUT_COMPAT, "dual")
    entries = card["data"]["character_book"]["entries"]; tech = {e["comment"]: e for e in entries[-4:]}; scripts = card["data"]["extensions"]["tavern_helper"]["scripts"]; regexes = card["data"]["extensions"]["regex_scripts"]
    qa = {"schema": "kaguya-jojo-fullstack-card-candidate1.qa.v1", "result": "PASS", "runtime_ref": RUNTIME_REF, "worldbook_entries": len(entries), "business_entries": 158, "mvu_system_entries": 4, "today_verdict_only_persistent_business_field": True, "scripts": [s["name"] for s in scripts], "regex_scripts": [r["scriptName"] for r in regexes], "checks": {"chara_card_v3": card["spec"] == "chara_card_v3" and card["spec_version"] == "3.0", "worldbook_entry_count_162": len(entries) == 162, "mvu_four_comments_exact": set(tech) == {"[mvu_update]变量更新规则", "[mvu_update]变量输出格式", "变量列表", "[initvar]变量初始化勿开"}, "mvu_four_double_recursion": all(e["extensions"]["prevent_recursion"] and e["extensions"]["exclude_recursion"] for e in tech.values()), "mvu_three_enabled_one_init_disabled": all(tech[n]["enabled"] for n in ("[mvu_update]变量更新规则", "[mvu_update]变量输出格式", "变量列表")) and not tech["[initvar]变量初始化勿开"]["enabled"], "mvu_scan_depth_null": all(e["extensions"]["scan_depth"] is None for e in tech.values()), "three_tavern_helper_scripts": [s["name"] for s in scripts] == ["MVU", "MVU ZOD", "变量状态栏"], "two_mvu_regex_scripts": len(regexes) == 2, "runtime_pinned": RUNTIME_REF in scripts[2]["content"], "legacy_high_school_opening_removed": not any(x in card["data"]["first_mes"] + "\n" + "\n".join(card["data"]["alternate_greetings"]) for x in ("秀知院学园", "男高中生", "桌游部", "超精英贵族学校")), "compact_ccv3_roundtrip": compact_report["roundtrip_ok"] and compact_report["payloads"] == ["ccv3"], "dual_roundtrip": dual_report["roundtrip_ok"] and dual_report["payloads"] == ["ccv3", "chara"]}, "json": {"bytes": OUT_JSON.stat().st_size, "sha256": sha256_bytes(OUT_JSON.read_bytes())}, "png_main": compact_report, "png_compat_dual": dual_report, "real_android_sillytavern_pass": False, "note": "源码/结构/PNG回读QA通过；真实Android/SillyTavern视频iframe、Awake播放与MVU写入仍需用户实机导入验收。"}
    if not all(qa["checks"].values()): raise RuntimeError("QA failed: " + ", ".join(k for k, v in qa["checks"].items() if not v))
    OUT_QA.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"); COVER_PNG.unlink(missing_ok=True)
    print("CARD_ASSEMBLY_CANDIDATE1: PASS"); print(OUT_JSON); print(OUT_PNG); print(OUT_COMPAT)

if __name__ == "__main__": main()
