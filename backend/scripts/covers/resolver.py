"""封面解析编排器（可插拔，按优先级依序尝试）。"""
from __future__ import annotations

import json
import logging
import os
from typing import Any, List, Optional

logger = logging.getLogger("animehub.covers")

from ..normalize import is_placeholder_cover
from .base import CoverProvider
from .local_mapping import LocalMappingProvider
from .myanimelist import MyAnimeListStaticProvider

# 本地维护封面映射文件（人工可持续维护）
MAPPING_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
    "data",
    "covers_mapping.json",
)


def load_local_mapping() -> dict:
    if not os.path.exists(MAPPING_FILE):
        return {}
    try:
        with open(MAPPING_FILE, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return {str(k): str(v) for k, v in data.items() if str(k).strip() and str(v).strip()}
    except Exception as exc:  # noqa: BLE001
        logger.warning("[cover] 读取本地映射失败: %s", exc)
    return {}


def build_resolvers(enable_network: bool = True, mapping: Optional[dict] = None) -> List[CoverProvider]:
    """构建可插拔的封面提供方列表（按 priority 升序）。

    优先级：本地 mapping（最稳） → MyAnimeList 静态 → Wikipedia（公开） → AniList（联网后备）。
    """
    from .wikipedia import WikipediaZhProvider

    providers: List[CoverProvider] = [LocalMappingProvider(mapping or {})]
    providers.append(MyAnimeListStaticProvider())
    if enable_network:
        providers.append(WikipediaZhProvider())
        try:
            from .anilist import AniListProvider

            providers.append(AniListProvider())
        except Exception:  # noqa: BLE001 - AniList 非主要源，失败不阻断
            pass
    return sorted(providers, key=lambda p: p.priority)


def resolve_cover(
    item: dict[str, Any],
    providers: List[CoverProvider],
    *,
    force: bool = False,
) -> Optional[str]:
    """为单个条目决定封面 URL。

    - 已有真实封面（非占位图）且不强刷 -> 保留原值；
    - 空封面或占位图 -> 依序尝试 providers；
    - 全部失败且原本是占位图 -> 返回 None（前端渐变占位，不写 placeholder）。
    """
    current = (item.get("cover") or "").strip()
    is_ph = is_placeholder_cover(current)

    if current and not is_ph and not force:
        return current

    for provider in providers:
        try:
            url = provider.resolve(
                (item.get("title") or ""),
                (item.get("chinese_title") or ""),
                item.get("year"),
            )
        except Exception as exc:  # noqa: BLE001 - 任何源异常都不阻断导入
            logger.warning("[cover] %s 解析失败: %s", provider, exc)
            continue
        if url and url.strip():
            return url.strip()

    # 拿不到真实封面：占位图置空由前端展示渐变，真实图保留
    return None if is_ph else (current or None)
