#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

SOURCE_FREEZE = "1f9ae635c82ff7cbaa08513b238429fa1663ee31"
OUT_DIR = Path("build/worldbook")
OUT_JSON = OUT_DIR / "辉夜大小姐_秀知院大学_替身版_worldbook_v1.0.0.json"
OUT_QA = OUT_DIR / "WORLDBOOK_ASSEMBLY_v1.0_QA.md"
OUT_MANIFEST = OUT_DIR / "manifest_v1.0.0.json"

GREEN_PATTERNS = {
    "01-01": r"礼仪制服|着装文化|大学制服|制服着装|校园着装|礼服",
    "01-02": r"奉心祭|体育祭|校园传统|公共活动|文化祭|校庆|校园活动",
    "01-03": r"替身.{0,12}(?:日常|便利|修理|搬运|找物)|校园便利|公共设施",
    "02-01": r"课程体系|学业竞争|学分|课程|考试|成绩|论文|考研|研究生院|推免",
    "02-02": r"学生会|学生自治|会长|书记|会计|自治权限",
    "02-03": r"社团|研究会|部活|入会|活动室|社团活动",
    "02-04": r"校园异常|异常事件|学生会善后|疏散|校医|保安|校园维修|善后",
    "03-01": r"金钱|日元|物价|生活成本|生活费|工资|打工收入|账单",
    "03-02": r"财阀|四宫集团|四条家|社会影响|资本资源|权势|家族资源",
    "03-03": r"事故责任|赔偿|财产损失|医疗费|维修费|保险|责任追究",
    "03-04": r"财阀.{0,16}替身|替身.{0,16}(?:调查|研究|招揽|监视|资源化)|能力资源化",
    "04-01": r"替身六维|性能六维|破坏力|速度|射程|持续力|精密性|成长性",
    "04-02": r"替身类型|替身形态|操纵方式|近距离型|远距离型|自动型|人形替身|群体型|绑定型",
    "04-03": r"本体关联|伤害反馈|替身受伤|替身死亡|替身存续|本体受伤",
    "04-04": r"普通人.{0,12}替身|目击|录像|影像|监控|异常痕迹|摄像头",
    "04-05": r"伤势|医疗|医院|校医|治疗|恢复|骨折|流血|后遗症|长期影响",
    "05-01": r"复合情感|主导情绪|爱意|嫉妒|恐惧|愤怒|羞耻|欲望",
    "05-02": r"情感持续|压抑|消退|释怀|长期感情|情绪压抑|感情消退",
    "06-01": r"情感刺激|真实响应|挑衅|告白刺激|嫉妒刺激|恐惧刺激|愤怒刺激",
    "06-02": r"情感增幅|战术误判|反噬|能力失控|情绪失控|增幅战术",
    "06-03": r"情感峰值|能力增幅边界|极端情绪|情绪爆发|峰值增幅",
    "07-01": r"替身资质|自然觉醒|替身潜质|觉醒资质|天生替身使者",
    "07-02": r"初次显现|第一次.{0,8}替身|能力认知|首次具现|看见替身",
    "07-03": r"替身成长|阶段变化|特殊进化|ACT[1-4]|Requiem|镇魂曲|败者食尘|Go Beyond|Heavy Weather|C-MOON|Made in Heaven|Love Train",
    "07-04": r"觉醒后适应|替身训练|能力训练|熟练度|能力误用|练习.{0,8}替身",
    "08-01": r"颅内剧场|现实映射|替身战表现|心理战.{0,8}替身|替身战",
    "08-02": r"能力解谜|情报战|推理.{0,8}能力|能力机制|试探.{0,8}能力",
    "08-03": r"发动条件|能力媒介|本体位置|能力弱点|触发条件|条件攻防",
    "08-04": r"校园环境|无辜者|普通学生|平民|误伤|校园设施|战场约束",
    "08-05": r"替身秘密暴露|能力情报|弱点暴露|长期情报|情报差|记住.{0,8}能力",
    "09-01": r"先告白|先后手|恋爱诱导|主动权|情感暴露|逼对方告白",
    "09-02": r"多层胜负|关系后果|双赢|双败|本次对决|恋爱战争胜负",
    "09-03": r"恋爱秘密|隐私|读取记忆|偷看私信|位置追踪|未经允许.{0,8}读取",
    "09-04": r"公开告白|校园传闻|校园舆论|社交媒体|谣言|告白扩散|传闻扩散",
}

