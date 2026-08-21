"""Stage 9-G 只读限流稳定性测试：连续 20 次真实 search_candidates。

每次请求间隔由 AniListProvider 内部全局节流（RATE_LIMIT_INTERVAL）控制，
验证 20 次连续请求不出现明显连续失败（AniList 429/burst 限流被规避）。

PASS = best 达标（score >= MIN_SCORE 且 cover 非空）。
输出每次 PASS/FAIL、总成功率。

只读：不写数据库、不写 covers_mapping.json、不触发任何写入。

用法（在 backend 目录）:
    .venv\\Scripts\\python -m scripts._test_anilist_rate_limit
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from scripts.covers.anilist import MIN_SCORE, AniListProvider  # noqa: E402

ROUNDS = 20

# (title, chinese_title, 数据库 year)
TARGETS = [
    ("头文字D", "头文字D", 1998),
    ("文豪野犈", "文豪野犬", 2016),
    ("哆啦A梦", "哆啦A梦", 1979),
    ("蜡笔小新", "蜡笔小新", 1992),
    ("樱桃小丸子", "樱桃小丸子", 1990),
    ("数码宝贝大冒险", "数码宝贝大冒险", 1999),
    ("精灵宝可梦", "精灵宝可梦", 1997),
    ("游戏王", "游戏王", 2000),
    ("网球王子", "网球王子", 2001),
    ("棒球大联盟", "棒球大联盟", 2004),
    ("赛马娘 Pretty Derby", "赛马娘 Pretty Derby", 2018),
]


def main() -> None:
    provider = AniListProvider()
    ok = 0
    for i in range(ROUNDS):
        title, cn, year = TARGETS[i % len(TARGETS)]
        r = provider.search_candidates(title, cn, year)
        best = r.get("best")
        passed = bool(best and best.get("score", 0) >= MIN_SCORE and best.get("coverImage"))
        if passed:
            ok += 1
            print(
                f"  [{i + 1:>2}/20] PASS {cn} (year={year}) "
                f"score={best.get('score')} year={best.get('seasonYear')} format={best.get('format')}"
            )
        else:
            print(f"  [{i + 1:>2}/20] FAIL {cn} (year={year}) -> {r.get('reject_reason')}")

    rate = ok / ROUNDS * 100
    print(f"\n总成功率: {ok}/{ROUNDS} = {rate:.1f}%")
    if ok != ROUNDS:
        print("FAIL：存在失败，请结合上方输出与 429/GraphQL 日志定位。")
        raise SystemExit(1)
    print("PASS：20 次连续请求全部通过。")


if __name__ == "__main__":
    main()
