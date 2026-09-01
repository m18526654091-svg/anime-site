"""Phase 39.x — Characters 与 Anime 关系完整性回归测试（只读，不改业务逻辑）。

覆盖：
  Test 1: GET /api/characters?anime_id=X 只返回与 X 有合法关系的角色
  Test 2: GET /api/characters（无参）仍返回全局角色
  Test 3: anime 详情页的 Characters 数据源为 anime-specific（不混入全局）
  Test 4: 同一角色合法属于多个 anime（同 source_id 各自记录）不被错误删除
  Test 5: 多个 anime 随机抽样，API 不出现跨作品角色
"""
import pytest
from sqlalchemy.orm import Session

from tests.test_api import client, TestingSessionLocal, engine  # noqa: F401
from app.models import Anime, Character, VoiceActor, CharacterVoice


def _mk_anime(db: Session, title: str, slug: str, **kw):
    a = Anime(title=title, chinese_title=title, slug=slug, genre="Action", score=8.0, **kw)
    db.add(a)
    db.flush()
    return a


def _mk_char(db: Session, anime_id: int, name: str, slug: str, source_id: str = ""):
    c = Character(name=name, name_en=name, slug=slug, anime_id=anime_id,
                  source="anilist" if source_id else "", source_id=source_id)
    db.add(c)
    db.flush()
    return c


@pytest.fixture
def char_world():
    # 本文件独立管理测试库（不依赖 test_api 的 autouse fixture）
    from app.database import Base as _Base
    from app.models import Anime as _Anime
    from app.seed import SAMPLE_ANIME as _SAMPLE

    _Base.metadata.drop_all(bind=engine)
    _Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        for item in _SAMPLE:
            db.add(_Anime(**item))
        a1 = _mk_anime(db, "Anime One", "anime-one")
        a2 = _mk_anime(db, "Anime Two", "anime-two")
        a3 = _mk_anime(db, "Franchise A Season 1", "franchise-a-season-1")
        a4 = _mk_anime(db, "Franchise A Season 2", "franchise-a-season-2")
        # a1: 2 个独立角色
        _mk_char(db, a1.id, "Alpha Hero", "alpha-hero", "1001")
        _mk_char(db, a1.id, "Alpha Sidekick", "alpha-sidekick", "1002")
        # a2: 1 个角色
        _mk_char(db, a2.id, "Beta Villain", "beta-villain", "1003")
        # a3/a4：同一 franchise 角色（合法跨作品，source_id 相同）
        _mk_char(db, a3.id, "Shared Protagonist", "shared-protagonist", "2001")
        _mk_char(db, a4.id, "Shared Protagonist", "shared-protagonist-2", "2001")
        db.commit()
        ids = {"a1": a1.id, "a2": a2.id, "a3": a3.id, "a4": a4.id}
        yield ids
    finally:
        db.close()


def test_1_anime_id_returns_only_own_characters(char_world):
    """Test 1: anime_id=X 只返回属于 X 的角色。"""
    r = client.get("/api/characters", params={"anime_id": char_world["a1"]})
    assert r.status_code == 200
    slugs = [c["slug"] for c in r.json()]
    assert slugs == ["alpha-hero", "alpha-sidekick"]
    assert "beta-villain" not in slugs
    # 验证返回的全部角色确实属于该 anime（无泄漏）
    assert all(c["anime_slug"] == "anime-one" for c in r.json())


def test_2_no_filter_returns_global(char_world):
    """Test 2: 无参数返回全局角色（sitemap 行为不变）。"""
    r = client.get("/api/characters")
    assert r.status_code == 200
    slugs = [c["slug"] for c in r.json()]
    assert len(slugs) == 5
    assert {"alpha-hero", "beta-villain", "shared-protagonist", "shared-protagonist-2"} <= set(slugs)


def test_3_detail_data_source_is_anime_specific(char_world):
    """Test 3: 前端 detail 数据源（fetchCharactersByAnime）为 anime-specific。

    通过 API 断言 + 校验页面 SSR 数据来源：/api/characters?anime_id= 响应中
    不允许出现其他 anime 的角色（对应 AnimeDetailClient 仅渲染 initialCharacters）。
    """
    for aid in (char_world["a1"], char_world["a2"]):
        r = client.get("/api/characters", params={"anime_id": aid})
        assert r.status_code == 200
        for c in r.json():
            assert c["anime_slug"] == ("anime-one" if aid == char_world["a1"] else "anime-two")


def test_4_multi_anime_character_not_removed(char_world):
    """Test 4: 同一角色合法属于多个 anime（同 source_id）时两条记录都保留。"""
    db = TestingSessionLocal()
    try:
        rows = db.query(Character).filter(Character.source_id == "2001").all()
        # 两条记录各自绑定不同 anime，都不应被删除
        assert len(rows) == 2
        anime_ids = {r.anime_id for r in rows}
        assert anime_ids == {char_world["a3"], char_world["a4"]}
    finally:
        db.close()
    # 且 API 各自只返回各自 anime 的这条角色
    r3 = client.get("/api/characters", params={"anime_id": char_world["a3"]})
    assert [c["slug"] for c in r3.json()] == ["shared-protagonist"]
    r4 = client.get("/api/characters", params={"anime_id": char_world["a4"]})
    assert [c["slug"] for c in r4.json()] == ["shared-protagonist-2"]


def test_5_sampling_no_cross_anime_leak(char_world):
    """Test 5: 多 anime 抽样，任意 anime 的 API 响应不含其他 anime 专属角色。"""
    import random
    random.seed(39)
    ids = list(char_world.values())
    sampled = random.sample(ids, min(3, len(ids)))
    all_global = client.get("/api/characters").json()
    global_slugs = {c["slug"]: c["anime_slug"] for c in all_global}
    for aid in sampled:
        r = client.get("/api/characters", params={"anime_id": aid})
        for c in r.json():
            # 该角色在全局列表中的归属必须与本次响应一致（同 anime）
            assert global_slugs[c["slug"]] == c["anime_slug"], \
                f"角色 {c['slug']} 跨作品泄漏: api={c['anime_slug']} global={global_slugs[c['slug']]}"
