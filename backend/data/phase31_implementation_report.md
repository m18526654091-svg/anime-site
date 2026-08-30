# AnimeHub Phase 31 — Implementation Report

> 日期：2026-08-30 · 目标：不新增 URL，提升既有页面搜索意图覆盖与质量 · 状态：✅ 完成

## 1. 变更内容

| # | 变更 | 文件 | 说明 |
|---|---|---|---|
| 1 | Anime Information 补充 **Studio**（链接 studio 页） | `frontend/components/AnimeDetailClient.tsx` | 实体事实完整（Type/Episodes/Status/Release/Genres/Score/**Studio**）；移除 About 后重复的 Studio 卡片 |
| 2 | FAQ 改**英文** + 数据驱动条件扩展 | `frontend/app/anime/[slug]/page.tsx` | 4 问：What is（genre/year/studio 存在时）/ How many episodes（episodes 存在时）/ When released（year 存在时）/ Watch order（franchise 匹配时） |
| 3 | Franchise 页 **Related Anime** 区块 | `frontend/app/anime-series/[slug]/page.tsx` | Trending/Discover/Seasonal/Best/New/Watch Orders 真实链接（非空区块） |
| 4 | Episodes 页 **franchise/watch-order 内链** | `frontend/app/anime/[slug]/episodes/page.tsx` | 匹配 franchise 时显示 Franchise Hub + Watch Order 链接 |

未新增任何 URL；未改 DB schema；未重构 URL。

## 2. FAQ 生成规则（全部来自 DB 字段，不虚构）

| 问题 | 生成条件 | 答案来源 |
|---|---|---|
| What is {name}? | genre \|\| year \|\| studio 任一存在 | 拼接 genre/year/studio 字段 |
| How many episodes does {name} have? | episodes > 0 | anime.episodes |
| When was {name} released? | year 存在 | anime.year |
| Where can I find the {name} watch order? | franchise 匹配 watch-order 页 | matchWatchOrderFranchise |

数据缺失时对应问题**不生成**（如无 episodes 的 Movie 只有 What/When）。

## 3. Step 6 CTR 审计结论

- detail title：三级压缩模板（Phase 9/17/19-22）——ASCII 标题 + genre suffix + watch order 后缀，56-65 字符区间，SERP 不截断 ✅
- episodes title：`{name} Episodes: Complete Episode List — {N} episodes` ✅
- franchise title：`{Franchise} Franchise - Watch Order, Seasons & Anime List`（56-65 字符）✅
- watch-order title：`{fr.name} Watch Order: How to Watch in the Correct Order` ✅
- **无批量问题，不重写**（仅记录）

## 4. 验证结果（Step 7）

| 检查项 | 结果 |
|---|---|
| `npm run typecheck` | ✅ 通过 |
| `npm run build` | ✅ Compiled successfully |
| SSR 20 detail（含正确 slug） | ✅ 全部 200 + canonical + 6 JSON-LD（TVSeries/Movie + FAQPage + BreadcrumbList + aggregateRating 等） |
| SSR 10 franchise | ✅ 全部 200 + canonical + 4 JSON-LD |
| SSR 5 episodes | ✅ 全部 200 + canonical + 2 JSON-LD + episode count title |
| SSR 5 watch-order | ✅ 全部 200 + canonical + 2 JSON-LD |
| FAQ 英文（AoT：4 问） | ✅ JSON 解析 valid，answers 非空 |
| Studio 显示（Anime Information） | ✅ |
| episodes 页 franchise/watch-order 内链 | ✅ |
| franchise 页 Related Anime 区块 | ✅ |
| sitemap 重复 | 未变更（不新增 URL） |

## 5. 变更文件清单

- `frontend/components/AnimeDetailClient.tsx`（Studio 移入 Anime Information）
- `frontend/app/anime/[slug]/page.tsx`（英文数据驱动 FAQ）
- `frontend/app/anime-series/[slug]/page.tsx`（Related Anime 区块）
- `frontend/app/anime/[slug]/episodes/page.tsx`（franchise/watch-order 内链）
- `backend/data/phase31_entity_seo_audit.md`
- `backend/data/phase31_search_intent_report.md`
- `backend/data/phase31_implementation_report.md`

## 6. 后续建议

1. 生产部署（合并 Phase 30+31 一次部署）
2. GSC 观察 FAQ rich result 展示与 CTR（FAQ 从中文改英文后重新验证结构化数据展示）
3. 数据任务：为 Episode 表补充 air_date 后可在 episodes 页展示播出日期（当前不可用字段不显示）
