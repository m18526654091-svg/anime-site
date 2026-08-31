# AnimeHub Phase 37 — Candidate Inventory

> 日期：2026-08-30 · 候选池：2981 条（Phase 35 1090 + 36 增量 + 37 增量 1021）

## 1. 候选来源（Step 4）

| 来源 | 查询 | 数量 |
|---|---|---|
| Phase 35（popularity/score/trending/2023-26 季番） | 31 | 1090 |
| Phase 36（2018-2022 季番） | 20 | +870 |
| **Phase 37（2013-2017 季番 + Movie/OVA/ONA/Special 专项）** | **31** | **+1021** |
| **合计** | | **2981** |

Phase 37 增量查询构成：
- 2013-2017 季番 × 4 季 = 20 查询（Year gap 修复）
- MOVIE popular ×3 + MOVIE score ×2 + OVA ×2 + ONA ×2 + SPECIAL ×2 = 11 查询（Type gap 修复）

## 2. 候选优先级分布（按 popularity）

- Tier 1（≥300k）：已基本消化（剩余 1 条）
- Tier 2（200k-300k）：已基本消化（剩余 0 条）
- Tier 3（<200k）：剩余 130 条长尾（不为数量强行导入）

## 3. 导入结果

- dry-run：new=884 / duplicate=1965 / invalid=132
- apply：**new=884**（一致）
- 无效 132 条：格式非 TV/MOVIE/ONA/OVA/SPECIAL（质量门槛）

## 4. 记录字段

每条候选含：title{english/romaji/native}、startDate{year/month/day}、description、genres、tags、studios、status、episodes、coverImage、averageScore、popularity、format、id/idMal

## 5. 剩余机会（Step 23）

| 类别 | 剩余 |
|---|---|
| 未导入候选总数 | 131 |
| Tier 1 | 1 |
| Tier 2 | 0 |
| Tier 3 | 130 |
| 其中 MOVIE | 4 |
| 其中 OVA/SPECIAL | 4 |
| 2013-2017 剩余高价值 | 已全部消化（top-50/季） |

> 结论：高价值候选已充分消化；剩余全部为低 popularity 长尾，按 Step 5 规则不强行导入。
