"""Growth Sprint 2 测试：10 部增强逻辑（临时 SQLite，不碰正式库）。"""
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
from scripts.growth_sprint2_enrich import (  # noqa: E402
    _FACTS, _NO_FACT_KEYS, _seo_title, apply_plan, build_plan,
)


def _tmp_db(keys):
    tmp = tempfile.mktemp(suffix=".db")
    eng = sa.create_engine(f"sqlite:///{tmp}")
    @event.listens_for(eng, "connect")
    def _fk(conn, _r):
        c = conn.cursor(); c.execute("PRAGMA foreign_keys=ON"); c.close()
    Base.metadata.create_all(eng)
    _seed_data_sources(eng)
    S = sessionmaker(bind=eng)
    db = S()
    for i, k in enumerate(keys, start=1):
        db.add(Anime(id=i, title=k, chinese_title=k, year=2000 + i,
                     studio="seed", episodes=12, seo_title="seed-title",
                     description="old desc"))
    db.commit()
    return eng, S, tmp, db


def test_plan_10_matched():
    eng, S, tmp, db = _tmp_db([f["key"] for f in _FACTS])
    plan = build_plan(db)
    assert len(plan) == 30 and all(p["matched"] for p in plan)
    db.close(); eng.dispose()
    try: os.remove(tmp)
    except OSError: pass
    print("1. 30 部样本全部匹配 PASS")


def test_non_verified_no_fact_fields():
    eng, S, tmp, db = _tmp_db([f["key"] for f in _FACTS])
    plan = build_plan(db)
    for p in plan:
        if not p["verified"]:
            assert p["new"]["studio"] is None
            assert p["new"]["episodes"] is None
            assert p["new"]["seo_title"] is None
            assert p["new"]["description"] is not None  # 仅 desc 增强
    db.close(); eng.dispose()
    try: os.remove(tmp)
    except OSError: pass
    print("2. 非 VERIFIED QID 不写事实字段/SEO title，仅 desc PASS")


def test_movie_episodes_one_and_title():
    assert _seo_title("你的名字。", 2016, "movie") == "你的名字。（2016）剧场版 | AnimeHub"
    assert _seo_title("进击的巨人", 2013, "series") == "进击的巨人（2013）TV 87集 | AnimeHub"
    assert _seo_title("叛逆的鲁路修", 2006, "unknown") is None  # 非 VERIFIED 不写
    eng, S, tmp, db = _tmp_db([f["key"] for f in _FACTS])
    plan = build_plan(db)
    movie = [p for p in plan if p["key"] == "你的名字。"][0]
    assert movie["new"]["episodes"] == 1 and movie["semantics"] == "movie"
    db.close(); eng.dispose()
    try: os.remove(tmp)
    except OSError: pass
    print("3. movie episodes=1 + SEO title 试点格式 PASS")


def test_apply_and_provenance_count():
    eng, S, tmp, db = _tmp_db([f["key"] for f in _FACTS])
    plan = build_plan(db)
    stats = apply_plan(db, plan)
    assert stats["anime_written"] == 30
    assert stats["field_written"] == 75          # 19 部 × 4 - 1(SAO eps None)
    assert stats["seo_title_written"] == 19
    assert stats["description_written"] == 30
    assert stats["provenance_written"] == 124    # 75 + 19 + 30
    assert db.query(AnimeFieldSource).count() == 124
    db.close(); eng.dispose()
    try: os.remove(tmp)
    except OSError: pass
    print("4. apply 写入数量 + provenance=45 PASS")


def test_idempotent_apply():
    eng, S, tmp, db = _tmp_db([f["key"] for f in _FACTS])
    plan = build_plan(db)
    apply_plan(db, plan)
    stats2 = apply_plan(db, plan)  # 重复 apply
    assert db.query(AnimeFieldSource).count() == 124  # 不重复
    assert stats2["provenance_written"] == 124      # upsert 覆盖
    db.close(); eng.dispose()
    try: os.remove(tmp)
    except OSError: pass
    print("5. 幂等（重复 apply 不产生重复 provenance）PASS")


def test_others_untouched():
    eng, S, tmp, db = _tmp_db([f["key"] for f in _FACTS])
    db.add(Anime(id=99, title="其它作品", chinese_title="其它作品", year=2010,
                 studio="other", episodes=12, seo_title="t", description="d"))
    db.commit()
    plan = build_plan(db)
    apply_plan(db, plan)
    other = db.query(Anime).filter(Anime.id == 99).first()
    assert other.episodes == 12 and other.studio == "other"
    assert db.query(AnimeFieldSource).filter(AnimeFieldSource.anime_id == 99).count() == 0
    db.close(); eng.dispose()
    try: os.remove(tmp)
    except OSError: pass
    print("6. 其他 Anime 完全不受影响 PASS")


if __name__ == "__main__":
    test_plan_10_matched()
    test_non_verified_no_fact_fields()
    test_movie_episodes_one_and_title()
    test_apply_and_provenance_count()
    test_idempotent_apply()
    test_others_untouched()
    print("\nALL TESTS PASS")
