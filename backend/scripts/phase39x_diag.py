"""Phase 39.x — 生产 Characters 完整性只读诊断脚本（不修改任何数据）。

用途：区分"角色显示错误"发生在哪一层：
  CASE A  DB 关系污染（角色绑到错误 anime）
  CASE B  后端 API 过滤失效（anime_id 未生效，返回全量）
  CASE C  前端 merge（本脚本无法测，需浏览器/SSR 检查）

用法（在服务器 backend 容器内）：
  docker compose exec backend python scripts/phase39x_diag.py
"""
from __future__ import annotations
import os
import sys
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from app.database import SessionLocal  # noqa: E402
from app.models import Anime, Character, CharacterVoice, VoiceActor  # noqa: E402

# 1. 已知有角色的 anime 采样（按角色数 top 取 5 个，避免误选无角色作品）
PROBE_ANIME = None  # 自动选择


def main():
    db = SessionLocal()
    print("=" * 60)
    print("Phase 39.x 生产诊断（只读）")
    print("=" * 60)

    # ---- 0. 后端 characters API 源码是否含 anime_id 过滤 ----
    try:
        src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..',
                                'app', 'api', 'characters.py'), encoding='utf-8').read()
        has_filter = 'Character.anime_id == anime_id' in src
        print(f"[0] characters.py 含 anime_id filter: {has_filter}  "
              f"({'新代码' if has_filter else '旧代码→过滤失效风险'})")
    except Exception as e:
        print(f"[0] 读取 characters.py 失败: {e}")

    # ---- 1. DB 直接查询：5 个 anime 的角色数 ----
    from sqlalchemy import func
    top = db.query(Anime.id, Anime.title, Anime.slug).join(
        Character, Character.anime_id == Anime.id
    ).group_by(Anime.id).order_by(func.count(Character.id).desc()).limit(5).all()
    if not top:
        print("[1] DB 中没有任何角色数据！")
        return
    print("\n[1] DB 直接查询（5 个角色最多的 anime）:")
    db_counts = {}
    for aid, title, slug in top:
        n = db.query(Character).filter(Character.anime_id == aid).count()
        db_counts[aid] = n
        print(f"    anime_id={aid} {str(title)[:36]!r} ({slug}) -> {n} 角色")

    # ---- 2. API 查询同样 5 个 anime ----
    print("\n[2] API 查询（GET /api/characters?anime_id=X）:")
    api_base = "http://127.0.0.1:8000/api"
    mismatch = []
    for aid, title, slug in top:
        try:
            with urllib.request.urlopen(f"{api_base}/characters?anime_id={aid}", timeout=15) as r:
                data = __import__('json').loads(r.read().decode('utf-8'))
            api_n = len(data)
            flag = "OK" if api_n == db_counts[aid] else f"⚠️ 不一致 (DB={db_counts[aid]})"
            if api_n != db_counts[aid]:
                mismatch.append((aid, db_counts[aid], api_n))
            print(f"    anime_id={aid} -> API {api_n} 角色 {flag}")
        except Exception as e:
            print(f"    anime_id={aid} -> API ERR {e}")
            mismatch.append((aid, db_counts[aid], 'ERR'))

    # ---- 3. 三个问题角色的 DB 绑定 ----
    print("\n[3] 问题角色 DB 绑定:")
    for kw in ['Tanjiro', 'Killua', 'Luffy']:
        rows = db.query(Character).filter(
            (Character.name_en.like(f"%{kw}%")) | (Character.native_name.like(f"%{kw}%"))
        ).all()
        for c in rows:
            a = db.query(Anime).filter(Anime.id == c.anime_id).first()
            print(f"    {c.name_en or c.name!r} source_id={c.source_id!r} -> "
                  f"anime_id={c.anime_id} {str(a.title)[:30] if a else '?'!r} slug={a.slug if a else '?'}")

    # ---- 4. 全局角色去重风险：同 source_id 跨 anime ----
    print("\n[4] 同 source_id 跨 anime 的角色（合法=同 franchise 多作品；异常=无关作品）:")
    from sqlalchemy import text
    from app.database import engine as _engine
    # 兼容 SQLite（GROUP_CONCAT）与 PostgreSQL（STRING_AGG）
    if _engine.dialect.name == "postgresql":
        agg = "STRING_AGG(DISTINCT a.title, '|')", "STRING_AGG(DISTINCT a.slug, '|')"
    else:
        agg = "GROUP_CONCAT(DISTINCT a.title)", "GROUP_CONCAT(DISTINCT a.slug)"
    rows = db.execute(text(
        f"SELECT c.source_id, COUNT(DISTINCT c.anime_id) n_anime, "
        f"{agg[0]} titles, {agg[1]} slugs "
        f"FROM characters c JOIN anime a ON a.id=c.anime_id "
        f"WHERE c.source_id != '' GROUP BY c.source_id HAVING n_anime > 1")).fetchall()
    if not rows:
        print("    无（每个角色只绑定一个 anime）")
    for r in rows[:20]:
        print(f"    source_id={r[0]} 出现在 {r[1]} 个 anime: {str(r[3])[:100]}")

    # ---- 结论 ----
    print("\n" + "=" * 60)
    if mismatch:
        print(f"结论: DB 与 API 角色数不一致 {len(mismatch)}/{len(top)} 处 → ")
        print("  若 API 返回数 ≈ 全量角色(如 476+) 且 DB 数小 → CASE B（后端 API 旧代码/anime_id 过滤失效）")
        print("  若 DB 数本身异常大 → CASE A（DB 关系污染，需进一步查 importer）")
    else:
        print("结论: 采样 anime 的 DB 与 API 角色数一致 → 过滤正常。")
        print("  若用户仍看到跨作品角色，需检查第 [4] 项跨 anime 角色是否为合法 franchise 关系；")
        print("  或检查 SSR/前端渲染（浏览器 Network 中 /api/characters?anime_id= 的实际返回）。")


if __name__ == '__main__':
    main()
