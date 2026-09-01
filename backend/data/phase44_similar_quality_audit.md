# AnimeHub Phase 44 — Similar Anime Page Quality & Scaling Decision

> 日期：2026-09-01 · 只读审计（零修改）· 样本：10 个现有 indexable Similar 页
> 证据口径：本地 SSR + API + DB 实测（Observed）；推断分类（Inferred）；无真实 GSC/SERP

## 1. 样本选择（Step 3）

**选择标准（先声明后评估）**：现有 indexable similar 页（anime_seo_priority≥60 且 slug 非数字）；刻意覆盖 高/中优先级、流行/小众、老作/新作、franchise/standalone/movie、不同 genre、不同推荐结构。非 cherry-pick（含 medium 与 franchise-heavy）。

| anime_id | title | slug | page_url | priority | 推荐数 |
|---|---|---|---|---|---|
| 1002 | 進撃の巨人 | attack-on-titan | /anime/attack-on-titan/similar/ | 81 | 24 available |
| 1028 | Steins;Gate | steins-gate | /anime/steins-gate/similar/ | 82 | 24 |
| 555 | 怪兽8号 | kaiju-no-8 | /anime/kaiju-no-8/similar/ | 71 | 24 |
| 214 | 银魂第二季 | gintama-season-2 | /anime/gintama-season-2/similar/ | 100 | 24 |
| 1004 | 呪術廻戦 | jujutsu-kaisen | /anime/jujutsu-kaisen/similar/ | 81 | 24 |
| 1020 | Chainsaw Man | chainsaw-man | /anime/chainsaw-man/similar/ | 93 | 24 |
| 1049 | 葬送のフリーレン | frieren-beyond-journey-s-end-2 | /anime/frieren-beyond-journey-s-end-2/similar/ | 100 | 24 |
| 1034 | Violet Evergarden | violet-evergarden | /anime/violet-evergarden/similar/ | 81 | 24 |
| 700 | 怪物 | monster | /anime/monster/similar/ | 100 | 24 |
| 830 | 间谍过家家剧场版 | spy-x-family-code-white | /anime/spy-x-family-code-white/similar/ | 69 | 24 |

多样性覆盖：franchise（AoT/JJK/Gintama/Frieren）、standalone（Steins;Gate）、movie（Spy Family）、old 2004（Monster）、recent 2023-24（Frieren/Kaiju）、high 100（Monster/Gintama/Frieren）与 medium 69（Spy Family）、genre 跨 动作/科幻/喜剧/心理/奇幻/日常/恐怖/超自然。

## 2. 推荐质量（Step 4-6）

**算法**（Observed，`backend/app/api/anime.py` `similar_anime`）：
```
raw = genre_jaccard*45 + tag_jaccard*25 + score_sim*18 + year_sim*12   (raw<15 过滤)
排序 = raw + anime_seo_priority*0.1；排除自身；quality<70 排除
```

**分类公式**（诊断工具，非排序公式）：
- strong：raw≥45 且 共享 genre≥2
- reasonable：raw≥30 且 共享 genre≥1
- weak：raw≥20
- irrelevant：raw<20

**80 个推荐结果**（10 页 × 前 8）：

| 分类 | 数量 | 占比 |
|---|---|---|
| strong | 66 | 82.5% |
| reasonable | 14 | 17.5% |
| weak | 0 | 0% |
| irrelevant | 0 | 0% |

**每页明细**：AoT 8/8 strong · Steins;Gate 8/8 · Kaiju 3S+5R · Gintama 8R · JJK 8/8 · Chainsaw 8/8 · Frieren 8/8 · Violet 8/8 · Monster 7S+1R · Spy 8/8

**客观证据**：全部 80 个推荐均有共享 genre（≥1）+ similarity_score 支撑；理由文本由共享 genre 的英文描述生成。

### 失败模式（Step 6，记录不修复）

