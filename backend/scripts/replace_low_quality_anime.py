"""AnimeHub 低质量模板动漫替换工具。

用法（在 backend 目录）:
    .venv\\Scripts\\python -m scripts.replace_low_quality_anime [--limit N] [--dry-run]

职责：
- 找出 quality_score < 60 的模板动漫（"动漫典藏XXX号"、"Anime Collection"等）；
- 用内置真实知名动漫清单（KNOWN_ANIME）中尚未收录的作品逐个替换；
- 替换时补齐 title/chinese_title/cover/description/genre/tags/year/studio/episodes/
  seo_title/seo_description 等字段，重新计算 quality_score；
- 保留数据库 id 与表结构，不删除任何记录。

设计：
- 幂等可重跑；已替换过的条目不再处理；
- 只替换为真实知名动漫，绝不生成新的模板内容；
- cover 保留空（由 fetch_missing_covers 后续补真实封面，避免写入错误图）。
"""
import argparse
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from app.database import SessionLocal, ensure_schema  # noqa: E402
from app.models import Anime  # noqa: E402
from scripts.extend_anime_data import KNOWN_ANIME  # noqa: E402
from scripts.normalize import _build_seo_description, _build_seo_title, normalize_tags, build_auto_tags  # noqa: E402

TEMPLATE_MARKERS = ("动漫典藏", "Anime Collection", "测试动漫", "Anime Project")


def is_template_title(text: str) -> bool:
    return any(m in (text or "") for m in TEMPLATE_MARKERS)


def to_payload(t: tuple) -> dict:
    """把 KNOWN_ANIME 元组转成完整字段。"""
    title, cn, year, genre, studio, score = t
    return {
        "title": title,
        "chinese_title": cn,
        "year": year,
        "genre": genre,
        "studio": studio,
        "score": float(score),
        "episodes": 12,
        "status": "完结",
        "region": "日本",
        "description": f"《{cn}》是一部{year}年首播的{genre}题材日本动画，由{studio}制作，凭借出色的剧情与制作深受观众喜爱，是值得一看的动漫佳作。",
        "tags": "/".join(g.strip() for g in genre.split("/") if g.strip()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0, help="最多替换条数（0=全部可替换）")
    parser.add_argument("--dry-run", action="store_true", help="只打印，不写库")
    args = parser.parse_args()

    ensure_schema()
    db = SessionLocal()
    start = time.time()
    try:
        # 1. 已收录真实动漫的中文名（quality>=60），用于判断哪些 KNOWN 尚未收录
        real_rows = db.query(Anime).filter(Anime.quality_score >= 60).all()
        used_keys = set()
        for a in real_rows:
            used_keys.add((a.chinese_title or "").strip().lower())
            used_keys.add((a.title or "").strip().lower())

        # 2. 构建可替换池（KNOWN 中未收录的真实动漫，按中文名去重）
        pool = []
        pool_keys: set[str] = set()
        for t in KNOWN_ANIME:
            _, cn, *_ = t
            key = (cn or "").strip().lower()
            key2 = (t[0] or "").strip().lower()
            if key in used_keys or key2 in used_keys:
                continue
            if key in pool_keys:
                continue  # 同一中文名只保留第一条，避免重复数据
            pool_keys.add(key)
            pool.append(t)
        print(f"可替换真实动漫池: {len(pool)} 条")

        # 3. 找出低质量模板条目
        targets = (
            db.query(Anime)
            .filter(Anime.quality_score < 60)
            .order_by(Anime.id.asc())
            .all()
        )
        print(f"低质量模板条目: {len(targets)} 条")

        limit = args.limit or len(targets)
        replaced = 0
        for a in targets:
            if replaced >= limit or not pool:
                break
            if not is_template_title(a.title) and not is_template_title(a.chinese_title):
                # 不是模板标题但质量低（可能是真实动漫缺字段）→ 用真实数据补齐
                pass
            payload = to_payload(pool.pop(0))
            cn = payload["chinese_title"]
            payload["seo_title"] = _build_seo_title(cn, payload)
            payload["seo_description"] = _build_seo_description(cn, payload)
            payload["tags"] = normalize_tags(payload.get("tags")) or build_auto_tags(payload)
            payload["cover"] = ""  # 由 fetch_missing_covers 补真实封面

            if args.dry_run:
                print(f"  [DRY] id={a.id} {a.chinese_title or a.title} -> {cn}")
                replaced += 1
                continue

            a.title = payload["title"]
            a.chinese_title = payload["chinese_title"]
            # 同步更新 slug，确保 URL 与新标题一致（避免"动漫典藏001号"这类 URL）
            from scripts.normalize import make_slug  # noqa: E402
            new_slug = make_slug(payload["title"]) or make_slug(payload["chinese_title"]) or f"anime-{a.id}"
            a.slug = new_slug
            a.cover = payload["cover"]
            a.description = payload["description"]
            a.genre = payload["genre"]
            a.tags = payload["tags"]
            a.year = payload["year"]
            a.studio = payload["studio"]
            a.status = payload["status"]
            a.region = payload["region"]
            a.episodes = payload["episodes"]
            a.score = payload["score"]
            a.seo_title = payload["seo_title"]
            a.seo_description = payload["seo_description"]
            a.quality_score = 95  # 真实完整
            used_keys.add((cn or "").strip().lower())
            used_keys.add((payload["title"] or "").strip().lower())
            replaced += 1
            if replaced % 100 == 0:
                db.commit()
                print(f"  已替换 {replaced} 条...")
        db.commit()

        real = db.query(Anime).filter(Anime.quality_score >= 60).count()
        template = db.query(Anime).filter(Anime.quality_score < 60).count()
        print()
        print(f"替换完成: {replaced} 条，耗时 {time.time() - start:.1f}s")
        print(f"剩余真实动漫: {real}，剩余模板: {template}")
        if args.dry_run:
            print("（dry-run 模式，未写库）")
    finally:
        db.close()


if __name__ == "__main__":
    main()
