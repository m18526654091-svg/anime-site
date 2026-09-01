from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_admin, get_current_user, get_optional_user
from ..models import Anime, Episode, Rating, User
from ..schemas import (
    AnimeCreate,
    AnimeOut,
    AnimePage,
    AnimeUpdate,
    BulkAnimeIn,
    CategoryStat,
    EpisodeOut,
    EpisodesOut,
    RatingCreate,
    RatingOut,
)
from ..letter_util import compute_letter

router = APIRouter(prefix="/api/anime", tags=["anime"])

# 季度 -> 首播月份范围（12/1/2 冬季，3/4/5 春季，6/7/8 夏季，9/10/11 秋季）
SEASON_MONTHS: dict[str, tuple[int, ...]] = {
    "winter": (12, 1, 2),
    "spring": (3, 4, 5),
    "summer": (6, 7, 8),
    "autumn": (9, 10, 11),
}


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
    status: Optional[str] = None,
    letter: Optional[str] = None,
    author: Optional[str] = None,
    studio: Optional[str] = None,
    sort: Optional[str] = Query(default=None, regex="^(latest|score|year|quality)$"),
    season: Optional[str] = Query(default=None, regex="^(winter|spring|summer|autumn)$"),
    page: Optional[int] = None,
    page_size: int = 18,
    db: Session = Depends(get_db),
):
    query = db.query(Anime)
    if q:
        # 中文名 / 原名 / slug / 多语言标题 模糊匹配
        # （Phase 35：新增 japanese_title / romaji_title / aliases 匹配，
        #   实现"进击的巨人/Shingeki no Kyojin/Attack on Titan"解析到同一实体）
        query = query.filter(
            or_(
                Anime.title.contains(q),
                Anime.chinese_title.contains(q),
                Anime.slug.contains(q),
                Anime.japanese_title.contains(q),
                Anime.romaji_title.contains(q),
                Anime.aliases.contains(q),
            )
        )
    if category:
        # genre 存为多值字符串（如 "动作/奇幻/战斗"），用子串匹配以兼容前端
        # genreMatch 的分词匹配行为，避免因精确等值匹配导致 /categories/动作 返回 0 结果。
        query = query.filter(Anime.genre.contains(category))
    if tag:
        query = query.filter(Anime.tags.contains(tag))
    if year:
        query = query.filter(Anime.year == year)
    if region:
        query = query.filter(Anime.region == region)
    if status:
        query = query.filter(Anime.status == status)
    if letter:
        query = query.filter(func.upper(Anime.letter) == letter.strip().upper())
    if author:
        query = query.filter(Anime.author == author)
    if studio:
        # 大小写不敏感匹配，兼容 /studio/mappa 与 "Mappa" 数据
        query = query.filter(func.lower(Anime.studio) == studio.strip().lower())
    if season:
        # 季度筛选：结合 year 限定年份；有 month 数据的精确匹配，
        # month 为空（旧数据）时保留该年作品，避免季度页空白。
        months = SEASON_MONTHS[season]
        season_filter = Anime.month.is_(None)
        for m in months:
            season_filter = season_filter | (Anime.month == m)
        query = query.filter(season_filter)

    ordering = {
        "score": Anime.score.desc(),
        "year": Anime.year.desc(),
        "quality": (Anime.quality_score.desc(), Anime.score.desc(), Anime.year.desc()),
        "latest": Anime.id.desc(),
    }.get(sort or "latest", Anime.id.desc())
    # 复合排序（quality 优先）需展开为多个参数
    if isinstance(ordering, tuple):
        query = query.order_by(*ordering)
    else:
        query = query.order_by(ordering)

    if page is None:
        return [
            _serialize(db, a) for a in query.limit(min(max(page_size, 1), 100)).all()
        ]

    page = max(int(page), 1)
    page_size = min(max(int(page_size), 1), 100)
    total = query.count()
    items = (
        query.offset((page - 1) * page_size)
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


@router.get("/{anime_id}/episodes", response_model=EpisodesOut)
def list_episodes(anime_id: int, db: Session = Depends(get_db)):
    anime = db.get(Anime, anime_id)
    if not anime:
        raise HTTPException(status_code=404, detail="Anime not found")
    items = (
        db.query(Episode)
        .filter(Episode.anime_id == anime_id)
        .order_by(Episode.episode_number.asc())
        .all()
    )
    return EpisodesOut(items=items, total=len(items))


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


@router.get("/studios")
def list_studios(db: Session = Depends(get_db)):
    """返回有作品的制作公司列表（含作品数），用于 studio 索引页与 sitemap。"""
    rows = (
        db.execute(
            select(Anime.studio, func.count(Anime.id))
            .where(Anime.studio != "")
            .group_by(Anime.studio)
            .order_by(func.count(Anime.id).desc())
        )
        .all()
    )
    return [{"studio": s, "count": c} for s, c in rows if (s or "").strip()]


@router.get("/seasons")
def list_seasons(db: Session = Depends(get_db)):
    """返回有数据覆盖的 (year, season) 组合，用于季度新番页 sitemap。

    有 month 数据的按实际首播月精确匹配季度；month 为空（旧数据）时
    保留该年份的全部四个季度（季度页会按年份展示，保证页面非空）。
    """
    result: dict[tuple[int, str], None] = {}
    # 有 month 数据 → 精确季度
    rows = db.execute(
        select(Anime.year, Anime.month).where(Anime.month.is_not(None))
    ).all()
    for y, m in rows:
        if y is None:
            continue
        for season, months in SEASON_MONTHS.items():
            if m in months:
                result.setdefault((y, season), None)
    # 无 month 数据的年份 → 四个季度都保留（回退按年展示）
    yrows = db.execute(select(Anime.year).where(Anime.year.is_not(None))).all()
    for (y,) in yrows:
        for season in SEASON_MONTHS:
            result.setdefault((y, season), None)

    order = {"winter": 0, "spring": 1, "summer": 2, "autumn": 3}
    out = [{"year": y, "season": s} for (y, s) in result]
    out.sort(key=lambda x: (x["year"], order[x["season"]]), reverse=True)
    return out


# 共享 genre 的英文描述（用于 similar 页面 reason，符合英文搜索表达）
# Phase 44.1：补全高频 genre（对齐前端 GENRE_EN 词条），并确保未映射 genre
# 永不拼出中文——英文页面 reason 不允许出现 raw Chinese。
_GENRE_REASON = {
    "热血": "intense battles and determined protagonists",
    "战斗": "high-octane fight scenes and skilled warriors",
    "动作": "fast-paced action and adrenaline-fueled moments",
    "奇幻": "immersive fantasy worlds and epic quests",
    "冒险": "grand adventures across unknown lands",
    "恋爱": "heartfelt romance and character-driven drama",
    "校园": "relatable school-life stories and coming-of-age moments",
    "科幻": "mind-bending sci-fi concepts and futuristic worlds",
    "悬疑": "mysteries that keep you guessing until the end",
    "推理": "clever mysteries and sharp deductions",
    "异世界": "epic isekai adventures in other worlds",
    "穿越": "thrilling time-travel and otherworldly journeys",
    "机甲": "mecha battles and strategic warfare",
    "搞笑": "sharp comedy and hilariously over-the-top characters",
    "日常": "slice-of-life warmth and everyday charm",
    "治愈": "heartwarming, soothing stories that lift your mood",
    "运动": "competitive sports rivalries and team spirit",
    "音乐": "music-driven stories with memorable performances",
    "恐怖": "tense, unsettling horror atmosphere",
    "黑暗": "dark, mature themes and moral complexity",
    "魔法": "spellbinding magic systems and mystical powers",
    "偶像": "idol performances and dreams of stardom",
    "历史": "epic historical settings and sweeping drama",
    "美食": "mouth-watering food and culinary passion",
    "心理": "deep psychological drama and mind games",
    "剧情": "character-driven drama and emotional depth",
    "超自然": "supernatural forces and otherworldly powers",
    "惊悚": "tense suspense and psychological twists",
    "时代剧": "historical settings and period drama",
    "青春": "youthful coming-of-age stories",
    "战争": "large-scale conflict and wartime stakes",
    "侦探": "clever detective work and unraveling mysteries",
    "异能": "extraordinary abilities and superhuman fights",
    "超能力": "extraordinary abilities and superhuman fights",
    "博弈": "high-stakes games and strategic mind games",
    "生存": "survival stakes and life-or-death decisions",
    "竞技": "competitive rivalries and tournament stakes",
    "格斗": "martial arts duels and hand-to-hand combat",
    "军事": "military operations and tactical warfare",
    "魔法少女": "magical girl transformations and heartfelt battles",
    "黑帮": "mafia underworld and organized crime",
    "职场": "workplace dynamics and office life",
    "福利": "playful, fanservice-driven tone",
}


def _genre_set(genre: str) -> set[str]:
    return {g.strip() for g in (genre or "").split("/") if g.strip()}


def _tag_set(tags: str) -> set[str]:
    return {t.strip().lower() for t in (tags or "").split("/") if t.strip()}


def _jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _similarity_reason(shared_genres: set[str]) -> str:
    if not shared_genres:
        return "similar themes, tone, and storytelling style"
    reasons = []
    for g in sorted(shared_genres):
        if g in _GENRE_REASON:
            reasons.append(_GENRE_REASON[g])
        if len(reasons) >= 2:
            break
    # Never emit an unmapped (potentially Chinese) genre token as copy.
    if not reasons:
        return "shared themes, tone, and storytelling style"
    return "Both feature " + " and ".join(reasons[:2])


@router.get("/{anime_id}/similar")
def similar_anime(anime_id: int, limit: int = 8, db: Session = Depends(get_db)):
    """基于 genre/tags 重叠 + score/year 接近计算相似动漫（Phase 1-B Similar SEO 页）。"""
    anime = db.get(Anime, anime_id)
    if not anime:
        raise HTTPException(status_code=404, detail="Anime not found")
    limit = min(max(limit, 1), 24)
    target_genres = _genre_set(anime.genre)
    target_tags = _tag_set(anime.tags)
    target_score = float(anime.score or 0.0)
    target_year = anime.year

    results = []
    for other in db.query(Anime).filter(Anime.id != anime_id).all():
        if (other.quality_score or 100) < 70:
            continue
        g = _genre_set(other.genre)
        t = _tag_set(other.tags)
        genre_j = _jaccard(target_genres, g)
        tag_j = _jaccard(target_tags, t)
        score_sim = max(0.0, 1.0 - abs(target_score - float(other.score or 0)) / 5.0)
        year_sim = 1.0
        if target_year and other.year:
            year_sim = max(0.0, 1.0 - abs(target_year - other.year) / 10.0)
        raw = genre_j * 45 + tag_j * 25 + score_sim * 18 + year_sim * 12
        if raw < 15:
            continue
        shared = target_genres & g
        score = round(min(raw + (other.anime_seo_priority or 0) * 0.05, 100), 1)
        results.append({
            "id": other.id,
            "title": other.title,
            "chinese_title": other.chinese_title,
            "slug": other.slug,
            "cover": other.cover,
            "genre": other.genre,
            "tags": other.tags,
            "year": other.year,
            "score": other.score,
            "anime_seo_priority": other.anime_seo_priority or 0,
            "similarity_score": round(raw, 1),
            "reason": _similarity_reason(shared),
        })
    results.sort(key=lambda x: (x["similarity_score"] + (x["anime_seo_priority"] or 0) * 0.1), reverse=True)
    return results[:limit]



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


@router.get("/statuses")
def list_statuses(db: Session = Depends(get_db)):
    rows = (
        db.execute(
            select(Anime.status, func.count(Anime.id))
            .where(Anime.status != "")
            .group_by(Anime.status)
            .order_by(func.count(Anime.id).desc())
        )
        .all()
    )
    return [{"status": s, "count": c} for s, c in rows]


@router.get("/letters")
def list_letters(db: Session = Depends(get_db)):
    rows = (
        db.execute(
            select(Anime.letter, func.count(Anime.id))
            .where(Anime.letter != "")
            .group_by(Anime.letter)
            .order_by(Anime.letter)
        )
        .all()
    )
    return [{"letter": l, "count": c} for l, c in rows]


@router.get("/{anime_id}", response_model=AnimeOut)
def get_anime(anime_id: int, db: Session = Depends(get_db)):
    anime = db.get(Anime, anime_id)
    if not anime:
        raise HTTPException(status_code=404, detail="Anime not found")
    return _serialize(db, anime)


@router.get("/by-slug/{slug}", response_model=AnimeOut)
def get_anime_by_slug(slug: str, db: Session = Depends(get_db)):
    """按 SEO slug 读取一部动漫（slug 为空则回退用 id 匹配）。"""
    slug = (slug or "").strip()
    if not slug:
        raise HTTPException(status_code=404, detail="Anime not found")
    anime = db.query(Anime).filter(func.lower(Anime.slug) == slug.lower()).first()
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
    """Bulk import / upsert anime (JSON array of AnimeCreate).

    - dedup by title (existing rows updated, new rows inserted)
    - normalizes tags (str/list -> "/"-joined)
    - auto-generates `letter` via pinyin / ascii first letter
    - fills sensible defaults
    """
    existing_titles = {t for (t,) in db.query(Anime.title).all()}
    added = 0
    updated = 0
    skipped = 0
    batch = 0
    for item in data.items:
        title = (item.title or "").strip()
        if not title:
            skipped += 1
            continue
        payload = item.model_dump()
        tags = payload.get("tags")
        if isinstance(tags, (list, tuple)):
            payload["tags"] = "/".join(str(t).strip() for t in tags if str(t).strip())
        elif isinstance(tags, str):
            payload["tags"] = "/".join(
                t.strip() for t in tags.replace(",", "/").replace("，", "/").split("/") if t.strip()
            )
        else:
            payload["tags"] = ""
        payload.setdefault("chinese_title", payload.get("title") or "")
        payload.setdefault("cover", "")
        payload.setdefault("description", "")
        payload.setdefault("genre", "")
        payload.setdefault("year", item.year if item.year is not None else None)
        payload.setdefault("score", 0.0)
        payload["letter"] = compute_letter(payload.get("chinese_title") or payload.get("title") or "").upper()
        if title in existing_titles:
            anime = db.query(Anime).filter(Anime.title == title).first()
            for k, v in payload.items():
                if k != "title":
                    setattr(anime, k, v)
            updated += 1
        else:
            db.add(Anime(**payload))
            existing_titles.add(title)
            added += 1
        batch += 1
        if batch % 500 == 0:
            db.commit()
    db.commit()
    return {"added": added, "updated": updated, "skipped": skipped, "total": db.query(Anime).count()}


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
