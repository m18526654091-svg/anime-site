# AnimeHub Phase 35 — High-Value Anime Candidates（Step 2）

> 日期：2026-08-30 · 来源：AniList GraphQL（31 请求，1090 条原始候选）· 质量门槛后 485 条已导入

## 1. 候选分层

| Tier | 定义（popularity） | 数量 |
|---|---|---|
| Tier 1 国际知名/长期高搜索 | ≥300,000 | 145 |
| Tier 2 热门续作/新番 | 200,000–300,000 | 125 |
| Tier 3 高分经典/长尾 | <200,000 | 820 |
| **合计** | | **1090** |

## 2. 格式分布

| 格式 | 数量 | 说明 |
|---|---|---|
| TV | 861 | 主搜索价值 |
| MOVIE | 97 | 剧场版 |
| ONA | 89 | 网络动画 |
| TV_SHORT / SPECIAL / OVA / MUSIC | 43 | 门槛过滤 |

## 3. Tier 1 代表（本轮已导入）

Assassination Classroom S2、Hell's Paradise、Demon Slayer: Mugen Train Arc、PSYCHO-PASS、Weathering With You、Hyouka、JoJo Stardust Crusaders、Dr. STONE STONE WARS、Miss Kobayashi's Dragon Maid、SPY x FAMILY Cour 2、Seraph of the End、Wotakoi、The Quintessential Quintuplets、Komi Can't Communicate、Noragami Aragoto、Princess Mononoke、Fire Force S2、Maid-Sama!、MASHLE 等

## 4. 每条记录字段（candidates JSON）

- title{romaji, english, native}（AniList 已验证）
- startDate{year, month, day}、description、genres、tags
- studios、status、episodes、coverImage、averageScore、popularity、format
- id / idMal（外部 ID）

## 5. 导入状态

- **已导入**：485 条（含多语言字段 japanese_title/romaji_title/aliases）
- 保留在 candidates JSON 的：invalid 19 条（格式不合规）不入库；其余 586 条为已存在/重复

## 6. 规则遵守

- 无随机导入（全部 AniList 高人气/高分/热门季番维度）
- 来源 ID 保留（anilist_id + mal_id）
- 无编造（所有字段 AniList 返回，中文标题缺省时用日文原生名或英文，不冒充官方中文名）
