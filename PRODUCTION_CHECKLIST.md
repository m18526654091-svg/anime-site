# AnimeHub v5.3 上线前检查清单（Production Checklist）

> 版本：v5.3 ｜ 更新：2026-08-13
> 检查环境：Windows 本地（后端 FastAPI :8000，前端生产构建 `next start` :3000，HTTP 级实测）。
> 说明：v5.2 新增生产安全守卫（SECRET_KEY / PostgreSQL / CORS fail-fast）；本地无 Docker 守护进程，Docker 部署项以**静态验证 + 配置评审**为准。

---

## 1. 环境变量检查

- [ ] **SECRET_KEY 已设置为强随机值**（必填，任何环境）
  - 后端 `auth.py` 已加固（v5.2）：**缺失 / 过短(<16) / 已知默认值 → 启动即报错**，不再有公开回退密钥
  - Docker：`docker-compose.yml` 使用 `${SECRET_KEY:?}`，未设置时 compose 直接报错
  - systemd：`deploy.sh` 自动生成并持久化到 `/root/.animehub_secret_key`，注入后端服务环境
  - 重启前后密钥必须一致（deploy.sh 已持久化；Docker 需在 .env 中固定）
- [ ] **ALLOWED_ORIGINS** 已限制为真实域名（逗号分隔），如：`https://your-domain.com,https://www.your-domain.com`
- [ ] **DATABASE_URL** 正确
  - 本地开发：`sqlite:///./animehub.db`（仅限 development）
  - Docker 生产（compose 已内置）：`postgresql+psycopg2://animehub:password@postgres:5432/animehub`
  - systemd 生产（deploy.sh 自动初始化）：`postgresql+psycopg2://animehub:<随机口令>@127.0.0.1:5432/animehub`
- [ ] **生产禁止 SQLite**：`ENVIRONMENT=production|staging` 时后端强制要求 `DATABASE_URL` 为 PostgreSQL（database.py 守卫，v5.2）
- [ ] **NEXT_PUBLIC_API_URL** 正确
  - 本机 systemd：`http://localhost:8000`
  - Docker（compose 已内置）：`http://backend:8000`
  - 前端同源代理 `/api/[[...path]]` 已改为读取该环境变量（v5.1 修复）
- [ ] **NEXT_PUBLIC_SITE_URL** 为最终对外域名（`https://` 开头，无末尾斜杠），用于规范链接/OG/sitemap
- [ ] `frontend/.env.local` 已创建且值正确（模板见 `frontend/.env.example`）

**实测**：`frontend/.env.local` = `NEXT_PUBLIC_SITE_URL=http://localhost:3000`、`NEXT_PUBLIC_API_URL=http://localhost:8000` ✅

---

## 2. 数据库检查

- [ ] 首次启动自动建表 + 自动写入动漫数据（`seed_anime`）
- [ ] 首次启动自动为每部动漫写入可播放剧集（v5.1 新增：只对**空库**触发）
- [ ] 对已有库执行数据导入 / 剧集补齐（幂等，可重复执行）：
  ```bash
  cd backend
  .venv\Scripts\python -m scripts.import_anime
  .venv\Scripts\python -m scripts.seed_episodes
  ```
- [ ] 数据量校验
  - 动漫总数：120
  - 剧集总数：955（覆盖全部 120 部动漫）
  - 无 `example.com` 占位地址残留

**实测**：`anime=120`，`episodes=955`，`覆盖动漫数=120`，`example.com 残留=0` ✅

---

## 3. API 检查（前端口径 = 同源 /api 代理）

- [ ] `GET /api/anime`（列表分页）→ 200
- [ ] `GET /api/anime?q={关键词}`（搜索）→ 200，返回匹配结果
- [ ] `GET /api/anime?category={类型}`（分类筛选）→ 200，返回对应类型
- [ ] `GET /api/anime/{id}`（详情）→ 200
- [ ] `GET /api/anime/{id}/episodes`（剧集）→ 200，含 items/total
- [ ] 登录 / 注册 / 评论 / 评分 / 收藏端点存在且可用（管理接口需要管理员 token）

