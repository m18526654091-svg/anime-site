"""Stage 12-E: 字段级 source provenance helper。

为后续明确的数据导入/更新操作记录「字段值来自哪个数据源」。
本阶段只实现基础能力 + 最小测试入口；不接入现有生产导入流程，
不回填历史 provenance、不猜测现有字段来源。

语义：
- source_value：来自该 source 的字段值（文本规范化 / 图片仅 URL，绝不保存二进制）
- verified：该值是否已经人工验证（默认 False；source 存在 ≠ verified=1）
- fetched_at：抓取/记录时间
- value_hash：source_key|field_name|source_value 的 SHA256（值变化 → hash 变化）

幂等：同 (anime_id, field_name, source_id) 不产生重复记录（upsert）。
"""
from __future__ import annotations

import hashlib
import re
from datetime import UTC, datetime

from app.models import AnimeFieldSource, DataSource  # noqa: E402

# 图片类字段：只保存 URL / source reference，不保存二进制
_IMAGE_FIELDS = {"cover", "banner", "poster", "image", "image_url", "logo"}


def _normalize_source_value(source_value, field_name: str) -> str:
    """规范化 source_value。

    - 仅接受 str；bytes/二进制拒绝
    - 图片字段（或值本身为 http URL）：压缩空白后原样保存 URL
    - 文本字段：strip + 合并空白
    """
    if isinstance(source_value, (bytes, bytearray)):
        raise ValueError("source_value 不接受二进制（图片只保存 URL / reference）")
    if source_value is None:
        return ""
    s = str(source_value).strip()
    if not s:
        return ""
    # URL 或图片字段：压缩空白，保留 URL 原样
    if field_name in _IMAGE_FIELDS or s.startswith(("http://", "https://")):
        return re.sub(r"\s+", "", s)
    # 文本字段：合并空白
    return re.sub(r"\s+", " ", s)


def _value_hash(source_key: str, field_name: str, normalized_value: str) -> str:
    key = f"{source_key}|{field_name}|{normalized_value}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


def record_field_source(
    db,
    anime_id: int,
    field_name: str,
    source_key: str,
    source_value,
    verified: bool = False,
    fetched_at: datetime | None = None,
) -> str:
    """记录字段级来源（幂等 upsert）。返回 value_hash。

    - source_key 不存在 → ValueError（明确报错）
    - 同 (anime_id, field_name, source_id) 只保留一条记录
    - verified 默认 False（source 存在 ≠ 人工验证）
    """
    field_name = (field_name or "").strip()
    if not field_name:
        raise ValueError("field_name 不能为空")

    src = db.query(DataSource).filter_by(source_key=source_key).first()
    if src is None:
        raise ValueError(
            f"data_sources 无 source_key={source_key!r}（请先执行 ensure_schema seed）"
        )

    norm = _normalize_source_value(source_value, field_name)
    h = _value_hash(source_key, field_name, norm)
    fetched = fetched_at or datetime.now(UTC)

    rec = (
        db.query(AnimeFieldSource)
        .filter_by(anime_id=anime_id, field_name=field_name, source_id=src.id)
        .first()
    )
    if rec is not None:
        # 幂等 upsert：值/验证状态更新，不产生重复记录
        rec.source_value = norm
        rec.value_hash = h
        rec.verified = int(bool(verified))
        rec.fetched_at = fetched
    else:
        db.add(
            AnimeFieldSource(
                anime_id=anime_id,
                field_name=field_name,
                source_id=src.id,
                source_value=norm,
                value_hash=h,
                verified=int(bool(verified)),
                fetched_at=fetched,
            )
        )
    return h