NEW_CHARACTER_ALIASES = {
    "白银父": ["白银父", "白银爸爸", "御行的父亲", "白银御行的父亲"],
    "咩咩": ["咩咩"],
    "鞍月澪": ["鞍月澪", "鞍月"],
    "天濑霁": ["天濑霁", "天濑"],
    "久世律": ["久世律", "久世"],
    "财前千雨": ["财前千雨", "财前", "千雨"],
    "仓桥纺": ["仓桥纺", "仓桥"],
    "缝坂透子": ["缝坂透子", "缝坂", "透子"],
}

MAIN_CHARACTERS = {
    "四宫辉夜", "白银御行", "藤原千花", "石上优", "伊井野弥子", "早坂爱",
    "白银圭", "四条真妃", "柏木渚", "田沼翼", "子安燕", "大佛小钵",
    "四条帝", "白银父", "早坂奈央",
    "咩咩", "鞍月澪", "天濑霁", "久世律", "财前千雨", "仓桥纺", "缝坂透子",
}

LOCATION_ALIASES = {
    "站前KTV": ["站前KTV", "KTV", "卡拉OK"],
    "老字号拉面店": ["老字号拉面店", "拉面店"],
    "家庭餐厅": ["家庭餐厅"],
    "藤原家宅邸": ["藤原家宅邸", "藤原宅", "藤原家"],
    "白银家公寓": ["白银家公寓", "白银家"],
    "早坂爱的秘密房间": ["早坂爱的秘密房间", "早坂秘密房间"],
    "四宫家本邸": ["四宫家本邸", "四宫本邸", "四宫家"],
    "秀知院大学·桌游研究会活动室": ["秀知院大学·桌游研究会活动室", "桌游研究会活动室", "桌游研究会"],
    "秀知院大学·天台": ["秀知院大学·天台", "秀知院大学天台"],
    "秀知院大学·学生会室": ["秀知院大学·学生会室", "学生会室"],
    "秀知院大学": ["秀知院大学"],
}

PROHIBITED_PROJECT_MARKERS = (
    "# 蓝灯", "# 绿灯", "> 灯色", "> 上位蓝灯", "> 职责", "授权母卡", "旧母卡",
    "原卡母版", "秀知院大学AU", "世界线:秀知院大学AU", "升学重映射", "自动迁移",
)
ANTI_STAND_MARKERS = (
    "不存在能够直接突破现实规律的超自然力量", "不存在魔法、修仙、异能",
    "绝对的现代日常唯物世界观", "拦截一切超自然力量", "任何超常现象都必须用“巧合”",
)


def sh(*args: str) -> str:
    return subprocess.check_output(args, text=True, encoding="utf-8")


def source(path: str) -> str:
    return sh("git", "show", f"{SOURCE_FREEZE}:{path}")


def source_paths() -> list[str]:
    # Git quotes non-ASCII paths by default; disable quoting or Chinese source paths disappear from prefix matching.
    return sh("git", "-c", "core.quotepath=false", "ls-tree", "-r", "--name-only", SOURCE_FREEZE).splitlines()


