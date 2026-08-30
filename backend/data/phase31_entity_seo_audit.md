# AnimeHub Phase 31 — Entity SEO Coverage Audit

> 日期：2026-08-30 · 范围：Detail / Franchise / Episodes / Watch Order 页意图覆盖审计 · 状态：✅ 完成

## 1. 审计对象与数据来源

- Detail：`frontend/components/AnimeDetailClient.tsx` + `frontend/app/anime/[slug]/page.tsx`
- Franchise：`frontend/app/anime-series/[slug]/page.tsx`
- Episodes：`frontend/app/anime/[slug]/episodes/page.tsx`
- Watch Order：`frontend/app/watch-order/[slug]/page.tsx`
- 全部数据来自 DB 字段（anime.title/chinese_title/genre/year/month/status/episodes/score/studio/author、characters、episodes）

## 2. 搜索意图覆盖矩阵

| 意图 | 示例查询 | 承载页面 | 覆盖 | 说明 |
|---|---|---|---|---|
| Basic Entity | what is X / X anime / X series | detail | ✅ | H1 + Entity Summary + Anime Information + Genres + About + Synopsis |
| Season | X season 1 / season 2 / final season | franchise hub | ✅ | "Season N" 是独立 DB 条目，franchise 页聚合（如 Re:Zero 10 条）。**不建季页**（避免重复 detail） |
| Episode | X episodes / how many episodes | /episodes/ + detail | ✅ | detail Entity Summary/Anime Information 显示集数 + 链接；episodes 页完整列表 |
| Watch Order | X watch order / timeline | watch-order + detail | ✅ | detail Explore More 条件链接 → franchise hub → watch-order（Phase 30 闭环） |
| Character / Cast | X characters / voice actors | detail Characters + /character/ | ✅ | 有数据时 SSR 角色区块 + 声优内链（119 部覆盖） |
| Release Date | X release date | detail | ✅ | Anime Information Release period（year+month→season）+ Release year 链接 |

## 3. 现状细节

### Anime Detail（/anime/{slug}/）
区块顺序（当前实际渲染顺序）：
1. H1（chinese_title || title）
2. **Entity Summary**（Phase 17：`{name} is a {genre} anime released in {release}. Episodes/Status/Genres/Score`）
3. Entity chips（Genre/Year/Region/Status/Episodes）
4. **Anime Information**（Phase 11：Type/Episodes/Status/Release period/Genres/Score + Last updated）
   - ⚠️ **Studio 缺失**（Studio 在 About 后的 meta 卡片中，不在 Anime Information 内）
5. Why This Anime Appears Here
6. **Genres**（Phase 10：中文 genre → 英文 chip → best-anime/categories 链接）
7. **About This Anime**（seo_description/description）
8. Who Should Watch This Anime
9. Author / Studio meta 卡片
10. Synopsis + "Anime Like {title}" 入口
11. Details（friendlyText）+ Tags
12. RatingWidget
13. **Watch Online**（播放器：lines + 选集，有 playData 时）
14. **Characters**（有数据时：角色卡 + Voiced by 声优内链）
15. **Related Anime**（SSR 推荐 + Similar 页链接）
16. **Explore More**（Trending/Discover/Best/Franchise/Similar/Season/Watch Order/New/Year）

JSON-LD（page.tsx）：TVSeries/Movie + **FAQPage**（中文 2 问：是什么/多少集）+ BreadcrumbList + aggregateRating（有评分时）

### Franchise Hub（/anime-series/{slug}/，Phase 30 18 页）
- H1 `{Franchise} Franchise` + intro + Franchise Overview（entries/years/genres）
- All Entries：TV Series & Seasons / Movies & Specials 分组（title/year/score/detail 链接）
- Watch Order CTA（5 个 franchise 匹配时）
- JSON-LD：BreadcrumbList + ItemList
- ⚠️ 缺 **Related Anime** 区块（Step 4 要求）

### Episodes（/anime/{slug}/episodes/）
- H1 + episode count 显式说明（"This anime has N episodes"）
- 列表（episode_number/title）+ View Anime Details / Similar 返回路径
- JSON-LD：BreadcrumbList + ItemList
- ⚠️ **air date 字段不可用**（Episode 表无 air_date）→ 页面不显示（符合任务"不显示不可用字段"）
- ⚠️ 缺 franchise/watch-order 内链（用户看完集数后找观看顺序的路径）

### Watch Order（/watch-order/{slug}/，8 franchise）
- 步骤 + 条目 + More Watch Orders + **Franchise CTA**（Phase 30 已加）
- JSON-LD：BreadcrumbList + ItemList
- 覆盖完整

## 4. 差距总结（本次实施）

| # | 差距 | 改进 | 文件 |
|---|---|---|---|
| 1 | Anime Information 缺 Studio | Anime Information dl 加 Studio 链接行；移除 About 后重复 Studio 卡片 | AnimeDetailClient.tsx |
| 2 | FAQ 为中文 2 问、缺 watch order/release 问题 | 改英文 FAQ + 条件扩展（episodes/year/watch order），仅数据存在时生成 | app/anime/[slug]/page.tsx |
| 3 | Franchise 页缺 Related Anime | 加 Related Anime 区块（franchise 主 genre 的 best-anime + Trending/Discover 真实链接） | app/anime-series/[slug]/page.tsx |
| 4 | Episodes 页缺 franchise 路径 | 匹配 franchise 时加 franchise hub/watch-order 内链 | app/anime/[slug]/episodes/page.tsx |
| 5 | Season 意图 | 已由 franchise 页承载（DB "Season N" 为独立条目），**不建季页** | — |

## 5. 明确不做

- 不建 Season 聚合页（避免与 franchise/detail 意图重复，DB 无 season 字段列）
- 不在 episodes 页伪造 air date（Episode 表无该字段）
- 不在 franchise 页聚合 Characters（跨 5-20 部逐部 fetch 成本高且覆盖仅 119 部，franchise→detail→characters 路径已存在）
- 不批量重写 title（Phase 9/17/19-22 已三级优化，无批量问题）
