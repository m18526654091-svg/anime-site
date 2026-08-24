"""Growth Sprint 2: Production 10 部内容增强 + SEO Title 试点（dry-run / apply）。

- 仅 10 部（Stage 12-I 样本）。
- 事实字段只允许使用 Stage 12-J.1.5 已 VERIFIED 的 Wikidata QID（7/10）。
  REVIEW/REJECTED 的 3 部不写任何事实字段 / 不写 SEO title（不虚构 format/episodes）。
- 写入：studio / episodes / status / region / description / seo_title + anime_field_sources。
- provenance：studio/episodes -> wikidata (verified=1)；status/region/description/seo_title -> manual。

用法（backend 目录）:
    python -m scripts.growth_sprint2_enrich --dry-run    # 只打印不写
    python -m scripts.growth_sprint2_enrich --apply      # 写 DATABASE_URL 指向的库
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import UTC, datetime

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from app.database import SessionLocal  # noqa: E402
from app.models import Anime, AnimeFieldSource, DataSource  # noqa: E402

_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

# ---- 10 部样本（QID 状态来自 stage12j_qid_repair_report.json） ----
# (key, anime_id, qid, qid_status, studio, episodes, status, region, episodes_semantics)
_FACTS: list[dict] = [
    {"key": "进击的巨人", "qid": "Q22126305", "verified": True,
     "studio": "WIT STUDIO", "episodes": 87, "status": "完结", "region": "日本",
     "semantics": "series"},
    {"key": "鬼灭之刃", "qid": "Q63350570", "verified": True,
     "studio": "ufotable", "episodes": 26, "status": "连载中", "region": "日本",
     "semantics": "series"},
    {"key": "钢之炼金术师FA", "qid": "Q437808", "verified": True,
     "studio": "BONES", "episodes": 64, "status": "完结", "region": "日本",
     "semantics": "series"},
    {"key": "死亡笔记", "qid": "Q718624", "verified": True,
     "studio": "MADHOUSE", "episodes": 37, "status": "完结", "region": "日本",
     "semantics": "series"},
    {"key": "命运石之门", "qid": "Q20590069", "verified": True,
     "studio": "WHITE FOX", "episodes": 24, "status": "完结", "region": "日本",
     "semantics": "series"},
    {"key": "你的名字。", "qid": "Q21697406", "verified": True,
     "studio": "CoMix Wave Films", "episodes": 1, "status": "完结", "region": "日本",
     "semantics": "movie"},
    {"key": "千与千寻", "qid": "Q155653", "verified": True,
     "studio": "吉卜力工作室", "episodes": 1, "status": "完结", "region": "日本",
     "semantics": "movie"},
    {"key": "叛逆的鲁路修", "qid": "Q114200", "verified": False, "semantics": "unknown"},
    {"key": "灌篮高手", "qid": "Q2430523", "verified": False, "semantics": "unknown"},
    {"key": "为美好的世界献上祝福！", "qid": "Q18239141", "verified": False,
     "semantics": "unknown"},
    {"key": "咒术回战", "qid": "Q98836216", "verified": True,
     "studio": "MAPPA", "episodes": 59, "status": "连载中", "region": "日本", "semantics": "series"},
    {"key": "火影忍者", "qid": "Q25929253", "verified": True,
     "studio": "Studio Pierrot", "episodes": 220, "status": "完结", "region": "日本", "semantics": "series"},
    {"key": "间谍过家家", "qid": "Q109333365", "verified": True,
     "studio": "Wit Studio", "episodes": 50, "status": "连载中", "region": "日本", "semantics": "series"},
    {"key": "电锯人", "qid": "Q104211858", "verified": True,
     "studio": "MAPPA", "episodes": 12, "status": "连载中", "region": "日本", "semantics": "series"},
    {"key": "葬送的芙莉莲", "qid": "Q115792176", "verified": True,
     "studio": "Madhouse", "episodes": 38, "status": "连载中", "region": "日本", "semantics": "series"},
    {"key": "我推的孩子", "qid": "Q112305523", "verified": True,
     "studio": "Doga Kobo", "episodes": 35, "status": "连载中", "region": "日本", "semantics": "series"},
    {"key": "刀剑神域", "qid": "Q24238538", "verified": True,
     "studio": "A-1 Pictures", "episodes": None, "status": "连载中", "region": "日本", "semantics": "series"},
    {"key": "黑子的篮球", "qid": "Q120118751", "verified": True,
     "studio": "Production I.G", "episodes": 75, "status": "完结", "region": "日本", "semantics": "series"},
    {"key": "名侦探柯南", "qid": "Q5363072", "verified": True,
     "studio": "TMS娱乐", "episodes": 1192, "status": "连载中", "region": "日本", "semantics": "series"},
    {"key": "银魂", "qid": "Q709716", "verified": True,
     "studio": "SUNRISE", "episodes": 353, "status": "完结", "region": "日本", "semantics": "series"},
    {"key": "紫罗兰永恒花园", "qid": "Q73896191", "verified": True,
     "studio": "京都动画", "episodes": 13, "status": "完结", "region": "日本", "semantics": "series"},
    {"key": "排球少年！！", "qid": "Q67144604", "verified": True,
     "studio": "Production I.G", "episodes": 85, "status": "完结", "region": "日本", "semantics": "series"},
    {"key": "海贼王", "qid": "Q673", "verified": False, "semantics": "unknown"},
    {"key": "石纪元", "qid": "Q38275959", "verified": False, "semantics": "unknown"},
    {"key": "我的英雄学院", "qid": "Q63686324", "verified": False, "semantics": "unknown"},
    {"key": "暗杀教室", "qid": "Q3277067", "verified": False, "semantics": "unknown"},
    {"key": "全职猎人", "qid": "Q696071", "verified": False, "semantics": "unknown"},
    {"key": "孤独摇滚！", "qid": "Q113317001", "verified": False, "semantics": "unknown"},
    {"key": "辉夜大小姐想让我告白", "qid": "Q135010800", "verified": False, "semantics": "unknown"},
    {"key": "一拳超人", "qid": "Q5102879", "verified": False, "semantics": "unknown"},
    {"key": "关于我转生变成史莱姆这档事", "qid": "Q61779950", "verified": True,
     "studio": "8bit", "episodes": 72, "status": "连载中", "region": "日本", "semantics": "series"},
    {"key": "新世纪福音战士", "qid": "Q1151814", "verified": True,
     "studio": "GAINAX", "episodes": 26, "status": "完结", "region": "日本", "semantics": "series"},
    {"key": "Fate/Zero", "qid": "Q96500220", "verified": True,
     "studio": "Ufotable", "episodes": 25, "status": "完结", "region": "日本", "semantics": "series"},
    {"key": "JOJO的奇妙冒险", "qid": "Q6204056", "verified": True,
     "studio": "David Production", "episodes": None, "status": "连载中", "region": "日本", "semantics": "series"},
    {"key": "轻音少女", "qid": "Q15863567", "verified": True,
     "studio": "京都动画", "episodes": 13, "status": "完结", "region": "日本", "semantics": "series"},
    {"key": "冰菓", "qid": "Q99853668", "verified": True,
     "studio": "京都动画", "episodes": 22, "status": "完结", "region": "日本", "semantics": "series"},
    {"key": "夏目友人帐", "qid": "Q55080189", "verified": True,
     "studio": "Shuka", "episodes": 13, "status": "连载中", "region": "日本", "semantics": "series"},
    {"key": "天气之子", "qid": "Q59692464", "verified": True,
     "studio": "CoMix Wave Films", "episodes": 1, "status": "完结", "region": "日本", "semantics": "movie"},
    {"key": "龙猫", "qid": "Q39571", "verified": True,
     "studio": "吉卜力工作室", "episodes": 1, "status": "完结", "region": "日本", "semantics": "movie"},
    {"key": "哈尔的移动城堡", "qid": "Q29011", "verified": True,
     "studio": "吉卜力工作室", "episodes": 1, "status": "完结", "region": "日本", "semantics": "movie"},
    {"key": "魔女宅急便", "qid": "Q196602", "verified": True,
     "studio": "吉卜力工作室", "episodes": 1, "status": "完结", "region": "日本", "semantics": "movie"},
    {"key": "幽灵公主", "qid": "Q186572", "verified": True,
     "studio": "吉卜力工作室", "episodes": 1, "status": "完结", "region": "日本", "semantics": "movie"},
    {"key": "食戟之灵", "qid": "Q79310969", "verified": True,
     "studio": "J.C.STAFF", "episodes": 86, "status": "完结", "region": "日本", "semantics": "series"},
    {"key": "妖精的尾巴", "qid": "Q124817637", "verified": True,
     "studio": "J.C.STAFF", "episodes": 328, "status": "完结", "region": "日本", "semantics": "series"},
    {"key": "Re:从零开始的异世界生活", "qid": "Q96401322", "verified": False, "semantics": "unknown"},
    {"key": "无职转生", "qid": "Q19840456", "verified": False, "semantics": "unknown"},
    {"key": "Fate/stay night UBW", "qid": None, "verified": False, "semantics": "unknown"},
    {"key": "龙与虎", "qid": "Q483150", "verified": False, "semantics": "unknown"},
    {"key": "未闻花名", "qid": None, "verified": False, "semantics": "unknown"},
    {"key": "声之形", "qid": "Q23925035", "verified": False, "semantics": "unknown"},
    {"key": "四月是你的谎言", "qid": "Q11419997", "verified": False, "semantics": "unknown"},
    {"key": "虫师", "qid": "Q1055370", "verified": False, "semantics": "unknown"},
    {"key": "灵能百分百", "qid": None, "verified": False, "semantics": "unknown"},
    {"key": "文豪野犬", "qid": "Q17215635", "verified": False, "semantics": "unknown"},
    {"key": "黄金神威", "qid": None, "verified": False, "semantics": "unknown"},
    {"key": "头文字D", "qid": "Q4041399", "verified": False, "semantics": "unknown"},
    {"key": "七大罪", "qid": "Q57606675", "verified": False, "semantics": "unknown"},
    {"key": "数码宝贝大冒险", "qid": "Q689114", "verified": False, "semantics": "unknown"},
    {"key": "CLANNAD", "qid": "Q110607", "verified": False, "semantics": "unknown"},
    {"key": "约定的梦幻岛", "qid": None, "verified": False, "semantics": "unknown"},
    {"key": "天空之城", "qid": "Q498577", "verified": True,
     "studio": "吉卜力工作室", "episodes": 1, "status": "完结", "region": "日本", "semantics": "movie"},
    {"key": "悬崖上的金鱼姬", "qid": "Q236728", "verified": True,
     "studio": "吉卜力工作室", "episodes": 1, "status": "完结", "region": "日本", "semantics": "movie"},
    {"key": "日常", "qid": "Q106567447", "verified": True,
     "studio": "京都动画", "episodes": 26, "status": "完结", "region": "日本", "semantics": "series"},
    {"key": "天使的心跳", "qid": "Q531552", "verified": True,
     "studio": "VISUAL ARTS", "episodes": 13, "status": "完结", "region": "日本", "semantics": "series"},
    {"key": "白色相簿2", "qid": "Q61515844", "verified": True,
     "studio": "SATELIGHT", "episodes": 13, "status": "完结", "region": "日本", "semantics": "series"},
    {"key": "黑执事", "qid": "Q11678056", "verified": True,
     "studio": "A-1 Pictures", "episodes": 70, "status": "完结", "region": "日本", "semantics": "series"},
    {"key": "蜡笔小新", "qid": "Q1134782", "verified": True,
     "studio": "Shin-Ei Animation", "episodes": None, "status": "连载中", "region": "日本", "semantics": "series"},
    {"key": "樱桃小丸子", "qid": "Q2624529", "verified": True,
     "studio": "日本动画公司", "episodes": None, "status": "连载中", "region": "日本", "semantics": "series"},
    {"key": "少女与战车", "qid": "Q28219", "verified": True,
     "studio": "Actas", "episodes": 12, "status": "完结", "region": "日本", "semantics": "series"},
    {"key": "摇曳露营△", "qid": "Q64029196", "verified": True,
     "studio": "C-Station", "episodes": 37, "status": "完结", "region": "日本", "semantics": "series"},
    {"key": "阿松", "qid": "Q22668361", "verified": True,
     "studio": "Studio Zero", "episodes": 56, "status": "完结", "region": "日本", "semantics": "series"},
    {"key": "凉宫春日的忧郁", "qid": "Q10913555", "verified": True,
     "studio": "京都动画", "episodes": 28, "status": "完结", "region": "日本", "semantics": "series"},
    {"key": "魔法禁书目录", "qid": "Q17219196", "verified": True,
     "studio": "J.C.STAFF", "episodes": 74, "status": "连载中", "region": "日本", "semantics": "series"},
    {"key": "城市猎人", "qid": "Q3678619", "verified": True,
     "studio": "SUNRISE", "episodes": 158, "status": "完结", "region": "日本", "semantics": "series"},
    {"key": "星际牛仔", "qid": "Q1334287", "verified": True,
     "studio": "SUNRISE", "episodes": 26, "status": "完结", "region": "日本", "semantics": "series"},
    {"key": "心理测量者", "qid": "Q18578673", "verified": True,
     "studio": "Production I.G", "episodes": None, "status": "完结", "region": "日本", "semantics": "series"},
    {"key": "阿基拉", "qid": "Q1905968", "verified": True,
     "studio": "TMS娱乐", "episodes": 1, "status": "完结", "region": "日本", "semantics": "movie"},
    {"key": "红辣椒", "qid": "Q578595", "verified": True,
     "studio": "Madhouse", "episodes": 1, "status": "完结", "region": "日本", "semantics": "movie"},
    {"key": "魔卡少女樱", "qid": "Q29972136", "verified": True,
     "studio": "Madhouse", "episodes": 70, "status": "完结", "region": "日本", "semantics": "series"},
    {"key": "美少女战士", "qid": "Q704353", "verified": True,
     "studio": "东映动画", "episodes": 200, "status": "完结", "region": "日本", "semantics": "series"},
    {"key": "魔法少女小圆", "qid": "Q53353", "verified": True,
     "studio": "SHAFT", "episodes": 12, "status": "完结", "region": "日本", "semantics": "series"},
    {"key": "灼眼的夏娜", "qid": "Q3959058", "verified": True,
     "studio": "J.C.STAFF", "episodes": 72, "status": "完结", "region": "日本", "semantics": "series"},
    {"key": "五等分的新娘", "qid": None, "verified": False, "semantics": "unknown"},
    {"key": "冰上的尤里", "qid": None, "verified": False, "semantics": "unknown"},
    {"key": "转生恶役只好拔除破灭旗标", "qid": None, "verified": False, "semantics": "unknown"},
    {"key": "盾之勇者成名录", "qid": None, "verified": False, "semantics": "unknown"},
    {"key": "OVERLORD", "qid": None, "verified": False, "semantics": "unknown"},
    {"key": "哥布林杀手", "qid": None, "verified": False, "semantics": "unknown"},
    {"key": "异世界食堂", "qid": None, "verified": False, "semantics": "unknown"},
    {"key": "萤火之森", "qid": None, "verified": False, "semantics": "unknown"},
    {"key": "樱花庄的宠物女孩", "qid": None, "verified": False, "semantics": "unknown"},
    {"key": "男子高中生的日常", "qid": None, "verified": False, "semantics": "unknown"},
    {"key": "中华小当家", "qid": None, "verified": False, "semantics": "unknown"},
    {"key": "狼与香辛料", "qid": None, "verified": False, "semantics": "unknown"},
    {"key": "记录的地平线", "qid": None, "verified": False, "semantics": "unknown"},
    {"key": "哆啦A梦", "qid": None, "verified": False, "semantics": "unknown"},
    {"key": "精灵宝可梦", "qid": None, "verified": False, "semantics": "unknown"},
    {"key": "游戏王", "qid": None, "verified": False, "semantics": "unknown"},
    {"key": "网球王子", "qid": None, "verified": False, "semantics": "unknown"},
    {"key": "棒球大联盟", "qid": None, "verified": False, "semantics": "unknown"},
    {"key": "赛马娘 Pretty Derby", "qid": None, "verified": False, "semantics": "unknown"},
    {"key": "小林家的龙女仆", "qid": None, "verified": False, "semantics": "unknown"},
    {"key": "齐木楠雄的灾难", "qid": None, "verified": False, "semantics": "unknown"},
    {"key": "笨女孩", "qid": None, "verified": False, "semantics": "unknown"},
    {"key": "学园孤岛", "qid": None, "verified": False, "semantics": "unknown"},
    {"key": "化物语", "qid": None, "verified": False, "semantics": "unknown"},
    {"key": "青春猪头少年不会梦到兔女郎学姐", "qid": None, "verified": False, "semantics": "unknown"},
    {"key": "中二病也要谈恋爱！", "qid": None, "verified": False, "semantics": "unknown"},
    {"key": "某科学的超电磁炮", "qid": None, "verified": False, "semantics": "unknown"},
    {"key": "黑之契约者", "qid": None, "verified": False, "semantics": "unknown"},
    {"key": "攻壳机动队SAC", "qid": None, "verified": False, "semantics": "unknown"},
    {"key": "NANA", "qid": None, "verified": False, "semantics": "unknown"},
    {"key": "好想告诉你", "qid": None, "verified": False, "semantics": "unknown"},
    {"key": "月刊少女野崎君", "qid": None, "verified": False, "semantics": "unknown"},
    {"key": "蜂蜜与四叶草", "qid": None, "verified": False, "semantics": "unknown"},
    {"key": "约会大作战", "qid": None, "verified": False, "semantics": "unknown"},
    {"key": "食梦者", "qid": None, "verified": False, "semantics": "unknown"},
    {"key": "东京喰种", "qid": None, "verified": False, "semantics": "unknown"},
    {"key": "樱兰高校男公关部", "qid": None, "verified": False, "semantics": "unknown"},
    {"key": "交响情人梦", "qid": None, "verified": False, "semantics": "unknown"},
]

# 非 VERIFIED 3 部：只增强 description，不写事实字段 / 不写 SEO title
_NO_FACT_KEYS = {"叛逆的鲁路修", "灌篮高手", "为美好的世界献上祝福！",
                     "海贼王", "石纪元", "我的英雄学院", "暗杀教室", "全职猎人",
                     "孤独摇滚！", "辉夜大小姐想让我告白", "一拳超人",
                     "Re:从零开始的异世界生活", "无职转生", "Fate/stay night UBW", "龙与虎",
                     "未闻花名", "声之形", "四月是你的谎言", "虫师", "灵能百分百", "文豪野犬",
                     "黄金神威", "头文字D", "七大罪", "数码宝贝大冒险", "CLANNAD", "约定的梦幻岛",
                     "五等分的新娘",
                     "冰上的尤里",
                     "转生恶役只好拔除破灭旗标",
                     "盾之勇者成名录",
                     "OVERLORD",
                     "哥布林杀手",
                     "异世界食堂",
                     "萤火之森",
                     "樱花庄的宠物女孩",
                     "男子高中生的日常",
                     "中华小当家",
                     "狼与香辛料",
                     "记录的地平线",
                     "哆啦A梦",
                     "精灵宝可梦",
                     "游戏王",
                     "网球王子",
                     "棒球大联盟",
                     "赛马娘 Pretty Derby",
                     "小林家的龙女仆",
                     "齐木楠雄的灾难",
                     "笨女孩",
                     "学园孤岛",
                     "化物语",
                     "青春猪头少年不会梦到兔女郎学姐",
                     "中二病也要谈恋爱！",
                     "某科学的超电磁炮",
                     "黑之契约者",
                     "攻壳机动队SAC",
                     "NANA",
                     "好想告诉你",
                     "月刊少女野崎君",
                     "蜂蜜与四叶草",
                     "约会大作战",
                     "食梦者",
                     "东京喰种",
                     "樱兰高校男公关部",
                     "交响情人梦"}

_DESC_JSON = os.path.join(_DATA_DIR, "stage12i_content_enrichment_samples.json")


def _load_desc_b() -> dict:
    with open(_DESC_JSON, encoding="utf-8") as f:
        si = json.load(f)
    out = {s["chinese_title"]: s["description_b"]["text"] for s in si["samples"]}
    for extra in ("growth_sprint3_desc.json", "growth_sprint4_desc.json",
                 "growth_final_desc_batch1.json", "growth_final_desc_batch2.json",
                 "growth_final_desc_batch3.json"):
        p4 = os.path.join(_DATA_DIR, extra)
        if os.path.exists(p4):
            with open(p4, encoding="utf-8") as f:
                out.update(json.load(f))
    return out


def _seo_title(key: str, year, semantics: str) -> str | None:
    if key in _NO_FACT_KEYS or year is None:
        return None
    ep = next(f.get("episodes") for f in _FACTS if f["key"] == key)
    if semantics == "movie":
        return f"{key}（{year}）剧场版 | AnimeHub"
    if ep is None:
        return f"{key}（{year}）TV | AnimeHub"
    return f"{key}（{year}）TV {ep}集 | AnimeHub"


def _hash(source_key: str, field: str, value: str) -> str:
    return hashlib.sha256(f"{source_key}|{field}|{value}".encode("utf-8")).hexdigest()[:16]


def _ensure_source(db, source_key: str) -> DataSource:
    src = db.query(DataSource).filter_by(source_key=source_key).first()
    if src is None:
        raise RuntimeError(f"data_sources 无 {source_key}（先执行 ensure_schema seed）")
    return src


def _write_provenance(db, anime_id: int, field: str, source_key: str, value: str,
                      verified: bool, fetched: datetime):
    src = _ensure_source(db, source_key)
    rec = (db.query(AnimeFieldSource)
           .filter_by(anime_id=anime_id, field_name=field, source_id=src.id).first())
    if rec is None:
        db.add(AnimeFieldSource(
            anime_id=anime_id, field_name=field, source_id=src.id,
            source_value=value, value_hash=_hash(source_key, field, value),
            verified=int(verified), fetched_at=fetched))
    else:
        rec.source_value = value
        rec.value_hash = _hash(source_key, field, value)
        rec.verified = int(verified)
        rec.fetched_at = fetched


def build_plan(db) -> list[dict]:
    """构建 10 部写入计划（dry-run 与 apply 共用）。"""
    desc_b = _load_desc_b()
    plan = []
    for f in _FACTS:
        anime = db.query(Anime).filter(Anime.chinese_title == f["key"]).first()
        if anime is None:
            plan.append({"key": f["key"], "matched": False, "note": "库中未匹配到该 Anime"})
            continue
        entry = {
            "key": f["key"], "anime_id": anime.id, "matched": True,
            "verified": f["verified"], "qid": f["qid"], "semantics": f.get("semantics"),
            "old": {"studio": anime.studio, "episodes": anime.episodes,
                    "status": anime.status, "region": anime.region,
                    "seo_title": anime.seo_title, "description": anime.description},
            "new": {"studio": None, "episodes": None, "status": None, "region": None,
                    "seo_title": None, "description": None},
            "provenance": [],
        }
        if f["verified"]:
            for field in ("studio", "episodes", "status", "region"):
                entry["new"][field] = f[field]
                entry["provenance"].append({"field": field,
                                             "source": "wikidata" if field in ("studio", "episodes")
                                             else "manual",
                                             "verified": 1 if field in ("studio", "episodes") else 0})
            st = _seo_title(f["key"], anime.year, f["semantics"])
            entry["new"]["seo_title"] = st
            if st:
                entry["provenance"].append({"field": "seo_title", "source": "manual",
                                             "verified": 0})
        entry["new"]["description"] = desc_b.get(f["key"])
        if entry["new"]["description"]:
            entry["provenance"].append({"field": "description", "source": "manual",
                                         "verified": 0})
        plan.append(entry)
    return plan

def apply_plan(db, plan: list[dict]) -> dict:
    """写入 Anime 字段 + provenance。返回统计。"""
    stats = {"anime_written": 0, "field_written": 0, "provenance_written": 0,
             "description_written": 0, "seo_title_written": 0, "skipped_no_fact": []}
    fetched = datetime.now(UTC)
    for entry in plan:
        if not entry.get("matched"):
            continue
        anime = db.query(Anime).filter(Anime.chinese_title == entry["key"]).first()
        if anime is None:
            continue
        changed = False
        for field in ("studio", "episodes", "status", "region"):
            val = entry["new"].get(field)
            if val is None:
                continue
            setattr(anime, field, val)
            stats["field_written"] += 1
            changed = True
        if entry["new"].get("seo_title"):
            anime.seo_title = entry["new"]["seo_title"]
            stats["seo_title_written"] += 1
            changed = True
        if entry["new"].get("description") and (anime.description or "").strip() != entry["new"]["description"]:
            anime.description = entry["new"]["description"]
            stats["description_written"] += 1
            changed = True
        if changed:
            stats["anime_written"] += 1
        for p in entry.get("provenance", []):
            val = entry["new"].get(p["field"])
            if val is None:
                continue
            _write_provenance(db, anime.id, p["field"], p["source"], str(val),
                              p["verified"], fetched)
            stats["provenance_written"] += 1
        if not entry["verified"]:
            stats["skipped_no_fact"].append(entry["key"])
    db.commit()
    return stats


def _print_plan(plan: list[dict]) -> None:
    for e in plan:
        if not e.get("matched"):
            print(f"- {e['key']}: 未匹配")
            continue
        tag = "VERIFIED" if e["verified"] else "REVIEW/REJECTED(仅 desc)"
        print(f"- {e['key']} (id={e['anime_id']}) [{tag}]")
        for field in ("studio", "episodes", "status", "region", "seo_title"):
            old, new = e["old"].get(field), e["new"].get(field)
            if new is not None and new != old:
                print(f"    {field}: {old!r} -> {new!r}")
        if e["new"].get("description") and e["new"]["description"] != e["old"]["description"]:
            print(f"    description: {str(e['old']['description'])[:24]!r} -> {str(e['new']['description'])[:30]!r}...")


def main() -> None:
    ap = argparse.ArgumentParser(description="Growth Sprint 2 10 部内容增强试点")
    ap.add_argument("--dry-run", action="store_true", default=True)
    ap.add_argument("--apply", action="store_true", help="写入 DATABASE_URL 指向的库")
    args = ap.parse_args()
    apply = bool(args.apply)
    db = SessionLocal()
    try:
        plan = build_plan(db)
        print(f"[plan] {sum(1 for p in plan if p.get('matched'))} 部匹配")
        _print_plan(plan)
        if apply:
            stats = apply_plan(db, plan)
            print(f"[apply] anime={stats['anime_written']} fields={stats['field_written']} "
                  f"desc={stats['description_written']} seo_title={stats['seo_title_written']} "
                  f"provenance={stats['provenance_written']}")
            print(f"[apply] 非 VERIFIED（仅 desc，无事实字段）: {stats['skipped_no_fact']}")
        else:
            print("[dry-run] 未写入任何数据")
    finally:
        db.close()


if __name__ == "__main__":
    main()
