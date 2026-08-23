"""Stage 10-C 收尾测试：backfill_external_ids 安全性最小测试。

覆盖：
- A 高置信 → 可进入 apply
- B → 不进入 apply
- ambiguous → 不进入 apply
- conflict（同 anilist_id/mal_id 分配给不同 Anime）→ 不自动写入
- 已有任一 ID → 不覆盖
- dry-run → 数据库零修改

只读安全：测试使用临时 SQLite 库（不碰正式库），无网络依赖。
用法（在 backend 目录）:
    .venv\\Scripts\\python -m scripts._test_backfill_external_ids
"""
from __future__ import annotations

import os
import sys
import tempfile
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import sqlalchemy as sa  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from app.database import Base  # noqa: E402
from app.models import Anime  # noqa: E402

import scripts.backfill_external_ids as mod  # noqa: E402


class FakeProvider:
    """按查询词返回预设候选，复用 provider 接口形状（_query_words/_fetch_candidates/_score/_title_score）。"""

    def __init__(self, cand_map):
        self.cand_map = cand_map

    def _query_words(self, title, chinese_title):
        key = (title or chinese_title or "").strip()
        return [key] if key else []

    def _fetch_candidates(self, q):
        return [dict(c) for c in self.cand_map.get(q, [])]

    def _score(self, q, cand, year):
        return cand.get("score", 0)

    def _title_score(self, q, cand):
        return cand.get("tscore", 100)


def test_classify():
    p = FakeProvider({})
    anime = SimpleNamespace(year=2013, id=1)

    # A：score>=82 + 年份一致 + 标题强匹配
    cands = [{"id": 10, "idMal": 100, "score": 95.0, "seasonYear": 2013, "query": "进击的巨人", "tscore": 100}]
    assert mod.classify(p, anime, cands)[0] == "A", "A 级应判定"

    # B：60<=score<82
    cands = [{"id": 20, "score": 70.0, "seasonYear": 2013, "query": "q", "tscore": 100}]
    assert mod.classify(p, anime, cands)[0] == "B", "B 级应判定"

    # C：score<60
    cands = [{"id": 30, "score": 30.0, "query": "q"}]
    assert mod.classify(p, anime, cands)[0] == "C", "C 级应判定"

    # ambiguous：top1 与 top2 差 <= 5 → B
    cands = [
        {"id": 40, "score": 95.0, "query": "q", "tscore": 100},
        {"id": 41, "score": 93.0, "query": "q", "tscore": 100},
    ]
    conf, reason, _ = mod.classify(p, anime, cands)
    assert conf == "B" and "ambiguous" in reason, "ambiguous 应进入 B"

    # 无候选 → C
    assert mod.classify(p, anime, [])[0] == "C", "无候选应为 C"

    print("test_classify PASS（A/B/C/ambiguous/无候选）")


def test_main_safety():
    tmp = tempfile.mktemp(suffix=".db")
    eng = sa.create_engine(f"sqlite:///{tmp}")
    Base.metadata.create_all(eng)
    S = sessionmaker(bind=eng)
    db = S()
    # 记录：
    #  id=1 无ID + A 候选；id=2 无ID + B 候选；id=3 无ID + ambiguous
    #  id=4 无ID + A 候选(占用 id=400)；id=5 无ID + A 候选(与 id=4 冲突)
    #  id=6 已有 anilist_id=999/mal_id=888（不应被覆盖）
    db.add_all(
        [
            Anime(id=1, title="A1", chinese_title="A1", year=2013),
            Anime(id=2, title="B1", chinese_title="B1", year=2013),
            Anime(id=3, title="AMB", chinese_title="AMB", year=2013),
            Anime(id=4, title="CONF1", chinese_title="CONF1", year=2013),
            Anime(id=5, title="CONF2", chinese_title="CONF2", year=2013),
            Anime(id=6, title="HAVE", chinese_title="HAVE", year=2013, anilist_id=999, mal_id=888),
        ]
    )
    db.commit()
    db.close()

    cand_map = {
        "A1": [{"id": 100, "idMal": 1000, "score": 95.0, "seasonYear": 2013, "query": "A1", "tscore": 100}],
        "B1": [{"id": 200, "idMal": 2000, "score": 70.0, "seasonYear": 2013, "query": "B1", "tscore": 100}],
        "AMB": [
            {"id": 300, "idMal": 3000, "score": 95.0, "seasonYear": 2013, "query": "AMB", "tscore": 100},
            {"id": 301, "idMal": 3001, "score": 93.0, "seasonYear": 2013, "query": "AMB", "tscore": 100},
        ],
        "CONF1": [{"id": 400, "idMal": 4000, "score": 95.0, "seasonYear": 2013, "query": "CONF1", "tscore": 100}],
        "CONF2": [{"id": 400, "idMal": 4000, "score": 95.0, "seasonYear": 2013, "query": "CONF2", "tscore": 100}],
    }

    # ---- dry-run：数据库零修改（快照对比）----
    with patch.object(mod, "SessionLocal", lambda: S()), patch.object(
        mod, "AniListProvider", lambda: FakeProvider(cand_map)
    ):
        sys.argv = ["backfill_external_ids", "--limit", "10"]
        mod.main()
    db = S()
    rows_after = {r.id: (r.anilist_id, r.mal_id) for r in db.query(Anime).all()}
    # 待处理的 id 1-5（无 ID）dry-run 后仍应全 NULL
    for i in range(1, 6):
        assert rows_after[i] == (None, None), f"dry-run 不应写库 id={i}: {rows_after[i]}"
    # 已有 ID 的 id=6 保持原值
    assert rows_after[6] == (999, 888), f"已有 ID 不应被改动 id=6: {rows_after[6]}"
    db.close()
    print("dry-run 数据库零修改 PASS")

    # ---- apply：仅 A 级无冲突写入 ----
    with patch.object(mod, "SessionLocal", lambda: S()), patch.object(
        mod, "AniListProvider", lambda: FakeProvider(cand_map)
    ):
        sys.argv = ["backfill_external_ids", "--apply", "--limit", "10"]
        mod.main()
    db = S()
    rows = {r.id: r for r in db.query(Anime).all()}
    assert rows[1].anilist_id == 100 and rows[1].mal_id == 1000, "A 级应写入"
    assert rows[2].anilist_id is None, "B 级不应写入"
    assert rows[3].anilist_id is None, "ambiguous 不应写入"
    assert rows[4].anilist_id == 400, "CONF1（先占用）应写入"
    assert rows[5].anilist_id is None, "CONF2（ID conflict）不应写入"
    assert rows[6].anilist_id == 999 and rows[6].mal_id == 888, "已有 ID 不应覆盖"
    db.close()
    try:
        os.remove(tmp)
    except OSError:
        pass  # SQLite 文件锁：临时文件由系统清理，不影响断言
    print("apply 安全规则 PASS（A 写入 / B·ambiguous·conflict 不写 / 已有 ID 不覆盖）")


if __name__ == "__main__":
    test_classify()
    test_main_safety()
    print("\nALL TESTS PASS")
