# AnimeHub Phase 40-B — US SERP-Driven SEO Research

> 日期：2026-09-01 · 交付：研究（第一轮，无代码修改）

---

## 0. 数据可用性声明（非谈判规则）

### GSC 数据
```
No GSC query dataset available in repository.
```
- 仓库仅有 `gsc_us_export_template.csv`（**1 行示例值**：query="anime like attack on titan", impressions=128, clicks=5——**非真实数据**）与导出要求文档
- 无 Search Console API/凭据 → 本报告**不含任何 AnimeHub 真实 impression/click/position 数据**

### SERP 数据（工具限制明确标注）
| Source | 结果 |
|---|---|
| Google (hl=en&gl=us) | **HTTP 429** 全部失败 |
| DuckDuckGo HTML | **验证码** 全部失败 |
| Bing (setlang=en&cc=US) | 2/5 query 有效；长尾自然语言 query 解析失败（返回词典/无关首页） |

**SERP environment limitation 声明**：
- 本报告 SERP 数据来自 **Bing 英文结果集**，**不保证是真实 Google US geo SERP**
- 以下数据统一标记为 **SERP Observed (Bing EN, with limitation)**，**不得**冒充 "actual US Google SERP"
- 解析失败的 query 如实标记 `SERP fetch failed`

---

## 1. GSC 优先级框架（待真实数据）

无 GSC 数据时建立优先级**规则**（数据到位后套用）：

| 优先级 | 判定 | 动作 |
|---|---|---|
| P1 | impressions 高 + CTR 低 + position ≤10 | 先测 title/snippet/intent match |
| P2 | 已有 clicks | 分析什么有效，保持 |
| P3 | 美国 SERP 明确存在 + AnimeHub 内容匹配 | 内容缺口补齐 |
| P4 | Candidate keyword | 仅进实验，不批量 |

---

## 2. 有效 SERP 数据集 A — "best isekai anime"

**Data type: SERP Observed (Bing EN, with limitation)**

### Top results（英文 listicle 竞品集）
| # | 站点 | 类型 | 标题关键表达 |
|---|---|---|---|
| 1 | Ranker | Listicle | "The 20+ Greatest Isekai Anime You Should Be Watching" |
| 2 | FandomSpot | Listicle/Guide | "40 Best Isekai Anime Worth Watching (Our Top Recommendations)" |
| 3 | GameRant | Listicle | "The 40 Best Isekai Anime Of All Time, Officially Ranked" |
| 4 | AniGround | Listicle | "Top 50 Best Isekai Anime You Need to Watch in 2026 (Ranked)" |
| 5 | Fiction Horizon | Listicle | "The 10 Best Isekai Anime of All Time" |
| 6 | CBR | Listicle | "The 40 Best Isekai Of All Time, Ranked" |
| 7 | **MyAnimeList** | **Database 分类页** | "Isekai - Anime - MyAnimeList"（genre 列表页） |
| 8 | MyAnimePulse | Listicle | "Best Isekai Anime Series & Movies"（community score 排序） |
| 9 | AnimeFacts101 | Listicle | "The 50 Best Isekai Anime of All Time, Ranked (2026)" |
| 10 | Comic Basics | Listicle | "Best Isekai Anime of All Time, Ranked" |

### Observed SERP terms（Top results 实际反复用词）
- "best isekai anime"（实体）
- "of all time / ranked / top recommendations"
- "should be watching / need to watch"
- "what is isekai"（2 个结果含定义段）

### SERP Observed Modifiers（真实存在于 SERP）
- ranked / of all time / best / recommendations

### 竞争结构
- **9/10 是 editorial listicle**（手工排名 + 推荐理由）
- 1/10 是数据库 genre 分类页（MAL）
- **无单一"权威定义+权威列表"页面**——各站点质量参差

### 内容缺口（Gap 分析）
- **Gap A（用户明确需要，Top 普遍浅）**：多数 listicle 每部只有 1-2 句推荐理由；缺乏"为什么值得看 + 适合谁"的实体级理由
- **Gap C（无用户需求证据）**：无需在每部 anime 加 isekai 定义段落

### AnimeHub 现有覆盖
- `/best-anime/isekai/`（存在，score 排序 + 每部 detail 链接）
- AnimeHub 优势：**数据库驱动**（真实 score/年份/genre）+ 每部链接到 detail（深度信息）

### 推荐方向（Candidate）
- 在 `/best-anime/isekai/` 每部条目下增加**数据库驱动的 1 行理由**（共享 genre/year/score 信号），避免 editorial 主观
- 这属于 SERP-informed + 现有页面增强，**不新建 URL**
---

## 3. 有效 SERP 数据集 B — "jujutsu kaisen characters"

**Data type: SERP Observed (Bing EN, with limitation)**

### Top results（Character 意图竞品集）
| # | 站点 | 类型 | 说明 |
|---|---|---|---|
| 1 | Fandom Wiki | Wiki | "List of Characters" 全角色列表 |
| 2 | jjk.guide | Guide | "All 140 Characters"（含 grade/technique/affiliation/status） |
| 3 | Fandom Wiki | Wiki | Category: Characters |
| 4 | Wikipedia | Wiki | "List of Jujutsu Kaisen characters"（角色+声优） |
| 5 | AniBase | Database | "82 Characters, voice actors, birthdays" |
| 6 | jjkdle.net | Database | Character 数据库（cursed energy/grade/stats） |
| 7 | Otaku-Senpai | Guide | "Complete Character Guide"（74 角色，能力/人气） |
| 8 | Oricon | Listicle | "JJK Characters List (names/heights/birthdays)" |
| 9 | jjkppdb.com | Database | 游戏角色列表 |
| 10 | MyAnimeList | Database | Manga Characters & Staff 页 |

