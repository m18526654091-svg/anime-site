# AnimeHub Phase 36 — Catalog Expansion Report (Round 2)

> 日期：2026-08-30 · 范围：第二批高价值 Anime（2018-2022 季番增量）· 状态：✅ 完成

## 1. Before / After

| 指标 | Before（Phase 35 末） | After |
|---|---|---|
| Anime count | 1964 | **2723（+759）** |
| sitemap count | 4044 | **4876（+832）** |
| AniList coverage | 964 (49.1%) | **1723 (63.3%)** |
| Localized coverage（japanese/romaji/aliases） | 964 (49.1%) | **1723 (63.3%)** |

## 2. 导入统计（Step 2）

| 指标 | dry-run | apply |
|---|---|---|
| added | 760 | **759** |
| updated | 0 | 0 |
| skipped | 0 | 0 |
| duplicates | 1128 | 1129 |
| invalid | 72 | 72 |
| failed | 0 | 0 |

> dry-run 与 apply 差 1（边界，无异常）。

## 3. 数据源（Step 1/3）

- **AniList GraphQL 增量抓取**：2018-2022 季番（Phase 35 未覆盖年份），merge 进现有 candidates
- 候选总量：1090（Phase 35）→ **1960**（+870 增量，2018-2022 季番 top-50/季）
- 复用 `discover_anime_anilist.py`（新增 merge 模式 + 每查询增量写盘）+ `import_anime_anilist.py`（幂等）
- Top 22 优先级检查：Attack on Titan / One Piece / Naruto / DB / Bleach / JJK / Demon Slayer / MHA / Frieren / Chainsaw Man / Solo Leveling / Death Note / HxH / Code Geass / Steins;Gate / FMA / Haikyuu / Gintama / JoJo / Fate / Monogatari / Re:Zero —— **全部已存在，未重复导入** ✅

## 4. Localization（Step 4）

| 语言 | 覆盖（导入条目） | 说明 |
|---|---|---|
| English | 100%（title） | AniList english title |
| Japanese（native） | 100%（759 条） | AniList native |
| Romaji | 100%（759 条） | AniList romaji |
| Chinese | 有真实来源才填 | AniList 无中文 → 用日文原生名（含汉字）或英文，**不冒充官方中文名** |
| Aliases | 100%（759 条） | [english, romaji, native] 去重 JSON |

## 5. Data Quality（Step 5）

全库扫描（2723 条）：duplicate anilist/mal = 0、title collision = 0、empty title/year/score/slug = 0、malformed aliases = 0、slug collision = 0
**CRITICAL = 0** ✅（详见 `phase36_data_quality_report.md`）

## 6. Entity Identity（Step 6）

50 个新增抽查（随机种子 42）：
- English title → 同一实体：**50/50**
- Japanese native → 同一实体：**50/50**
- Romaji → 同一实体：**40/40**
- **无 3-4 个独立 Anime 分裂** ✅

## 7. SEO 集成（Step 7/8/10）

- 新实体自动进入 detail/genre/year/studio/similar 管道（无手工链接）
- sitemap：**4876 URL，duplicates = 0，malformed = 0**（Before 4044）
- SSR：20 新增 + 10 旧页全部 **HTTP 200** + canonical + description + JSON-LD（6 块）+ English UI
- canonical 始终指向唯一实体（多语言名称仅用于 AKA/JSON-LD alternateName/搜索）

## 8. 新增 Top 50 高价值 Anime（按 AniList popularity）

1. My Hero Academia: Two Heroes 2. SAO Alicization War of Underworld 3. Angels of Death 4. Lycoris Recoil 5. Seven Deadly Sins: Imperial Wrath 6. World's Finest Assassin 7. Cells at Work! 8. Cautious Hero 9. DanMachi III 10. Bungo Stray Dogs 3 11. SAO Alicization P2 12. JoJo STONE OCEAN 13. A Whisker Away 14. Dorohedoro 15. Higehiro 16. Josee the Tiger and the Fish 17. Wise Man's Grandchild 18. BOFURI 19. Vivy -Fluorite Eye's Song- 20. Food Wars! Fourth Plate 21. MHA: Heroes Rising 22. TSUKIMICHI 23. Food Wars! Third Plate 24. Teasing Master Takagi-san 25. takt op.Destiny 26. Iruma-kun 27. Komi Part 2 28. SAO Alternative GGO 29. Laid-Back Camp 30. Dragon Maid S 31. More than a Married Couple 32. The Millionaire Detective 33. In/Spectre 34. The Way of the Househusband 35. Devil is a Part-Timer! S2 36. So I'm a Spider 37. Wandering Witch Elaina 38. Gleipnir 39. Uzaki-chan 40. HINAMATSURI 41. Food Wars! Fifth Plate 42. Asobi Asobase 43. My Next Life as a Villainess 44. Maquia 45. Citrus 46. Bottom-Tier Tomozaki 47. Fairy Tail Final Season 48. Plunderer 49. BEASTARS S2 50. ORESUKI

## 9. 规则遵守

- ✅ 复用现有 pipeline（discover merge + import 幂等），未重新造轮子
- ✅ 保留 external IDs（anilist_id/mal_id 1723/1722）
- ✅ 导入前去重（1129 duplicate 跳过）
- ✅ 多语言仅真实来源（AniList title 三字段；中文不冒充）
- ✅ 无重复实体 / 无假 Anime / 无 URL 修改 / 无批量重复语言 URL / 无空 SEO 页
- ✅ 未做大规模 SEO 架构重构

## 10. 后续建议

1. 生产部署：同步 3 新列 schema（Phase 35）+ 新 candidates（1960 条）+ 导入 1244 条（485+759）+ 回填 479
2. 第三批：2013-2017 季番 + MOVIE/OVA 专项
3. 中文标题源：接入已验证中文数据源后补 Chinese title
