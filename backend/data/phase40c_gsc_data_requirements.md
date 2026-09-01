# AnimeHub Phase 40-C — Real GSC US Data Requirements

> 日期：2026-09-01 · 用途：说明需要哪些真实 GSC 数据、如何导出、格式变体如何容忍

## 1. 首选导出方式（Google Search Console → Performance → Search results）

1. **Country**：`United States`（必须）
2. **Dimensions**：`Query` + `Page`（两列都勾选）
3. **Search type**：`Web`（默认）
4. **Date range**：`Last 28 days`（首选）；可附加 `Previous 28 days` 用于环比
5. **Export**：点击 Export → **CSV**

## 2. 必需逻辑字段

| 字段 | 必须 | 说明 |
|---|---|---|
| Query | ✅ | 原始搜索词（保留原值，不做规范化去重） |
| Page | ✅ | AnimeHub 落地 URL（bunivoa.com 下的路径） |
| Clicks | ✅ | 点击次数 |
| Impressions | ✅ | 展示次数 |
| CTR | ✅ | 点击率（计算值：clicks/impressions，避免平均各行 CTR） |
| Average position | ✅ | 平均排名 |

## 3. 可选但推荐字段

| 字段 | 说明 |
|---|---|
| Country | 用于显式确认 US scope |
| Date | 行级日期（若按日导出） |
| Search type | Web |

## 4. 列名变体容忍（分析器规范化）

实际导出可能是不同命名，分析器按以下映射归一：

| 标准名 | 可接受变体 |
|---|---|
| query | Query / query / keyword / Keyword / search_query |
| page | Page / page / landing_page / URL / url / landing page |
| clicks | Clicks / clicks / click |
| impressions | Impressions / impressions |
| ctr | CTR / ctr / click_through_rate |
| position | Position / position / avg_position / average_position / Average Position |
| country | Country / country / geo |
| date | Date / date / day |

## 5. US Scope 判定（严格）

- **YES**：CSV 含 `Country` 列且全部为 `United States`（或用户显式提供"已按 US 过滤"的说明）
- **NO**：Country 列存在但非 US
- **UNKNOWN**：无 Country 列且无过滤说明

**禁止**：根据 query 语言推断 US scope（英文 query ≠ US 用户）。

## 6. 数据使用边界（不混淆）

- **Observed**：query/page/clicks/impressions/CTR/position/country/date——GSC 直接给出
- **Inferred**：priority / intent / opportunity / cluster / mismatch——由 Observed 计算分类
- **Candidate**：新关键词/标题/页面想法——仅 AI 提议，**不是** Observed 搜索需求

## 7. 明确禁止

- ❌ 声称 impressions = 全美搜索量（GSC impressions 是 AnimeHub 专属曝光）
- ❌ 输出 monthly search volume / market size（无外部数据源时）
- ❌ 中文关键词翻译成英文冒充美国搜索词
- ❌ 无真实数据时生成"机会列表"

## 8. 交付物（有真实数据时）

- `backend/data/phase40c_us_gsc_opportunities.csv`
- `backend/data/phase40c_us_gsc_opportunities.json`
- `backend/data/phase40c_us_gsc_analysis.md`

无真实数据时：分析器仅验证输入并明确报告 `No real GSC data provided`。
