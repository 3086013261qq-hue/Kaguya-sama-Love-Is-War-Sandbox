# Kaguya Verdict MVU

《辉夜大小姐想让我告白》秀知院大学 × JoJo 极简 MVU 独立模块。

## 业务定位

MVU 只做两件事：

1. 双页 B 站视频锁屏；
2. `本日の勝敗 / 今日，是某某的败北。` 片尾判定牌 + 仓库 MP3 播放器。

不负责剧情推进，不复制世界书状态，不做地图、好感、战绩或多页仪表盘。

## 媒体

### 音乐

正式曲库：`mvu/music-manifest.v1.json`

- 默认主打歌：`岩崎琢 - Awake.mp3`
- `default_track_id = awake`
- `theme = true`
- 其余仓库 MP3 保留为可切换曲目。

播放生命周期继承《变形钢姬》成熟方案：

- 全局唯一 `<audio>`；
- UI重绘不创建第二实例；
- 用户点击“进入秀知院”后才开始主打歌；
- 返回锁屏时暂停音乐，避免与视频音轨冲突；
- 加载失败允许重试/切歌；
- 支持进度条与曲目选择。

### 视频锁屏

正式配置：`mvu/video-lockscreen-manifest.v1.json`

第1页：
- 《吉良吉影大小姐想让我告白~枯萎穿心！》
- B站短链：`https://b23.tv/y3zZF15`
- 主锁屏

第2页：
- 《【吊带袜JO使】~荒木庄的第一次钢管舞就献给你了☆》
- B站短链：`https://b23.tv/qKAKp5U`
- 彩蛋页

行为：

- 永远只允许1个 iframe；
- 翻页先销毁上一页 iframe；
- 左右滑 + 左右按钮并存；
- Android按钮触控区域 >=44px；
- 点击“进入秀知院”先销毁视频再进入 MVU；
- 返回锁屏恢复上次页码；
- 两页均保留“在 B 站打开”外链兜底。

### B站嵌入边界

当前两条来源是用户提供的 `b23.tv` 短链。运行层优先使用 `embed_url`（若后续补入官方 player.bilibili.com URL），否则使用短链 iframe。

B站页面/WebView可能因 CSP、X-Frame-Options、登录状态或网络策略拒绝站外 iframe。此类失败不得阻断：

- 翻页；
- 进入 MVU；
- Awake 播放器；
- `today_verdict` 显示。

因此外链按钮是正式兜底，不是临时调试按钮。

后续若取得两个视频固定 BV 号，应将 `mvu/video-lockscreen-manifest.v1.json` 补上官方：

`https://player.bilibili.com/player.html?bvid=<BV>&autoplay=0&muted=1&danmaku=0`

并保留短链作为 external fallback。

## 源码

- `src/player.mjs`：变形钢姬式单 audio 播放生命周期
- `src/lockscreen.mjs`：双页/单 iframe 视频锁屏
- `src/app.mjs`：锁屏→败北牌→播放器总装
- `src/styles.css`：移动端优先视觉

## MVU变量

业务变量仍只有：

```yaml
today_verdict: "今日，胜负未定。"
```

`app.mjs` 通过 `getVerdict()` 注入读取，不自行创建第二变量容器。正式整卡装配时由咩咩全栈原生 MVU 状态桥提供该值。

## 禁止事项

- 禁止锁屏同时创建两个视频 iframe；
- 禁止锁屏和 Awake 同时自动播放；
- 禁止每条消息创建新的 audio；
- 禁止 UI 点击直接修改 `today_verdict`；
- 禁止修改咩咩预设；
- 禁止自造第二套 MagVarUpdate / registrar。

## 当前状态

`KAGUYA_DUAL_VIDEO_LOCKSCREEN_MODULE: SOURCE_READY`

尚未声明真实 Android / SillyTavern PASS；需装入最终 Candidate 后由用户实机验收。
