# AnimeHub v5 体验版

一个生产就绪的动漫资源站：Next.js 14 前端 + FastAPI 后端 + SQLite 数据库。

> 搜索、分类筛选、详情、在线播放、点评、收藏、登录注册、SEO 全套可用。

## ✨ v5 功能亮点

- 🎬 **在线播放**：`/watch/[id]` 播放页 + 选集列表，数据库驱动，即点即看
- 🔍 **搜索与筛选**：关键词搜索、分类（类型）/年份筛选、评分/年份排序
- 📄 **详情页**：中文名、评分、年份、地区、作者、制作公司、标签、直播选集、收藏按钮、相关推荐
- 🛡 **全站中文化**：导航、按钮、标签、分页全部中文，无广告占位
- 🔎 **SEO 就绪**：动态 `sitemap.xml`、`robots.txt`、Open Graph、Twitter Card、结构化数据 JSON-LD、`metadataBase` 规范 URL
- 🖥 **部署友好**：环境变量驱动（API 地址 / 站点 URL / SECRET_KEY / CORS / 数据库），Docker Compose + systemd 部署脚本
- 📥 **数据导入**：`anime_data.json` 批量导入 + 剧集种子脚本，幂等可重复执行

## 📦 技术栈

| 层 | 技术 |
| --- | --- |
| 前端 | Next.js 14 (App Router) · TypeScript · Tailwind CSS · Axios |
| 后端 | FastAPI · SQLAlchemy · Pydantic v2 |
| 数据库 | SQLite（默认，可通过 `DATABASE_URL` 切换 PostgreSQL） |
| 部署 | Docker Compose · Nginx（可选） |

## 📁 目录结构

```
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── main.py          # 应用入口（CORS、路由、建表、种子）
│   │   ├── models.py        # User / Anime / Episode / Rating / Comment / Favorite
│   │   ├── schemas.py       # Pydantic 模型
│   │   ├── api/             # anime / users / comments / favorites 路由
│   │   ├── database.py      # SQLAlchemy + ensure_schema 轻量迁移
│   │   └── seed.py          # 空库自动填充动漫数据
│   └── scripts/
│       ├── import_anime.py  # 批量导入 anime_data.json
│       └── seed_episodes.py # 为缺失剧集的动漫生成可播放剧集
├── frontend/                # Next.js 前端
│   ├── app/                 # 页面（首页、详情、播放、分类、登录等）
│   ├── components/          # HomeClient / AnimeCard / AnimeDetailClient / Navbar …
│   └── lib/api.ts           # 与后端交互的统一 API 层
├── anime_data.json          # 动漫数据集（120+ 部）
├── deploy.sh                # systemd + Nginx 一键部署脚本
├── docker-compose.yml       # 前端 + 后端容器编排
└── DEPLOY.md                # 生产部署详细指南
```

## 🚀 本地开发

### 环境要求

- Node.js ≥ 18
- Python ≥ 3.10
- （可选）Docker

### 1. 启动后端（FastAPI，端口 8000）

后端启动前**必须**通过环境变量提供 `SECRET_KEY`（缺失或使用已知默认值会拒绝启动）：

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux / macOS
pip install -r requirements.txt

# 设置至少 16 位的随机密钥（开发演示即可；生产用 openssl rand -hex 32 生成）
set SECRET_KEY=dev-only-animehub-0123456789        # Windows cmd
# $env:SECRET_KEY = "dev-only-animehub-0123456789" # Windows PowerShell
# export SECRET_KEY=$(openssl rand -hex 32)        # Linux / macOS

.venv\Scripts\python -m uvicorn app.main:app --reload --port 8000
```

生产环境请用 `openssl rand -hex 32` 生成强随机密钥，并保证进程重启前后一致（否则已签发 token 失效）。

首次启动会自动建表并写入动漫数据（数据库为空的场景）。

### 2. 导入 / 补全数据（可选）

```bash
cd backend
# 从 anime_data.json 批量导入（新增 + 更新）
.venv\Scripts\python -m scripts.import_anime

# 为缺失剧集的动漫生成可播放的剧集（幂等，可重复执行）
.venv\Scripts\python -m scripts.seed_episodes
```

### 3. 启动前端（Next.js，端口 3000）

```bash
cd frontend
npm install
# 首次使用先复制环境变量模板
copy .env.example .env.local    # Windows
# cp .env.example .env.local    # Linux / macOS
npm run dev
```

访问 http://localhost:3000

### 4. 生产构建验证

```bash
cd frontend
npm run build && npm run start
```

## ⚙️ 环境变量

### 后端（`backend/.env` 或进程环境）

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `ENVIRONMENT` | `development` | 运行环境：`development` / `staging` / `production`；生产模式会强制安全配置 |
| `DATABASE_URL` | `sqlite:///./animehub.db` | 数据库连接；**生产（staging/production）必须为 PostgreSQL**，SQLite 仅限开发 |
| `SECRET_KEY` | 无（缺失即拒绝启动） | JWT 签名密钥，**必填**且为 ≥16 位强随机串；使用空值或已知默认值会拒绝启动 |
| `ALLOWED_ORIGINS` | development: `*` | 允许的跨域来源，逗号分隔；**生产必填且禁止 `*`** |

> 安全守卫：`SECRET_KEY` 缺失/过短/为默认值时后端拒绝启动并给出明确提示；`ENVIRONMENT=production` 时要求 `DATABASE_URL` 为 PostgreSQL、`ALLOWED_ORIGINS` 显式列出真实域名。

### 前端（`frontend/.env.local`）

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `NEXT_PUBLIC_API_URL` | `http://127.0.0.1:8000` | 浏览器端请求的后端地址（同源走 `/api` 代理） |
| `NEXT_PUBLIC_SITE_URL` | `http://localhost:3000` | 站点对外地址，用于 SEO 规范链接 / Open Graph |

浏览器端请求统一走 Next.js 同源代理（`/api/[[...path]]`），绕开 CORS / 容器内主机名问题。

## 🐳 Docker 部署

```bash
docker compose up --build -d
```

- 前端： http://localhost:3000
- 后端： http://localhost:8000
- Docker 内部前端通过 `http://backend:8000` 访问后端 API

详细的生产部署（Nginx + systemd + 证书）见 **[DEPLOY.md](DEPLOY.md)**。

## 🔎 SEO 说明

- `GET /sitemap.xml` — 动态生成所有动漫详情的 sitemap
- `GET /robots.txt` — 允许抓取
- 每个详情页输出 Open Graph、Twitter Card、`application/ld+json` 结构化数据
- 全站语言：`zh-CN`，规范链接基于 `NEXT_PUBLIC_SITE_URL`

## ✅ 状态

- [x] 动漫列表 / 搜索 / 分类筛选 / 分页
- [x] 详情页（中文名、评分、标签、相关推荐、收藏 UI）
- [x] 在线播放页 + 剧集列表
- [x] 登录 / 注册 / 评论 / 评分 / 收藏 API
- [x] SEO（sitemap / robots / OG / JSON-LD）
- [x] 全站中文化、无广告占位
- [x] 数据导入与剧集种子
- [x] 生产构建通过、Docker / systemd 部署脚本
