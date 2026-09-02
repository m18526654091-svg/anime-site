"""Phase 44.5 - entity matcher adversarial tests (pure functions, no DB/net).

Cases mirror Phase 44.5 section 18: same-title/different-year, movie-vs-TV,
sequel-vs-original, season-vs-aggregate, remake, same-franchise/different
work, unreliable episode count, external-source failure, no candidate.
Precision: the matcher must never auto-verify an ambiguous pair.
"""
import pytest

from scripts.entity_resolver import (
    VERIFIED,
    MANUAL,
    UNRESOLVED,
    HIGH,
    MEDIUM,
    LOW,
    NONE,
    de_punct,
    infer_type,
    is_exact_cn,
    resolve_entity,
)

E = dict  # shorthand


def L(id_, title, year=None, episodes=None, franchise=None):
    return {"id": id_, "title": title, "year": year, "episodes": episodes,
            "franchise": franchise, "slug": title}


def C(id_, title, year, episodes=None, kind="exact", anilist_id=None):
    return {"id": id_, "title": title, "slug": title, "year": year,
            "episodes": episodes, "anilist_id": anilist_id, "kind": kind}


def test_de_punct_normalizes_cn():
    assert de_punct("为美好的世界献上祝福！") == "为美好的世界献上祝福"
    assert de_punct("排球少年！！") == "排球少年"


def test_infer_type_movie_vs_tv():
    assert infer_type("Attack on Titan") == "tv"
    assert infer_type("KonoSuba Movie") == "movie"
    assert infer_type("鬼灭之刃剧场版") == "movie"


def test_exact_cn_only_when_equal():
    assert is_exact_cn("为美好的世界献上祝福", "为美好的世界献上祝福", []) is True
    assert is_exact_cn("为美好的世界献上祝福", "为美好的世界献上祝福剧场版", []) is False
    assert is_exact_cn("日常", "悠哉日常大王", []) is False


def test_verified_with_external_agreeing():
    legacy = L(31, "为美好的世界献上祝福", 2016, 12)
    cands = [C(136, "Konosuba", 2016, 10)]
    ext = {136: {"status": "ok", "source": "anilist", "anilist_id": 21202, "year": 2016}}
    d = resolve_entity(legacy, cands, ext)
    assert d["identity_decision"] == VERIFIED
    assert d["confidence"] == MEDIUM
    assert d["recommended_action"] == "FUTURE_CONSOLIDATION_CANDIDATE"


def test_single_exact_no_external_is_manual_not_verified():
    legacy = L(31, "为美好的世界献上祝福", 2016, 12)
    cands = [C(136, "Konosuba", 2016, 10)]
    d = resolve_entity(legacy, cands, None)
    assert d["identity_decision"] == MANUAL  # never auto-verify w/o external
    assert d["priority"] == "P0" or d["priority"] == "P1"


def test_same_title_different_year_not_verified():
    legacy = L(99, "某作品", 2016, 12)
    cands = [C(500, "Some Anime", 2024, 12)]
    ext = {500: {"status": "ok", "source": "anilist", "anilist_id": 1, "year": 2024}}
    d = resolve_entity(legacy, cands, ext)
    assert d["identity_decision"] == MANUAL
    assert any("year" in c for c in d["conflicts"])


def test_movie_vs_tv_conflict_blocks_verify():
    legacy = L(5, "某个 TV 系列", 2016, 12)
    cands = [C(600, "Some Movie", 2016, 1)]  # movie candidate
    ext = {600: {"status": "ok", "source": "anilist", "anilist_id": 2, "year": 2016}}
    d = resolve_entity(legacy, cands, ext)
    assert d["identity_decision"] == MANUAL
    assert any("type" in c for c in d["conflicts"])


def test_sequel_vs_original_not_auto_verified():
    # exact alias but candidate is a sequel entry (episodes/season hint)
    legacy = L(1, "进击的巨人", 2013, 87)  # aggregate legacy
    cands = [C(164, "Attack on Titan Final Season", 2020, 16)]
    ext = {164: {"status": "ok", "source": "anilist", "anilist_id": 110277, "year": 2020}}
    d = resolve_entity(legacy, cands, ext)
    assert d["identity_decision"] == MANUAL  # year 2013 vs 2020 blocks verify


def test_episode_mismatch_alone_does_not_block_verify():
    # exact + year agree + external agree, eps differs (legacy unreliable) -> verified with note
    legacy = L(57, "日常", 2011, 12)
    cands = [C(101, "Nichijou - My Ordinary Life", 2011, 26)]
    ext = {101: {"status": "ok", "source": "anilist", "anilist_id": 10165, "year": 2011}}
    d = resolve_entity(legacy, cands, ext)
    assert d["identity_decision"] == VERIFIED
    eps_conf = [c for c in d["conflicts"] if "episodes" in c]
    assert eps_conf, "episode mismatch must be recorded"


def test_multiple_exact_candidates_ambiguous():
    legacy = L(8, "葬送的芙莉莲", 2023, 12)
    cands = [C(173, "Frieren Season 2", 2024), C(441, "Frieren", 2023)]
    d = resolve_entity(legacy, cands, None)
    assert d["identity_decision"] == MANUAL
    assert d["priority"] == "P0"


def test_brand_substring_many_is_manual_low():
    legacy = L(4, "海贼王", 1999, 12)
    cands = [C(i, f"One Piece {n}", 2020 + i, kind="brand_substring") for i, n in
             enumerate(["East Blue", "Film Red", "Fan Letter", "Season 2"])]
    d = resolve_entity(legacy, cands, None)
    assert d["identity_decision"] == MANUAL
    assert d["confidence"] == LOW


def test_no_candidate_unresolved():
    legacy = L(19, "灌篮高手", 1993, 12)
    d = resolve_entity(legacy, [], None)
    assert d["identity_decision"] == UNRESOLVED
    assert d["confidence"] == NONE


def test_external_failure_not_upgraded():
    legacy = L(57, "日常", 2011, 12)
    cands = [C(101, "Nichijou - My Ordinary Life", 2011, 26)]
    ext = {101: {"status": "http_429"}}  # rate-limited
    d = resolve_entity(legacy, cands, ext)
    assert d["identity_decision"] == MANUAL  # failure must NOT promote to verified


def test_same_franchise_distinct_work_not_collapsed():
    # same franchise, clearly different season works - never verified without exact+year
    legacy = L(5, "火影忍者", 2002, 12)
    cands = [C(733, "Naruto Shippuden", 2007, kind="brand_substring"),
             C(734, "Naruto Movie 1", 2007, kind="brand_substring")]
    d = resolve_entity(legacy, cands, None)
    assert d["identity_decision"] == MANUAL
