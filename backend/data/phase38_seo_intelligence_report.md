# AnimeHub Phase 38 — SEO Intelligence Report

> 日期：2026-08-30 · 状态：Production sync 阻塞待人工 + 本地情报分析完成

---

## 1. Production（Step 1-4）

### 状态：⚠️ 阻塞（无 SSH 凭据，需人工在 43.133.211.250 执行）

| 项 | 本地（已就绪） | Production（现状） |
|---|---|---|
| Anime count | 3607 | 1479（Phase 9 状态） |
| 多语言覆盖 | 72.3%（2607） | 0%（无 3 新列） |
| sitemap | 5863 | 3469（Phase 9，dups=9 未修） |
| Phase 35-37 代码 | ✅ push origin/main (f2a4fe6) | 未部署 |

**交付物**：`phase38_production_sync_runbook.md`（备份 → migration → 导入 2128 → 回填 479 → 验证 → 回滚预案）
**预期部署结果**：added≈2128、updated=0、dups=0、CRITICAL=0（本地实测口径）

### 部署后验证清单（Step 2-4）
- Entity：3607、重复外部 ID 0、slug 冲突 0
- SEO：sitemap 5863、dups=0、malformed=0
- 搜索：30 抽查多语言解析同实体
- SSR：40 页（20 新 + 10 旧 + 10 Movie/OVA）HTTP 200

---

## 2. GSC Baseline（Step 5）

### 状态：⚠️ 无真实数据（bunivoa.com 域名验证 + sitemap 提交未完成，需人工）

当前可用信息：**无**（Phase 24 标记 WAITING FOR REAL DATA，不伪造）

### 部署后需采集
- impressions / clicks / CTR / avg position / indexed pages / top queries / top pages
- 意图类别监测（anime name/episodes/watch order/characters/cast/season/release date/similar/genre/year/franchise）
- 7/28/90 天趋势

> 重要：不能因某类别当前无 impression 就判定无需求（GSC 样本尚未建立）

---

## 3. Search Surface Inventory（Step 6）

详见 `phase38_search_surface_inventory.md`

- 页面类型：40+ 路由（detail/similar/episodes/franchise/watch-order/character/voice-actor/studio/genre/year/season/聚合/静态）
- 实体：Anime 3607（TV 1645/MOVIE 358/OVA 232/ONA 219/SPECIAL 152）、Character 476、VA 341
- 搜索名称：9031（avg 2.5/实体）
- **关键观察**：Movie/OVA 实体 742 条但无独立列表页；Characters 覆盖 476/3607 极低

---

## 4. Competitor Benchmark（Step 7）

详见 `phase38_competitor_benchmark.md`

| 维度 | 成熟网站（MAL/IMDb/ANN/Anime-Planet/Crunchyroll） | AnimeHub |
|---|---|---|
| 多语言标题 | entity 页集中（MAL 7+ 语言） | ✅ 已做 |
| 实体关系 | related works 细分（前传/续集/外传） | ⚠️ 部分 |
| Cast 网络 | person → filmography 反向 hub | ⚠️ 覆盖低 |
| 精细标签 | tag 云驱动发现 | ⚠️ 无 tag 聚合 SEO 页 |
| 分季导航 | seasons 结构化 | ✅ 已做 |
| 逐集页 | 独立 episode 页 | ❌ 数据不足 |

---

## 5. Gap Analysis（Step 8-9）

### Priority A — 高搜索价值 + 易实现 + 兼容现有架构
| Gap | 依据 | 难度 |
|---|---|---|
| Movie/OVA 列表页（/movies/ /ova/） | 742 实体已有仅缺聚合页；"best anime movies" 高频 | 低 |
| Tags 聚合 SEO 页 | DB tags 字段（AniList）已就绪；MAL/Anime-Planet 验证 | 低 |
| Watch Order 扩展（8→18） | 10 个 franchise hub 无顺序页；高意图 | 中 |
| Franchise Hub 扩展（18→57） | Phase 29 审计 57 集群 | 中 |
| Characters 数据扩充 | 476 vs 3607；cast/character 核心意图 | 中（数据任务） |
| Episodes 数据扩充 | 119 vs 3607；episodes 高频意图 | 中（数据任务） |

### Priority B — 有潜力需更多数据
- Voice Actor 页增强（Known for/Related）
- Studio 页增强（作品矩阵/年份）
- 推荐页（recommendations 引擎）
- Season 聚合页（Top franchise 季页）
- 中文标题数据源接入

### Priority C — 当前不值得
- 逐集 detail 页（需巨量数据）
- Staff/Director 表（新 schema）
- 用户系统 / 收藏 / 评论 / Watch Progress
- TV/Movies 大规模迁移

---

## 6. Top 20 Opportunities（Step 12）

