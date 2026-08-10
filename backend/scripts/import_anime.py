"""Bulk import anime from anime_data.json into the SQLite database.

Usage (from the backend directory):
    .venv\\Scripts\\python -m scripts.import_anime
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from app.database import SessionLocal, ensure_schema  # noqa: E402
from app.models import Anime  # noqa: E402

DATA_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "anime_data.json",
)


def main() -> None:
    if not os.path.exists(DATA_FILE):
        print(f"[error] data file not found: {DATA_FILE}")
        sys.exit(1)

    with open(DATA_FILE, encoding="utf-8") as f:
        items = json.load(f)

    # Make sure the existing database has the `year` column before inserting.
    ensure_schema()

    db = SessionLocal()
    start = time.time()
    try:
        existing = {t.strip() for (t,) in db.query(Anime.title).all()}
        added = 0
        skipped = 0
        for it in items:
            title = (it.get("title") or "").strip()
            if not title or title in existing:
                skipped += 1
                continue
            db.add(
                Anime(
                    title=title,
                    description=it.get("description", "") or "",
                    genre=it.get("genre", "") or "",
                    year=it.get("year"),
                    score=float(it.get("score") or 0.0),
                    cover=it.get("cover", "") or "",
                )
            )
            existing.add(title)
            added += 1
        db.commit()
        total = db.query(Anime).count()
        elapsed = time.time() - start
        print(
            f"Imported: {added}  Skipped(duplicates/invalid): {skipped}  "
            f"Total anime in DB: {total}  Time: {elapsed:.3f}s"
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()