# AnimeHub Phase 25 — Google Launch Report

> 生成于 2026-08-29 · 部署前状态（如实记录，不伪造部署成功）

## 部署状态

| 项 | 值 |
|---|---|
| target commit | `549dc14`（Phase 24，本地 HEAD = origin/main）|
| current production commit | ⚠️ **推断 Phase 9/SEO-Accel**（需在生产 `git rev-parse HEAD` 核实）|
| 部署状态 | ❌ **未部署**（Phase 10-24 共 13 个 release pending）|
| docker containers | 无法远程检查（需生产 `docker compose ps`）|

## 部署命令（在 43.133.211.250 root 终端执行）

```bash
cd /home/animehub/animehub
# Step 1 — Production Sync
git fetch origin main
git rev-parse HEAD; git rev-parse origin/main   # 记录 current / target
git merge --ff-only origin/main                 # → 549dc14
git rev-parse HEAD                              # EXPECT 549dc149258421538dc0c53b9ebde9f51abd708c

# Step 2 — Docker Deployment
docker compose build frontend
docker compose up -d
docker compose ps                               # EXPECT: backend/frontend/postgres healthy + caddy up
```
失败时：只修部署问题（镜像/依赖/网络），不改业务代码。

## 部署后验证清单

### Sitemap / Robots
```bash
curl -s https://bunivoa.com/sitemap.xml -o /tmp/sm.xml
echo "count=$(grep -c '<loc>' /tmp/sm.xml)"      # EXPECT 3470
echo "dups=$(grep -o '<loc>[^<]*</loc>' /tmp/sm.xml | sort | uniq -d | wc -l)"  # EXPECT 0（Phase 21 修复）
curl -s https://bunivoa.com/robots.txt | grep -c 'Sitemap: https://bunivoa.com/sitemap.xml'  # EXPECT 1
```

### 抽查页面（HTTP/title/description/canonical/JSON-LD/English UI）
```bash
for url in \
  "https://bunivoa.com/" \
  "https://bunivoa.com/anime/monster/" \
  "https://bunivoa.com/anime/attack-on-titan/" \
  "https://bunivoa.com/anime-series/fate/" \
  "https://bunivoa.com/best-anime/psychological/" ; do
  echo "=== $url ==="
  curl -sL -o /tmp/p.html -w "HTTP=%{http_code}\n" "$url"
  grep -o '<title>[^<]*</title>' /tmp/p.html | head -1
  grep -o 'rel="canonical" href="[^"]*"' /tmp/p.html | head -1
  grep -c 'application/ld+json' /tmp/p.html
  grep -o 'Anime Information\|>Genres<\|Home\|Trending' /tmp/p.html | sort -u | head -4
done
```

### Phase 10-24 功能验证
- Anime Information / Genres / Entity Summary / Similar reason badges / English UI / sitemap dups fix
```bash
curl -s https://bunivoa.com/anime/monster/ | grep -c 'Anime Information\|>Genres<\|anime released in'
# EXPECT ≥3（Anime Information + Genres + Entity Summary）
```

## 当前检查结果（部署前，实测）

| 项 | 状态 |
|---|---|
| Production commit | ⚠️ Phase 9 推断（未核实）|
| Sitemap | 3470 / **dups=9**（部署后应为 0）|
| Indexed baseline | **WAITING**（GSC 未接入）|
| Robots | ✅ Sitemap 行 + Allow / |
| Canonical | ✅ 自指 |
| JSON-LD | ✅ 2-6/页 |
| GA status | ⚠️ 组件待部署；无 GA ID 未启用（零影响）|
| AdSense readiness | ✅ PASS（信任页齐全）|
| Known issues | **生产未部署**（13 release pending）、sitemap dups=9、Phase 10-24 内容缺失 |

## 结论
Google Launch **被生产部署阻塞**。部署完成后按本报告验证清单确认，再进入 GSC 提交与 30 天实验。
