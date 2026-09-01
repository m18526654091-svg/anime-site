# AnimeHub Phase 40-A — Character Name Localization & Entity Naming Audit

> 日期：2026-09-01 · 纯审计（未修改任何数据/代码）· 状态：根因已定位，修复方案已提出待确认

## 1. Current Character Naming Model

### Schema（characters 表，476 行）

| 字段 | 类型 | 覆盖 | 来源 | 用途 | nullable |
|---|---|---|---|---|---|
| `name` | VARCHAR(120) | 476/476 (100%) | importer：`characters_cn → AniList native → full` | **主显示名（canonical display）** | NOT NULL |
| `name_en` | VARCHAR(120) | 476/476 (100%) | AniList `name.full`（英文/romaji 混合） | **English name** | ✓ |
| `native_name` | VARCHAR(120) | 457/476 (96%) | AniList `name.native`（日文） | **Japanese/native name** | ✓ |
| `slug` | VARCHAR(160) | 476/476 | 从 `name_full` 生成 | **canonical URL 标识**（唯一） | NOT NULL |
| `aliases` | VARCHAR(300) | 部分 | name/native/full 拼接 | 别名 | ✓ |
| `source_id` | VARCHAR(64) | 458/476 | AniList character ID | 外部身份 | ✓ |
| `source` | VARCHAR(40) | 458/476 | 'anilist' | 来源 | ✓ |

### 名称字段角色映射
- **canonical identity**：`slug`（唯一）+ `source_id`（外部稳定身份）
- **display name（当前）**：`name`（原生名优先——importer 逻辑 `name = characters_cn or native or full`）
- **English name**：`name_en`（AniList full）
- **Native name**：`native_name`（AniList native，日文）
- **Romaji**：无独立字段（AniList full 混合英文/romaji，如 'Tanjirou Kamado' 是 romaji、'Tanjiro Kamado' 是英文）

## 2. Data Coverage（476 characters）

| 名称 | 覆盖 | 说明 |
|---|---|---|
| name（原生/中文） | 476/476 (100%) | 其中 408 (86%) == native_name（日文）；部分为中文（旧种子） |
| **name_en（英文）** | **476/476 (100%)** | **英文名已全部存在** |
| native_name（日文） | 457/476 (96%) | |
| name 为纯 ASCII | 2 | 几乎全部是日文/中文 |

**关键**：English name 已 100% 存在（`name_en`），**不是数据缺失问题**。

## 3. Current Display Pipeline

```
Database:   name(原生) + name_en(英文) + native_name(日文)
   ↓
List API:   CharacterLite{ name }        ← 只返回 name（原生），无 name_en/native_name
Detail API: CharacterOut{ name, name_en } ← 返回 name + name_en
   ↓
SSR:        page.tsx fetchCharactersByAnime(anime.id) → initialCharacters
   ↓
UI:         AnimeDetailClient Characters 卡: {ch.name}           ← 显示原生名
            character/[slug] H1: {ch.name} + 小字别名(name_en/native)
            SEO title: {ch.name}（原生名）
```

## 4. Root Cause

**多因素，但非数据缺失**：
1. **Importer 设计**：主 `name` 优先 native（`cns or native or full`）→ 原生名作主显示
2. **List API**（CharacterLite）：`name=c.name`，**未暴露 `name_en`/`native_name`** → detail 页 Characters 区只能显示原生名
3. **Frontend**：`AnimeCharacter` type 无 `name_en`；UI `{ch.name}` 直接用原生名
4. **Character detail 页**：H1 `{ch.name}`（原生名），name_en 仅在别名小字行

→ **CASE A（English 已有，但 UI 没显示）+ API 未透出**。DB 数据完好。

## 5. Recommended Naming Strategy

```
English UI Primary display:  name_en || name        （英文优先）
Secondary display:           native_name（有且不同时，小字辅助）
Fallback:                    English → Romaji(full) → Native

示例（页面显示）：
  Tanjiro Kamado          ← primary (name_en)
  竈門 炭治郎             ← secondary (native_name，小字)
```

特殊处理：
- `name_en` 缺失（0%，当前无）→ 回退 `name`
- `name_en` 与 romaji 相同（如 'Gokuu Son'）→ 仍显示（它是当前可用英文/romaji）
- 不覆盖/不删除 `name`（原生名保留为实体属性）

## 6. SEO Implications

**原则**：One character entity → One canonical URL → Multiple language names

- **canonical URL 不变**：`/character/{slug}/`（slug 已由 name_full 生成，稳定）
- **H1**（English 页）：应显示 `name_en || name`（如 "Tanjiro Kamado"），原生名作副标题
- **SEO title**：`name_en || name` + anime 上下文（英文文案）
- **JSON-LD Person**：`name: name_en || name`，`additionalName: name`（原生名），`alternateName: aliases + native`（保留全部名称）
- **绝不创建** `/character/tanjirou/` `/character/竈門-炭治郎/` 等重复实体页

## 7. Minimal Fix（proposal，未实施）

| 层 | 改动 | 文件 |
|---|---|---|
| Backend | `CharacterLite` 加 `name_en: Optional[str]`、`native_name: Optional[str]`；list API 返回 | `backend/app/api/characters.py` |
| Frontend type | `AnimeCharacter` 加 `name_en`/`native_name` | `frontend/lib/api.ts` |
| Frontend detail 卡 | 主显示 `ch.name_en \|\| ch.name`，辅助小字原生名（不同时） | `frontend/components/AnimeDetailClient.tsx` |
| Frontend character 页 | H1/SEO title 用 `ch.name_en \|\| ch.name`；原生名保留副标题 | `frontend/app/character/[slug]/page.tsx` |
| JSON-LD | Person `name` 用英文名，原生名入 additionalName/alternateName | 同上 |

**不改 DB / 不改 importer / 不删 name**（name 保留原生名，实体完整）。

## 8. Tests

- 现有：`pytest tests/test_characters_relationships.py` 5 passed；全量 24 passed（未修改逻辑，无回归）
- 实施修复后应补：
  1. English name 存在 → API 返回 name_en、UI 用英文
  2. English 缺失 → 回退 name
  3. native_name 保留（API 返回）
  4. canonical URL 不变
  5. 既有 API consumers（sitemap/detail）不破坏

## 9. Production Changes

**本阶段（audit）无需任何生产数据修改。**
- ❌ 不 UPDATE/DELETE characters
- ❌ 不批量 rename
- ❌ 不重跑 importer
- ❌ 不修改 production DB

实施命名策略时仅需**前端/后端代码部署**（rebuild frontend/backend），数据零改动。

## 结论

English name 100% 存在（`name_en`）——问题是 **list API 未透出 + frontend 显示选择**（CASE A），非数据缺失。最小修复 = API 加字段 + 前端显示英文优先、原生名辅助保留。待确认后实施。
