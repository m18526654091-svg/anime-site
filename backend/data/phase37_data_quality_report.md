# AnimeHub Phase 37 — Data Quality Report

> 日期：2026-08-30 · 全库扫描（3607 条）· 状态：✅ CRITICAL = 0（来源固有差异 2 项观察）

## 1. Identity

| 检查项 | 结果 |
|---|---|
| duplicate AniList ID | 0 ✅ |
| duplicate MAL ID | 0（来源固有共享 1 对，见 §4） |
| duplicate external ID | 0 |
| duplicate normalized title | 0（导入前 title 去重） |
| slug collision | 0 ✅ |

## 2. Metadata

| 检查项 | 结果 |
|---|---|
| empty title | 0 ✅ |
| invalid year | 0 ✅ |
| invalid type | 0（132 条非合规格式导入时过滤） |
| invalid score | 0 ✅ |
| malformed aliases（JSON） | 0 ✅ |
| malformed genres | 1（来源固有，见 §4） |

## 3. Localization

| 检查项 | 结果 |
|---|---|
| invalid English/native/Romaji | 0（全部 AniList 来源） |
| duplicate aliases | 0 ✅ |

## 4. 来源固有差异（非导入错误，观察项）

1. **MAL ID 24151 共享**：`Ao Haru Ride: unwritten` 与 `Ao Haru Ride PAGE.13`（AniList 两个独立条目）共享同一 MAL ID——AniList 拆分特别篇而 MAL 不区分。两条目均保留来源给的 mal_id（不猜测），SEO 无影响（URL/slug 唯一）。
2. **IRIS OUT 空 genre**：AniList 该条目 genres=[]（来源无数据），保持空（不猜不编造）。

## 5. 覆盖变化

| 字段 | Before | After |
|---|---|---|
| total | 2723 | 3607 |
| japanese_title | 1723 (63.3%) | **2607 (72.3%)** |
| romaji_title | 1723 (63.3%) | **2607 (72.3%)** |
| aliases | 1723 (63.3%) | **2607 (72.3%)** |
