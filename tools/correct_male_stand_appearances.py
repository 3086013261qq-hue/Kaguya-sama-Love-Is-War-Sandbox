from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CORRECTIONS = {
    "characters/stand-abilities/001_学生会核心六人_替身能力_v0.1.md": {
        "白银御行": (
            "替身外貌:高大强壮的女性人形替身，整体带有近似护甲的流线结构；头部与肩胸区域大量使用心形、圆角和金属饰件意象，双眼锐利，整体兼具健壮战士与装饰性铠甲的观感；女性化后采用高挑、结实的运动员式战斗体，肩背和手臂保留Crazy Diamond的爆发力，腰线与腿部比例更利落，心形装饰仍是视觉中心。",
            "替身外貌:高大强壮的人形替身，整体带有近似护甲的流线结构；头部与肩胸区域大量使用心形、圆角和金属饰件意象，双眼锐利，整体兼具健壮战士与装饰性铠甲的观感。",
        ),
    },
    "characters/stand-abilities/002_第二批六人_替身能力_v0.1.md": {
        "白银父": (
            "替身外貌:高大、极度健壮的女性人形替身，体格与服装轮廓都带有强烈的DIO式压迫感，同时混入潜水/航海装备意象；头部佩戴覆盖额头与上半脸的锐角头盔，正面只留下倒三角形的脸部区域，四肢与腰部带厚重装甲感；女性化后呈高大健壮的重装战士轮廓，锐角头盔、潜水航海意象与厚重装甲不变，肩背宽阔、腰部收束，仍保留The World近乎霸道的压迫感。",
            "替身外貌:高大、极度健壮的人形替身，体格与服装轮廓都带有强烈的DIO式压迫感，同时混入潜水/航海装备意象；头部佩戴覆盖额头与上半脸的锐角头盔，正面只留下倒三角形的脸部区域，四肢与腰部带厚重装甲感。",
        ),
        "田沼翼": (
            "替身外貌:体型很小的矮人式女性机械人形替身，通常趴在使用者背后或肩上；头部像倒扣的桶，眼孔大小不一，下颚由螺栓固定并露出细小尖牙，头顶伸出带绳状“头发”的空心圆筒，身体以细肢、肩甲和链条般的脊柱连接；女性化后更接近趴在肩头的小型机械少女/妖精，桶状头部、大小眼孔、螺栓下颚、绳状头发与链条脊柱全部保留，轮廓轻巧而古怪。",
            "替身外貌:体型很小的矮人式机械人形替身，通常趴在使用者背后或肩上；头部像倒扣的桶，眼孔大小不一，下颚由螺栓固定并露出细小尖牙，头顶伸出带绳状“头发”的空心圆筒，身体以细肢、肩甲和链条般的脊柱连接。",
        ),
    },
    "characters/stand-abilities/003_第三批六人_替身能力_v0.1.md": {
        "四宫雁庵": (
            "替身外貌:真身是带机器人质感的女性化人工人形替身：躯干宽大、手臂细长呈管状，身体布满等距圆环状脊纹，腕部生有长而弯曲的刀片，扁平椭圆头部只有硬币般的双眼与金属框架；对普通人则常以89岁老者“明负悟”的人类伪装出现；女性化只作用于真身的机械人体比例，宽躯干、管状长臂、环状脊纹、腕刀和硬币状双眼全部保留；对普通人的89岁老者“明负悟”伪装维持原设，不随真身体态改变。",
            "替身外貌:真身是带机器人质感的人工人形替身：躯干宽大、手臂细长呈管状，身体布满等距圆环状脊纹，腕部生有长而弯曲的刀片，扁平椭圆头部只有硬币般的双眼与金属框架；对普通人则常以89岁老者“明负悟”的人类伪装出现。",
        ),
    },
}


def main() -> None:
    changed = []
    for rel, roles in CORRECTIONS.items():
        path = ROOT / rel
        text = path.read_text(encoding="utf-8")
        for role, (wrong, correct) in roles.items():
            if wrong not in text:
                raise SystemExit(f"expected feminized male appearance not found: {role}")
            text = text.replace(wrong, correct, 1)
            changed.append(role)
        path.write_text(text, encoding="utf-8")

    if changed != ["白银御行", "白银父", "田沼翼", "四宫雁庵"]:
        raise SystemExit(f"unexpected correction list: {changed}")

    qa = ROOT / "qa" / "031_替身外貌女性化统一QA_v1.0.md"
    q = qa.read_text(encoding="utf-8")
    q = q.replace("实际精修人形替身外貌：**19** 条。", "实际精修女性人形/类人形替身外貌：**15** 条。")
    for item in [
        "- `001_学生会核心六人_替身能力_v0.1.md`｜白银御行\n",
        "- `002_第二批六人_替身能力_v0.1.md`｜白银父\n",
        "- `002_第二批六人_替身能力_v0.1.md`｜田沼翼\n",
        "- `003_第三批六人_替身能力_v0.1.md`｜四宫雁庵\n",
    ]:
        q = q.replace(item, "")
    q = q.replace(
        "- `HEAVENS_DOOR_BOY_APPEARANCE_REMOVED: PASS`",
        "- `HEAVENS_DOOR_BOY_APPEARANCE_REMOVED: PASS`\n- `MALE_STAND_APPEARANCE_UNCHANGED: PASS`",
    )
    qa.write_text(q, encoding="utf-8")
    print("restored male Stand appearances:", ", ".join(changed))


if __name__ == "__main__":
    main()
