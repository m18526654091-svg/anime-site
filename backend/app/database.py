from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./animehub.db")

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


def _ensure_sqlite_schema() -> None:
    insp = inspect(engine)
    if "anime" in insp.get_table_names():
        cols = {c["name"] for c in insp.get_columns("anime")}
        with engine.begin() as conn:
            if "year" not in cols:
                conn.execute(text("ALTER TABLE anime ADD COLUMN year INTEGER"))
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
            if "episodes" not in cols:
                conn.execute(text("ALTER TABLE anime ADD COLUMN episodes INTEGER"))
            if "score" not in cols:
                conn.execute(text("ALTER TABLE anime ADD COLUMN score FLOAT DEFAULT 0.0"))
            if "seo_title" not in cols:
                conn.execute(text("ALTER TABLE anime ADD COLUMN seo_title TEXT DEFAULT ''"))
                        if "seo_description" not in cols:
                conn.execute(text("ALTER TABLE anime ADD COLUMN seo_description TEXT DEFAULT ''"))
            if "play_data" not in cols:
                conn.execute(text("ALTER TABLE anime ADD COLUMN play_data TEXT DEFAULT ''"))
            if "updated_at" not in cols:
                conn.execute(text("ALTER TABLE anime ADD COLUMN updated_at DATETIME"))


def _ensure_postgres_schema() -> None:
    with engine.begin() as conn:
        res = conn.execute(
            text("SELECT column_name FROM information_schema.columns WHERE table_name='anime'")
        )
        cols = {row[0] for row in res.fetchall()}
        statements = []
        if "year" not in cols:
            statements.append("ALTER TABLE anime ADD COLUMN year INTEGER")
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
        if "episodes" not in cols:
            statements.append("ALTER TABLE anime ADD COLUMN episodes INTEGER")
        if "score" not in cols:
            statements.append("ALTER TABLE anime ADD COLUMN score FLOAT DEFAULT 0.0")
        if "seo_title" not in cols:
            statements.append("ALTER TABLE anime ADD COLUMN seo_title TEXT DEFAULT ''")
        if "seo_description" not in cols:
            statements.append("ALTER TABLE anime ADD COLUMN seo_description TEXT DEFAULT ''")
        if "updated_at" not in cols:
            statements.append("ALTER TABLE anime ADD COLUMN updated_at TIMESTAMP")
        for stmt in statements:
            conn.execute(text(stmt))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
