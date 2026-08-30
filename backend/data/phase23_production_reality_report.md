# AnimeHub Phase 23 — Production Reality Check

> 生成于 2026-08-29 · 公网实测 + 本地 git 对比

## 1. 当前生产状态

| 项 | 值 |
|---|---|
| sitemap | 3470 loc · **dups=9**（/studio/ 重复，Phase 21 修复未部署） |
| robots.txt | ✅ Allow / + Sitemap 行 |
| canonical | ✅ 自指（历次抽查通过） |
| HTTP status | ✅ 主要页面 200 |
| page types | detail 1489 / similar 690 / watch-order 9 / best 20 / series 1 / studio 110 / characters 480 / hub 671 |
| Phase 10/11/17 内容 | ❌ **未部署**（Anime Information/Genres/Entity Summary = False） |

## 2. 部署状态对比

| 项 | 值 |
|---|---|
| 本地 HEAD | `fd5dca9`（Phase 22） |
| origin/main | `fd5dca9` |
| 生产 deployed commit | 推断为 Phase 9/SEO-Accel（`6c52530` 附近，基于内容特征） |
| **missing commits** | **12 个**：`3ef474b`(P10) → `fd5dca9`(P22) |
| 生产缺内容 | Anime Information / Genres 区块 / Entity Summary / Why 区块 / Last updated / GA4 层 / sitemap dup 修复 / Phase 18 英文化 / Phase 19 title 压缩 |

## 3. 期望生产状态（部署全部 pending commits 后）

- sitemap dups → **0**
- detail 页含完整 Phase 10-19 模块（Anime Information/Genres/About/Who/Why/Entity Summary/Last updated）
- 核心 UI 全英文（Phase 18）
- GA4 可启用（设 NEXT_PUBLIC_GA_ID 后 build）
- Re:Zero 等长标题 ≤68 字符（Phase 19）

## 4. 结论

**生产严重滞后**：本地 12 个 release 未部署。在部署前，GSC/流量数据无法反映本地最终代码。**部署是激活 Google 流量的前置条件**。
