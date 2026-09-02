# AnimeHub Phase 44.4 — Legacy Anime Entity Identity & Duplicate Audit

> 日期：2026-09-02 · AUDIT + MATCHING + DRY-RUN ONLY · 零写操作
> 交付：`phase44_4_entity_resolution.json`（115 pairs 机器可读）+ 本报告
> 可复现：确定性 DB-only 脚本（见 artifact summary.reproduce）

## 1. Identity Model（当前 Anime 如何被识别）

- **Primary**: `anime.id`（内键）+ `slug`（URL 身份，含中文 slug 的 legacy）
- **External stable identity**: `anilist_id` / `mal_id`（**仅 Phase 35+ 英文实体有**；115 legacy 全部 NULL）
- **Cross-language names**: `chinese_title` / `japanese_title` / `romaji_title` / `aliases`（Phase 35 起为已验证 AniList 数据）
- 前端/API 按 `slug` 解析（`/api/anime/by-slug/`，`animePath`）；sitemap 按 `quality_score>=70` 全量提交（**无 slug 语言过滤**）
- 无独立 type 列；无 legacy→新实体显式映射表

**身份鸿沟（Observed）**：legacy 简体中文 title（进击的巨人）与英文实体跨语言名（chinese_title=日文"進撃の巨人"/英文 "Attack on Titan"）**无字符级连接**——DB 内无直接 join 路径。

## 2. Legacy Cohort

**规则**（Phase 44.3 精确沿用）：`title` 含 CJK 汉字 → **115 条**（id 1-121 区间，全部 <200）。
共同属性（Observed）：全部 indexable（quality=100）、无 `anilist_id/mal_id`、112/115 中文 slug、58 部 priority≥60（在 similar sitemap）、21 部有 Characters（41 角色）、114 部有 Episodes（912 行）、ratings/favorites 0。
**解释**：Phase 35 前旧站导入的简体中文"作品级"条目（部分为跨季聚合：如 id=1 进击的巨人 eps=87=全系列；另部分 eps 为占位/不可靠：如 id=4 海贼王 eps=12）。

## 3. Candidate Matching（确定性、DB-only）

对每个 legacy 扫描 3492 英文实体，信号分层：
1. **exact**：`chinese_title` 去标点后 == legacy title，或 `aliases` 含精确项 == legacy title
2. **brand_substring**：英文实体 chinese_title/aliases 去标点后包含 legacy title（常命中同品牌续作/剧场版）
3. **franchise context**：legacy title 命中 18 franchise defs → 该 franchise 英文成员池（**仅上下文，永不单独构成匹配**）

**无外部源连接**（§11/§21）：legacy 无外部 ID；本地 `anilist_anime_candidates.json` 用英文/日文 title，无法按简体中文反查；无已连通的 AniList API。→ 外部验证不可用，如实标注。

## 4. Identity Decisions（115）

| decision | count |
|---|---|
| **SAME_ENTITY** | **2** |
| **MANUAL_REVIEW** | **54** |
| NO_MATCH | 59 |
| DISTINCT_ENTITY | 0 |

NO_MATCH=59 意味着 **DB 内无任何名称连接**（如 灌篮高手/新世纪福音战士/你的名字——英文实体跨语言名用日文/变体）。

## 5. Confidence

| 等级 | count |
|---|---|
| HIGH | **0** |
| MEDIUM | 2 |
| LOW | 54 |
| NONE | 59 |

**无 HIGH**：无外部 ID + 简体↔日文鸿沟 → DB 内不存在达到 HIGH 的证据。MEDIUM=2 也需人工最终确认。

MEDIUM SAME_ENTITY 明细：
- legacy id=31 为美好的世界献上祝福！（2016, 12eps）↔ **Konosuba**（2016, 12eps）— title/year/eps 全吻合
- legacy id=57 日常（2011）↔ **Nichijou - My Ordinary Life**（2011）— title/year 吻合；**eps 冲突**（legacy 12 vs Nichijou 26，legacy 数据错误）

## 6. Conflict Analysis（edge cases 实测）

候选对冲突统计（54 LOW 的 substring 命中主要是**同品牌续作/剧场版**，非本体）：
- **year 冲突**主导（如 2024/2025 vs legacy 1999/2013/2014——legacy 为本体年，命中多为近年续作）
- **type movie vs tv**: 10 例（legacy TV 本体 vs 命中的剧场版/电影条目）
- **episodes 冲突**：如 12 vs 26 / 12 vs 37（legacy 占位 eps vs 真实条目）
- 覆盖 §9 边界类：sequel vs original、movie vs TV、season 差异、多季聚合 legacy（eps≥40）均 observed
- 未发现 SAME_ENTITY 对内的不可调和冲突（id=57 的 eps 冲突归因 legacy 数据质量）

