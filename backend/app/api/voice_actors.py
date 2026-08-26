"""声优实体 API（Stage: 角色+声优 SEO MVP）。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import Anime, Character, CharacterVoice, VoiceActor
from pydantic import BaseModel
from typing import Optional, List


class RoleLite(BaseModel):
    id: int
    name: str
    slug: str
    anime_title: Optional[str] = None
    anime_slug: Optional[str] = None


class VoiceActorOut(BaseModel):
    id: int
    name: str
    name_en: str
    slug: str
    description: str
    aliases: str
    image: str
    characters: List[RoleLite] = []


class VoiceActorLiteOut(BaseModel):
    id: int
    name: str
    slug: str


router = APIRouter(prefix="/api/voice-actors", tags=["voice_actors"])


@router.get("/{slug}", response_model=VoiceActorOut)
def get_voice_actor(slug: str, db: Session = Depends(get_db)):
    va = db.query(VoiceActor).filter(func.lower(VoiceActor.slug) == slug.lower()).first()
    if va is None:
        raise HTTPException(status_code=404, detail="Voice actor not found")
    rows = (
        db.query(Character, Anime.title, Anime.slug)
        .join(CharacterVoice, CharacterVoice.character_id == Character.id)
        .join(Anime, Anime.id == Character.anime_id)
        .filter(CharacterVoice.voice_actor_id == va.id)
        .all()
    )
    return VoiceActorOut(
        id=va.id, name=va.name, name_en=va.name_en or "", slug=va.slug,
        description=va.description or "", aliases=va.aliases or "", image=va.image or "",
        characters=[RoleLite(id=c.id, name=c.name, slug=c.slug,
                             anime_title=a_title, anime_slug=a_slug) for c, a_title, a_slug in rows],
    )


@router.get("", response_model=List[VoiceActorLiteOut])
def list_voice_actors(db: Session = Depends(get_db)):
    rows = db.query(VoiceActor).all()
    return [VoiceActorLiteOut(id=v.id, name=v.name, slug=v.slug) for v in rows]
