"""AniList Anime 扩量导入脚本（幂等，支持 dry-run / 分批 / 指定数据源）。

数据流: data/anilist_anime_candidates.json ── 字段映射 ── 质量筛选 ── 去重 ── upsert

特性:
  - 幂等: anilist_id / title / slug 判重，重复运行不重复新增
  - --dry-run: 只统计，不写库
  - --limit / --start: 分批导入（第一批先验证，可断点续批）
  - month: AniList startDate.month（真实首播月，不猜测）

用法:
  python scripts/import_anime_anilist.py --dry-run
  python scripts/import_anime_anilist.py --dry-run --limit 120
  python scripts/import_anime_anilist.py --limit 120
"""
from __future__ import annotations
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from app.database import Base, engine, SessionLocal  # noqa: E402
from app.letter_util import compute_letter  # noqa: E402
from app.models import Anime  # noqa: E402
from scripts.normalize import normalize_item  # noqa: E402

DEFAULT_SOURCE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..',
                              'data', 'anilist_anime_candidates.json')

# AniList genre → 中文
GENRE_CN = {
    'Action': '动作', 'Adventure': '冒险', 'Comedy': '喜剧', 'Drama': '剧情',
    'Fantasy': '奇幻', 'Horror': '恐怖', 'Mystery': '悬疑', 'Romance': '恋爱',
    'Sci-Fi': '科幻', 'Slice of Life': '日常', 'Sports': '运动',
    'Supernatural': '超自然', 'Thriller': '惊悚', 'Music': '音乐',
    'Mahou Shoujo': '魔法少女', 'Mecha': '机战', 'Psychological': '心理',
    'School': '校园', 'Seinen': '青年', 'Shoujo': '少女', 'Shounen': '少年',
    'Josei': '女性', 'Military': '军事', 'Space': '太空', 'Kids': '儿童',
    'Historical': '历史', 'Parody': '恶搞', 'Police': '警察',
    'Super Power': '超能力', 'Vampire': '吸血鬼', 'Martial Arts': '格斗',
    'Game': '游戏', 'Ecchi': '福利', 'Yuri': '百合',
}
STATUS_CN = {
    'FINISHED': '完结', 'RELEASING': '连载中', 'NOT_YET_RELEASED': '未上映',
    'CANCELLED': '已取消', 'HIATUS': '暂停',
}
VALID_FORMATS = {'TV', 'MOVIE', 'ONA', 'OVA', 'SPECIAL'}
# 质量门槛：搜索价值优先（热门/高分/经典/新番）
MIN_SCORE = 45        # 平均分 <45（10 分制）的冷门作排除
MIN_POPULARITY = 800  # 无评分且人气过低的作品排除


