"""Stage 9-C 只读测试：6 部新增 alias 作品的 AniList 目标匹配。

对每部作品输出 AniList 候选（best）的 year / format / score / cover。
只读：不写数据库、不写 covers_mapping.json、不触发任何写入。

用法（在 backend 目录）:
    .venv\\Scripts\\python -m scripts._test_anilist_stage9c
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from scripts.covers.anilist import MIN_SCORE, AniListProvider  # noqa: E402

# (数据库中文标题, 期望 alias, 数据库 year)
TARGETS = [
    ("石纪元", "Dr. Stone", 2019),
    ("五等分的新娘", "5-toubun no Hanayome", 2019),
    ("我的英雄学院", "Boku no Hero Academia", 2016),
    ("名侦探柯南", "Detective Conan", 1996),
    ("钢之炼金术师FA", "Fullmetal Alchemist: Brotherhood", 2009),
    ("叛逆的鲁路修", "Code Geass: Hangyaku no Lelouch", 2006),
]


def main() -> None:
    provider = AniListProvider()
    passed = 0
    for cn, alias, year in TARGETS:
        print(f"\n===== {cn} (期望 alias: {alias}, year={year}) =====")
        r = provider.search_candidates("", cn, year)
        print("  queries:", r["queries"])
        best = r.get("best")
        if not best:
            print("  [FAIL] 无达标候选 |", r.get("reject_reason"))
            continue
        print(f"  best: {best.get('romaji')} / {best.get('english')}")
        print(
            f"  year: {best.get('seasonYear')} | format: {best.get('format')} "
            f"| score: {best.get('score')}"
        )
        print(f"  cover: {best.get('coverImage')}")
        ok = best.get("score", 0) >= MIN_SCORE and bool(best.get("coverImage"))
        print("  RESULT:", "PASS" if ok else "FAIL")
        if ok:
            passed += 1
    print(f"\n===== {passed}/{len(TARGETS)} PASS =====")


if __name__ == "__main__":
    main()
