# AnimeHub Phase 31 — Search Intent Report

> 日期：2026-08-30 · 分析：detail/franchise/episodes/watch-order 页的搜索意图覆盖与数据能力

## 1. 意图 → 承载 → 数据能力

| 意图组 | 示例查询 | 承载页面 | DB 数据支撑 | 覆盖判定 |
|---|---|---|---|---|
| Basic Entity | what is X / X anime / X series | /anime/{slug}/ | title/genre/year/status/episodes/score/studio | ✅ 完整 |
| Season | X season 1 / season 2 / final season | /anime-series/{slug}/（聚合） | "Season N" 独立条目（Re:Zero Season 2 等，DB 为独立行） | ✅ franchise 页聚合 |
| Episode | X episodes / how many episodes | /anime/{slug}/episodes/ + detail | episodes 表（119 部）+ anime.episodes | ✅ 完整 |
| Watch Order | X watch order / timeline | /watch-order/{slug}/ | 8 franchise 手工顺序 + franchise 匹配 | ✅ 完整 |
| Character/Cast | X characters / voice actors | detail Characters + /character/ | characters（476）+ voice_actors（341） | ✅ 有数据时显示 |
| Release Date | X release date | detail Anime Information | year + month（season 推导） | ✅ |
| Franchise Directory | X series list / all seasons | /anime-series/{slug}/ | franchise 关键词匹配（18 集群） | ✅ Phase 30 |

## 2. 关键数据能力确认

- **Episode 表无 air_date 字段** → episodes 页**不显示**播出日期（任务要求"不显示不可用字段"，现状正确）
- **无 season 字段列**（季为独立 DB 行）→ **不建季页**（避免重复 franchise/detail 意图）
- **characters 覆盖 119 部** → franchise 级角色聚合成本高，维持 franchise→detail→characters 路径
- **month 字段**存在（部分）→ Anime Information Release period 可显示 "Spring 2013" 级信息

## 3. 意图覆盖差距（本次已处理）

1. **Watch Order 深度**：detail FAQ 新增 "Where can I find the watch order?"（franchise 匹配时）
2. **Release Date 深度**：FAQ 新增 "When was X released?"（year 存在时）
3. **Episode 深度**：episodes 页新增 franchise/watch-order 内链（用户看完集数后找观看顺序）
4. **Entity 深度**：Anime Information 补充 Studio（实体事实完整化）

## 4. 未覆盖意图（明确不做）

| 意图 | 原因 |
|---|---|
| Season 聚合页（/anime/{base}/season/{n}/） | DB 无 season 字段列，season 关系已由 franchise 页承载；建页会制造低质重复 URL |
| air date（episodes） | Episode 表无该字段，不可虚构 |
| franchise 级 Characters | 覆盖仅 119 部 + 跨 5-20 部 fetch 成本高 |
| 逐集 detail（/episodes/{id}/） | 无独立集详情数据，且与 episodes 页意图重复 |

## 5. 结论

现有页面已覆盖全部 5 类核心意图（Basic Entity/Season/Episode/Watch Order/Character）。
本次在不新增 URL 的前提下，通过 FAQ 扩展 + 信息架构补全 + 内链优化提升各意图的页面内承载深度。
