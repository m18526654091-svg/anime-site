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
    Only supports SQLite and PostgreSQL."""
    if DATABASE_URL.startswith("sqlite"):
        _ensure_sqlite_schema()
    elif DATABASE_URL.startswith("postgresql"):
        _ensure_postgres_schema()
    # Backfill SEO-critical fields for legacy rows (e.g. old seed data with
    # empty slug/seo_*). Idempotent: only fills missing values, never overwrites.
    _backfill_anime_seo_fields()


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
