from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import Anime, Favorite, User
from ..schemas import AnimeOut

router = APIRouter(prefix="/api/favorites", tags=["favorites"])


@router.get("", response_model=list[AnimeOut])
def my_favorites(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    favs = (
        db.query(Favorite)
        .filter(Favorite.user_id == user.id)
        .order_by(Favorite.id.desc())
        .all()
    )
    return [db.get(Anime, f.anime_id) for f in favs]


@router.post("/{anime_id}")
def add_favorite(
    anime_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not db.get(Anime, anime_id):
        raise HTTPException(status_code=404, detail="动漫不存在")
    exists = (
        db.query(Favorite)
        .filter(Favorite.user_id == user.id, Favorite.anime_id == anime_id)
        .first()
    )
    if exists:
        return {"ok": True, "added": False}
    db.add(Favorite(user_id=user.id, anime_id=anime_id))
    db.commit()
    return {"ok": True, "added": True}


@router.delete("/{anime_id}")
def remove_favorite(
    anime_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    fav = (
        db.query(Favorite)
        .filter(Favorite.user_id == user.id, Favorite.anime_id == anime_id)
        .first()
    )
    if fav:
        db.delete(fav)
        db.commit()
    return {"ok": True}
