# AnimeHub Phase 24 — First 30-Day Experiment Plan

> 生成于 2026-08-29

## Day 0 — Deploy
- 生产执行：`git fetch + merge --ff-only origin/main`（→ 251c00f）→ `docker compose build frontend && up -d`
- 验证：sitemap dups=0、Phase 10-23 内容上线、`docker compose ps` healthy
- GSC 提交 sitemap + 域验证

## Day 1-7 — Wait for Google Crawling
- 不做改动
- 确认 robots/canonical 正常（已通过）

## Day 7 — Check Indexed Pages
- GSC Pages：indexed / submitted 数量
- 记录到 `phase24_growth_dashboard.md`

## Day 14 — Check Queries
- GSC Performance：首个 query 集
- 标记 top queries / impressions

## Day 21 — Improve Pages With Impressions
- 仅对**有 impressions** 的页面做 Action A/B（title/desc/内容/内链）
- 无数据页面不动

## Day 30 — Decision

| Case | 条件 | Decision |
|---|---|---|
| **A** | Indexed > 80% | Continue SEO expansion |
| **B** | Indexed 但无 impressions | Improve content quality |
| **C** | 未 Indexed | Fix technical issue（robots/canonical/质量）|

## 规则
- 30 天内仅允许：bug fix、SEO 问题修复、CTR 优化、GSC 数据驱动修改
- 禁止：新页面类型、大规模重构、DB 修改、未验证功能
- 数据优先：所有决策基于真实 GSC 数据