1. **Franchise 自推荐偏置**（Observed）：同 franchise 条目占据大量推荐位
   - AoT：8/8 为进击的巨人系列；Chainsaw：5/8 为呪術廻戦系列；Frieren：4/8 为無職転生系列；JJK：4/8 同系；Violet：3/8 同系；Monster：2/8；Kaiju：2/8；Spy：1/8；Steins：1/8；Gintama：0/8
   - 对"what to watch next"意图，同 franchise 条目有信息冗余（用户更可能想看相似但不同的作品）
2. **Studio 聚集**（Observed）：Monster 7/8 为 MADHOUSE（未含 studio 权重，是 genre/tags 趋同的副作用）
3. **无自推荐**（Observed，API 排除自身）✅
4. **无重复条目/无随机垃圾**（Observed）✅
5. **理由文本在 cluster 内重复**：Monster 页 reason 仅 2 个变体（同一 genre 组合）

## 3. 推荐集合重叠（Step 8）

10 页 top-8 集合 pairwise Jaccard：

- 44/45 对 = **0.00**（零重叠）
- 唯一例外：jujutsu-kaisen vs chainsaw-man = **0.45**（5/11 重合，同为 dark action/supernatural——合理语义接近）
- **无任何推荐 id 出现在 ≥3 个样本页**

结论（Observed）：推荐图**高度差异**——"不同 source anime → 基本不同推荐"，不存在"大量页面共享同一批热门推荐"的模板化问题。

## 4. 实体特定性（Step 7）

| 维度 | 判定 | 证据 |
|---|---|---|
| 推荐集合 | High | jaccard≈0 |
| 排序 | High | similarity_score 逐实体不同 |
| 推荐理由 | High | 基于该实体共享 genre |
| 页内数据（score/year/genre 徽章） | High | 卡片级实体数据 |
| title/H1 | High | "Anime Like {Entity}" |

**实体特定性：A**（推荐内容层完全实体驱动）


## 5. 模板复制（Step 9）

| 元素 | 判定 |
|---|---|
| title | "Anime Like {English Title}" — 自然、实体特定 ✅ |
| H1 | 同 title 实体特定 ✅ |
| meta description | **模板 + 中文 genre 残留**：`...from 悬疑/心理 hits`（Observed）⚠️ |
| lede 段落 | **95% 模板** + 中文 genre：`...from 动作 and 剧情 and 奇幻 to...`（Observed）⚠️ |
| 推荐卡片 | 实体特定（cover/title/score/year/genre 徽章/reason）✅ |
| JSON-LD | BreadcrumbList + ItemList（实体列表）✅ |

**模板差异化：B-**——页面主体由实体卡片承载，但顶部 desc/lede 模板化且**包含中文 genre 残留**（英文页面中显眼缺陷）。

## 6. 内容有用性测试（Step 10）

用户"刚看完 X"→ 本页能否帮助决定"接下来看什么"？

- **发现** ✅ H1 "Anime Like Monster" 立即说明用途
- **推荐有用性** ✅ 82.5% strong；同为心理悬疑经典
- **信息质量** ✅ 卡片含 score/year/genre 徽章 + 英文 reason
- **导航** ✅ 9 个内链直达推荐 detail 页
- **决策支持** ✅ reason 提供"为什么相似"依据（同 genre 时够用）

结论：**满足决策支持**，无需长文。卡片 + reason 足够。

## 7. 可解释性（Step 11）

- 每个推荐都有 `reason`（共享 genre 英文描述）+ similarity_score
- 算法输入（genre/tags/score/year）全部可见可查
- **Explainable**（Observed：reason 基于真实共享 genre，非编造）

## 8. 技术 SEO（Step 12，SSR 实测）

10/10 全部通过：

