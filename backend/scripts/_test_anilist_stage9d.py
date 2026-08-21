"""Stage 9-D 只读测试：暗杀教室 AniList 目标匹配。

必须命中：
- year == 2015
- format == TV
- score >= MIN_SCORE(60)
- cover 非空

只读：不写数据库、不写 covers_mapping.json、不触发任何写入。

用法（在 backend 目录）:
    .venv\\Scripts\\python -m scripts._test_anilist_stage9d
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from scripts.covers.anilist import MIN_SCORE, AniListProvider  # noqa: E402

TARGET_TITLE = "暗杀教室"
TARGET_YEAR = 2015
TARGET_FORMAT = "TV"


def main() -> None:
    provider = AniListProvider()
    print(f"===== {TARGET_TITLE} (期望 year={TARGET_YEAR} format={TARGET_FORMAT}) =====")
    r = provider.search_candidates(TARGET_TITLE, TARGET_TITLE, TARGET_YEAR)
    print("  queries:", r["queries"])
    best = r.get("best")
    if not best:
        print("  [FAIL] 无达标候选 |", r.get("reject_reason"))
        raise SystemExit(1)
    print(f"  best: {best.get('romaji')} / {best.get('english')}")
    print(
        f"  year: {best.get('seasonYear')} | format: {best.get('format')} "
        f"| score: {best.get('score')}"
    )
    print(f"  cover: {best.get('coverImage')}")

    ok_year = best.get("seasonYear") == TARGET_YEAR
    ok_format = best.get("format") == TARGET_FORMAT
    ok_score = best.get("score", 0) >= MIN_SCORE
    ok_cover = bool(best.get("coverImage"))
    print(f"  [check] year={TARGET_YEAR}: {ok_year} | format={TARGET_FORMAT}: {ok_format} "
          f"| score>={MIN_SCORE}: {ok_score} | cover 非空: {ok_cover}")
    if ok_year and ok_format and ok_score and ok_cover:
        print("  RESULT: PASS")
    else:
        print("  RESULT: FAIL")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
