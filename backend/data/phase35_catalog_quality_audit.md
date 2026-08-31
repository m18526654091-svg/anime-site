# AnimeHub Phase 35 — Catalog Quality Audit

> 日期：2026-08-30 · 审计：本地 DB（animehub.db，1479 条）数据质量与多语言字段现状

## 1. 基本统计

| 指标 | 数值 |
|---|---|
| total anime | 1479 |
| missing title | 0 |
| missing chinese_title | 0 |
| missing year | 0 |
| missing score | 1 |
| missing genre | 0 |
| missing slug | 0 |
| missing anilist_id | 1000（覆盖 479/1479 = 32.4%） |
| missing mal_id | 1001（覆盖 478/1479 = 32.3%） |
| 重复 slug | 0 |
| 重复 anilist_id | 0 |
| 重复 mal_id | 0 |

## 2. 标题质量

| 检查项 | 数量 | 说明 |
|---|---|---|
| title 含汉字（中文写入 title） | 115 | 旧种子数据（无外部 ID），如 `'进击的巨人'`、`'鬼灭之刃'`；**slug 也是中文**（/anime/进击的巨人/） |
| title 含日文假名 | 0 | 无日文名写入 title ✅ |
| chinese_title 为日文假名 | 346 | chinese_title 存日文原生名（進撃の巨人 等），Phase 33 已作为 AKA 使用 |
| chinese_title 为纯英文 | 110 | 轻微问题（chinese_title 与 title 同为英文） |
| title == chinese_title | 219 | 两字段相同（无额外名称信息） |

## 3. 多语言字段覆盖（Step 3 前提）

| 字段 | 当前覆盖 | 说明 |
|---|---|---|
| English title | 1479 | title（部分为中文，115 条异常） |
| Native（日文） | 346（存于 chinese_title） | 无独立列 |
| Romaji | ~0 | **无字段、无数据** |
| Chinese title | 1364（存于 chinese_title） | 无独立列 |
| Aliases | 0 | **无字段、无数据** |

## 4. 已知问题

1. **115 条中文 title 与英文条目构成跨语言重复对**（如 `/anime/进击的巨人/` vs `/anime/attack-on-titan/`）。Global Rules 禁止删除/改 URL，本阶段**不动它们**（保持 URL 稳定），仅在报告中记录。新增导入不会与之冲突（无 anilist_id，不参与匹配）。
2. 多语言字段（romaji/native/aliases）无存储——本阶段**最小 schema 扩展**（anime 表加 `japanese_title`/`romaji_title`/`aliases` 3 列，幂等 ALTER，SQLite+PostgreSQL 同步）。
3. 346 条 chinese_title 为日文原生名——Phase 33 已将其作为 AKA 展示（正确用法），本阶段通过新列规范化。

## 5. 结论

- 本地库基础质量良好（无重复、无缺失核心字段）
- 主要缺口：**外部 ID 覆盖 32%** + **多语言字段缺失** + **115 条历史中文 title 异常**
- 本阶段动作：最小 schema 扩展 + 扩大 AniList 候选抓取 + 500 高价值导入 + 多语言字段回填
