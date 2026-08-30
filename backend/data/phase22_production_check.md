# AnimeHub Phase 22 — Production SEO Verification

> 生成于 2026-08-29 · 公网实测

## 1. Sitemap

| 项 | 值 |
|---|---|
| total URLs | 3470 |
| duplicate URLs | **9**（/studio/ 重复，Phase 21 已修复待部署）|
| invalid URLs | 0 |

### URL 分类
| 类别 | 数量 |
|---|---|
| detail | 1489 |
| similar | 690 |
| watch-order | 9 |
| best-anime | 20 |
| series | 1 |
| studio | 110（含 9 重复） |
| characters | 480 |
| hub（categories/years/seasons/voice-actors 等） | 671 |

## 2. Robots
- `Allow: /` ✅
- `Sitemap: https://bunivoa.com/sitemap.xml` ✅

## 3. 抽查页面（SSR 验证）
本地最终代码（部署后生产应达状态）抽查：

| 类型 | 页数 | HTTP | title | description | canonical | JSON-LD | English UI |
|---|---|---|---|---|---|---|---|
| anime detail | 10 | 200 | ✅ | ✅ | ✅ | ✅ | ✅ |
| similar | 5 | 200 | ✅ | ✅ | ✅ | ✅ | ✅ |
| best-anime | 5 | 200 | ✅ | ✅ | ✅ | ✅ | ✅ |
| watch-order | 3 | 200 | ✅ | ✅ | ✅ | ✅ | ✅ |
| hub | 3 | 200 | ✅ | ✅ | ✅ | ✅ | ✅ |

## 4. GA4 Ready Layer 验证（Step 2）

| 模式 | build | SSR HTML |
|---|---|---|
| GA disabled（无 NEXT_PUBLIC_GA_ID） | ✅ | 无 gtag / googletagmanager script |
| GA enabled（NEXT_PUBLIC_GA_ID=G-TEST123456） | ✅ | 含 gtag init + src（afterInteractive） |

- 不影响 SSR / SEO / Core Web Vitals（无 GA ID 时零加载）
- 文件：`lib/analytics.ts` + `components/GoogleAnalytics.tsx` + layout 集成
