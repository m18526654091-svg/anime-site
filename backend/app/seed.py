"""Seed the database with sample anime when empty."""

import json
from pathlib import Path
from .database import SessionLocal
from .models import Anime, Episode
from scripts.normalize import normalize_item

SAMPLE_ANIME = [
    {
        "title": "进击的巨人",
        "genre": "动作/奇幻",
        "score": 9.0,
        "cover": "",
        "description": "人类在巨人的威胁下筑起高墙生存，艾伦为了夺回自由而战。",
    },
    {
        "title": "鬼灭之刃",
        "genre": "热血/奇幻",
        "score": 8.8,
        "cover": "",
        "description": "少年炭治郎为拯救变成鬼的妹妹，加入鬼杀队踏上斩鬼之旅。",
    },
    {
        "title": "海贼王",
        "genre": "冒险/热血",
        "score": 9.2,
        "cover": "",
        "description": "路飞与伙伴们追寻传说中的大秘宝，展开伟大航路的冒险。",
    },
]


# Real, public sample videos (Google GTV bucket) so fresh installs can play
# videos out of the box. Rotated across episodes.
SAMPLE_EPISODE_URLS = [
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


def _build_play_data(episode_count: int = 12) -> str:
    """Generate placeholder play data (3 lines, empty episodes) as JSON string.

    Playback is handled via Episode.video_url on the /watch/[id] page,
    so play_data no longer contains placeholder/example.com URLs.
    """
    lines = [
        {"name": "线路1", "episodes": []},
        {"name": "线路2", "episodes": []},
        {"name": "线路3", "episodes": []},
    ]
    return json.dumps({"lines": lines}, ensure_ascii=False)


def seed_anime() -> None:
    db = SessionLocal()
    try:
        if db.query(Anime).count() == 0:
            data_path = Path(__file__).resolve().parent.parent.parent / "anime_data.json"
            if data_path.exists():
                raw = data_path.read_text(encoding="utf-8")
                items = json.loads(raw)
            else:
                items = SAMPLE_ANIME
            for item in items:
                # 复用 normalize_item：补齐 slug / seo_title / seo_description / tags，
                # 与 import_anime.py 的 SEO 生成规则完全一致。
                payload = normalize_item(item)
                # normalize 可能把 play_data 归为 ""，此时才用 seed 的默认播放数据。
                if not payload.get("play_data"):
                    payload["play_data"] = _build_play_data()
                db.add(Anime(**payload))
            db.commit()

            # Seed episodes for the freshly created anime so playback works
            # immediately on a brand-new environment.
            for anime in db.query(Anime).order_by(Anime.id.asc()).all():
                declared = anime.episodes or 0
                count = min(max(int(declared), 1), 48) if declared > 0 else 8
                for n in range(1, count + 1):
                    db.add(
                        Episode(
                            anime_id=anime.id,
                            episode_number=n,
                            title=f"第{n}集",
                            video_url=SAMPLE_EPISODE_URLS[(n - 1) % len(SAMPLE_EPISODE_URLS)],
                        )
                    )
            db.commit()
    finally:
        db.close()
