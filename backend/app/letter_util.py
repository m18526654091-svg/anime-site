"""Compute the index 'letter' for an anime title.

- Chinese titles -> pinyin first letter (A-Z)
- English / Romaji / ASCII titles -> first ASCII letter
- Everything else -> ""  (rendered under the '#' bucket)
Used by the bulk import tool, the /bulk endpoint and (optionally) filtering.
"""
from typing import Optional

from pypinyin import FIRST_LETTER, lazy_pinyin

_LETTERS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")


def compute_letter(title: Optional[str]) -> str:
    if not title:
        return ""
    t = title.strip()
    if not t:
        return ""
    first = t[0]
    # Latin / ASCII letter (covers English, Romaji, numbers)
    if first.isascii() and first.isalpha():
        return first.upper()
    # CJK character -> pinyin first letter
    try:
        pin = lazy_pinyin(t[0], style=FIRST_LETTER)
        if pin and pin[0]:
            c = pin[0][0].upper()
            if c in _LETTERS:
                return c
    except Exception:
        pass
    return ""
