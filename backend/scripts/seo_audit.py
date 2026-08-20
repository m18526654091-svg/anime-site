"""AnimeHub Google 收录准备审计工具。

用法（在 backend 目录）:
    .venv\\Scripts\\python -m scripts.seo_audit

检查项：
- 数据库规模与 sitemap 可生成 URL 数量
- 重复 title / 重复 description / 空 slug / 低质量页面占比
- 封面完整性（真实/占位/缺失）

输出 SEO 审计报告，便于上线前评估收录就绪度。只读数据库。
"""
import os
import sys
import time
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from sqlalchemy import func, select  # noqa: E402

from app.database import SessionLocal  # noqa: E402
from app.models import Anime  # noqa: E402
from scripts.normalize import is_placeholder_cover  # noqa: E402


def main() -> None:
    start = time.time()
    db = SessionLocal()
    try:
        total = db.query(Anime).count()
        rows = db.query(Anime).all()

        # ---- 1. slug ----
        empty_slug = sum(1 for a in rows if not (a.slug or "").strip())

        # ---- 2. 重复 title / description ----
        titles = Counter((a.title or "").strip() for a in rows if (a.title or "").strip())
        descs = Counter((a.description or "").strip() for a in rows if (a.description or "").strip())
        dup_title = sum(1 for t, n in titles.items() if n > 1)
        dup_desc = sum(1 for d, n in descs.items() if n > 1)

        # ---- 3. 封面 ----
        real_cover = 0
        ph_cover = 0
        empty_cover = 0
        for a in rows:
            c = (a.cover or "").strip()
            if not c:
                empty_cover += 1
            elif is_placeholder_cover(c):
                ph_cover += 1
            else:
                real_cover += 1

        # ---- 4. 低质量页面（quality_score < 60）----
        low_quality = sum(1 for a in rows if (a.quality_score or 100) < 60)
        real_anime = sum(1 for a in rows if (a.quality_score or 100) >= 60)

        # ---- 5. sitemap 可生成 URL 数 ----
        genres = set()
        for (g,) in db.execute(select(Anime.genre).where(Anime.genre != "")).all():
            if g:
                genres.add(g.strip())
        tags: set[str] = set()
        for (t,) in db.execute(select(Anime.tags).where(Anime.tags != "")).all():
            if t:
                for p in t.split("/"):
                    p = p.strip()
                    if p:
                        tags.add(p)
        years = {
            y for (y,) in db.execute(select(Anime.year).where(Anime.year.is_not(None)).distinct()).all() if y
        }
        studios = {
            s.strip() for (s,) in db.execute(select(Anime.studio).where(Anime.studio != "")).all() if s
        }
        url_count = 7 + total + len(genres) + len(tags) + len(years) + len(studios) + len(years) * 4

        # ---- 报告 ----
        print("========== AnimeHub SEO 审计报告 ==========")
        print()
        print(f"数据库动漫总数: {total}")
        print(f"可生成 sitemap URL 数(约): {url_count}")
        print(f"  - anime 详情页: {total}")
        print(f"  - 类型页: {len(genres)}")
        print(f"  - 标签页: {len(tags)}")
        print(f"  - 年份页: {len(years)}")
        print(f"  - 制作公司页: {len(studios)}")
        print(f"  - 季度页: {len(years) * 4}")
        print()
        print("---- 内容质量 ----")
        print(f"真实动漫(quality>=60): {real_anime}")
        print(f"低质量页面(quality<60): {low_quality} ({low_quality/total*100:.1f}%)")
        print(f"重复 title 组数: {dup_title}")
        print(f"重复 description 组数: {dup_desc}")
        print(f"空 slug: {empty_slug}")
        print()
        print("---- 封面 ----")
        print(f"真实封面: {real_cover} ({real_cover/total*100:.1f}%)")
        print(f"占位封面: {ph_cover}")
        print(f"缺失封面: {empty_cover}")
        print()
        print(f"审计耗时: {time.time() - start:.3f}s")
    finally:
        db.close()


if __name__ == "__main__":
    main()
