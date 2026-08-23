"""Stage 10-C: 外部 ID 回填（默认只读匹配 + 报告；--apply 才写库）。

为 anilist_id 与 mal_id 均为空的 Anime 记录，复用现有 AniListProvider
（Page.media 多候选 + anime_aliases.json + 标题/年份评分 + MIN_SCORE + 全局节流/429 处理），
匹配候选并输出分级报告。

分级（ID 回填比封面更严格）：
- A 高置信：score >= 82 且 年份一致/接近 且 标题 exact/strong contains → 可自动回填
- B 人工审核：60 <= score < 82，或 ambiguous / ID conflict / 轻微不确定
- C 低置信：score < 60 或无候选
- ambiguous：最高分与第二名分数非常接近（差 <= 5）→ 进入 B
- conflict：同一 anilist_id/mal_id 不允许分配给多个不同 Anime → 绝不自动写入

不新增动漫；已有任一外部 ID 的记录绝不覆盖。

用法（在 backend 目录）:
    .venv\\Scripts\\python -m scripts.backfill_external_ids [--limit N] [--apply]
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from app.database import SessionLocal  # noqa: E402
from app.models import Anime  # noqa: E402
from scripts.covers.anilist import AniListProvider, MIN_SCORE  # noqa: E402

# ID 回填比封面更严格：A 级阈值与 ambiguous 判定
A_SCORE = 82.0
AMBIGUOUS_DELTA = 5.0

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # backend/
REPORT_MD = os.path.join(ROOT, "data", "external_id_backfill_report.md")
REPORT_JSON = os.path.join(ROOT, "data", "external_id_backfill_report.json")


def collect_candidates(provider: AniListProvider, title: str, chinese_title: str, year) -> list[dict]:
    """复用 provider 现有能力，跨查询词收集全部候选（含评分与 query）。"""
    out: list[dict] = []
    for q in provider._query_words(title, chinese_title):
        try:
            cands = provider._fetch_candidates(q)
        except Exception:
            continue
        for c in cands:
            c = dict(c)
            c["score"] = provider._score(q, c, year)
            c["query"] = q
            out.append(c)
    return out


def classify(provider: AniListProvider, anime: Anime, cands: list[dict]):
    """分级。返回 (confidence, reason, best)。"""
    if not cands:
        return "C", "无候选", None
    cands.sort(key=lambda c: c.get("score", 0), reverse=True)
    best = cands[0]
    second = cands[1] if len(cands) > 1 else None
    score = best.get("score", 0)

    # ambiguous：最高分与第二名分数非常接近 → 人工审核
    if second is not None and score - second.get("score", 0) <= AMBIGUOUS_DELTA:
        return "B", f"ambiguous top1={score:.1f} top2={second.get('score', 0):.1f}（需人工确认）", best
    if score < MIN_SCORE:
        return "C", f"score={score:.1f} 低于 MIN_SCORE={MIN_SCORE}", best

    # 年份一致性
    year_ok = True
    year_note = ""
    if anime.year and best.get("seasonYear"):
        diff = abs(int(anime.year) - int(best["seasonYear"]))
        if diff > 2:
            year_ok = False
            year_note = f"年份不符(db={anime.year} vs al={best['seasonYear']})"
        else:
            year_note = f"年份一致/接近(al={best['seasonYear']})"

    # 标题强匹配（exact/strong contains，_title_score>=80）
    tscore = provider._title_score(best.get("query") or "", best)
    title_strong = tscore >= 80

    if score >= A_SCORE and year_ok and title_strong:
        return "A", f"score={score:.1f} {year_note} 标题强匹配({tscore})", best
    note = f"{year_note} " if year_note else ""
    return "B", f"score={score:.1f} {note}需人工审核".strip(), best


def main() -> None:
    parser = argparse.ArgumentParser(description="外部 ID 回填（只读匹配 + 报告）")
    parser.add_argument("--limit", type=int, default=0, help="最多处理条数（0=全部）")
    parser.add_argument("--dry-run", action="store_true", help="只读匹配与报告，不写库（默认）")
    parser.add_argument("--apply", action="store_true", help="将 A 级高置信且无冲突的 ID 写入数据库")
    args = parser.parse_args()
    dry_run = not args.apply  # 默认只读

    provider = AniListProvider()
    db = SessionLocal()
    try:
        rows = (
            db.query(Anime)
            .filter(Anime.anilist_id.is_(None), Anime.mal_id.is_(None))
            .order_by(Anime.id.asc())
            .all()
        )
        if args.limit:
            rows = rows[: args.limit]
        print(f"待处理(anilist_id & mal_id 均为空): {len(rows)}（limit={args.limit or '全部'}）")
        if not dry_run:
            print("（--apply：A 级高置信且无冲突的 ID 将写入数据库）")

        stats = {"A": 0, "B": 0, "C": 0, "ambiguous": 0, "conflict": 0}
        accepted_anilist: dict[int, int] = {}
        accepted_mal: dict[int, int] = {}
        report_rows: list[dict] = []

        for a in rows:
            key = (a.chinese_title or a.title or "").strip()
            cands = collect_candidates(provider, (a.title or ""), (a.chinese_title or ""), a.year)
            conf, reason, best = classify(provider, a, cands)
            al_id = best.get("id") if best else None
            mal_id = best.get("idMal") if best else None

            # 冲突检查：仅对可能写入的 A 级检查
            if conf == "A" and al_id is not None:
                conflict_reason = ""
                if al_id in accepted_anilist and accepted_anilist[al_id] != a.id:
                    conflict_reason = f"anilist_id={al_id} 已分配给 anime#{accepted_anilist[al_id]}"
                if mal_id and mal_id in accepted_mal and accepted_mal[mal_id] != a.id:
                    conflict_reason = f"mal_id={mal_id} 已分配给 anime#{accepted_mal[mal_id]}"
                if conflict_reason:
                    conf = "B"  # 冲突 → 人工审核，绝不自动写入
                    reason = f"ID conflict: {conflict_reason}"
                    stats["conflict"] += 1
                else:
                    accepted_anilist.setdefault(al_id, a.id)
                    if mal_id:
                        accepted_mal.setdefault(mal_id, a.id)

            stats[conf] = stats.get(conf, 0) + 1
            if "ambiguous" in reason:
                stats["ambiguous"] += 1

            # 写库（仅 --apply 且 A 级且无冲突）
            if not dry_run and conf == "A":
                a.anilist_id = al_id
                a.mal_id = mal_id
                db.add(a)

            report_rows.append(
                {
                    "anime": key,
                    "year": a.year,
                    "query": best.get("query", "") if best else "",
                    "anilist_id": al_id,
                    "mal_id": mal_id,
                    "romaji": best.get("romaji", "") if best else "",
                    "english": best.get("english", "") if best else "",
                    "match_score": best.get("score", 0) if best else 0,
                    "confidence": conf,
                    "reason": reason,
                }
            )

        if not dry_run:
            db.commit()

        # ---- 生成报告 ----
        os.makedirs(os.path.dirname(REPORT_MD), exist_ok=True)
        no_result = sum(1 for r in report_rows if r["confidence"] == "C" and r["reason"] == "无候选")
        summary = {
            "generated_at": _dt.datetime.now().isoformat(timespec="seconds"),
            "mode": "apply" if not dry_run else "dry-run",
            "processed": len(report_rows),
            "A_high_confidence": stats["A"],
            "B_manual_review": stats["B"],
            "C_low_confidence": stats["C"],
            "no_result": no_result,
            "ambiguous": stats["ambiguous"],
            "id_conflict": stats["conflict"],
        }
        with open(REPORT_JSON, "w", encoding="utf-8") as f:
            json.dump({"summary": summary, "items": report_rows}, f, ensure_ascii=False, indent=2)

        lines = [
            "# AnimeHub 外部 ID 回填报告",
            "",
            f"- 生成时间：{summary['generated_at']}",
            f"- 模式：{'写库(--apply)' if not dry_run else '只读(dry-run)'}",
            f"- 匹配源：AniList（Page.media + alias + 标题/年份评分 + MIN_SCORE={MIN_SCORE}）",
            "",
            "## 汇总",
            "",
            "| 指标 | 数量 |",
            "|---|---:|",
            f"| 总处理数 | {summary['processed']} |",
            f"| A 高置信（可自动回填） | {summary['A_high_confidence']} |",
            f"| B 人工审核 | {summary['B_manual_review']} |",
            f"| C 低置信 | {summary['C_low_confidence']} |",
            f"| 无结果 | {summary['no_result']} |",
            f"| ambiguous | {summary['ambiguous']} |",
            f"| ID conflict | {summary['id_conflict']} |",
            "",
            "## 明细",
            "",
            "| Anime | Year | Query | AniList ID | MAL ID | Match Score | Confidence | Reason |",
            "|---|---|---:|---:|---:|---:|---|---|",
        ]
        for r in report_rows:
            lines.append(
                f"| {r['anime']} | {r['year'] or ''} | {r['query']} | {r['anilist_id'] or ''} "
                f"| {r['mal_id'] or ''} | {r['match_score']} | {r['confidence']} | {r['reason']} |"
            )
        with open(REPORT_MD, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        print()
        print(
            f"完成: 处理 {len(report_rows)} 条 | A={stats['A']} B={stats['B']} C={stats['C']} "
            f"| ambiguous={stats['ambiguous']} conflict={stats['conflict']} | 无结果={no_result}"
        )
        print(f"报告已生成: {REPORT_JSON}")
        print(f"            {REPORT_MD}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
