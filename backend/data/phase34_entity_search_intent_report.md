# AnimeHub Phase 34 — Entity Search Intent Report

> 日期：2026-08-30 · 目标：Top 30 实体 Topic Cluster（不大量新增页面）· 状态：✅ 完成

## 1. 实施变更（1 文件 + 报告）

| Step | 变更 | 文件 |
|---|---|---|
| 3. Detail "Seasons & Related Entries" | 匹配 franchise 时 SSR 拉取同系列兄弟条目（Season/Movie/OVA/Related），按 year 排序展示卡片 + Franchise 入口链接 | `frontend/app/anime/[slug]/page.tsx`（server fetch）+ `frontend/components/AnimeDetailClient.tsx`（渲染） |

## 2. Step 2 — Season Intent 评估结论

**不批量创建 season 页面。** 理由：
- DB 中 "Season N" 是独立 detail 条目（已存在 SEO URL，sitemap 已含）
- 季与季关系已由 franchise 页（18 集群）+ 本阶段新增的 detail 内兄弟互链承载
- 新建聚合季页会与 franchise/detail 重复意图

**Season 导航增强路径**（本次实施）：
```
detail（Season 1）
  → Seasons & Related Entries 区块（Season 2 / Season 3 / Movie / OVA 卡片）
  → franchise hub（全系列目录）
  → watch-order（顺序指引，若存在）
```

## 3. Step 4 — Release Timeline 评估结论

- 完整 air date 字段不存在（anime 表仅 year + month，month 部分缺失）
- 采用 **轻量时间线**：Seasons & Related Entries 区块按 year 升序排序，卡片显示 year——满足"按时间展示系列演进"且只用已有字段
- 不单独建 Release Timeline 区块（与 Seasons 区块内容重叠，避免冗余）；month 完整后才升级为季粒度时间线

## 4. Step 5 — Internal Link 路径

```
Detail ──Seasons & Related Entries──→ 兄弟 Season/Movie/OVA detail
  ├──→ Franchise Hub（区块入口 + Explore More）
  ├──→ Episodes（Anime Information）
  ├──→ Characters（有数据时）
  └──→ Similar / Related Anime
Franchise ──→ 每条目 detail + similar + watch-order CTA
```

实测（AoT detail）：Seasons 区块 8 卡（Season 2/Season 3×2/OVA×2/Related×3）+ Franchise 链接。无重复链接（兄弟条目互链唯一）。

## 5. Step 6 — SEO 验证

| 检查项 | 结果 |
|---|---|
| `npm run typecheck` | ✅ |
| `npm run build` | ✅ Compiled successfully |
| SSR 6 页（AoT/Bleach/JJK/ReZero/SpyFamily/Monster） | ✅ 全部 200 |
| canonical / JSON-LD | ✅ 全部存在（未改动，无回归） |
| Seasons & Related Entries 区块 | ✅ 渲染（franchise 匹配时） |
| sitemap | ✅ 正常（URL 无变更，dups 保持 0） |
| 无 URL 修改 / 无 schema 迁移 / 无 AI 剧情 | ✅ |

## 6. 关键规则遵守

- ❌ 未批量建 season 页（数据/意图不足时通过 detail+franchise 增强导航）
- ❌ 无空区块（仅 franchise 匹配且 >1 条目时渲染）
- ❌ 无 DB schema 迁移（复用 franchise 关键词匹配现有条目）
- ❌ 无 AI 生成内容（Season/Movie/OVA 标签基于 title 正则，year 来自 DB）
- ✅ 全部数据数据库驱动

## 7. 后续建议

1. 生产部署（Phase 30-34 合并）
2. 数据任务：扩展 episodes/characters 覆盖（Top 30 中 19 部缺角色数据）→ detail 区块自动补齐
3. GSC 观察：seasons 意图页的点击提升（新增兄弟互链后）
