# AnimeHub Phase 26 — Deployment Checklist

> 生成于 2026-08-29 · 生产（43.133.211.250 root）执行

## 执行命令

```bash
cd /home/animehub/animehub

# 1. Sync
git fetch origin main
git rev-parse HEAD              # 记录 current production commit
git merge --ff-only origin/main
git rev-parse HEAD              # EXPECT 02fdc14b1bce630aa5f73133806fa59b6e1e04fd
git log -1 --oneline            # EXPECT: feat: phase25 google launch preparation

# 2. Build & Up
docker compose build frontend
docker compose up -d
docker compose ps
```

## 验证要求

| 服务 | 状态 |
|---|---|
| backend | healthy |
| frontend | healthy |
| postgres | healthy |
| caddy | running |

## 失败处理
- 仅修部署问题（镜像构建失败/依赖/网络/卷）
- **不修改业务代码**，不重建数据库卷

## 部署后验证
```bash
# sitemap dups 应 = 0
curl -s https://bunivoa.com/sitemap.xml | grep -o '<loc>[^<]*</loc>' | sort | uniq -d | wc -l   # EXPECT 0

# Phase 10-24 内容
curl -s https://bunivoa.com/anime/monster/ | grep -c 'Anime Information\|>Genres<\|anime released in'  # EXPECT ≥3
```
