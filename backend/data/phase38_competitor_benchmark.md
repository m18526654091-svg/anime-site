# AnimeHub Phase 38 — Competitor Benchmark

> 日期：2026-08-30 · 研究：MyAnimeList / IMDb / Anime-Planet / Anime News Network / Crunchyroll（仅记录页面类型/功能概念/IA/SEO 观察，不复制任何内容）

## 1. MyAnimeList（MAL）

### Entity Coverage
- Synopsis / Background / Alternative Titles / Airing Dates / Producers / Relations / Duration / Source / External Links / Statistics
- Characters & Staff 页、Episodes 页、Videos、Reviews、Recommendations、Interest Stacks、News

### 多语言处理（重点）
- **Alternative Titles 区块**：Synonyms（AoT/SnK）+ Japanese（進撃の巨人）+ English + 多国语言（German/Spanish/French）+ "More titles"
- 一个 entity URL（`/anime/16498`），多语言名仅展示不建重复页

### 搜索意图
- 实体信息 / episodes / characters / cast / recommendations / related anime / watch 入口

### 内链网络
- Related Anime（prequel/sequel/spin-off）→ 直接链到相关实体
- Recommendations → 同类型 top 作品
- Characters → 角色页 → VA 页 → 该 VA 其他作品
- Genres/Themes/Demographic → 分类聚合页

### 观察
- **relations（前传/续集/外传）+ recommendations（用户推荐网络）是核心差异化**
- 多语言标题统一在 entity 页，SEO 集中

## 2. IMDb

### Entity Coverage（TV series）
- Plot / Cast（全角色+演员表）/ Episodes（分季）/ Seasons / User Reviews / Trivia / Awards / AKA
- Cast 页（人物）+ 其 filmography

### 搜索意图
- cast / episodes / seasons / release date / awards / trivia / similar titles

### IA 观察
- **Cast 是核心 hub**（person → filmography 反向网络）
- Episodes 分季组织，每季独立 section
- AKA 区集中多语言/替代标题
- "More like this" 推荐

## 3. Anime-Planet（403 拦截，基于已知结构）

- Synopsis / Characters（带"favorites"）/ Tags（精细标签云）/ Recommendations / Related anime
- **Tags 驱动发现**（精细 genre 标签 → tag 聚合页）
- 用户列表（Completed/Plan to Watch）为社区核心

## 4. Anime News Network（ANN Encyclopedia）

### Entity Coverage
- Alternative titles（多语言列表）/ Release dates（地区化）/ Cast & Staff / Related works（franchise/sequel/prequel/adaptation）
- 详细制作人员数据（导演/脚本/音乐）

### 观察
- **跨引用（related works）非常详尽**：区分 manga adaptation / sequel / prequel / side story / alternative version
- 多语言标题结构化存储（数据字段，非页面文案）

## 5. Crunchyroll（反爬，基于已知结构）

- Episodes（分季）/ Seasons / Cast / Related Series / Browse categories / Release calendar
- **分季结构清晰**（Season 1/2/3 导航）

## 6. 综合 Benchmark 结论

| 维度 | 成熟网站共性 | AnimeHub 现状 |
|---|---|---|
| 多语言标题 | entity 页集中展示（MAL 7+ 语言） | ✅ 已做（AKA + alternateName + 搜索） |
| 实体关系 | related works（前传/续集/外传）显式链接 | ⚠️ franchise hub 有，但 detail 页 relation 不细分 |
| Cast 网络 | person → filmography 反向 hub | ⚠️ 有 voice-actor 页，但 detail→VA 覆盖低（476 角色） |
| 推荐 | recommendations 网络（用户驱动） | ⚠️ similar（数据驱动）已有，但聚合/推荐页弱 |
| 精细标签 | tags 云驱动发现 | ⚠️ DB 有 tags 字段但无 tag 聚合 SEO 页 |
| 分季导航 | seasons 结构化（IMDb/Crunchyroll） | ✅ 已做（detail Seasons & Related Entries） |
| 剧集页 | 独立 episode 页 | ⚠️ 仅列表页（无逐集页，数据不足） |
| 制作人员 | staff/director 数据 | ❌ 无（DB 无 staff 表） |
