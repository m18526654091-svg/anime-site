# AnimeHub 部署指南

本文档提供 AnimeHub 项目的完整部署步骤和配置说明。

## 目录

- [环境要求](#环境要求)
- [安装步骤](#安装步骤)
- [环境变量配置](#环境变量配置)
- [数据导入步骤](#数据导入步骤)
- [启动命令](#启动命令)
- [常见问题](#常见问题)
- [生产环境检查清单](#生产环境检查清单)

---

## 环境要求

### 系统要求
- **操作系统**: Linux (Ubuntu 20.04+ / Debian 11+)
- **Python**: 3.10+
- **Node.js**: 18+ (推荐 20 LTS)
- **npm**: 9+
- **内存**: 最低 1GB，推荐 2GB+
- **存储**: 最低 5GB 可用空间

### 可选组件
- **PostgreSQL**: 14+ (如果使用 PostgreSQL 替代 SQLite)
- **Docker**: 20+ (如果使用 Docker 部署)
- **Docker Compose**: 2+ (如果使用 Docker 部署)

---

## 安装步骤

### 方式一：Docker 部署（推荐）

#### 1. 克隆代码
```bash
git clone <your-repo-url> /home/animehub
cd /home/animehub
```

#### 2. 配置环境变量
```bash
cp frontend/.env.example frontend/.env.local
nano frontend/.env.local
```

#### 3. 修改 docker-compose.yml
```bash
nano docker-compose.yml
```

需要修改的配置：
```yaml
services:
  frontend:
    environment:
      NEXT_PUBLIC_SITE_URL: https://your-domain.com  # 修改为你的域名
```

#### 4. 启动服务
```bash
docker-compose up -d
```

#### 5. 导入数据
```bash
docker-compose exec backend python -m scripts.import_anime
python -m scripts.seed_episodes
```

---

### 方式二：手动部署

#### 1. 克隆代码
```bash
git clone <your-repo-url> /home/animehub
cd /home/animehub
```

#### 2. 安装系统依赖
```bash
apt update
apt install -y python3 python3-venv python3-pip nodejs npm
```

#### 3. 配置后端
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### 4. 配置前端
```bash
cd ../frontend
cp .env.example .env.local
nano .env.local
```

#### 5. 构建前端
```bash
npm install
npm run build
```

---

## 环境变量配置

### 前端环境变量 (.env.local)

#### 必需变量
```env
NEXT_PUBLIC_SITE_URL=https://your-domain.com
NEXT_PUBLIC_API_URL=http://localhost:8000
```

#### 说明
- `NEXT_PUBLIC_SITE_URL`: 必须设置为实际域名（包括 https://）
- `NEXT_PUBLIC_API_URL`:
  - 开发环境：`http://localhost:8000`
  - Docker 环境：`http://backend:8000`
  - 生产环境：`http://localhost:8000`

---

## 数据导入步骤

### 自动导入
后端启动时会自动导入 anime_data.json 中的数据。

### 手动导入
```bash
cd backend
python -m scripts.import_anime
python -m scripts.seed_episodes
```

### 导入日志示例
```
Imported: 0  Updated: 120  Skipped: 0  
Total anime in DB: 120  Time: 0.034s
```

---

## 启动命令

### Docker 部署
```bash
docker-compose up -d
docker-compose logs -f
```

### 手动部署 - 后端
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 手动部署 - 前端
```bash
cd frontend
npm start
```

---

## 常见问题

### 1. 数据库迁移失败
```bash
cd backend
python -c "from app.database import ensure_schema; ensure_schema()"
```

### 2. JWT 签名错误
- 确保 SECRET_KEY 环境变量已设置
- 确保前后端使用相同的 SECRET_KEY
- 重启后端服务

### 3. CORS 错误
```bash
export ALLOWED_ORIGINS="https://your-domain.com"
```

### 4. 图片加载失败
- 检查 cover URL 是否有效
- 确保服务器可以访问外网

### 5. 构建失败
```bash
rm -rf .next node_modules
npm install
npm run build
```

---
## 生产环境检查清单

### 部署前检查

- [ ] **环境变量**
  - [ ] `NEXT_PUBLIC_SITE_URL` 已设置为实际域名
  - [ ] `SECRET_KEY` 已设置为强随机字符串
  - [ ] `DATABASE_URL` 已配置
  - [ ] `ALLOWED_ORIGINS` 已配置为生产域名

- [ ] **数据库**
  - [ ] 数据库文件已备份
  - [ ] 数据库迁移已执行
  - [ ] 数据已导入

- [ ] **前端构建**
  - [ ] `npm run build` 成功
  - [ ] 无 TypeScript 错误

- [ ] **后端配置**
  - [ ] API 健康检查通过
  - [ ] 数据库连接正常

- [ ] **SEO 配置**
  - [ ] `robots.txt` 可访问
  - [ ] `sitemap.xml` 可访问
  - [ ] `og-image.png` 已替换

- [ ] **安全配置**
  - [ ] `SECRET_KEY` 不是默认值
  - [ ] CORS 配置了具体域名
  - [ ] 防火墙已配置
  - [ ] HTTPS 已配置

---

## 快速部署命令

### Docker 一键部署
```bash
cd /home/animehub
cp frontend/.env.example frontend/.env.local
# 编辑 .env.local
docker-compose up -d
docker-compose exec backend python -m scripts.import_anime
python -m scripts.seed_episodes
```

### 手动部署
```bash
cd /home/animehub
bash deploy.sh
```

---

## 更新日志

- **v1.5** (2026-08-12)
  - 完善部署文档
  - 优化环境变量配置
  - 修复 CORS 配置
  - 修复 SECRET_KEY 配置
