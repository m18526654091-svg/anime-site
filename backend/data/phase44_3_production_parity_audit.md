# AnimeHub Phase 44.3 — Production Parity + English Entity Data Gap Audit

> 日期：2026-09-01 · 只读审计 + 生产验证（零代码/DB 改动）· HEAD = e779730（= origin/main）
> 本阶段不扩展 SEO、不生成关键词、不修改推荐系统。

## A. Repository / Production Parity

| 项 | 值 |
|---|---|
| 本地仓库 HEAD | `e779730`（= origin/main） |
| Phase 40-A commit | `55c9e88`（5 文件：characters.py / test_characters_naming.py / character page / AnimeDetailClient / api.ts） |
| 生产仓库 | 无法直接核对（远程主机，本机无 docker/.env/ssh） |
| 生产 backend | `1.7.0`（`/api/version` 实测，environment=production） |
| 生产域名 | `https://bunivoa.com`（可达） |
| **Phase 40-A deployed** | **NO**（runtime 证据，见 B） |

## B. Phase 40-A Verification

**Expected behavior（55c9e88）**：
- `GET /api/characters`（list，含 `?anime_id=`）→ 每条含 `name_en` + `native_name`（CharacterLite 新增）
- `GET /api/characters/{slug}` → 含 `native_name`（CharacterOut 新增）
- Anime detail 角色卡：主名 `name_en || name`，native 辅助
- /character/{slug} H1/SEO title：`name_en || name`

**Observed（生产 runtime，2026-09-01）**：
1. `GET https://bunivoa.com/api/characters` → 480 条，keys=`[anime_slug,id,name,slug,voice_actors]`，**无 name_en/native_name**
2. `GET https://bunivoa.com/api/characters/gojo-satoru` → `{name:'五条悟', name_en:'Satoru Gojo', native_name:null}`（= 55c9e88 **之前**状态：detail 早有 name_en，native_name 是 40-A 新增 → 缺失）
3. `/anime/kaiju-no-8/` 角色卡 → **"日比野卡夫卡"**（中文名；40-A 应为 "Kafka Hibino"）
4. `/character/gojo-satoru/` → H1 `五条悟`（40-A 应为 `Satoru Gojo`）

**结论**：Phase 40-A 后端与前端**均未部署**到生产。生产运行的是 55c9e88 之前的 image。

**Deployment 准备（需生产主机执行）**：
```bash
# on production host, repo at HEAD containing 55c9e88:
git pull
docker compose build backend frontend
docker compose up -d backend frontend
# verify:
#  curl https://bunivoa.com/api/characters?anime_id=<id>   # name_en present
#  curl https://bunivoa.com/api/characters/gojo-satoru      # native_name == '五条悟'
#  curl -s https://bunivoa.com/anime/kaiju-no-8/ | grep -c Kafka   # > 0
```
Deployment 后验证清单：backend health / frontend health / homepage 200 / characters API name_en / 一个 detail 页角色卡 / 一个 character 页 H1 / sitemap 有效 / 无 5xx 日志。

**Tests**：后端 44 passed、前端 14 passed、typecheck/build pass（本阶段无代码改动，baseline 即 final）。

## C. English Entity Data Audit（本地 animehub.db 3607）

字段实况：anime 表**无独立 english_title 列**；现有字段 `title`（主显示，语言混合）+ `chinese_title` + `japanese_title`（Phase 35 日文 native）+ `romaji_title` + `aliases`（JSON 别名）。无 backfill pipeline 写入 `english_title`（此前回填的是 japanese/romaji/aliases 三列）。

**分类结果（3607 条）**：
| 类 | 定义 | 数量 | % |
|---|---|---|---|
| **A** | title 为英文/拉丁可用（无 CJK/假名） | **3492** | 96.8% |
| **E** | title 含中文（legacy 中文实体） | **115** | 3.2% |
| B/C/D | — | 0 | — |

说明：B（非英文但有 romaji/alias 英文源）实际为 0——凡 title 含 CJK/假名的实体都落入 E/D，而无 CJK/假名的均算 A（含弯引号等拉丁标点）。DB 中不存在"英文 title 缺失且可从本地字段补齐"的记录；也不存在 kana-only canonical（D）记录。

**E 类 115 细查**：
- 全部 indexable（quality 100，is_indexable=1）
- 58 部 anime_seo_priority≥60（进 similar sitemap）
- 112/115 slug 为中文
- **外部 ID：全部无 anilist_id/mal_id**
- **根因**：Phase 35 前的 legacy 中文实体（id≈1-115），与 Phase 35-37 导入的英文实体（带 anilist_id）**表示同一批作品**

**重复性验证**：
- 53/115 直接验证 counterpart（其中文名被英文实体的 chinese_title/aliases 引用）
- 其余 62 经英文 title 反查，绝大多数 counterpart 存在（My Hero Academia↔我的英雄学院、Neon Genesis Evangelion↔新世纪福音战士、Your Name↔你的名字、Spirited Away↔千与千寻、Slam Dunk↔灌篮高手 等）——英文实体的 chinese_title 多用日文/变体导致漏配
- 少量 manual review（虫师/Mushishi 等）

