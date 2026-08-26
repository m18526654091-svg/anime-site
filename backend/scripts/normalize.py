"""AnimeHub 数据标准化工具。

职责：
- 生成稳定、URL 安全的 SEO slug
- 补齐 chinese_title / seo_title / seo_description / letter
- 规范化 tags / 拼音字母
- 判定封面是否为占位图

与前端 `frontend/lib/slug.ts` 规则保持一致，保证 URL 匹配稳定。
"""
from __future__ import annotations

import re
from typing import Any

# 占位图特征（这些 URL 不是真实海报，导入时应被真实封面覆盖）
PLACEHOLDER_MARKERS = (
    "placehold.co",
    "placeholdit",
    "dummyimage",
    "via.placeholder",
    "placeholder.com",
)


def is_placeholder_cover(cover: str) -> bool:
    c = (cover or "").strip().lower()
    if not c:
        return False
    return any(m in c for m in PLACEHOLDER_MARKERS)


def make_slug(value: str, fallback: str = "") -> str:
    """生成 URL 安全的 slug。

    - 优先提取 ASCII（英文/罗马拼音）转小写并用 '-' 连接；
    - 无 ASCII 时降级为 Unicode（中文）紧凑 slug；
    - 实在为空时用 fallback。
    """
    s = (value or "").strip()
    if not s:
        return fallback

    # 中英文之间、以及常见分隔符统一转空格
    ascii_: str = re.sub(r"[：:，,、·・．。!！?？（）()（）/\\]", " ", s)
    ascii_ = ascii_.lower()
    ascii_ = re.sub(r"[^a-z0-9]+", "-", ascii_)
    ascii_ = re.sub(r"^-+|-+$", "", ascii_)
    ascii_ = re.sub(r"-{2,}", "-", ascii_)
    # 仅当 ASCII 部分有实际意义（≥3 字符）才使用，否则回退到 Unicode 全文，
    # 以免 "钢之炼金术师FA" 之类被压成 "fa"。
    if len(ascii_) >= 3:
        return ascii_

    unicode_: str = re.sub(r"\s+", "-", s)
    unicode_ = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fa5-]", "", unicode_)
    unicode_ = re.sub(r"-{2,}", "-", unicode_)
    unicode_ = re.sub(r"^-+|-+$", "", unicode_)
    if unicode_:
        return unicode_

    return fallback


def normalize_tags(tags: Any) -> str:
    """把 tags 归一为 '/' 分隔字符串（兼容 str / list / 逗号分隔）。"""
    if tags is None:
        return ""
    if isinstance(tags, (list, tuple)):
        return "/".join(str(t).strip() for t in tags if str(t).strip())
    text = str(tags)
    return "/".join(
        t.strip()
        for t in re.split(r"[/，,、]", text)
        if t.strip()
    )


# Meta description 推荐长度上限（Google 约 150~160 字符会截断）。
SEOMETA_MAX = 150


def _build_seo_title(chinese_title: str, data: dict[str, Any]) -> str:
    """自动组合自然的 SEO 标题：中文名 + 年份/类型 + 制作公司/地区 + 品牌。

    规则（避免固定模板造成标题全部雷同，也避免过度关键词堆砌）：
    - 主标题 = 中文名；
    - 有年份与类型时补「YYYY年XX动漫」，仅有一项时补其中一项；
    - 有制作公司时补「XX制作」，无制作公司但有地区时补「XX动画」；
    - 结尾统一加品牌「AnimeHub」，并保留「在线观看」动词语义。
    """
    year = data.get("year")
    genre = (data.get("genre") or "").strip()
    region = (data.get("region") or "").strip()
    studio = (data.get("studio") or "").strip()

    parts: list[str] = [chinese_title]
    primary = genre.split("/")[0].strip() if genre else ""
    if year and primary:
        parts.append(f"{year}年{primary}动漫")
    elif year:
        parts.append(f"{year}年动漫")
    elif primary:
        parts.append(f"{primary}动漫")
    if studio:
        parts.append(f"{studio}制作")
    elif region:
        parts.append(f"{region}动画")
    parts.append("在线观看")
    parts.append("AnimeHub")
    return " ".join(parts)


def _build_seo_description(chinese_title: str, data: dict[str, Any]) -> str:
    """自动组合 meta description：名称 + 类型 + 年份 + 地区 + 简介。

    控制在 SEOMETA_MAX 字符内，适合 Google 搜索结果摘要展示。
    """
    parts: list[str] = [f"{chinese_title}：在线观看"]
    genre = (data.get("genre") or "").strip()
    year = data.get("year")
    region = (data.get("region") or "").strip()
    desc = (data.get("description") or "").strip()

    if genre:
        parts.append(f"类型{genre}")
    if year:
        parts.append(f"{year}年")
    if region:
        parts.append(f"{region}地区")
    if desc:
        # 预留足够空间给简介，使总长度不超过上限
        joined = "，".join(parts)
        budget = max(20, SEOMETA_MAX - len(joined) - 3)
        parts.append(desc if len(desc) <= budget else desc[: budget - 1] + "…")

    text = "，".join(parts)
    # 防御性截断（多字段超长时）
    if len(text) > SEOMETA_MAX:
        text = text[: SEOMETA_MAX - 1] + "…"
    return text


def build_auto_tags(data: dict[str, Any]) -> str:
    """当 tags 为空时，从已有字段生成基础标签（genre + region + year）。

    注意：只用于补全，绝不覆盖用户提供的 tags。
    """
    parts: list[str] = []
    genre = (data.get("genre") or "").strip()
    region = (data.get("region") or "").strip()
    year = data.get("year")

    if genre:
        parts.extend(g.strip() for g in re.split(r"[/，,、\s]+", genre) if g.strip())
    if region and region not in parts:
        parts.append(region)
    if year:
        year_tag = f"{year}年"
        if year_tag not in parts:
            parts.append(year_tag)
    return "/".join(parts)


def normalize_item(item: dict[str, Any]) -> dict[str, Any]:
    """补齐并规范化单条动漫数据，返回新的 dict。"""
    d = dict(item)
    title = (d.get("title") or "").strip()
    chinese_title = (d.get("chinese_title") or "").strip() or title

    # slug：优先数据自带，否则由 title（或其英文部分）生成
    slug = (d.get("slug") or "").strip()
    if not slug:
        english_candidate = title
        slug = make_slug(english_candidate)

    # 避免重复 slug：若生成结果=fallback 空，用 chinese 兜底
    if not slug:
        slug = make_slug(chinese_title)

    # SEO 标题 / 描述兜底（未提供时用规则生成，避免标题雷同）
    seo_title = (d.get("seo_title") or "").strip()
    if not seo_title:
        seo_title = _build_seo_title(chinese_title, d)

    seo_description = (d.get("seo_description") or "").strip()
    if not seo_description:
        # 自动组合：名称 + 类型 + 年份 + 地区 + 简介，控制长度 <= SEOMETA_MAX
        seo_description = _build_seo_description(chinese_title, d)

    d.setdefault("chinese_title", chinese_title)
    d["slug"] = slug
    d["seo_title"] = seo_title
    d["seo_description"] = seo_description
    # 已有 tags 保留；为空时用 genre/region/year 自动补全，绝不覆盖已有值
    d["tags"] = normalize_tags(d.get("tags")) or build_auto_tags(d)
    d["year"] = d.get("year")
    d["month"] = d.get("month")
    d["score"] = float(d.get("score") or 0.0)
    d["episodes"] = d.get("episodes")
    d["play_data"] = d.get("play_data") or ""
    return d