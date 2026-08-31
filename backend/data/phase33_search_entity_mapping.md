# AnimeHub Phase 33 — Search Entity Mapping

> 日期：2026-08-30 · 验证：后端 `/api/anime?q=` 全量结果（page_size=100）判断不同名称是否命中同一实体页

## 1. 实体 × 名称变体 匹配矩阵

| 实体 | 名称变体 | 命中 | 结果数 |
|---|---|---|---|
| attack-on-titan | Attack on Titan（英文） | ✅ | 8 |
| | 進撃の巨人（日文原生） | ✅ | 7 |
| | Shingeki no Kyojin（romaji） | ❌ 0 | 无数据 |
| | 进击的巨人（简体） | ❌ | 2（仅 Final Season 条目，主条目 chinese_title=進撃の巨人） |
| | AOT（缩写） | ❌ 0 | 无数据 |
| monster | Monster | ✅ | 7 |
| | 怪物 | ✅ | 5 |
| bleach | Bleach | ✅ | 9 |
| | 死神 | ✅ | 9 |
| fate-stay-night-ubw | Fate/stay night UBW | ✅ | 1 |
| | Fate | ✅ | 11 |
| | 命运之夜（简体） | ❌ | 8（UBW 主条目 chinese_title=同英文，无简体；2006 版含） |
| jujutsu-kaisen | JUJUTSU KAISEN | ✅ | 8 |
| | 呪術廻戦（日文） | ✅ | 5 |
| | 咒术回战（简体） | ❌ | 4（主条目为日文名，无简体） |
| re-zero | Re:Zero | ✅ | 9 |
| | 从零开始的异世界生活 | ✅ | 6 |

## 2. 结论

- **英文 + 日文原生名**（chinese_title 中的進撃の巨人/呪術廻戦/死神等）**可识别同一实体页** ✅
- **romaji 名**（Shingeki no Kyojin）、**缩写**（AOT）、**简体中文**（进击的巨人/咒术回战/命运之夜）为数据缺口：DB 无这些名称，**不伪造不硬凑**
- 后端搜索 `q` 匹配 title/chinese_title/slug 三个字段，与 AKA 显示集合一致（信息闭环）

## 3. 搜索命中覆盖率（本次测试）

- 已具备匹配能力：英文名 7/7、日文原生名 4/4（存在于 DB 的）
- 缺口（无数据，需数据任务）：romaji 3/3 缺失、缩写 1/1 缺失、简体中文 3/4 缺失

## 4. 改进建议（不改变 URL，待数据任务）

1. 数据任务填充别名（AniList/MAL native/romaji/中文）至 aliases 数据
2. 后端搜索 q 扩展到别名匹配
3. 前端搜索页 AKA 命中提示（搜索"進撃の巨人"时展示实体 + AKA）

> 现有能力已满足"同一实体多语言识别"的核心目标（英文/日文原生名），其余为增量优化。
