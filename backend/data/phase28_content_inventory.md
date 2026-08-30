# AnimeHub Phase 28 — Content Inventory

> 生成于 2026-08-29 · 基于 DB 字段派生

## Content Type Inventory

| Type | Count | Available Fields | SEO Opportunity |
|---|---|---|---|
| tv_series | 1395 | title/year/episodes/status/genre/score | detail 全覆盖（现有）|
| movie | 74 | title/year/genre/score（33 部 pri≥60）| ⚠️ 已有 /anime/{slug}/ 覆盖；**不建 /movie/**（重复 intent）|
| special/ova | 10 | 同上 | 低量，不建独立类型 |
| unknown | 0 | — | — |
| 有 episode 数据 | **119** 部（952 条）| episode_number/title | ✅ **已实现 /anime/{slug}/episodes/** |
| characters / voice_actors | 476 / 341 | name/slug/关联 | 现有 /character/ /voice-actor/ 覆盖 |

## 可直接生成页面的类型

| 类型 | 决策 |
|---|---|
| Episode 页（/anime/{slug}/episodes）| ✅ **本阶段实现**（119 部有真实数据）|
| TV 页（/tv/{slug}）| ❌ **不建**（DB 为 anime 库，无真人剧数据，会空页）|
| Movie 页（/movie/{slug}）| ❌ **不建**（74 部 anime 电影已有 /anime/ 页，重复）|
| Season 作品页 | ⚠️ 设计（title Season N 派生），待 GSC 后评估 |

## 数据缺口
- Episode duration：无字段（不显示）
- Where to watch 平台：无数据源（不编造）
- 真人 TV 剧集：无数据
