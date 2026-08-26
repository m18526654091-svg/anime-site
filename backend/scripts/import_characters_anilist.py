"""AniList 角色/声优批量导入流水线。

fetch(AniList GraphQL) → normalize → dedupe → import

特性:
  - 幂等: 重复运行不重复新增角色/声优/关系（source_id / 名称 / 唯一约束兜底）
  - --dry-run: 只统计 new/skipped/conflicts，不写库
  - 外部 ID: Character/VoiceActor 写入 source='anilist' + source_id
  - 旧库自动 ALTER 补列（sqlite / postgres 兼容）

用法:
  python scripts/import_characters_anilist.py --dry-run
  python scripts/import_characters_anilist.py
"""
from __future__ import annotations
import argparse
import json
import os
import re
import sys
import time
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from sqlalchemy import text
from app.database import Base, engine, SessionLocal
from app.models import Anime, Character, CharacterVoice, VoiceActor

# stdout 行缓冲：日志重定向到文件时能实时看到进度
try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass

OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))
GRAPHQL = 'https://graphql.anilist.co'
MANIFEST = 'data/anilist_characters_manifest.json'

# 默认请求参数（保守稳定优先，可通过 CLI 覆盖）
DEFAULT_DELAY = 1.0       # 成功请求之间最小间隔（秒）
DEFAULT_RETRIES = 4       # 429/网络错误最大重试次数
DEFAULT_TIMEOUT = 45      # 单请求超时（秒）
MAX_BACKOFF = 30          # 指数退避上限（秒）

# 全局请求状态（统计 + 间隔控制）
REQUEST_STATS = {'count': 0, 'http_429': 0, 'http_5xx': 0, 'http_other': 0}
_last_request_at = 0.0

# 新列（旧库需 ALTER 补充）
NEW_COLUMNS = {
    'characters': [('native_name', 'VARCHAR(120)'), ('source', 'VARCHAR(40)'), ('source_id', 'VARCHAR(64)')],
    'voice_actors': [('native_name', 'VARCHAR(120)'), ('source', 'VARCHAR(40)'), ('source_id', 'VARCHAR(64)')],
}

def _slug(v: str) -> str:
    s = re.sub(r'[^a-z0-9]+', '-', (v or '').lower()).strip('-')
    return s or 'x'

def _norm(v: str) -> str:
    """名称规范化：小写、去空格/标点/长音符，用于宽容匹配。

    仅对含拉丁字母/数字的名称做规范化（正则 \\W 会吃掉 CJK/假名/谚文，
    纯非拉丁文本保留原样，避免不同日文名被压成空串互相误匹配）。
    """
    s = (v or '').strip()
    if not s:
        return s
    low = s.lower()
    if not re.search(r'[a-z0-9]', low):
        return s
    s = re.sub(r'[\s\W_]+', '', low)
    for a, b in (('ō', 'o'), ('ū', 'u'), ('ā', 'a'), ('ī', 'i'), ('ē', 'e'), ('ō', 'o')):
        s = s.replace(a, b)
    return s

def ensure_columns():
    """旧库（已建表无新列）自动补列。"""
    for table, cols in NEW_COLUMNS.items():
        if engine.dialect.name == 'sqlite':
            with engine.connect() as c:
                existing = {r[1] for r in c.execute(text('PRAGMA table_info(%s)' % table)).fetchall()}
        else:
            with engine.connect() as c:
                existing = {r[0] for r in c.execute(text(
                    "SELECT column_name FROM information_schema.columns WHERE table_name='%s'" % table)).fetchall()}
        with engine.begin() as c:
            for col, typ in cols:
                if col not in existing:
                    c.execute(text('ALTER TABLE %s ADD COLUMN %s %s DEFAULT \'\'' % (table, col, typ)))

def _backoff_seconds(attempt: int) -> float:
    """指数退避：第1次失败 2s、第2次 4s、第3次 8s，上限 MAX_BACKOFF。"""
    return min(2 ** (attempt + 1), MAX_BACKOFF)


