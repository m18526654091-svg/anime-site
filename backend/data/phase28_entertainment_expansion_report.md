# AnimeHub Phase 28 — Entertainment SEO Expansion Report

> 生成于 2026-08-29

## 新增页面类型 / URL

| 新增 | 数量 | 说明 |
|---|---|---|
| `/anime/{slug}/episodes/` | **动态路由**（119 部有真实 episode 数据；全部 anime 可访问，无数据显示 not available）| Episode list 页（SSR + canonical + JSON-LD Breadcrumb/ItemList）|

**URL 数量变化**：sitemap 未增加（episodes 页靠 detail 内链发现，避免无数据页入 sitemap）；本地路由 +1 类。

## SEO 关键词覆盖（新增）

| Query | 承载 |
|---|---|
| {anime} episode list / how many episodes | ✅ /anime/{slug}/episodes/ |
| {anime} episodes | ✅ 同上 |

（cast/characters/watch order/release date 已由现有 detail/character/voice-actor/watch-order 覆盖）

## 未新增（数据/意图决策）

| 类型 | 原因 |
|---|---|
| /tv/{slug} | DB 无真人 TV 剧集数据（空页风险）|
| /movie/{slug} | 74 部 anime 电影已有 /anime/ 页（重复 intent）|
| /where-to-watch/ | 无合法平台数据源（禁止编造）|
| Season 作品页 | 可派生但需 GSC 数据证明独立 intent（P2）|

## 代码变更

| 文件 | 修改 |
|---|---|
| `frontend/app/anime/[slug]/episodes/page.tsx` | **新增**：episodes 页（episode list + count + no-data 诚实显示 + JSON-LD + canonical + 内链）|
| `frontend/components/AnimeDetailClient.tsx` | Anime Information 的 Episodes 值加链接 → episodes 页（内链闭环）|

## 数据缺口

- Episode duration / air date 精确值：无字段（Air date 用 year/month 派生，无精确日）
- 占位 video_url **未展示**（无泄漏，杜绝盗版/占位内容）
- 真人 TV / where-to-watch：无数据

## 下一阶段建议

1. 生产部署 + GSC 验证（仍为最高优先）
2. episodes 页对 119 部确认 indexed 后，评估扩展（Season 作品页）
3. cast 网络增强（/character/ /voice-actor/ 英文 + 互链）

## Verification
- `npm run typecheck` ✅ · `npm run build` ✅
- SSR：episodes 页（有/无数据）200 + title/canonical/JSON-LD；detail Episodes 链接 ✓
- sitemap 未变 · 现有 URL 未变 · canonical 未变