**实测**（前端代理 3000 → 后端 8000）✅：
| 端点 | 结果 |
| --- | --- |
| `/api/anime?q=巨人&page=1&page_size=18` | 200，total=1（进击的巨人） |
| `/api/anime?category=校园/恋爱&page=1&page_size=18` | 200，total=4（全部为校园/恋爱） |
| `/api/anime/1/episodes` | 200，total=3，视频源为真实 mp4 |

---

## 4. SEO 检查

- [ ] `GET /robots.txt` → 200，内容含 `Sitemap:` 指向
- [ ] `GET /sitemap.xml` → 200，含全部动漫详情 URL（`<urlset>`）
- [ ] 详情页输出 `application/ld+json`（TVSeries/Movie 结构化数据）
- [ ] 详情页输出 Open Graph / Twitter Card meta，图片为封面
- [ ] `metadataBase` 基于 `NEXT_PUBLIC_SITE_URL`
- [ ] `lang="zh-CN"`，规范链接与 `trailingSlash` 配置一致

**实测**：`/robots.txt` 200（302B）；`/sitemap.xml` 200（16,336B）✅

---

## 5. 页面检查

- [ ] 首页 200（服务端渲染动漫网格）
- [ ] 搜索框交互正常（客户端请求走代理）
- [ ] 分类按钮点击后列表变化
- [ ] 分页正常（上一页/下一页/页码省略号）
- [ ] 详情页 200（海报、中文名、评分、标签、收藏按钮、「开始播放」按钮）
- [ ] 播放页 200（`/watch/{id}`，含 `<video>` + `<source>`）
- [ ] 登录 / 注册页可达
- [ ] 管理页面可达（需管理员权限）

**实测**（HTTP 级）：首页/详情/播放页均 200，按钮与链接存在于渲染 HTML ✅

### 移动端（代码审查，需真机复测）

- [ ] 首页网格：`grid-cols-2 sm:3 md:4 lg:5/6`，小屏两列 ✅
- [ ] 动漫卡片：图片 `h-52`→`h-60`，标题 `truncate` + 状态徽章，宽屏无溢出 ✅
- [ ] 详情页：海报居中 `mx-auto`；标题行 `flex-1` + 收藏按钮 `shrink-0`，播放按钮在主信息区 ✅
- [ ] 播放器：`aspect-video w-full`（16:9）✅
- [ ] 选集按钮：`grid-cols-4 sm:6 md:8 lg:10`，小屏四列 ✅
- [ ] 导航条：仅「首页」+「详情」，小屏无溢出 ✅
- [ ] 建议：在 ≤390px 真机（iPhone SE/安卓）人工过一遍上述页面

---

## 6. 播放检查

- [ ] 详情页「开始播放」跳转 `/watch/{id}` 正确
- [ ] 播放页加载第一集视频源（mp4，可直接流播）
- [ ] **选集切换**：点击第 N 集 → URL 变为 `?ep=N` → 加载对应集（v5.1 修复）
- [ ] 当前选集高亮（`shadow-glow`）正确
- [ ] 无剧集时显示「暂无播放资源」（容错）
- [ ] 浏览器 ❌ CORS 报错（同源代理无跨域）

**实测**：
- `/watch/1` → 第 1 集 `BigBuckBunny.mp4` ✅
- `/watch/1?ep=2` → 第 2 集 `ElephantsDream.mp4`，选集切换生效 ✅
- `/watch/1?ep=3` → 第 3 集（`ForBiggerBlazes.mp4`）✅

---

## 7. 安全配置检查（v5.2 新增）

### SECRET_KEY 检查
- [ ] 环境变量 `SECRET_KEY` 已设置，且为 ≥16 位强随机串（`openssl rand -hex 32`）
- [ ] 数据库中未残留任何使用「旧默认密钥」签发的 token（若曾被默认密钥污染，请在更换密钥后清理/失效旧 token）
- [ ] 后端启动有保护：缺失 / 过短 / 常见默认值（如 `change-me-in-production`）→ 启动报错并提示生成命令
- [ ] `SECRET_KEY` 不在代码 / 仓库 / 日志中明文出现

### 数据库密码检查
- [ ] PostgreSQL 口令为强随机值（非 `password` / 非弱口令）
- [ ] Docker：compose 中 `POSTGRES_PASSWORD` 通过 `.env` 注入，不硬编码弱口令
- [ ] systemd：deploy.sh 生成的数据库口令仅存于 `/root/.animehub_pg_password`（`chmod 600`），日志不回显
- [ ] 数据库端口不对外暴露（Docker 内网 / 127.0.0.1）
- [ ] 生产连接使用 `postgresql+psycopg2://`，且测试 SQLite 仅存在于开发环境

