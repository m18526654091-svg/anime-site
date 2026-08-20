"""AnimeHub 缺失封面补全工具。

用法（在 backend 目录）:
    .venv\\Scripts\\python -m scripts.fetch_missing_covers [--limit N] [--dry-run]

职责：
- 找出 cover 为空或占位图的动漫；
- 依序尝试公开封面源：Wikimedia Commons → MyAnimeList 缩略图 → 其他；
- 成功则写回数据库 cover 字段；失败保留空（前端使用站内渐变占位），
  绝不写入错误/占位图片 URL。

设计：
- 幂等可重跑；--limit 控制单次处理条数；
- --dry-run 只打印将处理的条目，不写库。
"""
import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from app.database import SessionLocal  # noqa: E402
from app.models import Anime  # noqa: E402
from scripts.normalize import is_placeholder_cover  # noqa: E402

# 封面缓存文件：记录成功（title -> url/source）与失败（避免重复请求）
CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cover_cache.json")

TIMEOUT = 10
UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
}


def _http_get_json(url: str) -> dict | None:
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return json.loads(r.read().decode("utf-8", errors="replace"))
    except Exception:
        return None


def fetch_from_wikipedia(keyword: str, lang: str = "zh") -> str | None:
    """通过 Wikipedia REST summary 获取词条首图（通常是官方海报/封面）。

    仅接受 upload.wikimedia.org 图片，避免写入不可靠来源。
    """
    slug = keyword.replace(" ", "_")
    url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(slug)}"
    data = _http_get_json(url)
    if not data:
        return None
    thumb = (data.get("thumbnail") or {}).get("source")
    if thumb and thumb.startswith("https://upload.wikimedia.org/"):
        # 去掉 tracking 参数
        return thumb.split("?")[0]
    return None


def fetch_from_myanimelist(keyword: str) -> str | None:
    """通过 Jikan 公开 API（MyAnimeList 非官方镜像）搜索封面。"""
    q = urllib.parse.quote(keyword)
    url = f"https://api.jikan.moe/v4/anime?q={q}&limit=1&sfw=true"
    data = _http_get_json(url)
    if not data:
        return None
    for item in (data.get("data") or []):
        img = ((item.get("images") or {}).get("jpg") or {}).get("image_url")
        if img and img.startswith("http"):
            return img
    return None


def resolve_cover(item: Anime) -> str | None:
    """依序尝试各源。返回 None 表示失败（保留 fallback）。

    顺序：中文 Wikipedia 词条首图 → 英文 Wikipedia 词条首图 → Jikan(MyAnimeList)。
    只接受可确认为官方海报/封面图的来源，绝不为命中失败写入占位/错误图。
    """
    title = (item.title or "").strip()
    cn = (item.chinese_title or "").strip()

    if cn:
        url = fetch_from_wikipedia(cn, "zh")
        if url:
            return url
    if title:
        url = fetch_from_wikipedia(title, "en")
        if url:
            return url
        url = fetch_from_myanimelist(title)
        if url:
            return url
    if cn:
        url = fetch_from_myanimelist(cn)
        if url:
            return url
    return None


# 请求间隔（秒）：避免触发 Wikipedia/API 限流
REQUEST_DELAY = 1.0


def _load_cache() -> dict:
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"urls": {}, "failed": []}


def _save_cache(cache: dict) -> None:
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=50, help="单次最多处理条数")
    parser.add_argument("--dry-run", action="store_true", help="只打印，不写库")
    args = parser.parse_args()

    cache = _load_cache()
    cached_urls = cache.get("urls", {})
    cached_failed = set(cache.get("failed", []))

    db = SessionLocal()
    try:
        rows = db.query(Anime).filter(
            (Anime.cover.is_(None)) | (Anime.cover == "")
        ).order_by(Anime.id.asc()).all()
        rows = [a for a in rows if not (a.cover or "").strip()]
        # 跳过缓存中已失败的条目（避免重复请求）
        rows = [a for a in rows if (a.chinese_title or a.title or "").strip() not in cached_failed]
        rows = rows[: args.limit]
        print(f"待补封面: {len(rows)} 条（limit={args.limit}，缓存命中跳过 {len(cached_failed)} 条失败记录）")

        updated = 0
        failed = 0
        reused_cache = 0
        start = time.time()
        for a in rows:
            key = (a.chinese_title or a.title or "").strip()
            # 1. 命中缓存
            if key in cached_urls:
                if not args.dry_run:
                    a.cover = cached_urls[key]["url"]
                    db.add(a)
                    updated += 1
                    reused_cache += 1
                print(f"  [CACHE] {key} -> {cached_urls[key]['url'][:80]}")
                continue
            # 2. 实时抓取（请求间加延时，避免触发限流）
            time.sleep(REQUEST_DELAY)
            cover = resolve_cover(a)
            if cover:
                if not args.dry_run:
                    a.cover = cover
                    db.add(a)
                    cached_urls[key] = {"url": cover, "source": "wikipedia"}
                    updated += 1
                print(f"  [OK] {key} -> {cover[:100]}")
            else:
                failed += 1
                cached_failed.add(key)
                print(f"  [--] {key} 未找到封面（保留 fallback，已记录失败）")
            if updated and updated % 20 == 0:
                db.commit()
        if updated:
            db.commit()
        if not args.dry_run:
            cache["urls"] = cached_urls
            cache["failed"] = sorted(cached_failed)
            _save_cache(cache)

        print()
        print(f"完成: 新增成功 {updated - reused_cache}，缓存复用 {reused_cache}，失败 {failed}，耗时 {time.time() - start:.1f}s")
        print(f"缓存文件: {CACHE_FILE}（成功 {len(cached_urls)} 条，失败记录 {len(cached_failed)} 条）")
        if args.dry_run:
            print("（dry-run 模式，未写库）")
    finally:
        db.close()


if __name__ == "__main__":
    main()
