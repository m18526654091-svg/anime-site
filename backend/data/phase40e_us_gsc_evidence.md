# AnimeHub Phase 40-E — US GSC Evidence（状态报告）

> 日期：2026-09-01 · 状态：**无真实 GSC 数据 → 分析 STOP（insufficient evidence）**

## 1. Dataset Scope

```
Input file:        未提供（仓库中无真实 GSC US 导出）
Input rows:        N/A
Detected columns:  N/A
Date range:        N/A
Country scope:     无法验证
Search type:       N/A
US scope = UNKNOWN
```

仓库中唯一 CSV 为 `gsc_us_export_template.csv`（**示例值 128/5，明确非真实**，本阶段排除）。

按 Phase 40-E Step 3：

> "If US scope cannot be verified: STOP. Do not analyze it as US data."

## 2. Data Quality

未执行（无输入数据）。分析器 `backend/scripts/analyze_gsc_us.py` 已就绪（13 个专项测试通过），真实文件到位后自动输出 valid/invalid/duplicate/malformed 统计。

## 3–10. 分析章节（US 赢家 / 高曝光机会 / 零点击 / 170-1 调查 / 映射 / 冲突 / 意图聚类）

**全部 PENDING**——无 Observed 数据则任何输出都是伪造。

## 11. 170 Impressions / 1 Click 调查

用户此前观测约 US 170 曝光 / 1 点击。**当前无数据集可验证**：

- 无法确认是单 query 还是多 query
- 无法确认是否已过期（date range 未知）
- 无法复现

> 结论：需真实 CSV 后由分析器定位产生 170/1 的 query/page 行。

## 12. SERP Research Queue

**空**。无 GSC 证据 → 无法选出 5-10 个研究目标。

> 规则（Step 28）："If insufficient data exists: STOP — insufficient evidence. Do NOT force 5–10 queries."

## 13. Limitations

- 缺真实 GSC 导出（Query+Page+US+28 天）
- 样本无（而非"小样本"）
- Google US SERP 当前工具不可用（Google 429 / DDG 验证码 / Bing 解析差 / 无 US geo）
- 任何本阶段结论均不可作 Observed

## 14. Safety

```
No production database changes.
No SEO changes.
No keyword insertion.
No URL changes.
No production deployment.
No fabricated metrics.
```

## 15. 解锁条件（用户提供真实文件后）

1. 放置 `backend/data/gsc_us_export_<date>.csv`（GSC → Performance → US + Query+Page + Web + Last 28 days → 导出）
2. `python scripts/analyze_gsc_us.py --input <real.csv> --out backend/data/phase40e_gsc/`
3. 分析器产出：数据质量 / 170-1 定位 / 赢家 / 高曝光机会 / 零点击 / 意图聚类 / 冲突 / 5-10 研究队列
4. 队列交接到 Google US SERP 阶段（需 US geo 环境）
