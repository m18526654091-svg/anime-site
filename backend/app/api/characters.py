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
    native_name: Optional[str] = None
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
    # Phase 40-A：暴露本地化名称（英文主显示 + 日文原生辅助），兼容旧响应
    name_en: Optional[str] = None
    native_name: Optional[str] = None
    # Sprint 6-D：按 anime_id 查询时附带该角色的配音声优（供详情页 SSR 实体内链）
    voice_actors: List[VoiceActorLite] = []


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
        id=ch.id, name=ch.name, name_en=ch.name_en or "", native_name=ch.native_name or None,
        slug=ch.slug,
        description=ch.description or "", aliases=ch.aliases or "", image=ch.image or "",
        anime=AnimeLite(id=anime.id, title=anime.title, chinese_title=anime.chinese_title or "",
                        slug=anime.slug) if anime else None,
        voice_actors=[VoiceActorLite(id=v.id, name=v.name, slug=v.slug) for v in vas],
    )


@router.get("", response_model=List[CharacterLite])
def list_characters(
    anime_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """角色列表。

    - 无参数：返回全部角色（sitemap 使用，行为与之前一致）。
    - anime_id=X：仅返回该动漫的角色，并附带每位角色的配音声优
      （Sprint 6-D：anime 详情页 SSR 实体内链使用）。
    """
    query = db.query(Character, Anime.slug).join(Anime, Anime.id == Character.anime_id)
    if anime_id is not None:
        query = query.filter(Character.anime_id == anime_id)
    rows = query.all()
    result: list[CharacterLite] = []
    for c, a_slug in rows:
        vas: list[VoiceActorLite] = []
        if anime_id is not None:
            va_rows = (
                db.query(VoiceActor)
                .join(CharacterVoice, CharacterVoice.voice_actor_id == VoiceActor.id)
                .filter(CharacterVoice.character_id == c.id)
                .all()
            )
            vas = [VoiceActorLite(id=v.id, name=v.name, slug=v.slug) for v in va_rows]
        result.append(
            CharacterLite(
                id=c.id, name=c.name, slug=c.slug, anime_slug=a_slug,
                name_en=c.name_en or None, native_name=c.native_name or None,
                voice_actors=vas,
            )
        )
    return result