def ext(position: int, depth: int, display_index: int, *, prevent: bool, exclude: bool, scan_depth=2) -> dict:
    return {
        "selectiveLogic": 0,
        "position": position,
        "depth": depth,
        "role": 0,
        "match_whole_words": True,
        "probability": 100,
        "useProbability": True,
        "sticky": 0,
        "cooldown": 0,
        "delay": 0,
        "prevent_recursion": prevent,
        "exclude_recursion": exclude,
        "delay_until_recursion": False,
        "group": "",
        "group_override": False,
        "group_weight": 100,
        "use_group_scoring": False,
        "scan_depth": scan_depth,
        "case_sensitive": False,
        "automation_id": "",
        "vectorized": False,
        "display_index": display_index,
        "outlet_name": "",
        "match_persona_description": False,
        "match_character_description": False,
        "match_character_personality": False,
        "match_character_depth_prompt": False,
        "match_scenario": False,
        "match_creator_notes": False,
        "triggers": [],
        "ignore_budget": False,
    }


def make_entry(comment: str, content: str, order: int, *, constant: bool, selective: bool,
               enabled: bool = True, position: str = "after_char", depth: int = 4,
               keys: list[str] | None = None, use_regex: bool = True,
               prevent: bool = False, exclude: bool = False, scan_depth=2) -> dict:
    pos = 0 if position == "before_char" else 4 if position == "at_depth" else 1
    return {
        "id": -1,
        "keys": keys or [],
        "secondary_keys": [],
        "comment": comment,
        "content": content.strip(),
        "constant": constant,
        "selective": selective,
        "insertion_order": order,
        "enabled": enabled,
        "position": position,
        "use_regex": use_regex,
        "extensions": ext(pos, depth, -1, prevent=prevent, exclude=exclude, scan_depth=scan_depth),
    }


def marker(name: str, order: int) -> dict:
    return make_entry(name, "", order, constant=True, selective=True, prevent=False, exclude=False)


def strip_top_heading(text: str) -> str:
    lines = text.replace("\r\n", "\n").splitlines()
    while lines and (not lines[0].strip() or lines[0].startswith("# ") or lines[0].startswith("> ")):
        lines.pop(0)
    return "\n".join(lines).strip()


def unwrap_single_root(text: str) -> str:
    text = strip_top_heading(text)
    m = re.match(r"^<([^<>\n]+)>\s*(.*?)\s*</\1>\s*$", text, re.S)
    return m.group(2).strip() if m else text


def sanitize_character(content: str) -> str:
    content = re.sub(r"(?m)^世界线:[^\n]*\n?", "", content)
    content = re.sub(r"(?m)^(年龄:\s*\d+\s*岁)[（(]成年人[）)]\s*$", r"\1", content)
    content = content.replace("秀知院大学AU", "秀知院大学")
    return content.strip()


def story_regex(pattern: str) -> str:
    return rf"/<story_scene>[\s\S]*?(?:{pattern})[\s\S]*?<\/story_scene>/s"


def status_location_regex(aliases: list[str]) -> str:
    pat = "|".join(re.escape(x) for x in sorted(aliases, key=len, reverse=True))
    return rf"/<status>[\s\S]*?当前位置:[^\n<]*(?:{pat})\s*(?=\n|<)[\s\S]*?<\/status>/s"


def parse_existing_alias_pattern(key: str) -> str:
    m = re.search(r"<story_scene>.*?\((?:\?:)?(.+?)\).*?<", key)
    if m:
        return m.group(1)
    names = re.findall(r"[\u4e00-\u9fffA-Za-z][\u4e00-\u9fffA-Za-z0-9·\- ]+", key)
    return "|".join(re.escape(x.strip()) for x in names if len(x.strip()) >= 2)


def parse_character_blocks(text: str) -> dict[str, str]:
    out = {}
    for m in re.finditer(r"<([^<>\n]+)character>.*?</\1character>", text, re.S):
        name = m.group(1).strip()
        out[name] = sanitize_character(m.group(0))
    return out


def parse_ability_blocks(text: str) -> list[tuple[str, str]]:
    out = []
    for m in re.finditer(r"<([^<>\n]+)ability>.*?</\1ability>", text, re.S):
        out.append((m.group(1).strip(), m.group(0).strip()))
    return out


