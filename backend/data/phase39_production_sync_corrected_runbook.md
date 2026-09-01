# AnimeHub Phase 39 — Corrected Production Sync Runbook

> 日期：2026-09-01 · 修正目标：解决"生产 candidates 只有 535 条 + 3 列缺失"的根因
> 依据：本地 Git 对象库实际审计（非 runbook 假设）

## 1. 根因（已审计确认）

### 根因 A：生产 candidates 文件不是 Git 版本
Git 中该文件真实演进（本地 git show 实测）：

| commit | Phase | records | total_requests |
|---|---|---|---|
| f632727 | 35 | **1090** | 31 |
| 8f786f3 | 36 | **1960** | 20 |
| f2a4fe6 | 37 | **2981** | 31 |
| 0c75a52 | 39（当前） | **2981**（blob 608e9530） | 31 |

- 生产显示 **535** = Phase 35 之前的旧文件（从未被 merge/checkout 更新）
- dry-run `source_total=535, duplicate=527, invalid=8` 与旧文件完全吻合（527 已在库 + 8 格式不合规）
- **证据**：`git rev-parse HEAD:backend/data/anilist_anime_candidates.json` = `608e95305fecd87da7dbc8a2f15eabdc6a67a1e6`，与本地当前文件 `git hash-object` 一致（2981 条 4.8MB）

### 根因 B：3 列缺失 = backend 未用新代码重建
- `ensure_schema()` 在 `app/main.py:17` 启动时调用
- `database.py` PostgreSQL 分支（line 194-199）含 3 列幂等 `ALTER TABLE`（已审计）
- backend 为 **image-based**（docker-compose `build: context: ./backend`，无 volume 挂载代码）→ **必须 `docker compose build backend`** 才能加载含 3 列迁移的新代码
- 仅 `docker compose up -d` 不触发 rebuild → 旧 image 的 ensure_schema 无 3 列逻辑 → 列未创建

## 2. 真实数据链（Step 2 结论）

```
2128 条新增 Anime
 = 485（Phase 35，来自 candidates@f632727，1090 条中）
 + 759（Phase 36，来自 candidates@8f786f3，1960 条中）
 + 884（Phase 37，来自 candidates@f2a4fe6，2981 条中）
```

- **文件**：`backend/data/anilist_anime_candidates.json`（Git 对象 `608e9530`，2981 条）
- **importer**：`backend/scripts/import_anime_anilist.py`（DEFAULT_SOURCE 读取该文件，幂等，anilist_id/title/slug 三维去重）
- **字段**：japanese_title / romaji_title / aliases（Phase 35 新增，import 写入）
- **可安全重放**：✅ 是（本地用同一 importer 已验证 2128 条；幂等，重复运行不重复新增）
- **注意**：candidates@f2a4fe6 已包含 Phase 35/36 的全部数据（1090→1960→2981 是累加 merge）→ **生产只需一次导入 2981 候选即可得到 485+759+884=2128 新增**

## 3. 执行步骤（严格顺序）

```bash
# ① 进入仓库
cd /home/animehub/animehub

# ② 确认 HEAD
git log -1 --oneline   # 期望 0c75a52

# ③ 恢复 candidates 文件到 Git 版本（安全：只恢复该文件，不触碰其他）
git restore --source=0c75a52 backend/data/anilist_anime_candidates.json
# 验证 records=2981：
python -c "import json;d=json.load(open('backend/data/anilist_anime_candidates.json',encoding='utf-8'));print(len(d['items']))"

# ④ 重建 backend（加载含 3 列迁移的新代码）
docker compose build backend
docker compose up -d backend
# 等 healthy（healthcheck 自动跑 ensure_schema 建 3 列）
docker compose ps

# ⑤ 验证 3 列已建（幂等，重复跑无害）
docker compose exec backend python -c "
from app.database import engine
from sqlalchemy import inspect
cols={c['name'] for c in inspect(engine).get_columns('anime')}
print('japanese_title' in cols, 'romaji_title' in cols, 'aliases' in cols)
# 期望 True True True
"
```

## 4. 导入（dry-run → 检查 → apply）

```bash
# ④ dry-run（只统计不写库）
docker compose exec backend python scripts/import_anime_anilist.py --dry-run
# 预期（数学推导，生产 1479 起点）：
#   source_total=2981
#   new≈2128      ← 精确值（推导见下）
#   duplicate≈853
#   invalid≈223   ← 格式非 TV/MOVIE/ONA/OVA/SPECIAL（19+72+132 累计）
#   updated=0 / skipped=0 / failed=0
# 若 new 显著偏离 2128（如 0 或 <500）：停止，检查 candidates 是否 2981 条、DB 初始库是否 1479
```

