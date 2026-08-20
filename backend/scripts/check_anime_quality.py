"""AnimeHub 数据质量检测工具。

用法（在 backend 目录）:
    .venv\\Scripts\\python -m scripts.check_anime_quality

功能:
- 统计动漫总数
- 统计基础字段 / SEO 字段缺失数量
- 统计重复 title / 重复 slug
- 统计占位封面数量与无效图片 URL 数量
- 只读检测，不修改数据库

可在每次批量扩充数据前后重复运行，快速判断数据质量。
"""
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from sqlalchemy import func, select  # noqa: E402

from app.database import SessionLocal  # noqa: E402
from app.models import Anime  # noqa: E402
from scripts.normalize import is_placeholder_cover  # noqa: E402

# 需要检测的字段（基础 + SEO）
FIELDS = [
    "title",
    "slug",
    "cover",
    "description",
    "genre",
    "year",
    "studio",
    "tags",
    "seo_title",
    "seo_description",
]

# 无需非空校验的字段（year 允许为空；studio 可后续补充）
ALLOW_EMPTY = {"year", "studio"}


def main() -> None:
    start = time.time()
    db = SessionLocal()
    try:
        total = db.query(Anime).count()
        print(f"Anime total: {total}")
        print()

        # ---- 1. 各字段缺失统计 ----
        for field in FIELDS:
            col = getattr(Anime, field)
            q = db.query(Anime).filter(
                (col.is_(None)) | (col == "")
            )
            if field == "year":
                q = db.query(Anime).filter(col.is_(None))
            missing = q.count()
            if field not in ALLOW_EMPTY and missing:
                print(f"Missing {field}:")
                print(missing)
        print()

        # ---- 2. 重复 title / 重复 slug ----
        dup_titles = (
            db.query(Anime.title, func.count(Anime.id))
            .filter(Anime.title != "")
            .group_by(Anime.title)
            .having(func.count(Anime.id) > 1)
            .all()
        )
        print(f"Duplicate title:")
        print(len(dup_titles))
        if dup_titles:
            print("Top duplicates:")
            for title, cnt in dup_titles[:10]:
                print(f"  x{cnt}: {title[:60]}")

        dup_slugs = (
            db.query(Anime.slug, func.count(Anime.id))
            .filter(Anime.slug != "")
            .group_by(Anime.slug)
            .having(func.count(Anime.id) > 1)
            .all()
        )
        print(f"Duplicate slug:")
        print(len(dup_slugs))
        if dup_slugs:
            print("Top duplicates:")
            for slug, cnt in dup_slugs[:10]:
                print(f"  x{cnt}: {slug[:60]}")
        print()

        # ---- 3. 封面问题统计 ----
        # 占位封面（placehold.co 等，数据库中不应存在）
        ph_covers = 0
        invalid_urls = 0
        empty_cover = 0
        covers = db.execute(select(Anime.cover)).all()
        for (cover,) in covers:
            c = (cover or "").strip()
            if not c:
                empty_cover += 1
            elif is_placeholder_cover(c):
                ph_covers += 1
            elif not (c.startswith("http://") or c.startswith("https://")):
                invalid_urls += 1

        print(f"Empty cover:")
        print(empty_cover)
        print(f"Placeholder cover:")
        print(ph_covers)
        print(f"Invalid image URL:")
        print(invalid_urls)
        print()

        # ---- 4. 汇总 ----
        print(f"Quality check done in {time.time() - start:.3f}s")
    finally:
        db.close()


if __name__ == "__main__":
    main()
