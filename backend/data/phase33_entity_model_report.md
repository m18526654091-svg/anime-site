# AnimeHub Phase 33 — Entity Name Data Model Report

> 日期：2026-08-30 · 目标：一个实体页 + 多个已验证名称（不建多语言重复 URL）

## 1. 需求 vs 现状

目标模型：

```
Primary title:   Attack on Titan
Alternative:     進撃の巨人 / Shingeki no Kyojin / 进击的巨人
```

DB 现状：
- title（英文/romaji）+ chinese_title（日文原生/中文混合）✅
- 无 japanese_title 列、无 aliases 表（external_entities 预留但空）❌

## 2. 最小解决方案（本次实施，**无 schema 变更**）

采用 **title + chinese_title 双名称**作为实体名称集合：

```
AKA = unique[ title, chinese_title ]   （两者均来自已验证 DB 数据）
```

| 实体 | AKA 集合（实际渲染） |
|---|---|
| Attack on Titan | ["Attack on Titan", "進撃の巨人"] |
| Bleach | ["Bleach", "死神"] |
| JUJUTSU KAISEN | ["JUJUTSU KAISEN", "呪術廻戦"] |
| Monster | ["Monster", "怪物"] |
| Re:Zero | ["Re:Zero", "从零开始的异世界生活"] |
| Spy x Family | ["SPY x FAMILY"]（title==chinese_title，AKA 隐藏） |

规则：
- 只显示已验证 DB 名称
- title == chinese_title 时隐藏 AKA 区块（无差异即无内容）
- 缺失的 romaji/简体别名**不填**（无来源 = 不伪造）

## 3. Schema 变更评估

| 方案 | 变更 | 理由 |
|---|---|---|
| A. 双字段 AKA（本次） | 无 | 现有 title/chinese_title 足够支撑；唯一风险是未来需增加别名时扩展 |
| B. anime_aliases 表 | 新建表 | **暂缓**：无已验证数据源可填充（external_entities 已空 0 行）；待 AniList/MAL 名称数据任务后启用 |
| C. 改 URL 结构 | 禁止 | 规则要求不改变 URL |

## 4. 推荐演进路径（数据任务，非本次）

1. 数据任务：调用 AniList/MAL API（有 anilist_id/mal_id 的 479/478 条目）拉取 native/romaji/synonyms 标题，写入 `external_entities`（raw_snapshot）或新 `anime_aliases` 表
2. 后端 `/api/anime?q=` 搜索扩展到 aliases（SQL OR 条件）
3. AKA 区块自动扩展为 4-5 个名称

> 期间不阻塞：现有 title/chinese_title 已覆盖英文 + 日文原生名双语言识别。

## 5. 结论

采用**方案 A（零 schema 变更）**完成实体多名称支持。未来别名扩展仅需数据填充 + 查询扩展，无需 URL 变更。