## D. Priority Records（30+ 代表例，完整见 `_s443_gap.json`/`_s443_eclass.json` 分析）

**Legacy 中文实体 → 英文 counterpart（去重治理候选，backfill/leave 判定见下）**：
进击的巨人(id1)/鬼灭之刃(id2)/咒术回战(id3)/海贼王(id4)/火影忍者(id5)/间谍过家家(id6)/电锯人(id7)/芙莉莲(id8)/我推的孩子(id9)/孤独摇滚(id10)/辉夜大小姐(id11)/石纪元(id12)/约定的梦幻岛(id13)/五等分的新娘(id14)/刀剑神域(id15)/灌篮高手(id19)/钢之炼金术师FA(id25)/新世纪福音战士(id26)/你的名字(id42)/千与千寻(id44)/哈尔的移动城堡(id47)/转生史莱姆(id35)/排球少年(id18)/我的英雄学院(id17)/天气之子(id43)/异世界食堂(id38)…
→ **leave unchanged（本阶段）**：不可 merge/改 slug/删除（§19/§11）；补英文 title 反而与英文实体混淆。属**独立数据治理阶段**候选。

**manual review 候选**：虫师(id40, Mushishi 无英文实体命中)、冰上的尤里(id21, 仅 side-story 英文实体) 等 ~5-10 部。

**backfill 候选**：**0**（无外部 ID 可关联；现有安全源无法定位）。

## E. Backfill Source

- **权威源层级**：AniList（Phase 35 已验证回填管道）→ 本地 `anilist_anime_candidates.json` → 现有 `backfill_external_ids.py` / `persist_external_entities.py`
- **可映射性**：E 类全部无 anilist_id/mal_id → **无法用现有 pipeline 安全 join**（用 title 猜测外部 ID 不可靠，任务禁止 LLM/scrape）
- **结论**：backfill 源对 E 类**不可用**；A 类 3492 无需 backfill

## F. Dry-Run Backfill

**不适用**。原因：
1. E 类 115 缺外部 ID → 无安全关联源
2. E 类本质是 legacy 重复实体，补英文 title 会制造双英文名混淆
3. A 类 3492 无缺口
→ 诚实声明：**本阶段无安全可执行的 backfill**；正确路径是 legacy 实体治理（映射/redirect），需单独授权阶段。

## G. SEO Surface Impact

**A 类 3492（96.8%）**：英文 title 完整 → title/H1/meta/OG/JSON-LD/sitemap/内链/Similar/Franchise 全部正常英文。

**E 类 115（3.2%）**——中文 title/slug 实体，影响以下 surface（均为英文站点的非英文实体页）：
| Surface | 影响 |
|---|---|
| title/H1/meta/OG | 中文名（如 `/anime/火影忍者/` title=`火影忍者 Anime…`） |
| sitemap | 含 115 个中文 slug URL（quality≥70 全提交，无 slug 语言过滤） |
| 内链卡 | displayName=chinese_title→中文 |
| Similar/Franchise | 模板英文、实体名中文（Phase 44.2 已见火影忍者类似页） |
| JSON-LD | name=中文 |
| **重复风险** | 与英文 counterpart 页（如 /anime/my-hero-academia/）同作品双 URL |

**关键限制**：这 115 页的"中文"是**实体名**（非模板泄漏——Phase 44.1/44.2 已验证模板层干净）；问题在**实体层重复**，修复需数据治理而非模板/backfill。

## H. Remaining Blockers

1. **真实 GSC US CSV 未提供**（40-B/C/D/E + 44.2/44.3 SEO 证据阻塞）
2. **Google US/ES/JP SERP 不可用**（429）
3. **Phase 40-A 未部署生产**（本次已用 runtime 证据确认；需生产主机执行 compose build/up）
4. **115 legacy 中文实体 vs 英文实体重复**（需独立治理决策：canonical 归属 + redirect 策略）
5. 少量 manual-review 实体（虫师等）

## I. Recommended Next Phase

**选择 2：Fix data-source issues first**（非 SEO 扩展）

理由：
- 40-A 生产部署是已确认的待办（可立即执行）
- 115 legacy 实体重复是数据源问题（Phase 35 新旧实体并存），backfill 不适用——需治理设计（幂等映射 + redirect 风险评估），与 SEO 内容无关
- 在真实 GSC 数据到位前，任何 SEO 扩展都违反证据原则

## Evidence 标签

| 结论 | 分类 |
|---|---|
| 生产 40-A 未部署（API 无 name_en、卡名中文、H1 中文） | **Observed**（runtime 实测） |
| A=3492 / E=115 分类、E 无外部 ID | **Observed**（DB 实测） |
| E 类与英文实体重复（53 直接 + 其余反查） | **Observed**（DB 交叉验证） |
| E 类重复会损害英文 SEO/造成重复内容 | **Inferred**（无 GSC 证明实际索引影响） |
| backfill 候选 = 0 | **Inferred**（基于外部 ID 缺失 + 重复推断） |
