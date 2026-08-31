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
# Phase 36 Round 2：增量抓取 2018-2022 季番（Phase 35 未覆盖年份），merge 进现有 candidates
PLAN = [
    ('season_2018_winter', 1, 'season: WINTER, seasonYear: 2018, sort: [POPULARITY_DESC]'),
    ('season_2018_spring', 1, 'season: SPRING, seasonYear: 2018, sort: [POPULARITY_DESC]'),
    ('season_2018_summer', 1, 'season: SUMMER, seasonYear: 2018, sort: [POPULARITY_DESC]'),
    ('season_2018_fall', 1, 'season: FALL, seasonYear: 2018, sort: [POPULARITY_DESC]'),
    ('season_2019_winter', 1, 'season: WINTER, seasonYear: 2019, sort: [POPULARITY_DESC]'),
    ('season_2019_spring', 1, 'season: SPRING, seasonYear: 2019, sort: [POPULARITY_DESC]'),
    ('season_2019_summer', 1, 'season: SUMMER, seasonYear: 2019, sort: [POPULARITY_DESC]'),
    ('season_2019_fall', 1, 'season: FALL, seasonYear: 2019, sort: [POPULARITY_DESC]'),
    ('season_2020_winter', 1, 'season: WINTER, seasonYear: 2020, sort: [POPULARITY_DESC]'),
    ('season_2020_spring', 1, 'season: SPRING, seasonYear: 2020, sort: [POPULARITY_DESC]'),
    ('season_2020_summer', 1, 'season: SUMMER, seasonYear: 2020, sort: [POPULARITY_DESC]'),
    ('season_2020_fall', 1, 'season: FALL, seasonYear: 2020, sort: [POPULARITY_DESC]'),
    ('season_2021_winter', 1, 'season: WINTER, seasonYear: 2021, sort: [POPULARITY_DESC]'),
    ('season_2021_spring', 1, 'season: SPRING, seasonYear: 2021, sort: [POPULARITY_DESC]'),
    ('season_2021_summer', 1, 'season: SUMMER, seasonYear: 2021, sort: [POPULARITY_DESC]'),
    ('season_2021_fall', 1, 'season: FALL, seasonYear: 2021, sort: [POPULARITY_DESC]'),
    ('season_2022_winter', 1, 'season: WINTER, seasonYear: 2022, sort: [POPULARITY_DESC]'),
    ('season_2022_spring', 1, 'season: SPRING, seasonYear: 2022, sort: [POPULARITY_DESC]'),
    ('season_2022_summer', 1, 'season: SUMMER, seasonYear: 2022, sort: [POPULARITY_DESC]'),
    ('season_2022_fall', 1, 'season: FALL, seasonYear: 2022, sort: [POPULARITY_DESC]'),
]


def fetch_page(args: str, page: int):
    q = ('query { Page(page: %d, perPage: 50) { media(%s, type: ANIME, isAdult: false) { %s } } }'
         % (page, args, MEDIA_FIELDS))
    d = imp.gql(q)
    return d['data']['Page']['media']


def main():
    seen_ids = {}
    items = []
    # Phase 36：merge 模式 — 加载现有 candidates，只增量追加（不丢已有数据）
    if os.path.exists(OUT):
        try:
            old = json.load(open(OUT, encoding='utf-8'))
            old_items = old.get('items') if isinstance(old, dict) else old
            for m in old_items:
                if m.get('id') not in seen_ids:
                    seen_ids[m['id']] = 1
                    items.append(m)
            print('[merge] 已加载现有候选 %d 条，继续增量抓取' % len(items))
        except Exception as e:
            print('[merge] 加载现有候选失败: %s' % str(e)[:80])
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
            # Phase 36：每查询后增量写盘（进程被杀不丢已抓进度）
            with open(OUT, 'w', encoding='utf-8') as f:
                json.dump({'generated_at': time.strftime('%Y-%m-%dT%H:%M:%S'),
                           'source': 'anilist', 'total_requests': total_requests,
                           'items': items}, f, ensure_ascii=False)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump({'generated_at': time.strftime('%Y-%m-%dT%H:%M:%S'),
                   'source': 'anilist', 'total_requests': total_requests,
                   'items': items}, f, ensure_ascii=False)
    print('== 完成 == 请求=%d | 候选=%d | 输出=%s | 耗时=%.0fs'
          % (total_requests, len(items), OUT, time.time() - start))


if __name__ == '__main__':
    main()
