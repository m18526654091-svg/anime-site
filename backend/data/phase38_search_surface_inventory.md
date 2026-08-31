# AnimeHub Phase 38 — Search Surface Inventory

> 日期：2026-08-30 · 当前真实 SEO 资产清点（本地 3607 实体）

## 1. 页面类型清单

| 页面类型 | URL 模式 | 数量 | 结构化数据 | 搜索意图 |
|---|---|---|---|---|
| Anime detail | /anime/{slug}/ | 3607（indexable ~2000+） | TVSeries/Movie + FAQPage + BreadcrumbList + aggregateRating | 实体/信息/集数/发布 |
| Similar | /anime/{slug}/similar/ | ~690 | BreadcrumbList + ItemList | anime like X |
| Episodes | /anime/{slug}/episodes/ | 119（有数据） | BreadcrumbList + ItemList | episodes/how many |
| Franchise | /anime-series/{slug}/ | 18 | BreadcrumbList + ItemList | franchise/seasons/watch order |
| Watch Order | /watch-order/{slug}/ | 8 | BreadcrumbList + ItemList | watch order/timeline |
| Character | /character/{slug}/ | 476 | Person + BreadcrumbList | character/voice |
| Voice Actor | /voice-actor/{slug}/ | 341 | Person | VA works/roles |
| Studio | /studio/{studio}/ | ~110 | — | studio anime |
| Genre | /categories/{genre}/ + /best-anime/{category}/ | 19 best + 分类 | ItemList | best genre anime |
| Year | /years/{year}/ | 47 | — | {year} anime |
| Season | /season/{slug}/ + /seasons/ | ~91 | ItemList | seasonal anime |
| 聚合 | /top-anime/ /trending-anime/ /latest-anime/ /discover-anime/ /new-anime/ /upcoming-anime/ | 8 | ItemList | discovery |
| 静态 | /about/ /terms/ /privacy/ | 3 | — | informational |

## 2. 实体覆盖

| 实体类型 | 数量 | 说明 |
|---|---|---|
| Anime | 3607 | TV 1645 / MOVIE 358 / OVA 232 / ONA 219 / SPECIAL 152 |
| Characters | 476 | 覆盖 119 部 anime |
| Voice Actors | 341 | |
| Studios | ~110 | |
| Franchise Hub | 18 | |
| Watch Order | 8 | |

## 3. 搜索名称

- 可搜索名称总数：**9031**（avg 2.5/实体）
- 多语言覆盖：JP/Romaji/Aliases 72.3%（2607 条）

## 4. 缺口观察

- **Movie/OVA 实体已有 742 条但无独立"Movies"列表页**（/movies/ /ova/ 不存在）
- **Characters 覆盖低**（476 角色 vs 3607 anime）——大量新导入 anime 无角色页
- **Season 无独立聚合页**（franchise 内 season 导航已建）
- **Watch Order 仅 8 个 franchise**（18 个 franchise hub 中 10 个无顺序指引）
- **无 "anime recommendations" 聚合页**（有 similar 但无推荐引擎页）
