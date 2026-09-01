# AnimeHub Phase 43 — SERP Observation

> 状态：**Google US SERP = 不可用**（延续 Phase 40-B 实测：Google 429 防护、DDG captcha、Bing 非 US geo）
> 本文件如实记录：本阶段**没有**可验证的真实 SERP 观察。

## 1. 目标查询（研究种子 — 来自 Phase 40-B/41 的意图框架）

以下为研究种子，**非已验证关键词**：

```
best isekai anime
best romance anime
best psychological anime
anime like Attack on Titan
anime like Death Note
anime watch order
summer 2026 anime
best mecha anime
```

## 2. 观察记录

| 查询 | Observed 排名页 | 页面类型 | 标题 | PAA | Related | 判定 |
|---|---|---|---|---|---|---|
| 全部 | **无** | — | — | — | — | ❌ 无可靠访问 |

## 3. 为什么不做替代

- **Bing EN（非 US geo）**：Phase 40-B 曾抓取但明确标注"Bing EN with limitation"，不是 Google US SERP
- **DDG**：captcha 封锁
- **Google**：429 防护

按任务要求，**不可靠访问时不伪装**。本阶段 0 条 Observed SERP。

## 4. 页面类型分析框架（保留待用）

真实 SERP 可用后，按以下分类记录（Phase 40-B 框架）：
official / database / wiki / guide / editorial / listicle / streaming / news / forum-reddit / video / other

预期（Inferred，非 Observed）：
- "best X anime" SERP 以 database（MyAnimeList/AniList）+ listicle + Reddit 为主
- "anime like X" SERP 以 database + Reddit/forum + 专门相似站点为主
- "watch order" SERP 以 wiki + 专门 guide 为主

## 5. PAA 分析

无真实 Google PAA。不编造问题原文。

## 6. 内容缺口（Inferred，来自本地实测）

| 潜在缺口 | 证据强度 | 说明 |
|---|---|---|
| similar 690 页内容实体特定性 | Inferred（弱） | 本地结构已知，内容质量未审计 |
| franchise watch-order 10 个缺失 | Inferred（结构证据） | 18 hub vs 8 watch-order 不一致 |
| upcoming-anime 薄页 | **Observed（本地数据）** | 仅 4 部"未上映"记录 |
| best-anime category 静态 17 个 | Inferred | 无证据表明缺哪些 category |

## 7. AnimeHub 机会（Candidate）

无真实 SERP/GSC 前，**无已验证机会**。所有机会均标注 Candidate，等待：
1. 真实 GSC US 数据（曝光/点击/位置，按 query）
2. 可用的 Google US SERP 访问（SERP 页面类型 + PAA）

## 8. 信息边界

本阶段**未**产生/声称：
- 任何搜索量
- 任何 Google SERP 排名
- 任何 PAA 原文
- 任何 CTR 数据
- 任何"用户已在搜索 X"的 Observed 断言

仅交付：本地资产盘点（Observed）+ 结构推断（Inferred）+ 机会排序（Candidate）。
