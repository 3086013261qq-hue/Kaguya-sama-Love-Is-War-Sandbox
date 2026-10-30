# 030 双视频锁屏与 Awake 播放器源码 QA v1.0

基线：`Kaguya-sama-Love-Is-War-Sandbox/main`

本轮范围：MVU 独立源码层，不含最终整卡 Candidate，不冒充 Android / SillyTavern 实机验收。

## 媒体

- [x] `岩崎琢 - Awake.mp3` 已存在于 `mvu/media/music/`
- [x] `mvu/music-manifest.v1.json` 存在
- [x] `default_track_id = awake`
- [x] Awake `theme = true`
- [x] 其余6首仓库 MP3 保留为可切换曲库
- [x] 音频 URL 使用 HTTPS raw.githubusercontent.com
- [x] 音频 URL 锁定到用户上传完成后的固定 commit `40f6e52e9c68beb497b073c0676fee8d69686594`

## 播放器生命周期

- [x] 复用《变形钢姬》单 `<audio>` 生命周期思路
- [x] UI 重绘不创建第二音频实例
- [x] 锁屏阶段不自动播放 Awake
- [x] 点击“进入秀知院”后才触发 `player.enter()`
- [x] 返回锁屏时先暂停音频
- [x] 支持上一首 / 下一首 / 曲目选择 / 播放暂停 / seek
- [x] 加载失败有状态反馈

## 双视频锁屏

- [x] 视频页固定为2页
- [x] 第1页：吉良吉影大小姐想让我告白~枯萎穿心！
- [x] 第2页：【吊带袜JO使】~荒木庄的第一次钢管舞就献给你了☆
- [x] 默认页 = 1/2
- [x] 第2页标记为彩蛋页
- [x] 同时最多只存在1个 iframe
- [x] 翻页前销毁旧 iframe
- [x] 进入 MVU 前销毁 iframe
- [x] 返回锁屏恢复上次页码
- [x] 左右滑手势存在
- [x] 左右按钮存在
- [x] 主要按钮触控区域 >=44px
- [x] 每页都有 B站外链兜底

## B站嵌入风险边界

当前用户提供的是两条 `b23.tv` 短链。

由于当前施工环境无法可靠解析短链到固定 BV 号，源码采用：

1. 若 manifest 后续存在 `embed_url`，优先使用官方嵌入地址；
2. 否则使用短链 iframe 尝试加载；
3. 无论 iframe 是否受 B站 CSP/X-Frame/WebView 策略阻断，均保留“在 B站打开”外链；
4. 视频失败不得阻断进入 MVU 或音乐播放器。

固定 BV 号补齐后，应将 `embed_url` 切换到 `player.bilibili.com/player.html?...`，再做 Android 实机验证。

## 败北 MVU

- [x] 业务变量保持唯一：`today_verdict`
- [x] 默认：`今日，胜负未定。`
- [x] UI 只读取，不从按钮写变量
- [x] 败北牌为单页，无Tab/地图/好感/战绩冗余
- [x] 未修改157条业务世界书
- [x] 未修改咩咩预设

## 结论

`DUAL_VIDEO_LOCKSCREEN_SOURCE_QA: PASS`

`AWAKE_THEME_PLAYER_SOURCE_QA: PASS`

`SINGLE_AUDIO_INSTANCE_POLICY: PASS`

`SINGLE_VIDEO_IFRAME_POLICY: PASS`

`TODAY_VERDICT_MINIMAL_BUSINESS: PASS`

`BILIBILI_OFFICIAL_EMBED_BVID_RESOLUTION: PENDING`

`ANDROID_SILLYTAVERN_REAL_DEVICE_PASS: NOT_RUN`
