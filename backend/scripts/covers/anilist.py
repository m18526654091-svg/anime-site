"""AniList 封面源（联网，主来源）。

通过 AniList GraphQL 公开接口按标题搜索动漫并返回真实海报 URL。
无第三方依赖（使用标准库 urllib）。适合批量补真实封面。
"""
from __future__ import annotations

import json
import urllib.request
from typing import Optional

from .base import CoverProvider

ANILIST_ENDPOINT = "https://graphql.anilist.co"

_QUERY = """
query ($search: String!) {
  Media(search: $search, type: ANIME, sort: SEARCH_MATCH) {
    title { english romaji native }
    coverImage { large extraLarge }
  }
}
"""


class AniListProvider(CoverProvider):
    priority = 10

    def __init__(self, timeout: int = 15) -> None:
        self.timeout = timeout

    def _query(self, search: str) -> Optional[str]:
        body = json.dumps({"query": _QUERY, "variables": {"search": search}}).encode("utf-8")
        req = urllib.request.Request(
            ANILIST_ENDPOINT,
            data=body,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "AnimeHub-Importer/1.0 (SEO content pipeline)",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        media = ((data.get("data") or {}).get("Media") or {})
        cover = ((media.get("coverImage") or {}) or {})
        return cover.get("extraLarge") or cover.get("large") or None

    def resolve(self, title, chinese_title="", year=None):
        candidates = [title, chinese_title]
        for cand in candidates:
            if not cand or not str(cand).strip():
                continue
            try:
                url = self._query(str(cand).strip())
                if url:
                    return url
            except Exception:
                # 该候选失败，尝试下一个；整体失败返回 None
                continue
        return None


if __name__ == "__main__":  # 手动测试
    p = AniListProvider()
    print(p.resolve("Fullmetal Alchemist: Brotherhood"))