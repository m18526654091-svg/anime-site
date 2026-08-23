"""Stage 12-D 测试：external_entities 落库（10 项，临时 SQLite 只读验证）。"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import sqlalchemy as sa  # noqa: E402
from sqlalchemy import event  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from app.database import Base, _seed_data_sources  # noqa: E402
from app.models import Anime, ExternalEntity  # noqa: E402

import scripts.persist_external_entities as mod  # noqa: E402

VERIFIED_TITLES = [
    "进击的巨人", "鬼灭之刃", "咒术回战", "火影忍者", "间谍过家家", "电锯人",
    "葬送的芙莉莲", "我推的孩子", "我的英雄学院", "排球少年！！", "黑子的篮球",
]


def build_db():
    tmp = tempfile.mktemp(suffix=".db")
    eng = sa.create_engine(f"sqlite:///{tmp}")

    @event.listens_for(eng, "connect")
    def _fk(dbapi_conn, _rec):
        c = dbapi_conn.cursor()
        c.execute("PRAGMA foreign_keys=ON")
        c.close()

    Base.metadata.create_all(eng)
    _seed_data_sources(eng)
    S = sessionmaker(bind=eng)
    db = S()
    all_titles = VERIFIED_TITLES + ["某REVIEW", "某AMB", "某REJ", "重名"]
    for i, t in enumerate(all_titles, start=1):
        db.add(Anime(id=i, title=t, chinese_title=t, year=2013))
    db.commit()
    db.close()
    return eng, S, tmp


def make_item(title, status, qid, score=95, mal=None, imdb=None):
    return {"sample": title, "status": status, "qid": qid, "score": score,
            "label": title, "p31": ["Q63952888"], "wd_year": 2013,
            "mal_id": mal, "imdb_id": imdb}


def write_report(path, items):
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"items": items}, f, ensure_ascii=False)


def run_main(S, report_path, apply=False):
    with patch.object(mod, "SessionLocal", lambda: S()):
        argv = ["persist_external_entities", "--report", report_path]
        if apply:
            argv.append("--apply")
        sys.argv = argv
        mod.main()


def test_1_to_8_10():
    eng, S, tmp = build_db()
    report = tmp + ".json"
    items = [
        make_item("进击的巨人", "VERIFIED_CANDIDATE", "Q22126305", 103, 16498, "tt2560140"),
        make_item("电锯人", "VERIFIED_CANDIDATE", "Q104211858", 103, 44511, "tt13616990"),
        make_item("某REVIEW", "REVIEW", "Q999", 75),
        make_item("某AMB", "AMBIGUOUS", "Q998", 98),
        make_item("某REJ", "REJECTED", "Q997", 30),
    ]
    write_report(report, items)

    # 7. dry-run → 0 写入
    run_main(S, report, apply=False)
    db = S()
    assert db.query(ExternalEntity).count() == 0, "dry-run 必须 0 写入"
    db.close()
    print("7. dry-run → 0 写入 PASS")

    # 8. apply → VERIFIED 写入，REVIEW/AMBIGUOUS/REJECTED 不写
    run_main(S, report, apply=True)
    db = S()
    rows = db.query(ExternalEntity).all()
    assert len(rows) == 2, f"应写 2 条 VERIFIED: {len(rows)}"
    assert all(r.status == "verified" and r.canonical == 1 for r in rows)
    assert {r.source_entity_id for r in rows} == {"Q22126305", "Q104211858"}
    db.close()
    print("1/2/3/4. VERIFIED 写入 / REVIEW·AMBIGUOUS·REJECTED 不写 PASS")

    # 10. 重复 apply → already_exists，0 新增
    run_main(S, report, apply=True)
    db = S()
    assert db.query(ExternalEntity).count() == 2, "重复 apply 不应新增"
    db.close()
    print("10. 重复 apply → already_exists PASS")
    eng.dispose()
    try:
        os.remove(tmp)
    except OSError:
        pass


def test_5_qid_duplicate_conflict():
    eng, S, tmp = build_db()
    report = tmp + ".json"
    items = [
        make_item("进击的巨人", "VERIFIED_CANDIDATE", "Q22126305", 103),
        make_item("某REVIEW", "VERIFIED_CANDIDATE", "Q22126305", 90),  # 同 QID 映射不同 anime
    ]
    write_report(report, items)
    run_main(S, report, apply=True)
    db = S()
    rows = db.query(ExternalEntity).all()
    assert len(rows) == 1, f"QID 冲突不应写入第二条: {len(rows)}"
    assert rows[0].anime_id == 1, "第一个映射应保留"
    db.close()
    print("5. QID duplicate → conflict PASS")
    eng.dispose()
    try:
        os.remove(tmp)
    except OSError:
        pass


def test_6_anime_has_canonical_conflict():
    eng, S, tmp = build_db()
    report = tmp + ".json"
    items = [
        make_item("进击的巨人", "VERIFIED_CANDIDATE", "Q22126305", 103),
        make_item("进击的巨人", "VERIFIED_CANDIDATE", "Q22222222", 90),  # 同一 anime 第二个
    ]
    write_report(report, items)
    run_main(S, report, apply=True)
    db = S()
    rows = db.query(ExternalEntity).all()
    assert len(rows) == 1, "anime 已有 canonical 不应写第二个"
    db.close()
    print("6. Anime 已有 canonical Wikidata → conflict PASS")
    eng.dispose()
    try:
        os.remove(tmp)
    except OSError:
        pass


def test_9_rollback():
    eng, S, tmp = build_db()
    report = tmp + ".json"
    items = [
        make_item("进击的巨人", "VERIFIED_CANDIDATE", "Q22126305", 103),
        make_item("电锯人", "VERIFIED_CANDIDATE", "Q104211858", 103),
    ]
    write_report(report, items)

    # 第二个写入时 build_snapshot 抛异常 → 整体 rollback → 0 写入
    orig = mod.build_snapshot
    call = {"n": 0}

    def boom(item, anime):
        call["n"] += 1
        if call["n"] >= 2:
            raise RuntimeError("snapshot error")
        return orig(item, anime)

    with patch.object(mod, "build_snapshot", boom):
        try:
            run_main(S, report, apply=True)
        except RuntimeError:
            pass
    db = S()
    assert db.query(ExternalEntity).count() == 0, "异常必须整体 rollback，0 部分提交"
    db.close()
    print("9. rollback → 异常时零部分提交 PASS")
    eng.dispose()
    try:
        os.remove(tmp)
    except OSError:
        pass


def test_report_input_validation():
    """报告输入验证：不存在/格式错误 → 退出；只接受 VERIFIED。"""
    eng, S, tmp = build_db()
    # report 不存在 → SystemExit
    try:
        run_main(S, tmp + ".missing.json", apply=True)
        assert False, "报告不存在应退出"
    except SystemExit:
        pass
    # 格式错误（非 JSON）→ SystemExit
    bad = tmp + ".bad.json"
    with open(bad, "w", encoding="utf-8") as f:
        f.write("not json{{{")
    try:
        run_main(S, bad, apply=True)
        assert False, "格式错误应退出"
    except SystemExit:
        pass
    # 只接受 VERIFIED / VERIFIED_CANDIDATE；REVIEW/AMBIGUOUS/REJECTED/NO_MATCH/API_ERROR 跳过
    ok = tmp + ".ok.json"
    write_report(ok, [
        make_item("进击的巨人", "VERIFIED", "Q22126305", 100),
        make_item("某REVIEW", "REVIEW", "Q999", 75),
        make_item("某AMB", "AMBIGUOUS", "Q998", 98),
        make_item("某REJ", "REJECTED", "Q997", 30),
        make_item("某NOM", "NO_MATCH", None, 0),
        make_item("某API", "API_ERROR", None, 0),
    ])
    run_main(S, ok, apply=True)
    db = S()
    assert db.query(ExternalEntity).count() == 1, "只应写入 VERIFIED 1 条"
    db.close()
    print("report 输入验证 PASS（不存在/格式错误退出；仅 VERIFIED 写入）")
    eng.dispose()
    try:
        os.remove(tmp)
        os.remove(bad)
        os.remove(ok)
    except OSError:
        pass


if __name__ == "__main__":
    test_1_to_8_10()
    test_5_qid_duplicate_conflict()
    test_6_anime_has_canonical_conflict()
    test_9_rollback()
    test_report_input_validation()
    print("\nALL TESTS PASS")
