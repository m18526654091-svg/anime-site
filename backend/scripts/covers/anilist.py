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
import logging
import os
import random
import time
import urllib.error
import urllib.request
from typing import Any, Optional

from .base import CoverProvider

logger = logging.getLogger("animehub.covers.anilist")

ANILIST_ENDPOINT = "https://graphql.anilist.co"

# 单次搜索返回的最大候选数
QUERY_CANDIDATES = 5

# 最低接受阈值（标题匹配权重 0.65 + 年份加成后需达标）
MIN_SCORE = 60.0

# ---- 全局请求节流（Stage 9-G）----
# AniList 官方约 30 requests/minute 时开始降级，且有 burst limiter。
# 目标速率 20~24 req/min，故每次真实 HTTP 请求最小间隔 ~2.7s（60/22）。
RATE_LIMIT_INTERVAL = 60.0 / 22.0

# 每次请求允许的最大尝试次数（HTTP/GraphQL 429 按 Retry-After/限流信息退避后重试）
MAX_ATTEMPTS = 3

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
        # 全局节流：记录上一次真实 HTTP 请求的时间（按每次 HTTP request 节流）
        self._last_request_time = 0.0

    def _throttle(self) -> None:
        """每次真实 HTTP 请求前调用：确保与上一次请求间隔 >= RATE_LIMIT_INTERVAL。

        多查询词 / retry 都必须经过同一节流器，避免连续请求形成 burst。
        """
        now = time.monotonic()
        if self._last_request_time:
            elapsed = now - self._last_request_time
            if elapsed < RATE_LIMIT_INTERVAL:
                time.sleep(RATE_LIMIT_INTERVAL - elapsed)
        self._last_request_time = time.monotonic()

    def _post(self, body: bytes) -> dict:
        """发送一次 GraphQL POST（经全局节流），返回 JSON dict。

        - HTTP 429：读取 Retry-After，至少等待该时间后重试（有限次数）；
        - GraphQL errors 含 429 / Too Many Requests / rate limit：按限流信息退避后重试；
        - 其他 GraphQL 错误：返回 {}（安全处理，调用方继续下一查询词，不阻断批次）；
        - 其他网络异常：短退避重试，耗尽后抛出由调用方处理。
        响应头 X-RateLimit-* 仅输出 debug 日志。
        """
        last_exc: Optional[Exception] = None
        for attempt in range(MAX_ATTEMPTS):
            self._throttle()
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
                    limit = resp.headers.get("X-RateLimit-Limit")
                    remaining = resp.headers.get("X-RateLimit-Remaining")
                    if limit or remaining:
                        logger.debug(
                            "[anilist] rate limit headers: limit=%s remaining=%s", limit, remaining
                        )
                    data = json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                if exc.code == 429:
                    retry_after = (exc.headers or {}).get("Retry-After")
                    try:
                        wait = max(float(retry_after), 1.0) if retry_after else 2.0
                    except (TypeError, ValueError):
                        wait = 2.0
                    logger.warning(
                        "[anilist] HTTP 429 attempt=%d Retry-After=%r wait=%.1fs",
                        attempt + 1,
                        retry_after,
                        wait,
                    )
                    last_exc = exc
                    if attempt < MAX_ATTEMPTS - 1:
                        time.sleep(wait)
                        continue
                    raise exc  # 有限次数耗尽，抛给调用方（继续下一查询词）
                last_exc = exc
                if attempt < MAX_ATTEMPTS - 1:
                    time.sleep(random.uniform(1.0, 2.0))
                    continue
                raise exc
            except Exception as exc:  # noqa: BLE001 - 网络/解析异常
                last_exc = exc
                if attempt < MAX_ATTEMPTS - 1:
                    time.sleep(random.uniform(1.0, 2.0))
                    continue
                raise exc

            # HTTP 200：检查 GraphQL errors（限流可能在 GraphQL 层返回）
            errs = (data or {}).get("errors")
            if errs:
                retry_after = None
                for e in errs:
                    st = e.get("status")
                    msg = str((e.get("message") or "") + " " + (e.get("error") or "")).lower()
                    if st == 429 or "too many requests" in msg or "rate limit" in msg:
                        retry_after = e.get("retryAfter") or e.get("retry_after")
                        break
                if retry_after is not None:
                    try:
                        wait = max(float(retry_after), 1.0)
                    except (TypeError, ValueError):
                        wait = 2.0
                    logger.warning(
                        "[anilist] GraphQL 429 attempt=%d wait=%.1fs errors=%s",
                        attempt + 1,
                        wait,
                        [e.get("status") for e in errs],
                    )
                    if attempt < MAX_ATTEMPTS - 1:
                        time.sleep(wait)
                        continue
                    # 尝试耗尽：按无候选处理，不阻断
                    return {}
                # 其他 GraphQL 错误：安全返回空，不阻断批次
                logger.debug("[anilist] GraphQL errors ignored: %s", errs)
                return {}
            return data
        return {}

    def _fetch_candidates(self, search: str) -> list[dict[str, Any]]:
        """向 AniList 搜索并返回结构化候选列表。

        Stage 9-G：所有真实 HTTP 请求都经全局节流（_throttle）与 _post 的
        429 / GraphQL 限流重试处理。不改变候选评分逻辑。
        """
        body = json.dumps({"query": _QUERY, "variables": {"search": search}}).encode("utf-8")
        data = self._post(body)
        if not data:
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

