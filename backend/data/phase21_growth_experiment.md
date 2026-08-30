# AnimeHub Phase 21 — Google Growth Experiment Setup

> 生成于 2026-08-29 · 30 天增长实验启动文档

## 1. Production Status（详见 phase21_production_status.md）
- 生产 sitemap=3470 · robots/canonical ✓
- ⚠️ 发现并修复 **sitemap /studio/ 9 个重复 URL**（sitemap.ts 加 dedup）
- Phase 10/11/17 内容未部署（待生产部署）

## 2. GSC Plan（phase21_gsc_tracking.md）
- 周度表（clicks/impressions/CTR/position/indexed）+ 页面类型追踪
- 当前无 GSC 权限，数据待填（不伪造）

## 3. Keyword Baseline（phase21_keyword_seed.md）
- 14+ 种子 query（detail/watch-order/best/similar intent），position 全部 unknown

## 4. Analytics Plan
- **现状**：无任何 tracking 代码（gtag/GA4/plausible 均无）→ SSR 无阻塞 ✓
- **未来安装步骤**（生产部署后、GSC 确认后）：
  1. 在 `frontend/app/layout.tsx` 的 `<head>` 添加 GA4 gtag script（Next.js Script 组件，`afterInteractive` 策略，避免阻塞 SSR）
  2. 使用 `NEXT_PUBLIC_GA_ID` 环境变量（不进 git）
  3. 验证：页面加载后 gtag 事件正常、SSR HTML 无 script 泄漏到首屏关键路径
- **注意**：安装前确认 GA4 不影响 Core Web Vitals（`afterInteractive` + 延迟加载）

## 5. Monetization Readiness（AdSense）
- 信任页：About/Contact/Privacy/Terms/Copyright 全存在 + footer 链接 ✅
- 用户旅程：Google → landing → related anime → more pages 完整 ✅（Phase 14/17 验证）
- 无广告代码、无广告伪装 ✅

## 6. Freeze Rules（30 天）
**允许**：bug fixes（如本次 sitemap dups）、基于真实 GSC 数据的 CTR 优化、索引修复
**禁止**：新增数百页、重设计、不必要功能、DB 变更、URL 重构

## 7. 30 天实验目标
- 部署全部代码后，GSC 确认 indexed/submitted ≥ 90%
- 种子关键词 position 进前 10
- CTR ≥ 2%（Top 100）
- 周度按 GSC 数据迭代

## Commit
- `sitemap.ts` studio dedup（bug fix）+ 本实验文档
