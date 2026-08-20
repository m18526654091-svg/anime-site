"""为缺失 SEO 字段（seo_title / seo_description）的动漫自动补全。

纯本地规则生成，不调用外部 AI API，可重复执行（幂等）。

用法（在 backend 目录下执行）：
    .venv\\Scripts\\python -m scripts.generate_seo
    # 可选：--force 强制按新模板重写全部记录（默认只补全空值）
    .venv\\Scripts\\python -m scripts.generate_seo --force

生成规则：
    seo_title       = "{中文名或原名}在线观看 - 高清动漫介绍 | AnimeHub"
    seo_description = 由 title / genre / description 组合，长度 120-160 字符
"""
import argparse
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from app.database import SessionLocal, ensure_schema  # noqa: E402
from app.models import Anime  # noqa: E402

BRAND = "AnimeHub"
MIN_LEN = 120
MAX_LEN = 160


def _clean(text: str) -> str:
    """合并多余空白（含换行），返回单行文本。"""
    return " ".join((text or "").split()).strip()


def build_seo_title(anime) -> str:
    title = (anime.chinese_title or anime.title or "").strip()
    return f"{title}在线观看 - 高清动漫介绍 | {BRAND}"


def build_seo_description(anime) -> str:
    title = (anime.chinese_title or anime.title or "").strip()
    genre = (anime.genre or "").strip()
    desc = _clean(anime.description)

    # 主体：简介前 110 字符（去掉多余空白，保留句意）
    body = desc[:110].rstrip()

    # 尾部：类型 + 品牌关键词，保证包含目标关键词
    tail = f"类型：{genre}。" if genre else "高清动漫。"
    tail += f"{title}在线观看，高清画质，收录全集与最新更新，尽在{BRAND}。"
    text = body
    if body and not body[-1] in "。！？!?.":
        text += "。"
    text += tail

    if len(text) > MAX_LEN:
        text = text[: MAX_LEN - 1].rstrip() + "。"
    elif len(text) < MIN_LEN:
        # 循环补充相关句子，直到达到 120 字符下限
        fills = [
            f"{title}是一部值得收藏的{genre or '动漫'}作品，剧情精彩。",
            "高清画质，更新及时，支持手机端在线免费观看。",
            f"更多关于{title}的剧情、角色与全集信息，尽在{BRAND}动漫资源站。",
        ]
        for fill in fills:
            if len(text) >= MIN_LEN:
                break
            text += fill
        if len(text) > MAX_LEN:
            text = text[: MAX_LEN - 1].rstrip() + "。"
        elif text and not text.endswith("。"):
            text += "。"
    return text


def main() -> None:
    parser = argparse.ArgumentParser(description="补全动漫 SEO 字段（seo_title / seo_description）")
    parser.add_argument("--force", action="store_true", help="强制按新模板重写所有记录（默认只补全空值）")
    args = parser.parse_args()

    ensure_schema()
    db = SessionLocal()
    start = time.time()
    try:
        animes = db.query(Anime).all()
        updated = 0
        length_stats: list[int] = []
        for a in animes:
            need_title = args.force or not (a.seo_title or "").strip()
            need_desc = args.force or not (a.seo_description or "").strip()
            if not (need_title or need_desc):
                continue
            if need_title:
                a.seo_title = build_seo_title(a)
            if need_desc:
                a.seo_description = build_seo_description(a)
                length_stats.append(len(a.seo_description))
            updated += 1
        db.commit()
        total = db.query(Anime).count()
        elapsed = time.time() - start
        print(f"Updated {updated} anime (total {total})  Time: {elapsed:.3f}s")
        if length_stats:
            print(f"seo_description length: min={min(length_stats)} max={max(length_stats)}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