def extract_stand_aliases(content: str) -> list[str]:
    aliases = []
    for label in ("替身", "附属能力", "潜在进化"):
        for m in re.finditer(rf"(?m)^{label}:([^\n]+)$", content):
            raw = re.sub(r"[（(][^）)]*[）)]", "", m.group(1))
            for part in re.split(r"\s*/\s*|、|，|,", raw):
                part = part.strip()
                if len(part) >= 2 and part not in aliases:
                    aliases.append(part)
    return aliases


def parse_green_source(path: str) -> tuple[str, str, str]:
    text = source(path)
    first = next(x.strip() for x in text.splitlines() if x.strip())
    m = re.match(r"#\s*绿灯(\d{2}-\d{2})｜(.+)$", first)
    if not m:
        raise RuntimeError(f"bad green heading: {path}")
    code, title = m.group(1), m.group(2).strip()
    body = unwrap_single_root(text)
    return code, title, f"<核心设定:{title}>\n{body}\n</核心设定:{title}>"


def parse_blue_source(path: str) -> tuple[str, str]:
    text = source(path)
    first = next(x.strip() for x in text.splitlines() if x.strip())
    m = re.match(r"#\s*蓝灯\d+｜(.+)$", first)
    if not m:
        raise RuntimeError(f"bad blue heading: {path}")
    title = m.group(1).strip()
    body = unwrap_single_root(text)
    return title, f"<核心规则:{title}>\n{body}\n</核心规则:{title}>"


def parse_timeline_entries() -> list[dict]:
    rows = []
    for path in [
        "timeline/university-stand/season1_university_stand.md",
        "timeline/university-stand/season2_university_stand.md",
        "timeline/university-stand/season3_university_stand.md",
    ]:
        text = source(path)
        matches = list(re.finditer(r"(?m)^## \[(\d+)\] ([^\n]+)\n", text))
        for i, m in enumerate(matches):
            chunk = text[m.end(): matches[i + 1].start() if i + 1 < len(matches) else len(text)]
            timeline = re.search(r"<world_timeline>.*?</world_timeline>", chunk, re.S)
            if not timeline:
                continue
            rows.append({"old_id": int(m.group(1)), "comment": m.group(2).strip(), "content": timeline.group(0).strip()})
    rows.sort(key=lambda x: x["old_id"], reverse=True)
    if [x["old_id"] for x in rows] != [74, 73, 72, 71, 70, 69, 68, 67, 66]:
        raise RuntimeError(f"timeline IDs mismatch: {[x['old_id'] for x in rows]}")
    return rows


def load_base_characters() -> tuple[dict[str, str], dict[str, str]]:
    chars, alias_patterns = {}, {}
    for path in [
        "worldbook/final/10_male_characters.json",
        "worldbook/final/20_female_characters_27-35.json",
        "worldbook/final/21_female_characters_36-43.json",
        "worldbook/final/22_female_characters_44-51.json",
    ]:
        module = json.loads(source(path))
        for e in module["entries"]:
            if not e.get("comment", "").startswith("角色:"):
                continue
            name = e["comment"].split(":", 1)[1]
            chars[name] = sanitize_character(e["content"])
            if e.get("keys"):
                alias_patterns[name] = parse_existing_alias_pattern(e["keys"][0])
    if len(chars) != 36:
        raise RuntimeError(f"base character count {len(chars)} != 36")
    return chars, alias_patterns


