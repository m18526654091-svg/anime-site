"""AnimeHub 一键数据导入流水线（幂等、可重复执行）。

数据流程： 数据源 JSON ── normalize ── cover 解析 ── upsert ──> 数据库
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from app.database import SessionLocal, ensure_schema  # noqa: E402
from app.letter_util import compute_letter  # noqa: E402
from app.models import Anime  # noqa: E402

from scripts.covers import build_resolvers, resolve_cover  # noqa: E402
from scripts.normalize import is_placeholder_cover, normalize_item  # noqa: E402

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_DATA_FILE = os.path.join(ROOT_DIR, "anime_data.json")
MAPPING_FILE = os.path.join(ROOT_DIR, "data", "covers_mapping.json")


def load_mapping() -> dict[str, str]:
    if not os.path.exists(MAPPING_FILE):
        return {}
    try:
        with open(MAPPING_FILE, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return {k: v for k, v in data.items() if isinstance(k, str) and isinstance(v, str)}
    except Exception as exc:  # noqa: BLE001
        print(f"[warn] 读取映射文件失败: {exc}")
    return {}


def save_mapping(mapping: dict[str, str]) -> None:
    try:
        os.makedirs(os.path.dirname(MAPPING_FILE), exist_ok=True)
        with open(MAPPING_FILE, "w", encoding="utf-8") as f:
            json.dump(mapping, f, ensure_ascii=False, indent=2)
    except Exception as exc:  # noqa: BLE001
        print(f"[warn] 写回映射文件失败: {exc}")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="AnimeHub 一键导入流水线")
    p.add_argument("--source", default=DEFAULT_DATA_FILE, help="数据源 JSON 路径")
    p.add_argument("--no-covers", action="store_true", help="跳过联网封面解析")
    p.add_argument("--force-covers", action="store_true", help="强制重刷所有封面（含真实图）")
    p.add_argument("--no-save-mapping", action="store_true", help="解析成功后不回写 data/covers_mapping.json")
    p.add_argument("--dry-run", action="store_true", help="不写库、不写 mapping，仅统计")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    if not os.path.exists(args.source):
        print(f"[error] 数据源不存在: {args.source}")
        sys.exit(1)
    with open(args.source, encoding="utf-8") as f:
        raw_items = json.load(f)
    if isinstance(raw_items, dict):
        raw_items = raw_items.get("items", [])
    if not isinstance(raw_items, list):
        print("[error] 数据源顶层应为数组（或 {items: [...]}）")
        sys.exit(1)

    ensure_schema()
    mapping = load_mapping()
    providers = build_resolvers(enable_network=not args.no_covers, mapping=mapping)
    print(f"[cover] 启用源: {providers}")
    print(f"[import] 数据源: {args.source}  共 {len(raw_items)} 条  {'DRY-RUN' if args.dry_run else ''}")
    if mapping:
        print(f"[cover] 本地映射命中: {len(mapping)} 条")

    db = SessionLocal()
    start = time.time()
    try:
        existing = {a.title: a for a in db.query(Anime).all()}
        # 幂等去重：一次性拉取已有 slug（小写）；新增插入时与其互斥，避免重复 URL。
        existing_slugs = {(a.slug or "").lower() for a in existing.values()}

        def _reserve_slug(base: str) -> str:
            """生成唯一 slug：base -> base-2 -> base-3 ...（与 DB + 本批已增均互斥）。"""
            if not base:
                return ""
            low = base.lower()
            if low not in existing_slugs:
                existing_slugs.add(low)
                return base
            n = 2
            while f"{low}-{n}" in existing_slugs:
                n += 1
            final = f"{base}-{n}"
            existing_slugs.add(f"{low}-{n}")
            return final
        added = updated = skipped = 0
        cover_filled = 0
        errors: list[str] = []
        for idx, it in enumerate(raw_items, start=1):
            title = (it.get("title") or "").strip() or (it.get("chinese_title") or "").strip()
            if not title:
                skipped += 1
                continue

            norm = normalize_item(it)

            orig_cover = (it.get("cover") or "").strip()
            cover = resolve_cover(norm, providers, force=args.force_covers)

            if cover:
                norm["cover"] = cover
                cover_filled += 1
                if not args.no_save_mapping and not args.dry_run and title not in mapping:
                    mapping[title] = cover
            elif is_placeholder_cover(orig_cover):
                # 解析不到真实封面 & 原本是占位图 → 清空，前端显示站内渐变占位
                norm["cover"] = ""

            eps = norm.get("episodes")
            try:
                score = float(norm.get("score") or 0.0)
            except (TypeError, ValueError):
                score = 0.0
            fields = dict(
                chinese_title=(norm.get("chinese_title") or "").strip() or title,
                slug=norm["slug"],
                cover=norm.get("cover") or "",
                description=(norm.get("description") or "").strip(),
                genre=(norm.get("genre") or "").strip(),
                tags=norm.get("tags") or "",
                year=norm.get("year"),
                month=norm.get("month"),
                region=(norm.get("region") or "").strip(),
                author=(norm.get("author") or "").strip(),
                studio=(norm.get("studio") or "").strip(),
                status=(norm.get("status") or "").strip(),
                episodes=eps,
                score=score,
                seo_title=norm.get("seo_title") or "",
                seo_description=norm.get("seo_description") or "",
                play_data=norm.get("play_data") or "",
                letter=compute_letter((norm.get("chinese_title") or title or "")).upper(),
            )

            if args.dry_run:
                added += 1
                continue

            rec = existing.get(title)
            if rec is not None:
                # 已存在标题 → 禁止修改 slug，保障已有 /anime/{slug} URL 不变
                for k in fields:
                    if k == "slug":
                        continue
                    setattr(rec, k, fields[k])
                updated += 1
            else:
                # 新增插入 → 冲突时自动生成 slug / slug-2 / slug-3 …
                fields["slug"] = _reserve_slug(fields.get("slug") or "")
                existing[title] = Anime(title=title, **fields)
                db.add(existing[title])
                added += 1

        if not args.dry_run:
            db.commit()
            if not args.no_save_mapping:
                save_mapping(mapping)
            total = db.query(Anime).count()
        else:
            total = len(existing)
        print(
            f"[done] added={added} updated={updated} skipped={skipped} "
            f"cover_resolved={cover_filled}/{len(raw_items)} total_in_db={total} "
            f"mapping_total={len(mapping)} "
            f"time={time.time()-start:.2f}s"
        )
        if errors:
            print("validation errors:", errors[:20])
    finally:
        db.close()


if __name__ == "__main__":
    main()
