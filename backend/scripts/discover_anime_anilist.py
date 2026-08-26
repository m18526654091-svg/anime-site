"""AniList Anime 候选发现：按高价值维度拉取候选，输出 data/anilist_anime_candidates.json。

高价值维度:
  - 高人气 / 高评分 / 高热度 / 高收藏
  - 2025-2026 热门季番
字段: id idMal title{romaji english native} startDate{year month day} description
      genres tags studios status episodes coverImage averageScore popularity format countryOfOrigin

用法:
  python scripts/discover_anime_anilist.py
"""
from __future__ import annotations
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import import_characters_anilist as imp  # 复用 gql（429/retry/delay）

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data',
                   'anilist_anime_candidates.json')

MEDIA_FIELDS = '''
  id idMal title { romaji english native }
  startDate { year month day }
  description
  genres
  tags { name }
  studios { nodes { name } }
  status episodes coverImage { extraLarge }
  averageScore popularity format countryOfOrigin
'''

# 拉取计划：(query_name, page_count, query_args)
PLAN = [
    ('popularity', 2, 'sort: [POPULARITY_DESC]'),
    ('score', 2, 'sort: [SCORE_DESC]'),
    ('trending', 2, 'sort: [TRENDING_DESC]'),
    ('favourites', 2, 'sort: [FAVOURITES_DESC]'),
    ('season_2025_winter', 1, 'season: WINTER, seasonYear: 2025, sort: [POPULARITY_DESC]'),
    ('season_2025_spring', 1, 'season: SPRING, seasonYear: 2025, sort: [POPULARITY_DESC]'),
    ('season_2025_summer', 1, 'season: SUMMER, seasonYear: 2025, sort: [POPULARITY_DESC]'),
    ('season_2025_fall', 1, 'season: FALL, seasonYear: 2025, sort: [POPULARITY_DESC]'),
    ('season_2026_winter', 1, 'season: WINTER, seasonYear: 2026, sort: [POPULARITY_DESC]'),
    ('season_2026_spring', 1, 'season: SPRING, seasonYear: 2026, sort: [POPULARITY_DESC]'),
    ('season_2026_summer', 1, 'season: SUMMER, seasonYear: 2026, sort: [POPULARITY_DESC]'),
]


def fetch_page(args: str, page: int):
    q = ('query { Page(page: %d, perPage: 50) { media(%s, type: ANIME, isAdult: false) { %s } } }'
         % (page, args, MEDIA_FIELDS))
    d = imp.gql(q)
    return d['data']['Page']['media']


def main():
    seen_ids = {}
    items = []
    total_requests = 0
    start = time.time()
    for name, pages, args in PLAN:
        for page in range(1, pages + 1):
            try:
                medias = fetch_page(args, page)
            except Exception as e:
                print('  [%s] page %d 失败: %s' % (name, page, str(e)[:100]))
                continue
            total_requests += 1
            print('[%s] page %d → %d 部 (累计 %d)' % (name, page, len(medias), len(items)))
            for m in medias:
                if m.get('isAdult') or (m.get('countryOfOrigin') or '') != 'JP':
                    continue
                if m['id'] in seen_ids:
                    continue
                seen_ids[m['id']] = 1
                items.append(m)
            # 每页后间隔
            time.sleep(1.0)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump({'generated_at': time.strftime('%Y-%m-%dT%H:%M:%S'),
                   'source': 'anilist', 'total_requests': total_requests,
                   'items': items}, f, ensure_ascii=False)
    print('== 完成 == 请求=%d | 候选=%d | 输出=%s | 耗时=%.0fs'
          % (total_requests, len(items), OUT, time.time() - start))


if __name__ == '__main__':
    main()
