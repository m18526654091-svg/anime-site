# AnimeHub Phase 35 — Catalog Expansion Report

> 日期：2026-08-30 · 范围：第一批 500 高价值 Anime（实际 485）+ 多语言标题回填 · 状态：✅ 完成

## 1. Before / After

| 指标 | Before | After |
|---|---|---|
| Anime count | 1479 | **1964（+485）** |
| English title 覆盖 | 1479 (100%) | 1964 (100%) |
| Japanese（native）title 覆盖 | 346（仅存于 chinese_title） | **964/1964 (49.1%)** |
| Romaji title 覆盖 | 0 | **964/1964 (49.1%)** |
| Chinese title 覆盖 | 1479 (100%) | 1964 (100%) |
| Alias 覆盖 | 0 | **964/1964 (49.1%)** |
| anilist_id 覆盖 | 479 (32.4%) | **964 (49.1%)** |
| mal_id 覆盖 | 478 (32.3%) | 963 (49.0%) |

## 2. 导入统计（Step 5）

| 指标 | dry-run | apply |
|---|---|---|
| added | 485 | **485** |
| updated | 0 | 0 |
| skipped | 0 | 0 |
| duplicate（外部 ID + 标题 + 候选内互重） | 586 | 586 |
| invalid（格式非 TV/MOVIE/ONA/OVA/SPECIAL） | 19 | 19 |

## 3. 数据源与来源覆盖

- 数据源：**AniList GraphQL**（31 请求，1090 原始候选；Tier1=145 / Tier2=125 / Tier3=820）
- 来源 ID 保留：anilist_id + mal_id（964/963）
- 本地回填：对现有 479 条有 anilist_id 条目批量回填 japanese_title/romaji_title/aliases（**updated=479, failed=0**）

## 4. 重复与缺失统计

- 重复 slug：0
- 重复 anilist_id / mal_id：0
- missing English title：0
- missing native title：1000（无 anilist_id 的旧条目，未回填）
- missing Romaji：1000（同上）
- missing Chinese title：0
- missing aliases：1000（同上）
- missing year / genre：0

## 5. 多语言展示（Step 6 验证）

- Hyouka 页 AKA 区块实测：`Hyouka 氷菓`（英文 + 日文原生名）
- JSON-LD alternateName：新条目 20/20 含（含日文/romaji）
- 搜索匹配（Step 8，10 实体 × 多语言变体）：**romaji 名称全部命中同一实体**
  - Shingeki no Kyojin→attack-on-titan ✓ / Hagane no Renkinjutsushi→FMA ✓ / Ansatsu Kyoushitsu→Assassination Classroom ✓ / サイコパス→PSYCHO-PASS ✓（后端 q 搜索已扩展匹配 japanese_title/romaji_title/aliases）

## 6. 集成验证（Step 7/11）

- **SSR**：20 新增 + 20 旧 Anime 全部 200 + canonical + JSON-LD（6块）+ English UI
- **sitemap**：4044 URL（+575），**dups=0**，新条目自动进入（hyouka/psycho-pass/maid-sama 等）
- 新条目自动进入 detail/genre/year/studio 等现有管道（无手工链接）

## 7. 未导入项（如实）

- invalid 19 条（格式不合规）
- 586 条重复（已在库）
- 无 anilist_id 的 1000 旧条目：多语言字段未回填（无外部来源，**不猜不填**）

## 8. 规则遵守

- ✅ 复用现有 pipeline（discover/import + gql），未重新造轮子
- ✅ 幂等（dry-run 与 apply 一致，重复运行不重复新增）
- ✅ 来源 ID 保留（anilist_id/mal_id）
- ✅ 无编造（所有标题字段 AniList 已验证；无中文数据时用日文原生名或英文，不冒充官方中文名）
- ✅ 无 URL 修改 / 无删除 / 无 slug 变更（新条目 slug 唯一化仅用于冲突场景）
- ✅ 去重（一个实体一个页面；Attack on Titan 的 進撃の巨人/Shingeki no Kyojin 均为别名非独立实体）
- ✅ schema 最小扩展（anime 表 +3 列，幂等 ALTER，SQLite/PostgreSQL 同步）

## 9. 后续建议

1. 生产部署：需要同步 `ensure_schema` 迁移（3 新列）+ 新 candidates 数据文件 + 导入（485 条）+ 回填（479 条）
2. 第二批：继续扩大候选（Tier3 长尾 + 更多页），可达到 +1000
3. 中文标题来源：后续数据任务接入已验证中文标题源（当前用日文原生名/英文，避免冒充）
