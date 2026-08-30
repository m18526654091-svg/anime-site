# AnimeHub Phase 27 — Entertainment SEO Opportunity Report

> 生成于 2026-08-29 · 基于 DB 数据审计

## 1. 数据统计

| 类别 | 数量 | 说明 |
|---|---|---|
| anime 总数 | 1479 | |
| 多季/续作标记（Season N/Final/Part） | **307** | 157 部 priority≥60 |
| 电影标记（Movie/Film/剧场版） | **74** | 如 Demon Slayer Mugen Train、Jujutsu Kaisen 0 |
| 特别篇/OVA 标记 | 10 | |
| characters | 476（覆盖 119 部）| |
| voice_actors | 341（513 关联）| |
| episodes | 952（覆盖 119 部）| ⚠️ video_url 为占位示例，禁止作播放源 |

## 2. 高价值多季 Franchise（Top）

| Franchise | 条目 | 代表条目 |
|---|---|---|
| Attack on Titan | 7 | 最终季 pri=100 |
| My Hero Academia | 5 | |
| Gintama | 4 | S2 pri=100 |
| Re:Zero / Mushoku Tensei / Vinland Saga / Spy x Family / Frieren / Oshi no Ko | 各 2-3 | 均含 Season 2+ |

## 3. 推荐新增/增强

| 候选页面类型 | 适用作品 | 决策 |
|---|---|---|
| `/watch-order/{slug}/` | 有复杂顺序的多季 franchise | ✅ 现有 8 个；候选：Mushoku Tensei、Frieren、Spy x Family（需数据+顺序确认）|
| `/anime-series/{slug}/` | 多季+电影+franchise 结构 | ✅ 现有 Fate；候选：Attack on Titan（7 条）、My Hero Academia（5 条）——**数据充分** |
| `/where-to-watch/{slug}/` | 全部 | ⚠️ **无合法数据源** → 仅设计框架，不批量生成 |
| `/anime/{slug}/episodes` | 119 部有 episodes 数据 | P1（数据充分后）|
| character/voice-actor 增强 | 476/341 实体 | P1（现有页增强）|

## 4. 结论
- 多季 franchise（AoT 7 条、MHA 5 条）数据充分，适合 franchise 体系扩展（**待生产部署+GSC 后按优先级启动**）
- Episode/Where-to-watch 受数据限制（占位 video_url / 无平台数据）
- 本阶段：只规划 + 确认现有覆盖，不批量生成
