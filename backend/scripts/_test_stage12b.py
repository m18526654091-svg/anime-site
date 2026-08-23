"""Stage 12-B 测试：数据治理表实施（data_sources / external_entities / anime_field_sources）。

覆盖 10 项：
1. 新表创建成功  2. ensure_schema 重复执行  3. source_key UNIQUE
4. external(source_id, entity_id) UNIQUE  5. field_sources(anime, field, source) UNIQUE
6. candidate 可无 anime_id  7. verified 无 anime_id 应失败
8. FK 正常  9. 现有 Anime 数量不变  10. 现有 Anime 字段不变

只读安全：临时 SQLite 库 + 本地正式库（非生产）。
"""
from __future__ import annotations

import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import sqlalchemy as sa  # noqa: E402
from sqlalchemy import event, inspect  # noqa: E402
from sqlalchemy.exc import IntegrityError  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from app.database import Base, ensure_schema, _seed_data_sources  # noqa: E402
from app.models import Anime, AnimeFieldSource, DataSource, ExternalEntity  # noqa: E402


def build_tmp():
    tmp = tempfile.mktemp(suffix=".db")
    eng = sa.create_engine(f"sqlite:///{tmp}")

    @event.listens_for(eng, "connect")
    def _fk(dbapi_conn, _rec):
        cur = dbapi_conn.cursor()
        cur.execute("PRAGMA foreign_keys=ON")
        cur.close()

    Base.metadata.create_all(eng)
    _seed_data_sources(eng)
    S = sessionmaker(bind=eng)
    return eng, S, tmp


def cleanup(eng, tmp):
    eng.dispose()
    try:
        os.remove(tmp)
    except OSError:
        pass


def test_tables_and_seed():
    eng, S, tmp = build_tmp()
    names = inspect(eng).get_table_names()
    assert {"data_sources", "external_entities", "anime_field_sources"}.issubset(names), names
    db = S()
    rows = {s.source_key: s for s in db.query(DataSource).all()}
    assert len(rows) == 6, f"seed 应为 6: {list(rows)}"
    assert rows["wikidata"].status == "active" and rows["wikidata"].commercial_ok == 1
    assert rows["commons"].commercial_ok is None  # UNVERIFIED
    assert rows["anilist"].status == "paused"  # 当前 403
    assert rows["mal"].status == "excluded"  # 未授权
    db.close()
    cleanup(eng, tmp)
    print("1. 新表创建成功 + seed 状态符合 Stage 11 审计 PASS")


def test_existing_data_unchanged():
    """9/10：现有 Anime 数据与字段不变（本地正式库）。"""
    from app.database import SessionLocal

    with SessionLocal() as db:
        before_count = db.query(Anime).count()
    con = sa.create_engine("sqlite:///f:/最新动漫代码/backend/animehub.db").connect()
    before_cols = {r[1] for r in con.execute(sa.text("PRAGMA table_info(anime)")).fetchall()}
    con.close()

    ensure_schema()
    ensure_schema()  # 幂等：重复执行

    with SessionLocal() as db:
        after_count = db.query(Anime).count()
    con = sa.create_engine("sqlite:///f:/最新动漫代码/backend/animehub.db").connect()
    after_cols = {r[1] for r in con.execute(sa.text("PRAGMA table_info(anime)")).fetchall()}
    con.close()
    assert before_count == after_count, f"Anime 数量变化 {before_count}->{after_count}"
    assert before_cols == after_cols, "Anime 列集不应变化"
    print(f"9/10. 现有 Anime 数据与字段不变 PASS（count={before_count} 列数={len(before_cols)}）")


def test_unique_constraints():
    eng, S, tmp = build_tmp()
    db = S()
    # 3. source_key UNIQUE
    try:
        db.add(DataSource(source_key="wikidata", name="dup"))
        db.commit()
        assert False, "source_key 重复应失败"
    except IntegrityError:
        db.rollback()
    # 4. external (source_id, source_entity_id) UNIQUE
    wd = db.query(DataSource).filter_by(source_key="wikidata").one()
    db.add(ExternalEntity(source_id=wd.id, source_entity_id="Q123", status="candidate"))
    db.commit()
    try:
        db.add(ExternalEntity(source_id=wd.id, source_entity_id="Q123", status="candidate"))
        db.commit()
        assert False, "external UNIQUE 应失败"
    except IntegrityError:
        db.rollback()
    # 5. field_sources (anime_id, field_name, source_id) UNIQUE
    an = Anime(title="T1", chinese_title="T1")
    db.add(an)
    db.commit()
    db.add(AnimeFieldSource(anime_id=an.id, field_name="title", source_id=wd.id))
    db.commit()
    try:
        db.add(AnimeFieldSource(anime_id=an.id, field_name="title", source_id=wd.id))
        db.commit()
        assert False, "field_sources UNIQUE 应失败"
    except IntegrityError:
        db.rollback()
    db.close()
    cleanup(eng, tmp)
    print("3/4/5. source_key / external / field_sources UNIQUE PASS")


def test_entity_status_rules():
    eng, S, tmp = build_tmp()
    db = S()
    wd = db.query(DataSource).filter_by(source_key="wikidata").one()
    # 6. candidate 可无 anime_id
    db.add(ExternalEntity(source_id=wd.id, source_entity_id="Q-CAND", status="candidate"))
    db.commit()
    # 7. verified 无 anime_id 应失败（CHECK）
    try:
        db.add(ExternalEntity(source_id=wd.id, source_entity_id="Q-VER", status="verified", confidence=95))
        db.commit()
        assert False, "verified 无 anime_id 应失败"
    except IntegrityError:
        db.rollback()
    # 8. FK：无效 source_id 应失败
    try:
        db.add(ExternalEntity(source_id=9999, source_entity_id="Q-FK", status="candidate"))
        db.commit()
        assert False, "无效 FK 应失败"
    except IntegrityError:
        db.rollback()
    # 空 source_entity_id 应失败
    try:
        db.add(ExternalEntity(source_id=wd.id, source_entity_id="", status="candidate"))
        db.commit()
        assert False, "空 source_entity_id 应失败"
    except IntegrityError:
        db.rollback()
    db.close()
    cleanup(eng, tmp)
    print("6/7/8. candidate 可无 anime / verified 需 anime / FK / 空 entity_id PASS")


if __name__ == "__main__":
    test_tables_and_seed()
    test_unique_constraints()
    test_entity_status_rules()
    test_existing_data_unchanged()
    print("\nALL TESTS PASS")
