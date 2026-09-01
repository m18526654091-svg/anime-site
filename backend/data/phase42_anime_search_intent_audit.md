# AnimeHub Phase 42 — Anime Detail Search-Intent Audit

> 日期：2026-09-01 · 范围：现有 Anime Detail 页意图覆盖审计（SSR 实测 8 个代表性 Anime）· 状态：✅ 覆盖已高度完整，无 high-confidence 空白需实现

## 1. 审计方法

对 8 个代表性 Anime（franchise/standalone/multi-season/movie/classic/current/big-cast）做 SSR 实测，检查 14 个意图/功能标记。

| Anime | 类型 |
|---|---|
| attack-on-titan | franchise、multi-season |
| steins-gate | standalone、popular |
| jujutsu-kaisen | multi-season、big-cast |
| princess-mononoke | movie |
| gintama | multi-season、franchise |
| hunter-x-hunter-2011 | classic、big-cast |
| kaiju-no-8 | current |
| cowboy-bebop | classic |

## 2. 意图覆盖矩阵（SSR 实测）

| 意图 | 区块/元素 | 8/8 页覆盖 | 条件化 |
|---|---|---|---|
| Entity | Entity Summary（H1 下事实句） | ✅ | — |
| Information | Anime Information（Type/Episodes/Status/Release/Genres/Score/Studio） | ✅ | — |
| Episodes | Episodes 链接（Anime Information 行） | ✅ | 有 episodes 时 |
| Genres | Genres 区块（英文 chip → best/categories） | ✅ | — |
| About | About This Anime | ✅ | — |
| FAQ | FAQPage JSON-LD（What/How many/When/Where watch order） | ✅ | 数据存在时 |
| Season/Franchise | Seasons & Related Entries（franchise 兄弟条目） | ✅（3/8） | 仅 franchise 匹配 |
| Characters | Characters 区块（角色卡+声优内链） | ✅ | 有角色数据时 |
| Voice Actors | 角色卡 Voiced by 内链 → /voice-actor/ | ✅ | 有 VA 数据时 |
| Watch Order | Explore More 条件链接 + FAQ | ✅（条件正确） | 仅 8 franchise |
| Franchise | Explore More 条件链接 + Seasons 区 | ✅（3/8） | 仅 18 franchise defs |
| Similar | Anime Like 链接 + Related Anime 区 | ✅ | — |
| Studio | Anime Information Studio 行 → /studio/ | ✅ | 有 studio 时 |
| Discover | Explore More（Trending/Discover/Best/Season/New/Year） | ✅ | — |
| Release | Anime Information Release period（season+year） | ✅ | — |

**验证细节**：
- watch-order 条件链接**正确**：AoT 有 `/watch-order/attack-on-titan/`；princess-mononoke（movie）仅有通用 `/watch-order/` 索引链接
- Seasons & Related Entries 仅 franchise 匹配的 3 页显示（AoT/JJK/Gintama）——**条件激活正确**
- 无空区块（数据缺失时区块自动隐藏）

## 3. 各意图族审计（Step 8-14）

### A. Episodes（Step 8）
- 数据：DB episodes 表（119 部）+ anime.episodes 字段
- detail 页：Anime Information Episodes 行（链接到 /episodes/）+ Watch Online 播放器（有 playData 时）
- FAQ："How many episodes does X have?"（Phase 31）
- 覆盖 ✅（有数据时）；无集数数据时不展示

### B. Season/Release（Step 9）
- Anime Information Release period（year+month→season）+ Release year chip
- Seasons & Related Entries（franchise 兄弟，按 year 排序）
- FAQ："When was X released?"
- 覆盖 ✅；不生成不存在的 season（数据驱动）

### C. Watch Order（Step 10）
- 8 franchise 有 /watch-order/ 页；detail Explore More 条件链接 + FAQ
- 简单 standalone（如 Steins;Gate）无 watch-order 区块——**正确**（无顺序复杂性不建）
- 覆盖 ✅

### D. Characters（Step 11）
- Characters 区块（SSR 角色卡）+ /character/{slug}/ 实体页
- English-first 显示（Phase 40-A）+ native 辅助
- 覆盖 ✅（有角色数据时）

### E. Voice Actors（Step 12）
- 角色卡 Voiced by → /voice-actor/{slug}/
- 明确：当前为**日语声优数据**（AniList JAPANESE voiceActors），不声称 English cast
- 覆盖 ✅

### F. Franchise/Series（Step 13）
- /anime-series/ 18 集群 + detail Seasons & Related Entries + Explore More 条件链接
- 覆盖 ✅；无重复页（title/franchise/series 均指向实体页）

### G. Similar/Discovery（Step 14）
- /similar/ 页 + Related Anime 区 + Explore More
- 覆盖 ✅

## 4. 结论

**detail 页已高度满足全部 7 个意图族**（Phase 31-37 累积）。条件化区块按数据激活，无空区块，无重复 URL。

**无 high-confidence 空白需要实现**——进一步优化应**由真实 GSC/SERP 证据驱动**（如某意图族的 title/CTR 问题），而非继续加区块。

## 5. 建议（Candidate，未实施）

1. 待真实 GSC 数据：识别高曝光低 CTR 的 detail 页 → 按意图族诊断（title/结构/内链）
2. 待真实 US SERP：验证各意图族的 SERP 页面类型与 AnimeHub title 措辞匹配度
3. 无证据前不新增区块/不改 title 模板
