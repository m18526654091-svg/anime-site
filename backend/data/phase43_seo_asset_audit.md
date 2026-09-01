# AnimeHub Phase 43 — SEO Asset Expansion Research: Discovery Pages Opportunity Audit

> 日期：2026-09-01 · 类型：研究/规划（零实现）· 证据口径：Google US SERP 不可用、GSC 未提供 → 全部结论为 **Inferred / Candidate**（无 Observed）

## 1. 现有 SEO 资产清点（Step 1 — 实测路由 + DB）

### A. Anime discovery / collection 页

| 路由 | 用途 | 数据源 | Indexable 数 | 当前 SEO 价值 | 弱点 | 机会 |
|---|---|---|---|---|---|---|
| `/best-anime/` + 17 个英文 category 子页 | 英文"最佳 X"意图 | score + genre 集合 + 静态 intro | 18（静态） | ★★★★ 最完整的英文意图页集 | category 集合静态写死 | 有 SERP 证据后扩展 category |
| `/top-anime` `/high-score` `/ranking` | 高分/排行意图 | score 排序 | 3 | ★★★ | **三页语义高度重叠（cannibalization 风险 Inferred）** | 统一 canonical 或差异化 |
| `/latest-anime` `/new-anime` | 新番意图 | 数据导入时间/年份 | 2 | ★★★ | 与 seasonal 页重叠 | GSC 验证哪个入口胜出 |
| `/trending-anime` | 趋势 | score+popularity | 1 | ★★☆ | 排序逻辑与 top 相似 | 待 GSC |
| `/upcoming-anime` | 未来作品 | status="未上映" | 1 | ★☆ **薄页** | **仅 4 部"未上映"** | 数据补齐前价值低 |
| `/discover-anime` | 探索 | 多维度 | 1 | ★★☆ | 无独立数据视角 | 保持 |
| `/categories/` + `/categories/[genre]` | 中文 genre 页 | genre 组合精确匹配 | 175（≥5） | ★★☆ | **883 组合中 434 个单部**；精确组合匹配；fallback meta 为中文模板 | genre 数据重构后才有价值 |
| `/tags/` + `/tags/[tag]` | 标签页 | tags 列（/分隔） | **0（全 noindex）** | ☆ 正确决策 | 与 genre 高度重叠 | **维持 noindex** |
| `/years/` + `/years/[year]` | 年份页 | year 字段 | 49 | ★★★ | 9 个单部薄年 | 经典年代页需 SERP 证据 |
| `/seasons/` + `/season/{y}/{s}` + `/season/{s}-{y}-anime/` | 季度页 | month 精确匹配（75.7% 覆盖） | 去冗余后 | ★★★ | 冗余季页已 noindex（正确） | 当前季新鲜度 |

### B. Entity network 页

| 路由 | Indexable 数 | 价值 |
|---|---|---|
| `/anime/{slug}/`（+`/episodes/` `/similar/`） | 3607（quality≥70 全提交；0 个 <50 noindex） | ★★★★★ 核心资产 |
| `/character/{slug}/` | 476 | ★★★☆ 数据覆盖有限（仅 119 部有角色） |
| `/voice-actor/{slug}/` | 341 | ★★★☆ |
| `/studio/{studio}/` | 194（≥3 部） | ★★★ |

### C. Relationship 页

| 路由 | Indexable 数 | 价值 |
|---|---|---|
| `/anime-series/{slug}/` | 18 | ★★★★ franchise hub |
| `/watch-order/{slug}/` + `/watch-order/` | 9 | ★★★☆ |
| `/anime/{slug}/similar/` | 690（priority≥60） | ★★★★ 但**未充分利用** |

## 2. 搜索意图缺口（Step 2 — 全为 Inferred）

| 意图组 | 现状 | 缺口 |
|---|---|---|
| A. Recommendation（best X anime） | best-anime 17 英文页 + top/high-score/ranking | top/high-score/ranking 三页重叠 |
| B. Similarity（anime like X） | similar 690 页 | **2128 部（priority<20）无 similar 页**；且 690 页内容质量未审计 |
| C. Franchise navigation | watch-order 8 + franchise hub 18 | **10 个 franchise 有 hub 无 watch-order**（结构不一致） |
| D. Character/entity exploration | character 476 / VA 341 | 角色实体数据覆盖低（119/3607 部）——**数据问题非页面问题** |
| E. Seasonal discovery | season + new/latest/upcoming | **upcoming-anime 仅 4 部（薄）** |

## 3. 数据能力评估（Step 3-4 — 每个候选类型的质量测试）

