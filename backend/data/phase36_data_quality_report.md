# AnimeHub Phase 36 — Data Quality Report

> 日期：2026-08-30 · 导入后全库扫描（2723 条）· 状态：✅ CRITICAL = 0

## 1. 扫描结果

| 检查项 | 数量 | 状态 |
|---|---|---|
| duplicate anilist_id | 0 | ✅ |
| duplicate mal_id | 0 | ✅ |
| normalized title collision | 0（导入脚本 title 去重） | ✅ |
| empty title | 0 | ✅ |
| invalid year | 0 | ✅ |
| invalid score | 0 | ✅ |
| invalid type（format 非 TV/MOVIE/ONA/OVA/SPECIAL） | 0（72 条导入时已过滤） | ✅ |
| malformed aliases（JSON 解析失败） | 0 | ✅ |
| empty slug | 0 | ✅ |
| slug collision | 0 | ✅ |
| **CRITICAL** | **0** | ✅ |

## 2. 导入后全局覆盖

| 字段 | 数量 | 覆盖率 |
|---|---|---|
| total anime | 2723 | — |
| anilist_id | 1723 | 63.3% |
| japanese_title | 1723 | 63.3% |
| romaji_title | 1723 | 63.3% |
| aliases | 1723 | 63.3% |

## 3. 说明

- 72 条 invalid（格式不合规）在导入时按质量门槛过滤，不入库
- 无 anilist_id 的 1000 条旧条目（历史种子数据）不参与多语言回填（无外部来源，不猜）
- 全部字段来自 AniList 已验证数据；无伪造
