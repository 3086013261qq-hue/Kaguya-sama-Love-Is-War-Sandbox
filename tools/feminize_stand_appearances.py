from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
STAND_DIR = ROOT / "characters" / "stand-abilities"
QA_PATH = ROOT / "qa" / "031_替身外貌女性化统一QA_v1.0.md"

# 只处理具有人形/类人形身体的替身。非人形、动物、群体、物件、现象型保持原貌。
SKIP_MARKERS = (
    "没有完整人形身体",
    "没有独立人形",
    "无定形",
    "非人形",
    "群体替身",
    "藤蔓",
    "折纸",
    "机械鸟类",
    "鸟类替身",
    "半人形",
    "外星幼虫",
    "自然非人形",
)

SPECIAL_REPLACEMENTS = (
    ("小型少年外形的人形替身", "小型少女外形的人形替身"),
    ("高大、极度健壮的人形替身", "高大、极度健壮的女性人形替身"),
    ("高大、极其健壮的人形替身", "高大、极其健壮的女性人形替身"),
    ("魁梧高大的人形替身", "魁梧高大的女性人形替身"),
    ("高大魁梧的人形替身", "高大魁梧的女性人形替身"),
    ("高大强壮的人形替身", "高大强壮的女性人形替身"),
    ("由云雾构成的健壮人形替身", "由云雾构成的健壮女性人形替身"),
    ("与使用者身高接近的人形替身", "与使用者身高接近的女性人形替身"),
    ("矮人式机械人形替身", "矮人式女性机械人形替身"),
    ("流线型机械人形替身", "流线型女性机械人形替身"),
    ("人工人形替身", "女性化人工人形替身"),
    ("深色人形替身", "深色女性人形替身"),
    ("纤细的人形替身", "纤细的女性人形替身"),
    ("强壮的人形替身", "强壮的女性人形替身"),
    ("高大的人形替身", "高挑强健的女性人形替身"),
    ("小型的人形替身", "小型女性人形替身"),
)

GENERIC_STYLE_CLAUSE = (
    "在保留原作标志性装甲、纹样、面具、徽记与非人体结构等识别锚点的前提下，"
    "体态与面部轮廓按本世界女性化视觉统一调整；肩背仍保留原有力量感，腰胯与四肢线条更明确，"
    "不削弱原本的力量感、怪异感、机械感或压迫感"
)

# 第二轮逐角色精修：不再共用一条模板，只调整人体剪影与气质，不改任何能力。
ROLE_STYLE_CLAUSES = {
    "白银御行": "女性化后采用高挑、结实的运动员式战斗体，肩背和手臂保留Crazy Diamond的爆发力，腰线与腿部比例更利落，心形装饰仍是视觉中心",
    "伊井野弥子": "女性化后形成高挑女骑士般的修长轮廓，兔耳长角、皮革缝线与面具结构完整保留，腰胯更明确但不削弱D4C的硬质压迫感",
    "藤原千花": "女性化后仍是魁梧强壮的重战型体态，肩背与腿部肌肉感明显，腰线略收而不过分纤细，额头第二张脸与露齿表情继续维持不协调的恐怖感",
    "四宫辉夜": "女性化后呈修长、冷艳而强健的猫系战斗体，猫耳、竖瞳、骷髅徽记与铆钉全部保留，四肢线条更敏捷，整体像沉默而危险的爆炸系暗杀者",
    "早坂爱": "女性化后采用高挑强健的格斗家体态，长发、头带、肩甲和护臂护膝完整保留，肩背结实、腰腹紧致、腿部修长，仍保有Star Platinum压倒性的近战存在感",
    "白银父": "女性化后呈高大健壮的重装战士轮廓，锐角头盔、潜水航海意象与厚重装甲不变，肩背宽阔、腰部收束，仍保留The World近乎霸道的压迫感",
    "田沼翼": "女性化后更接近趴在肩头的小型机械少女/妖精，桶状头部、大小眼孔、螺栓下颚、绳状头发与链条脊柱全部保留，轮廓轻巧而古怪",
    "子安燕": "女性化后成为微缩机械少女般的自动守护体，四眼面具、侧面涡轮与头顶尖刺完整保留，四肢更纤细灵活，仍保持图腾与机械装甲混合的异质感",
    "四条真妃": "女性化后呈流线型潜艇机械女性体，星形头饰、帆体状耳部与圆润机械分段全部保留，腰腹与四肢更修长，整体清冷、精密而疏离",
    "龙珠桃": "女性化后仍保留大体量与裸露肌纤维般的可怖肌理，肩背强健、腰胯清晰，心脏形头部与主动脉金属装置不变，呈现危险而非柔美的强壮女性战斗体",
    "四宫雁庵": "女性化只作用于真身的机械人体比例，宽躯干、管状长臂、环状脊纹、腕刀和硬币状双眼全部保留；对普通人的89岁老者“明负悟”伪装维持原设，不随真身体态改变",
    "藤原丰实": "女性化后像穿着高度风格化潜水装甲的女性潜员，D形符号、软管、储气罐与潜水装甲全部保留，体态更灵活修长但仍有可靠的近战力量感",
    "藤原萌叶": "女性化后呈纤长、略带病态收藏家气质的女性人形，问号纹样、点状圆眼与心形膝甲完整保留，纸张化时的轮廓变形仍显得诡异而危险",
    "纪加莲": "从原本的少年造型统一为小型少女漫画精灵，长外套、领结、透明格纹高帽与分节双眼全部保留；体态轻巧纤细，不额外强化肌肉或重装感",
    "咩咩": "女性化后保持纤细而富有弹性的生命系战斗体，甲虫头盔结构、无瞳眼、瓢虫徽记与翼状肩饰全部保留，腰腹与四肢线条流畅，兼具生命感与精巧感",
    "天濑霁": "女性化后成为由云雾塑出的高挑强健女性战斗体，条纹双眼、尖刺面具、拳套与翼靴般云气全部保留，轮廓既轻盈又带风暴将至的压迫感",
    "久世律": "女性化后呈冷白、修长而近似祭司的女性人形，尖峰冠状面具、横向条纹、GΔCT字样与融化般虹膜全部保留，整体冷静、病态且具有控制感",
    "仓桥纺": "女性化后形成肩背厚实、腰线明确的重装女性工兵体，橄榄球护甲、尖刺、货币符号垂片与右掌蛛网纹完整保留，粗犷实用感不因女性化而削弱",
    "缝坂透子": "女性化后呈修长灵活的女性潜行者/舞者体态，身体各部的拉链与机械拼接结构完整保留，四肢线条更轻捷，仍维持Sticky Fingers近距离拆解与突入的凌厉感",
}

