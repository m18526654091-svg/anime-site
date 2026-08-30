# AnimeHub Phase 20 — Index Coverage & Content Differentiation Audit

> 生成于 2026-08-29

## Step 1 — Index Coverage Audit

| 类型 | URL | Index 价值 | 内容独特性 | 内链 | 薄内容风险 |
|---|---|---|---|---|---|
| detail | 1489 | 核心（episodes/release/similar intent） | 每部唯一（标题/信息/描述/相关） | 8 类内链 | 无（HTML 38-56KB） |
| similar | 690 | 高（anime like X 长尾） | 每页针对源 anime，推荐项+理由徽章 | detail 双向 | 低（内容由数据驱动） |
| watch-order | 9 | 高（高意图顺序搜索） | 每 franchise 唯一步骤+条目 | detail 链接 | 无 |
| best-anime | 20 | 高（best {genre} 长尾） | 每类唯一 intro + 选择逻辑 + reason | Keep Discovering + detail | 无 |
| series | 1 | 中高（franchise 目录） | Fate 唯一 timeline 分组 | watch-order/best/detail | 无 |
| hub | ~53 | 中（枢纽） | 各入口页 | 全站导航 | 无 |

**结论**：无删除必要，无薄内容页（全部数据充实）。

## Step 2 — Content Differentiation Audit

| 页面 | 搜索意图 | 独特性 | 判定 |
|---|---|---|---|
| best-anime/psychological | 心理惊悚推荐 | intro 区分心理 vs 侦探 | ✅ 唯一 |
| best-anime/mystery | 侦探/案件推荐 | intro 明确侦探/推理 | ✅ 与 psychological 区分 |
| best-anime/school | 校园设定 | intro 聚焦校园 vs romance 恋爱主题 | ✅ |
| best-anime/adventure | 冒险旅程 | intro 聚焦旅程 vs action/fantasy | ✅ |
| similar 页 | "anime like X" | 每页针对特定 X，推荐+理由 | ✅ 非模板重复 |
| watch-order 各页 | "X watch order" | 每 franchise 唯一步骤 | ✅ |
| underrated | 隐藏佳作 | 独特选择逻辑（高分低曝光） | ✅ |

**结论**：所有 programmatic 页面回答唯一搜索意图，无 "Best anime list" 类泛泛重复页。**无需修改**。

## 通用结论
- 无薄内容、无重复 intent、无孤立页
- Index 价值排序：detail > similar > watch-order > best-anime > series > hub
