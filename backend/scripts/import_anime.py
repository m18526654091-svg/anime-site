"""Bulk import anime from anime_data.json into the SQLite database.

Usage (from the backend directory):
    .venv\\Scripts\\python -m scripts.import_anime
"""
import json
import os
import sys
import time
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from app.database import Base, SessionLocal, engine, ensure_schema  # noqa: E402
from app.models import Anime  # noqa: E402
from scripts.normalize import is_placeholder_cover, normalize_item  # noqa: E402

DATA_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "anime_data.json",
)

# Batch commit size: keep transactions small when importing 1000+ rows.
BATCH_SIZE = 500


def validate_item(index: int, item: dict[str, Any]) -> str | None:
    """Validate a single anime item. Returns error message or None if valid.

    cover 不强制：缺失封面由前端渐变占位兜底，随后可用
    fetch_missing_covers 补真实封面（不要因缺 cover 跳过数据）。
    """
    title = (item.get("title") or "").strip()
    genre = (item.get("genre") or "").strip()

    if not title:
        return f"[row {index}] missing title"
    if not genre:
        return f"[row {index}] missing genre for '{title}'"

    return None


def _unique_slug(base: str, used_slugs: set[str]) -> str:
    """Return a slug that does not collide with slugs already in the DB.

    Base comes from normalize.make_slug so it is stable across imports;
    collisions (same slug for a different anime) get `-2`/`-3` suffix.
    """
    candidate = (base or "").strip() or "anime"
    if candidate not in used_slugs:
        return candidate
    n = 2
    while f"{candidate}-{n}" in used_slugs:
        n += 1
    return f"{candidate}-{n}"


def main() -> None:
    if not os.path.exists(DATA_FILE):
        print(f"[error] data file not found: {DATA_FILE}")
        sys.exit(1)

    with open(DATA_FILE, encoding="utf-8") as f:
        items = json.load(f)

    # Make sure the existing database has all columns before inserting
    # (creates fresh tables on a brand-new DB, migrates existing ones).
    Base.metadata.create_all(bind=engine)
    ensure_schema()

    db = SessionLocal()
    start = time.time()
    try:
        # Load existing rows ONCE and index them to avoid N+1 queries on
        # every row of a large import (scales to 10k+ rows).
        existing_rows = (
            db.query(Anime.id, Anime.slug, Anime.title, Anime.chinese_title).all()
        )
        # slug -> lowest id (canonical record)
        by_slug: dict[str, int] = {}
        by_title: dict[str, int] = {}
        by_chinese: dict[str, int] = {}
        used_slugs: set[str] = set()
        for rid, rslug, rtitle, rchinese in existing_rows:
            if rslug:
                used_slugs.add(rslug)
                by_slug.setdefault(rslug.lower(), rid)
            if rtitle:
                by_title.setdefault(rtitle.strip(), rid)
            if rchinese:
                by_chinese.setdefault(rchinese.strip(), rid)

        added = 0
        updated = 0
        skipped = 0
        errors: list[str] = []
        batch = 0

        for idx, it in enumerate(items, start=1):
            # Validate required fields
            error = validate_item(idx, it)
            if error:
                errors.append(error)
                skipped += 1
                continue

            # Normalize / auto-generate SEO fields (keeps existing values).
            item = normalize_item(it)

            # ----- Dedup: slug > title > chinese_title -----
            slug = (item.get("slug") or "").strip()
            title = (item.get("title") or "").strip()
            chinese_title = (item.get("chinese_title") or "").strip()

            match_id: int | None = None
            if slug:
                match_id = by_slug.get(slug.lower())
            if match_id is None and title:
                match_id = by_title.get(title)
            if match_id is None and chinese_title:
                match_id = by_chinese.get(chinese_title)

            if match_id is not None:
                anime = db.get(Anime, match_id)
                if anime is None:
                    # Defensive: stale index, treat as new.
                    match_id = None
                else:
                    # Upgrade: ensure slug exists on this row if empty.
                    if not anime.slug and slug and slug.lower() not in by_slug:
                        anime.slug = slug
                    # SEO fields: only fill when empty (never overwrite).
                    if not anime.seo_title and item.get("seo_title"):
                        anime.seo_title = item["seo_title"]
                    if not anime.seo_description and item.get("seo_description"):
                        anime.seo_description = item["seo_description"]
                    if not anime.tags and item.get("tags"):
                        anime.tags = item["tags"]
                    # Data refresh. Cover: only overwrite when the source is a
                    # REAL image URL. Placeholder URLs (e.g. placehold.co) never
                    # overwrite an existing real cover, keeping curated artwork.
                    new_cover = (item.get("cover") or "").strip()
                    if not is_placeholder_cover(new_cover):
                        anime.cover = new_cover
                    anime.description = (item.get("description") or "").strip()
                    anime.chinese_title = (item.get("chinese_title") or "").strip()
                    anime.genre = (item.get("genre") or "").strip()
                    anime.year = item.get("year")
                    anime.region = (item.get("region") or "").strip()
                    anime.author = (item.get("author") or "").strip()
                    anime.studio = (item.get("studio") or "").strip()
                    anime.status = (item.get("status") or "").strip()
                    anime.episodes = item.get("episodes")
                    anime.score = float(item.get("score") or 0.0)
                    by_title[title] = match_id
                    updated += 1
            else:
                # ----- New anime -----
                final_slug = _unique_slug(slug, used_slugs)
                payload = {
                    key: item.get(key)
                    for key in (
                        "title",
                        "chinese_title",
                        "cover",
                        "description",
                        "genre",
                        "tags",
                        "year",
                        "region",
                        "author",
                        "studio",
                        "status",
                        "episodes",
                        "score",
                        "seo_title",
                        "seo_description",
                    )
                }
                payload["slug"] = final_slug
                # Never store placeholder cover URLs in the DB: if the source is
                # a placeholder, keep cover empty so the frontend renders its
                # built-in gradient placeholder instead of a broken image.
                src_cover = (payload.get("cover") or "").strip()
                payload["cover"] = "" if is_placeholder_cover(src_cover) else src_cover
                db.add(Anime(**payload))

                # Update in-memory indexes so later rows in this same file
                # with the same slug map back to this new record.
                used_slugs.add(final_slug)
                if slug:
                    by_slug.setdefault(final_slug.lower(), -1)  # placeholder
                by_title[title] = -1
                if chinese_title:
                    by_chinese.setdefault(chinese_title, -1)
                added += 1

            batch += 1
            if batch % BATCH_SIZE == 0:
                db.commit()

        db.commit()
        total = db.query(Anime).count()
        elapsed = time.time() - start

        print(
            f"Imported: {added}  Updated: {updated}  Skipped: {skipped}  "
            f"Total anime in DB: {total}  Time: {elapsed:.3f}s"
        )

        if errors:
            print("\nValidation errors:")
            for err in errors[:20]:  # Show first 20 errors
                print(f"  {err}")
            if len(errors) > 20:
                print(f"  ... and {len(errors) - 20} more errors")
    finally:
        db.close()


if __name__ == "__main__":
    main()