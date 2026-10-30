# 《辉夜大小姐想让我告白｜秀知院大学 × 替身》
# Candidate2 实机返工施工单 v1.0

> 交接对象：Work 模式「静静」
> 
> 唯一仓库：`3086013261qq-hue/Kaguya-sama-Love-Is-War-Sandbox`
> 
> branch：`main`
> 
> 本施工单创建前最后确认基线 HEAD：`604ff287d06c0c32a5159a512da6f3f2233ed7e6`
> 
> 真实设备反馈来源：Android / SillyTavern Candidate1 实机导入。

---

## 0. 总原则

本轮不是重做世界书，也不是重新设计业务。

只做 **Candidate1 实机返工 → Candidate2**。

必须继续使用当前最新版「咩咩制卡包·全栈」原生结构：

- `chara_card_v3`
- 原生 `MVU`
- 原生 `MVU ZOD`
- 原生 `变量状态栏`
- 四条 MVU 系统世界书：
  - `[initvar]变量初始化勿开`
  - `[mvu_update]变量更新规则`
  - `[mvu_update]变量输出格式`
  - `变量列表`
- 两条原生正则：
  - `[MVU]去除变量更新显示`
  - `[MVU]去除正文底部占位符`
- 不得自造第二套 MagVarUpdate / registrar / state container。
- 不得修改咩咩预设。

本轮业务层冻结：

- 158 条业务世界书正文全部冻结，不允许为了修导入问题而重写内容。
- 30 条替身能力、44 人物、地点、时间线、蓝灯/绿灯、替身外貌与最新 JOJO 战斗演出蓝灯全部冻结。
- `today_verdict` 仍然是唯一 MVU 持久业务字段。
- 音乐播放进度、锁屏页码、视频状态全部继续只做前端临时状态。
- Awake 仍为默认主打歌。

**不要使用本轮聊天里误生成的“樱花海报/新锁屏海报”。该图作废。**

---

## 1. Candidate1 真实 Android / SillyTavern 反馈

用户已经真实导入 Candidate1，当前确认有四类问题。

### P0｜世界书在 SillyTavern UI 中显示为空

实机现象：

- 世界书名称可以看到：`辉夜大小姐想让我告白｜秀知院大学 × 替身｜咩咩全栈...`
- 但世界书分页显示 `1-0 ... 0`，实际条目数量为 0。
- Candidate1 构建脚本自己的 JSON 计数虽然显示 162 条，但这不能算通过。

这是本轮第一优先级。

#### 修复要求

1. 直接读取并保留正式业务世界书：
   `build/worldbook/辉夜大小姐_秀知院大学_替身版_worldbook_v1.0.0.json`
2. 业务 entries 必须仍为 158 条。
3. 再按咩咩全栈原生结构加入 4 条 MVU 系统世界书，最终应为 162 条。
4. 不允许手工重新生成 158 条正文。
5. 重点排查 **Character Card V3 内嵌 character_book 的真实 SillyTavern 兼容结构**，不要只做 `len(entries)==162` 的 JSON 自检。
6. 必须拿仓库/资料库中已经在 Android/SillyTavern 成功导入且世界书非空的咩咩全栈卡作为结构参照，逐字段比较：
   - `data.character_book`
   - entries 容器形状
   - entry id / keys / secondary_keys / comment / content / constant / selective / insertion_order / enabled / position / use_regex
   - extensions 中递归、depth、position、scan_depth 等字段
   - 是否存在 SillyTavern 需要但当前 Candidate1 缺失或类型错误的字段
7. 修复后必须做 PNG 反解：从 Candidate2 PNG 重新读取 `ccv3`，确认 `data.character_book.entries` 在反解 payload 内仍是 162 条。
8. 不得把“PNG 反解 162 条”冒充“真实 SillyTavern UI 显示 162 条”。最终实机 PASS 仍由用户 Android 验收确认。

Candidate2 最低静态门：

```text
BUSINESS_WORLDBOOK_ENTRIES = 158
MVU_SYSTEM_ENTRIES = 4
EMBEDDED_CHARACTER_BOOK_ENTRIES = 162
CCV3_ROUNDTRIP_CHARACTER_BOOK_ENTRIES = 162
```

---

## 2. 双视频页映射放反

用户实机确认：**当前两个 B 站视频实际内容与我们设定的页/标题映射放反了。**

不要只交换显示标题；必须核验实际 BV 内容后修 manifest。

用户原始意图顺序：

### 1 / 2 主视频

《吉良吉影大小姐想让我告白~枯萎穿心！》