## 7. Dependency Impact（HIGH/MEDIUM 对）

**SAME_ENTITY 2 对**：
| legacy | Characters | Episodes | 说明 |
|---|---|---|---|
| id=31 美好世界 | 2 | 8 行 | 候选 Konosuba 无 anilist_id |
| id=57 日常 | 0 | 8 行 | 候选 Nichijou 有 anilist_id=10165 |

legacy 全量：21 部有 characters(41)、114 部有 episodes(912)、0 ratings/favorites。未来任何 consolidation 需迁移这些 FK（characters.anime_id/episodes.anime_id），并处理 episodes 重复（legacy 8 行 vs 英文实体也有 episodes 行）。

## 8. URL / SEO Risk（分层声明）

**Observed**：
- 115 legacy URL（中文 slug）与英文 counterpart URL **均 200 + `index,follow` + 各自 self-canonical**（实测 id=31/为美好的世界献上祝福 与 /anime/konosuba/；id=57/日常 与 /anime/nichijou-my-ordinary-life/）
- 两套 URL 的 title/H1/meta 各自独立（legacy 中文模板 / 英文模板）
- legacy URL 全部在 sitemap（quality≥70 全量逻辑，中文 slug 无排除）
- **两套 indexable URL 表示同一作品**

**Inferred**：可能的重复内容表示 / 抓取效率浪费（115 中文 URL × 对应英文条目）。
**Unproven**：实际 Google 排名或流量损失（无 GSC 数据，不声称）。

## 9. Exact Mapping

完整机器可读 artifact：`backend/data/phase44_4_entity_resolution.json`
每条含：legacy 字段 + candidates[]（id/title/slug/year/episodes/anilist_id/kind/year_match/episode_match/type_match/conflicts）+ decision/confidence/evidence/future_action + 依赖标记。
确定性方法 + 稳定排序（按 id）+ 时间戳，可复现。

## 10. Future Consolidation Strategy（不实施，仅概述）

仅针对最终人工确认为 SAME_ENTITY 的对（当前 MEDIUM 2 + 人工复核后可扩展）：
- 候选策略：B(legacy→英文 canonical 301) 或 D(merge+redirect)；legacy 中文 URL 应 301 到英文 slug，canonical 指向英文实体
- 复杂度：characters/episodes FK 重指；912 行 episodes 与英文实体 episodes 行去重；115 中文 URL 的 301 需独立发布；rollback 需保留 legacy 行（标记 retired 而非删除）
- **所有 54 MANUAL_REVIEW / 59 NO_MATCH 在外部验证前不得进入任何 consolidation**

## 11. Safety

确认：无 DELETE/UPDATE/INSERT、无 migration、无 merge、无 redirect、无 slug/canonical 变更、无 importer rerun、无 sitemap/元数据改写。仅 SELECT + 生成报告文件。

## 12. Recommendation

**B. CONDITIONAL — manual review required**

理由：
- 识别出 2 个 MEDIUM SAME_ENTITY（title/year 强证据，可人工确认）
- 54 个有品牌候选池（substring/franchise）——可通过**人工 + 外部源（AniList/MAL）复核**确认 anilist_id 后升级
- 59 个 DB 无连接——需人工外部检索，或保持现状（precision 优先，不强行合并）
- **无任何自动 HIGH**：consolidation phase 不得自动执行；前置 = 人工复核 + 外部身份验证
- 下一步（独立阶段）建议：生成 115 个人工复核工单（含候选池 + 需确认的外部 ID），复核后产出 final SAME_ENTITY 清单 → 才可设计 consolidation

## Evidence 标签

| 结论 | 分类 |
|---|---|
| 115 legacy 属性/依赖/URL 状态/决策分布 | **Observed**（DB/SSR 实测） |
| legacy 与英文条目语义等价（Konosuba/Nichijou 等） | **MEDIUM（DB 证据）** |
| 54 substring 命中指向同品牌续作/剧场版 | **Observed + Inferred**（候选属性冲突可见） |
| 重复 URL 造成 SEO 损害 | **Unproven**（无 GSC，不声称） |
| 外部源可用性 | **不可用**（无 API/无法反查，如实） |