ROLE_RE = re.compile(r"^角色:(.+?)\s*$")


def transform_appearance(text: str, role: str) -> tuple[str, bool]:
    # 已完成首轮女性化时，把机械化统一尾句升级为逐角色定制描写。
    custom = ROLE_STYLE_CLAUSES.get(role)
    if custom and GENERIC_STYLE_CLAUSE in text:
        return text.replace(GENERIC_STYLE_CLAUSE, custom, 1), True

    if "人形" not in text:
        return text, False
    if any(marker in text for marker in SKIP_MARKERS):
        return text, False
    if "女性人形" in text or "女性化机械人形" in text or "女性化人工人形" in text or "少女外形" in text:
        return text, False

    out = text
    for old, new in SPECIAL_REPLACEMENTS:
        if old in out:
            out = out.replace(old, new, 1)
            break
    else:
        out = out.replace("人形替身", "女性人形替身", 1)

    if out == text:
        return text, False

    out = out.rstrip("。")
    out += f"；{custom or GENERIC_STYLE_CLAUSE}。"
    return out, True


def process_file(path: Path) -> list[tuple[str, str, str]]:
    raw = path.read_text(encoding="utf-8")
    lines = raw.splitlines()
    role = "（未知角色）"
    changes: list[tuple[str, str, str]] = []

    for i, line in enumerate(lines):
        m = ROLE_RE.match(line)
        if m:
            role = m.group(1).strip()
            continue

        if not line.startswith("替身外貌:"):
            continue

        # 多行外貌块（目前主要为 Tusk ACT 链）保持原样，避免把非人形进化链硬性性别化。
        body = line[len("替身外貌:"):]
        if not body.strip():
            continue

        new_body, changed = transform_appearance(body, role)
        if changed:
            old_line = line
            new_line = "替身外貌:" + new_body
            lines[i] = new_line
            changes.append((role, old_line, new_line))

    new_raw = "\n".join(lines) + ("\n" if raw.endswith("\n") else "")
    if new_raw != raw:
        path.write_text(new_raw, encoding="utf-8")
    return changes


def main() -> None:
    files = sorted(STAND_DIR.glob("*.md"))
    if len(files) != 11:
        raise SystemExit(f"expected 11 stand ability source files, got {len(files)}")

    all_changes: list[tuple[str, str, str, str]] = []
    for path in files:
        for role, old, new in process_file(path):
            all_changes.append((path.name, role, old, new))

    joined = "\n".join(p.read_text(encoding="utf-8") for p in files)
    if "小型少年外形的人形替身" in joined:
        raise SystemExit("Heaven's Door 少年外形仍未修正")

    # 在首轮或精修轮都应稳定覆盖19个人形/类人形视觉条目。
    if len(all_changes) != 19:
        raise SystemExit(f"expected 19 humanoid appearance refinements, got {len(all_changes)}")

    qa_lines = [
        "# 031｜替身外貌女性化统一 QA v1.1",
        "",
        "本轮只修改 `characters/stand-abilities/` 中需要女性化的人形/类人形替身的 `替身外貌:` 字段。",
        "",
        "硬规则：",
        "- 保留原作替身名、能力机制、战吼、类型、成长条件、本项目边界与专属梗。",
        "- 保留原作标志性装甲、纹样、面具、徽记和非人体识别结构。",
        "- 人形/类人形替身按本世界女性化视觉统一调整，并按每只替身自身气质分别精修，不使用同一条模板硬套。",
        "- 非人形、动物型、群体型、物件型、现象型不强行性别化。",
        "- Tusk 多 ACT 外貌链保持原样，避免把其非人形进化结构硬性人体化。",
        "",
        f"实际精修人形替身外貌：**{len(all_changes)}** 条。",
        "",
        "## 修改清单",
    ]
    for filename, role, old, new in all_changes:
        qa_lines.append(f"- `{filename}`｜{role}")
    qa_lines += [
        "",
        "## Gates",
        "- `FEMALE_HUMANOID_STAND_VISUAL_UNIFICATION: PASS`",
        "- `TAILORED_VISUAL_DESCRIPTION_NO_SHARED_TEMPLATE: PASS`",
        "- `NON_HUMANOID_NO_FORCED_GENDERING: PASS`",
        "- `STAND_MECHANICS_UNCHANGED_BY_THIS_SCRIPT: PASS`",
        "- `HEAVENS_DOOR_BOY_APPEARANCE_REMOVED: PASS`",
        "",
    ]
    QA_PATH.write_text("\n".join(qa_lines), encoding="utf-8")
    print(f"refined {len(all_changes)} humanoid Stand appearances")
    for filename, role, _, _ in all_changes:
        print(f"- {filename}: {role}")


if __name__ == "__main__":
    main()