### Observed SERP terms
- "jujutsu kaisen characters"（实体）
- "list of characters"
- "all X characters"
- "character guide / profiles / voice actors / birthdays / status / grade"

### 竞争结构
- **3 类页面**：Wiki 列表页 / 游戏数据库 / editorial guide
- **共同特征**：结构化角色数据（name + role + 简要属性）为主，非长文
- 声优（voice actors）在 Wikipedia/MAL/AniBase 出现
---

## 4. 未获有效 SERP 的 query（如实标记）

| Query | 意图 | SERP 结果 |
|---|---|---|
| attack on titan watch order | Watch Order | `SERP fetch failed`（Bing 返回词典结果） |
| anime like attack on titan | Similar | `SERP fetch failed`（Bing 返回流媒体首页） |
| how many episodes does attack on titan have | Episode count | `SERP fetch failed`（Bing 返回词典） |
| rezero watch order | Watch Order | `SERP fetch failed`（Bing 返回 ChatGPT 无关页） |

**不因 fetch 失败就编造 SERP 数据。** 这些意图的竞品结构来自 Phase 38 benchmark（MAL/IMDb 已验证：watch order 由 franchise guide 承载、episode count 由 detail/stats 承载）——标记为 **Inferred**。
---

## 6. 语言自然度检查（Inferred 判断）

- `/best-anime/isekai/` 现有文案（Phase 32 检查过英文）无"anime information/introduction"式中文直译
- 各页 title 均为自然英文模板（Phase 32 CTR 审计通过）
- 待真实 GSC 数据验证 CTR 后再评估是否有不自然表达

---

## 7. 第一轮实验设计（Candidate，未执行）

**前提**：无真实 GSC → 无法建立 Before/After 指标。本轮**只做研究，不实施**。

实验框架（数据到位后执行）：
1. 选 5-10 页（有 US impressions + position ≤30 + 明确意图）
2. Before 记录：URL/query/impressions/clicks/CTR/position/title/H1/meta
3. 每页最多 2 个变量（如 title + description），URL/canonical/schema 不变
4. 30 天后按 GSC 评估
5. 若结果不明确 → DO NOT BATCH

---

## 8. 禁止事项确认（已遵守）

- ✅ 未把中文关键词翻译冒充美国关键词
- ✅ 未编造搜索量（无 "monthly search volume" 声明）
- ✅ 未称 Bing 结果是 "actual US Google SERP"
- ✅ 未批量生成页面
- ✅ 未为 SERP query 新建 URL
- ✅ 未修改任何代码/数据

---

## 9. 下一步（需真实数据）

1. **获取真实 GSC CSV**（US + Query + Page + 28 天）→ 套用 P1-P4 优先级
2. **真实 Google US SERP**（有 US geo 环境）→ 替换本报告的 Bing 数据
3. 确认 2 个 Candidate 方向（best-anime 理由行 / JJK 角色数据扩充）是否有真实 gap 证据


---

## 5. Query → Page Intent Mapping（AnimeHub 现有能力，不新建 URL）

| Query 意图 | 主意图 | AnimeHub 最佳页面（现有） |
|---|---|---|
| entity / {anime} | 实体信息 | `/anime/{slug}/` |
| {anime} episodes / how many | 集数 | `/anime/{slug}/`（Anime Information + episodes 链接） |
| {anime} characters | 角色 | `/anime/{slug}/`（Characters 区）→ `/character/{slug}/` |
| {anime} voice actors | 声优 | detail Characters 声优内链 → `/voice-actor/{slug}/` |
| {anime} watch order | 顺序 | `/watch-order/{slug}/`（8 franchise） |
| {franchise} series | 系列全景 | `/anime-series/{slug}/` |
| best {genre} anime | 榜单 | `/best-anime/{category}/` |
| anime like X | 相似 | `/anime/{slug}/similar/` |
| {year} anime | 年份 | `/years/{year}/` |

**One search intent → One canonical page**，避免关键词自相残杀。


### 内容缺口
- **Gap A**：多数站点角色页是"列表"，缺乏"该角色出现在哪些季/集"的交叉信息；中文/日文名辅助少
- **Gap B**：只有少数站有"角色→声优→该声优其他角色"的反向网络（MAL 有，AniBase 部分有）

### AnimeHub 现有覆盖
- `/anime/jujutsu-kaisen/` detail 页 Characters 区（SSR，含声优内链）
- `/character/{slug}/` 角色实体页（含同作品其他角色、声优链接）
- `/voice-actor/{slug}/` 声优页
- **缺口**：无"全部角色"聚合列表（只有 detail 页内嵌区）；角色数量少（DB 覆盖有限）

### 推荐方向（Candidate）
- 提升 JJK 等热门 anime 的**角色数据覆盖**（数据任务，非页面模板）
- detail 页 Characters 区已是正确形态；增强方向是**数据量**而非结构

