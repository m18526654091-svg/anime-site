"""AnimeHub Stage9-B 只读测试：AniList 中文标题别名匹配验证（不写数据库）。

用法（在 backend 目录）:
    .venv\\Scripts\\python -m scripts._test_anilist_match

对 12 部目标作品输出：中文标题、year、查询词、top 候选、最终选中、评分与拒绝原因。
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from scripts.covers.anilist import AniListProvider  # noqa: E402

# 目标作品：中文标题 -> 期望的 (AniList seasonYear, format)
TARGETS = {
    "黑子的篮球": (2012, "TV"),
    "冰上的尤里": (2016, "TV"),
    "转生恶役只好拔除破灭旗标": (2020, "TV"),
    "萤火之森": (2011, "MOVIE"),
    "未闻花名": (2011, "TV"),
    "中华小当家": (1997, "TV"),
    "天使的心跳": (2010, "TV"),
    "JOJO的奇妙冒险": (2012, "TV"),
    "灵能百分百": (2016, "TV"),
    "阿松": (2015, "TV"),
    "攻壳机动队SAC": (2002, "TV"),
    "红辣椒": (2006, "MOVIE"),
}


def main() -> None:
    provider = AniListProvider()
    print("=== AniList 中文标题别名匹配测试（只读）===\n")
    passed = 0
    failed = 0
    for cn, (exp_year, exp_format) in TARGETS.items():
        print(f"--- {cn} (期望 {exp_year} {exp_format}) ---")
        try:
            r = provider.search_candidates(cn, cn, exp_year)
            print(f"  查询词: {r['queries']}")
            for c in r.get("rejected", [])[:5]:
                print(f"    rejected: {c.get('romaji')} {c.get('seasonYear')} {c.get('format')} score={c.get('score')}")
            best = r.get("best")
            if best:
                ok = best.get("seasonYear") == exp_year and best.get("format") == exp_format
                mark = "[PASS]" if ok else "[FAIL]"
                print(f"  {mark} BEST: {best.get('romaji')} | id={best.get('id')} idMal={best.get('idMal')} year={best.get('seasonYear')} format={best.get('format')} score={best.get('score')}")
                print(f"    cover: {(best.get('coverImage') or '')[:60]}")
                passed += 1 if ok else 0
                failed += 0 if ok else 1
            else:
                print(f"  [FAIL] 未匹配: {r.get('reject_reason')}")
                failed += 1
        except Exception as exc:  # noqa: BLE001
            print(f"  [FAIL] 异常: {exc}")
            failed += 1
        print()
    print(f"=== 通过 {passed} / {len(TARGETS)}，失败 {failed} ===")


if __name__ == "__main__":
    main()
