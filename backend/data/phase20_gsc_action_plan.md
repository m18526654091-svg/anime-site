# AnimeHub Phase 20 — GSC Action Plan

> 生成于 2026-08-29 · GSC 接入后周度工作流

## Weekly Workflow

### 1. Export Queries
从 GSC Performance 导出最近 28 天 query 数据（美国 + 全部）。

### 2. Find High Impressions / Low CTR
筛选条件：
- Impressions > 100 且 CTR < 1% → **优化 title/description**
- 处理优先级：Top 100 页面 > franchise 页 > best-anime 列表

### 3. Find Position 5-20 Keywords
- position 5-20 且 impressions > 50 → **内容增强/内链补强**（目标进前 5）
- 逐条记录到 `phase14_gsc_dashboard_template.md` 关键词表

### 4. Improve Pages
按 Action 分类执行：
| Action | 触发 | 做法 |
|---|---|---|
| improve title | CTR<1% + imp>100 | Phase 9/19 模板规则（Anime/Watch Order/Episodes 词） |
| improve content | position 5-20 | 增强 Anime Information/About/Why 模块 |
| add internal link | 页面低权重 | 从相关 detail/best/watch-order 加内链 |
| create new page | 独立 intent | Phase 8 Existing vs New 流程（≤300/阶段，freeze 期暂缓） |

## 周报输出
- `phase13_gsc_monitoring_plan.md` Step 1 模板（indexed/clicks/impressions/CTR/position）
- 每次只改明确问题页面，不做全量强行修改

## 里程碑（GSC 数据出现后）
- indexed/submitted 比 ≥ 90%
- Top 100 detail CTR ≥ 2%
- position 5-20 关键词持续进前 5
