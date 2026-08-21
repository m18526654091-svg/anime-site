"""AniList 封面源（联网，主来源）。

通过 AniList GraphQL 公开接口按标题搜索动漫并返回真实海报 URL。

Stage9-B 升级：
- 使用 Page.media(search=...) 一次取得最多 5 个候选（不再只取单个结果）；
- 支持标题别名（data/anime_aliases.json）：中文标题无法直接搜索时，
  用英文/罗马音搜索词召回；
- 对候选做本地评分（标题匹配 + 年份匹配），不允许无条件取第一候选；
- 设置最低接受阈值，无候选达标时返回 None。

无第三方依赖（使用标准库 urllib）。
"""
from __future__ import annotations

import json
import os
import random
import time
import urllib.request
from typing import Any, Optional

from .base import CoverProvider

ANILIST_ENDPOINT = "https://graphql.anilist.co"

# 单次搜索返回的最大候选数
QUERY_CANDIDATES = 5

# 最低接受阈值（标题匹配权重 0.65 + 年份加成后需达标）
MIN_SCORE = 60.0

_QUERY = (
    """
query ($search: String!) {
  Page(perPage: %d) {
    media(search: $search, type: ANIME, sort: SEARCH_MATCH) {
      id
      idMal
      title { english romaji native }
      synonyms
      format
      seasonYear
      coverImage { large extraLarge }
    }
  }
}
"""
    % QUERY_CANDIDATES
)

ALIASES_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data",
    "anime_aliases.json",
)


