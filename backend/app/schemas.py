from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    is_admin: int = 0


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class AnimeBase(BaseModel):
    title: str
    chinese_title: Optional[str] = ""
    slug: Optional[str] = ""
    cover: Optional[str] = ""
    description: Optional[str] = ""
    genre: Optional[str] = ""
    tags: Optional[str] = ""
    year: Optional[int] = None
    month: Optional[int] = None  # 首播月份 1-12，用于季度页
    region: Optional[str] = ""
    author: Optional[str] = ""
    studio: Optional[str] = ""
    status: Optional[str] = ""
    letter: Optional[str] = ""
    episodes: Optional[int] = None
    score: Optional[float] = 0.0
    seo_title: Optional[str] = ""
    seo_description: Optional[str] = ""
    play_data: Optional[str] = ""
    quality_score: Optional[int] = 100
    is_indexable: Optional[int] = 1
    updated_at: Optional[datetime] = None


class AnimeCreate(AnimeBase):
    pass


class AnimeUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    cover: Optional[str] = None
    description: Optional[str] = None
    genre: Optional[str] = None
    tags: Optional[str] = None
    year: Optional[int] = None
    region: Optional[str] = None
    author: Optional[str] = None
    studio: Optional[str] = None
    status: Optional[str] = None
    letter: Optional[str] = None
    episodes: Optional[int] = None
    score: Optional[float] = None
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    play_data: Optional[str] = None


class AnimeOut(AnimeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    avg_score: float = 0.0
    rating_count: int = 0
    updated_at: Optional[datetime] = None


class AnimePage(BaseModel):
    items: list[AnimeOut]
    total: int
    page: int
    page_size: int
    pages: int


class EpisodeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    anime_id: int
    episode_number: int
    title: str
    video_url: str
    created_at: datetime


class EpisodesOut(BaseModel):
    items: list[EpisodeOut]
    total: int


# --- admin / stats helpers ---


class CategoryStat(BaseModel):
    genre: str
    count: int


class StatsOut(BaseModel):
    anime_count: int
    user_count: int
    comment_count: int
    favorite_count: int
    rating_count: int
    genres: list[CategoryStat]


class AdminUserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    is_admin: int
    anime_count: int = 0
    comment_count: int = 0
    rating_count: int = 0
    favorite_count: int = 0


class BulkAnimeIn(BaseModel):
    items: list[AnimeCreate]


class RatingBase(BaseModel):
    score: int  # 1..10


class RatingCreate(RatingBase):
    pass


class RatingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    anime_id: int
    user_id: int
    username: str
    score: int
    created_at: Optional[datetime] = None


class CommentCreate(BaseModel):
    content: str


class CommentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    anime_id: int
    user_id: int
    username: str = ""
    content: str
