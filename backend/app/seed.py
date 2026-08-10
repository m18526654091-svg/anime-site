"""Seed the database with sample anime when empty."""

import json
from pathlib import Path
from .database import SessionLocal
from .models import Anime

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


def _build_play_data(episode_count: int = 12) -> str:
    """Generate placeholder play data (3 lines, test episodes) as JSON string."""
    lines = [
        {
            "name": "线路1",
            "episodes": [
                {"ep": e, "title": f"第{e}集", "url": f"https://example.com/play/{e}"}
                for e in range(1, episode_count + 1)
            ],
        },
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
                payload = dict(item)
                payload.setdefault("play_data", _build_play_data())
                db.add(Anime(**payload))
            db.commit()
    finally:
        db.close()
