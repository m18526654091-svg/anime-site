# AnimeHub Phase 44.2 — Controlled Similar Anime Pilot & Measurement Report

> 日期：2026-09-01 · 实验（非扩展）· 交付：`phase44_2_pilot_cohort.json` + 本报告
> 证据口径：本地 DB/API/SSR 实测（Observed）；GSC 数据未提供、Google US SERP 不可用 → SEO 证据为空（如实声明）

## 1. Pilot Cohort（25 部）

**选择方法（可复现、分层确定性、无主观偏好）**：
- 资格池：690 个现有 indexable similar 页（anime_seo_priority≥60 且 slug 非数字，与 sitemap 口径一致）
- 分层：5 个 priority band（100 / 90-99 / 80-89 / 70-79 / 60-69），每 band 按 (priority desc, id asc) 取前 5
- franchise 覆盖保证：每 band 若 franchise 命中 <2，按 id asc 从该 band 的 franchise 条目补足（确定性替换尾部非 franchise 条目）

**分布**：franchise 10 / standalone 15；old(<2010) 6 / mid 12 / recent(≥2022) 7；22 个 distinct genre；每 band 5 部。

**代表性标题**：OVERLORD、Bleach、Dragon Ball Z、Vinland Saga、One Piece Fan Letter、Re:ZERO S4、Neon Genesis Evangelion、BLEACH TYBW、One-Punch Man S3、My Hero Academia、Tokyo Ghoul、JoJo TV、Frieren S2/Movie、Kaguya OVA、火影忍者（数据缺口样本）等。

## 2. Pre-Pilot Baseline（与 Phase 44 相同方法论）

| 指标 | Phase 44 (10页) | Phase 44.2 (25页) |
|---|---|---|
| 质量（cap 前） | 66 strong + 14 reasonable + 0 weak + 0 irr | **183 strong + 17 reasonable + 0 + 0** |
| strong 占比 | 82.5% | **91.5%** |
| 跨页 Jaccard mean | 0.00 | **0.012** |
| 自推荐 | 0 | **0** |
| 重复推荐 | 0 | **0** |

## 3. Template Quality

- **语言泄漏**：模板层（reason/卡片 genre 徽章/lede 事实/desc）**25/25 零中文**（SSR 实测）
- **实体特定性**：lede 全为事实句（genre/year/episodes/ASCII studio），如 `Frieren Season 2 is a Fantasy, Adventure title with 12 episodes from 2024 by Toho`
- **事实准确性**：全部来自 DB 字段；无编造语义/主题/观众声称
- **模板重复**：尾句共享措辞（有意保留，不做随机同义词）

## 4. Recommendation Impact（cap=2 前后）

| 指标 | Before cap | After cap |
|---|---|---|
| strong | 183 | **183（无损耗）** |
| reasonable | 17 | **17（无损耗）** |
| unique franchises/页（avg） | 2.1 | **2.2** |
| ≤2 franchise 页数 | 16/25 | 14/25 |
| 自推荐 / 重复 | 0 / 0 | **0 / 0** |

**Cap 实际影响**：OVERLORD/One Piece Fan Letter/Re:ZERO/BLEACH TYBW/OPM S3/S2/MHA/Frieren S2/Movie 等 franchise 页均被替换 1-3 个同 franchise 条目 → 跨 franchise 推荐。**质量零损耗**（替换进来的同为 strong/reasonable）。

**高重叠对（跨页）**：Frieren S2↔Movie = 0.78、Evangelion↔EoE = 0.60（均为同 franchise 条目，推荐集语义必然相近）；跨 franchise 对仍 ≈0。

## 5. Technical SEO（25/25 SSR 实测）

- HTTP **200** × 25
- canonical 自指 ✓（含 percent-encoded 中文 slug 页）
- title/H1/meta desc/OG 存在 ✓
- JSON-LD：BreadcrumbList + ItemList × 25 ✓
- robots：`index, follow` × 25 ✓
- 内链：9 个 anime 链接（8 推荐 + 源）✓
- **sitemap**：pilot 页全部已在（693 similar URLs，总 5863 loc）——**本阶段 0 新 URL**（pilot 页均现有页面）

## 6. GSC Evidence

**无**。真实 GSC US 数据未提供。无 impressions/clicks/CTR/position/query——未虚构。

## 7. SERP Evidence

**无**。Google US SERP 不可用（429 防护）。未用 Bing/DDG 冒充。无搜索量/排名声称。

## 8. Problems Found

**Observed**：
- 1/25 页（火影忍者 id=5）title/slug 本身为中文实体名（DB 无英文 title）→ desc/lede 含实体名中文。模板层完好（reason/badge 干净、canonical/robots/JSON-LD 正确）。属既有数据缺口（Phase 35 英文 title 回填未覆盖该条目），非模板缺陷
- 同 franchise 条目对推荐集高重叠（Frieren S2/Movie 0.78）——语义合理但跨页有重复

**Inferred**：
- franchise cap=2 已消除可见同 franchise 拥挤（Phase 44 的 AoT 8/8 → 2/8），质量无损耗；cap 对非 franchise 集中的页几乎无影响（多数页 unchanged）
- studio 浓度（Monster 7/8 MADHOUSE 模式）在 25 页样本中未系统性复现（未统计为普遍问题，保持监控）

**Hypothesis（非事实）**：
- "anime like X" 意图页若质量/技术达标，真实 GSC 数据可能显示曝光——**待验证**，未声称

## 9. Decision：**CONDITIONAL**

- 内容/推荐/技术质量：**全部达标**（91.5% strong、0 无关、0 self/dup、模板零泄漏、技术 25/25）
- SEO 证据：**空白**（无 GSC/SERP 真实数据）
- 按 §20/§21 规则：**不得以"质量好"宣告 PASS**——SEO 可行性未证实

## 10. Expansion Recommendation：**Continue pilot（不扩大）**

1. 当前 690 个 indexable similar 页保持现状（不新增、不删除）
2. 将 cohort 25 部作为 **GSC 观测组**——真实 GSC 数据到位后对比 cohort vs 非 cohort 的 impressions/clicks/queries
3. 数据到位前：**不扩展**（§21 第 9/10 条未满足）
4. 修复 Observed 数据缺口（火影忍者等无英文 title 条目）可提升英文页质量，但属数据修复（非本阶段范围，记录待办）

## Evidence 标签

| 结论 | 分类 |
|---|---|
| 质量/重叠/cap 影响/技术 SEO/语言 | **Observed**（本地实测） |
| cap=2 有效性、studio 非普遍 | **Inferred** |
| Similar 页搜索可见性 | **无证据**（GSC/SERP 空白） |
| "anime like X" US 需求 | **Hypothesis** |
