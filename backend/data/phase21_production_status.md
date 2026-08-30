# AnimeHub Phase 21 — Production Status

> 生成于 2026-08-29 · 公网实测

## 生产状态（2026-08-29）

| 项 | 状态 | 详情 |
|---|---|---|
| backend | 1.7.0 production | /api/version |
| sitemap | 3470 loc · **dups=9（已定位）** | ⚠️ 9 个 /studio/ 页重复 |
| robots | ✅ | Sitemap 行 + Allow / |
| canonical | ✅ | 5 页抽查全自指 |
| Phase 10/11/17 内容 | ❌ 未部署 | monster 无 Anime Information/Genres/Entity Summary |
| docker containers | 无法远程检查 | 需在生产执行 docker compose ps |

## 发现并修复的问题

**生产 sitemap 9 个重复 /studio/ URL**（SUNRISE/J.C.Staff/Bones/Studio Deen/White Fox/Zero-G/david production/KINEMA CITRUS/GONZO 各 x2）。

根因：`sitemap.ts` 的 studio 页生成缺少 URL 去重（后端返回重复 studio 条目时，`<loc>` 重复）。

修复：`frontend/app/sitemap.ts` studio 生成加 `seenStudio` Set 去重（与 anime/similar 一致）。本地验证：mock 返回重复 studio → sitemap dups=0 ✅。

**部署生效条件**：此修复随 Phase 10-21 代码一起部署生产后，sitemap dups 将从 9 → 0。

## 待办
1. 生产部署本地最新代码（Phase 10-21，`3ef474b` → 本次 commit）
2. 部署后重跑本报告验证（sitemap dups=0 + Phase 10/11 内容上线）
