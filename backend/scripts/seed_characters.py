"""角色 + 声优 MVP 导入（manual curated 知名作品公开配音信息）。"""
from __future__ import annotations
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from app.database import Base, engine, SessionLocal
from app.models import Anime, Character, CharacterVoice, VoiceActor

def _slug(v: str) -> str:
    import re
    s = re.sub(r'[^a-z0-9]+', '-', (v or '').lower()).strip('-')
    return s or 'x'

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()
    Base.metadata.create_all(engine)
    data = json.load(open('data/character_seed.json', encoding='utf-8'))
    db = SessionLocal()
    va_map = {}; stats = {'va': 0, 'char': 0, 'rel': 0, 'skip': []}
    try:
        for anime_cn, cname, cname_en, cslug, va_cn, va_en, cdesc in data['rows']:
            anime = db.query(Anime).filter(Anime.chinese_title == anime_cn).first()
            if anime is None:
                stats['skip'].append(f'{anime_cn}/{cname}')
                continue
            if va_cn not in va_map:
                va = db.query(VoiceActor).filter(VoiceActor.name == va_cn).first()
                if va is None and not args.dry_run:
                    va = VoiceActor(name=va_cn, name_en=va_en, slug=_slug(va_en or va_cn),
                                    description=data['va_desc'].get(va_cn, ''))
                    db.add(va); db.flush()
                    stats['va'] += 1
                elif va is not None:
                    stats['va'] += 0
                va_map[va_cn] = va
            va = va_map.get(va_cn)
            ch = db.query(Character).filter(Character.slug == cslug).first()
            if ch is None and not args.dry_run:
                ch = Character(name=cname, name_en=cname_en, slug=cslug, description=cdesc,
                               aliases=f'{cname},{cname_en}', anime_id=anime.id)
                db.add(ch); db.flush()
                stats['char'] += 1
                if va:
                    db.add(CharacterVoice(character_id=ch.id, voice_actor_id=va.id))
                    stats['rel'] += 1
        if not args.dry_run:
            db.commit()
        print('声优:', stats['va'], '| 角色:', stats['char'], '| 关系:', stats['rel'], '| 跳过:', stats['skip'] or '无')
    finally:
        db.close()

if __name__ == '__main__':
    main()
