"""Seed episodes for anime that have none, so the playback page actually works.

Each episode gets a real, publicly-hosted sample MP4 (CORS-friendly) so the
<video> element in /watch/[id] can stream out of the box. Idempotent: anime
that already have episodes are left untouched.

Usage (from the backend directory):
    .venv\\Scripts\\python -m scripts.seed_episodes
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from app.database import SessionLocal  # noqa: E402
from app.models import Anime, Episode  # noqa: E402

# Real, public sample videos (Google GTV bucket) that support direct streaming
# and cross-origin playback. Rotated across episodes.
SAMPLE_URLS = [
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4",
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyrides.mp4",
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerMeltdowns.mp4",
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4",
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/SubaruOutbackOnStreetAndDirt.mp4",
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4",
]

DEFAULT_EPISODES = 8  # used when an anime has no declared episode count
MAX_EPISODES = 48  # safety cap


def episode_count_for(anime: Anime) -> int:
    declared = anime.episodes
    if declared and declared > 0:
        return min(int(declared), MAX_EPISODES)
    return DEFAULT_EPISODES


def normalize_legacy_urls(db) -> int:
    """Replace legacy placeholder URLs (example.com) with real sample videos."""
    fixed = 0
    for ep in db.query(Episode).filter(Episode.video_url.contains("example.com")).all():
        ep.video_url = SAMPLE_URLS[(ep.episode_number - 1) % len(SAMPLE_URLS)]
        fixed += 1
    return fixed


def main() -> None:
    db = SessionLocal()
    try:
        # Replace legacy placeholder URLs (e.g. example.com) with real samples.
        legacy_fixed = normalize_legacy_urls(db)

        # anime that already have at least one episode
        seeded_ids = {
            e for (e,) in db.query(Episode.anime_id).distinct().all()
        }
        targets = db.query(Anime).order_by(Anime.id.asc()).all()
        seeds = [a for a in targets if a.id not in seeded_ids]

        if not seeds:
            print(f"No anime missing episodes. Legacy URLs fixed: {legacy_fixed}")
            db.commit()
            return

        created = 0
        for anime in seeds:
            count = episode_count_for(anime)
            for n in range(1, count + 1):
                url = SAMPLE_URLS[(n - 1) % len(SAMPLE_URLS)]
                db.add(
                    Episode(
                        anime_id=anime.id,
                        episode_number=n,
                        title=f"第{n}集",
                        video_url=url,
                    )
                )
                created += 1

        db.commit()
        total_episodes = db.query(Episode).count()
        total_anime = db.query(Anime).count()
        print(f"Seeded episodes for {len(seeds)} anime. Legacy URLs fixed: {legacy_fixed}")
        print(f"Created: {created}  Total episodes in DB: {total_episodes}  Anime: {total_anime}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
