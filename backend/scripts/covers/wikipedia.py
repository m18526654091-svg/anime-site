"""Wikipedia 中文封面源（公开、稳定、无需 Key）。

通过 zh.wikipedia REST API 按中文条目标题取图；若 summary 无图（常见于
存在同名消歧义页或图片位于条目页时），改用条目页 meta og:image 作为回退。
返回 upload.wikimedia.org 的真实图片 URL（清洗掉 API/页面附加的 UTM 参数）。
"""
from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from typing import Optional

from .base import CoverProvider

SUMMARY_URL = "https://zh.wikipedia.org/api/rest_v1/page/summary/{title}"
ARTICLE_URL = "https://zh.wikipedia.org/wiki/{title}"
_HEADERS = {
    "User-Agent": "AnimeHub-Importer/1.0 (SEO content pipeline; contact: admin@animehub.local)",
    "Accept": "application/json",
}
_BROWSER = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"}
_OG_RE = re.compile(r'<meta property="og:image" content="([^"]+)"')


def _clean(src: str) -> str:
    """去掉 wikimedia 地址附带的 UTM 参数。"""
    if not src:
        return ""
    return src.split("?", 1)[0]


class WikipediaZhProvider(CoverProvider):
    priority = 8

    def __init__(self, timeout: int = 10) -> None:
        self.timeout = timeout

    def _summary_image(self, title: str) -> Optional[str]:
        url = SUMMARY_URL.format(title=urllib.parse.quote(title))
        try:
            req = urllib.request.Request(url, headers=_HEADERS)
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except Exception:
            return None
        if not isinstance(data, dict) or data.get("type") == "disambiguation":
            return None
        original = ((data.get("originalimage") or {}) or {}).get("source") or ""
        thumbnail = ((data.get("thumbnail") or {}) or {}).get("source") or ""
        return _clean(original or thumbnail)

    def _og_image(self, title: str) -> Optional[str]:
        url = ARTICLE_URL.format(title=urllib.parse.quote(title))
        try:
            req = urllib.request.Request(url, headers=_BROWSER)
            html = urllib.request.urlopen(req, timeout=self.timeout).read().decode("utf-8", "ignore")
        except Exception:
            return None
        m = _OG_RE.search(html)
        if not m:
            return None
        return _clean(m.group(1))

    def resolve(self, title: str, chinese_title: str = "", year: Optional[int] = None):
        candidates = []
        for c in (chinese_title, title):
            c = (c or "").strip()
            if c and c not in candidates:
                candidates.append(c)
        for cand in candidates:
            img = self._summary_image(cand) or self._og_image(cand)
            if img:
                return img
        return None


if __name__ == "__main__":  # 手动测试
    p = WikipediaZhProvider()
    for t in ("咒术回战", "电锯人", "孤独摇滚", "我推的孩子"):
        print(t, "->", p.resolve("", t))
