"""MyAnimeList 封面源（搜索页抓取）。

通过 myanimelist.net 搜索页抓取第一条结果的海报。MAL 拥有最完整的番组库，
适配中文名 / 罗马字名均可命中。抓取的是搜索结果列表的第一张图。
"""
from __future__ import annotations

import re
import time
import urllib.parse
import urllib.request
from typing import Optional

from .base import CoverProvider

SEARCH_URL = "https://myanimelist.net/anime.php?q={q}&cat=anime"
_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
    "Accept": "text/html",
}

# 匹配搜索结果项中的缩略图（含 r/50x70/ 缩放前缀） -> 提取真实 id 对
_IMG_RE = re.compile(
    r'data-src="https://cdn\.myanimelist\.net/[^"]*?/images/anime/(\d+)/(\d+)\.jpg'
)


class MyAnimeListSearchProvider(CoverProvider):
    """搜索 myanimelist.net，取第 1 个结果的封面。"""

    priority = 9

    def __init__(self, timeout: int = 10, delay: float = 0.35) -> None:
        self.timeout = timeout
        self.delay = delay

    def _search_cover(self, query: str) -> Optional[str]:
        if not query or not query.strip():
            return None
        url = SEARCH_URL.format(q=urllib.parse.quote(query.strip()))
        try:
            req = urllib.request.Request(url, headers=_HEADERS)
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                html = resp.read().decode("utf-8", "ignore")
        except Exception:
            return None
        m = _IMG_RE.search(html)
        if not m:
            return None
        # 将缩略图 URL 还原为原图（去掉 r/WxH/ 前缀）
        return f"https://cdn.myanimelist.net/images/anime/{m.group(1)}/{m.group(2)}.jpg"

    def resolve(self, title: str, chinese_title: str = "", year: Optional[int] = None):
        candidates = []
        for c in (chinese_title, title):
            c = (c or "").strip()
            if c and c not in candidates:
                candidates.append(c)
        for cand in candidates:
            url = self._search_cover(cand)
            if url:
                return url
            time.sleep(self.delay)
        return None
