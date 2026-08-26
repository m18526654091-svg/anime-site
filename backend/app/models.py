from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_admin = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    comments = relationship("Comment", back_populates="user")
    favorites = relationship("Favorite", back_populates="user")
    ratings = relationship("Rating", back_populates="user", cascade="all, delete-orphan")


class Anime(Base):
    __tablename__ = "anime"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    chinese_title = Column(String(200), default="")
    slug = Column(String(220), default="", index=True)
    cover = Column(Text, default="")
    description = Column(Text, default="")
    genre = Column(String(100), default="")
    tags = Column(String(500), default="")
    year = Column(Integer, nullable=True)
    month = Column(Integer, nullable=True)  # 首播月份 1-12，用于季度/新番页
    region = Column(String(50), default="")
    author = Column(String(100), default="")
    studio = Column(String(100), default="")
    status = Column(String(20), default="")
    letter = Column(String(1), default="", index=True)
    episodes = Column(Integer, nullable=True)
    score = Column(Float, default=0.0, index=True)
    # 外部稳定身份（Stage 10-B）：可空，暂不启动回填/同步
    anilist_id = Column(Integer, nullable=True, index=True)
    mal_id = Column(Integer, nullable=True, index=True)
    seo_title = Column(String(200), default="")
    seo_description = Column(String(500), default="")
    quality_score = Column(Integer, default=100, index=True)  # 内容质量分 0-100
    is_indexable = Column(Integer, default=1, index=True)  # 1=进sitemap；0=不提交sitemap
    play_data = Column(Text, default="")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    comments = relationship("Comment", back_populates="anime")
    favorites = relationship("Favorite", back_populates="anime")
    ratings = relationship("Rating", back_populates="anime", cascade="all, delete-orphan")
    episodes_list = relationship("Episode", back_populates="anime", cascade="all, delete-orphan")
    characters = relationship("Character", back_populates="anime", cascade="all, delete-orphan")


class Episode(Base):
    __tablename__ = "episodes"

    id = Column(Integer, primary_key=True, index=True)
    anime_id = Column(Integer, ForeignKey("anime.id"), nullable=False, index=True)
    episode_number = Column(Integer, nullable=False)
    title = Column(String(200), default="")
    video_url = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    anime = relationship("Anime", back_populates="episodes_list")


