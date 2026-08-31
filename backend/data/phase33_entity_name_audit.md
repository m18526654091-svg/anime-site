# AnimeHub Phase 33 — Entity Name Audit

> 日期：2026-08-30 · 审计：DB 实体名称字段可用性（支持多语言搜索识别）

## 1. 数据库名称字段现状

anime 表（1479 行）名称相关字段：

| 字段 | 存在 | 覆盖 | 内容说明 |
|---|---|---|---|
| title | ✅ | 1479/1479 (100%) | 英文/romaji 标题（Attack on Titan、Shingeki no Kyojin 类） |
| chinese_title | ✅ | 1479/1479 (100%) | **混合**：部分日文原生名（進撃の巨人、呪術廻戦、死神）、部分中文名（怪物、从零开始的异世界生活、不死者之王） |
| slug | ✅ | 1479/1479 (100%) | 英文 URL 标识（attack-on-titan） |
| anilist_id / mal_id | ✅ | 479 / 478 (32%) | 外部权威实体 ID |
| japanese_title / native_title | ❌ 无字段 | — | DB 无独立日文标题列 |
| aliases / synonyms 表 | ❌ 无表 | — | 无别名表；external_entities 表存在但 **0 行** |
| anime_field_sources | ⚠️ 45 行 | — | 仅 studio/episodes/status/region/seo_title/description，无标题变体 |

## 2. Top 实体名称字段实测

| 实体 | title | chinese_title | 含日文原生名 | 缺口 |
|---|---|---|---|---|
| Attack on Titan | Attack on Titan | 進撃の巨人 | ✅ 日文 | Shingeki no Kyojin（romaji）/ AOT / 进击的巨人（简体）无 |
| JUJUTSU KAISEN | JUJUTSU KAISEN | 呪術廻戦 | ✅ 日文 | 咒术回战（简体）无 |
| Bleach | Bleach | 死神 | ✅ 日文 | — |
| Monster | Monster | 怪物 | ❌ 中文 | 日文名 MONSTER（无变化） |
| Fate/stay night UBW | Fate/stay night UBW | Fate/stay night UBW | 同 | 命运之夜（简体）仅 2006 版 chinese_title 含 |
| Re:Zero | Re:Zero | 从零开始的异世界生活 | ❌ 中文 | Re:Zero（英文）已可匹配 |

## 3. 缺失字段统计

- **无** japanese_title 列（部分日文名已隐式存在 chinese_title）
- **无** aliases 表（external_entities 为预留空表）
- 简体中文别名（进击的巨人/咒术回战）在**热门实体**普遍缺失（仅少量条目 chinese_title 含简体）

## 4. Top 缺失别名（数据任务候选，未验证来源不填）

| 实体 | 缺失变体 | 来源建议 |
|---|---|---|
| Attack on Titan | Shingeki no Kyojin / AOT / 进击的巨人 | AniList native+romaji / MAL synonyms / 官方简体名 |
| Jujutsu Kaisen | 咒术回战（简体） | 官方中文译名（已验证媒体名） |
| Re:Zero | Re:Zero kara Hajimeru Isekai Seikatsu | AniList romaji |

> 约束：所有别名须来自已验证数据源（AniList/MAL 官方字段），禁止 AI 发明。

## 5. 结论

DB 已具备**双名称能力**（title + chinese_title），其中 chinese_title 混合日文原生名与中文名——均为导入时已验证数据。
缺失：独立日文列、别名表、简体中文别名。最小方案见 `phase33_entity_model_report.md`。
