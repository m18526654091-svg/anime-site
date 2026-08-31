# AnimeHub Phase 33 — Popular Anime Priority Expansion List

> 日期：2026-08-30 · 评分：popularity(priority) ×2 + 外部 ID + 质量 + 评分

## 1. 评分模型

```
score = anime_seo_priority × 2 + 10(有 anilist/mal id) + 10(quality≥70) + score(0-10)
```

- popularity：anime_seo_priority（0-100）
- search demand / franchise potential：priority + franchise 集群
- data completeness：anilist_id/mal_id 存在（可拉取已验证别名）+ quality + score
- 名称完整度：chinese_title 含日文假名（jpname）标记

## 2. Top 25 扩展候选（高优先别名/多语言数据任务目标）

| 标题 | chinese_title | pri | ext ID | 日文名 |
|---|---|---|---|---|
| Frieren: Beyond Journey's End | 葬送のフリーレン | 100 | ✅ | ✅ |
| Chainsaw Man – The Movie: Reze Arc | チェンソーマン レゼ篇 | 100 | ✅ | ✅ |
| Puella Magi Madoka Magica | 魔法少女まどか☆マギカ | 100 | ✅ | ✅ |
| Food Wars! | 食戟のソーマ | 100 | ✅ | ✅ |
| Bungo Stray Dogs | 文豪ストレイドッグス | 99 | ✅ | ✅ |
| The Devil is a Part-Timer! | はたらく魔王さま! | 99 | ✅ | ✅ |
| Re:ZERO -Starting Life in Another World- | Re:ゼロから始める異世界生活 | 98 | ✅ | ✅ |
| The Apothecary Diaries S2 | 薬屋のひとりごと 第2期 | 97 | ✅ | ✅ |
| My Hero Academia FINAL SEASON | 僕のヒーローアカデミア FINAL | 97 | ✅ | ✅ |
| Demon Slayer: Infinite Castle | 劇場版「鬼滅の刃」無限城編 | 96 | ✅ | ✅ |
| BLEACH: TYBW | BLEACH 千年血戦篇 | 96 | ✅ | — |
| OSHI NO KO Season 3 | 【推しの子】第3期 | 96 | ✅ | ✅ |
| MONOGATARI Series: OFF & MONSTER | 〈物語〉シリーズ オフ&モンスター | 96 | ✅ | ✅ |
| JUJUTSU KAISEN Season 3 | 呪術廻戦 死滅回游 前編 | 96 | ✅ | — |
| Mushoku Tensei III | 無職転生Ⅲ | 96 | ✅ | ✅ |
| Solo Leveling S2 | 俺だけレベルアップな件 | 96 | ✅ | ✅ |
| Witch Hat Atelier | とんがり帽子のアトリエ | 96 | ✅ | ✅ |
| Orb: On the Movements of the Earth | チ。-地球の運動について- | 96 | ✅ | ✅ |
| The Dangers in My Heart S2 | 僕の心のヤバイやつ 第2期 | 96 | ✅ | ✅ |

## 3. 结论

- 这 19 个高优先条目**均已具备**英文 title + 日文原生 chinese_title + anilist/mal ID（ext=Y）
- **最高价值数据任务**：对 ext=Y 的 479 条目调用 AniList/MAL API 拉取 romaji/native/synonyms/中文官方名 → 填充 aliases，即可补齐 Phase 33 审计发现的缺口（Shingeki no Kyojin/AOT/简体名等）
- 别名填充后：AKA 区块/JSON-LD alternateName/搜索匹配 三个出口自动扩展，**无需 URL 变更**
- 排序依据：priority（搜索价值）优先，ext ID（数据可行度）次之

## 4. 实施优先级（数据任务，非本次）

1. P0：Top 19 条目的多语言别名（先做高优先）
2. P1：全部 ext=Y 479 条目
3. P2：无 ext ID 条目（需人工验证来源，低优先级）
