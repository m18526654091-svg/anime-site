from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import Anime, Comment, User
from ..schemas import CommentCreate, CommentOut

router = APIRouter(prefix="/api", tags=["comments"])


@router.get("/anime/{anime_id}/comments", response_model=list[CommentOut])
def list_comments(anime_id: int, db: Session = Depends(get_db)):
    rows = (
        db.query(Comment)
        .filter(Comment.anime_id == anime_id)
        .order_by(Comment.id.desc())
        .all()
    )
    result = []
    for c in rows:
        u = db.get(User, c.user_id)
        result.append(
            CommentOut(
                id=c.id,
                anime_id=c.anime_id,
                user_id=c.user_id,
                username=u.username if u else "",
                content=c.content,
            )
        )
    return result


@router.post("/anime/{anime_id}/comments", response_model=CommentOut)
def create_comment(
    anime_id: int,
    data: CommentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not db.get(Anime, anime_id):
        raise HTTPException(status_code=404, detail="动漫不存在")
    if not data.content.strip():
        raise HTTPException(status_code=400, detail="评论内容不能为空")

    comment = Comment(user_id=user.id, anime_id=anime_id, content=data.content.strip())
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return CommentOut(
        id=comment.id,
        anime_id=comment.anime_id,
        user_id=comment.user_id,
        username=user.username,
        content=comment.content,
    )


@router.delete("/comments/{comment_id}")
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    comment = db.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")
    if comment.user_id != user.id and not user.is_admin:
        raise HTTPException(status_code=403, detail="没有权限删除该评论")
    db.delete(comment)
    db.commit()
    return {"ok": True}