### 2 / 2 彩蛋视频

《【吊带袜JO使】~荒木庄的第一次钢管舞就献给你了☆》

现有两个 BV：

- `BV1xP4y1B7iG`
- `BV1iD4y1U7ki`

Candidate1 已证明当前映射至少有一处相反。

#### 修复要求

- 实际打开/核对两个 BV 对应的真实视频标题与内容。
- 将正确的 `bvid / source_url / embed_url / title / role` 重新绑定。
- 最终 1/2 必须实际播放“吉良吉影大小姐想让我告白~枯萎穿心！”。
- 最终 2/2 必须实际播放“吊带袜JO使”。
- 仍保持单 iframe 生命周期：翻页先销毁旧 iframe，再加载新页。
- 视频必须用户手势后加载；外层总锁屏阶段不得预加载 B 站 iframe。
- B 站失败不得阻塞进入 MVU；保留“在 B 站打开”兜底。

---

## 3. 新增最外层「辉夜大小姐」总锁屏

用户明确要求：**在双视频页外面再加一层锁屏。**

新的 UI 层级固定为：

```text
[总锁屏：辉夜大小姐标志]
        ↓ 解锁
[双视频页 1/2 ↔ 2/2]
        ↓ 进入秀知院
[今日胜负 + 音乐播放器]
```

### 总锁屏视觉

方向：动画《辉夜大小姐想让我告白》的标志性视觉语言，不要做成通用网页登录页。

建议元素：

- 红 / 黑 / 米白主色
- 爱心、皇冠、细线框、恋爱头脑战式几何装饰
- 中央主标志/标题：`辉夜大小姐想让我告白`
- 副标：`秀知院大学 × JOJO`
- 可以有 `恋愛頭脳戦` / `LOVE IS WAR` 等极少量装饰字
- 解锁提示应精致，例如“上滑解锁”或中央触控徽记；不要大号俗气按钮
- Android 触控区域 ≥44×44px
- 总锁屏不播放音乐、不创建 B 站 iframe

实现要求：

- 总锁屏解锁状态只做当前聊天/前端会话状态，不写入 MVU。
- 新聊天重新出现总锁屏。
- 同一聊天后续楼层重绘不要每轮强制把用户重新踢回总锁屏。
- `CHAT_CHANGED` 时重置。

---

## 4. MVU 整体视觉必须重做

用户实机评价：**Candidate1 MVU 整体很丑。**

当前问题：

- 大面积奶白圆角网页卡片感过强。
- “返回锁屏”像普通 HTML 按钮。
- 视频页标题、分页、按钮、外链排版像通用网页组件。
- 内页“今日胜负”是一个大白块压在背景图中央，破坏画面。
- 播放器像普通表单/网页播放器，与辉夜风格脱节。

### Candidate2 视觉目标

关键词：

**辉夜大小姐动画片尾卡 / 恋爱头脑战 / 精致红黑米白 / 轻装饰 / 中央窄条 / 非通用网页组件**

不是 JOJO 漫画页，也不是古典欧式婚礼卡。

### 胜负页固定构图

继续使用已经生成并确认的“辉夜与白银左右对视、中央留白”背景图。

但中央判定必须重做：

- 不要大白矩形。
- 使用 **窄而修长的半透明/纸质竖条** 放在中央留白处。
- 竖条宽度尽量控制在画面 20%～28%。
- 顶部小字：`本日の勝敗`
- 中央主文：动态 `today_verdict`
- 判定文字应有动画片尾字幕感，不要粗黑大字像 PPT。
- `敗北` 印章缩小，只作为底部/侧下方点睛，不抢主文。
- 如果 verdict 为 `今日，胜负未定。`，不要强行显示一个巨大“败北”印章；可将印章弱化/隐藏。
- 背景人物不能被大块 UI 遮住。

### 播放器

沿用《变形钢姬》成熟单 Audio 生命周期逻辑，但视觉改成辉夜主题：

- 做成底部窄条/唱片信息带，而不是一个大白色表单盒。
- Awake 默认主打歌。
- 曲名 / 艺术家 / 播放暂停 / 上一首下一首 / 进度条 / 曲目选择都保留。
- 移动端优先，触控 ≥44px。
- 不得因为状态栏重绘创建第二个 audio。

### 视频页

- 仍为两页。
- 视频框可保留 16:9，但外围装饰重新做成辉夜风格。
- 页码、左右翻页、标题、外链与进入按钮视觉整合，不要像五个独立 HTML 控件。
- 页面上不要出现两个互相冲突的 `1/2` 页码。

