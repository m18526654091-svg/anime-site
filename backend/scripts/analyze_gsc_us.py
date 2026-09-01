"""Phase 40-C — 只读 GSC US 查询分析器（真实数据驱动，绝不伪造）。

用法:
  python scripts/analyze_gsc_us.py --input <real-gsc.csv> [--out <dir>]

行为:
  - 只读输入 CSV；不修改任何页面/DB/元数据
  - 列名规范化（容忍大小写/命名变体）
  - US scope 判定：Country 列=US → YES；无列 → UNKNOWN；绝不按 query 语言推断
  - 行级校验：空行/畸形/重复行统计，不静默丢弃大量数据
  - CTR 由 clicks/impressions 计算（不平均各行 CTR）
  - 输出: 汇总(stdout) + 机会 CSV/JSON/MD（仅当提供了真实输入且 --out 指定）
  - 全部指标标注 Observed / Inferred / Candidate

注意:
  - GSC impressions 是 AnimeHub 专属曝光，NOT 全美搜索量
  - 不输出 monthly search volume / market size
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from collections import Counter, defaultdict

# ---- 列名规范化映射（标准名 -> 可接受变体集合） ----
_COL_ALIASES = {
    "query": {"query", "keyword", "search_query"},
    "page": {"page", "url", "landing_page", "landing page"},
    "clicks": {"clicks", "click"},
    "impressions": {"impressions", "impression"},
    "ctr": {"ctr", "click_through_rate"},
    "position": {"position", "avg_position", "average_position", "average position"},
    "country": {"country", "geo"},
    "date": {"date", "day"},
}
_STD_COLS = ["query", "page", "clicks", "impressions", "ctr", "position"]
_OPT_COLS = ["country", "date", "search_type"]


def normalize_header(raw: str) -> str:
    """把原始表头归一为标准列名（小写、去空白/下划线）。"""
    return re.sub(r"[\s_]+", "_", raw.strip().lower())


def resolve_column(header: list[str]) -> tuple[dict, list[str]]:
    """header(原样) → ({标准列名: 原始列索引}, 缺失必需列列表)。"""
    mapping: dict[str, int] = {}
    normed = [normalize_header(h) for h in header]
    used = set()
    for std, aliases in _COL_ALIASES.items():
        for i, n in enumerate(normed):
            if i in used:
                continue
            if n in aliases or n.startswith(std):
                mapping[std] = i
                used.add(i)
                break
    missing = [c for c in _STD_COLS if c not in mapping]
    return mapping, missing


def parse_ctr(value: str) -> float | None:
    """解析 CTR：'0.039' / '3.9%' / '3.9'（假设为百分比时按 /100）。返回 0-1 或 None。"""
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    try:
        if s.endswith("%"):
            return float(s[:-1]) / 100.0
        f = float(s)
        if f > 1.0:
            return f / 100.0
        return f
    except ValueError:
        return None


def parse_float(value: str) -> float | None:
    try:
        return float(str(value).strip())
    except (ValueError, TypeError):
        return None


def parse_int(value: str) -> int | None:
    try:
        return int(float(str(value).strip()))
    except (ValueError, TypeError):
        return None


def infer_us_scope(rows: list[dict], has_country: bool) -> str:
    """US scope 判定。绝不按 query 语言推断。"""
    if not has_country:
        return "UNKNOWN"
    non_us = [r for r in rows if r.get("country") and str(r["country"]).strip().lower() not in
              ("united states", "us", "usa", "united states of america")]
    if non_us:
        return "NO"
    return "YES"

_INTENT_KEYWORDS = [
    ("episodes", ["episode", "how many episodes"]),
    ("watch_order", ["watch order", "chronological order", "order to watch"]),
    ("characters", ["character", "who is", "voice actor", "cast"]),
    ("where_to_watch", ["where to watch", "streaming", "watch online", "crunchyroll", "netflix"]),
    ("release", ["release date", "airing", "when does", "season", "premiere"]),
    ("similar", ["anime like", "similar anime", "shows like"]),
    ("franchise", ["franchise", "series order", "all seasons"]),
    ("genre", ["best ", "top ", "recommend"]),
    ("entity", ["anime"]),
]


def infer_intent(query: str) -> str:
    """基于 Observed query 推断意图（Inferred）。低置信度归 other。"""
    q = (query or "").lower()
    for intent, kws in _INTENT_KEYWORDS:
        if any(k in q for k in kws):
            return intent
    return "other"


def page_type(page: str) -> str:
    p = page.split("?")[0].lower()
    if "/watch-order/" in p:
        return "watch_order"
    if "/anime-series/" in p:
        return "franchise"
    if "/character/" in p:
        return "character"
    if "/voice-actor/" in p:
        return "voice_actor"
    if "/similar" in p:
        return "similar"
    if "/best-anime/" in p or "/categories/" in p or "/genres" in p:
        return "genre"
    if "/episodes" in p:
        return "episodes"
    if "/anime/" in p or "/years/" in p or "/season" in p:
        return "anime_detail"
    return "other"


def load_csv(path: str) -> tuple[list[dict], dict]:
    """读取 CSV，返回 (规范行, 校验统计)。"""
    stats = {"input_rows": 0, "valid_rows": 0, "invalid_rows": 0,
             "duplicate_rows": 0, "rows_used": 0, "malformed": []}
    rows: list[dict] = []
    try:
        f = open(path, "r", encoding="utf-8-sig", newline="")
    except UnicodeDecodeError:
        f = open(path, "r", encoding="utf-8", newline="")
    with f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header is None:
            raise ValueError("Empty CSV (no header row)")
        mapping, missing = resolve_column(header)
        if missing:
            raise ValueError(f"Missing required columns: {missing}. Found header: {header}")
        seen_keys = set()
        for i, row in enumerate(reader, start=2):
            stats["input_rows"] += 1
            if not row or all(not (c or "").strip() for c in row):
                continue
            try:
                rec = {
                    "query": str(row[mapping["query"]]).strip(),
                    "page": str(row[mapping["page"]]).strip(),
                    "clicks": parse_int(row[mapping["clicks"]]),
                    "impressions": parse_int(row[mapping["impressions"]]),
                    "position": parse_float(row[mapping["position"]]),
                }
                if mapping.get("country") is not None:
                    rec["country"] = str(row[mapping["country"]]).strip()
                if mapping.get("date") is not None:
                    rec["date"] = str(row[mapping["date"]]).strip()
            except Exception:
                stats["invalid_rows"] += 1
                stats["malformed"].append(i)
                continue
            if not rec["query"] or not rec["page"]:
                stats["invalid_rows"] += 1
                stats["malformed"].append(i)
                continue
            if rec["impressions"] is None or rec["clicks"] is None:
                stats["invalid_rows"] += 1
                stats["malformed"].append(i)
                continue
            key = (rec["query"].lower(), rec["page"])
            if key in seen_keys:
                stats["duplicate_rows"] += 1
                continue
            seen_keys.add(key)
            rec["ctr"] = (rec["clicks"] / rec["impressions"]) if rec["impressions"] else 0.0
            rows.append(rec)
    stats["valid_rows"] = len(rows)
    stats["rows_used"] = len(rows)
    return rows, stats
def analyze(rows: list[dict], us_scope: str) -> dict:
    """机会分析（全部为 Inferred 标签；原始字段为 Observed）。"""
    # 1. 赢家：clicks > 0
    winners = [r for r in rows if (r["clicks"] or 0) > 0]
    winners.sort(key=lambda r: -(r["clicks"] or 0))

    # 2. 高曝光低 CTR：impressions >= 20 且 ctr < 0.02 且 position <= 30
    high_imp_low_ctr = [
        r for r in rows
        if (r["impressions"] or 0) >= 20 and (r["ctr"] or 0) < 0.02
        and (r["position"] is None or r["position"] <= 30)
    ]
    high_imp_low_ctr.sort(key=lambda r: -(r["impressions"] or 0))

    # 3. 零点击可见性：impressions >= 20 且 clicks == 0
    zero_click = [r for r in rows if (r["impressions"] or 0) >= 20 and (r["clicks"] or 0) == 0]
    zero_click.sort(key=lambda r: -(r["impressions"] or 0))

    # 4. query -> page 映射 + 冲突检测
    q_pages: dict[str, set] = defaultdict(set)
    p_queries: dict[str, set] = defaultdict(set)
    for r in rows:
        q_pages[r["query"].lower()].add(r["page"])
        p_queries[r["page"]].add(r["query"].lower())
    query_conflicts = {q: sorted(ps) for q, ps in q_pages.items() if len(ps) > 1}
    page_broad = {p: sorted(qs) for p, qs in p_queries.items() if len(qs) >= 5}

    # 5. 意图聚类（Inferred）
    intent_counts: Counter = Counter()
    for r in rows:
        r["intent"] = infer_intent(r["query"])
        r["page_type"] = page_type(r["page"])
        intent_counts[r["intent"]] += 1

    # 6. 优先级队列（Inferred）
    def priority(r):
        imp = r["impressions"] or 0
        pos = r["position"]
        if (r["clicks"] or 0) > 0:
            return (2, -(r["clicks"] or 0))
        if imp >= 20 and pos is not None and pos <= 30 and (r["ctr"] or 0) < 0.02:
            return (1, -imp)
        if imp >= 20 and pos is not None and pos <= 40:
            return (3, -imp)
        return (4, -imp)

    ranked = sorted(rows, key=priority)
    queue = ranked[:10]

    return {
        "winners": winners[:10],
        "high_imp_low_ctr": high_imp_low_ctr[:10],
        "zero_click": zero_click[:10],
        "query_conflicts": dict(list(query_conflicts.items())[:10]),
        "page_broad": dict(list(page_broad.items())[:10]),
        "intent_counts": dict(intent_counts),
        "research_queue": queue,
    }


def write_outputs(out_dir: str, analysis: dict, us_scope: str, rows_used: int) -> None:
    os.makedirs(out_dir, exist_ok=True)

    csv_path = os.path.join(out_dir, "phase40c_us_gsc_opportunities.csv")
    seen = set()
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["query", "page", "clicks", "impressions", "ctr", "position",
                    "intent", "page_type", "evidence_type", "priority", "reason", "next_action"])
        for item in analysis["research_queue"]:
            key = (item["query"], item["page"])
            if key in seen:
                continue
            seen.add(key)
            reason = "existing clicks" if (item["clicks"] or 0) > 0 else (
                "high impressions, low CTR, good position" if (item["impressions"] or 0) >= 20
                and (item["ctr"] or 0) < 0.02 else "ranking opportunity")
            w.writerow([item["query"], item["page"], item["clicks"], item["impressions"],
                        f"{item['ctr']:.4f}", item["position"], item["intent"], item["page_type"],
                        "Inferred", "P1" if (item["clicks"] or 0) > 0 else "P3",
                        reason, "SERP research queue"])

    json_path = os.path.join(out_dir, "phase40c_us_gsc_opportunities.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({
            "us_scope": us_scope,
            "rows_used": rows_used,
            "analysis": analysis,
            "label_note": "GSC fields=Observed; intent/priority=Inferred; actions=Candidate",
            "no_search_volume_claim": True,
        }, f, ensure_ascii=False, indent=2)

    md_path = os.path.join(out_dir, "phase40c_us_gsc_analysis.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# AnimeHub Phase 40-C — US GSC Analysis\n\n")
        f.write(f"## 1. Dataset Scope\n\nUS-scoped: **{us_scope}** (YES/NO/UNKNOWN)\n\n")
        f.write("## 2. Data Quality\n\nRows used: %d. GSC fields are Observed; intent/priority are Inferred.\n\n" % rows_used)
        f.write("## 4. Existing Winners (clicks > 0)\n\n")
        f.write("| query | page | clicks | impressions | ctr | position |\n|---|---|---|---|---|---|\n")
        for r in analysis["winners"]:
            f.write(f"| {r['query']} | {r['page']} | {r['clicks']} | {r['impressions']} | {r['ctr']:.4f} | {r['position']} |\n")
        f.write("\n## 5. High-Impression / Low-CTR\n\n")
        f.write("| query | page | impressions | clicks | ctr | position |\n|---|---|---|---|---|---|\n")
        for r in analysis["high_imp_low_ctr"]:
            f.write(f"| {r['query']} | {r['page']} | {r['impressions']} | {r['clicks']} | {r['ctr']:.4f} | {r['position']} |\n")
        f.write("\n## 6. Zero-Click Visibility\n\n")
        for r in analysis["zero_click"]:
            f.write(f"- {r['query']} ({r['page']}) impressions={r['impressions']} position={r['position']}\n")
        f.write("\n## 9. Intent Clusters (Inferred)\n\n")
        for k, v in sorted(analysis["intent_counts"].items(), key=lambda x: -x[1]):
            f.write(f"- {k}: {v}\n")
        f.write("\n## 10. Priority SERP Research Queue\n\n")
        for i, r in enumerate(analysis["research_queue"], 1):
            f.write(f"{i}. {r['query']} -> {r['page']} (imp={r['impressions']} clicks={r['clicks']} "
                    f"pos={r['position']} intent={r['intent']})\n")
        f.write("\n## 11. Limitations\n\n")
        f.write("- GSC impressions are AnimeHub-specific, not total US search volume.\n")
        f.write("- No search-volume claims. Intent labels are Inferred. Actions are Candidate.\n")
        f.write("- US scope: %s (never inferred from query language).\n" % us_scope)


def main():
    ap = argparse.ArgumentParser(description="Read-only GSC US query analyzer (Phase 40-C)")
    ap.add_argument("--input", required=True, help="Path to real GSC export CSV")
    ap.add_argument("--out", default="", help="Output dir for opportunities CSV/JSON/MD (optional)")
    args = ap.parse_args()

    if not os.path.exists(args.input):
        print(f"[error] input not found: {args.input}")
        sys.exit(1)

    rows, stats = load_csv(args.input)
    has_country = any("country" in r for r in rows)
    us_scope = infer_us_scope(rows, has_country)

    print("== Input validation ==")
    print(f"  input_rows: {stats['input_rows']}")
    print(f"  valid_rows: {stats['valid_rows']}")
    print(f"  invalid_rows: {stats['invalid_rows']}")
    print(f"  duplicate_rows: {stats['duplicate_rows']}")
    print(f"  rows_used: {stats['rows_used']}")
    if stats["malformed"]:
        print(f"  malformed line numbers: {stats['malformed'][:10]}{'...' if len(stats['malformed']) > 10 else ''}")
    print(f"  US scope: {us_scope}")

    if not rows:
        print("[info] No valid rows. Provide a real GSC export (see phase40c_gsc_data_requirements.md).")
        return

    analysis = analyze(rows, us_scope)
    print(f"\n== Summary ==")
    print(f"  winners (clicks>0): {len(analysis['winners'])}")
    print(f"  high-impression/low-CTR: {len(analysis['high_imp_low_ctr'])}")
    print(f"  zero-click (imp>=20): {len(analysis['zero_click'])}")
    print(f"  intent clusters: {analysis['intent_counts']}")
    print(f"  potential query->multi-page: {len(analysis['query_conflicts'])}")
    print(f"  research queue: {len(analysis['research_queue'])}")

    if args.out:
        write_outputs(args.out, analysis, us_scope, stats["rows_used"])
        print(f"\n[written] outputs under {args.out}")


if __name__ == "__main__":
    main()
