"""AnimeHub 缺失封面批量回填工具（Stage9-B / Stage9-C）。

用法（在 backend 目录）:
    .venv\\Scripts\\python -m scripts.fetch_missing_covers [--limit N] [--dry-run]
    .venv\\Scripts\\python -m scripts.fetch_missing_covers --suggest-wikipedia [--limit N]
    .venv\\Scripts\\python -m scripts.fetch_missing_covers --repair-wikipedia [--limit N] [--dry-run]

职责：
- 读取数据库当前 Anime 数据（SQLite/PostgreSQL 均可，通过 SessionLocal）；
- 只处理 cover 为空或占位图（placehold.co 等）的记录；
- 使用 build_resolvers()/resolve_cover() 依序尝试：LocalMapping → MyAnimeListStatic
  → AniList → Wikipedia；
- 成功则写回 Anime.cover，并同步更新 data/covers_mapping.json；
- 已存在的真实封面绝不被覆盖；占位图失败保留 fallback（前端展示站内渐变占位）。

Stage 9-C：
- --suggest-wikipedia：扫描已有 Wikimedia 封面，若 AniList 能找到更高置信候选
  （score >= MIN_SCORE），仅打印建议替换，绝不写库。
- --repair-wikipedia：把已有 Wikimedia 封面正式替换为 AniList 更高置信候选
  （默认真正写库并更新 covers_mapping.json）；配合 --dry-run 仅预览。
  安全条件：best 存在 且 score >= MIN_SCORE 且 coverImage 非空 且与当前 URL 不同。
  单条异常不中断批次。此参数不处理空 cover / placeholder。

设计：
- 默认运行安全（--dry-run 只打印不写库）；
- --limit 控制单次处理条数，适合分批执行；
- 幂等可重跑。
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from app.database import SessionLocal  # noqa: E402
from app.models import Anime  # noqa: E402
from scripts.covers import build_resolvers, resolve_cover  # noqa: E402
from scripts.covers.anilist import AniListProvider, MIN_SCORE  # noqa: E402
from scripts.covers.resolver import MAPPING_FILE  # noqa: E402
from scripts.normalize import is_placeholder_cover  # noqa: E402

# 请求间隔（秒）：避免触发各来源 API 限流
REQUEST_DELAY = 1.0

# Wikimedia 封面前缀（用于 --suggest-wikipedia 扫描）
WIKIMEDIA_PREFIX = "https://upload.wikimedia.org/"


def source_of(url: str) -> str:
    """根据 URL host 粗略判断来源，用于统计。"""
    if "anilist.co" in url:
        return "anilist"
    if "upload.wikimedia.org" in url:
        return "wikipedia"
    if "myanimelist.net" in url:
        return "myanimelist"
    return "other"


def load_mapping() -> dict:
    if not os.path.exists(MAPPING_FILE):
        return {}
    try:
        with open(MAPPING_FILE, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return {str(k): str(v) for k, v in data.items() if str(k).strip() and str(v).strip()}
    except Exception:
        pass
    return {}


def save_mapping(mapping: dict) -> None:
    os.makedirs(os.path.dirname(MAPPING_FILE), exist_ok=True)
    with open(MAPPING_FILE, "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)


def _wikipedia_rows(db, limit: int) -> list:
    """Wikimedia 封面记录（--suggest-wikipedia / --repair-wikipedia 共用）。"""
    query = db.query(Anime).filter(Anime.cover.like(f"{WIKIMEDIA_PREFIX}%")).order_by(Anime.id.asc())
    rows = query.all()
    if limit:
        rows = rows[:limit]
    return rows


def _anilist_best(anilist: AniListProvider, a: Anime) -> Optional[dict]:
    """AniList 达标候选；无候选/低于 MIN_SCORE/无封面返回 None。"""
    r = anilist.search_candidates((a.title or ""), (a.chinese_title or ""), a.year)
    best = r.get("best")
    if not best or best.get("score", 0) < MIN_SCORE or not best.get("coverImage"):
        return None
    return best


def suggest_wikipedia_replacements(db, anilist: AniListProvider, limit: int) -> None:
    """扫描已有 Wikimedia 封面；AniList 有更高置信候选时仅打印建议（只读，不写库）。

    判定：AniList best 候选 score >= MIN_SCORE 且封面与当前 Wikimedia URL 不同。
    """
    rows = _wikipedia_rows(db, limit)
    print(f"Wikimedia 封面数: {len(rows)}（limit={limit or '全部'}）")
    suggestions = 0
    for a in rows:
        key = (a.chinese_title or a.title or "").strip()
        time.sleep(REQUEST_DELAY)
        best = _anilist_best(anilist, a)
        if not best:
            continue
        if best["coverImage"] == (a.cover or "").strip():
            continue
        suggestions += 1
        print(
            f"  [建议] {key} -> AniList score={best.get('score')} "
            f"year={best.get('seasonYear')} format={best.get('format')}"
        )
        print(f"         当前(wikipedia): {(a.cover or '')[:90]}")
        print(f"         建议(anilist)  : {best['coverImage'][:90]}")
    print(f"完成: 建议替换 {suggestions} 条（仅建议，未写库）")


def repair_wikipedia_replacements(
    db,
    anilist: AniListProvider,
    mapping: dict,
    limit: int,
    dry_run: bool,
) -> None:
    """正式修复：把已有 Wikimedia 封面替换为 AniList 更高置信候选（默认真正写库）。

    安全条件（与 --suggest-wikipedia 一致）：
      best 存在 且 score >= MIN_SCORE 且 coverImage 非空 且与当前 Wikimedia URL 不同。
    - 默认写 Anime.cover 并同步 covers_mapping.json；
    - --dry-run 时只打印，不写数据库、不写 mapping；
    - 单条异常不中断批次（计入错误数）。
    不处理空 cover / placeholder（本参数只修复已有 Wikimedia 封面）。
    """
    rows = _wikipedia_rows(db, limit)
    checked = len(rows)
    suggested = 0
    replaced = 0
    skipped = 0
    errors = 0
    print(f"Wikimedia 封面数: {checked}（limit={limit or '全部'}）")
    if not dry_run:
        print("（--repair-wikipedia 将真正写库并更新 covers_mapping.json；建议先 --dry-run 预览）")
    for a in rows:
        key = (a.chinese_title or a.title or "").strip()
        current = (a.cover or "").strip()
        try:
            time.sleep(REQUEST_DELAY)
            best = _anilist_best(anilist, a)
        except Exception as exc:  # noqa: BLE001 - 单条异常不中断批次
            errors += 1
            print(f"  [ERR] {key} 查询异常，跳过: {exc}")
            continue
        if not best:
            skipped += 1
            continue
        if best["coverImage"] == current:
            skipped += 1
            continue
        suggested += 1
        if dry_run:
            print(
                f"  [将替换] {key} -> AniList score={best.get('score')} "
                f"year={best.get('seasonYear')} format={best.get('format')}"
            )
            print(f"           当前(wikipedia): {current[:90]}")
            print(f"           目标(anilist)  : {best['coverImage'][:90]}")
            continue
        a.cover = best["coverImage"]
        db.add(a)
        mapping[key] = best["coverImage"]
        replaced += 1
        print(
            f"  [替换] {key} -> AniList score={best.get('score')} "
            f"year={best.get('seasonYear')} format={best.get('format')}"
        )
        print(f"         当前(wikipedia): {current[:90]}")
        print(f"         目标(anilist)  : {best['coverImage'][:90]}")

    if not dry_run and replaced:
        db.commit()
        save_mapping(mapping)
    print()
    print(
        f"完成: 检查 {checked} | 建议替换 {suggested} | 实际替换 {replaced} "
        f"| 跳过 {skipped} | 错误 {errors}"
    )
    if dry_run:
        print("（dry-run：未写数据库、未写 covers_mapping.json）")


def main() -> None:
    parser = argparse.ArgumentParser(description="批量回填缺失封面")
    parser.add_argument("--limit", type=int, default=50, help="单次最多处理条数")
    parser.add_argument("--dry-run", action="store_true", help="只打印，不写库")
    parser.add_argument(
        "--suggest-wikipedia",
        action="store_true",
        help="扫描 Wikimedia 封面，AniList 有更高置信候选时仅打印建议（只读，不写库）",
    )
    parser.add_argument(
        "--repair-wikipedia",
        action="store_true",
        help=(
            "把已有 Wikimedia 封面正式替换为 AniList 更高置信候选（默认真正写库并更新 "
            "covers_mapping.json；配合 --dry-run 仅预览）"
        ),
    )
    args = parser.parse_args()

    providers = build_resolvers()
    mapping = load_mapping()

    db = SessionLocal()
    try:
        if args.suggest_wikipedia or args.repair_wikipedia:
            anilist_provider = next((p for p in providers if isinstance(p, AniListProvider)), None)
            if anilist_provider is None:
                print("AniList provider 不可用，无法执行 --suggest-wikipedia / --repair-wikipedia")
                return
            if args.suggest_wikipedia:
                suggest_wikipedia_replacements(db, anilist_provider, args.limit)
            else:
                repair_wikipedia_replacements(
                    db,
                    anilist_provider,
                    mapping,
                    args.limit,
                    dry_run=args.dry_run,
                )
            return
        total = db.query(Anime).count()
        # 全量查询后在 Python 中过滤空/占位封面：占位图（如 placehold.co）的 cover
        # 非空，若在 SQL 阶段用 (cover IS NULL OR cover='') 筛选会被提前排除，导致
        # is_placeholder_cover 永远处理不到它们（Stage 9-B 修复）。当前约 1000 条，
        # 全量查询 + Python 过滤足够，无需复杂 SQL。
        rows = db.query(Anime).order_by(Anime.id.asc()).all()
        # 只处理空封面或占位图；已有真实封面绝不覆盖
        rows = [
            a for a in rows
            if not (a.cover or "").strip() or is_placeholder_cover((a.cover or "").strip())
        ]
        pending = len(rows)
        rows = rows[: args.limit]

        print(f"总动漫数: {total}")
        print(f"待处理(空/占位): {pending}（limit={args.limit}）")

        success = 0
        failed = 0
        source_stats: dict[str, int] = {}
        start = time.time()

        for a in rows:
            key = (a.chinese_title or a.title or "").strip()
            item = {
                "title": (a.title or "").strip(),
                "chinese_title": (a.chinese_title or "").strip(),
                "year": a.year,
                "cover": (a.cover or "").strip(),
            }
            time.sleep(REQUEST_DELAY)
            url = resolve_cover(item, providers)
            if url and url.strip():
                src = source_of(url)
                source_stats[src] = source_stats.get(src, 0) + 1
                if not args.dry_run:
                    a.cover = url.strip()
                    db.add(a)
                    mapping[key] = url.strip()
                success += 1
                print(f"  [OK] {key} -> {url[:70]} ({src})")
            else:
                failed += 1
                print(f"  [--] {key} 未找到封面（保留 fallback）")

        if not args.dry_run:
            db.commit()
            save_mapping(mapping)

        print()
        print(f"完成: 成功 {success}，失败 {failed}，耗时 {time.time() - start:.1f}s")
        print(f"来源统计: {source_stats or '无'}")
        print(f"实际数据库更新: {success if not args.dry_run else 0}（dry-run 不写库）" if args.dry_run else f"实际数据库更新: {success}")
        if args.dry_run:
            print("（dry-run 模式，未写库）")
    finally:
        db.close()


if __name__ == "__main__":
    main()

