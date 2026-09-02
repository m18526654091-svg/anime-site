"""AnimeHub Phase 44.5 - legacy entity resolution run (read-only).

Reproducible CLI:
    python scripts/phase44_5_legacy_resolve.py [--external]

Reads backend/animehub.db (SELECT only), generates DB candidates for the
115 legacy (Chinese-title) anime, optionally corroborates candidate
identities against the AniList GraphQL API, and writes:
    backend/data/phase44_5_entity_resolution.json
    backend/data/phase44_5_review_queue.json
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys
import time
import urllib.error
import urllib.request
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from entity_resolver import (  # noqa: E402
    CJK,
    de_punct,
    is_brand_substring,
    is_exact_cn,
    resolve_entity,
)

DB_PATH = os.environ.get("ANIMEHUB_DB", os.path.join(os.path.dirname(__file__), "..", "animehub.db"))
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
ANILIST_URL = "https://graphql.anilist.co"
ANILIST_QUERY = """query($s:String){ Media(search:$s,type:ANIME){ id idMal
  title{ romaji english native } startDate{ year month } episodes } }"""

FRANCHISE_KW = [
    ("attack-on-titan", ["attack on titan", "进击的巨人", "進撃の巨人", "shingeki"]),
    ("my-hero-academia", ["my hero academia", "我的英雄学院", "僕のヒーローアカデミア"]),
    ("rezero", ["re:zero", "从零开始", "异世界生活"]),
    ("jujutsu-kaisen", ["jujutsu kaisen", "呪術廻戦", "咒术回战"]),
    ("one-punch-man", ["one punch man", "一拳超人"]),
    ("slime", ["转生史莱姆", "転生したらスライム", "slime"]),
    ("fire-force", ["fire force", "炎炎消防队"]),
    ("gintama", ["gintama", "银魂", "銀魂"]),
    ("haikyuu", ["haikyuu", "排球少年", "ハイキュー"]),
    ("golden-kamuy", ["golden kamuy", "黄金神威"]),
    ("monogatari", ["monogatari", "物语", "物語"]),
    ("bleach", ["bleach", "死神", "千年血战"]),
    ("spy-family", ["spy x family", "spy family", "间谍过家家"]),
    ("frieren", ["frieren", "葬送的芙莉莲", "芙莉莲"]),
    ("mushoku-tensei", ["mushoku", "无职转生"]),
    ("overlord", ["overlord", "不死者之王"]),
    ("one-piece", ["one piece", "海贼王"]),
    ("fate", ["fate", "圣杯"]),
]


def franchise_of(title):
    t = de_punct(title or "").lower()
    for fs, kws in FRANCHISE_KW:
        for kw in kws:
            if kw and de_punct(kw).lower() in t:
                return fs
    return None


def alias_list(raw):
    if not raw:
        return []
    try:
        v = json.loads(raw)
        return v if isinstance(v, list) else []
    except Exception:
        return [x.strip() for x in raw.split(",") if x.strip()]


def load_data():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    cur = db.cursor()
    all_rows = cur.execute("SELECT * FROM anime ORDER BY id").fetchall()
    legacy = [r for r in all_rows if r["title"] and CJK.search(r["title"])]
    english = [r for r in all_rows if r["title"] and not CJK.search(r["title"])]
    return db, legacy, english


def build_candidates(lg, english):
    t = de_punct(lg["title"])
    exact, sub = [], []
    for en in english:
        al = alias_list(en["aliases"])
        if is_exact_cn(lg["title"], en["chinese_title"], al):
            exact.append(en)
        elif is_brand_substring(lg["title"], en["chinese_title"], al):
            sub.append(en)
    seen, out = set(), []
    for grp, kind in ((exact, "exact"), (sub, "brand_substring")):
        for en in grp:
            if en["id"] in seen:
                continue
            seen.add(en["id"])
            out.append({"id": en["id"], "title": en["title"], "slug": en["slug"],
                        "year": en["year"], "episodes": en["episodes"],
                        "anilist_id": en["anilist_id"], "kind": kind})
    return out


def anilist_search(title, timeout=12):
    q = json.dumps({"query": ANILIST_QUERY, "variables": {"s": title}})
    req = urllib.request.Request(ANILIST_URL, data=q.encode(),
                                 headers={"Content-Type": "application/json",
                                          "User-Agent": "AnimeHub-audit/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            m = json.loads(r.read().decode()).get("data", {}).get("Media")
            if not m:
                return {"status": "empty"}
            return {"status": "ok", "anilist_id": m.get("id"), "mal_id": m.get("idMal"),
                    "english": (m.get("title") or {}).get("english"),
                    "native": (m.get("title") or {}).get("native"),
                    "year": (m.get("startDate") or {}).get("year"),
                    "episodes": m.get("episodes"), "source": "anilist"}
    except urllib.error.HTTPError as e:
        return {"status": "http_" + str(e.code)}
    except Exception as e:
        return {"status": "error", "detail": type(e).__name__}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--external", action="store_true", help="corroborate top candidates via AniList")
    args = ap.parse_args()

    db, legacy, english = load_data()
    rows = []
    ext_stats = Counter()
    for lg in legacy:
        cands = build_candidates(lg, english)
        external = {}
        if args.external and cands:
            targets = [c for c in cands if c["kind"] == "exact"][:1] or cands[:1]
            for c in targets:
                ext = anilist_search(c["title"])
                ext_stats[ext["status"]] += 1
                external[c["id"]] = ext
                time.sleep(0.4)
        d = resolve_entity(
            {"id": lg["id"], "title": lg["title"], "year": lg["year"],
             "episodes": lg["episodes"], "franchise": franchise_of(lg["title"]), "slug": lg["slug"]},
            cands, external,
        )
        rows.append({
            "legacy_anime_id": lg["id"], "legacy_title": lg["title"], "legacy_slug": lg["slug"],
            "legacy_year": lg["year"], "legacy_episodes": lg["episodes"],
            "legacy_chinese_title": lg["chinese_title"], "legacy_status": lg["status"],
            "franchise": franchise_of(lg["title"]), "anilist_id": lg["anilist_id"], "mal_id": lg["mal_id"],
            "candidates": cands[:10], "external": external,
            "identity_decision": d["identity_decision"], "confidence": d["confidence"],
            "evidence": d["evidence"], "conflicts": d["conflicts"],
            "priority": d["priority"], "recommended_action": d["recommended_action"],
        })

    decisions = Counter(r["identity_decision"] for r in rows)
    conf = Counter(r["confidence"] for r in rows)
    prio = Counter(r["priority"] for r in rows)
    print("legacy:", len(rows))
    print("decisions:", dict(decisions))
    print("confidence:", dict(conf))
    print("priority:", dict(prio))
    if args.external:
        print("external statuses:", dict(ext_stats))

    os.makedirs(OUT_DIR, exist_ok=True)
    import datetime
    artifact = {"generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
                "source_db": os.path.abspath(DB_PATH), "external": bool(args.external),
                "method": "entity_resolver.resolve_entity; exact=de-punctuated chinese_title/alias equality; brand_substring=containment; external=AniList corroboration",
                "decisions": dict(decisions), "confidence": dict(conf), "priority": dict(prio),
                "reproduce": "python scripts/phase44_5_legacy_resolve.py [--external]"}
    with open(os.path.join(OUT_DIR, "phase44_5_entity_resolution.json"), "w", encoding="utf-8") as f:
        json.dump({"summary": artifact, "pairs": rows}, f, ensure_ascii=False, indent=1)

    q = [r for r in rows if r["identity_decision"] == "MANUAL_REVIEW_REQUIRED"]
    with open(os.path.join(OUT_DIR, "phase44_5_review_queue.json"), "w", encoding="utf-8") as f:
        json.dump({"queue_size": len(q), "items": q}, f, ensure_ascii=False, indent=1)
    print("wrote phase44_5_entity_resolution.json + phase44_5_review_queue.json")
    db.close()


if __name__ == "__main__":
    main()

