"""本地封面映射提供方（最高优先级、人工可持续维护）。

读取 data/covers_mapping.json（键=动漫标题，值=已验证封面 URL）。
当标题在映射中命中原样返回，保证稳定、可访问、可审计。
"""
from __future__ import annotations

from typing import Dict, Optional

from .base import CoverProvider


class LocalMappingProvider(CoverProvider):
    priority = 1

    def __init__(self, mapping: Optional[Dict[str, str]] = None) -> None:
        self.mapping: Dict[str, str] = {k: v for k, v in (mapping or {}).items()}

    def resolve(self, title, chinese_title="", year=None):
        for key in (title, chinese_title):
            key = (key or "").strip()
            if key and key in self.mapping:
                url = (self.mapping.get(key) or "").strip()
                if url:
                    return url
        return None