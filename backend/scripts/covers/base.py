"""封面提供方抽象基类。"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional


class CoverProvider(ABC):
    """一个封面数据源：按标题解析真实海报 URL。"""

    #: 优先级（数字越小越先尝试）
    priority = 100

    @abstractmethod
    def resolve(
        self,
        title: str,
        chinese_title: str = "",
        year: Optional[int] = None,
    ) -> Optional[str]:
        """返回真实海报 URL，找不到返回 None。"""

    def __repr__(self) -> str:  # pragma: no cover - 仅日志
        return f"<{self.__class__.__name__} priority={self.priority}>"