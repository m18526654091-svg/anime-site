"""AnimeHub Google 收录健康报告工具。

用法（在 backend 目录）:
    .venv\\Scripts\\python -m scripts.seo_health_report

输出：
- 总 URL 数量（可生成 sitemap 的 URL 数）
- 高质量 URL 数量（quality_score >= 60）
- 低质量 URL 数量（quality_score < 60）
- sitemap 数量（可生成 URL 总数）
- 空字段数量（slug / cover / studio / tags 等）
- 重复内容数量（重复 title / description / seo_title）

只读数据库，用于持续监控收录健康度。
"""
import os
import sys
import time
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from sqlalchemy import select  # noqa: E402

from app.database import SessionLocal  # noqa: E402
from app.models import Anime  # noqa: E402
from scripts.normalize import is_placeholder_cover  # noqa: E402


def main() -> None:
    start = time.time()
    db = SessionLocal()
    try:
        rows = db.query(Anime).all()
        total = len(rows)

        # ---- 质量分层 ----
        high = sum(1 for a in rows if (a.quality_score or 100) >= 60)
        low = total - high

        # ---- 空字段 ----
        empty = {}
        for field in ("slug", "cover", "studio", "tags", "genre", "description"):
            empty[field] = sum(1 for a in rows if not str(getattr(a, field) or "").strip())
        empty_year = sum(1 for a in rows if a.year is None)

        # ---- 重复内容 ----
        titles = Counter((a.title or "").strip() for a in rows if (a.title or "").strip())
        descs = Counter((a.description or "").strip() for a in rows if (a.description or "").strip())
        seos = Counter((a.seo_title or "").strip() for a in rows if (a.seo_title or "").strip())
        dup = {
            "title": sum(1 for _, n in titles.items() if n > 1),
            "description": sum(1 for _, n in descs.items() if n > 1),
            "seo_title": sum(1 for _, n in seos.items() if n > 1),
        }

        # ---- 封面 ----
        real_cover = sum(1 for a in rows if (a.cover or "").strip() and not is_placeholder_cover(a.cover))
        ph_cover = sum(1 for a in rows if is_placeholder_cover((a.cover or "").strip()))
        empty_cover = empty["cover"]

        # ---- sitemap 可生成 URL ----
        genres = {g.strip() for (g,) in db.execute(select(Anime.genre).where(Anime.genre != "")).all() if g}
        tags: set[str] = set()
        for (t,) in db.execute(select(Anime.tags).where(Anime.tags != "")).all():
            if t:
                tags.update(p.strip() for p in t.split("/") if p.strip())
        years = {y for (y,) in db.execute(select(Anime.year).where(Anime.year.is_not(None)).distinct()).all() if y}
        studios = {s.strip() for (s,) in db.execute(select(Anime.studio).where(Anime.studio != "")).all() if s}
        sitemap_urls = 10 + total + len(genres) + len(tags) + len(years) + len(studios) + len(years) * 4

        # ---- 报告 ----
        print("========== AnimeHub SEO 健康报告 ==========")
        print()
        print(f"[URL 资产]")
        print(f"  总 URL 数量: {sitemap_urls}")
        print(f"  高质量 URL (quality>=60): {high}")
        print(f"  低质量 URL (quality<60): {low} ({low/total*100:.1f}%)")
        print(f"  sitemap 数量: {sitemap_urls}")
        print()
        print(f"[字段完整性]")
        for f, n in empty.items():
            if n:
                print(f"  空 {f}: {n}")
        if empty_year:
            print(f"  空 year: {empty_year}")
        if all(n == 0 for n in empty.values()) and empty_year == 0:
            print("  全部字段完整")
        print()
        print(f"[重复内容]")
        print(f"  重复 title: {dup['title']}")
        print(f"  重复 description: {dup['description']}")
        print(f"  重复 seo_title: {dup['seo_title']}")
        print()
        print(f"[封面]")
        print(f"  真实封面: {real_cover} ({real_cover/total*100:.1f}%)")
        print(f"  占位封面: {ph_cover}")
        print(f"  缺失封面: {empty_cover}")
        print()
        print(f"报告耗时: {time.time() - start:.3f}s")
    finally:
        db.close()


if __name__ == "__main__":
    main()