def _strip_html(s):
    if not s:
        return ''
    s = re.sub(r'<br\s*/?>', '\n', s, flags=re.I)
    s = re.sub(r'<[^>]+>', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s[:1200]


def _has_hanzi(s):
    return bool(re.search(r'[\u4e00-\u9fff]', s or ''))


def anilist_to_item(m: dict) -> dict:
    t = m.get('title') or {}
    romaji = (t.get('romaji') or '').strip()
    english = (t.get('english') or '').strip()
    native = (t.get('native') or '').strip()
    title = english or romaji or native
    # chinese_title：AniList 无中文；用日文原名（真实，非编造），无汉字时用英文
    chinese_title = native if _has_hanzi(native) else title
    sd = m.get('startDate') or {}
    genres = '/'.join(GENRE_CN.get(g, g) for g in (m.get('genres') or []))
    tags = '/'.join(x.get('name', '') for x in (m.get('tags') or []) if x.get('name'))[:300]
    studios = (m.get('studios') or {}).get('nodes') or []
    studio = studios[0].get('name') if studios else ''
    score = m.get('averageScore')
    item = {
        'title': title,
        'chinese_title': chinese_title,
        'description': _strip_html(m.get('description')),
        'genre': genres,
        'tags': tags,
        'year': sd.get('year'),
        'month': sd.get('month'),
        'region': '日本',
        'studio': studio,
        'status': STATUS_CN.get(m.get('status'), ''),
        'episodes': m.get('episodes'),
        'score': round(score / 10.0, 1) if score else 0.0,
        'cover': (m.get('coverImage') or {}).get('extraLarge') or '',
        'anilist_id': str(m['id']),
        'mal_id': str(m['idMal']) if m.get('idMal') else '',
        'format': m.get('format'),
        'popularity': m.get('popularity') or 0,
    }
    return item


def _quality_gate(item: dict) -> str:
    """返回 None=通过，否则返回原因。"""
    if not item.get('title'):
        return 'no_title'
    if item.get('format') not in VALID_FORMATS:
        return 'format:%s' % item.get('format')
    if len(item.get('description') or '') < 20:
        return 'no_description'
    if item.get('score'):
        if item['score'] * 10 < MIN_SCORE:
            return 'low_score'
    elif item.get('popularity', 0) < MIN_POPULARITY:
        return 'low_popularity'
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', default=DEFAULT_SOURCE, help='候选数据文件路径')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--limit', type=int, default=0, help='本批最多导入条数（分批用，0=全部）')
    ap.add_argument('--start', type=int, default=0, help='从候选第几条开始（断点续批）')
    args = ap.parse_args()

    Base.metadata.create_all(engine)
    raw = json.load(open(args.source, encoding='utf-8'))
    cands = raw.get('items') if isinstance(raw, dict) else raw
    if not isinstance(cands, list):
        print('[error] 候选文件格式错误')
        sys.exit(1)

    db = SessionLocal()
    stats = {'source_total': len(cands), 'new': 0, 'updated': 0, 'skipped': 0,
             'duplicate': 0, 'invalid': 0, 'cover_resolved': 0}
    try:
        # 现有数据索引（幂等去重）
        existing_by_id = {}
        existing_by_title = {}
        existing_by_slug = {}
        for a in db.query(Anime).all():
            if getattr(a, 'anilist_id', None):
                existing_by_id[str(a.anilist_id)] = a
            if a.title:
                existing_by_title[a.title.lower()] = a
            if a.chinese_title:
                existing_by_title.setdefault(a.chinese_title.lower(), a)
            if a.slug:
                existing_by_slug[a.slug.lower()] = a

        end = len(cands) if not args.limit else min(args.start + args.limit, len(cands))
        batch = cands[args.start:end]
        print('[import] 候选=%d | 本批=%d (%d..%d) | 库内已有=%d | %s'
              % (len(cands), len(batch), args.start, end, len(existing_by_id),
                 'DRY-RUN' if args.dry_run else ''))

        for i, m in enumerate(batch, start=args.start + 1):
            item = anilist_to_item(m)
            reason = _quality_gate(item)
            if reason:
                stats['invalid'] += 1
                if i <= 10:
                    print('  [invalid] %s (%s)' % (item['title'][:30], reason))
                continue
            # 去重：anilist_id / title / slug
            if item['anilist_id'] in existing_by_id:
                stats['duplicate'] += 1
                continue
            t = item['title'].lower()
            if t in existing_by_title:
                stats['duplicate'] += 1
                continue
            norm = normalize_item(item)
            slug = norm['slug'].lower()
            if slug in existing_by_slug:
                # slug 冲突：不同 title 但 slug 相同 → 唯一化（-2），不覆盖已有 URL
                base = norm['slug']
                n = 2
                while ('%s-%d' % (base, n)).lower() in existing_by_slug:
                    n += 1
                norm['slug'] = '%s-%d' % (base, n)
            fields = dict(
                title=item['title'],
                chinese_title=(norm.get('chinese_title') or '').strip() or item['title'],
                slug=norm['slug'],
                cover=item['cover'],
                description=norm.get('description') or '',
                genre=norm.get('genre') or '',
                tags=norm.get('tags') or '',
                year=item.get('year'),
                month=item.get('month'),
                region=item.get('region') or '',
                author='',
                studio=item.get('studio') or '',
                status=item.get('status') or '',
                episodes=item.get('episodes'),
                score=float(item.get('score') or 0.0),
                seo_title=norm.get('seo_title') or '',
                seo_description=norm.get('seo_description') or '',
                anilist_id=int(item['anilist_id']) if str(item['anilist_id']).isdigit() else None,
                mal_id=int(item['mal_id']) if str(item.get('mal_id') or '').isdigit() else None,
                letter=compute_letter((norm.get('chinese_title') or item['title'])).upper(),
            )
            if item.get('cover'):
                stats['cover_resolved'] += 1
            if args.dry_run:
                stats['new'] += 1
                continue
            rec = Anime(**fields)
            db.add(rec)
            existing_by_id[item['anilist_id']] = rec
            existing_by_title[item['title'].lower()] = rec
            existing_by_slug[rec.slug.lower()] = rec
            stats['new'] += 1
        if not args.dry_run:
            db.commit()
        print('--- 结果 ---')
        print('source_total=%d | new=%d | updated=%d | skipped=%d | duplicate=%d | invalid=%d | cover_resolved=%d'
              % (stats['source_total'], stats['new'], stats['updated'], stats['skipped'],
                 stats['duplicate'], stats['invalid'], stats['cover_resolved']))
    finally:
        db.close()


if __name__ == '__main__':
    main()
