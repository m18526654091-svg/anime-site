"""Stage 9-E 只读测试：第三批 11 部作品的 AniList 目标匹配。

对每部调用 AniListProvider.search_candidates(title, chinese_title, year)，输出
queries / best romaji / best english / seasonYear / format / score / cover。

严格要求：
- seasonYear 与数据库 year 一致
- format 为预期（TV）
- score >= MIN_SCORE
- cover 非空

特别注意：游戏王 / 精灵宝可梦 / 棒球大联盟 / 赛马娘 不得误命中其他系列/电影/OVA。

只读：不写数据库、不写 covers_mapping.json、不触发任何写入。

用法（在 backend 目录）:
    .venv\\Scripts\\python -m scripts._test_anilist_stage9e
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from scripts.covers.anilist import MIN_SCORE, AniListProvider  # noqa: E402

# (title, chinese_title, 数据库 year, 预期 format)
# 注：哆啦A梦 1979 在 AniList 分类为 TV_SHORT（每集约 11 分钟的连载形式），非误命中。
TARGETS = [
    ("头文字D", "头文字D", 1998, "TV"),
    ("文豪野犈", "文豪野犬", 2016, "TV"),
    ("哆啦A梦", "哆啦A梦", 1979, "TV_SHORT"),
    ("蜡笔小新", "蜡笔小新", 1992, "TV"),
    ("樱桃小丸子", "樱桃小丸子", 1990, "TV"),
    ("数码宝贝大冒险", "数码宝贝大冒险", 1999, "TV"),
    ("精灵宝可梦", "精灵宝可梦", 1997, "TV"),
    ("游戏王", "游戏王", 2000, "TV"),
    ("网球王子", "网球王子", 2001, "TV"),
    ("棒球大联盟", "棒球大联盟", 2004, "TV"),
    ("赛马娘 Pretty Derby", "赛马娘 Pretty Derby", 2018, "TV"),
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
