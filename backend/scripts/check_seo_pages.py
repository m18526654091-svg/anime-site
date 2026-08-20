"""AnimeHub SEO 页面资产统计工具。

用法（在 backend 目录）:
    .venv\\Scripts\\python -m scripts.check_seo_pages

统计当前站点可生成的 SEO 页面数量：
- anime 详情页
- genre 分类页
- tag 标签页
- year 年份页
- studio 制作公司页
- season 季度页

用于持续观察 SEO 内容资产增长。只读数据库，不修改数据。
"""
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from sqlalchemy import func, select  # noqa: E402

from app.database import SessionLocal  # noqa: E402
from app.models import Anime  # noqa: E402

SEASONS = ["spring", "summer", "autumn", "winter"]


def main() -> None:
    start = time.time()
    db = SessionLocal()
    try:
        # ---- anime 详情页 ----
        total_anime = db.query(Anime).count()
        slug_empty = db.query(Anime).filter((Anime.slug.is_(None)) | (Anime.slug == "")).count()

        # ---- genre 分类页（genre 多值字符串按原样作为 URL 参数）----
        genres = set()
        for (g,) in db.execute(select(Anime.genre).where(Anime.genre != "")).all():
            if g:
                genres.add(g.strip())
        total_genres = len(genres)

        # ---- tag 标签页（tags 按 / 拆分，每个标签一个页面）----
        tags: set[str] = set()
        for (t,) in db.execute(select(Anime.tags).where(Anime.tags != "")).all():
            if t:
                for part in t.split("/"):
                    part = part.strip()
                    if part:
                        tags.add(part)
        total_tags = len(tags)

        # ---- year 年份页 ----
        total_years = len(
            {
                y
                for (y,) in db.execute(
                    select(Anime.year).where(Anime.year.is_not(None)).distinct()
                ).all()
                if y is not None
            }
        )

        # ---- studio 制作公司页 ----
        studios = set()
        for (s,) in db.execute(select(Anime.studio).where(Anime.studio != "")).all():
            if s:
                studios.add(s.strip())
        total_studios = len(studios)

        # ---- season 季度页（每年 4 个季度，与 /seasons 端点回退逻辑一致）----
        total_seasons = total_years * len(SEASONS)

        print("=== AnimeHub SEO 页面资产统计 ===")
        print()
        print(f"Anime total: {total_anime}")
        print(f"Anime detail pages (anime/): {total_anime}")
        print(f"  - slug 为空（用数字 id 兜底）: {slug_empty}")
        print(f"Genre pages (categories/): {total_genres}")
        print(f"Tag pages (tags/): {total_tags}")
        print(f"Year pages (years/): {total_years}")
        print(f"Studio pages (studio/): {total_studios}")
        print(f"Season pages (season/): {total_seasons}")
        print()
        print(f"可生成 SEO 页面总数: {total_anime + total_genres + total_tags + total_years + total_studios + total_seasons}")
        print(f"统计耗时: {time.time() - start:.3f}s")
    finally:
        db.close()


if __name__ == "__main__":
    main()