### dry-run new=2128 的数学推导（为什么生产起点 1479 时精确成立）

```
前提：
- 本地 Phase 37 库 = 2723 = 1479（原始）+ 485（P35）+ 759（P36）[生产 = 1479，即本地原始子集]
- 本地从 2723 导入 2981 候选 → new_local = 884（实测）
- 生产 1479 ⊆ 本地 2723；本地比生产多的 1244 条（485+759）全部来自候选

推导：
new_prod = 候选 2981 中不在生产 1479 的
        = (不在本地 2723 的 884) + (在本地 2723 但不在生产 1479 的 1244)
        = 884 + 1244
        = 2128

即：生产一次导入 2981 候选，会得到 485(P35) + 759(P36) + 884(P37) = 2128 全部新增。
```

> 验证：`duplicate_prod` = 2981 − 2128 − 223(invalid) = 630（生产 1479 中与候选匹配的 + 候选内部 title 重复），合理范围 600-900。

### dry-run 通过标准
- [ ] `new` 在 2000–2250 区间
- [ ] `failed=0`、`updated=0`
- [ ] `invalid` ≈ 223（±10）
- [ ] 3 列已验证存在（True True True）

### ⑤ 检查通过后正式导入（幂等，可重跑，不会覆盖已有数据）

```bash
docker compose exec backend python scripts/import_anime_anilist.py
# 预期：new≈2128（与 dry-run 一致）
# 导入完成后验证：
docker compose exec backend python -c "
from app.database import SessionLocal
from app.models import Anime
print('anime count:', SessionLocal().query(Anime).count())   # 预期 3607
print('localized:', SessionLocal().query(Anime).filter(Anime.japanese_title != '').count())  # 预期 2607"
```

## 5. 多语言回填（可选但推荐，479 条旧数据）

```bash
docker compose exec backend python scripts/backfill_localized_titles.py --dry-run
docker compose exec backend python scripts/backfill_localized_titles.py
# 预期 updated≈479（依赖生产现有 anilist_id 覆盖；若无外部网络访问 AniList 则跳过此步）
```

> 注意：backfill 需要生产可访问 `graphql.anilist.co`。若无外网，跳过（不影响主导入）。

## 6. apply 后验证

```bash
# Anime count = 3607
docker compose exec backend python -c "
from app.database import SessionLocal
from app.models import Anime
print(SessionLocal().query(Anime).count())"

# 多语言搜索（示例：進撃の巨人 解析到 attack-on-titan）
curl -s "http://127.0.0.1:8000/api/anime?q=%E9%80%B2%E6%92%83%E3%81%AE%E5%B7%A8%E4%BA%BA&page=1&page_size=1"

# 重建 frontend 使 sitemap 含新实体
docker compose build frontend && docker compose up -d frontend

# sitemap
curl -s https://bunivoa.com/sitemap.xml | grep -o "<loc>" | wc -l   # 预期 5863
curl -s https://bunivoa.com/sitemap.xml | sort | uniq -d | wc -l    # 预期 0

# 质量检查（CRITICAL=0）
docker compose exec backend python scripts/phase15_quality_scan.py   # 若存在；否则用 DB 查询验证
```

## 7. 检查条件（apply 前必须满足）

- [ ] `git log -1` = 0c75a52
- [ ] candidates records = **2981**
- [ ] dry-run `new` = **2128**（数学推导：884 不在本地2723 + 1244 本地多出且来自候选；±50 内均视为通过，若生产初始库非 1479 则按实际，但不应为 0）
- [ ] dry-run `failed=0`、`updated=0`
- [ ] duplicate/invalid 比率合理（≠100%）
- [ ] 3 列已验证存在（True True True）

## 8. Rollback

- **DB**：`docker compose exec -T postgres psql -U animehub animehub < backup_phase37_20260901_005915.sql`
- **代码**：`git checkout f2a4fe6 -- backend/scripts frontend/app && docker compose build frontend backend && docker compose up -d`
- **导入幂等**：重复运行不重复新增（anilist_id/title 去重）
- candidates 文件：`git restore --source=0c75a52 backend/data/anilist_anime_candidates.json` 可随时还原

## 9. 停止条件

若以下任一成立，**立即停止并报告，不强行导入**：
1. candidates records ≠ 2981（restore 后仍异常）
2. dry-run new=0 或 new 异常低（说明文件/去重逻辑有误）
3. 3 列迁移失败（ensure_schema 报错）
4. 生产 DB 初始 Anime 数异常（≠1479 且无法解释）
