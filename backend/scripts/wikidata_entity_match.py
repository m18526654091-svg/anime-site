"""Stage 12-C: Wikidata QID 实体匹配（只读验证，20 部）。

为 AnimeHub 生产前 20 部建立 Wikidata 候选实体匹配：候选搜索 → 本地评分 →
P31 类型校验 → 外部 ID 读取 → 审核报告。

只读安全：0 INSERT / 0 UPDATE / 0 DELETE，不写 external_entities / anilist_id / mal_id。

用法（在 backend 目录）:
    .venv\\Scripts\\python -m scripts.wikidata_entity_match [--limit N]
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from app.database import SessionLocal  # noqa: E402
from app.models import Anime  # noqa: E402

UA = {"User-Agent": "AnimeHub-Stage12C/1.0 (readonly verification; contact admin@animehub.local)"}

WIKI_SEARCH = "https://www.wikidata.org/w/api.php"
WIKI_ENTITY = "https://www.wikidata.org/w/api.php"
SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"

# 允许的动画实体类型（P279 传递闭包命中即视为动画）
ANIME_TYPES = {
    "Q1107",       # anime
    "Q63952888",   # animated television series
    "Q15773317",   # animated film
    "Q45382",      # original video animation
    "Q634117",     # original net animation
}
# 明确排除的类型（命中即 manga/novel/character）
EXCLUDED_TYPES = {
    "Q8274",     # manga
    "Q111045",   # light novel
    "Q482994",   # novel
    "Q95074",    # fictional character
    "Q1789252",  # comic
    "Q21198342", # manga series
    "Q742345",   # comic series
}

# 外部 ID 属性
EXTERNAL_PROPS = {
    "P4086": "MAL anime ID",
    "P5800": "MAL manga ID",
    "P345": "IMDb ID",
    "P1985": "ANN anime ID",
    "P856": "official website",
    "P577": "publication date",
    "P580": "inception/start time",
}


def normalize_title(s: str) -> str:
    """统一标题归一化：大小写、全半角、标点、空格、简繁（zh-hans 优先已在 texts 收集）。"""
    s = (s or "").strip().lower()
    # 全角 → 半角
    s = s.replace("！", "!").replace("：", ":").replace("（", "(").replace("）", ")")
    s = s.replace("・", "").replace("·", "").replace("×", "x")
    s = re.sub(r"[\s\-_:/:!?？，,、.．。()（）\[\]【】「」『』]+", "", s)
    return s


# 简体标题 → 繁体/英文/罗马音别名（用于匹配 Wikidata 繁体 zh label 与 en label）
CH_ALIASES: dict[str, list[str]] = {
    "进击的巨人": ["進擊的巨人", "Attack on Titan"],
    "鬼灭之刃": ["鬼滅之刃", "Demon Slayer", "Kimetsu no Yaiba"],
    "咒术回战": ["咒術迴戰", "Jujutsu Kaisen"],
    "海贼王": ["航海王", "One Piece"],
    "火影忍者": ["Naruto"],
    "间谍过家家": ["SPY×FAMILY", "Spy x Family"],
    "电锯人": ["鏈鋸人", "Chainsaw Man"],
    "葬送的芙莉莲": ["葬送的芙莉蓮", "Frieren"],
    "我推的孩子": ["【我推的孩子】", "Oshi no Ko"],
    "孤独摇滚": ["孤獨搖滾", "Bocchi the Rock"],
    "辉夜大小姐想让我告白": ["輝夜姬想讓人告白", "Kaguya-sama: Love Is War"],
    "石纪元": ["Dr. Stone", "Dr.STONE"],
    "约定的梦幻岛": ["約定的夢幻島", "The Promised Neverland"],
    "五等分的新娘": ["五等分的花嫁", "The Quintessential Quintuplets", "Go-Toubun no Hanayome"],
    "刀剑神域": ["刀劍神域", "Sword Art Online"],
    "一拳超人": ["One-Punch Man"],
    "我的英雄学院": ["我的英雄學院", "My Hero Academia", "Boku no Hero Academia"],
    "排球少年": ["排球少年", "Haikyu!!"],
    "灌篮高手": ["灌籃高手", "Slam Dunk"],
    "黑子的篮球": ["黑子的籃球", "Kuroko's Basketball"],
}


def title_score(query: str, texts: list[str], extra_queries: list[str] | None = None) -> float:
    """标题评分：exact 100 / strong contains 80 / all tokens 55 / partial 35 / 0。

    extra_queries：简体标题对应的繁体/英文别名，用于匹配 Wikidata 繁体 zh label 与 en label。
    """
    queries = [q for q in ([query] + (extra_queries or [])) if normalize_title(q)]
    best = 0.0
    for q in queries:
        ql = normalize_title(q)
        if not ql:
            continue
        for t in texts:
            tl = normalize_title(t)
            if not tl:
                continue
            if tl == ql:
                best = max(best, 100.0)
            elif ql in tl or tl in ql:
                best = max(best, 80.0)
            elif all(w in tl for w in ql.split()):
                best = max(best, 55.0)
            elif any(w in tl for w in ql.split()):
                best = max(best, 35.0)
    return best


def year_delta(anime_year, wd_year) -> int:
    if not anime_year or not wd_year:
        return 0
    diff = abs(int(anime_year) - int(wd_year))
    if diff == 0:
        return 30
    if diff <= 1:
        return 15
    if diff > 2:
        return -30
    return 0


# 宽泛类型（非动画专属）：TV series / film / tv program
BROAD_TYPES = {"Q7889", "Q11424", "Q196600", "Q5398426", "Q15416", "Q24862"}
# 多季标识（用于优先 main series）
SEASON_MARKERS = re.compile(r"(season|第\s*\d+\s*季|第\d+期|s\s*\d+|2nd|part\s*2|\bii\b|\biii\b|second)", re.I)


def type_score(p31: list, type_status_map: dict) -> tuple[int, bool]:
    """动画类型评分。返回 (type_score, is_excluded)。

    - 任一 P31 明确动画（SPARQL 判定 anime）→ 40
    - 任一 P31 漫画/小说/角色（excluded）且无动画 → 强制拒绝
    - 仅宽泛类型（TV series / film）→ 10
    - 其他 → 0
    """
    has_anime = False
    has_broad = False
    has_other = False
    for p in p31:
        st = type_status_map.get(p)
        if st == "anime":
            has_anime = True
        elif st == "excluded":
            continue  # 若同时有动画 P31，以动画为准；纯漫画在下方拒绝
        elif p in BROAD_TYPES:
            has_broad = True
        else:
            has_other = True
    if has_anime:
        return 40, False
    # 纯漫画/小说/角色（所有 P31 均被排除，无动画）
    if p31 and all(type_status_map.get(p) == "excluded" for p in p31):
        return 0, True
    if has_broad:
        return 10, False
    return 0, False


def external_score(ext: dict) -> int:
    mal = ext.get("MAL anime ID") or ext.get("MAL manga ID")
    imdb = ext.get("IMDb ID")
    if mal and imdb:
        return 10
    if mal or imdb:
        return 5
    return 0


def is_season_candidate(texts: list[str]) -> bool:
    return any(SEASON_MARKERS.search(t) for t in texts)


def compute_final_score(title_score_v, type_score_v, year_delta_v, ext_score_v) -> float:
    """加权总分（0-100，clamp）：title 50% + type 25% + year 15% + external 10%。"""
    title_part = title_score_v * 0.5
    type_part = type_score_v * 0.625  # /40 * 25
    year_part = (year_delta_v + 30) / 60.0 * 15.0  # -30→0, +30→15
    ext_part = float(ext_score_v)
    total = title_part + type_part + year_part + ext_part
    # 最终统一 clamp 到 0-100（报告 score / confidence 必须 0-100）
    return round(max(0.0, min(100.0, total)), 1)


def extract_year(claim_value) -> int | None:
    """从 Wikidata 日期值（如 +2013-00-00T00:00:00Z）提取年份。"""
    if not claim_value:
        return None
    m = re.match(r"^[+-]?(\d{4})", str(claim_value))
    return int(m.group(1)) if m else None


def classify(anime_year, candidates: list[dict], type_status_map: dict | None = None) -> tuple[str, str, dict | None]:
    """综合判定（Stage 12-C.5 加权评分 + 多季处理）。返回 (status, reason, best)。

    评分：title 50% + type 25% + year 15% + external 10%。
    阈值：>=85 VERIFIED_CANDIDATE / 70-84 REVIEW / <70 REJECTED。
    """
    tsm = type_status_map or {}
    if not candidates:
        return "NO_MATCH", "请求成功但无候选", None

    # 1. 评分
    for c in candidates:
        c["title_score"] = float(title_score(c.get("query") or "", c.get("texts") or [],
                                              c.get("query_aliases") or []))
        c["year_delta"] = year_delta(anime_year, c.get("wd_year"))
        ts, excluded = type_score(c.get("p31") or [], tsm)
        c["type_score"] = ts
        c["is_excluded"] = excluded
        c["ext_score"] = external_score(c.get("external_ids") or {})
        c["score"] = compute_final_score(c["title_score"], ts, c["year_delta"], c["ext_score"])
        # main series 仅作排序加分（不剔除 season 候选；不允许单独触发 VERIFIED）
        if not is_season_candidate(c.get("texts") or []):
            c["score"] = round(min(100.0, c["score"] + 3.0), 1)
            c["main_bonus"] = 3.0

    candidates.sort(key=lambda c: c["score"], reverse=True)
    best = candidates[0]
    second = candidates[1] if len(candidates) > 1 else None

    # 3. 漫画/小说/角色：强制拒绝
    if best.get("is_excluded"):
        return "REJECTED", f"TYPE_MISMATCH: 实体类型被排除({best.get('p31', [])})", best

    # 4. ambiguous：top1 与 top2 接近（且都非被排除）
    if second is not None and not second.get("is_excluded") and best["score"] - second["score"] <= 3:
        return "AMBIGUOUS", f"top1={best['score']} top2={second['score']}（多候选接近）", best

    # 5. 阈值判定
    if best["score"] >= 85 and best["title_score"] >= 80:
        return "VERIFIED_CANDIDATE", (
            f"score={best['score']} title={best['title_score']} type={best['type_score']} "
            f"year_delta={best['year_delta']} ext={best['ext_score']}"
        ), best
    if best["score"] >= 70:
        return "REVIEW", f"score={best['score']} 需人工确认", best
    return "REJECTED", f"score={best['score']} 低置信", best


def wb_search(q: str, lang: str) -> list:
    """Wikidata Search API。返回 hit 列表或 [{"_error": ...}]。"""
    url = (
        f"{WIKI_SEARCH}?action=wbsearchentities"
        f"&search={urllib.parse.quote(q)}&language={lang}&uselang=zh&format=json&limit=5"
    )
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode("utf-8")).get("search", [])
    except Exception as exc:  # noqa: BLE001 - 403/429/timeout/5xx 网络错误
        return [{"_error": f"{type(exc).__name__}: {exc}"}]


def wb_get(qids: list[str]) -> dict:
    """Wikidata Entity API（批量）。ids 必须用 %7C（|）分隔，逗号不被识别。"""
    url = (
        f"{WIKI_ENTITY}?action=wbgetentities&ids={'%7C'.join(qids)}"
        "&props=labels|descriptions|aliases|claims|sitelinks"
        "&format=json&languages=zh-hans|zh-hant|zh|en|ja"
    )
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as exc:  # noqa: BLE001
        return {"_error": f"{type(exc).__name__}: {exc}"}


def sparql_p31_ancestors(p31_qids: list[str]) -> dict:
    """用一条 SPARQL 查询所有候选 P31 的 P279 传递闭包，判断类型。

    返回 {p31_qid: "anime" | "excluded" | "unknown"}。
    仅小规模使用（本阶段 20 部），不建逐条 SPARQL 架构。
    """
    if not p31_qids:
        return {}
    values = " ".join(f"wd:{q}" for q in p31_qids)
    allowed = " ".join(f"wd:{q}" for q in ANIME_TYPES | EXCLUDED_TYPES)
    sparql = (
        "SELECT ?type ?ancestor WHERE { "
        f"VALUES ?type {{ {values} }} "
        "?type wdt:P279* ?ancestor . "
        f"VALUES ?ancestor {{ {allowed} }} "
        "}"
    )
    url = SPARQL_ENDPOINT + "?query=" + urllib.parse.quote(sparql) + "&format=json"
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read().decode("utf-8"))
    except Exception:  # noqa: BLE001 - 类型校验失败按 unknown 处理，不阻断
        return {q: "unknown" for q in p31_qids}

    result: dict[str, str] = {}
    bindings = ((data or {}).get("results") or {}).get("bindings") or []
    for b in bindings:
        t = (b.get("type") or {}).get("value", "").split("/")[-1]
        a = (b.get("ancestor") or {}).get("value", "").split("/")[-1]
        if not t or not a:
            continue
        if a in ANIME_TYPES:
            result.setdefault(t, "anime")
        elif a in EXCLUDED_TYPES:
            result.setdefault(t, "excluded")
    for q in p31_qids:
        result.setdefault(q, "unknown")
    return result


REPORT_MD, REPORT_JSON = "", ""


def main() -> None:
    parser = argparse.ArgumentParser(description="Wikidata QID 实体匹配（只读）")
    parser.add_argument("--limit", type=int, default=20, help="最多处理条数")
    parser.add_argument("--report-suffix", default="stage12c5", help="报告文件后缀")
    args = parser.parse_args()

    global REPORT_MD, REPORT_JSON
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # backend/
    REPORT_MD = os.path.join(base, "data", f"{args.report_suffix}_wikidata_report.md")
    REPORT_JSON = os.path.join(base, "data", f"{args.report_suffix}_wikidata_report.json")

    db = SessionLocal()
    rows = db.query(Anime).order_by(Anime.id.asc()).limit(args.limit).all()
    print(f"处理 Anime 前 {len(rows)} 部（只读）")
    db.close()

    all_entities: dict[str, dict] = {}
    per_anime: list[dict] = []
    api_error_anime: set[int] = set()

    # ---- 1. 候选搜索（zh + en） ----
    for a in rows:
        queries = []
        for q in ((a.chinese_title or "").strip(), (a.title or "").strip()):
            if q and q not in queries:
                queries.append(q)
        cand_refs: dict[str, dict] = {}
        got_error = False
        for q in queries:
            for lang in ("zh", "en"):
                hits = wb_search(q, lang)
                time.sleep(0.25)
                if hits and "_error" in hits[0]:
                    got_error = True
                    continue
                for h in hits[:5]:
                    qid = h.get("id")
                    if not qid:
                        continue
                    cand_refs.setdefault(qid, {
                        "qid": qid, "query": q,
                        "search_label": h.get("label", ""),
                        "search_desc": h.get("description", ""),
                    })
        if got_error and not cand_refs:
            api_error_anime.add(a.id)
        per_anime.append({"anime": a, "cand_refs": cand_refs, "queries": queries})
        for qid in cand_refs:
            all_entities.setdefault(qid, {})
        print(f"[{len(per_anime)}/{len(rows)}] {a.title}: {len(cand_refs)} 候选", flush=True)

    # ---- 2. 批量获取实体详情（每批 20，避免 URL 过长导致空响应） ----
    qids = list(all_entities.keys())
    for i in range(0, len(qids), 20):
        batch = qids[i:i + 20]
        data = wb_get(batch)
        time.sleep(0.3)
        if "_error" in data:
            for q in batch:
                all_entities[q]["_error"] = data["_error"]
            continue
        for q, ent in (data.get("entities") or {}).items():
            all_entities[q] = ent

    # ---- 3. 收集所有 P31 → 一条 SPARQL 类型校验 ----
    p31_set = set()
    for ent in all_entities.values():
        for c in (ent.get("claims") or {}).get("P31", []):
            v = c.get("mainsnak", {}).get("datavalue", {}).get("value")
            if isinstance(v, dict) and v.get("id"):
                p31_set.add(v["id"])
    type_status = sparql_p31_ancestors(list(p31_set)) if p31_set else {}

    # ---- 4. 构建每部候选并综合判定 ----
    results = _classify_all(per_anime, all_entities, type_status, api_error_anime)
    _write_report(rows, results)


def _classify_all(per_anime, all_entities, type_status, api_error_anime):
    results = []
    for item in per_anime:
        a = item["anime"]
        if a.id in api_error_anime:
            results.append({"sample": a.title, "year": a.year, "status": "API_ERROR",
                            "reason": "外部 API 请求失败", "qid": None, "score": 0,
                            "candidates": []})
            continue
        cands = []
        for qid, ref in item["cand_refs"].items():
            ent = all_entities.get(qid) or {}
            if "_error" in ent:
                continue
            labels = ent.get("labels") or {}
            claims = ent.get("claims") or {}
            p31 = []
            for c in claims.get("P31", []):
                v = c.get("mainsnak", {}).get("datavalue", {}).get("value")
                if isinstance(v, dict) and v.get("id"):
                    p31.append(v["id"])
            # 简体优先收集标题（zh-hans > zh-hant > zh > en > ja），避免繁体/港台译名不匹配
            texts = []
            for lang in ("zh-hans", "zh-hant", "zh", "en", "ja"):
                v = (labels.get(lang) or {}).get("value", "")
                if v:
                    texts.append(v)
            aliases = []
            for al in (ent.get("aliases") or {}).values():
                aliases.extend(x.get("value", "") for x in al if x.get("value"))
            texts += aliases
            ext = {}
            for pid, name in EXTERNAL_PROPS.items():
                cl = claims.get(pid)
                if cl:
                    for c in cl:
                        v = c.get("mainsnak", {}).get("datavalue", {}).get("value")
                        if isinstance(v, dict):
                            val = v.get("id") or v.get("text") or v.get("time")
                        else:
                            val = v
                        if val:
                            ext[name] = val
                            break
            wd_year = None
            for pid in ("P577", "P580"):
                cl = claims.get(pid)
                if cl:
                    v = cl[0].get("mainsnak", {}).get("datavalue", {}).get("value")
                    if isinstance(v, dict):
                        wd_year = extract_year(v.get("time"))
                        if wd_year:
                            break
            ts = "unknown"
            for p in p31:
                st = type_status.get(p)
                if st == "anime":
                    ts = "anime"
                    break
                if st == "excluded":
                    ts = "excluded"
            cands.append({
                "qid": qid, "query": ref.get("query", ""), "texts": texts,
                "p31": p31, "type_status": ts, "wd_year": wd_year,
                "query_aliases": CH_ALIASES.get(a.chinese_title or a.title or "", []),
                "external_ids": ext,
            })
        status, reason, best = classify(a.year, cands, type_status)
        best_qid = best["qid"] if best else None
        best_ext = best.get("external_ids", {}) if best else {}
        results.append({
            "sample": a.title, "year": a.year, "status": status, "reason": reason,
            "qid": best_qid,
            "label": (best.get("texts") or [""])[0] if best else "",
            "p31": best.get("p31") if best else [],
            "wd_year": best.get("wd_year") if best else None,
            "title_score": best.get("title_score") if best else 0,
            "year_delta": best.get("year_delta") if best else 0,
            "score": best.get("score") if best else 0,
            "mal_id": best_ext.get("MAL anime ID"),
            "imdb_id": best_ext.get("IMDb ID"),
            "candidates": [
                {"qid": c["qid"], "type": c["type_status"], "query": c["query"]} for c in cands[:5]
            ],
        })
    return results



    main()


def _write_report(rows, results):
    total = len(results)
    stat = {"VERIFIED_CANDIDATE": 0, "REVIEW": 0, "AMBIGUOUS": 0, "REJECTED": 0,
            "TYPE_MISMATCH": 0, "TYPE_UNVERIFIED": 0, "NO_MATCH": 0, "API_ERROR": 0}
    for r in results:
        st = r["status"]
        stat[st] = stat.get(st, 0) + 1
        if "TYPE_MISMATCH" in r["reason"]:
            stat["TYPE_MISMATCH"] += 1
        if "TYPE_UNVERIFIED" in r["reason"]:
            stat["TYPE_UNVERIFIED"] += 1

    json_out = {"generated_at": _dt.datetime.now().isoformat(timespec="seconds"),
                "scope": f"前 {len(rows)} 部", "summary": stat, "items": results}
    with open(REPORT_JSON, "w", encoding="utf-8") as f:
        json.dump(json_out, f, ensure_ascii=False, indent=1)

    qid_hit = sum(1 for r in results if r.get("qid"))
    anime_confirmed = sum(1 for r in results if r["status"] == "VERIFIED_CANDIDATE")
    mal_cov = sum(1 for r in results if r.get("mal_id"))
    imdb_cov = sum(1 for r in results if r.get("imdb_id"))
    ambiguous = stat["AMBIGUOUS"]
    type_mismatch = stat["TYPE_MISMATCH"]
    api_err = stat["API_ERROR"]

    L = []
    A = L.append
    A("# AnimeHub Stage 12-C Wikidata QID 实体匹配报告\n")
    A(f"- 生成时间：{json_out['generated_at']} ｜ 只读验证（0 INSERT/UPDATE/DELETE）")
    A(f"- 数据范围：当前生产库前 {len(rows)} 部\n")
    A("## 汇总\n")
    A("| 指标 | 数量 |")
    A("|---|---:|")
    for k, v in stat.items():
        A(f"| {k} | {v} |")
    A("")
    A("## 覆盖率指标\n")
    A(f"- QID 命中率：{qid_hit}/{total}（{qid_hit/total*100:.0f}%）")
    A(f"- Anime 类型确认率：{anime_confirmed}/{total}（{anime_confirmed/total*100:.0f}%）")
    A(f"- MAL ID 覆盖率：{mal_cov}/{total}（{mal_cov/total*100:.0f}%）")
    A(f"- IMDb ID 覆盖率：{imdb_cov}/{total}（{imdb_cov/total*100:.0f}%）")
    A(f"- 自动高置信率：{anime_confirmed}/{total}（{anime_confirmed/total*100:.0f}%）")
    A(f"- ambiguous 率：{ambiguous}/{total}（{ambiguous/total*100:.0f}%）")
    A(f"- manga 误匹配率：{type_mismatch}/{total}（{type_mismatch/total*100:.0f}%）")
    A(f"- API_ERROR 率：{api_err}/{total}（{api_err/total*100:.0f}%）")
    A(f"- **可安全映射数：{anime_confirmed}/{total}**（VERIFIED_CANDIDATE）\n")
    A("## 明细\n")
    A("| Anime | Year | QID | Label | P31 | Wikidata Year | MAL ID | IMDb ID | Score | Status | Reason |")
    A("|---|---|---|---|---|---|---|---|---|---|---|")
    for r in results:
        A(f"| {r['sample']} | {r['year']} | {r['qid'] or ''} | {(r['label'] or '')[:20]} | "
          f"{(','.join(r['p31']) if r['p31'] else '')} | {r['wd_year'] or ''} | {r['mal_id'] or ''} | "
          f"{r['imdb_id'] or ''} | {r['score']} | {r['status']} | {r['reason'][:60]} |")
    with open(REPORT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    print(f"\n报告已生成: {REPORT_JSON}")
    print(f"            {REPORT_MD}")
    print(f"汇总: {json_out['summary']}")

    print(f"汇总: {json_out['summary']}")


if __name__ == "__main__":
    main()