| 检查项 | 结果 |
|---|---|
| HTTP 状态 | 200/200 |
| canonical | 自指 `/anime/{slug}/similar/` ✅ |
| title/H1 | 存在且实体特定 ✅ |
| meta description | 存在（含中文 genre 缺陷，见 §5） |
| OpenGraph | 存在 ✅ |
| JSON-LD | BreadcrumbList + ItemList（10 ListItems）✅ |
| robots | `index, follow`（无意外 noindex）✅ |
| 内链 | 9 个 anime 链接（8 推荐 + 1 源实体）✅ |
| 重复 H1 | 无 ✅ |
| 渲染失败 | 无 ✅ |

**技术 SEO：A**


## 9. 局限（Step 25 证据口径）

- **无真实 GSC 数据**：无 impressions/clicks/CTR/排名——未虚构
- **Google US SERP 不可用**（Google 429 防护）：无 SERP 结论；未用 Bing/DDG 冒充
- **无搜索量声称**
- 推荐质量分类基于**系统内部客观证据**（shared genres/tags/score/era + 算法输出），非个人偏好；样本 80 推荐中 0 条 weak/irrelevant，但 franchise/studio 偏置为**推断出的体验风险**（Inferred），非硬失败

## 10. 最终判定

四维评分：

| 维度 | 等级 |
|---|---|
| A. 推荐质量 | **B+**（82.5% strong，0 无关；存在 franchise/studio 聚集） |
| B. 实体特定性 | **A**（推荐图零重叠） |
| C. 模板差异化 | **B-**（desc/lede 模板化 + 中文 genre 残留） |
| D. 技术 SEO | **A**（10/10） |

按 §17 规则：推荐质量是 gate 因素——**非 D**（无无关推荐、无模板垃圾），但模板存在明确缺陷（Observed 中文残留）且 franchise 偏置影响意图匹配。

# 判定：**CONDITIONAL**

Similar 页类型有真实价值（推荐准确、实体特定、技术达标），但扩展前必须修复：
1. **desc/lede 中文 genre → 英文映射**（Observed 缺陷，高优先级）
2. **同 franchise 推荐占位控制**（展示层建议：同 franchise 最多 1-2 个，其余给跨 franchise 相似作品）
3. lede 增加实体特定信息（如 episode count/score/studio）减少模板感

## 11. 下一步行动（唯一）

# **Improve Similar template**

（修复后重新评估，再考虑 50-100 部受控 pilot）

## 12. Expansion Gate（§18，pilot 前置条件）

从样本推导的门槛：
1. **推荐质量**：0 irrelevant；≥5/8 为 strong 或 reasonable（全样本达标）
2. **推荐数**：≥5 个推荐（样本全部 24 available，页面展示 8）
3. **无自推荐/无重复条目**（已验证 API 保障）
4. **推荐重叠**：跨页 Jaccard ≤ 0.3（实测 ≈0）
5. **同 franchise 占位** ≤2（修复项）
6. **模板修复**：desc/lede 英文 genre（修复项）
7. **技术 SEO**：必检项通过（已验证）

## 13. Pilot 提案（§19，未来阶段）

修复模板后，选 **50-100 部**：
- anime_seo_priority 40+（候选池足够：raw≥15 的推荐 ≥5 个）
- 覆盖 franchise/standalone/movie/old/recent
- 排除推荐数 <5 的尾部
- 测量指标：页面生成成功率、推荐数、技术错误、索引状态（pilot 后 4-8 周再评估 GSC 表现）

## 14. 多语言（§23）

本阶段英文优先。西/日语 Similar 页需各自独立 SERP 研究（不得翻译本阶段英文模板）。

## 15. Evidence 标签汇总

| 结论 | 分类 |
|---|---|
| 算法公式/样本数据/重叠度/技术 SEO/中文残留 | **Observed**（本地实测） |
| 推荐质量"高"、franchise/studio 偏置影响意图 | **Inferred**（从采样数据推断） |
| "anime like X" 是有效 US 搜索意图 | **Candidate**（无 GSC/SERP 验证） |
| 搜索量/CTR/排名 | 无 |

