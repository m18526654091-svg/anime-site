"""Phase 35 Step 6: localization backfill for existing anime with anilist_id (batch mode).
Fetches AniList titles in batches of 50 (Page id_in) and fills
japanese_title/romaji_title/aliases for existing DB rows.
Usage: python scripts/backfill_localized_titles.py [--dry-run] [--limit N]
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from app.database import Base, engine, SessionLocal  # noqa: E402
from app.models import Anime  # noqa: E402
from scripts.import_characters_anilist import gql  # noqa: E402

BATCH = 50


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--limit', type=int, default=0)
    args = ap.parse_args()

    Base.metadata.create_all(engine)
    db = SessionLocal()
    rows = [a for a in db.query(Anime).filter(Anime.anilist_id.isnot(None)).all()
            if not (getattr(a, 'romaji_title', None) and getattr(a, 'japanese_title', None))]
    if args.limit:
        rows = rows[:args.limit]
    print('[backfill] rows to backfill: %d | %s' % (len(rows), 'DRY-RUN' if args.dry_run else ''))

    by_id = {}
    for a in rows:
        by_id[int(a.anilist_id)] = a
    ids = list(by_id.keys())

    updated = 0
    failed = 0
    for start in range(0, len(ids), BATCH):
        chunk = ids[start:start + BATCH]
        try:
            q = ('query { Page(perPage: 50) { media(id_in: %s, type: ANIME) { '
                 'id title { romaji english native } } } }' % json.dumps(chunk))
            d = gql(q)
        except Exception as e:
            failed += len(chunk)
            print('  [err] batch %d: %s' % (start // BATCH, str(e)[:100]))
            continue
        medias = (d or {}).get('data', {}).get('Page', {}).get('media') or []
        for m in medias:
            a = by_id.get(m.get('id'))
            if not a:
                continue
            t = m.get('title') or {}
            romaji = (t.get('romaji') or '').strip()
            english = (t.get('english') or '').strip()
            native = (t.get('native') or '').strip()
            title = (a.title or '').strip()
            aliases = json.dumps(
                [x for x in dict.fromkeys(filter(None, [english, romaji, native])) if x != title],
                ensure_ascii=False,
            )
            if args.dry_run:
                updated += 1
                continue
            if getattr(a, 'romaji_title', None) is None or not a.romaji_title:
                a.romaji_title = romaji
            if getattr(a, 'japanese_title', None) is None or not a.japanese_title:
                a.japanese_title = native
            if getattr(a, 'aliases', None) is None or not a.aliases:
                a.aliases = aliases
            updated += 1
        time.sleep(1.0)
    if not args.dry_run:
        db.commit()
    print('[done] updated=%d failed=%d' % (updated, failed))


if __name__ == '__main__':
    main()
