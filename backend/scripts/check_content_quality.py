"""AnimeHub 内容质量检查工具。

用法（在 backend 目录）:
    .venv\\Scripts\\python -m scripts.check_content_quality

职责：
- 识别模板/低质量数据（"动漫典藏"、"Anime Collection"、测试/占位标题等）
- 检测重复 description / 相似 seo_title / 相同 cover / 空 studio / 空 tags
- 为每条动漫计算 quality_score（90-100 真实完整；60-89 字段缺失；<60 需替换）
- 在数据库中写入 quality_score 字段（不删除任何数据）

只做标记与报告，不修改业务数据。
"""
import os
import sys
import time
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from sqlalchemy import text  # noqa: E402

from app.database import SessionLocal, ensure_schema  # noqa: E402
from app.models import Anime  # noqa: E402

# 模板/占位标题特征（真实动漫的标题是真实作品名，不含这些标记）
TEMPLATE_MARKERS = (
    "动漫典藏",
    "Anime Collection",
    "测试动漫",
    "批量测试",
    "Anime Project",
)


def is_template(item: Anime) -> bool:
    """仅依据标题/中文名判断是否为模板数据。

    真实动漫（知名作品名）即使描述为信息型模板也不视为模板数据，
    避免误伤；模板数据特指标题本身即占位/典藏/测试的条目。
    """
    title = (item.title or "")
    cn = (item.chinese_title or "")
    return any(m in title for m in TEMPLATE_MARKERS) or any(m in cn for m in TEMPLATE_MARKERS)


# 模板化描述特征（真实数据但描述结构雷同，降低质量分）
TEMPLATE_DESC_MARKERS = (
    "凭借出色的剧情与制作深受观众喜爱",
    "是一部值得一看的动漫作品",
    "动漫典藏系列",
    "支持在线观看高清全集",
)


def compute_quality(item: Anime) -> int:
    """计算 0-100 质量分。真实完整 >= 90，字段缺失 60-89，模板/低质 < 60。"""
    if is_template(item):
        # 模板数据即使字段完整也视为低质量（需替换）
        score = 40
        if (item.cover or "") and (item.studio or "") and (item.description or ""):
            score = 55
        return score

    score = 100
    checks = [
        (item.title, 15),
        (item.chinese_title, 10),
        (item.slug, 10),
        (item.cover, 15),
        (item.description, 20),
        (item.genre, 10),
        (item.studio, 5),
        (item.tags, 5),
        (item.year, 5),
        (item.score or 0, 5),  # 真实评分权重
        (item.seo_title, 3),
        (item.seo_description, 2),
    ]
    for val, weight in checks:
        if val is None or str(val or "").strip() == "":
            score -= weight
    # 描述模板化（结构雷同）扣分，鼓励独特内容
    desc = (item.description or "").strip()
    if desc and any(m in desc for m in TEMPLATE_DESC_MARKERS):
        score -= 8
    return max(score, 0)


def main() -> None:
    start = time.time()
    ensure_schema()
    db = SessionLocal()
    try:
        rows = db.query(Anime).all()
        total = len(rows)

        template_items = [a for a in rows if is_template(a)]
        real_items = [a for a in rows if not is_template(a)]

        # 重复 description（完整相同）
        desc_counter = Counter((a.description or "").strip() for a in rows if (a.description or "").strip())
        dup_desc = {d: n for d, n in desc_counter.items() if n > 1}

        # 相同 cover
        cover_counter = Counter((a.cover or "").strip() for a in rows if (a.cover or "").strip())
        dup_cover = {c: n for c, n in cover_counter.items() if n > 1}

        # 相似 seo_title（按品牌模板生成且除名称外完全相同的模式）
        seo_titles = [(a.title, a.seo_title or "") for a in rows]
        # 空 studio / 空 tags
        empty_studio = sum(1 for a in rows if not (a.studio or "").strip())
        empty_tags = sum(1 for a in rows if not (a.tags or "").strip())
        empty_cover = sum(1 for a in rows if not (a.cover or "").strip())

        # 计算质量分并写入数据库（含 is_indexable 控制）
        low_quality = 0
        medium_quality = 0
        high_quality = 0
        updated = 0
        for a in rows:
            q = compute_quality(a)
            if q < 60:
                low_quality += 1
            elif q < 90:
                medium_quality += 1
            else:
                high_quality += 1
            if a.quality_score != q:
                a.quality_score = q
                updated += 1
            # 进 sitemap 的页面：quality_score >= 70
            new_indexable = 1 if q >= 70 else 0
            if a.is_indexable != new_indexable:
                a.is_indexable = new_indexable
                updated += 1
        if updated:
            db.commit()

        # 重复 seo_title（完全相同的）统计
        seo_counter = Counter((a.seo_title or "").strip() for a in rows if (a.seo_title or "").strip())
        dup_seo = {s: n for s, n in seo_counter.items() if n > 1}

        print("=== AnimeHub 内容质量报告 ===")
        print()
        print(f"Total anime: {total}")
        print(f"Real anime (非模板): {len(real_items)}")
        print(f"Template anime (模板): {len(template_items)}")
        print()
        print(f"Duplicate description: {len(dup_desc)}")
        if dup_desc:
            print("Top:")
            for d, n in sorted(dup_desc.items(), key=lambda x: -x[1])[:5]:
                print(f"  x{n}: {d[:60]}")
        print(f"Duplicate cover: {len(dup_cover)}")
        print(f"Duplicate seo_title: {len(dup_seo)}")
        print()
        print(f"Empty studio: {empty_studio}")
        print(f"Empty tags: {empty_tags}")
        print(f"Empty cover: {empty_cover}")
        print()
        print("质量分布（已写入 quality_score 字段）:")
        print(f"  >= 90 (真实完整): {high_quality}")
        print(f"  60-89 (字段缺失): {medium_quality}")
        print(f"  < 60 (需要替换): {low_quality}")
        print(f"  模板占比: {len(template_items) / total * 100:.1f}%")
        print(f"检查耗时: {time.time() - start:.3f}s")
    finally:
        db.close()


if __name__ == "__main__":
    main()
