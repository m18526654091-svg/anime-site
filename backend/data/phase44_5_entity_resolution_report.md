# AnimeHub Phase 44.5 — Legacy Anime Entity Resolution & Human Review System

> 日期：2026-09-02 · READ-ONLY 身份解析 + 复核系统 · 零写操作
> HEAD 基线：e97bd4c（本阶段交付于其后）
> 交付：`backend/scripts/entity_resolver.py` + `phase44_5_legacy_resolve.py` + `tests/test_entity_resolver.py` + `phase44_5_entity_resolution.json` + `phase44_5_review_queue.json` + 本报告

## 1. Scope

- legacy 数：**115**（title 含 CJK，Phase 44.3/44.4 规则精确沿用，id 1-121）
- 匹配运行时间戳：见 artifact `summary.generated_at`
- 数据源：`backend/animehub.db`（本地只读）+ AniList GraphQL API（外部佐证，可复现 `--external` 标志）
- 可复现命令：`python scripts/phase44_5_legacy_resolve.py [--external]`（确定性排序/规范化/时间戳/外部失败记录）

## 2. Identity Method

- **身份定义**：同实体 = 两条 row 表示同一底层作品（非"相似标题"、非"同 franchise"）
- **证据层级**（实现于 `entity_resolver.py`）：
  - Tier 1/2（DB 强信号）：chinese_title/aliases **精确等价**（去标点）== legacy title；外部 AniList id/原生 title
  - Tier 3 佐证：year（±2）、type（movie/tv 由 title 推断）、episode count
  - Tier 4 上下文：brand-substring（仅候选池，永不单独成立）、franchise defs
- **自动 VERIFIED 条件**（§14 实现）：唯一 exact 候选 + year 一致 + 无 year/type 阻塞冲突 + 外部佐证存在且 year 一致。外部不可用 → 一律 MANUAL，**绝不自动升级**。
- **episode mismatch 单独不拒绝**（legacy eps 已知不可靠），记录在 `conflicts` 供复核者见

## 3. Candidate Results

- candidates found：56 legacy 有 ≥1 候选（exact 2、brand-substring 54）
- zero-candidate records：59（DB 无任何名称连接）
- multiple-candidate：54（substring 多为同品牌续作/剧场版）

## 4. Final Identity States（--external 运行）

| 状态 | count |
|---|---|
| **VERIFIED_SAME_ENTITY** | **2** |
| REVIEWED_DISTINCT_ENTITY | 0 |
| **MANUAL_REVIEW_REQUIRED** | **54** |
| **UNRESOLVED** | **59** |

VERIFIED 明细：
- **legacy 31 为美好的世界献上祝福！↔ Konosuba(id=136)**：exact chinese_title + AniList(21202/30831) native='この素晴らしい世界に祝福を！' + year 2016 一致 + 无冲突
- **legacy 57 日常 ↔ Nichijou(id=1549)**：exact chinese_title + AniList(10165) **native='日常'（与 legacy 同字）** + year 2011 一致 + eps note（26 vs 12，legacy 不可靠已记录）

## 5. Confidence

| 等级 | count |
|---|---|
| HIGH | 0 |
| MEDIUM | 2（=VERIFIED 2，外部佐证但无 legacy 自身外部 ID，保守 MEDIUM） |
| LOW / NONE | 54 / 59 |

## 6. External Evidence（AniList 佐证运行）

- 查询 56 个 top candidate：**ok 45 / http_404 9 / error 2**
- AniList-confirmed：2（VERIFIED 对）；MAL-confirmed：2（Konosuba 30831、Nichijou 10165 双 ID）
- unavailable/conflicting：如实记录于 artifact（http_404/error 未升级任何候选）

## 7. Conflict Analysis（记录于 conflicts/edge 分类）

- **year 冲突**主导（substring 候选多为 2020+ 续作 vs legacy 本体年 1999-2016）
- **movie vs TV**：多条 substring 候选为剧场版
- **sequel vs original / season vs aggregate**：legacy 聚合条目（eps≥40）vs 分季英文条目
- **episodes 差异**：legacy 12/26 等占位 vs 真实条目（已记录为 note，不阻塞但可见）
- title 碰撞 / remake / compilation：无自动误判（见 §18 对抗测试）

