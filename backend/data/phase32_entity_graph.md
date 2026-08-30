# AnimeHub Phase 32 — Entity Authority Graph（Top 7 实体）

> 日期：2026-08-30 · 验证：SSR 实测 7 实体链路（detail → franchise → watch-order → episodes → characters → similar）

## 1. 实体链路矩阵（SSR HTML 实测）

| 实体 | detail→franchise | detail→watch-order | detail→episodes | detail→similar | detail→characters | episodes→franchise | episodes→watch-order |
|---|---|---|---|---|---|---|---|
| Attack on Titan | ✅ | ✅ | ✅ | ✅ | ✅（有角色数据） | ✅ | ✅ |
| Bleach | ✅ | ✅ | ✅ | ✅ | ⚪ 无角色数据 | ✅ | ✅ |
| Jujutsu Kaisen | ✅ | —（无 watch-order 页，正确） | ✅ | ✅ | ⚪ | ✅ | — |
| Fate（stay night UBW） | ✅ | — | ✅ | ✅ | ⚪ | ✅ | — |
| Monster | —（单一作品，不建 franchise） | — | ✅ | ✅ | ⚪ | — | — |
| Frieren | ✅ | — | ✅ | ✅ | ✅ | ✅ | — |
| Re:Zero | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

> ✅ = 链接存在；⚪ = DB 无该作品角色数据（覆盖仅 119 部），**不虚构不补空区块**；— = 无该类型页面（意图不成立，不建低质页）

## 2. 链路质量分析

### Attack on Titan（完整权威链路示例）
```
Detail ─→ Franchise Hub（9 条目聚合）
  ├──→ Watch Order（8 步骤顺序指引）
  ├──→ Episodes（25 集列表）
  ├──→ Characters（角色→声优）
  └──→ Similar（recommendation）
```
Google 可从任一入口完整遍历实体知识：作品事实 → 系列全景 → 观看顺序 → 剧集 → 角色 → 推荐。

### 差异说明
- **Monster**：单一完整作品（无季/衍生）→ franchise 页意图不成立，detail 独立承载。链路 detail→episodes→similar 已闭合。
- **Fate**：多条目已由 franchise hub（12 条目）聚合，无 watch-order（时间线争议，Phase 9 决策不建）→ franchise 页为权威入口。
- **Characters 覆盖**：AoT/Frieren/Re:Zero 有角色数据（角色→声优内链完整）；Bleach/JJK/Fate/Monster 无角色数据 → 维持 detail 无该区块（Phase 28 零泄漏原则，不造数据）。

## 3. 高价值链接检查

| 链接 | 存在 | 说明 |
|---|---|---|
| detail → franchise | ✅ 18 franchise 匹配时（Explore More） |
| detail → episodes | ✅ Anime Information + Watch Online |
| detail → watch-order | ✅ 8 franchise 匹配时 |
| detail → characters | ✅ 数据存在时（角色→声优双向） |
| episodes → franchise/watch-order | ✅ Phase 31 |
| franchise → detail（每条目） | ✅ 18 页全条目 |
| franchise → watch-order | ✅ 5 个匹配 |
| similar → franchise | ✅ Phase 30 |
| similar → detail（每条推荐） | ✅ |

## 4. 结论

- 7 个 Top 实体（Step 3 清单）全部满足 detail→franchise→watch-order→episodes→characters→similar 链路（数据存在处）
- **无新增链接需求**（避免 link stuffing）；唯一可做是角色数据扩充（数据任务，非链接）
- 实体权威已由：结构化数据（TVSeries/FAQ/ItemList）+ 全链路内链 + 数据驱动正文共同构成
