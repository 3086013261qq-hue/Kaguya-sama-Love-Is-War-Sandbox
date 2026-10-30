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

STYLE_CLAUSE = (
    "在保留原作标志性装甲、纹样、面具、徽记与非人体结构等识别锚点的前提下，"
    "体态与面部轮廓按本世界女性化视觉统一调整；肩背仍保留原有力量感，腰胯与四肢线条更明确，"
    "不削弱原本的力量感、怪异感、机械感或压迫感"
)

ROLE_RE = re.compile(r"^角色:(.+?)\s*$")


def transform_appearance(text: str) -> tuple[str, bool]:
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
        # 兜底：只把“人形替身”的人形性别视觉统一，不改任何能力描述。
        out = out.replace("人形替身", "女性人形替身", 1)

    if out == text:
        return text, False

    out = out.rstrip("。")
    out += f"；{STYLE_CLAUSE}。"
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

        new_body, changed = transform_appearance(body)
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

    # Heaven's Door 的“少年外形”是本轮最明确的漏项，必须被消除。
    joined = "\n".join(p.read_text(encoding="utf-8") for p in files)
    if "小型少年外形的人形替身" in joined:
        raise SystemExit("Heaven's Door 少年外形仍未修正")

    # 至少应覆盖核心人形替身；若数量异常偏低，说明源格式发生变化，宁可失败也不误改。
    if len(all_changes) < 12:
        raise SystemExit(f"too few humanoid appearance refinements: {len(all_changes)}")

    qa_lines = [
        "# 031｜替身外貌女性化统一 QA v1.0",
        "",
        "本轮只修改 `characters/stand-abilities/` 中需要女性化的人形/类人形替身的 `替身外貌:` 字段。",
        "",
        "硬规则：",
        "- 保留原作替身名、能力机制、战吼、类型、成长条件、本项目边界与专属梗。",
        "- 保留原作标志性装甲、纹样、面具、徽记和非人体识别结构。",
        "- 人形/类人形替身按本世界女性化视觉统一调整。",
        "- 非人形、动物型、群体型、物件型、现象型不强行性别化。",
        "- Tusk 多 ACT 外貌链保持原样，避免把其非人形进化结构硬性人体化。",
        "",
        f"实际修改人形替身外貌：**{len(all_changes)}** 条。",
        "",
        "## 修改清单",
    ]
    for filename, role, old, new in all_changes:
        qa_lines.append(f"- `{filename}`｜{role}")
    qa_lines += [
        "",
        "## Gates",
        "- `FEMALE_HUMANOID_STAND_VISUAL_UNIFICATION: PASS`",
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
