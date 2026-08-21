"""Stage 9-C 后续只读测试：5 部目标作品的 AniList 匹配（含请求短重试）。

对每部作品输出 AniList 候选（best）的 year / format / score / cover。
只读：不写数据库、不写 covers_mapping.json、不触发任何写入。

用法（在 backend 目录）:
    .venv\\Scripts\\python -m scripts._test_anilist_stage9c2
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from scripts.covers.anilist import MIN_SCORE, AniListProvider  # noqa: E402

# (数据库 title, 数据库 chinese_title, 数据库 year)
TARGETS = [
    ("Fate/stay night UBW", "Fate/stay night UBW", 2014),
    ("中华小当家", "中华小当家", 1997),
    ("天使的心跳", "天使的心跳", 2010),
    ("JOJO的奇妙冒险", "JOJO的奇妙冒险", 2012),
    ("灵能百分百", "灵能百分百", 2016),
]


def main() -> None:
    provider = AniListProvider()
    passed = 0
    for title, cn, year in TARGETS:
        print(f"\n===== {cn} (year={year}) =====")
        r = provider.search_candidates(title, cn, year)
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
