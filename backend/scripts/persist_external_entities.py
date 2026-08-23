"""Stage 12-D: 将 Stage 12-C.6 VERIFIED Wikidata 实体写入 external_entities。

只处理 VERIFIED_CANDIDATE（11 个已人工审核样本）。
只写 external_entities；绝不修改 anime 字段（anilist_id/mal_id/cover/...）。
ID provenance：只创建 source=wikidata 的 entity；MAL/IMDb 仅作为 raw_snapshot 证据，
不创建独立 mal/imdb external_entities。

安全：
- 冲突检查（4 项）不通过 → 标记 conflict，不写
- 幂等：重复运行识别 already_exists
- --apply 使用 transaction，异常整体 rollback
- 默认 --dry-run（0 修改）

用法（在 backend 目录）:
    .venv\\Scripts\\python -m scripts.persist_external_entities [--apply] [--report PATH]
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from sqlalchemy.exc import IntegrityError  # noqa: E402

from app.database import SessionLocal  # noqa: E402
from app.models import Anime, DataSource, ExternalEntity  # noqa: E402

MATCHER_VERSION = "stage12c6"
DEFAULT_REPORT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "stage12c6_wikidata_report.json",
)


def _value_hash(item: dict) -> str:
    key = "|".join([
        str(item.get("qid", "")),
        str(item.get("sample", "")),
        str(item.get("wd_year") or ""),
        str(item.get("mal_id") or ""),
        str(item.get("imdb_id") or ""),
    ])
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


def build_snapshot(item: dict, anime) -> str:
    """raw_snapshot：仅保存必要候选信息（不保存完整 API response）。"""
    return json.dumps({
        "qid": item.get("qid"),
        "label": (item.get("label") or "")[:120],
        "matched_title": (item.get("sample") or "")[:120],
        "matched_language": "zh",
        "p31": (item.get("p31") or [])[:6],
        "year": item.get("wd_year"),
        "mal_id": item.get("mal_id"),
        "imdb_id": item.get("imdb_id"),
        "match_score": item.get("score", 0),
        "matcher_version": MATCHER_VERSION,
    }, ensure_ascii=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="写入 VERIFIED Wikidata 实体到 external_entities")
    parser.add_argument("--apply", action="store_true", help="真正写入（默认 dry-run）")
    parser.add_argument("--report", default=DEFAULT_REPORT, help="Stage 12-C.6 报告 JSON 路径")
    args = parser.parse_args()
    dry_run = not args.apply

    if not os.path.exists(args.report):
        print(f"[error] 报告不存在，拒绝执行: {args.report}")
        sys.exit(1)
    try:
        with open(args.report, encoding="utf-8") as f:
            report = json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        print(f"[error] 报告无法解析（格式错误）: {args.report} :: {exc}")
        sys.exit(1)
    if not isinstance(report, dict) or not isinstance(report.get("items"), list):
        print(f"[error] 报告格式错误（缺少 items 列表）: {args.report}")
        sys.exit(1)
    # 只接受人工审核的 VERIFIED / VERIFIED_CANDIDATE；其余状态一律跳过
    verified = [
        r for r in report.get("items", [])
        if r.get("status") in ("VERIFIED", "VERIFIED_CANDIDATE")
    ]
    skipped_status = sum(1 for r in report.get("items", []) if r.get("status") not in ("VERIFIED", "VERIFIED_CANDIDATE"))
    print(f"VERIFIED 样本: {len(verified)}（模式: {'apply' if not dry_run else 'dry-run'}，非 VERIFIED 跳过: {skipped_status}）")

    db = SessionLocal()
    stats = {"prepared": 0, "skipped": 0, "conflict": 0, "invalid": 0, "already_exists": 0, "written": 0}
    detail: list[dict] = []
    try:
        wd = db.query(DataSource).filter_by(source_key="wikidata").first()
        if not wd:
            print("[error] data_sources 无 wikidata（先执行 ensure_schema seed）")
            return

        for item in verified:
            title = (item.get("sample") or "").strip()
            qid = item.get("qid")
            anime = (
                db.query(Anime)
                .filter((Anime.chinese_title == title) | (Anime.title == title))
                .order_by(Anime.id.asc())
                .first()
            )
            row = {"anime": title, "qid": qid, "action": "", "reason": ""}
            if not qid or not anime:
                row.update(action="invalid", reason="缺 QID 或未找到 Anime")
                stats["invalid"] += 1
                detail.append(row)
                continue

            # ---- 冲突 / 幂等检查 ----
            dup = (
                db.query(ExternalEntity)
                .filter_by(source_id=wd.id, source_entity_id=qid)
                .first()
            )
            if dup:
                if dup.anime_id == anime.id:
                    row.update(action="already_exists", reason=f"source_entity_id={qid} 已存在（同一 anime）")
                    stats["already_exists"] += 1
                else:
                    row.update(action="conflict", reason=f"QID {qid} 已映射 anime#{dup.anime_id}（非当前 anime#{anime.id}）")
                    stats["conflict"] += 1
                detail.append(row)
                continue
            has_verified = (
                db.query(ExternalEntity)
                .filter(ExternalEntity.anime_id == anime.id, ExternalEntity.status == "verified")
                .first()
            )
            if has_verified:
                row.update(action="conflict", reason=f"anime#{anime.id} 已有 verified Wikidata 实体")
                stats["conflict"] += 1
                detail.append(row)
                continue
            qid_other = (
                db.query(ExternalEntity)
                .filter(ExternalEntity.source_id == wd.id, ExternalEntity.source_entity_id == qid)
                .first()
            )
            if qid_other:
                row.update(action="conflict", reason=f"QID {qid} 已映射 anime#{qid_other.anime_id}")
                stats["conflict"] += 1
                detail.append(row)
                continue

            stats["prepared"] += 1
            row.update(action="write" if not dry_run else "prepared", reason="冲突检查通过")
            detail.append(row)

            if not dry_run:
                db.add(ExternalEntity(
                    anime_id=anime.id,
                    source_id=wd.id,
                    source_entity_id=qid,
                    status="verified",
                    confidence=max(0, min(100, int(round(item.get("score", 0))))),
                    canonical=1,
                    raw_snapshot=build_snapshot(item, anime),
                    value_hash=_value_hash(item),
                    verified_at=_dt.datetime.utcnow(),
                ))
                stats["written"] += 1

        if not dry_run:
            try:
                db.commit()
            except IntegrityError:
                db.rollback()
                print("[error] 写入失败，整体 rollback（数据库未修改）")
                raise
        print(f"\n结果: prepared={stats['prepared']} skipped={stats['skipped']} "
              f"conflict={stats['conflict']} invalid={stats['invalid']} "
              f"already_exists={stats['already_exists']} written={stats['written']}")
        if dry_run:
            print("（dry-run：数据库 0 修改）")
        else:
            print(f"（apply：已提交 {stats['written']} 条 external_entities）")
        for r in detail:
            print(f"  [{r['action']}] {r['anime']} {r['qid'] or ''} - {r['reason']}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
