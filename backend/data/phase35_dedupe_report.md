# AnimeHub Phase 35 — Deduplication Report（Step 4）

> 日期：2026-08-30 · 目的：防止 Attack on Titan / 進撃の巨人 / Shingeki no Kyojin 被建为 3 个实体

## 1. 去重策略（导入前，P0）

| 检查维度 | 规则 | 命中数 |
|---|---|---|
| 1. External ID | anilist_id / mal_id 与 DB 匹配 | 478 |
| 2. Normalized English title | title 去标点/大小写/空白后匹配 | 125 |
| 3. Normalized native title | 日文原生名匹配 | 并入 2 |
| 4. Normalized Romaji | romaji 匹配 | 并入 2 |
| 5. Existing slug | slug 冲突唯一化（-2 后缀），不覆盖已有 URL | 0（无冲突） |
| **合计重复** | | **586**（含候选内互重） |

## 2. 正确结果示例

一个实体（Attack on Titan，anilist_id=16498）：
- title: Attack on Titan
- chinese_title: 進撃の巨人（日文原生）
- japanese_title: 進撃の巨人
- romaji_title: Shingeki no Kyojin
- aliases: ["進撃の巨人", "Shingeki no Kyojin"]

搜索匹配（AniList title 三字段）+ AKA 展示 + JSON-LD alternateName 全来自同一实体，**无重复 URL**。

## 3. 现有库内重复检查

| 维度 | 结果 |
|---|---|
| 重复 slug | 0 |
| 重复 anilist_id | 0（导入后 964 条全部唯一） |
| 重复 mal_id | 0 |
| 跨语言重复对（历史遗留） | 115 条旧中文 title 条目（/anime/进击的巨人/ 等）与英文条目对应——**按 Global Rules 保留不动**（禁止删除/改 URL），仅记录 |

## 4. 导入结果去重统计

- source_total=1090 → duplicate=586（外部 ID 478 + 标题 125 + 候选内互重）→ **new=485**
- 新 485 条 slug 唯一（无与现有冲突）
- invalid=19（格式非 TV/MOVIE/ONA/OVA/SPECIAL）

## 5. 结论

去重安全：无重复实体创建、无 slug 覆盖、无跨语言分裂。
