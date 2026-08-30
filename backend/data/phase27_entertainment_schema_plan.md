# AnimeHub Phase 27 — Entertainment Schema Plan

> 生成于 2026-08-29 · 未来扩展设计（不迁移数据库）

## 目标
未来支持 TV Series / Movie / OVA / Special 内容类型，**当前不迁移 DB**。

## 设计：content_type 派生

**原则**：不新增 DB 字段（任务禁止），由现有字段派生 content_type：

| content_type | 判定规则（现有字段）|
|---|---|
| `anime_tv` | episodes > 1 或 status ∈ {完结, 连载} 且非电影标记 |
| `movie` | title 含 movie/film/剧场版/劇場版 标记 或 episodes == 1 |
| `ova` | title 含 ova/special/短篇 标记 |
| `unknown` | 无法判定（保持 Unknown guard）|

## 应用场景

1. **detail 页 Type 字段**：Anime Information 的 "Type" 用派生结果（当前实现基于 episodes：TV Series/Movie/Unknown）
2. **JSON-LD schemaType**：`/anime/[slug]/page.tsx` 已按 `episodes > 1 → TVSeries else Movie` 派生——扩展为含 OVA/Special 判定
3. **franchise 页分组**：TV/Movie/OVA 分组展示（现有 anime-series 页已按 timeline 分组，可扩展）

## 兼容性
- 全部基于现有字段派生，**DB schema 零变更**
- 现有 URL 与 canonical 不变
- SSR/JSON-LD 兼容

## 实施时机
- 待生产部署 + GSC 数据验证后评估（P2）
- 若需真实 content_type 数据 → 单独数据任务（不改 schema）
