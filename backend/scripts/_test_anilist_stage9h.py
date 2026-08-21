"""Stage 9-H 只读测试：7 部目标作品的 AniList 匹配。

每部调用 AniListProvider.search_candidates(title, chinese_title, year)，输出
queries / best romaji / english / seasonYear / format / score / cover。

严格要求：
- seasonYear 与数据库 year 一致
- format 为预期（TV）
- score >= MIN_SCORE
- cover 非空

只读：不写数据库、不写 covers_mapping.json、不触发任何写入。

用法（在 backend 目录）:
    .venv\\Scripts\\python -m scripts._test_anilist_stage9h
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from scripts.covers.anilist import MIN_SCORE, AniListProvider  # noqa: E402

# (title, chinese_title, 数据库 year, 预期 format)
TARGETS = [
    ("学园孤岛", "学园孤岛", 2015, "TV"),
    ("某科学的超电磁炮", "某科学的超电磁炮", 2009, "TV"),
    ("黑之契约者", "黑之契约者", 2007, "TV"),
    ("好想告诉你", "好想告诉你", 2009, "TV"),
    ("灼眼的夏娜", "灼眼的夏娜", 2005, "TV"),
    ("食梦者", "食梦者", 2010, "TV"),
    ("东京喰种", "东京喰种", 2014, "TV"),
]


def main() -> None:
    provider = AniListProvider()
    passed = 0
    for title, cn, year, fmt in TARGETS:
        print(f"\n===== {cn} (year={year} format={fmt}) =====")
        r = provider.search_candidates(title, cn, year)
        print("  queries:", r["queries"])
        best = r.get("best")
        if not best:
            print("  [FAIL] 无达标候选 |", r.get("reject_reason"))
            continue
        print(f"  best romaji : {best.get('romaji')}")
        print(f"  best english: {best.get('english')}")
        print(
            f"  seasonYear  : {best.get('seasonYear')} | format: {best.get('format')} "
            f"| score: {best.get('score')}"
        )
        print(f"  cover       : {best.get('coverImage')}")
        ok_year = best.get("seasonYear") == year
        ok_format = best.get("format") == fmt
        ok_score = best.get("score", 0) >= MIN_SCORE
        ok_cover = bool(best.get("coverImage"))
        ok = ok_year and ok_format and ok_score and ok_cover
        print(
            f"  [check] year={year}: {ok_year} | format={fmt}: {ok_format} "
            f"| score>={MIN_SCORE}: {ok_score} | cover 非空: {ok_cover}"
        )
        print("  RESULT:", "PASS" if ok else "FAIL")
        if ok:
            passed += 1
    print(f"\n===== {passed}/{len(TARGETS)} PASS =====")
    if passed != len(TARGETS):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
