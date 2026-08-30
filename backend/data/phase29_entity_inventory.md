# AnimeHub Phase 29 — Entity Inventory

> 生成于 2026-08-29 · 基于 DB 实测

## 实体清单

| 实体 | 数量 | 备注 |
|---|---|---|
| Anime | 1479 | 核心实体 |
| Franchise 集群（slug 前缀 ≥3 条）| **57** | AoT 8、MHA 6、Re:Zero 5、Fire Force 5、JJK 5、Slime 5、Gintama 5、Haikyuu 5 等 |
| 多季标记（Season/Final/Part/季）| 337 | |
| Movie 标记 | 74 | |
| Episodes | 952 条 / 119 部 | episode_number/title（video_url 占位不可用）|
| Characters | 476 / 119 部 | |
| Voice Actors | 341（513 关联）| |
| Studios | 264（110 个 count≥3）| |
| Genres | 459 组合字符串 | |
| Years | 46 | |
| Watch Order | 8 franchise | |
| Anime Series（franchise 页）| 1（Fate）| |

## 数据充分度

| 实体 | 数据完整度 | 说明 |
|---|---|---|
| Franchise Hub | ⭐⭐⭐⭐⭐ | 57 集群，多季/电影条目充足 |
| Season（作品季）| ⭐⭐⭐⭐ | 337 条 title 标记 |
| Episode | ⭐⭐ | 119 部有数据（8%）|
| Character | ⭐⭐⭐ | 476 实体（覆盖 119 部）|
| Voice Actor | ⭐⭐⭐ | 341 实体 |
| Studio | ⭐⭐⭐⭐ | 264 实体，110 个 ≥3 部 |