### HTTPS 检查
- [ ] 对外域名使用有效 TLS 证书（Docker 参考 DEPLOY.md 配置 Nginx/Caddy）
- [ ] Caddy/Nginx 配置：HTTP→HTTPS 跳转、`X-Content-Type-Options`/`X-Frame-Options` 等安全响应头
- [ ] `NEXT_PUBLIC_SITE_URL` 为 `https://` 开头且与证书域名一致
- [ ] 证书自动续期（Caddy 默认 / certbot cron）

### 域名配置检查
- [ ] `DOMAIN`（deploy.sh）已改为真实域名，非 `YOUR_DOMAIN` 占位
- [ ] `NEXT_PUBLIC_SITE_URL` 为最终对外地址，无尾部斜杠
- [ ] 规范链接 / sitemap / Open Graph 使用该域名
- [ ] DNS A/AAAA 记录已指向服务器，`curl -I https://<域名>` 返回 200

### CORS 检查
- [ ] 生产 `ALLOWED_ORIGINS` 显式列出真实来源（逗号分隔），**禁止 `*`**
- [ ] 后端守卫（v5.2）：`ENVIRONMENT=production|staging` 时 `ALLOWED_ORIGINS` 缺失或为 `*` → 启动报错
- [ ] 浏览器实际访问页面无 CORS 报错（同源 `/api` 代理）
- [ ] 管理/登录接口 Cookie→同源；凭据类请求来源均在 `ALLOWED_ORIGINS` 内

---

## 当前上线风险（必须知悉）

| 级别 | 风险 | 说明 / 缓解 |
| --- | --- | --- |
| 🟢 已修复 | **JWT 回退密钥** | v5.2：`auth.py` 已加启动守卫，缺失/过短/默认值拒绝启动；无公开回退密钥 |
| 🟠 中 | **样例视频源为公共样片** | 目前播放内容为 Google GTV 测试视频，**上线前必须替换为授权/自有视频源**（`anime_data.json` 或 `seed_episodes.py` 的 URL 池） |
| 🟡 低 | **Docker 未真机验证** | 本地无 Docker，`docker-compose.yml` 仅静态校验；请在服务器执行 `docker compose config` + 全量 `up` 验证 |
| 🟡 低 | **PostgreSQL 口令默认值** | compose 中 `POSTGRES_PASSWORD: password` 为模板值，`POSTGRES_USER/DATABASE` 亦固定；生产应使用强口令并从 `.env` 注入（已列入数据库密码检查） |
| 🟡 低 | **无自动化 E2E** | 移动端/交互目前为代码审查 + HTTP 实测；建议上线后补 Playwright/Cypress 覆盖主链路 |
| 🟢 已修复 | **deploy.sh 裸机生产路径安全** | v5.3：SSH 防火墙保护（`SSH_PORT`默认22） + 非交互部署支持（`SKIP_UPLOAD_WAIT=1`）；正式环境建议先 `bash -n` 验证 |
| 🟢 说明 | **Docker 构建依赖稳定性** | v5.3：`frontend/Dockerfile` 切为 `npm ci`（`package-lock.json` 已存在），保证可复式构建 |
| 🟢 说明 | **CORS/SECRET_KEY 守卫属新增保护** | development 默认行为不变（CORS `*`、SQLite），仅生产（staging/production）强制安全配置 |

## 上线前最终命令（服务器）

```bash
# 1) 配置环境
cp .env.example .env
# 编辑 .env：SECRET_KEY / ALLOWED_ORIGINS / NEXT_PUBLIC_SITE_URL / NEXT_PUBLIC_API_URL

# 2) 校验 compose 配置
docker compose config

# 3) 启动
docker compose up --build -d

# 4) 数据初始化（新库会自动完成；已有库手动补）
docker compose exec backend python -m scripts.import_anime
docker compose exec backend python -m scripts.seed_episodes

# 5) 健康检查
curl -I https://your-domain.com/sitemap.xml
curl http://localhost:8000/api/anime?page=1&page_size=1
```