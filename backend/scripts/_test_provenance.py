"""Stage 12-E 测试：provenance helper（10 项，临时 SQLite）。"""
from __future__ import annotations

import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import sqlalchemy as sa  # noqa: E402
from sqlalchemy import event  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from app.database import Base, _seed_data_sources  # noqa: E402
from app.models import Anime, AnimeFieldSource  # noqa: E402

from scripts.provenance import record_field_source  # noqa: E402


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
    db.add(Anime(id=1, title="进击的巨人", chinese_title="进击的巨人", year=2013))
    db.commit()
    return eng, S, tmp


def test_source_key_missing():
    eng, S, tmp = build_db()
    db = S()
    try:
        record_field_source(db, 1, "title", "no_such_source", "进击的巨人")
        assert False, "source_key 不存在应报错"
    except ValueError as e:
        assert "no_such_source" in str(e)
    db.rollback()
    db.close()
    eng.dispose()
    try:
        os.remove(tmp)
    except OSError:
        pass
    print("1. source_key 不存在 → FAIL PASS")


def test_insert_and_idempotent_and_no_duplicate():
    eng, S, tmp = build_db()
    db = S()
    h1 = record_field_source(db, 1, "title", "wikidata", "进击的巨人")
    db.commit()
    assert db.query(AnimeFieldSource).count() == 1, "应 INSERT 1 条"
    # 同值再次写入 → 幂等，仍 1 条
    h2 = record_field_source(db, 1, "title", "wikidata", "进击的巨人")
    db.commit()
    assert db.query(AnimeFieldSource).count() == 1, "幂等：不产生重复记录"
    assert h1 == h2
    db.close()
    eng.dispose()
    try:
        os.remove(tmp)
    except OSError:
        pass
    print("2/3/7. 新 provenance INSERT / 同值幂等 / 不产生重复记录 PASS")


def test_hash_changes_on_value_change():
    eng, S, tmp = build_db()
    db = S()
    h1 = record_field_source(db, 1, "title", "wikidata", "进击的巨人")
    db.commit()
    h2 = record_field_source(db, 1, "title", "wikidata", "Attack on Titan")
    db.commit()
    assert h1 != h2, "值变化 value_hash 应改变"
    rec = db.query(AnimeFieldSource).first()
    assert rec.source_value == "Attack on Titan"
    db.close()
    eng.dispose()
    try:
        os.remove(tmp)
    except OSError:
        pass
    print("4. 值发生变化 → value_hash 改变 PASS")


def test_verified_control():
    eng, S, tmp = build_db()
    db = S()
    record_field_source(db, 1, "title", "wikidata", "进击的巨人", verified=False)
    db.commit()
    rec = db.query(AnimeFieldSource).first()
    assert rec.verified == 0, "source 存在 ≠ verified=1"
    # 单独置 verified
    record_field_source(db, 1, "title", "wikidata", "进击的巨人", verified=True)
    db.commit()
    rec = db.query(AnimeFieldSource).first()
    assert rec.verified == 1, "verified 可单独控制"
    db.close()
    eng.dispose()
    try:
        os.remove(tmp)
    except OSError:
        pass
    print("5. verified 状态可单独控制 PASS")


def test_anime_untouched_and_rollback():
    eng, S, tmp = build_db()
    db = S()
    record_field_source(db, 1, "title", "wikidata", "进击的巨人")
    # rollback：未 commit 的记录回滚
    db.rollback()
    assert db.query(AnimeFieldSource).count() == 0, "rollback 后 0 条 provenance"
    # Anime 不受影响
    a = db.query(Anime).filter(Anime.id == 1).first()
    assert a.title == "进击的巨人" and a.anilist_id is None and a.mal_id is None
    db.close()
    eng.dispose()
    try:
        os.remove(tmp)
    except OSError:
        pass
    print("6/8. 不影响 Anime + transaction rollback PASS")


def test_text_and_cover_value():
    eng, S, tmp = build_db()
    db = S()
    # 文本字段：多余空白规范化
    record_field_source(db, 1, "description", "wikipedia", "  人类  在巨人  的威胁下  生存。  ")
    db.commit()
    rec = db.query(AnimeFieldSource).filter_by(field_name="description").first()
    assert rec.source_value == "人类 在巨人 的威胁下 生存。", repr(rec.source_value)
    # cover：URL 原样保存（空白压缩，不存二进制）
    record_field_source(db, 1, "cover", "commons", "https://example.com/cover  image.jpg")
    db.commit()
    rec2 = db.query(AnimeFieldSource).filter_by(field_name="cover").first()
    assert rec2.source_value == "https://example.com/coverimage.jpg", repr(rec2.source_value)
    db.close()
    eng.dispose()
    try:
        os.remove(tmp)
    except OSError:
        pass
    print("9/10. 文本 source_value 规范化 + cover URL 保存 PASS")


if __name__ == "__main__":
    test_source_key_missing()
    test_insert_and_idempotent_and_no_duplicate()
    test_hash_changes_on_value_change()
    test_verified_control()
    test_anime_untouched_and_rollback()
    test_text_and_cover_value()
    print("\nALL TESTS PASS")
