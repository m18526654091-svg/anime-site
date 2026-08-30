# AnimeHub Phase 26 — Google Search Console Launch Guide

> 生成于 2026-08-29

## 首次上线流程

### 1. 验证 Domain
- Google Search Console → 添加资源 → **域名** → `bunivoa.com`
- DNS TXT 记录验证（或 HTML 文件验证）

### 2. 提交 Sitemap
- `https://bunivoa.com/sitemap.xml`
- 前置：生产部署完成（Phase 26 checklist），dups=0 确认

### 3. 等待状态
| 状态 | 含义 | 预期时间 |
|---|---|---|
| Discovered | Google 发现 URL | 1-7 天 |
| Crawled | 已抓取 | 3-14 天 |
| Indexed | 已收录 | 7-30 天 |

## Day 0 Baseline（首次接入时记录）

| 项 | 值 |
|---|---|
| Date | |
| Production commit | |
| Sitemap submitted | |
| Pages indexed | WAITING |
| Pages not indexed | WAITING |
| Clicks / Impressions | WAITING |
| CTR / Avg Position | WAITING |

## 后续
- 按 `phase24_growth_dashboard.md` 周度填写
- 30 天实验按 `phase24_30day_experiment.md` 执行
- 数据原则：真实 GSC 数据驱动，不模拟

## Step 5 — Analytics 状态（Phase 26 检查）

| 项 | 状态 |
|---|---|
| GA4 Ready Layer | ✅ 已实现（Phase 22：lib/analytics.ts + GoogleAnalytics.tsx）|
| NEXT_PUBLIC_GA_ID | 未设置 → **不加载任何 script（零影响）** |
| 有 GA ID 时行为 | ✅ afterInteractive 加载（Phase 22 验证）|
| 结论 | ✅ 准备完成，当前禁用（符合要求，不修改）|

## Step 6 — Monetization Readiness（Phase 26 检查）

| 项 | 状态 |
|---|---|
| About / Contact / Privacy / Terms / Copyright | ✅ 全部存在 |
| footer 链接 | ✅ |
| 空页/坏页/中文 UI（主路径）/假流量 | ✅ 无 |
| **AdSense 前置条件** | **PASS**（准备就绪；实际审核由 Google 决定，流量达标后申请）|

