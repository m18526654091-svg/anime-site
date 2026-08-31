# AnimeHub Phase 34 — Entity Gap Audit（Top 30 热门动漫）

> 日期：2026-08-30 · 审计：Top 30 实体 × 10 搜索意图覆盖（基于 DB 数据实测）

## 1. Top 30 实体数据全景（DB 实测）

| 实体 | DB 条目 | 季节条目 | 角色数据 | 集数数据 | Franchise 页 | Watch Order |
|---|---|---|---|---|---|---|
| Attack on Titan | 8 | 7 | ✅(2) | — | ✅ | ✅ |
| Jujutsu Kaisen | 8 | 2 | — | — | ✅ | — |
| Demon Slayer | 9 | — | ✅(6) | — | — | — |
| One Piece | 8 | — | — | — | ✅ | ✅ |
| Naruto | 5 | — | — | — | — | ✅ |
| Bleach | 9 | — | ✅(6) | — | ✅ | ✅ |
| My Hero Academia | 10 | 6 | — | — | ✅ | — |
| Frieren | 7 | 2 | — | — | ✅ | — |
| Re:Zero | 9 | 5 | — | — | ✅ | — |
| Fate | 11 | — | — | — | ✅ | — |
| Chainsaw Man | 3 | — | ✅(5) | — | — | — |
| Solo Leveling | 4 | 1 | — | — | — | — |
| Monster | 7 | 1 | — | — | — | — |
| Spy x Family | 4 | 2 | — | — | ✅ | — |
| Vinland Saga | 2 | 1 | — | — | — | — |
| Overlord | 5 | — | — | ✅(8) | ✅ | — |
| One-Punch Man | 3 | 2 | — | — | ✅ | — |
| Mushoku Tensei | 4 | 2 | — | — | ✅ | — |
| Haikyuu | 5 | 2 | — | — | ✅ | — |
| Gintama | 10 | 4 | — | — | ✅ | — |
| Steins;Gate | 3 | — | ✅(6) | — | — | — |
| Cowboy Bebop | 1 | — | ✅(6) | — | — | — |
| Death Note | 3 | — | — | — | — | — |
| Code Geass | 8 | — | ✅(6) | — | — | ✅ |
| Fullmetal Alchemist | 2 | — | ✅(6) | — | — | — |
| Hunter x Hunter | 1 | — | ✅(6) | — | — | — |
| Gurren Lagann | 1 | — | — | — | — | — |
| No Game No Life | 1 | — | — | — | — | — |
| Made in Abyss | 6 | — | — | — | — | — |
| 86 Eighty-Six | 2 | — | — | — | — | — |

## 2. 搜索意图覆盖矩阵

| 意图 | 覆盖方式 | 覆盖率 |
|---|---|---|
| 1. {anime} anime | detail 页（title 含 "Anime" 词） | ✅ 30/30 |
| 2. {anime} episodes | /episodes/ 页（DB 有集数的） | ⚠️ 仅 Overlord 等 119 部有集数据 |
| 3. {anime} seasons | detail "Seasons & Related Entries"（本阶段新增）+ franchise 页 | ✅ 14/30（franchise 匹配） |
| 4. {anime} season 1/2 | Season N 独立 detail 页 + 新增区块互链 | ✅ 有季节条目的（AoT7/MHA6/ReZero5 等） |
| 5. {anime} watch order | /watch-order/（8 franchise） | ⚠️ 8/30 |
| 6. {anime} characters | detail Characters 区块 | ⚠️ 有角色数据的（11/30） |
| 7. {anime} voice actors | detail 声优内链 + /voice-actor/ | ⚠️ 随角色数据 |
| 8. {anime} studio | detail Anime Information Studio 行 + /studio/ | ✅ 30/30（有 studio 的） |
| 9. {anime} release date | detail Anime Information Release period | ✅ 30/30 |
| 10. anime like {anime} | /similar/ 页 | ✅ 30/30 |

## 3. 缺口分类

| 类别 | 缺口 | 处理 |
|---|---|---|
| **结构已闭合**（本次实施） | seasons 导航 | detail 页新增 "Seasons & Related Entries" 区块（Season/Movie/OVA/Related 兄弟条目互链） |
| 数据缺口（不伪造） | episodes/characters/voice actors 覆盖 | DB 仅 119 部有集数、部分有角色——维持"无数据不显示"原则 |
| 意图不成立 | watch order（22/30 无） | 仅 8 个 franchise 有真实顺序数据，其余不建 |
| 单一作品 | Monster/Cowboy Bebop 等 | 无季无衍生，detail 独立承载（franchise 页不成立） |

## 4. 结论

- 10 类意图中 4 类（anime/seasons/season N/studio/release/similar）已全覆盖
- 本阶段核心修复：**season 意图的页面内导航**（新增 Seasons & Related Entries）
- 其余缺口为数据覆盖限制（episodes/characters/voice actors），按"无数据不显示"原则处理，不伪造
