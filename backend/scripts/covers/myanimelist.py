"""MyAnimeList 封面源（本地静态映射，离线兜底）。

内置一批已验证的真实 MAL CDN 海报 URL。仅作为离线兜底 / 种子；
要大规模补齐真实封面，请启用 anilist.py（联网按标题搜索）。
"""
from __future__ import annotations

from typing import Optional

from .base import CoverProvider

# key -> 真实 MAL 海报 URL（key 用英文/中文均可，匹配时转小写模糊匹配）
_MAL_MAP: dict[str, str] = {
    # 已验证的真实 URL（来自种子数据，校验通过）
    "attack on titan": "https://cdn.myanimelist.net/images/anime/10/47347.jpg",
    "进击的巨人": "https://cdn.myanimelist.net/images/anime/10/47347.jpg",
    "demon slayer": "https://cdn.myanimelist.net/images/anime/1286/99889.jpg",
    "鬼灭之刃": "https://cdn.myanimelist.net/images/anime/1286/99889.jpg",
    "one piece": "https://cdn.myanimelist.net/images/anime/6/73245.jpg",
    "海贼王": "https://cdn.myanimelist.net/images/anime/6/73245.jpg",
    "naruto": "https://cdn.myanimelist.net/images/anime/13/17405.jpg",
    "火影忍者": "https://cdn.myanimelist.net/images/anime/13/17405.jpg",
    "spy x family": "https://cdn.myanimelist.net/images/anime/1441/122795.jpg",
    "间谍过家家": "https://cdn.myanimelist.net/images/anime/1441/122795.jpg",
    "frieren": "https://cdn.myanimelist.net/images/anime/1819/126736.jpg",
    "葬送的芙莉莲": "https://cdn.myanimelist.net/images/anime/1819/126736.jpg",
    # 注意：咒术回战/孤独摇滚/我推的孩子/电锯人 的 MAL 海报 ID 已失效，
    # 不再放入静态表，统一交给 data/covers_mapping.json（Wikipedia 真实图）处理。
}


class MyAnimeListStaticProvider(CoverProvider):
    priority = 5

    def _lookup(self, text: str) -> Optional[str]:
        t = (text or "").strip().lower()
        if not t:
            return None
        # 精确小写匹配优先，其次包含匹配（防止标题带后缀）
        if t in _MAL_MAP:
            return _MAL_MAP[t]
        for key, url in _MAL_MAP.items():
            if key in t or t in key:
                return url
        return None

    def resolve(self, title, chinese_title="", year=None):
        return self._lookup(title) or self._lookup(chinese_title) or None