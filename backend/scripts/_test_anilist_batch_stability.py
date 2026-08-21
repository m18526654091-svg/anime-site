"""Stage 9-F 只读批量稳定性测试：11 部作品连续 3 轮调用 search_candidates。

目的：验证批量回填时 AniList 请求的稳定性（重试 + 退避生效），
而非标题匹配正确性。

每轮对每部调用现有 AniListProvider.search_candidates(title, chinese_title, year)。
PASS = best 达标（score >= MIN_SCORE 且 cover 非空）。
输出每部每轮 PASS/FAIL、每轮成功数、总成功率。

只读：不写数据库、不写 covers_mapping.json、不触发任何写入。

用法（在 backend 目录）:
    .venv\\Scripts\\python -m scripts._test_anilist_batch_stability
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from scripts.covers.anilist import MIN_SCORE, AniListProvider  # noqa: E402

ROUNDS = 3

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
    round_stats: list[int] = []
    total_ok = 0
    total_tries = len(TARGETS) * ROUNDS

    for i in range(ROUNDS):
        ok = 0
        print(f"===== 第 {i + 1} 轮 =====")
        for title, cn, year in TARGETS:
            r = provider.search_candidates(title, cn, year)
            best = r.get("best")
            passed = bool(best and best.get("score", 0) >= MIN_SCORE and best.get("coverImage"))
            if passed:
                ok += 1
                print(
                    f"  [PASS] {cn} (year={year}) score={best.get('score')} "
                    f"year={best.get('seasonYear')} format={best.get('format')}"
                )
            else:
                print(f"  [FAIL] {cn} (year={year}) -> {r.get('reject_reason')}")
        round_stats.append(ok)
        total_ok += ok
        print(f"  第 {i + 1} 轮成功: {ok}/{len(TARGETS)}")

    print()
    for i, s in enumerate(round_stats):
        print(f"  第 {i + 1} 轮: {s}/{len(TARGETS)}")
    rate = total_ok / total_tries * 100 if total_tries else 0.0
    print(f"总成功率: {total_ok}/{total_tries} = {rate:.1f}%")
    if total_ok != total_tries:
        print("FAIL：未达到满轮全通过，请结合输出定位仍失败的条目。")
        raise SystemExit(1)
    print("PASS：11 部 × 3 轮全部通过。")


if __name__ == "__main__":
    main()
