from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_admin, get_current_user, get_optional_user
from ..models import Anime, Rating, User
from ..schemas import (
    AnimeCreate,
    AnimeOut,
    AnimePage,
    AnimeUpdate,
    BulkAnimeIn,
    CategoryStat,
    RatingCreate,
    RatingOut,
)

router = APIRouter(prefix="/api/anime", tags=["anime"])


def _rating_stats(db: Session, anime_id: int) -> tuple[float, int]:
    row = db.execute(
        select(
            func.coalesce(func.avg(Rating.score), 0),
            func.coalesce(func.count(Rating.id), 0),
        ).where(Rating.anime_id == anime_id)
    ).first()
    return float(row[0] or 0), int(row[1] or 0)


def _serialize(db: Session, anime: Anime) -> AnimeOut:
    avg, count = _rating_stats(db, anime.id)
    payload = anime.__dict__.copy()
    payload["avg_score"] = avg
    payload["rating_count"] = count
    return AnimeOut.model_validate(payload)


@router.get("")
def list_anime(
    q: Optional[str] = None,
    category: Optional[str] = None,
    tag: Optional[str] = None,
    year: Optional[int] = None,
    region: Optional[str] = None,
    author: Optional[str] = None,
    studio: Optional[str] = None,
    sort: Optional[str] = Query(default=None, regex="^(latest|score|year)$"),
    page: Optional[int] = None,
    page_size: int = 18,
    db: Session = Depends(get_db),
):
    query = db.query(Anime)
    if q:
        query = query.filter(Anime.title.contains(q))
    if category:
        query = query.filter(Anime.genre == category)
    if tag:
        query = query.filter(Anime.tags.contains(tag))
    if year:
        query = query.filter(Anime.year == year)
    if region:
        query = query.filter(Anime.region == region)
    if author:
        query = query.filter(Anime.author == author)
    if studio:
        query = query.filter(Anime.studio == studio)

    ordering = {
        "score": Anime.score.desc(),
        "year": Anime.year.desc(),
        "latest": Anime.id.desc(),
    }.get(sort or "latest", Anime.id.desc())
    query = query.order_by(ordering)

    if page is None:
        return [
            _serialize(db, a) for a in query.limit(min(max(page_size, 1), 100)).all()
        ]

    page = max(int(page), 1)
    page_size = min(max(int(page_size), 1), 100)
    total = query.count()
    items = (
        query.order_by(ordering)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return AnimePage(
        items=[_serialize(db, a) for a in items],
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size if total else 0,
    )


@router.get("/categories", response_model=list[CategoryStat])
def list_categories(db: Session = Depends(get_db)):
    rows = (
        db.execute(
            select(Anime.genre, func.count(Anime.id))
            .where(Anime.genre != "")
            .group_by(Anime.genre)
            .order_by(func.count(Anime.id).desc())
        )
        .all()
    )
    return [CategoryStat(genre=g, count=c) for g, c in rows]


@router.get("/tags")
def list_tags(db: Session = Depends(get_db)):
    rows = db.execute(select(Anime.tags).where(Anime.tags != "")).all()
    tag_counts: dict[str, int] = {}
    for (tags,) in rows:
        if not tags:
            continue
        for t in tags.split("/"):
            t = t.strip()
            if t:
                tag_counts[t] = tag_counts.get(t, 0) + 1
    return sorted(
        [{"tag": k, "count": v} for k, v in tag_counts.items()],
        key=lambda x: x["count"],
        reverse=True,
    )


@router.get("/years")
def list_years(db: Session = Depends(get_db)):
    rows = (
        db.execute(
            select(Anime.year, func.count(Anime.id))
            .where(Anime.year.is_not(None))
            .group_by(Anime.year)
            .order_by(Anime.year.desc())
        )
        .all()
    )
    return [{"year": y, "count": c} for y, c in rows if y is not None]


@router.get("/people")
def list_people(db: Session = Depends(get_db)):
    author_rows = (
        db.execute(
            select(Anime.author, func.count(Anime.id))
            .where(Anime.author != "")
            .group_by(Anime.author)
            .order_by(func.count(Anime.id).desc())
        )
        .all()
    )
    studio_rows = (
        db.execute(
            select(Anime.studio, func.count(Anime.id))
            .where(Anime.studio != "")
            .group_by(Anime.studio)
            .order_by(func.count(Anime.studio).desc())
        )
        .all()
    )
    people = {}
    for name, count in author_rows:
        if name:
            people[name] = people.get(name, 0) + count
    for name, count in studio_rows:
        if name:
            people[name] = people.get(name, 0) + count
    return sorted(
        [{"name": k, "count": v} for k, v in people.items()],
        key=lambda x: x["count"],
        reverse=True,
    )


@router.get("/regions")
def list_regions(db: Session = Depends(get_db)):
    rows = (
        db.execute(
            select(Anime.region, func.count(Anime.id))
            .where(Anime.region != "")
            .group_by(Anime.region)
            .order_by(func.count(Anime.id).desc())
        )
        .all()
    )
    return [{"region": r, "count": c} for r, c in rows]


@router.get("/{anime_id}", response_model=AnimeOut)
def get_anime(anime_id: int, db: Session = Depends(get_db)):
    anime = db.get(Anime, anime_id)
    if not anime:
        raise HTTPException(status_code=404, detail="Anime not found")
    return _serialize(db, anime)


@router.post("", response_model=AnimeOut)
def create_anime(
    data: AnimeCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_admin),
):
    anime = Anime(**data.model_dump())
    db.add(anime)
    db.commit()
    db.refresh(anime)
    return _serialize(db, anime)