def _load_aliases() -> dict:
    """加载 data/anime_aliases.json；不存在或损坏返回空 dict。"""
    if not os.path.exists(ALIASES_FILE):
        return {}
    try:
        with open(ALIASES_FILE, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    return {}


class AniListProvider(CoverProvider):
    # Stage 9-C：priority 6，介于 MyAnimeListStatic(5) 与 WikipediaZh(8) 之间，
    # 保证按 LocalMapping → MAL → AniList → Wikipedia 顺序尝试。
    priority = 6

    def __init__(self, timeout: int = 15) -> None:
        self.timeout = timeout
        self.aliases = _load_aliases()

    def _fetch_candidates(self, search: str) -> list[dict[str, Any]]:
        """向 AniList 搜索并返回结构化候选列表。

        单次请求异常做短重试（最多 2 次尝试，0.8~1.5s 随机退避），
        重试耗尽后异常抛给调用方处理。不改变候选评分逻辑。
        """
        body = json.dumps({"query": _QUERY, "variables": {"search": search}}).encode("utf-8")
        last_exc: Optional[Exception] = None
        data: Optional[dict] = None
        for attempt in range(2):
            try:
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
                break
            except Exception as exc:  # noqa: BLE001 - 重试耗尽后抛给调用方
                last_exc = exc
                if attempt == 0:
                    time.sleep(random.uniform(0.8, 1.5))
        if data is None:
            if last_exc is not None:
                raise last_exc
            return []
        page = (data.get("data") or {}).get("Page") or {}
        media = page.get("media") or []
        out: list[dict[str, Any]] = []
        for m in media:
            title = m.get("title") or {}
            ci = m.get("coverImage") or {}
            out.append(
                {
                    "id": m.get("id"),
                    "idMal": m.get("idMal"),
                    "romaji": title.get("romaji") or "",
                    "english": title.get("english") or "",
                    "native": title.get("native") or "",
                    "synonyms": list(m.get("synonyms") or []),
                    "format": m.get("format"),
                    "seasonYear": m.get("seasonYear"),
                    "coverImage": ci.get("extraLarge") or ci.get("large") or "",
                }
            )
        return out

    def _title_score(self, query: str, cand: dict[str, Any]) -> float:
        """标题匹配评分 0-100：完全匹配 > 包含 > 分词命中。

        归一化省略号/尾部标点：AniList 用 … 截断长标题，而别名里是 ...，
        二者应视为等价，避免长标题（如转生恶役）被误判为不匹配。
        """

        def _norm(s: str) -> str:
            return s.replace("…", "").replace("...", "").strip(" .,!?，。！？")

        query_l = _norm((query or "").lower())
        if not query_l:
            return 0.0
        titles = [
            cand.get("romaji"),
            cand.get("english"),
            cand.get("native"),
        ] + list(cand.get("synonyms") or [])
        best = 0.0
        for t in titles:
            tl = _norm(str(t or "").lower())
            if not tl:
                continue
            if tl == query_l:
                best = max(best, 100.0)
            elif query_l in tl or tl in query_l:
                best = max(best, 80.0)
            elif all(w in tl for w in query_l.split()):
                best = max(best, 55.0)
            elif any(w in tl for w in query_l.split()):
                best = max(best, 35.0)
        return best

    def _score(self, query: str, cand: dict[str, Any], animehub_year: Optional[int]) -> float:
        """综合评分：标题匹配（权重 0.65）+ 年份匹配/冲突。"""
        score = self._title_score(query, cand) * 0.65
        sy = cand.get("seasonYear")
        if animehub_year and sy:
            diff = abs(int(animehub_year) - int(sy))
            if diff == 0:
                score += 30.0
            elif diff == 1:
                score += 15.0
            elif diff > 2:
                score -= 30.0
        return round(score, 1)

    def _query_words(self, title: str, chinese_title: str) -> list[str]:
        """查询词顺序：title → chinese_title → 别名 search 列表，去重保序。"""
        words: list[str] = []
        for w in [title, chinese_title]:
            if w and str(w).strip():
                words.append(str(w).strip())
        for key in [chinese_title, title]:
            if not key:
                continue
            entry = self.aliases.get(str(key))
            if not entry:
                continue
            for w in entry.get("search") or []:
                if w and str(w).strip():
                    words.append(str(w).strip())
        # 去重（保序）
        seen: set[str] = set()
        out: list[str] = []
        for w in words:
            k = w.lower()
            if k not in seen:
                seen.add(k)
                out.append(w)
        return out

    def search_candidates(self, title: str, chinese_title: str = "", year: Optional[int] = None) -> dict[str, Any]:
        """按查询词依次搜索并对候选评分；返回结构化结果供测试与 resolve 使用。

        返回字段：queries（实际查询词）、best（达标/最高分候选）、
        rejected（未达标候选）、reject_reason（未达标原因）。
        """
        result: dict[str, Any] = {
            "title": title,
            "chinese_title": chinese_title,
            "year": year,
            "queries": [],
            "best": None,
            "rejected": [],
            "reject_reason": "",
        }
        best: Optional[dict[str, Any]] = None
        for q in self._query_words(title, chinese_title):
            result["queries"].append(q)
            try:
                candidates = self._fetch_candidates(q)
            except Exception:
                # 该查询失败，尝试下一个
                continue
            for cand in candidates:
                sc = self._score(q, cand, year)
                cand["score"] = sc
                cand["query"] = q
                if best is None or sc > best.get("score", 0):
                    best = dict(cand)
                if sc >= MIN_SCORE:
                    result["best"] = dict(cand)
                    return result
                result["rejected"].append(dict(cand))

        result["best"] = best
        if best is None:
            result["reject_reason"] = "无候选"
        else:
            result["reject_reason"] = f"最高分 {best.get('score')} 低于阈值 {MIN_SCORE}"
        return result

    def resolve(self, title, chinese_title="", year=None) -> Optional[str]:
        """CoverProvider 接口：仅当候选评分 >= MIN_SCORE 时返回封面；否则 None。"""
        try:
            r = self.search_candidates(title, chinese_title, year)
            best = r.get("best")
            if best and best.get("score", 0) >= MIN_SCORE and best.get("coverImage"):
                return best["coverImage"]
        except Exception:
            # provider 异常不得阻断导入流程
            return None
        return None


if __name__ == "__main__":  # 手动测试
    p = AniListProvider()
    r = p.search_candidates("Fullmetal Alchemist: Brotherhood", "", 2009)
    print("queries:", r["queries"])
    print("best:", r.get("best"))

