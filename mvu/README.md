# MVU

当前正式方向：**双页视频锁屏 + 极简片尾判定牌 + Awake 主打歌播放器**。

本模块不承担剧情推进、不复制世界书状态、不做多页仪表盘。

## 唯一业务变量

- `today_verdict`：记录最新一次真正结算后的《辉夜大小姐》式片尾判定，例如“今日，是四宫辉夜的败北。”

## UI结构

1. 双页 B站视频锁屏：
   - 第1页：《吉良吉影大小姐想让我告白~枯萎穿心！》
   - 第2页：《【吊带袜JO使】~荒木庄的第一次钢管舞就献给你了☆》
   - 左右滑 + 左右按钮
   - 同时只允许1个 iframe
   - 独立“进入秀知院”按钮
2. `本日の勝敗`片尾判定牌
3. 仓库 MP3 播放器
   - 主打歌：`岩崎琢 - Awake.mp3`
   - 继承《变形钢姬》成熟的全局单一 `<audio>` 生命周期
   - 其余仓库歌曲保留为可切换曲库

## 正式配置

- `mvu/music-manifest.v1.json`
- `mvu/video-lockscreen-manifest.v1.json`
- `mvu/001_极简片尾判定MVU设计_v0.1.md`

## 独立源码模块

`modules/kaguya-verdict-mvu/`

包含：

- `src/player.mjs`
- `src/lockscreen.mjs`
- `src/app.mjs`
- `src/styles.css`
- `README.md`

## 技术底座

最终整卡继续使用咩咩制卡·全栈 v1.0.0 原生 MVU 九件套；不修改咩咩预设，不自造第二套 MagVarUpdate / registrar / 状态容器。

当前独立 UI 只通过 `getVerdict()` 读取 `today_verdict`；正式装配时再由咩咩全栈原生状态桥接入。

## B站嵌入边界

当前两条视频来源为用户提供的 b23.tv 短链。源码已经支持：

- `embed_url` 存在时优先官方嵌入；
- 否则短链 iframe 尝试；
- 每页永久保留“在B站打开”外链兜底；
- 视频加载失败不得阻断进入 MVU、败北牌或音乐播放器。

固定 BV 号与官方 `player.bilibili.com` 地址补齐后，再做真实 Android / SillyTavern 验收。

## 当前状态

- `DUAL_VIDEO_LOCKSCREEN_SOURCE_QA: PASS`
- `AWAKE_THEME_PLAYER_SOURCE_QA: PASS`
- `ANDROID_SILLYTAVERN_REAL_DEVICE_PASS: NOT_RUN`