@router.post("/bulk")
def bulk_create_anime(
    data: BulkAnimeIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_admin),
):
    existing = {t for (t,) in db.query(Anime.title).all()}
    added = 0
    skipped = 0
    for item in data.items:
        title = (item.title or "").strip()
        if not title or title in existing:
            skipped += 1
            continue
        db.add(Anime(**item.model_dump()))
        existing.add(title)
        added += 1
    db.commit()
    total = db.query(Anime).count()
    return {"added": added, "skipped": skipped, "total": total}


@router.put("/{anime_id}", response_model=AnimeOut)
def update_anime(
    anime_id: int,
    data: AnimeUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_admin),
):
    anime = db.get(Anime, anime_id)
    if not anime:
        raise HTTPException(status_code=404, detail="Anime not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(anime, key, value)
    db.commit()
    db.refresh(anime)
    return _serialize(db, anime)


@router.delete("/{anime_id}")
def delete_anime(
    anime_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_admin),
):
    anime = db.get(Anime, anime_id)
    if not anime:
        raise HTTPException(status_code=404, detail="Anime not found")
    db.delete(anime)
    db.commit()
    return {"ok": True}


# ===== Ratings =====


@router.post("/{anime_id}/ratings", response_model=RatingOut)
def rate_anime(
    anime_id: int,
    data: RatingCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    anime = db.get(Anime, anime_id)
    if not anime:
        raise HTTPException(status_code=404, detail="Anime not found")

    score = int(data.score)
    if score < 1 or score > 10:
        raise HTTPException(status_code=400, detail="Score must be 1..10")

    rating = (
        db.query(Rating)
        .filter(Rating.anime_id == anime_id, Rating.user_id == user.id)
        .first()
    )
    if rating:
        rating.score = score
    else:
        rating = Rating(anime_id=anime_id, user_id=user.id, score=score)
        db.add(rating)
    db.commit()
    db.refresh(rating)
    return {
        "id": rating.id,
        "anime_id": rating.anime_id,
        "user_id": rating.user_id,
        "username": user.username,
        "score": rating.score,
        "created_at": rating.created_at,
    }


@router.get("/{anime_id}/ratings", response_model=dict)
def get_ratings(
    anime_id: int,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user),
):
    if not db.get(Anime, anime_id):
        raise HTTPException(status_code=404, detail="Anime not found")
    avg, count = _rating_stats(db, anime_id)
    my_score: Optional[int] = None
    if user:
        row = db.execute(
            select(Rating.score).where(
                Rating.anime_id == anime_id, Rating.user_id == user.id
            )
        ).first()
        if row is not None:
            my_score = int(row[0])
    return {"avg_score": avg, "rating_count": count, "my_score": my_score}
