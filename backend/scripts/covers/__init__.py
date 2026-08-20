"""AnimeHub 封面适配器（可插拔封面源）。

原则：
- 不把系统绑定到单一图片来源。
- 每个数据源实现 CoverProvider，由 resolver 依序尝试。
- 导入时优先真实海报；占位图或空封面才触发替换；均失败则留空，
  由前端使用站内 CSS 渐变占位（绝不写 placeholder 图片）。
"""
from __future__ import annotations

from .base import CoverProvider
from .resolver import build_resolvers, resolve_cover

__all__ = ["CoverProvider", "build_resolvers", "resolve_cover"]