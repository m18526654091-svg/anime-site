# AnimeHub Phase 38 — Production Sync Runbook（Phase 35-37 合并部署）

> 服务器：43.133.211.250 (root) · 目录：/home/animehub/animehub
> 目标：将 Phase 35-37 的 +2128 Anime 与多语言字段同步到 production
> 阻塞说明：本 runbook 需人工在服务器执行（当前环境无 SSH 凭据）

## 0. 前置

```bash
cd /home/animehub/animehub
git fetch origin
git merge --ff-only origin/main   # 期望到 f2a4fe6
```

## 1. 备份 production DB

```bash
docker compose exec -T backend python -c "
from app.database import SessionLocal, engine
import shutil, time
# PostgreSQL 备份（dump 到 backend/data）
docker compose exec -T postgres pg_dump -U animehub animehub > backup_phase37_$(date +%Y%m%d).sql
"
```

## 2. Migration（自动，幂等）

```bash
docker compose up -d backend   # ensure_schema 自动添加 3 新列：
# japanese_title TEXT DEFAULT ''
# romaji_title TEXT DEFAULT ''
# aliases TEXT DEFAULT ''
```

验证列存在：
```bash
docker compose exec -T backend python -c "
import sqlite3  # 或 psycopg2
from app.database import engine
from sqlalchemy import inspect
cols = {c['name'] for c in inspect(engine).get_columns('anime')}
print('japanese_title' in cols, 'romaji_title' in cols, 'aliases' in cols)
"
```

## 3. 导入 Phase 35-37 数据（2128 条）

```bash
# candidates 数据已随代码进入 backend/data/anilist_anime_candidates.json（2981 条）
docker compose exec -T backend python scripts/import_anime_anilist.py --dry-run
# 确认 new≈2128、duplicates 合理、invalid 约 223、无异常后：
docker compose exec -T backend python scripts/import_anime_anilist.py
```

预期结果（本地实测）：
- added: 2128（485 + 759 + 884）
- updated: 0 / skipped: 0
- duplicates: 累计（与库内已有匹配）
- invalid: 223（格式不合规）
- failed: 0

## 4. 多语言回填（479 条旧数据）

```bash
docker compose exec -T backend python scripts/backfill_localized_titles.py --dry-run
docker compose exec -T backend python scripts/backfill_localized_titles.py
```

预期：updated≈479（依赖 production 现有 anilist_id 覆盖）

## 5. 重启 + 验证

```bash
docker compose build frontend
docker compose up -d
docker compose ps   # 全部 healthy
```

## 6. Post-deploy 验证（Step 2-4）

```bash
# Anime count
curl -s "http://localhost:8000/api/anime?page=1&page_size=1" | python -c "import sys,json; d=json.load(sys.stdin); print(d['total'])"
# 预期 3607

# sitemap
curl -s https://bunivoa.com/sitemap.xml | grep -o "<loc>" | wc -l   # 预期 5863
curl -s https://bunivoa.com/sitemap.xml | sort | uniq -d | wc -l    # 预期 0

# 多语言搜索
curl -s "http://localhost:8000/api/anime?q=進撃の巨人&page=1&page_size=1" | python -c "import sys,json; print(json.load(sys.stdin)['items'][0]['slug'])"
# 预期 attack-on-titan
```

## 7. GSC 后续（Step 5）

```bash
# 部署完成后重新提交 sitemap（GSC → Sitemaps → https://bunivoa.com/sitemap.xml）
# 记录 Day 0 baseline（impressions/clicks/CTR/position/indexed）
```

## 8. 回滚预案

- DB 备份恢复：`docker compose exec -T postgres psql -U animehub < backup_phase37_YYYYMMDD.sql`
- 代码回滚：`git checkout <前一 commit> && docker compose build frontend && docker compose up -d`
- 导入幂等：重复运行不重复新增（anilist_id/title 去重）
