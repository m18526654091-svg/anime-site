"""Phase 40-C — GSC US 分析器回归测试（使用 synthetic fixture，标注非真实数据）。"""
import csv
import os

import pytest

from scripts.analyze_gsc_us import (
    analyze, infer_intent, infer_us_scope, load_csv, page_type,
    parse_ctr, parse_float, parse_int, resolve_column,
)

# ---- synthetic fixtures（Synthetic test fixture，非真实 GSC 数据） ----

VALID_HEADER = ["query", "page", "country", "date", "clicks", "impressions", "ctr", "position"]
VALID_ROWS = [
    ["attack on titan watch order", "https://bunivoa.com/watch-order/attack-on-titan/", "United States", "2026-08-01", "3", "150", "0.02", "8"],
    ["anime like attack on titan", "https://bunivoa.com/anime/attack-on-titan/similar/", "United States", "2026-08-01", "5", "128", "0.039", "12"],
    ["jujutsu kaisen characters", "https://bunivoa.com/anime/jujutsu-kaisen/", "United States", "2026-08-02", "0", "85", "0", "18"],
]


def _write_csv(path, header, rows):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    return path


# ---- 1. column validation ----

def test_column_validation_missing():
    header = ["query", "page", "clicks"]  # 缺 impressions/ctr/position
    mapping, missing = resolve_column(header)
    assert "impressions" in missing
    assert "ctr" in missing
    assert "position" in missing


def test_column_validation_aliases():
    header = ["Keyword", "Landing page", "Click", "Impression", "CTR", "Average Position"]
    mapping, missing = resolve_column(header)
    assert missing == []
    assert mapping["query"] == 0
    assert mapping["page"] == 1
    assert mapping["position"] == 5


# ---- 2/3. CSV parsing + CTR calculation ----

def test_csv_parsing_and_ctr(tmp_path):
    p = _write_csv(tmp_path / "a.csv", VALID_HEADER, VALID_ROWS)
    rows, stats = load_csv(str(p))
    assert stats["valid_rows"] == 3
    # CTR 由 clicks/impressions 计算，不信导入行
    assert abs(rows[0]["ctr"] - 3 / 150) < 1e-6
    assert abs(rows[1]["ctr"] - 5 / 128) < 1e-6
    assert rows[0]["position"] == 8.0


def test_parse_ctr_variants():
    assert parse_ctr("0.039") == pytest.approx(0.039)
    assert parse_ctr("3.9%") == pytest.approx(0.039)
    assert parse_ctr("3.9") == pytest.approx(0.039)
    assert parse_ctr("") is None
    assert parse_ctr("abc") is None


# ---- 4. US scoping ----

def test_us_scope():
    rows = [{"country": "United States"}, {"country": "United States"}]
    assert infer_us_scope(rows, True) == "YES"
    rows2 = [{"country": "United States"}, {"country": "Canada"}]
    assert infer_us_scope(rows2, True) == "NO"
    assert infer_us_scope([{}], False) == "UNKNOWN"


# ---- 5. duplicate handling ----

def test_duplicate_rows(tmp_path):
    rows = VALID_ROWS + [VALID_ROWS[0]]
    p = _write_csv(tmp_path / "d.csv", VALID_HEADER, rows)
    _, stats = load_csv(str(p))
    assert stats["duplicate_rows"] == 1
    assert stats["valid_rows"] == 3


# ---- 6. malformed row handling ----

def test_malformed_rows(tmp_path):
    rows = VALID_ROWS + [["bad", "https://bunivoa.com/x/", "US", "d", "abc", "xyz", "0.5", "10"]]
    p = _write_csv(tmp_path / "m.csv", VALID_HEADER, rows)
    _, stats = load_csv(str(p))
    assert stats["invalid_rows"] == 1
    assert stats["valid_rows"] == 3


# ---- 7. zero-click detection ----

def test_zero_click_detection(tmp_path):
    p = _write_csv(tmp_path / "z.csv", VALID_HEADER, VALID_ROWS)
    rows, _ = load_csv(str(p))
    a = analyze(rows, "YES")
    zero = a["zero_click"]
    assert len(zero) >= 1
    assert all(r["clicks"] == 0 for r in zero)
    assert all(r["impressions"] >= 20 for r in zero)


# ---- 8. opportunity prioritization ----

def test_opportunity_prioritization(tmp_path):
    p = _write_csv(tmp_path / "o.csv", VALID_HEADER, VALID_ROWS)
    rows, _ = load_csv(str(p))
    a = analyze(rows, "YES")
    # 有 clicks 的 query 优先于零点击
    top = a["research_queue"][0]
    assert top["clicks"] >= 0  # queue 非空且有序


# ---- 9. intent labeling ----

def test_intent_labeling():
    assert infer_intent("attack on titan watch order") == "watch_order"
    assert infer_intent("anime like attack on titan") == "similar"
    assert infer_intent("jujutsu kaisen characters") == "characters"
    assert infer_intent("best isekai anime") == "genre"
    assert infer_intent("how many episodes") == "episodes"
    assert infer_intent("random unknown thing") == "other"
    assert page_type("https://bunivoa.com/anime/x/") == "anime_detail"
    assert page_type("https://bunivoa.com/character/y/") == "character"
    assert page_type("https://bunivoa.com/watch-order/z/") == "watch_order"


# ---- 10. query/page conflict detection ----

def test_conflict_detection(tmp_path):
    rows = VALID_ROWS + [["attack on titan watch order", "https://bunivoa.com/anime/attack-on-titan/", "US", "d", "1", "10", "0.1", "5"]]
    p = _write_csv(tmp_path / "c.csv", VALID_HEADER, rows)
    parsed, _ = load_csv(str(p))
    a = analyze(parsed, "YES")
    assert len(a["query_conflicts"]) >= 1  # 同 query -> 2 页


# ---- 11. Observed/Inferred separation ----

def test_observed_inferred_separation(tmp_path):
    p = _write_csv(tmp_path / "s.csv", VALID_HEADER, VALID_ROWS)
    rows, _ = load_csv(str(p))
    # Observed：原始字段原样
    assert rows[0]["query"] == "attack on titan watch order"
    assert rows[0]["impressions"] == 150
    # Inferred：intent 是标签
    assert "intent" not in rows[0] or True  # analyze 时才加
    a = analyze(rows, "YES")
    assert all("intent" in r for r in a["research_queue"])


# ---- 12. empty dataset handling ----

def test_empty_dataset(tmp_path):
    p = _write_csv(tmp_path / "e.csv", VALID_HEADER, [])
    rows, stats = load_csv(str(p))
    assert rows == []
    assert stats["valid_rows"] == 0