---

## 5. MVU 功能冻结

Candidate2 不新增复杂业务状态。

Schema 仍应只有：

```js
export const Schema = z.object({
  today_verdict: z.string().prefault('今日，胜负未定。'),
}).prefault({
  today_verdict: '今日，胜负未定。',
});
```

模型更新规则仍然只允许：

```text
/today_verdict
```

不得新增：

- 视频页码
- 总锁屏是否解锁
- 音乐进度
- 当前曲目
- 当前日期
- 当前 NPC
- 好感/关系副本
- 战斗状态副本

这些都不是长期事实源。

---

## 6. 现有成熟媒体逻辑必须保留

音乐：

- 默认主打歌：`岩崎琢 - Awake`
- 当前仓库 7 首 MP3 曲库全部保留。
- 单一全局 audio。
- 同一聊天楼层重绘时允许续播。
- 切换聊天时停止并重置，不串音到别的聊天。

视频：

- 单 iframe。
- 用户手势后才加载。
- 翻页先销毁旧 iframe。
- 进入胜负页时销毁 iframe，避免视频后台继续发声。
- 返回视频页时按当前页重新创建。

---

## 7. Candidate2 构建与交付

必须生成：

1. `辉夜大小姐_秀知院大学_替身版_v1.0.0-candidate2.json`
2. `辉夜大小姐_秀知院大学_替身版_v1.0.0-candidate2.png`
3. Candidate2 QA

主 PNG 继续使用用户最终确认的 JOJO 学生会合照封面，不换图、不重新生成。

不要使用误生成的“樱花海报”。

如果仓库内封面二进制存在截断/损坏，禁止拿损坏副本重新压制；沿用 Candidate1 已确认的原始封面资产生成路径，或将最终 PNG 作为聊天附件交付。

主发行卡优先单 `ccv3` 完整 payload；可额外保留 compat-dual 备用，但必须与同一权威 JSON 同源。

---

## 8. QA 硬门

静态 QA 至少要求：

```text
CHARA_CARD_V3: PASS
BUSINESS_WORLDBOOK_158_UNCHANGED: PASS
MVU_SYSTEM_ENTRIES_4: PASS
EMBEDDED_CHARACTER_BOOK_162: PASS
CCV3_ROUNDTRIP_162: PASS
MVU_CORE_NATIVE_IMPORT: PASS
MVU_ZOD_NATIVE_IMPORT: PASS
INITVAR_DISABLED: PASS
MVU_SYSTEM_RECURSION_GUARDS: PASS
TODAY_VERDICT_ONLY_WRITABLE_PATH: PASS
OUTER_LOCKSCREEN_PRESENT: PASS
OUTER_LOCKSCREEN_NO_AUDIO_NO_IFRAME: PASS
VIDEO_MAPPING_VERIFIED: PASS
VIDEO_SINGLE_IFRAME: PASS
AWAKE_DEFAULT: PASS
SINGLE_AUDIO_LIFECYCLE: PASS
CHAT_CHANGE_AUDIO_RESET: PASS
VERDICT_VERTICAL_STRIP_LAYOUT: PASS
ANDROID_TOUCH_TARGETS_GE_44PX: PASS
```

但以下状态禁止在静态环境伪造：

```text
REAL_ANDROID_SILLYTAVERN_PASS
```

只有用户下载 Candidate2 后在真实 Android / SillyTavern 导入并确认：

- 世界书确实显示 162 条而不是 0
- 总锁屏显示正常
- 解锁进入双视频页
- 1/2 与 2/2 视频映射正确
- B 站播放器能用或可可靠兜底
- 进入秀知院后胜负页视觉正确
- Awake / 曲库正常
- 后续楼层 today_verdict 实时更新

才允许标记真实实机 PASS。

---

## 9. 禁止事项

本轮禁止：

- 重写 158 条业务世界书正文
- 重做人物 / 替身 / 时间线 / 地点
- 改 JOJO 战斗蓝灯正文
- 修改咩咩预设
- 自造第二 MVU 引擎
- 新增复杂状态机
- 换封面
- 使用误生成樱花海报
- 用“JSON里有162条”代替 SillyTavern 世界书兼容性修复
- 未经用户真实导入就标记 Android PASS

---

## 10. 本轮唯一目标

**让 Candidate2 在真实 Android / SillyTavern 中成为一张：世界书能正常显示、锁屏层级正确、双视频不放反、Awake正常播放、胜负页真正有《辉夜大小姐》味道的可导入完整卡。**
