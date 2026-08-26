"""角色实体 API（Stage: 角色+声优 SEO MVP）。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import Anime, Character, CharacterVoice, VoiceActor
from pydantic import BaseModel
from typing import Optional, List


class AnimeLite(BaseModel):
    id: int
    title: str
    chinese_title: str
    slug: str


class VoiceActorLite(BaseModel):
    id: int
    name: str
    slug: str


class CharacterOut(BaseModel):
    id: int
    name: str
    name_en: str
    slug: str
    description: str
    aliases: str
    image: str
    anime: Optional[AnimeLite] = None
    voice_actors: List[VoiceActorLite] = []


class CharacterLite(BaseModel):
    id: int
    name: str
    slug: str
    anime_slug: Optional[str] = None


router = APIRouter(prefix="/api/characters", tags=["characters"])


@router.get("/{slug}", response_model=CharacterOut)
def get_character(slug: str, db: Session = Depends(get_db)):
    ch = db.query(Character).filter(func.lower(Character.slug) == slug.lower()).first()
    if ch is None:
        raise HTTPException(status_code=404, detail="Character not found")
    anime = db.query(Anime).filter(Anime.id == ch.anime_id).first()
    vas = (
        db.query(VoiceActor)
        .join(CharacterVoice, CharacterVoice.voice_actor_id == VoiceActor.id)
        .filter(CharacterVoice.character_id == ch.id)
        .all()
    )
    return CharacterOut(
        id=ch.id, name=ch.name, name_en=ch.name_en or "", slug=ch.slug,
        description=ch.description or "", aliases=ch.aliases or "", image=ch.image or "",
        anime=AnimeLite(id=anime.id, title=anime.title, chinese_title=anime.chinese_title or "",
                        slug=anime.slug) if anime else None,
        voice_actors=[VoiceActorLite(id=v.id, name=v.name, slug=v.slug) for v in vas],
    )


@router.get("", response_model=List[CharacterLite])
def list_characters(db: Session = Depends(get_db)):
    rows = db.query(Character, Anime.slug).join(Anime, Anime.id == Character.anime_id).all()
    return [CharacterLite(id=c.id, name=c.name, slug=c.slug, anime_slug=a_slug)
            for c, a_slug in rows]