## 8. Review Queue（`phase44_5_review_queue.json`，54 条）

- **P0：15**（多候选/品牌歧义/需 franchise-season 消歧）
- **P1：39**（单一品牌候选 + 冲突/无外部佐证）
- P2：2 条已 VERIFIED 出队（不重复排队）；P3：UNRESOLVED 59 条不生成复核工单（无候选可复核），保留在 resolution artifact

每条含：legacy 实体全字段 + candidates + external + evidence/conflicts + recommended_action + 空 reviewer_decision/notes 待填。

## 9. Dependency Impact（VERIFIED 2 对，未迁移）

| legacy | Characters | Episodes | candidate | Characters | Episodes |
|---|---|---|---|---|---|
| 31 美好世界 | 2 | 8 | 136 Konosuba | 0 | 0 |
| 57 日常 | 0 | 8 | 1549 Nichijou | 0 | 0 |

legacy 全量：21 部 41 characters、114 部 912 episodes、0 ratings/favorites（§19 其余依赖见 44.4）。候选侧依赖为空 → 未来 consolidation 方向应保留 legacy 依赖数据（迁移至 canonical），本阶段不执行。

## 10. URL / SEO Evidence（VERIFIED 对实测）

**Observed**：legacy URL 与 English URL 均 200 + `index,follow` + 各自 canonical（本地实测：`/anime/为美好的世界献上祝福/` & `/anime/konosuba/`；`/anime/日常/` & `/anime/nichijou-my-ordinary-life/`）；均进 sitemap。
**Inferred**：两套 indexable URL 表示同一作品 → 潜在抓取重复。
**Unproven**：实际排名/流量损失（无 GSC，不声称）。

## 11. Mapping Artifact

- `backend/data/phase44_5_entity_resolution.json`：115 pairs，每条含 legacy/candidates/external/decision/confidence/evidence/conflicts/priority/recommended_action + summary（时间戳/DB/external 标志/分布/复现命令）
- `backend/data/phase44_5_review_queue.json`：54 条人工复核工单（P0/P1）

## 12. Tests

- Baseline：44 passed
- 新增 `tests/test_entity_resolver.py`（纯函数对抗性 14 例：verified w/ external、single exact no external→manual、same title diff year、movie vs TV、sequel vs original、episode mismatch note、multiple exact、brand substring many、no candidate unresolved、external failure not upgraded、same franchise distinct、de_punct、infer_type、exact_cn）
- Final：**58 passed**（44 + 14）

## 13. Safety

确认零写操作：无 INSERT/UPDATE/DELETE、无 merge/migration/redirect/slug/canonical/title 变更、无 importer 重跑、无 sitemap/SEO 改动。脚本只读 DB（SELECT）+ 写新 artifact JSON。

## 14. Decision

# CONDITIONAL

理由：身份解析系统已建立且精确（2 VERIFIED 由**外部 AniList 原生 title 佐证**，54 复核工单含完整候选/证据/冲突），但 **VERIFIED 仅 2/115**，其余需人工复核（54）或外部检索（59）。无任何自动 HIGH（legacy 无外部 ID，MEDIUM 为上限——正确保守）。consolidation phase 前置 = 人工复核队列完成 + 剩余 59 外部人工验证。

下一步建议（独立阶段）：执行 review queue 人工复核 → 更新 VERIFIED/DISTINCT 清单 → 才可设计 consolidation。SEO/关键词/Similar 一律不在此阶段触碰。

## Evidence 标签

| 结论 | 分类 |
|---|---|
| 115 决策分布 / 外部状态 / URL 状态 | **Observed**（本次运行实测） |
| 2 VERIFIED（native title 同字/对应 + year + 无冲突） | **Observed + 外部佐证（MEDIUM）** |
| 其余 113 需人工/外部 | **Observed（证据不足如实）** |
| 重复 URL 损害 | **Unproven**（无 GSC） |
