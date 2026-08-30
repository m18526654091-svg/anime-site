# AnimeHub Phase 27 — Entertainment SEO Expansion Plan

> 生成于 2026-08-29 · 规划阶段（只设计，不批量实现）

## Step 1 — SEO Opportunity Audit

| Keyword | Search Intent | Est. Value | Current Coverage | Recommended Page |
|---|---|---|---|---|
| {anime} episode list | 查看集数/分集 | 高 | detail 显示集数（无分集）| `/anime/{slug}/episodes`（P1，数据受限）|
| {anime} episode guide | 分集目录 | 中高 | 无 | 同上（P1）|
| {anime} season guide | 季数/季节指南 | 高 | detail + season 页 | Season 聚合（P0，标题含 Season N 数据充分）|
| {anime} cast / characters | 角色 | 高 | `/character/{slug}`（476 条）| **现有页已覆盖**（P1 增强）|
| {anime} voice actors | 声优 | 高 | `/voice-actor/{slug}`（341 条）| **现有页已覆盖**（P1 增强）|
| where to watch {anime} | 观看渠道 | 高 | 无 | 合法观看信息模块（P2，无视频源数据）|
| {anime} watch order | 顺序 | 高 | watch-order 8 franchise | ✅ 已覆盖 |

## Step 2 — Episode SEO Design（只设计）

**URL**：`/anime/{slug}/episodes`

**结构**：
- H1：`{Anime Name} Episodes`（如 "Attack on Titan Episodes: Complete List"）
- Episode count（Anime Information 已有字段）
- Episode list（title + episode_number + 顺序）
- Season information（若标题含 Season N，聚合）

**要求**：SSR + canonical + JSON-LD（ItemList）+ 内链（detail 双向）

**数据限制**（重要）：
- episodes 表仅 952 条 / 119 部（8% 覆盖率）
- `video_url` 为占位示例视频（BigBuckBunny 等）——**禁止展示为播放源**
- 无 episodes 数据的 anime → 页面显示 "Episode list not available"（不造假）
- **结论**：设计可行但 P1（数据充分后再批量生成；当前只对 119 部有数据作品可用）

## Step 3 — Season SEO Design

**方案**：聚合 detail 中标题含 "Season 1/2/3/Final" 的条目（已有 2025/2026 数据充足）

**URL**：复用 detail + season 页体系，**不新建季聚合 URL**（避免与现有 detail/season 重复 intent）
- 增强：detail 的 "Season" 信息行已展示（Phase 11 Anime Information）
- 候选：Season 聚合页需证明独立 intent 才建（P2）

**结论**：现有 season 页 + detail Season 信息已覆盖季意图；**无需新页面（P2 观察）**

## Step 4 — Cast SEO Audit

数据：
- characters：476 条（覆盖 119 部）· voice_actors：341 条 · character_voices：513 关联
- 现有 `/character/{slug}` 与 `/voice-actor/{slug}` 页面已存在（Phase 前建设）

评估 `/people/[slug]`：
- **不建议新建** `/people/`——与现有 character/voice-actor 页 intent 重叠（cannibalization）
- 增强方向（P1）：character/voice-actor 页的英文内容与互链（观察 GSC 后决定）

**结论**：Cast intent 由现有实体页覆盖；`/people/` 不建（重复 intent）

## Step 5 — Where To Watch SEO（合法）

**禁止**：盗版链接、视频源、播放页（现有 /watch/ 为占位播放，不入 SEO 扩展）
**合法设计**（P2）：
- Detail 加 "Where to Watch" 信息模块：说明"该作品可于主流流媒体平台获取"（**仅通用表述**，无具体盗版链接）
- 或依赖外部官方信息（需新增数据源，本阶段无）→ **保守：不建独立页面**，仅在 detail 说明观看渠道类型

**结论**：无合法数据源 → 不实现独立 Where to Watch 页（避免低质/违规内容）

## Step 6 — 优先级

| 优先级 | 项目 | 理由 |
|---|---|---|
| **P0** | 无新页面（维持现状）| 生产部署未完成，先验证现有 3470 URL 的真实表现 |
| **P1** | `/anime/{slug}/episodes`（119 部有数据）| episode list 高意图；数据充分后生成 |
| **P1** | character/voice-actor 页英文增强 | cast intent 高价值，增强现有页 |
| **P2** | Season 聚合页、Where to Watch 模块 | 需独立 intent 证明或新增数据源 |

## 核心原则
- 本阶段**只规划，不批量实现**（生产部署与 GSC 数据优先）
- 所有新页面必须：真实搜索意图 + 数据充分 + 无 cannibalization + 不涉及盗版