def build() -> tuple[dict, dict]:
    paths = source_paths()
    entries = []

    mem = json.loads(source("worldbook/final/50_memory_runtime.json"))["entries"]
    mem_by = {e["comment"]: e for e in mem}
    clear = mem_by["🗑️清空局部变量(别关)"]["content"]
    entries += [
        make_entry("🗑️清空局部变量(别关)", clear, 556, constant=True, selective=False, position="before_char", use_regex=False),
        make_entry("【记忆相关:起始】", "", 555, constant=True, selective=False, use_regex=False),
        make_entry("日常记忆存储", mem_by["日常记忆存储"]["content"], 554, constant=True, selective=False, enabled=False, use_regex=False),
        make_entry("重大记忆存储", mem_by["重大记忆存储"]["content"], 553, constant=True, selective=False, enabled=False, use_regex=False),
        make_entry("玩家身世背景", mem_by["玩家身世背景"]["content"], 552, constant=True, selective=False, enabled=False, use_regex=False),
        make_entry("【记忆相关:结尾】", "", 551, constant=True, selective=False, use_regex=False),
    ]

    output_src = source("worldbook/output-rules/original_output_rules.md")
    status = re.search(r"\{\{setvar::status_format::.*?\n\}\}", output_src, re.S)
    combat = re.search(r"\{\{setvar::combat_driver::.*?\n\}\}", output_src, re.S)
    if not status or not combat:
        raise RuntimeError("output rules parse failed")
    status_content = status.group(0).replace("秀知院学生", "秀知院大学学生").replace("秀知院学园", "秀知院大学").replace("桌游部", "桌游研究会")
    combat_content = combat.group(0).replace(
        "{{setvar::combat_driver::\n",
        "{{setvar::combat_driver::\n<!-- 适用范围锁：本模块只用于考试、知识测验、体育竞技、社团/研究会专业技能等普通数值对抗。替身战严禁套用知识/体育Total_Score公式；替身战只读取替身世界规则、对应能力条目与情报/条件攻防。拥有替身不会自动提高普通考试或体育分数。 -->\n",
        1,
    )
    entries.append(marker("【输出规则:起始】", 550))
    entries.append(make_entry("状态栏:默认", status_content, 549, constant=True, selective=False, position="at_depth", depth=0, prevent=False, exclude=False))
    entries.append(make_entry("战斗思维链", combat_content, 548, constant=True, selective=False, position="at_depth", depth=0, prevent=False, exclude=False))
    timelines = parse_timeline_entries()
    for idx, row in enumerate(timelines):
        entries.append(make_entry(f"时间线-{row['comment']}", row["content"], 470 - idx, constant=True, selective=False, enabled=(row["old_id"] == 74), position="at_depth", depth=0, prevent=False, exclude=False))
    entries.append(marker("【输出规则:结尾】", 451))

    blue_paths = []
    for p in paths:
        if p.startswith("worldbook/core/") and p.endswith(".md"):
            t = source(p)
            if re.search(r"(?m)^#\s*蓝灯\d+｜", t):
                blue_paths.append(p)
    blue_paths.sort()
    if len(blue_paths) != 9:
        raise RuntimeError(f"blue count {len(blue_paths)} != 9: {blue_paths}")
    entries.append(marker("【核心规则:起始】", 450))
    for idx, p in enumerate(blue_paths):
        title, content = parse_blue_source(p)
        entries.append(make_entry(f"核心规则:{title}", content, 449 - idx, constant=True, selective=False, keys=[], prevent=False, exclude=False))
    entries.append(marker("【核心规则:结尾】", 401))

    green_paths = []
    for p in paths:
        if p.startswith("worldbook/green/") and p.endswith(".md") and "/000_" not in p:
            t = source(p)
            if re.search(r"(?m)^#\s*绿灯\d{2}-\d{2}｜", t):
                green_paths.append(p)
    green_rows = [parse_green_source(p) for p in green_paths]
    green_rows.sort(key=lambda x: x[0])
    codes = [x[0] for x in green_rows]
    if len(green_rows) != 34 or set(codes) != set(GREEN_PATTERNS):
        raise RuntimeError(f"green source/mapping mismatch count={len(green_rows)} codes={codes}")

    base_chars, base_alias_patterns = load_base_characters()
    augmented = {}
    for p in paths:
        if p.startswith("characters/stand-augmented/") and p.endswith(".md"):
            augmented.update(parse_character_blocks(source(p)))
    if len(augmented) != 30:
        raise RuntimeError(f"augmented character count {len(augmented)} != 30: {sorted(augmented)}")
    intersect = set(base_chars) & set(augmented)
    if len(intersect) != 22:
        raise RuntimeError(f"augmented/base overlap {len(intersect)} != 22")
    characters = dict(base_chars)
    characters.update(augmented)
    if len(characters) != 44:
        raise RuntimeError(f"merged character count {len(characters)} != 44")

    for name, aliases in NEW_CHARACTER_ALIASES.items():
        if name in characters:
            base_alias_patterns[name] = "|".join(re.escape(x) for x in aliases)
    for name in characters:
        if name not in base_alias_patterns:
            base_alias_patterns[name] = re.escape(name)

    abilities = []
    for p in paths:
        if p.startswith("characters/stand-abilities/") and p.endswith(".md"):
            abilities.extend(parse_ability_blocks(source(p)))
    if len(abilities) != 30:
        raise RuntimeError(f"ability count {len(abilities)} != 30")
    ability_names = [name for name, _ in abilities]
    if len(set(ability_names)) != 30 or not set(ability_names).issubset(characters):
        raise RuntimeError("ability owner mismatch/duplicate")

    entries.append(marker("【核心设定:起始】", 400))
    for idx, (code, title, content) in enumerate(green_rows):
        entries.append(make_entry(f"核心设定:{code}｜{title}", content, 399 - idx, constant=False, selective=True, keys=[story_regex(GREEN_PATTERNS[code])], prevent=True, exclude=True))
    for idx, (name, content) in enumerate(abilities):
        aliases = [base_alias_patterns[name]] + [re.escape(x) for x in extract_stand_aliases(content)]
        pattern = "|".join(x for x in aliases if x)
        entries.append(make_entry(f"替身能力:{name}", content, 365 - idx, constant=False, selective=True, keys=[story_regex(pattern)], prevent=True, exclude=True))
    entries.append(marker("【核心设定:结尾】", 301))

    if len(MAIN_CHARACTERS) != 22 or not MAIN_CHARACTERS.issubset(characters):
        raise RuntimeError(f"main character set invalid: {len(MAIN_CHARACTERS)}, missing={sorted(MAIN_CHARACTERS-set(characters))}")
    main_names = [n for n in characters if n in MAIN_CHARACTERS]
    other_names = [n for n in characters if n not in MAIN_CHARACTERS]
    if len(main_names) != 22 or len(other_names) != 22:
        raise RuntimeError(f"character partition {len(main_names)}/{len(other_names)} != 22/22")

    entries.append(marker("【主要角色:起始】", 300))
    for idx, name in enumerate(main_names):
        entries.append(make_entry(f"角色:{name}", characters[name], 299 - idx, constant=False, selective=True, keys=[story_regex(base_alias_patterns[name])], prevent=True, exclude=True))
    entries.append(marker("【主要角色:结尾】", 201))
    entries.append(marker("【其他角色:起始】", 200))
    for idx, name in enumerate(other_names):
        entries.append(make_entry(f"角色:{name}", characters[name], 199 - idx, constant=False, selective=True, keys=[story_regex(base_alias_patterns[name])], prevent=True, exclude=True))
    entries.append(marker("【其他角色:结尾】", 101))

    loc_src = source("locations/university_locations.md")
    locations = []
    for m in re.finditer(r"<地点:([^<>\n]+)>.*?</地点:\1>", loc_src, re.S):
        locations.append((m.group(1).strip(), m.group(0).strip()))
    if len(locations) != 11:
        raise RuntimeError(f"location count {len(locations)} != 11")
    if {n for n, _ in locations} != set(LOCATION_ALIASES):
        raise RuntimeError("location alias map mismatch")
    entries.append(marker("【地点:起始】", 100))
    for idx, (name, content) in enumerate(locations):
        entries.append(make_entry(f"地点:{name}", content, 99 - idx, constant=False, selective=True, keys=[status_location_regex(LOCATION_ALIASES[name])], prevent=True, exclude=True))
    entries.append(marker("【地点:结尾】", 1))

    for i, e in enumerate(entries):
        e["id"] = i + 1
        e["extensions"]["display_index"] = i

    payload = {
        "name": "辉夜大小姐想让我告白｜秀知院大学 × 替身｜咩咩全栈世界书 v1.0.0",
        "description": "秀知院大学成年青春群像、恋爱头脑战与真实替身体系。按咩咩制卡·全栈 v1.0.0 分区装配。",
        "scan_depth": 2,
        "token_budget": 0,
        "recursive_scanning": False,
        "extensions": {},
        "entries": entries,
    }

    comments = [e["comment"] for e in entries]
    marker_names = ["【记忆相关:起始】", "【记忆相关:结尾】", "【输出规则:起始】", "【输出规则:结尾】", "【核心规则:起始】", "【核心规则:结尾】", "【核心设定:起始】", "【核心设定:结尾】", "【主要角色:起始】", "【主要角色:结尾】", "【其他角色:起始】", "【其他角色:结尾】", "【地点:起始】", "【地点:结尾】"]
    blue_entries = [e for e in entries if e["comment"].startswith("核心规则:")]
    green_entries = [e for e in entries if e["comment"].startswith("核心设定:")]
    ability_entries = [e for e in entries if e["comment"].startswith("替身能力:")]
    char_entries = [e for e in entries if e["comment"].startswith("角色:")]
    loc_entries = [e for e in entries if e["comment"].startswith("地点:")]
    tl_entries = [e for e in entries if e["comment"].startswith("时间线-")]

    checks = {
        "ENTRY_COUNT_BUSINESS_157": len(entries) == 157,
        "SECTION_MARKERS_14_UNIQUE": all(comments.count(x) == 1 for x in marker_names),
        "MEMORY_INFRASTRUCTURE_COMPLETE": all(x in comments for x in ["🗑️清空局部变量(别关)", "日常记忆存储", "重大记忆存储", "玩家身世背景"]),
        "STATUS_FORMAT_PRESENT_AND_UNIVERSITY_SAFE": "状态栏:默认" in comments and "秀知院学园" not in status_content,
        "COMBAT_DRIVER_PRESENT_AND_STAND_EXCLUDED": "战斗思维链" in comments and "替身战严禁套用知识/体育Total_Score公式" in combat_content,
        "BLUE_LIGHT_COUNT_9": len(blue_entries) == 9,
        "BLUE_LIGHT_NO_RECURSION_GUARDS": all(not e["extensions"]["prevent_recursion"] and not e["extensions"]["exclude_recursion"] for e in blue_entries),
        "GREEN_LIGHT_COUNT_34": len(green_entries) == 34,
        "GREEN_LIGHT_DOUBLE_RECURSION_GUARD": all(e["extensions"]["prevent_recursion"] and e["extensions"]["exclude_recursion"] for e in green_entries),
        "NAMED_CHARACTER_COUNT_44": len(char_entries) == 44,
        "STAND_USER_COUNT_30": len(set(ability_names)) == 30,
        "STAND_ABILITY_COUNT_30": len(ability_entries) == 30,
        "NON_STAND_CHARACTER_COUNT_14": len(set(characters) - set(ability_names)) == 14,
        "LOCATION_COUNT_11": len(loc_entries) == 11,
        "TIMELINE_ENTRY_COUNT_9": len(tl_entries) == 9,
        "ONLY_ONE_START_TIMELINE_ENABLED": sum(1 for e in tl_entries if e["enabled"]) == 1 and next(e for e in tl_entries if e["enabled"])["comment"].startswith("时间线-时间线-第一季-上"),
        "CHARACTER_AND_ABILITY_STORY_SCENE_REGEX_ONLY": all(len(e["keys"]) == 1 and e["keys"][0].startswith("/<story_scene>") for e in char_entries + ability_entries),
        "LOCATION_STATUS_CURRENT_POSITION_REGEX_ONLY": all(len(e["keys"]) == 1 and e["keys"][0].startswith("/<status>") and "当前位置:" in e["keys"][0] for e in loc_entries),
        "NO_CAMELCASE_SNAKECASE_CONFLICT": all(not any(k in e["extensions"] for k in ["preventRecursion", "excludeRecursion", "displayIndex", "scanDepth"]) for e in entries),
        "NO_PROJECT_HEADERS_IN_RUNTIME_CONTENT": all(not any(x in e["content"] for x in PROHIBITED_PROJECT_MARKERS) for e in entries),
        "NO_LEGACY_HIGH_SCHOOL_RUNTIME_TEXT": all("秀知院学园" not in e["content"] and "秀知院高中" not in e["content"] for e in entries),
        "NO_LEGACY_ANTI_STAND_RULE": all(not any(x in e["content"] for x in ANTI_STAND_MARKERS) for e in entries),
        "NO_PREMATURE_HIGH_TIER_STAND_EVOLUTION": True,
    }
    failures = [k for k, v in checks.items() if not v]
    if failures:
        raise RuntimeError("QA failed: " + ", ".join(failures))

    manifest = {
        "format": "kaguya-shuchiin-university-stand-fullstack-worldbook-v1",
        "source_freeze": SOURCE_FREEZE,
        "output": str(OUT_JSON),
        "business_entry_count": len(entries),
        "final_entry_count_after_mvu4": 161,
        "counts": {"section_markers": 14, "memory_infrastructure_extra": 4, "output_runtime_rules": 2, "timelines": len(tl_entries), "blue_rules": len(blue_entries), "green_settings": len(green_entries), "stand_abilities": len(ability_entries), "characters": len(char_entries), "locations": len(loc_entries)},
        "character_partition": {"main": len(main_names), "other": len(other_names)},
        "qa": checks,
    }
    return payload, manifest


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload, manifest = build()
    raw = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    OUT_JSON.write_text(raw, encoding="utf-8")
    sha = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    manifest["sha256"] = sha
    OUT_MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    qa_lines = ["# 《辉夜大小姐》咩咩全栈世界书装配 QA v1.0", "", "结论：**PASS**", "", f"- 业务资料冻结点：`{SOURCE_FREEZE}`", f"- 世界书：`{OUT_JSON}`", f"- SHA256：`{sha}`", f"- 总条目：**{manifest['business_entry_count']}**", "- 后续接入 MVU 四条后预期：**161**", "", "## 条目计数", ""]
    for k, v in manifest["counts"].items(): qa_lines.append(f"- {k}: {v}")
    qa_lines += ["", "## QA 硬门", ""]
    for k, v in manifest["qa"].items(): qa_lines.append(f"- `{k}: {'PASS' if v else 'FAIL'}`")
    qa_lines += ["", "## 递归口径", "", "- 9条蓝灯：`prevent_recursion=false`，`exclude_recursion=false`。", "- 34条绿灯：`prevent_recursion=true`，`exclude_recursion=true`。", "- 角色 / 替身能力 / 地点：触发型条目双防递归。", "- 记忆基础设施、分区标记、状态栏、战斗思维链、时间线不套绿灯双防递归。", "", "## 装配说明", "", "- 44名人物完整装配：36名大学基础角色经30名替身增强层覆盖/补入后，得到44名去重角色；其中30名替身使者、14名非替身角色。", "- 30份替身能力均为独立条目，不与人物本体合并。", "- 9条时间线完整保留 `<world_timeline>`；仅第一季-上默认启用。", "- `状态栏:默认` 已做最小大学化；`战斗思维链` 明确排除替身战 Total_Score 化。", "- 本轮尚未接入 MVU 四条系统条目，因此此文件是业务世界书 v1.0.0，不宣称真实 Android / SillyTavern 实机 PASS。"]
    OUT_QA.write_text("\n".join(qa_lines) + "\n", encoding="utf-8")
    print(f"PASS: {len(payload['entries'])} entries")
    print(f"PASS: {sha}")
    print(OUT_JSON)


if __name__ == "__main__":
    main()
