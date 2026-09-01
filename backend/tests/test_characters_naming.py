"""Phase 40-A — Character 英文优先命名回归测试（API 层）。

覆盖：
  Test 1: API 返回 name_en（English primary 数据可用）
  Test 2: API 返回 native_name（Native 保留）
  Test 3: name_en 缺失时返回 None（前端回退 name）
  Test 4: name_en 与 native_name 同时返回，前端可去重（数据层不重复）
  Test 5: canonical slug 不变
  Test 6: anime_id 过滤保持（Phase 39.z 修复不回归）
  Test 7: 全局 /api/characters 保持
"""
import pytest
from sqlalchemy.orm import Session

from tests.test_api import client, TestingSessionLocal, engine  # noqa: F401
from app.database import Base as _Base
from app.models import Anime as _Anime, Character as _Character
from app.seed import SAMPLE_ANIME as _SAMPLE


def _mk(db, **kw):
    db.add(_Anime(**kw))
    db.flush()
    return db.query(_Anime).filter(_Anime.slug == kw["slug"]).first()


@pytest.fixture
def world():
    _Base.metadata.drop_all(bind=engine)
    _Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        for item in _SAMPLE:
            db.add(_Anime(**item))
        a1 = _mk(db, title="Anime One", chinese_title="Anime One", slug="anime-one",
                 genre="Action", score=8.0)
        a2 = _mk(db, title="Anime Two", chinese_title="Anime Two", slug="anime-two",
                 genre="Action", score=7.0)
        # English 存在 + Native 存在（不同）
        db.add(_Character(name="竈門炭治郎", name_en="Tanjiro Kamado", native_name="竈門炭治郎",
                          slug="tanjiro-kamado", anime_id=a1.id, source="anilist", source_id="126071"))
        # English 缺失（NULL）→ 前端回退 name
        db.add(_Character(name="原生名角色", name_en="", native_name="原生名角色",
                          slug="native-only", anime_id=a1.id))
        # English == Native（去重场景）
        db.add(_Character(name="Same Name", name_en="Same Name", native_name="Same Name",
                          slug="same-name", anime_id=a2.id))
        db.commit()
        yield {"a1": a1.id, "a2": a2.id}
    finally:
        db.close()


def test_1_name_en_exposed(world):
    """Test 1: API 返回 name_en（English primary 可用）。"""
    r = client.get("/api/characters", params={"anime_id": world["a1"]})
    assert r.status_code == 200
    tanjiro = next(c for c in r.json() if c["slug"] == "tanjiro-kamado")
    assert tanjiro["name"] == "竈門炭治郎"
    assert tanjiro["name_en"] == "Tanjiro Kamado"
    # 前端 primary = name_en || name = "Tanjiro Kamado"
    assert (tanjiro["name_en"] or tanjiro["name"]) == "Tanjiro Kamado"


def test_2_native_preserved(world):
    """Test 2: native_name 保留并返回（前端 secondary）。"""
    r = client.get("/api/characters", params={"anime_id": world["a1"]})
    tanjiro = next(c for c in r.json() if c["slug"] == "tanjiro-kamado")
    assert tanjiro["native_name"] == "竈門炭治郎"
    # 前端去重条件：native != primary 时显示
    primary = tanjiro["name_en"] or tanjiro["name"]
    assert tanjiro["native_name"] != primary


def test_3_missing_english_fallback(world):
    """Test 3: name_en 缺失 → API 返回空，前端回退 name（不伪造翻译）。"""
    r = client.get("/api/characters", params={"anime_id": world["a1"]})
    native_only = next(c for c in r.json() if c["slug"] == "native-only")
    assert native_only["name_en"] in (None, "")
    assert native_only["name"] == "原生名角色"
    # 前端 primary = name_en || name = 原生名
    assert (native_only["name_en"] or native_only["name"]) == "原生名角色"


def test_4_duplicate_suppression_data(world):
    """Test 4: name_en == native_name 时数据仍一致，前端可去重不重复渲染。"""
    r = client.get("/api/characters", params={"anime_id": world["a2"]})
    same = next(c for c in r.json() if c["slug"] == "same-name")
    assert same["name_en"] == "Same Name"
    assert same["native_name"] == "Same Name"
    primary = same["name_en"] or same["name"]
    # 前端条件：native != primary 才显示 secondary → 此处应隐藏
    assert same["native_name"] == primary


def test_5_canonical_slug_unchanged(world):
    """Test 5: canonical slug 不变（/character/{slug}/）。"""
    r = client.get("/api/characters", params={"anime_id": world["a1"]})
    slugs = [c["slug"] for c in r.json()]
    assert "tanjiro-kamado" in slugs
    assert "native-only" in slugs


def test_6_anime_id_filter_preserved(world):
    """Test 6: anime_id 过滤保持（Phase 39.z 不回归）。"""
    r = client.get("/api/characters", params={"anime_id": world["a1"]})
    assert {c["slug"] for c in r.json()} == {"tanjiro-kamado", "native-only"}
    r2 = client.get("/api/characters", params={"anime_id": world["a2"]})
    assert {c["slug"] for c in r2.json()} == {"same-name"}


def test_7_global_preserved(world):
    """Test 7: 全局 /api/characters 保持返回全部。"""
    r = client.get("/api/characters")
    assert r.status_code == 200
    assert len(r.json()) == 3
    assert "tanjiro-kamado" in {c["slug"] for c in r.json()}
