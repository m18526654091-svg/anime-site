# AnimeHub Phase 39.x — Character/Anime Relationship Integrity Audit Report

> 日期：2026-09-01 · 范围：完整审计（未修改任何生产/本地业务数据）· 状态：根因定位完成，待生产诊断确认

## 1. Root Cause

**仓库代码链完整正确**（本地全链验证无异常）。用户报告的生产"跨作品角色显示"问题，根因**指向生产环境**，最可能为：

- **主要怀疑（CASE B）**：生产后端运行**旧版 characters API**——历史记录 `detail_500_root_cause_report.md` 明确记载：生产 1.7.0 的 `GET /api/characters?anime_id=` **anime_id 过滤未生效**（返回全量角色），与仓库代码行为不符。若 Phase 39 部署未正确 rebuild backend 镜像，此问题会直接导致所有 Anime Detail 页显示全部角色（含 Tanjiro/Killua/Luffy）。
- **次要怀疑（CASE A）**：生产 DB 角色被 Character importer 写入污染（需诊断确认）。

**排除项**（基于本地审计）：
- ❌ 仓库 API filter 错误：`characters.py` 有正确 `Character.anime_id == anime_id` 过滤（实测通过）
- ❌ 前端 merge/缓存错误：detail 页 Characters 数据源单一（SSR `fetchCharactersByAnime(anime.id)` → `initialCharacters`），无全局列表混入
- ❌ 本地 DB 污染：30 anime/125 关系抽样零跨作品

## 2. Evidence

| 层 | 检查 | 结果 |
|---|---|---|
| DB schema | `characters.anime_id` 单值 FK（NOT NULL），`slug` UNIQUE，无多对多中间表 | 模型明确 |
| DB 关系 | Tanjiro→鬼灭(anime 2)、Tanjirou→Demon Slayer IC(1114)、Killua→HxH(1007)、Luffy→海贼(4) | ✅ 正确 |
| DB 抽样 | 30 anime / 125 relationships，同 source_id 跨 anime = 0 | ✅ 无污染 |
| Backend API | `/api/characters?anime_id=1/2/3/1007/1114` 各返回 3-6 个正确角色 | ✅ 过滤生效 |
| API vs DB | 5 个采样 anime 数量全部一致 | ✅ |
| Frontend | `page.tsx` SSR `fetchCharactersByAnime(anime.id)`；`AnimeDetailClient` 仅渲染 `initialCharacters` | ✅ 无 merge |
| Importer | 新角色绑定 `anime_id=anime.id`（当前处理作品）；`reuse` 复用已有角色**不移动 anime_id** | ✅ 逻辑正确 |

## 3. Reproduction

**本地无法复现**（本地全链正确）。生产复现/定位命令：

```bash
# 在服务器执行只读诊断（已写入 backend/scripts/phase39x_diag.py）
docker compose exec backend python scripts/phase39x_diag.py
# 输出会区分：
#   CASE B（API 旧代码）：[0] characters.py 不含 anime_id filter 或 [2] API 数 ≈ 全量
#   CASE A（DB 污染）：[1] DB 角色数异常大 / [3] 问题角色绑定错误 / [4] 跨 anime 同角色
```

## 4. Impact

- **本地**：影响 0（零污染）
- **生产**：无法远程确定。若 CASE B，影响**所有**含角色的 Anime Detail 页（显示全量角色）；若 CASE A，影响被污染的具体页面。`phase39x_diag.py` 给出精确统计。

## 5. Data Integrity

- **本地 DB**：未污染（476 角色/119 anime 全绑定正确）
- **生产 DB**：待 `phase39x_diag.py` [1]/[3]/[4] 项确认
- 注意：一个角色合法属于同一 franchise 多作品（如 Tanjiro 在 TV+Movie+Season 2）是**正常**的，不能据此判定污染

## 6. Minimal Fix

**待生产诊断结果确认后执行，当前未修改任何逻辑。**

- **CASE B（API 旧代码）**：重建 backend 使新代码生效
  ```bash
  docker compose build backend && docker compose up -d backend
  # 验证：docker compose exec backend python -c "print('ok')" 后重跑诊断，[2] 应全 OK
  ```
- **CASE A（DB 污染）**：基于 `phase39x_diag.py` [4] 输出，对**明确无关**的跨作品绑定做最小修复（生成 repair SQL → 确认数量 → 执行），不重跑 importer

## 7. Data Repair

- 未执行任何修复（遵守"先审计"要求）
- 若诊断确认 CASE A：将先输出 dry-run 报告（受影响关系数/角色数/anime 数/样例），经确认后执行最小 UPDATE
- 不采用：DELETE 全表 / truncate / 无条件 relationship rebuild

## 8. Regression Tests（已新增，全部通过）

`backend/tests/test_characters_relationships.py`（5 tests）：

| Test | 验证 |
|---|---|
| test_1 | `?anime_id=X` 只返回 X 的角色（含 anime_slug 归属校验） |
| test_2 | 无参数仍返回全局角色 |
| test_3 | detail 数据源 anime-specific（无跨作品泄漏） |
| test_4 | 同 source_id 合法多 anime 记录不被删除 |
| test_5 | 多 anime 抽样无跨作品泄漏 |

全量测试：**24 passed**（19 原有 + 5 新增，无回归）

## 9. Production Verification（部署后）

```bash
# 1. 诊断脚本全项通过
docker compose exec backend python scripts/phase39x_diag.py
#   期望：[0]=True, [1]/[2] 数量一致, [3] 绑定正确, [4] 无异常

# 2. 实测一个 detail 页（如 /anime/attack-on-titan/）浏览器查看 Characters 区
#   只应显示进击的巨人角色，不应出现 Tanjiro/Killua/Luffy

# 3. API 抽查
curl -s "http://127.0.0.1:8000/api/characters?anime_id=1" | python -c "import sys,json;print(len(json.load(sys.stdin)))"
#   期望返回该 anime 实际角色数（非 476）
```

## 结论

- 根因：**仓库代码链正确，问题在生产环境**（最可能后端旧版 characters API 或生产 DB 角色污染，待 `phase39x_diag.py` 确认）
- 交付：只读诊断脚本 + 5 个回归测试 + 本报告
- 未执行任何生产/本地数据修改；未重跑 importer
