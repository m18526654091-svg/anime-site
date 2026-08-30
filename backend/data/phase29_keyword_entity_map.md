# AnimeHub Phase 29 — Keyword Entity Map

> 生成于 2026-08-29

## 实体 → 搜索意图 → 承载

| 实体 | Intent 示例 | 当前承载 | 缺口 |
|---|---|---|---|
| Anime | what is X / X episodes / X release date / X genre | ✅ detail（Entity Summary/Anime Information/Genres）| 无 |
| Season（作品季）| X season 1 / season 2 / final season | ⚠️ detail 标题/信息（无独立季页）| **Season 聚合页** |
| Franchise | X watch order / release order / chronological order | ✅ watch-order（8）+ anime-series（1）| **Franchise Hub 扩展**（57 集群）|
| Character | X character name / who voices X | ✅ /character/（476）| 增强（互链/英文）|
| Voice Actor | X works / anime roles | ✅ /voice-actor/（341）| 增强（Known for/Related）|
| Studio | X studio anime | ✅ /studio/（264）| 增强（count≥3 入 sitemap）|
| Episode | X episode 1 / episode list / how many episodes | ✅ /anime/{slug}/episodes/（Phase 28）| 数据覆盖低（119/1479）|

## 意图强度评估

| 意图 | 强度 | 理由 |
|---|---|---|
| franchise watch/release order | ★★★★★ | 高价值长尾 + 现成 watch-order 模式可复制 |
| season N | ★★★★ | 多季作品搜索稳定 |
| character/voice | ★★★★ | 高流量但数据覆盖 119 部 |
| studio | ★★★ | 中型长尾 |
| episode | ★★★ | 高意图但数据受限 |

## 结论
- **Franchise Hub（57 集群）是最强扩展方向**：数据充分 + 搜索价值高 + 模式已验证（Fate）
- Season 聚合页次之（337 条标记）
- Character/Voice/Studio 为增强型（不新建类型，强化现有页）
