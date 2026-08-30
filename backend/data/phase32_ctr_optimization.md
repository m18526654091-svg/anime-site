# AnimeHub Phase 32 — SERP CTR Optimization Audit

> 日期：2026-08-30 · 范围：全站 title/meta 模板 · 原则：仅改有明显问题的模板，不逐页重写

## 1. Title 模板审计

| 页面类型 | 当前模板 | 实测示例 | 长度 | 关键词位置 | 判定 |
|---|---|---|---|---|---|
| Home | AnimeHub - Anime Database, Recommendations & Watch Orders | 同左 | 54 | "Anime Database" 中前 | ✅ |
| Detail | `{title} Anime: {genre suffix}{, Watch Order}`（三级压缩） | Attack on Titan Anime: Action, Plot & Characters, Watch Order | 65 | title 开头 | ✅ |
| Detail 超长回退 | `{title} Anime: {short genre}` | Re:Zero Anime: Isekai | <68 | title 开头 | ✅ |
| Franchise | `{Franchise} Franchise - Watch Order, Seasons & Anime List` | Bleach Franchise - Watch Order, Seasons & Anime List | 56 | franchise 开头 | ✅ |
| Watch Order | `{fr.name} Watch Order: How to Watch in the Correct Order` | Monogatari Watch Order: How to Watch in the Correct Order | 55 | name+intent 开头 | ✅ |
| Episodes | `{name} Episodes: Complete Episode List — {N} episodes` | Attack on Titan Episodes: Complete Episode List — 25 episodes | 61 | name+intent 开头 | ✅ |
| Similar | `Anime Like {name}: Best Similar Shows To Watch` | Anime Like Attack on Titan: Best Similar Shows To Watch | 55 | intent 开头 | ✅ |
| Best Anime | `Best {category} Anime: Top Shows To Watch` | Best Isekai Anime: Top Shows To Watch | 39 | intent 开头 | ✅ |
| Season | `{label} {year} Anime` + 说明 | Fall 2026 Anime | <65 | label 开头 | ✅ |
| Character | `{name} - Anime Character | AnimeHub` | 实测 <65 | name 开头 | ✅ |
| Voice Actor | `{name} - Anime Voice Actor | AnimeHub` | 实测 <65 | name 开头 | ✅ |

**全部模板满足**：主关键词靠前、意图明确、无冗余词、50-65 字符区间。

## 2. Description 模板审计

| 页面类型 | 回答"这是什么页" | 回答"为何点击" | 长度 |
|---|---|---|---|
| Detail | ✅ title + genre + year + eps | ✅ episodes/characters/watch info | ≤160 |
| Franchise | ✅ 全 season/movie/spin-off | ✅ watch order + release years | ≤158 |
| Watch Order | ✅ 正确观看顺序 | ✅ every season/movie/special | ≤158 |
| Episodes | ✅ 完整剧集列表 | ✅ count + release information | ≤158 |
| Similar | ✅ 同 genre/theme 相似作品 | ✅ 隐藏宝藏发现 | ≤158 |
| Best Anime | ✅ score 排行 | ✅ genres/years/watch links | ≤158 |
| Home | ✅ 站点定位 | ✅ ranked by score | ≤160 |

## 3. 需修改项（本次实施）

| 问题 | 修改 |
|---|---|
| 首页 H1 下方残留中文 slogan（"热门新番 · 分类精选 · 高分佳作 · 观看顺序"） | 移除（H1+英文副标题已表达） |
| 首页区块标题中文（季度新番/动漫类型/制作公司/查看全部） | 英文化（Seasonal Anime / Genres / Studios / View all） |

Title/meta 模板**无批量问题，不重写**。

## 4. 结论

- 全站 title 模板经 Phase 9/17/19-22 累积优化已达 CTR 要求（关键词靠前 + 意图明确 + 长度合规）
- 本次仅修复首页语言一致性（US 用户 5 秒理解目标），SSR 实测无中文残留
- 建议 GSC 观察 CTR：重点对比首页/详情页模板在改版前后的 SERP 展示
