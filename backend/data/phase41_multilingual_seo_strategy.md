# AnimeHub Phase 41 — Multilingual Search-Intent SEO Strategy

> 日期：2026-09-01 · 状态：架构审计完成 + 战略框架（无真实 SERP 证据，未实施任何页面/翻译）

---

## 1. 当前 i18n 架构审计（Step 4）

| 维度 | 现状 | 缺口 |
|---|---|---|
| i18n 库 | 无（package.json 无 next-intl/react-i18next/formatjs） | 需引入或自建 |
| locale 配置 | next.config 无 i18n | — |
| 语言检测 | 无 middleware | 需建立 |
| URL 结构 | 单语言（`/anime/{slug}/` 等，无 `/en/` `/es/` `/ja/`） | 多语言 URL 架构未定 |
| canonical | 单 canonical（`alternates.canonical`） | 多语言时需 per-locale canonical |
| **hreflang** | **无** | 需按实际存在的页面建立互指 |
| sitemap | 单语言（4044+ URL） | 多语言时需 per-locale + hreflang |
| `<html lang>` | **`zh-CN`**（root layout 硬编码） | ⚠️ 与英文内容不匹配，应 `lang="en"` |
| metadata locale | openGraph `en_US` | 有，但仅英文 |
| 翻译文件 | 无 | 需逐语言建立 |

**结论**：当前架构**完全单语言**（英文内容 + 少量中文残留）。支持西/日语需：
1. 先修 `<html lang>` 不一致（最小）
2. 决定 URL 架构（`/es/` `/ja/` 前缀 vs 子域 vs 单域 cookie）——**未决定**，需评估迁移风险
3. 建立 hreflang 互指
4. 引入 locale 内容层

**本阶段不做架构重建**（任务规则：不 redesign 除非必需）。

---

## 2. 一实体多语言原则（不可违反）

```
一个 Anime Entity（DB 单条记录）
    ↓
Attack on Titan
    ↓
en:  Attack on Titan
es:  Attack on Titan（若西语用户已用英文名，保留英文；有西语官方名才用西语）
ja:  進撃の巨人（官方日文原生名）
    ↓
多语言名称 = 实体属性（anime.title / japanese_title / aliases 已有存储）
```

- **不**创建重复 Anime/Character 记录（语言不同 ≠ 实体不同）
- **不**修改 canonical slug（`/anime/attack-on-titan/` 保持）
- 本地化名称仅用于：显示层（locale-aware）+ metadata + hreflang 页面 + 搜索

---

## 3. 各语言命名策略（locale-aware）

| 语言 | Anime 主名 | Character 主名 | 辅助名 |
|---|---|---|---|
| en-US | 英文 title | 英文 name_en | native/romaji |
| es | 西语用户已建立的名称（未验证前保留英文 title） | 英文或已建立西语名 | native |
| ja-JP | 官方日文 title（japanese_title） | 日文 native_name | 英文/romaji |

**显示策略**：Phase 40-A 的 `name_en || name` 模式需扩展为 locale-aware（当前仅英文优先）。西/日语页面启用前需先有对应页面。

---

## 4. 各语言意图族（种子研究 query，全部 Candidate）

> 无真实 SERP/GSC 证据 → 以下仅研究种子，**不**视为已验证关键词。

### 英文（Stage 1，已有页面承载）
| 意图族 | 种子 query（Candidate） | 承载页 |
|---|---|---|
| episodes | "X episodes / how many episodes" | `/anime/{slug}/` |
| characters | "X characters" | detail + `/character/{slug}/` |
| watch order | "X watch order" | `/watch-order/{slug}/` |
| release/season | "X season 2 / release date" | detail + franchise |
| franchise | "X series list" | `/anime-series/{slug}/` |
| voice actors | "X voice actors" | `/voice-actor/{slug}/` |
| similar | "anime like X" | `/similar/` |
| genre | "best {genre} anime" | `/best-anime/` |

### 西班牙语（Stage 2，需独立 SERP 研究）
| 意图族 | 种子 query（Candidate） | 承载（未建） |
|---|---|---|
| episodios | "X episodios / cuántos episodios tiene X" | 待定 |
| personajes | "X personajes" | 待定 |
| orden | "X orden para ver" | 待定 |
| estreno | "X fecha de estreno" | 待定 |
| temporada | "X temporada 2" | 待定 |

### 日语（Stage 3，需独立 SERP 研究）
| 意图族 | 种子 query（Candidate） | 承载（未建） |
|---|---|---|
| 話数 | "X 話数 / 何話" | 待定 |
| キャラクター | "X キャラクター" | 待定 |
| 見る順番 | "X 見る順番" | 待定 |
| 放送 | "X 放送日 / 2期" | 待定 |
| 声優 | "X 声優" | 待定 |

**关键**：不同语言意图优先级不同（en: watch order 热门；es: personajes；ja: 話数/声優）——**不强制对称**。

---

## 5. 西班牙语市场范围（未定，需证据）

- 当前不区分 es-ES / es-MX / es-419（无证据不建区域页）
- 保持单一西语体验，直到出现真实 query/区域差异证据 + hreflang 架构就绪

## 6. 日语命名

- 日语页面主名用官方日文原生名（`japanese_title` 已有数据，72.3% 覆盖）
- 英文/romaji 保留为别名（实体属性）
- 日语用户搜索行为（缩写/kanji/kana/季简写）需独立研究，不套英文模式

---

## 7. 优先级（Stage 1→2→3）

1. **Stage 1 — 英文**：继续 US 意图扩展（已有页面体系）
2. **Stage 2 — 西语**：先修架构（lang/hreflang/URL），再独立 SERP 研究
3. **Stage 3 — 日语**：同上，独立研究

**前置条件**（每一语言开启前）：
- 真实 SERP/GSC 证据（本语言）
- 架构就绪（hreflang/URL/canonical）
- 代表性样本 20-50 部验证（非全量）
- QA：母语级文案（非机器翻译）

---

## 8. 数据诚实性声明

- **无真实 GSC/SERP 证据**（已连续多轮确认）→ 本报告所有种子 query 标注 **Candidate**
- 未使用 Bing/DDG 冒充 Google US/ES/JP SERP
- 未翻译任何中文/英文关键词冒充目标语言关键词
- 未输出搜索量

---

## 9. 不做清单（Absolute Prohibitions 确认）

- ❌ 未创建 `/es/` `/ja/` 页面
- ❌ 未机器翻译任何标题/描述/H1/FAQ
- ❌ 未将英文关键词列表翻译成西/日语
- ❌ 未新建 URL / 未改 canonical / 未改 slug
- ❌ 未插入关键词到 DB
- ❌ 未按"英文模板 × 翻译"批量生成
- ❌ 未改 `<html lang>`（记录为待修最小项，需实施阶段处理）

---

## 10. 下一步（建议顺序）

1. **最小架构修复**（实施阶段）：`<html lang="zh-CN">` → `lang="en"`（当前英文站）
2. **英文 Stage 1**：继续基于真实 US GSC/SERP（阻塞于真实数据）
3. **多语言 URL 架构决策**：评估 `/es/` `/ja/` 前缀（含 hreflang/迁移风险）——需独立决策，非本阶段
4. **西/日语独立 SERP 研究**：需对应语言真实 Google SERP 环境（当前工具不可用）
