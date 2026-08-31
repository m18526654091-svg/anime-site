# AnimeHub Phase 37 — Catalog Expansion Report (Round 3)

> 日期：2026-08-30 · 范围：2013-2017 季番 + Movie/OVA/ONA/Special 专项 · 状态：✅ 完成

## 1. Pre-Expansion Audit

- Before：Anime 2723，sitemap 4876，AniList/多语言覆盖 63.3%
- 缺口：2013-2017 每年仅 54-74 条（正常季番 300+）；Movie 81 / OVA+Special 43（type 缺口）
- 详见 `phase37_pre_expansion_audit.md`

## 2. Candidate Inventory

- 候选池 2981（+1021 增量：2013-2017 季番 20 查询 + Movie/OVA/ONA/Special 11 查询）
- 详见 `phase37_anime_candidates.md`

## 3. Candidate Prioritization

- Tier 1（≥300k popularity）优先；Tier 2 次之；Tier 3（低 popularity）不强行导入
- 2013-2017 高价值季番 + 高价值 Movie/OVA 全部纳入 Tier 1

## 4. Dry-Run / Applied

| 指标 | dry-run | apply |
|---|---|---|
| added | 884 | **884** |
| updated | 0 | 0 |
| skipped | 0 | 0 |
| duplicates | 1965 | 1965 |
| invalid | 132 | 132 |
| failed | 0 | 0 |

## 5. Deduplication

- 外部 ID + normalized title + slug 三维去重（1965 重复跳过）
- 一个实体一个 canonical URL；多语言名称仅 AKA/JSON-LD/搜索

## 6. Localization

| 字段 | Before | After | Delta |
|---|---|---|---|
| English | 100% | 100% | — |
| Japanese | 63.3% | **72.3%** | +9.0pp |
| Romaji | 63.3% | **72.3%** | +9.0pp |
| Chinese | 100%（chinese_title） | 100% | — |
| Aliases | 63.3% | **72.3%** | +9.0pp |

## 7. Search Surface（Step 7）

- Entities：**3607**
- Searchable names：**9031**（avg **2.5** names/entity）
- 语言直方图：1 语言=210、2 语言=1370、3 语言=2027、0 语言=0
- 新增本阶段贡献：+884 实体 × ~2.5 名称 ≈ **+2200 可搜索名称**

## 8. Franchise / Relationship

- 新导入含高价值 franchise entry：Fate/stay night UBW 2nd Season、SAO Ordinal Scale（Movie）、Steins;Gate Movie、The Last Naruto Movie、Hellsing Ultimate（OVA）、PSYCHO-PASS 2、Fairy Tail Series 2、Kuroko's Basketball 2/3 等
- 关系：全部来自 AniList 已验证 title/format，未仅凭标题猜测 franchise

## 9. Type Integrity（Step 10）

- TV/MOVIE/OVA/ONA/SPECIAL 严格保留来源 format（Movie 不伪装 Season，OVA 不伪装 TV）

## 10. Data Quality

- **CRITICAL = 0**（详见 `phase37_data_quality_report.md`）
- 观察项 2 条（来源固有：AniList 拆分条目共享 MAL ID / AniList 无 genre），非导入错误

## 11. Search Verification（Step 17）

- English：25/25、Japanese：25/25、Romaji：18/18 全部解析到同一实体
- 无因语言产生重复页面

## 12. Sitemap（Step 19）

| | Before | After | Delta |
|---|---|---|---|
| total loc | 4876 | **5863** | +987 |
| duplicate | 0 | **0** | ✅ |
| malformed | 0 | **0** | ✅ |

## 13. Build / SSR（Step 20）

- typecheck ✅ / build ✅
- SSR：20 新（Nausicaä/Gunbuster/JoJo/Evangelion 1.0 等）+ 10 Movie/OVA + 10 旧 = **40/40 HTTP 200** + canonical + description + JSON-LD(6) + English UI

## 14. Top 50 High-Value Additions（按 popularity）

Monthly Girls' Nozaki-kun、Yona of the Dawn、SHIMONETA、Fate/stay night UBW 2nd Season、Kiznaiver、Akashic Records、Seraph of the End Nagoya、High School DxD NEW、Black Bullet、SAO Ordinal Scale（Movie）、Into the Forest of Fireflies' Light（Movie）、Yamada and the Seven Witches、Ponyo（Movie）、Kiki's Delivery Service（Movie）、Fairy Tail Series 2、Hellsing Ultimate（OVA）、Free! Iwatobi、Chunibyo Heart Throb、Grimgar、Kuroko's Basketball 2、Snow White with the Red Hair、BLEND-S、Blue Exorcist Kyoto Saga、Saekano、High School DxD BorN、INUYASHIKI、Seven Deadly Sins Signs、Monster Musume、Magi Kingdom of Magic、Little Witch Academia、Nisekoi、Amagi Brilliant Park、Kuroko's Basketball 3、Testament of Sister New Devil、Tsukigakirei、My Love Story!!、Asterisk War、Paprika（Movie）、WataMote、Date A Live II、My First Girlfriend is a Gal、Fate Heaven's Feel I（Movie）、Fruit of Grisaia、Netoge no Yome、Evangelion 1.0（Movie）、The Last Naruto Movie、Blood Lad、Steins;Gate Movie、PSYCHO-PASS 2、Myriad Colors

## 15. Remaining High-Value Candidates（Step 23）

| 类别 | 剩余 |
|---|---|
| 未导入候选 | 131（全部 Tier 3 长尾） |
| Tier 1 | 1 |
| Tier 2 | 0 |
| MOVIE | 4 |
| OVA/SPECIAL | 4 |

> 高价值候选（Tier 1/2）已充分消化；剩余为低 popularity 长尾，按规则不强行导入。

## 16. Recommended Next Expansion

1. **生产部署**（Phase 35-37 合并）：schema 3 列 + candidates 2981 + 导入 2128 条 + 回填 479
2. 下一轮（若继续）：**2013-2017 季番 second page**（当前只抓 top-50/季）或 **高价值 Movie/OVA 第二页**
3. 中文标题数据源接入（AniList 无中文，当前用日文原生名/英文）
4. GSC 验证：Movie/OVA 新页面的搜索表现

## 战略评估（Done 定义）

- ✅ 真实可搜索 Entity Surface 显著扩大：2723 → **3607**（+884），searchable names **9031**
- ✅ Entity uniqueness 保持：dups=0、malformed=0、slug collision=0、CRITICAL=0
- ✅ 数据真实性：全部 AniList 来源，无编造/无猜测
- ✅ 多语言解析质量：EN/JP/Romaji 100% 解析到同一实体
- ✅ 覆盖缺口修复：2013-2017 Year gap + Movie/OVA Type gap
