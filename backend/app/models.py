from datetime import datetime

from sqlalchemy import (
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