class Rating(Base):
    __tablename__ = "ratings"
    __table_args__ = (UniqueConstraint("user_id", "anime_id", name="uq_user_anime_rating"),)

    id = Column(Integer, primary_key=True, index=True)
    anime_id = Column(Integer, ForeignKey("anime.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    score = Column(Integer, nullable=False)  # 1..10
    created_at = Column(DateTime, default=datetime.utcnow)

    anime = relationship("Anime", back_populates="ratings")
    user = relationship("User", back_populates="ratings")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    anime_id = Column(Integer, ForeignKey("anime.id"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="comments")
    anime = relationship("Anime", back_populates="comments")


class Favorite(Base):
    __tablename__ = "favorites"
    __table_args__ = (UniqueConstraint("user_id", "anime_id", name="uq_user_anime"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    anime_id = Column(Integer, ForeignKey("anime.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="favorites")
    anime = relationship("Anime", back_populates="favorites")


# =====================================================================
# Stage 12-B：数据治理基础设施（独立治理层，不影响现有业务表）
# =====================================================================


class DataSource(Base):
    """数据源登记表（来源注册，不代表全部可用于生产）。"""

    __tablename__ = "data_sources"

    id = Column(Integer, primary_key=True, index=True)
    source_key = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(120), nullable=False)
    source_type = Column(String(20), default="api")  # api | dump | manual | scrape
    license = Column(String(80), default="")
    license_url = Column(Text, default="")
    attribution = Column(Integer, default=0)  # 0=不需要 1=需要
    # NULL=UNVERIFIED；1=允许商业；0=不允许
    commercial_ok = Column(Integer, nullable=True)
    # active | paused | excluded | unverified
    status = Column(String(20), default="unverified")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ExternalEntity(Base):
    """外部实体映射（AniList/MAL/Wikidata 等 → AnimeHub anime）。"""

    __tablename__ = "external_entities"
    __table_args__ = (
        UniqueConstraint("source_id", "source_entity_id", name="uq_external_source_entity"),
        CheckConstraint(
            "status IN ('candidate','verified','rejected','ambiguous')",
            name="ck_external_status",
        ),
        CheckConstraint("confidence >= 0 AND confidence <= 100", name="ck_external_confidence"),
        CheckConstraint(
            "NOT (status = 'verified' AND anime_id IS NULL)",
            name="ck_external_verified_needs_anime",
        ),
        CheckConstraint("source_entity_id <> ''", name="ck_external_entity_id_not_empty"),
    )

    id = Column(Integer, primary_key=True, index=True)
    anime_id = Column(Integer, ForeignKey("anime.id"), nullable=True, index=True)
    source_id = Column(Integer, ForeignKey("data_sources.id"), nullable=False, index=True)
    source_entity_id = Column(String(80), nullable=False)
    # candidate | verified | rejected | ambiguous
    status = Column(String(20), default="candidate", nullable=False)
    confidence = Column(Integer, default=0)  # 0-100
    canonical = Column(Integer, default=0)
    # 仅保存与实体匹配直接相关的必要快照，绝不保存完整 API response
    raw_snapshot = Column(Text, default="")
    value_hash = Column(String(64), default="")
    verified_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AnimeFieldSource(Base):
    """字段级来源追踪（字段值来自哪个数据源）。"""

    __tablename__ = "anime_field_sources"
    __table_args__ = (
        UniqueConstraint("anime_id", "field_name", "source_id", name="uq_anime_field_source"),
    )

    id = Column(Integer, primary_key=True, index=True)
    anime_id = Column(Integer, ForeignKey("anime.id"), nullable=False, index=True)
    field_name = Column(String(50), nullable=False)
    source_id = Column(Integer, ForeignKey("data_sources.id"), nullable=False, index=True)
    value_hash = Column(String(64), default="")
    # 普通文本存规范化字段值；图片只存 URL / source reference，不存二进制
    source_value = Column(Text, default="")
    verified = Column(Integer, default=0)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class VoiceActor(Base):
    """声优 / 配音演员（Stage: 角色+声优 SEO MVP）。"""

    __tablename__ = "voice_actors"
    __table_args__ = (
        UniqueConstraint("slug", name="uq_voice_actor_slug"),
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False, index=True)   # 中文名（常用名）
    name_en = Column(String(120), default="")
    native_name = Column(String(120), default="")  # 日文原名
    slug = Column(String(160), default="", index=True)
    description = Column(Text, default="")
    aliases = Column(String(300), default="")  # 别名，逗号分隔
    image = Column(Text, default="")
    source = Column(String(40), default="")      # 数据来源（anilist / manual / ...）
    source_id = Column(String(64), default="")   # 外部稳定 ID
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    characters = relationship("Character", secondary="character_voices",
                              back_populates="voice_actors")


class Character(Base):
    """动漫角色（Stage: 角色+声优 SEO MVP）。"""

    __tablename__ = "characters"
    __table_args__ = (
        UniqueConstraint("slug", name="uq_character_slug"),
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False, index=True)   # 中文名（常用名）
    name_en = Column(String(120), default="")
    native_name = Column(String(120), default="")  # 日文原名
    slug = Column(String(160), default="", index=True)
    description = Column(Text, default="")
    aliases = Column(String(300), default="")  # 别名，逗号分隔
    image = Column(Text, default="")
    source = Column(String(40), default="")      # 数据来源（anilist / manual / ...）
    source_id = Column(String(64), default="")   # 外部稳定 ID
    anime_id = Column(Integer, ForeignKey("anime.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    anime = relationship("Anime", back_populates="characters")
    voice_actors = relationship("VoiceActor", secondary="character_voices",
                                back_populates="characters")


class CharacterVoice(Base):
    """角色-声优关系（角色 → 声优）。"""

    __tablename__ = "character_voices"
    __table_args__ = (
        UniqueConstraint("character_id", "voice_actor_id", name="uq_character_voice"),
    )

    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=False, index=True)
    voice_actor_id = Column(Integer, ForeignKey("voice_actors.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