def gql(query: str, timeout: float = None, retries: int = None, delay: float = None):
    """GraphQL 请求，带 429 Retry-After / 指数退避 / 请求间隔。

    策略:
      - 429: 优先遵守 Retry-After header，否则 2^n 指数退避（上限 30s），最多 retries 次重试
      - 5xx: 最多 2 次重试（指数退避）
      - 4xx 非 429: 不重试，直接抛错
      - 网络/超时错误: 指数退避重试
    每次请求（含重试）前保证与上一次至少间隔 delay 秒。
    """
    timeout = timeout if timeout is not None else DEFAULT_TIMEOUT
    retries = retries if retries is not None else DEFAULT_RETRIES
    delay = delay if delay is not None else DEFAULT_DELAY
    global _last_request_at

    body = json.dumps({'query': query}).encode('utf-8')
    req = urllib.request.Request(GRAPHQL, data=body, headers={
        'Content-Type': 'application/json', 'User-Agent': 'AnimeHub-Import/1.0'})

    last = None
    for attempt in range(retries + 1):  # 初始请求 + retries 次重试
        # 请求间隔控制（成功/失败请求都算）
        wait = delay - (time.time() - _last_request_at)
        if wait > 0:
            time.sleep(wait)
        _last_request_at = time.time()
        REQUEST_STATS['count'] += 1
        try:
            resp = OPENER.open(req, timeout=timeout)
            return json.loads(resp.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            status = e.code
            if status == 429:
                REQUEST_STATS['http_429'] += 1
                ra = e.headers.get('Retry-After') if e.headers else None
                wait_s = 0
                if ra and ra.strip().isdigit():
                    wait_s = min(int(ra.strip()), MAX_BACKOFF)
                else:
                    wait_s = _backoff_seconds(attempt)
                if attempt < retries:
                    time.sleep(wait_s)
                    continue
                last = e
            elif status >= 500:
                REQUEST_STATS['http_5xx'] += 1
                if attempt < min(retries, 2):  # 5xx 最多 2 次重试
                    time.sleep(_backoff_seconds(attempt))
                    continue
                last = e
            else:
                # 4xx 非 429 不重试
                REQUEST_STATS['http_other'] += 1
                last = e
            break
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            REQUEST_STATS['http_other'] += 1
            last = e
            if attempt < retries:
                time.sleep(_backoff_seconds(attempt))
                continue
            break
        except Exception as e:
            REQUEST_STATS['http_other'] += 1
            last = e
            if attempt < retries:
                time.sleep(_backoff_seconds(attempt))
                continue
            break
    raise last

def fetch_characters(anilist_id: int, timeout: float = None, retries: int = None, delay: float = None):
    """分页拉取 AniList 角色（perPage 上限 50，最多 4 页）。"""
    all_out = []
    title = ''
    for page in range(1, 5):
        q = ('query { Media(id: %d) { id title { romaji } '
             'characters(page: %d, perPage: 50, sort: ROLE) { edges { role '
             'voiceActors(language: JAPANESE) { id name { full native } } '
             'node { id name { full native } } } } } }' % (anilist_id, page))
        d = gql(q, timeout=timeout, retries=retries, delay=delay)
        m = d['data']['Media']
        if not title:
            title = m['title']['romaji']
        edges = m['characters']['edges']
        if not edges:
            break
        for e in edges:
            c = e['node']
            all_out.append({
                'aid': c['id'],
                'name_full': c['name']['full'],
                'name_native': c['name'].get('native') or '',
                'role': e['role'],
                'vas': [{'id': v['id'], 'name_full': v['name']['full'],
                         'name_native': v['name'].get('native') or ''} for v in e['voiceActors']],
            })
    return title, all_out


def find_character(db, name_full, name_native, name_cn, source_id, anime_id):
    """去重匹配 Character：source_id > name_en/native > name。"""
    if source_id:
        c = db.query(Character).filter(Character.source == 'anilist',
                                       Character.source_id == str(source_id)).first()
        if c:
            return c, 'exists'
    if name_full:
        c = db.query(Character).filter(Character.name_en == name_full).first()
        if c:
            return c, 'reuse'
        n = _norm(name_full)
        for cc in db.query(Character).filter(Character.name_en != '').all():
            if _norm(cc.name_en) == n:
                return cc, 'reuse'
    if name_native:
        c = db.query(Character).filter(Character.native_name == name_native).first()
        if c:
            return c, 'reuse'
        n = _norm(name_native)
        for cc in db.query(Character).filter(Character.native_name != '').all():
            if _norm(cc.native_name) == n:
                return cc, 'reuse'
    if name_cn:
        c = db.query(Character).filter(Character.name == name_cn).first()
        if c:
            return c, 'reuse'
    return None, 'new'

def find_voice_actor(db, va, merge_map):
    """去重匹配 VoiceActor：merge 中文名 > source_id > name_en/native > name。"""
    staff_id = str(va['id'])
    if staff_id in merge_map:
        c = db.query(VoiceActor).filter(VoiceActor.name == merge_map[staff_id]).first()
        if c:
            return c, 'reuse'
    if va['id']:
        c = db.query(VoiceActor).filter(VoiceActor.source == 'anilist',
                                        VoiceActor.source_id == staff_id).first()
        if c:
            return c, 'exists'
    full, native = va['name_full'], va['name_native']
    nf = _norm(full)
    if full:
        c = db.query(VoiceActor).filter(VoiceActor.name_en == full).first()
        if c:
            return c, 'reuse'
        for v in db.query(VoiceActor).filter(VoiceActor.name_en != '').all():
            if _norm(v.name_en) == nf:
                return v, 'reuse'
    if native:
        c = db.query(VoiceActor).filter(VoiceActor.native_name == native).first()
        if c:
            return c, 'reuse'
        nn = _norm(native)
        for v in db.query(VoiceActor).filter(VoiceActor.native_name != '').all():
            if _norm(v.native_name) == nn:
                return v, 'reuse'
    return None, 'new'


def build_configs_from_db(db, n: int):
    """从数据库自动发现高价值作品（anilist_id 非空，按评分排序取前 n，anilist_id 去重）。

    无 only_ids / characters_cn：角色按 MAIN > SUPPORTING 截取前 max_characters 个，
    name 使用 AniList 可靠原名（native 日文 / 英文），不猜测中文译名。
    """
    rows = db.execute(text(
        "SELECT slug, anilist_id, COALESCE(score, 0) AS sc, year FROM anime "
        "WHERE anilist_id IS NOT NULL ORDER BY sc DESC, year DESC")).fetchall()
    seen = set()
    configs = []
    for r in rows:
        aid = int(r[1])
        if aid in seen:
            continue
        seen.add(aid)
        configs.append({'anime_slug': r[0], 'anilist_id': aid,
                        'min_role': 'SUPPORTING', 'max_characters': 6})
        if len(configs) >= n:
            break
    return configs

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--anime', default='', help='只处理指定 anime_slug（逗号分隔）')
    ap.add_argument('--anime-from-db', type=int, default=0,
                    help='从数据库自动发现：按评分选前 N 部 anilist 作品拉角色（0=用 manifest）')
    ap.add_argument('--delay', type=float, default=DEFAULT_DELAY,
                    help='请求最小间隔秒数（默认 %.1f）' % DEFAULT_DELAY)
    ap.add_argument('--retries', type=int, default=DEFAULT_RETRIES,
                    help='429/网络错误最大重试次数（默认 %d）' % DEFAULT_RETRIES)
    ap.add_argument('--timeout', type=float, default=DEFAULT_TIMEOUT,
                    help='单请求超时秒数（默认 %d）' % DEFAULT_TIMEOUT)
    args = ap.parse_args()

    Base.metadata.create_all(engine)
    ensure_columns()

    db = SessionLocal()
    if args.anime_from_db:
        configs = build_configs_from_db(db, args.anime_from_db)
        merge_map = {}
        print('[auto] 从数据库自动选择 %d 部高价值作品（按评分排序）' % len(configs))
    else:
        manifest = json.load(open(MANIFEST, encoding='utf-8'))
        configs = manifest['animes']
        merge_map = manifest.get('voice_actor_merge', {})
    stats = {'va_new': 0, 'char_new': 0, 'rel_new': 0,
             'va_reuse': 0, 'char_reuse': 0, 'rel_skip': 0,
             'skip_no_anime': [], 'conflict': [], 'failed': [],
             'succeeded': []}
    only = [s for s in args.anime.split(',') if s] if args.anime else []
    # 已有关系键（character.source_id, voice_actor.source_id）——dry-run/正式统一用外部键去重
    existing_rels = set()
    for r in db.execute(text(
            "SELECT ch.source_id, va.source_id FROM character_voices cv "
            "JOIN characters ch ON ch.id = cv.character_id "
            "JOIN voice_actors va ON va.id = cv.voice_actor_id "
            "WHERE ch.source_id != '' AND va.source_id != ''")).all():
        if r[0] and r[1]:
            existing_rels.add((r[0], r[1]))
    try:
        # 阶段 1：并发 fetch 全部作品的角色（3 workers，稳定优先，delay/retry 保留）
        import concurrent.futures

        def _fetch_one(conf):
            return fetch_characters(conf['anilist_id'], timeout=args.timeout,
                                    retries=args.retries, delay=args.delay)

        fetch_results = {}
        targets = [c for c in configs if not only or c['anime_slug'] in only]
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
            future_map = {ex.submit(_fetch_one, conf): conf for conf in targets}
            for fut in concurrent.futures.as_completed(future_map):
                conf = future_map[fut]
                try:
                    media_title, chars = fut.result()
                    fetch_results[conf['anime_slug']] = (conf, media_title, chars)
                    print('== %s (anilist %s) fetch OK | 角色 %d'
                          % (conf['anime_slug'], conf['anilist_id'], len(chars)))
                except Exception as e:
                    stats['failed'].append((conf['anime_slug'], str(e)[:120]))
                    print('== %s fetch 失败: %s' % (conf['anime_slug'], str(e)[:120]))

        # 阶段 2：串行导入（幂等去重）
        for conf in configs:
            slug = conf['anime_slug']
            if only and slug not in only:
                continue
            fetched = fetch_results.get(slug)
            if fetched is None:
                continue  # fetch 失败已记录在 failed
            anime = db.query(Anime).filter(Anime.slug == slug).first()
            if anime is None:
                stats['skip_no_anime'].append(slug)
                continue
            conf, media_title, chars = fetched
            stats['succeeded'].append(slug)
            print('-- 导入 %s (%s) | 角色 %d' % (anime.title, slug, len(chars)))
            cns = conf.get('characters_cn', {})
            vans = conf.get('voice_actors_cn', {})
            maxc = conf.get('max_characters', 10)
            role_min = conf.get('min_role', 'SUPPORTING')
            order = {'MAIN': 0, 'SUPPORTING': 1, 'BACKGROUND': 2}
            chars = [c for c in chars if order.get(c['role'], 9) <= order[role_min]]
            only_ids = conf.get('only_ids')
            if only_ids:
                # 精确角色清单：只导入指定 AniList 角色（不受 fetch 顺序影响）
                want = {str(x) for x in only_ids}
                chars = [c for c in chars if str(c['aid']) in want]
            else:
                chars = chars[:maxc]
            for c in chars:
                name = cns.get(str(c['aid'])) or c['name_native'] or c['name_full']
                existing, how = find_character(db, c['name_full'], c['name_native'], name,
                                               str(c['aid']), anime.id)
                if how in ('exists', 'reuse'):
                    stats['char_reuse'] += 1
                    ch = existing
                    if not ch.source_id and not args.dry_run:
                        ch.source = 'anilist'
                        ch.source_id = str(c['aid'])
                        ch.native_name = c['name_native'] or ch.native_name
                else:
                    slug = _slug(c['name_full'] or name)
                    if db.query(Character).filter(Character.slug == slug).first():
                        stats['conflict'].append('slug:%s' % slug)
                        print('   冲突跳过 角色: %s (slug %s 已占用)' % (name, slug))
                        continue
                    stats['char_new'] += 1
                    ch = None
                    if not args.dry_run:
                        ch = Character(name=name[:120], name_en=c['name_full'],
                                       native_name=c['name_native'], slug=slug,
                                       aliases=','.join([x for x in (name, c['name_native'], c['name_full']) if x][:4]),
                                       source='anilist', source_id=str(c['aid']),
                                       anime_id=anime.id)
                        db.add(ch)
                        db.flush()
                for va in c['vas']:
                    if not va['id']:
                        continue
                    vname = vans.get(str(va['id'])) or va['name_native'] or va['name_full']
                    v, how2 = find_voice_actor(db, va, merge_map)
                    if how2 in ('exists', 'reuse'):
                        stats['va_reuse'] += 1
                        if not v.source_id and not args.dry_run:
                            v.source = 'anilist'
                            v.source_id = str(va['id'])
                            v.native_name = va['name_native'] or v.native_name
                    else:
                        vslug = _slug(va['name_full'] or vname)
                        if db.query(VoiceActor).filter(VoiceActor.slug == vslug).first():
                            stats['conflict'].append('va_slug:%s' % vslug)
                            print('   冲突跳过 声优: %s' % vname)
                            continue
                        stats['va_new'] += 1
                        v = None
                        if not args.dry_run:
                            v = VoiceActor(name=vname[:120], name_en=va['name_full'],
                                           native_name=va['name_native'], slug=vslug,
                                           aliases=','.join([x for x in (vname, va['name_native'], va['name_full']) if x][:4]),
                                           source='anilist', source_id=str(va['id']))
                            db.add(v)
                            db.flush()
                    rel_key = (str(c['aid']), str(va['id']))
                    if ch is not None and v is not None:
                        # 已有实体：直接用 id 判重（幂等兜底，覆盖无 source_id 的旧数据）
                        dup = db.query(CharacterVoice).filter(
                            CharacterVoice.character_id == ch.id,
                            CharacterVoice.voice_actor_id == v.id).first()
                        if dup:
                            stats['rel_skip'] += 1
                            continue
                    elif rel_key in existing_rels:
                        stats['rel_skip'] += 1
                        continue
                    stats['rel_new'] += 1
                    if not args.dry_run and ch is not None and v is not None:
                        db.add(CharacterVoice(character_id=ch.id, voice_actor_id=v.id))
                        existing_rels.add(rel_key)
        if not args.dry_run:
            db.commit()
        print('--- 结果 ---')
        print('新增角色: %d | 复用角色: %d' % (stats['char_new'], stats['char_reuse']))
        print('新增声优: %d | 复用声优: %d' % (stats['va_new'], stats['va_reuse']))
        print('新增关系: %d | 已存在关系跳过: %d' % (stats['rel_new'], stats['rel_skip']))
        print('跳过(无作品):', stats['skip_no_anime'] or '无')
        print('冲突:', stats['conflict'] or '无')
        print('成功作品:', stats['succeeded'] or '无')
        print('失败作品:', [(s, e) for s, e in stats['failed']] or '无')
        print('请求统计: 429次数=%d | HTTP 5xx次数=%d | 其他错误=%d | 实际请求次数=%d'
              % (REQUEST_STATS['http_429'], REQUEST_STATS['http_5xx'],
                 REQUEST_STATS['http_other'], REQUEST_STATS['count']))
    finally:
        db.close()

if __name__ == '__main__':
    main()

