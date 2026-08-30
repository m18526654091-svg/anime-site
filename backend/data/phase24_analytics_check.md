# AnimeHub Phase 24 — Analytics Check

> 生成于 2026-08-29

## GA4 集成状态

| 项 | 状态 |
|---|---|
| 代码 | ✅ `lib/analytics.ts` + `components/GoogleAnalytics.tsx`（Phase 22）|
| NEXT_PUBLIC_GA_ID | 未设置（生产/本地均无）|
| 生产部署 | ❌ 未部署（随 Phase 10-23 pending）|

## 运行时行为验证

| 模式 | build | SSR HTML |
|---|---|---|
| **无 NEXT_PUBLIC_GA_ID** | ✅ | **无 gtag / googletagmanager**（零加载，组件 return null）|
| 有 NEXT_PUBLIC_GA_ID（G-TEST123456，Phase 22 验证）| ✅ | **含 gtag init + src**（afterInteractive）|

- 编译产物含 gtag 字符串属组件源码（正常），**运行时**行为由 gaId 决定
- 不影响 SSR / SEO / Core Web Vitals

## 激活步骤（部署后）
1. 生产部署最新代码
2. 设置 `NEXT_PUBLIC_GA_ID=<真实 GA4 ID>`（`.env`，不进 git）
3. `docker compose build frontend && docker compose up -d`
4. 验证首页 HTML 含 gtag、GA4 Realtime 有访问

## 结论
✅ GA4 Ready Layer 工作正常；当前未启用（无 ID），零影响。
