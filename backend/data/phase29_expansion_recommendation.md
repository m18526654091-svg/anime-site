# AnimeHub Phase 29 — Expansion Recommendation

> 生成于 2026-08-29 · 下一阶段实体 SEO 扩展规划

## Step 2 — Entity Opportunity 评估

| 类型 | 数据支持 | 可生成量 | 搜索价值 | 重复风险 | 优先级 |
|---|---|---|---|---|---|
| **Franchise Hub** | 强（57 集群）| 15-25 页（候选精选）| ★★★★★ | 低（与 watch-order 互补）| **P0** |
| Season 聚合页 | 中强（337 标记）| 30-60 页 | ★★★★ | 中（需与 detail 区分）| P1 |
| Episode 页 | 中（119 部）| 119 页 | ★★★ | 低 | P1（已有）|
| Character / Voice | 中（476/341）| 增强现有 | ★★★★ | 低 | P1（增强）|
| Studio | 强（264）| 增强现有 | ★★★ | 低 | P2 |
| Movie 独立页 | 中（74）| 不建 | — | 高（重复 /anime/）| 跳过 |

## Step 4 — Page Architecture 原则

每个未来页面必须：
- **unique search intent**（Franchise=系列全景；Season=单季信息；不与 detail 重复）
- **unique internal links**（Franchise Hub ↔ watch-order ↔ detail ↔ similar）
- **canonical 策略**：Franchise `/anime-series/{slug}/`；Season `/anime/{base-slug}/season/{n}/`
- **sitemap 策略**：仅 quality 充分 + 数据完整页入 sitemap（沿用现有 dedup + threshold）

## Step 5 — Top 100 Future Pages 评分（Top 示例）

| # | 页面 | Intent | 数据 | 人气 | 内链值 | 总分 |
|---|---|---|---|---|---|---|
| 1 | /anime-series/attack-on-titan/ | franchise 全景 | 8 条 | 顶级 | 高 | 98 |
| 2 | /anime-series/my-hero-academia/ | franchise | 6 条 | 顶级 | 高 | 95 |
| 3 | /anime-series/rezero/ | franchise | 5 条 | 高 | 高 | 93 |
| 4 | /anime-series/jujutsu-kaisen/ | franchise | 5 条 | 顶级 | 高 | 93 |
| 5 | /anime-series/fire-force/ | franchise | 5 条 | 中高 | 中 | 88 |
| 6 | /anime-series/one-punch-man/ | franchise | 5 条 | 高 | 中 | 90 |
| 7 | /anime-series/slime/ | franchise | 5 条 | 高 | 中 | 90 |
| 8 | /anime/attack-on-titan/season/1/ | season | 数据足 | 顶级 | 高 | 92 |
| ... | （其余 franchise/season 按同评分）| | | | | |

## Step 6 — Final Recommendation

### P0（下一阶段优先开发）
1. **Franchise Hub 扩展**：/anime-series/{slug}/ 覆盖 15-25 个高人气集群（AoT/MHA/Re:Zero/JJK/OPM/Slime/Fire Force/Gintama/Haikyuu/Golden Kamuy 等）——复用 Fate 页面模式，数据充分
2. 前提：生产部署 + GSC 验证 Fate 页表现

### P1
- Season 聚合页（/anime/{base}/season/{n}/）：先做 Top 10 franchise 的季页
- Episode 页数据扩展（119→更多，需数据任务）
- Character/Voice 页增强（Known for/Related/互链）

### P2
- Studio 页增强
- 其余 franchise（数据 <3 条不建）
- Movie 独立页（不建，重复）

## 禁止确认
- 不建 /tv/（无真人剧数据）
- 不建 streaming/watch-free 页
- 不编造剧情/演员/评分
- 不创建空页面
- 不改已有 URL

## 启动前提
1. **生产部署**（pending 13 release）
2. GSC 验证现有 3470 URL indexed
3. Fate franchise 页数据表现确认后扩展