| # | 机会 | 意图/查询 | 现有覆盖 | 难度 | SEO 风险 | 优先级 |
|---|---|---|---|---|---|---|
| 1 | Movie 列表页 | best anime movies | 358 实体无页 | 低 | 低 | High |
| 2 | OVA/Special 列表页 | best anime ova | 384 实体无页 | 低 | 低 | High |
| 3 | Tags 聚合页 | {tag} anime list | 字段就绪 | 低 | 低 | High |
| 4 | Watch Order 扩至 18 | {franchise} watch order | 8/18 | 中 | 低 | High |
| 5 | Characters 数据扩充（Top 100 anime） | {anime} characters | 476 角色 | 中 | 低 | High |
| 6 | Episodes 数据扩充（Top 100） | {anime} episodes | 119 部 | 中 | 低 | High |
| 7 | Franchise Hub 57 集群 | {franchise} list | 18/57 | 中 | 中 | High |
| 8 | detail Relation 细分（prequel/sequel） | 相关搜索 | franchise 聚合 | 中 | 中 | High |
| 9 | 2026 fall/新番页增强 | new anime season | 已有时效页 | 低 | 低 | High |
| 10 | Voice Actor Known for | {VA} works | 341 页 | 中 | 低 | Medium |
| 11 | Studio 作品矩阵 | {studio} anime list | 110 页 | 中 | 低 | Medium |
| 12 | 高分 Movie 榜 | top anime movies | 无 | 低 | 低 | Medium |
| 13 | 推荐聚合页 | recommended anime | similar | 中 | 中 | Medium |
| 14 | 中文标题数据源 | 中文搜索 | 无可靠源 | 中 | 中 | Medium |
| 15 | Season 聚合页（Top 10 franchise） | {anime} season 2 | franchise 内导航 | 中 | 中 | Medium |
| 16 | Search SSR 化 | site search | client-side | 中 | 低 | Medium |
| 17 | 2013-2017 季番 second page | 长尾补全 | top-50/季 | 中 | 中 | Medium |
| 18 | Movie/OVA second page | 更多剧场版 | top-250 | 中 | 中 | Low |
| 19 | 逐集 detail 页 | {anime} episode 5 | 无 | 高 | 高 | Low |
| 20 | Staff/Director 数据 | {director} anime | 无 | 高 | 高 | Low |

---

## 7. Localization Gap（Step 10）

| 字段 | 覆盖 | 缺口 | 处理 |
|---|---|---|---|
| English | 100% | — | — |
| Japanese | 72.3% | 1000 条无 anilist_id 旧数据 | 无外部来源，保持 NULL |
| Romaji | 72.3% | 同上 | 同上 |
| Chinese | 100%（chinese_title） | 部分为日文原生名 | 需可靠中文源（不机器翻译） |
| Aliases | 72.3% | 同上 | 同上 |

> 结论：Localization 增量空间有限（剩余全部无外部 ID），非下阶段重点。

---

## 8. Anime Catalog Gap（Step 11）

**Continue Anime Expansion? → CONDITIONAL（当前 NO，条件满足后 YES）**

理由：
- 高价值候选已消化（Tier1/2 清零，剩余 131 全 Tier3）
- 3607 实体覆盖 2013-2026 季番 top-50 + Movie/OVA top-250
- 继续抓取回报递减（Tier3 长尾搜索价值低）

条件（满足后可恢复）：
1. 生产部署完成 + GSC 有数据验证现有实体表现
2. 或做 2013-2017 季番 second page（覆盖 ~30-50% 未覆盖年份）
3. 或高价值 Movie/OVA second page

---

## 9. Recommended Next Phase（Step 13）

> **首选方向：B. Anime Search-Intent Expansion — Movie/OVA + Tags Search Surface（利用现有数据建页，不依赖新抓取）**

### 为什么（对比其他方向）
| 方向 | 否决理由 |
|---|---|
| A. Catalog expansion | 高价值已消化；Tier3 长尾 ROI 低 |
| C. Movie/OVA expansion | **并入 B**：742 条 Movie/OVA 实体已存在，缺的是列表页而非数据 |
| D. Localization | 72.3% 已达标，剩余无外部 ID 无法补 |
| E. Discovery/Recommendation | 依赖 GSC 数据（尚未建立） |
| F. TV/Movies 架构 | 为时尚早（Anime 尚未充分变现） |

### B 的具体内容
1. **/movies/ /ova/ 列表页**（利用 358 MOVIE + 384 OVA/SPECIAL 现有实体）——低难度、数据就绪、立即扩 search surface
2. **/tags/ 聚合页**（利用 DB tags 字段）——MAL/Anime-Planet 验证的发现模式
3. **Watch Order 8→18** + **Franchise Hub 18→57**（复用已验证模式）
4. 并行：**Characters/Episodes 数据扩充**（为最高频 cast/episodes 意图提供基础）

**前置**：生产部署（Phase 35-37）必须先由人工完成，否则所有本地新增页面无法生效。

---

## 10. 交付物清单

1. `phase38_production_sync_runbook.md`（部署指引）
2. `phase38_search_surface_inventory.md`（Step 6）
3. `phase38_competitor_benchmark.md`（Step 7）
4. 本报告（Step 14：Production/GSC/Surface/Benchmark/Gap/Top20/Recommendation）

## 11. 等待人工决定

- 是否执行生产部署（43.133.211.250）
- 是否批准下一步 B（Movie/OVA + Tags Search Surface）
- GSC 域名验证 + sitemap 提交
