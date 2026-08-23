from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import os

ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()

# 统一 SQLite 默认路径：基于 backend/ 目录的稳定绝对路径，
# 禁止 sqlite:///./animehub.db（相对路径会随 CWD 不同导致多库分裂）。
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DEFAULT_SQLITE = os.path.join(_BASE_DIR, "animehub.db").replace("\\", "/")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{_DEFAULT_SQLITE}").strip()


def _validate_database_url() -> None:
    """Production environments must use PostgreSQL; SQLite is dev-only."""
    if ENVIRONMENT in ("production", "staging") and not DATABASE_URL.startswith("postgresql"):
        raise RuntimeError(
            "DATABASE_URL must point to PostgreSQL in production/staging "
            f"(got: '{DATABASE_URL or 'unset'}').\n"
            "Example: postgresql+psycopg2://user:password@host:5432/animehub\n"
            "SQLite is only allowed in the development environment."
        )


_validate_database_url()

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def ensure_schema() -> None:
    """Lightweight migration: add missing columns to an existing DB
    without recreating tables (keeps existing data intact).
    Only supports SQLite and PostgreSQL.

    Stage 12-B: 幂等创建治理表（data_sources / external_entities /
    anime_field_sources）并 seed 数据源登记；不影响现有业务表。
    """
    # 幂等建表（IF NOT EXISTS）：包含 Stage 12-B 治理表
    Base.metadata.create_all(bind=engine)
    if DATABASE_URL.startswith("sqlite"):
        _ensure_sqlite_schema()
    elif DATABASE_URL.startswith("postgresql"):
        _ensure_postgres_schema()
    # Stage 12-B：数据源登记 seed（幂等）
    _seed_data_sources(engine)
    # Backfill SEO-critical fields for legacy rows (e.g. old seed data with
    # empty slug/seo_*). Idempotent: only fills missing values, never overwrites.
    _backfill_anime_seo_fields()


# Stage 12-B：数据源登记 seed（按 Stage 11 审计结果；仅登记，不代表全部可生产）
_SEED_SOURCES: list[tuple[str, str, str, str, str, int, int | None, str]] = [
    # (source_key, name, source_type, license, license_url, attribution, commercial_ok, status)
    ("wikidata", "Wikidata", "api", "CC0", "https://www.wikidata.org/wiki/Wikidata:Licensing", 0, 1, "active"),
    ("wikipedia", "Wikipedia", "api", "CC BY-SA 4.0", "https://en.wikipedia.org/wiki/Wikipedia:Reusing_Wikipedia_content", 1, 1, "active"),
    ("commons", "Wikimedia Commons", "api", "逐文件核实(CC0/CC BY/CC BY-SA/PD)", "https://commons.wikimedia.org/wiki/Commons:Licensing", 1, None, "active"),
    ("anilist", "AniList", "api", "未明确(当前 HTTP 403)", "https://github.com/AniList/ApiV2-GraphQL-Docs", 0, None, "paused"),
    ("mal", "MyAnimeList", "scrape", "未授权(登录墙未核实)", "", 0, 0, "excluded"),
    ("manual", "AnimeHub 人工维护", "manual", "自有", "", 0, 1, "active"),
]


def _seed_data_sources(engine) -> None:
    """幂等 seed data_sources（source_key UNIQUE 冲突时跳过）。"""
    if engine.dialect.name == "sqlite":
        sql = (
            "INSERT OR IGNORE INTO data_sources "
            "(source_key, name, source_type, license, license_url, attribution, commercial_ok, status) "
            "VALUES (:k, :n, :t, :l, :u, :a, :c, :s)"
        )
    else:
        sql = (
            "INSERT INTO data_sources "
            "(source_key, name, source_type, license, license_url, attribution, commercial_ok, status) "
            "VALUES (:k, :n, :t, :l, :u, :a, :c, :s) "
            "ON CONFLICT (source_key) DO NOTHING"
        )
    with engine.begin() as conn:
        for k, n, t, lic, url, att, comm, st in _SEED_SOURCES:
            conn.execute(
                text(sql),
                {"k": k, "n": n, "t": t, "l": lic, "u": url, "a": att, "c": comm, "s": st},
            )


