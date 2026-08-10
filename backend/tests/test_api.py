import os
import tempfile

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.seed import SAMPLE_ANIME

_tmp = tempfile.mkdtemp()
TEST_DB_PATH = os.path.join(_tmp, "test_animehub.db")

engine = create_engine(
    f"sqlite:///{TEST_DB_PATH}",
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def _clean_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    from app.models import Anime

    db = TestingSessionLocal()
    try:
        for item in SAMPLE_ANIME:
            db.add(Anime(**item))
        db.commit()
    finally:
        db.close()


def _register(username="alice", email="alice@example.com", password="secret123"):
    return client.post(
        "/api/register",
        json={"username": username, "email": email, "password": password},
    )


def _auth_headers(username="alice", password="secret123"):
    res = client.post(
        "/api/login", json={"username": username, "password": password}
    )
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# ---------- Anime API ----------

def test_list_anime_returns_array_without_page():
    res = client.get("/api/anime")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) == len(SAMPLE_ANIME)


def test_create_anime_requires_admin():
    res = client.post("/api/anime", json={"title": "X", "genre": "Y"})
    assert res.status_code == 401


def test_create_anime_as_admin():
    _register()
    headers = _auth_headers()
    res = client.post(
        "/api/anime",
        json={"title": "Admin Anime", "genre": "Action", "score": 9.0},
        headers=headers,
    )
    assert res.status_code == 200
    assert res.json()["title"] == "Admin Anime"


def test_get_anime_not_found():
    res = client.get("/api/anime/99999")
    assert res.status_code == 404


def test_get_anime_ok():
    res = client.get("/api/anime/1")
    assert res.status_code == 200
    assert res.json()["title"] == SAMPLE_ANIME[0]["title"]


def test_update_anime_requires_admin():
    res = client.put("/api/anime/1", json={"title": "New Title"})
    assert res.status_code == 401


def test_delete_anime_requires_admin():
    res = client.delete("/api/anime/1")
    assert res.status_code == 401


def test_bulk_create_requires_admin():
    res = client.post(
        "/api/anime/bulk",
        json={"items": [{"title": "Bulk1", "genre": "G", "score": 7.0}]},
    )
    assert res.status_code == 401


# ---------- Categories ----------


def test_list_categories():
    res = client.get("/api/anime/categories")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert any(c["genre"] == "动作/奇幻" for c in data)


# ---------- Comments ----------


def test_comments_require_login():
    res = client.post("/api/anime/1/comments", json={"content": "hi"})
    assert res.status_code == 401


def test_comments_list():
    res = client.get("/api/anime/1/comments")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


# ---------- Favorites ----------


def test_favorites_require_login():
    res = client.post("/api/favorites/1")
    assert res.status_code == 401


def test_list_favorites_requires_login():
    res = client.get("/api/favorites")
    assert res.status_code == 401

# ---------- Pagination ----------


def test_pagination_page_object():
    res = client.get("/api/anime", params={"page": 1, "page_size": 2})
    assert res.status_code == 200
    data = res.json()
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert data["total"] == len(SAMPLE_ANIME)
    assert len(data["items"]) == 2
    assert data["pages"] == 2


def test_pagination_pages_do_not_overlap():
    p1 = client.get("/api/anime", params={"page": 1, "page_size": 2}).json()
    p2 = client.get("/api/anime", params={"page": 2, "page_size": 2}).json()
    ids1 = {a["id"] for a in p1["items"]}
    ids2 = {a["id"] for a in p2["items"]}
    assert len(ids1 & ids2) == 0
    assert len(p2["items"]) == 1


def test_pagination_combined_with_search():
    res = client.get("/api/anime", params={"q": "巨人", "page": 1, "page_size": 2})
    data = res.json()
    assert data["total"] >= 1
    assert all("巨人" in a["title"] for a in data["items"])


def test_legacy_array_response_unchanged():
    # Without `page`, the API still returns a plain array (backward compat).
    res = client.get("/api/anime")
    assert res.status_code == 200
    assert isinstance(res.json(), list)
    assert len(res.json()) == len(SAMPLE_ANIME)


def test_year_field_in_anime():
    res = client.get("/api/anime")
    data = res.json()
    assert all("year" in a for a in data)


def test_search_returns_matching_titles():
    res = client.get("/api/anime", params={"q": "巨人"})
    assert res.status_code == 200
    data = res.json()
    assert any("巨人" in a["title"] for a in data)




