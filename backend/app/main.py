import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import anime, comments, favorites, users
from .database import DATABASE_URL, ENVIRONMENT, SessionLocal, Base, engine, ensure_schema
from .models import Anime
from .seed import seed_anime

# 部署版本标识：优先读环境变量（Docker build arg / compose 注入），
# 便于线上快速确认运行的是哪个版本、何时构建。
APP_VERSION = os.getenv("APP_VERSION", "1.7.0").strip()
APP_BUILD_TIME = os.getenv("APP_BUILD_TIME", "").strip()

# Create tables (new DBs) + migrate existing DBs (add missing columns)
Base.metadata.create_all(bind=engine)
ensure_schema()
seed_anime()

# 启动时输出数据库路径与动漫数量（避免多库分裂、便于定位线上版本）
try:
    with SessionLocal() as db:
        _anime_count = db.query(Anime).count()
except Exception:
    _anime_count = -1
print("=== AnimeHub 启动信息 ===")
print(f"Database: {DATABASE_URL}")
print(f"Anime count: {_anime_count}")
print(f"Environment: {ENVIRONMENT}")
print("========================")

app = FastAPI(title="AnimeHub API", version="1.0.0")


def _build_allowed_origins() -> list[str]:
    """CORS origins.

    - development: open CORS by default (ALLOWED_ORIGINS overridable).
    - production/staging: explicit, non-wildcard origins are REQUIRED.
    """
    allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "").strip()

    if ENVIRONMENT in ("production", "staging"):
        if not allowed_origins_env:
            raise RuntimeError(
                "ALLOWED_ORIGINS environment variable is required in production/staging.\n"
                "Provide comma-separated real origins, e.g.\n"
                "  ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com\n"
                "Refusing to start with open CORS."
            )
        origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]
        if not origins or "*" in origins:
            raise RuntimeError(
                "ALLOWED_ORIGINS with a wildcard '*' (or an empty list) is not allowed "
                "in production/staging. List your real origins explicitly."
            )
        return origins

    # development default: open CORS unless explicitly configured
    if not allowed_origins_env:
        return ["*"]
    return [o.strip() for o in allowed_origins_env.split(",") if o.strip()]


# CORS configuration
# In production, set ALLOWED_ORIGINS environment variable (comma-separated)
# Example: ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com
allow_origins = _build_allowed_origins()

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(anime.router)
app.include_router(comments.router)
app.include_router(favorites.router)


@app.get("/")
def root():
    return {"service": "AnimeHub", "status": "running"}


@app.get("/health")
def health():
    """Lightweight health endpoint used by Docker compose healthchecks."""
    return {"status": "ok"}


@app.get("/api/version")
def api_version():
    """部署版本标识：backend_version + build_time + environment，用于线上快速确认版本。"""
    return {
        "backend_version": APP_VERSION,
        "build_time": APP_BUILD_TIME or "unknown",
        "environment": ENVIRONMENT,
    }