def _ensure_sqlite_schema() -> None:
    insp = inspect(engine)
    if "anime" in insp.get_table_names():
        cols = {c["name"] for c in insp.get_columns("anime")}
        with engine.begin() as conn:
            if "chinese_title" not in cols:
                conn.execute(text("ALTER TABLE anime ADD COLUMN chinese_title TEXT DEFAULT ''"))
            if "year" not in cols:
                conn.execute(text("ALTER TABLE anime ADD COLUMN year INTEGER"))
            if "month" not in cols:
                conn.execute(text("ALTER TABLE anime ADD COLUMN month INTEGER"))
            if "tags" not in cols:
                conn.execute(text("ALTER TABLE anime ADD COLUMN tags TEXT DEFAULT ''"))
            if "region" not in cols:
                conn.execute(text("ALTER TABLE anime ADD COLUMN region TEXT DEFAULT ''"))
            if "author" not in cols:
                conn.execute(text("ALTER TABLE anime ADD COLUMN author TEXT DEFAULT ''"))
            if "studio" not in cols:
                conn.execute(text("ALTER TABLE anime ADD COLUMN studio TEXT DEFAULT ''"))
            if "status" not in cols:
                conn.execute(text("ALTER TABLE anime ADD COLUMN status TEXT DEFAULT ''"))
            if "letter" not in cols:
                conn.execute(text("ALTER TABLE anime ADD COLUMN letter TEXT DEFAULT ''"))
            if "episodes" not in cols:
                conn.execute(text("ALTER TABLE anime ADD COLUMN episodes INTEGER"))
            if "slug" not in cols:
                conn.execute(text("ALTER TABLE anime ADD COLUMN slug TEXT DEFAULT ''"))
            if "score" not in cols:
                conn.execute(text("ALTER TABLE anime ADD COLUMN score FLOAT DEFAULT 0.0"))
            if "anilist_id" not in cols:
                conn.execute(text("ALTER TABLE anime ADD COLUMN anilist_id INTEGER"))
            if "mal_id" not in cols:
                conn.execute(text("ALTER TABLE anime ADD COLUMN mal_id INTEGER"))
            # ALTER ADD COLUMN 不会自动建索引，手动补齐（与 models.py index=True 一致，幂等）
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_anime_anilist_id ON anime (anilist_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_anime_mal_id ON anime (mal_id)"))
            if "seo_title" not in cols:
                conn.execute(text("ALTER TABLE anime ADD COLUMN seo_title TEXT DEFAULT ''"))
            if "quality_score" not in cols:
                conn.execute(text("ALTER TABLE anime ADD COLUMN quality_score INTEGER DEFAULT 100"))
            if "is_indexable" not in cols:
                conn.execute(text("ALTER TABLE anime ADD COLUMN is_indexable INTEGER DEFAULT 1"))
            if "seo_description" not in cols:
                conn.execute(text("ALTER TABLE anime ADD COLUMN seo_description TEXT DEFAULT ''"))
            if "play_data" not in cols:
                conn.execute(text("ALTER TABLE anime ADD COLUMN play_data TEXT DEFAULT ''"))
            if "updated_at" not in cols:
                conn.execute(text("ALTER TABLE anime ADD COLUMN updated_at DATETIME"))
            if "episodes_list" not in [c for c in cols]:
                # episodes are stored in separate table, skip
                pass


def _ensure_postgres_schema() -> None:
    with engine.begin() as conn:
        res = conn.execute(
            text("SELECT column_name FROM information_schema.columns WHERE table_name='anime'")
        )
        cols = {row[0] for row in res.fetchall()}
        statements = []
        if "chinese_title" not in cols:
            statements.append("ALTER TABLE anime ADD COLUMN chinese_title TEXT DEFAULT ''")
        if "year" not in cols:
            statements.append("ALTER TABLE anime ADD COLUMN year INTEGER")
        if "month" not in cols:
            statements.append("ALTER TABLE anime ADD COLUMN month INTEGER")
        if "tags" not in cols:
            statements.append("ALTER TABLE anime ADD COLUMN tags TEXT DEFAULT ''")
        if "region" not in cols:
            statements.append("ALTER TABLE anime ADD COLUMN region TEXT DEFAULT ''")
        if "author" not in cols:
            statements.append("ALTER TABLE anime ADD COLUMN author TEXT DEFAULT ''")
        if "studio" not in cols:
            statements.append("ALTER TABLE anime ADD COLUMN studio TEXT DEFAULT ''")
        if "status" not in cols:
            statements.append("ALTER TABLE anime ADD COLUMN status TEXT DEFAULT ''")
        if "letter" not in cols:
            statements.append("ALTER TABLE anime ADD COLUMN letter TEXT DEFAULT ''")
        if "episodes" not in cols:
            statements.append("ALTER TABLE anime ADD COLUMN episodes INTEGER")
        if "slug" not in cols:
            statements.append("ALTER TABLE anime ADD COLUMN slug TEXT DEFAULT ''")
        if "score" not in cols:
            statements.append("ALTER TABLE anime ADD COLUMN score FLOAT DEFAULT 0.0")
        if "anilist_id" not in cols:
            statements.append("ALTER TABLE anime ADD COLUMN anilist_id INTEGER")
        if "mal_id" not in cols:
            statements.append("ALTER TABLE anime ADD COLUMN mal_id INTEGER")
        # ALTER ADD COLUMN 不会自动建索引，手动补齐（与 models.py index=True 一致，幂等）
        statements.append("CREATE INDEX IF NOT EXISTS ix_anime_anilist_id ON anime (anilist_id)")
        statements.append("CREATE INDEX IF NOT EXISTS ix_anime_mal_id ON anime (mal_id)")
        if "seo_title" not in cols:
            statements.append("ALTER TABLE anime ADD COLUMN seo_title TEXT DEFAULT ''")
        if "quality_score" not in cols:
            statements.append("ALTER TABLE anime ADD COLUMN quality_score INTEGER DEFAULT 100")
        if "is_indexable" not in cols:
            statements.append("ALTER TABLE anime ADD COLUMN is_indexable INTEGER DEFAULT 1")
        if "seo_description" not in cols:
            statements.append("ALTER TABLE anime ADD COLUMN seo_description TEXT DEFAULT ''")
        if "updated_at" not in cols:
            statements.append("ALTER TABLE anime ADD COLUMN updated_at TIMESTAMP")
        if "play_data" not in cols:
            statements.append("ALTER TABLE anime ADD COLUMN play_data TEXT DEFAULT ''")
        for stmt in statements:
            conn.execute(text(stmt))


def _backfill_anime_seo_fields() -> None:
    """Idempotent migration: fill missing slug/seo_title/seo_description/tags
    for existing rows (e.g. legacy seed data). Never overwrites already-set
    values, so re-running is safe in production."""
    # Lazy import to avoid circular imports and import-time coupling.
    from scripts.normalize import make_slug, _build_seo_description, build_auto_tags
    from .models import Anime

    insp = inspect(engine)
    if "anime" not in insp.get_table_names():
        return
    cols = {c["name"] for c in insp.get_columns("anime")}
    # Wait until the SEO columns have been added by the migrations above.
    if not {"slug", "seo_title", "seo_description", "tags"}.issubset(cols):
        return

    changed = False
    with SessionLocal() as db:
        # Snapshot already-used non-empty slugs so regenerated ones stay unique.
        used = {
            slug
            for (slug,) in db.execute(text("SELECT slug FROM anime WHERE slug IS NOT NULL AND slug <> ''")).fetchall()
        }

        rows = db.query(Anime).all()
        for a in rows:
            dirty = False

            if not (a.slug or "").strip():
                base = make_slug(a.chinese_title or a.title) or make_slug(a.title) or f"anime-{a.id}"
                slug = base
                n = 2
                while slug.lower() in used:
                    slug = f"{base}-{n}"
                    n += 1
                a.slug = slug
                used.add(slug.lower())
                dirty = True

            if not (a.seo_title or "").strip():
                a.seo_title = f"{(a.chinese_title or a.title)} - 在线观看 - AnimeHub"
                dirty = True

            if not (a.seo_description or "").strip():
                desc = _build_seo_description(a.chinese_title or a.title, a.__dict__)
                if desc:
                    a.seo_description = desc
                    dirty = True

            if not (a.tags or "").strip():
                a.tags = build_auto_tags(a.__dict__)
                dirty = True

            if dirty:
                changed = True

        if changed:
            db.commit()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
