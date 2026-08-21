"""Stage 9-C 只读测试：--repair-wikipedia 安全性。

验证当前所有 Wikimedia 封面中，将被 --repair-wikipedia 建议替换的候选
都满足：score >= MIN_SCORE 且 coverImage 非空 且与当前 URL 不同；
确保不会把封面错误替换成低于 MIN_SCORE 的低置信候选。

只读：不写数据库、不写 covers_mapping.json、不触发写入。

用法（在 backend 目录）:
    .venv\\Scripts\\python -m scripts._test_repair_wikipedia
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from app.database import SessionLocal  # noqa: E402
from scripts.covers.anilist import MIN_SCORE, AniListProvider  # noqa: E402
from scripts.fetch_missing_covers import _anilist_best, _wikipedia_rows  # noqa: E402


def main() -> None:
    db = SessionLocal()
    try:
        rows = _wikipedia_rows(db, 0)
        print(f"Wikimedia 封面数: {len(rows)}")
        anilist = AniListProvider()
        suggested = 0
        bad: list[tuple[str, float]] = []
        for a in rows:
            key = (a.chinese_title or a.title or "").strip()
            best = _anilist_best(anilist, a)
            if not best:
                print(f"  [SKIP] {key}: 无达标候选")
                continue
            if best["coverImage"] == (a.cover or "").strip():
                print(f"  [SKIP] {key}: 候选与当前相同")
                continue
            sc = best.get("score", 0)
            suggested += 1
            print(
                f"  [建议] {key}: score={sc} year={best.get('seasonYear')} "
                f"format={best.get('format')} cover={bool(best.get('coverImage'))}"
            )
            if sc < MIN_SCORE or not best.get("coverImage"):
                bad.append((key, sc))

        print(f"\n建议替换: {suggested} | 低于 MIN_SCORE 或缺失封面: {len(bad)}")
        if bad:
            print("FAIL:", bad)
            raise SystemExit(1)
        print("PASS：所有建议替换候选 score >= MIN_SCORE 且封面非空")
    finally:
        db.close()


if __name__ == "__main__":
    main()
