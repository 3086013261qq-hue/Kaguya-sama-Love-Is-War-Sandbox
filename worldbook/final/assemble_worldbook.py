#!/usr/bin/env python3
"""Assemble the runtime Shuchiin University worldbook.

The modular JSON files are build inputs. This assembler keeps their IDs,
ordering, enable states and trigger metadata intact while normalizing text
that belongs only to project migration/history notes.

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

ACADEMIC_RULE = """<大学学籍与年级>
## 秀知院大学·学籍与年级
秀知院大学本科阶段的入学年龄不低于18岁。学生的课程、社团、学生会职责、毕业规划与社会活动均按照当前大学年级展开。

年级与行政课程组：
- 大四A组：风野、龙珠桃、子安燕、阿天坊梦、寺岛
- 大三A组：四宫辉夜、早坂爱
- 大三B组：白银御行、藤原千花、柏木渚、四条真妃、田沼翼、风祭豪、丰崎三郎、骏河昴
- 大三C组：纪加莲、火之口三铃、巨濑绘理香、朝日雫
- 大二A组：不知火衣、槙原梢
- 大二B组：石上优、伊井野弥子、小野寺丽、大佛小钵
- 大一B组：藤原萌叶、白银圭

校外大学生：
- 大友京子、荻野航：外部大学大二
- 四条帝：外部大学大三，与四条真妃、四宫辉夜处于同龄层
- 贝尔托瓦茨·贝奇：法国合作大学大四，并担任学生自治组织负责人

社会人士：
- 藤原丰实、早坂奈央、四宫雁庵、藤原大地、田沼正造等维持各自的家庭、职业与社会身份。

校园关系规则：
- 四宫辉夜与白银御行、藤原千花同属大三，但行政课程组不同；学生会事务与共同课程可以频繁交集，不默认视为固定同班。
- 石上优、伊井野弥子属于大二；子安燕等大四前辈拥有明确的年级差与前后辈关系。
- 校外大学生与社会人士不会被视为秀知院大学的常规在校生。

升学与未来规划：
- 大三开始显著进入研究室选择、推免、考研、实习与海外深造准备。
- 大四集中面对毕业研究、研究计划书、研究生院考试、就业面试与留学申请。
</大学学籍与年级>"""

EXTREME_RELATIONSHIP_RULE = """<关系崩坏极端结局>
## 关系崩坏极端结局
当<user>同时维持多段彼此排他的恋爱关系，并被相关对象掌握长期欺骗与出轨的确凿证据时，原本依赖信任维系的关系可能发生不可逆崩坏。

- 多名受骗者会根据各自性格、掌握的证据与彼此关系作出真实反应，不再配合维持表面的恋爱喜剧和平衡。
- 可能出现公开质问、断绝关系、报复、家族或社交层面的制裁，以及在极端情绪与现实条件共同作用下发生的危险冲突。
- 极端暴力绝不是默认结果，也不能凭空出现；只有人物动机、现场条件与事态升级足以支持时才可能发生。
- 一旦造成严重现实后果，后续关系与社会影响必须连续存在，不能在下一场景自动恢复原状。
</关系崩坏极端结局>"""

WORLD_RULE = """<Worldview_Boundary_and_Filter>
# 世界基本规律
秀知院大学及其周边社会属于现代现实世界。人物的优势来自学力、财力、家族资源、情报能力、身体素质、专业技能与社交手腕，不存在能够直接突破现实规律的超自然力量。

## 现实边界
- 不存在魔法、修仙、异能、真实读心、超自然催眠、科幻机甲或其他违反现实规律的能力。
- 四宫家等大型财阀能够通过金钱、人脉、安保与情报网络制造近似“无所不能”的效果，但其本质仍是现实社会资源。
- 除明确进入关系崩坏等极端现实冲突外，校园日常不会因为夸张的心理描写自动产生真实致命伤害。

## 头脑战与主观感受
角色会把一句问候、一次递物、座位选择、消息回复速度或眼神交锋体验成高度紧张的心理战。人物主观感受中可以出现棋盘、雷达、刀光剑影、爆炸、箭矢、审判庭等夸张意象；客观现实中发生的仍是普通校园与生活行为。

## 恋爱与社交逻辑
- 恋爱中的自尊、误会、嫉妒、试探、嘴硬与过度推理可以极度夸张，但人物不会因此失去既有性格、社会身份与长期记忆。
- 家世、成绩、社团、朋友、家庭与未来规划都会真实影响恋爱关系，任何感情进展都必须落在连续的人际互动上。
- 成年大学生之间可以自然出现恋爱、接吻、成人话题与带有性暗示的误会；这些内容服务于人物关系和校园生活，不会让整个世界失去原有的日常与群像重心。
</Worldview_Boundary_and_Filter>"""

CONTENT_OVERRIDES = {
    56: ACADEMIC_RULE,
    57: EXTREME_RELATIONSHIP_RULE,
    61: WORLD_RULE,
}

COMMENT_OVERRIDES = {
    56: "核心规则:<大学学籍与年级>",
    57: "核心规则:<关系崩坏极端结局>",
    61: "核心规则:<世界基本规律>",
    81: "局部变量初始化",
}

PROHIBITED_RUNTIME_MARKERS = (
    "授权母卡",
    "旧母卡",
    "原卡",
    "原作",
    "本世界书",
    "正式运行",
    "运行时",
    "升学重映射",
    "自动迁移",
    "世界线:秀知院大学AU",
    "秀知院大学AU",
    "（成年人）",
)


def sanitize_entry(source: dict) -> dict:
    entry = copy.deepcopy(source)
    entry_id = entry.get("id")

    if entry_id in CONTENT_OVERRIDES:
        entry["content"] = CONTENT_OVERRIDES[entry_id]
    else:
        content = entry.get("content", "")
        # Character profiles should state only facts that exist inside the world.
        content = re.sub(r"(?m)^世界线:[^\n]*\n", "", content)
        content = re.sub(r"(?m)^(年龄:\s*\d+\s*岁)[（(]成年人[）)]\s*$", r"\1", content)
        entry["content"] = content

    if entry_id in COMMENT_OVERRIDES:
        entry["comment"] = COMMENT_OVERRIDES[entry_id]
    else:
        entry["comment"] = entry.get("comment", "").replace("(多选一)", "")

    return entry


def assert_runtime_text_is_in_world(entries: list[dict]) -> None:
    failures: list[str] = []
    for entry in entries:
        content = entry.get("content", "")
        for marker in PROHIBITED_RUNTIME_MARKERS:
            if marker in content:
                failures.append(f"entry {entry.get('id')}: {marker}")
    if failures:
        raise RuntimeError("project-layer text leaked into runtime worldbook: " + "; ".join(failures))


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
        "name": "辉夜大小姐想让我告白 - 秀知院大学 v1.0",
        "description": "以东京秀知院大学为核心舞台的青春群像、校园生活与恋爱头脑战世界。",
        "scan_depth": 2,
        "token_budget": 0,
        "recursive_scanning": False,
        "extensions": {},
        "entries": entries,
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"PASS: {len(entries)} entries -> {OUTPUT.name}")
    print("PASS: runtime worldbook contains no project-layer migration markers")


if __name__ == "__main__":
    main()
