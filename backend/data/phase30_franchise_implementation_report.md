# AnimeHub Phase 30 — Franchise Hub SEO Implementation Report

> 日期：2026-08-30 · 范围：/anime-series/{slug}/ Franchise Hub（第一批 18 个高价值 franchise）· 状态：✅ 完成

## 1. 新增 URL 数量

| 项目 | 数值 |
|---|---|
| 新增 franchise 页面（/anime-series/{slug}/） | **17 个新增**（fate 为 Phase 9 已有，统一纳入 18） |
| 本次总 franchise 页面 | 18 |
| sitemap 总 URL | 3469 |
| sitemap 重复 URL | **0**（Phase 9 硬编码 fate 条目已移除，避免重复） |

## 2. 页面列表（18 个 franchise）

| slug | franchise | DB entries |
|---|---|---|
| attack-on-titan | Attack on Titan | 9 |
| my-hero-academia | My Hero Academia | 11 |
| rezero | Re:Zero | 10 |
| jujutsu-kaisen | Jujutsu Kaisen | 9 |
| one-punch-man | One-Punch Man | 6 |
| slime | That Time I Got Reincarnated as a Slime | 8 |
| fire-force | Fire Force | 5 |
| gintama | Gintama | 11 |
| haikyuu | Haikyuu | 9 |
| golden-kamuy | Golden Kamuy | 6 |
| monogatari | Monogatari | 20 |
| bleach | Bleach | 13 |
| spy-family | Spy x Family | 5 |
| frieren | Frieren | 8 |
| mushoku-tensei | Mushoku Tensei | 5 |
| overlord | Overlord | 5 |
| one-piece | One Piece | 9 |
| fate | Fate | 12 |

（候选映射详见 `phase30_franchise_candidates.md`；vinland-saga 仅 2 条、kaiji 低优先被排除）

## 3. SEO 覆盖

### 页面结构（每页）
- **H1**：`{Franchise} Franchise`
- **Franchise Overview**：DB 驱动统计（entry 数、发行年份区间、genres，不编造）
- **Anime Entries**：按 TV/Season 与 Movie/Specials 分组，展示 title/year/score/type + detail 链接
- **Watch Order**：franchise 有 watch-order 页时显示 CTA（AoT/Monogatari/Re:Zero/Bleach/One Piece）
- **Related**：每条目 Similar 链接 + 页面内 Watch Order/Best Anime 交叉链接

### Metadata
- **title**：`{Franchise} Franchise - Watch Order, Seasons & Anime List`（实测 56–65 字符，全部 <68 不截断）
- **description**：含 franchise/seasons/watch order/anime entries 关键词，无 keyword stuffing
- **canonical**：`/anime-series/{slug}/`（每页唯一）

### Structured Data（每页 2 个 JSON-LD，均通过解析验证）
- **BreadcrumbList**（Home → Franchise）
- **ItemList**（numberOfItems = 真实条目数，position 完整 1..N）

## 4. 内链闭环（Step 5）

```
Anime detail ──(Explore More: franchise 匹配)──→ /anime-series/{slug}/
Watch Order  ──(Browse the X Franchise CTA)────→ /anime-series/{slug}/
Similar      ──(More from the X Franchise Hub)──→ /anime-series/{slug}/
Franchise    ──(每条目 detail/similar + watch-order CTA)──→ Anime / Watch Order
```

实测（SSR HTML）：
- `/anime/attack-on-titan/` → `/anime-series/attack-on-titan/` ✅
- `/anime/jujutsu-kaisen/` → `/anime-series/jujutsu-kaisen/` ✅
- `/watch-order/monogatari/` → `/anime-series/monogatari/` ✅
- `/anime/attack-on-titan/similar/` → `/anime-series/attack-on-titan/` ✅

## 5. 验证结果

| 检查项 | 结果 |
|---|---|
| `npm run typecheck` | ✅ 通过 |
| `npm run build` | ✅ Compiled successfully |
| 18 franchise 页 SSR status | ✅ 全部 200 |
| 页面内容完整（非"being collected"） | ✅ 18/18 |
| Franchise Overview 渲染 | ✅ 18/18 |
| JSON-LD（BreadcrumbList + ItemList） | ✅ 18/18，解析 valid |
| canonical/title/description | ✅ 全部生成 |
| sitemap franchise URL | ✅ 18 个唯一 |
| sitemap duplicates | ✅ **0** |

## 6. 变更文件

- `frontend/lib/franchise.ts` — FRANCHISE_DEFS 扩至 18 个 franchise（数据库驱动关键词匹配）
- `frontend/app/anime-series/[slug]/page.tsx` — H1/Franchise Overview/Watch Order CTA + metadata 优化
- `frontend/app/watch-order/[slug]/page.tsx` — Franchise CTA（franchise 匹配时）
- `frontend/app/anime/[slug]/similar/page.tsx` — Franchise discovery 区块
- `frontend/app/sitemap.ts` — franchisePages 统一生成（移除 Phase 9 fate 硬编码，修复重复）

## 7. 后续建议

1. 生产部署（pending）：本地验证完成，等待用户在 43.133.211.250 执行 `git fetch && merge --ff-only && docker compose build frontend && up -d`
2. GSC 验证：franchise 页收录 + 关键词表现（franchise watch order / anime list）
3. 下一批 franchise（Phase 29 P2）：数据 ≥3 条的其余集群（Data-driven）
