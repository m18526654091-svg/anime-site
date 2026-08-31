# AnimeHub Phase 37 — Pre-Expansion Audit

> 日期：2026-08-30 · 全库扫描（2723 条）· 状态：✅ 完成

## 1. Entity 统计

| 维度 | 数值 |
|---|---|
| total anime | 2723 |
| 2013 | 54 |
| 2014 | 61 |
| 2015 | 57 |
| 2016 | 74 |
| 2017 | 67 |
| 其他年份 | 2410 |

> **2013-2017 明显缺口**：每年正常季番约 300+ 部，当前仅 54-74 部（覆盖 ~20%）。

## 2. Type 分布（近似）

| Type | 数量 | 说明 |
|---|---|---|
| TV（默认） | ~2600 | 主体 |
| Movie（title 含 movie/film/剧场版） | 81 | **缺口**（AniList 有大量高价值剧场版未覆盖） |
| OVA/Special | 43 | **缺口** |

## 3. Localization 覆盖

| 字段 | 数量 | 覆盖率 |
|---|---|---|
| English（title） | 2723 | 100% |
| Chinese（chinese_title） | 2723 | 100%（部分为日文原生名） |
| Japanese（japanese_title） | 1723 | 63.3% |
| Romaji（romaji_title） | 1723 | 63.3% |
| Aliases | 1723 | 63.3% |
| anilist_id | 1723 | 63.3% |
| mal_id | 1715 | 63.0% |

## 4. Data Quality

- duplicate anilist_id / mal_id / slug：**0**
- empty title / year：**0**
- empty genre：1 / empty score：3（可忽略）

## 5. 缺口结论

1. **Year gap**：2013-2017 每季覆盖不足（优先 Tier 1）
2. **Type gap**：Movie 81 / OVA+Special 43（高价值剧场版/OVA 缺失）
3. **Franchise gaps**：热门 franchise 的 Movie/OVA/season 条目待补（如 AoT/OnePiece/MHA 剧场版）
4. **Localization**：63.3% 的实体已多语言；新增实体将保持 100% 多语言