| 候选页面类型 | 用户价值 | 数据独特性 | 内链价值 | 薄页风险 | 判定 |
|---|---|---|---|---|---|
| Similar 页全量（3607 全覆盖） | 高（"anime like X"） | 中（genre-based） | 高（anime↔anime） | 低 priority 的 similar 内容同质化 | **P1 审计/质量提升** |
| Franchise watch-order 补齐（10 个） | 高（franchise 导航） | 高（排序关系来自 franchise defs） | 高（hub→detail） | 无（每 franchise 独立内容） | **P1 候选** |
| English best-anime 扩展 | 高 | 中（score+genre 集合） | 中 | 需 SERP 验证意图 | **P2** |
| Season 当前季增强 | 高（时效） | 高（2026 有 166 部） | 中 | 内容随数据变化 | **P2** |
| Character 实体扩容 | 高 | 高 | 高 | 无（实体页模式已验证） | **P2（数据导入）** |
| Tag 页恢复 index | 低 | 低（与 genre 重叠） | 低 | 高 | **P3 拒绝** |
| 单部 genre 组合页 | 低 | 低 | 低 | 高 | **P3 拒绝（noindex 正确）** |
| "strongest anime characters" 类 editorial | 中 | **无 power-level 数据** | 中 | 高（编造排名） | **P3 拒绝** |

## 4. 现有 collection 页审计（Step 5 — 只报告不修改）

### Best Anime ✅
- 17 个 category 静态定义，score 降序 + genre 集合过滤 + 英文 intro/JSON-LD
- 排序逻辑合理（"best"由 score 支撑）；类别精选自已知英文意图词
- 风险：category 间部分重叠（action/mecha/sports 均含战斗）

### Genre pages ⚠️ 核心数据问题
- **883 个 genre 组合**，其中 434 个仅 1 部、274 个 2-4 部；组合长度 1→115 个标签不等（存在超长垃圾组合，如 97/115 标签串）
- `/categories/{genre}` 按**精确组合**匹配（`/categories/动作/` ≠ 含"动作"的全部）
- 组合 <5 部 → noindex（175 页 indexable）——**该过滤正确**，但根因是 genre 数据组合化
- fallback meta description 是中文模板（`AnimeHub 收录的{genre}类型动漫资源…`）——**与英文内容不匹配**（Phase 41 遗留）

### Year pages ✅ 基本健康
- 49 年覆盖 1960s-2027；9 个单部薄年（2027=1 部）

### Season pages ✅ 处理正确
- month 覆盖 75.7%；冗余季页（同 ID 集合）已 noindex；英文 slug 页已建

### Tag pages ✅ noindex 正确
- tags 列全量非空（3607/3607）但全部 noindex——与 genre 重叠决策正确

## 5. 高价值机会（Step 8 — P1/P2/P3）

### P1（高价值 · 数据支持 · 风险可控）
1. **Similar pages 质量审计 + 覆盖评估**（现有 690 页资产未充分利用；意图"anime like X"明确）
   - 需审计：similar 内容是否实体特定（而非模板化 genre 列表）
   - 数据：genre 集合 + score；覆盖可评估扩展到 priority 40+
2. **Franchise watch-order 补齐**（18 hub vs 8 watch-order 的不一致）
   - 每个 franchise 已有排序定义（Phase 30），watch-order 页模板已验证
   - 实施前需样本验证 5-10 个 franchise

### P2（有趣但需证据）
1. English best-anime 新 category（仅在有真实 SERP/搜索行为证据后）
2. 当前季 season 页增强（2026 秋即将开播，数据已有 166 部 2026）
3. Character/VA 实体数据扩容（476→更多，属数据导入非页面架构）

### P3（当前避免）
1. Tag 页恢复 index（与 genre 重叠，维持 noindex）
2. 单部 genre 组合页、薄年页（维持 noindex）
3. "最强角色/榜单" editorial 页（无数据支持）
4. 任何 URL 变体（title/franchise/series 重复页）
5. top-anime/high-score/ranking 三页合并（需先有 GSC 证明重叠有害）

## 6. 实现建议（Step 9 — 本阶段不实现）

优先顺序（研究→样本→验证→小规模）：
1. **similar 页质量抽样**（10 页对照"实体特定 vs 模板化"）——纯只读
2. **franchise watch-order 覆盖矩阵**（18 franchise 中哪些真正需要 watch-order）
3. 等真实 GSC/SERP：验证 similar 页曝光、best-anime 各 category 表现、seasonal 页点击

## 7. 多语言路线（Step 7）

- 本阶段全部英文/US 视角
- 西/日语：所有上述机会**不可翻译**——需各自独立 SERP 研究（en/es/ja 意图不同，如 es 重 personajes、ja 重 話数/声優）
- 未来 URL 架构（/es/ /ja/）决策与本阶段无关，暂不涉及

## 8. 证据分类声明

| 结论 | 分类 | 依据 |
|---|---|---|
| 现有资产覆盖（路由/页数/数据） | **Observed** | 本地 SSR + DB 实测 |
| 意图缺口（similar 覆盖/franchise 不一致/upcoming 薄） | **Inferred** | 从结构差异推导 |
| P1/P2/P3 机会排序 | **Candidate** | 无真实 SERP/GSC 验证 |
| Google US SERP 结果 / 搜索量 / CTR | **无** | 不可用/未提供，未虚构 |
