"""Stage 12-C.5 最小测试：Wikidata 实体匹配增强逻辑（只读）。"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import scripts.wikidata_entity_match as m  # noqa: E402

# P31 → 类型（模拟 SPARQL 校验结果）
TSM = {
    "Q63952888": "anime",   # animated television series
    "Q1107": "anime",       # anime
    "Q15773317": "anime",   # animated film
    "Q8274": "excluded",    # manga
    "Q21198342": "excluded",  # manga series
    "Q95074": "excluded",   # fictional character
    "Q111045": "excluded",  # light novel
    "Q7889": "unknown",     # television series（宽泛）
    "Q11424": "unknown",    # film（宽泛）
}


def cand(qid, query, texts, p31, wd_year, mal=None, imdb=None):
    return {
        "qid": qid, "query": query, "texts": texts, "p31": p31,
        "wd_year": wd_year,
        "external_ids": {"MAL anime ID": mal, "IMDb ID": imdb},
    }


def test_simplified_title():
    """简繁标题：texts 为繁体 zh label，query 简体 + 别名 → 匹配 → VERIFIED。"""
    # 繁体 zh label（進擊的巨人）+ en label（Attack on Titan），别名命中
    c = cand("Q22126305", "进击的巨人", ["進擊的巨人", "Attack on Titan"], ["Q63952888"], 2013, imdb="tt2560140")
    c["query_aliases"] = m.CH_ALIASES["进击的巨人"]
    st, reason, best = m.classify(2013, [c], TSM)
    assert st == "VERIFIED_CANDIDATE" and best["title_score"] == 100, (st, reason, best)
    print("1. 简繁标题（别名匹配繁体 zh label）PASS")


def test_english_title_hit():
    c = cand("Q2", "Jujutsu Kaisen", ["Jujutsu Kaisen", "咒术回战"], ["Q63952888"], 2020, imdb="tt12343534")
    st, reason, _ = m.classify(2020, [c], TSM)
    assert st == "VERIFIED_CANDIDATE", (st, reason)
    print("2. 英文标题命中 PASS")


def test_manga_rejected():
    c = cand("Q3", "海贼王", ["海贼王", "One Piece"], ["Q21198342"], 1997)
    st, reason, _ = m.classify(1999, [c], TSM)
    assert st == "REJECTED" and "TYPE_MISMATCH" in reason, (st, reason)
    print("3. manga 被拒绝 PASS")


def test_correct_anime_beats_game():
    """进击的巨人：动画实体（繁体 label + type40）应优先于游戏/宽泛实体（简体 label 但 type10）。"""
    anime = cand("Q22126305", "进击的巨人", ["進擊的巨人", "Attack on Titan"], ["Q63952888"], 2013, imdb="tt2560140")
    game = cand("Q20800425", "进击的巨人", ["进击的巨人：人类最后之翼", "Attack on Titan: Humanity in Chains"], ["Q7889"], 2013)
    for c in (anime, game):
        c["query_aliases"] = m.CH_ALIASES["进击的巨人"]
    st, reason, best = m.classify(2013, [anime, game], TSM)
    assert st == "VERIFIED_CANDIDATE" and best["qid"] == "Q22126305", (st, reason, best)
    print("4. 动画实体（繁体 label）优先于宽泛实体 PASS")


def test_tv_series_weighting():
    c1 = cand("Q4", "鬼灭之刃", ["鬼灭之刃"], ["Q63952888"], 2019, imdb="tt9335498")
    st1, _, best1 = m.classify(2019, [c1], TSM)
    assert st1 == "VERIFIED_CANDIDATE" and best1["type_score"] == 40, (st1, best1)
    c2 = cand("Q5", "某剧", ["某剧"], ["Q7889"], 2019, imdb="tt0000000")
    st2, _, best2 = m.classify(2019, [c2], TSM)
    assert best2["type_score"] == 10 and st2 == "REVIEW", (st2, best2)
    print("5. TV series 加权 PASS（animated=40→VERIFIED / 宽泛=10→REVIEW）")


def test_main_series_bonus_and_ambiguous():
    """main series 仅加分排序；两个 main 同分 → AMBIGUOUS。"""
    c1 = cand("Q6", "一拳超人", ["One-Punch Man", "一拳超人"], ["Q63952888"], 2015, imdb="tt4508902")
    c2 = cand("Q7", "一拳超人", ["One-Punch Man Season 2", "一拳超人第二季"], ["Q63952888"], 2019, imdb="tt4508902")
    st, reason, best = m.classify(2015, [c1, c2], TSM)
    # main (c1) 加分后优先，但仅 1 个 main 高分 → 不 ambiguous
    assert st == "VERIFIED_CANDIDATE" and best["qid"] == "Q6", (st, reason)
    # 两个 main 同分 → AMBIGUOUS（season 候选保留参与判定）
    c3 = cand("Q8", "五等分的新娘", ["五等分的新娘", "The Quintessential Quintuplets"], ["Q63952888"], 2019, imdb="tt9584920")
    c4 = cand("Q9", "五等分的新娘", ["五等分的新娘", "Go-Toubun no Hanayome"], ["Q63952888"], 2019, imdb="tt9584920")
    for c in (c3, c4):
        c["query_aliases"] = m.CH_ALIASES["五等分的新娘"]
    st2, reason2, _ = m.classify(2019, [c3, c4], TSM)
    assert st2 == "AMBIGUOUS", (st2, reason2)
    print("6. main series 加分 + 同分 AMBIGUOUS PASS")


def test_score_clamped():
    """compute_final_score 与 main bonus 最终分数必须 clamp 到 0-100。"""
    # 满分维度 → 仍 ≤100
    s = m.compute_final_score(100, 40, 30, 10)
    assert 0 <= s <= 100.0, s
    # main bonus 不使最终分数超过 100（exact+type40+year30+ext10 = 100，+3 后仍 100）
    c = cand("Q10", "火影忍者", ["Naruto", "火影忍者"], ["Q63952888"], 2002, mal=20, imdb="tt0409591")
    st, reason, best = m.classify(2002, [c], TSM)
    assert best["score"] <= 100.0, best["score"]
    assert st == "VERIFIED_CANDIDATE", (st, reason)
    print("score clamp + main bonus ≤100 PASS")


def test_api_error_not_no_match():
    class Fake:
        def __init__(self, id_, title):
            self.id = id_
            self.title = title
            self.chinese_title = title
            self.year = 2013

    per = [{"anime": Fake(1, "进击的巨人"), "cand_refs": {}}]
    res = m._classify_all(per, {}, {}, {1})
    assert res[0]["status"] == "API_ERROR", res[0]
    print("7. API_ERROR 不误判成 NO_MATCH PASS")


if __name__ == "__main__":
    test_simplified_title()
    test_english_title_hit()
    test_manga_rejected()
    test_correct_anime_beats_game()
    test_tv_series_weighting()
    test_main_series_bonus_and_ambiguous()
    test_score_clamped()
    test_api_error_not_no_match()
    print("\nALL TESTS PASS")

