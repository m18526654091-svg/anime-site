"""AnimeHub Phase 44.5 - entity identity resolution core.

Pure decision functions (no DB, no network) so the matching rules are
unit-testable. The CLI (phase44_5_legacy_resolve.py) feeds DB rows +
optional AniList corroboration into these functions.

Rules (documented, precision over recall):
- `exact` candidates: an English entity whose de-punctuated chinese_title
  equals the legacy title, or whose aliases contain an exact equal item.
  This is the strongest DB-internal cross-language name signal.
- `brand_substring`: chinese_title/aliases merely contain the legacy title
  (usually sequel/movie entries of the same brand). Context only.
- Episode mismatch alone does NOT reject (legacy episode counts are known
  unreliable) and does NOT block a VERIFIED decision; it is recorded in
  `conflicts` so the reviewer still sees it.
- VERIFIED_SAME_ENTITY requires: exactly one exact candidate, year
  agreement (<=2y), no type conflict, and external corroboration with
  agreeing year. Without external corroboration the case is
  MANUAL_REVIEW_REQUIRED, never auto-verified.
"""
from __future__ import annotations

import re

CJK = re.compile(r"[\u4e00-\u9fff]")
KANA = re.compile(r"[\u3040-\u30ff]")
PUNCT = re.compile(
    "[！!？?·・~〜、，,。.‘’'\"\"()（）\\[\\]【】\\-–—\\s]+"
)
MOVIE_MARK = re.compile(
    r"movie|film|\u5267\u573a\u7248|\u5287\u5834\u7248|compilation|\u7dcf\u96c6\u7de8|recap",
    re.I,
)

VERIFIED = "VERIFIED_SAME_ENTITY"
DISTINCT = "REVIEWED_DISTINCT_ENTITY"
MANUAL = "MANUAL_REVIEW_REQUIRED"
UNRESOLVED = "UNRESOLVED"

HIGH = "HIGH"
MEDIUM = "MEDIUM"
LOW = "LOW"
NONE = "NONE"


def de_punct(s: str) -> str:
    """Remove punctuation/whitespace; keep CJK characters intact."""
    return PUNCT.sub("", s or "").strip()


def norm(s: str) -> str:
    return de_punct(s).lower()


def infer_type(title: str) -> str:
    """Infer movie vs tv from the title (no type column exists in DB)."""
    return "movie" if MOVIE_MARK.search(title or "") else "tv"


def is_exact_cn(legacy_title, en_chinese_title, en_aliases) -> bool:
    """Exact cross-language name equality (strong DB signal)."""
    t = norm(legacy_title)
    if not t:
        return False
    if norm(en_chinese_title) == t:
        return True
    return any(norm(a) == t for a in (en_aliases or []))


def is_brand_substring(legacy_title, en_chinese_title, en_aliases) -> bool:
    """True when the legacy title is contained in another name (not equal)."""
    t = norm(legacy_title)
    if not t or len(t) < 2:
        return False
    blob = [norm(en_chinese_title)] + [norm(a) for a in (en_aliases or [])]
    return any(b and t in b and b != t for b in blob)


def years_close(a, b, tol=2) -> bool:
    return bool(a and b and abs(int(a) - int(b)) <= tol)


def _blocking_conflicts(conflicts):
    """Year/type conflicts block auto-verify; episode notes do not."""
    return [c for c in conflicts if not c.startswith("episodes")]


def resolve_entity(legacy, candidates, external=None):
    """Resolve one legacy record against its DB candidates.

    legacy: dict(id,title,year,episodes,franchise,slug)
    candidates: list of dict(id,title,slug,year,episodes,anilist_id,kind)
    external: dict cand_id -> dict(anilist_id,year,episodes,source,status)
    Returns an auditable decision dict.
    """
    lg_year = legacy.get("year")
    exact = [c for c in candidates if c["kind"] == "exact"]
    sub = [c for c in candidates if c["kind"] == "brand_substring"]
    conflicts = []

    def year_conflict(c):
        if lg_year and c.get("year") and not years_close(lg_year, c["year"]):
            conflicts.append(f"year {c['year']} vs legacy {lg_year}")

    def type_conflict(c):
        lt = infer_type(legacy["title"])
        ct = infer_type(c["title"])
        if lt != ct:
            conflicts.append(f"type {ct} vs legacy {lt}")

    def eps_note(c):
        if legacy.get("episodes") and c.get("episodes"):
            lep, cep = int(legacy["episodes"]), int(c["episodes"])
            if abs(lep - cep) > 3 and lep < 40:
                conflicts.append(f"episodes {cep} vs legacy {lep} (legacy may be unreliable)")

    if not exact and not sub:
        return {
            "identity_decision": UNRESOLVED, "confidence": NONE,
            "evidence": ["no candidate / no db name connection"],
            "conflicts": [], "priority": "P3", "recommended_action": "UNRESOLVED",
        }

    if len(exact) == 1:
        c = exact[0]
        year_conflict(c)
        type_conflict(c)
        eps_note(c)
        ext = (external or {}).get(c["id"])
        ext_ok = ext and ext.get("status") == "ok"
        blocking = _blocking_conflicts(conflicts)
        year_agree = years_close(lg_year, c.get("year"))
        if year_agree and not blocking:
            ext_year_agree = bool(ext_ok and years_close(lg_year, ext.get("year")))
            if ext_ok and not ext_year_agree:
                blocking.append(f"external year {ext.get('year')} disagrees with legacy {lg_year}")
            if ext_ok and ext_year_agree:
                return {
                    "identity_decision": VERIFIED, "confidence": MEDIUM,
                    "evidence": [
                        "exact chinese_title/alias equality",
                        "external {src} id={eid} year={ey} agrees".format(
                            src=ext.get("source"), eid=ext.get("anilist_id"), ey=ext.get("year")),
                    ],
                    "conflicts": conflicts, "priority": "P2",
                    "recommended_action": "FUTURE_CONSOLIDATION_CANDIDATE",
                }
            return {
                "identity_decision": MANUAL, "confidence": MEDIUM,
                "evidence": ["single exact candidate; external corroboration missing or disagrees"],
                "conflicts": conflicts or ["external corroboration unavailable"],
                "priority": "P0", "recommended_action": "MANUAL_REVIEW",
            }
        return {
            "identity_decision": MANUAL, "confidence": MEDIUM,
            "evidence": ["single exact candidate with blocking conflicts"],
            "conflicts": conflicts, "priority": "P0" if blocking else "P1",
            "recommended_action": "MANUAL_REVIEW",
        }

    if len(exact) > 1:
        for c in exact[:5]:
            year_conflict(c)
            type_conflict(c)
        return {
            "identity_decision": MANUAL, "confidence": MEDIUM,
            "evidence": [f"{len(exact)} exact candidates - ambiguous"],
            "conflicts": conflicts, "priority": "P0",
            "recommended_action": "MANUAL_REVIEW",
        }

    if len(sub) > 2:
        return {
            "identity_decision": MANUAL, "confidence": LOW,
            "evidence": [f"{len(sub)} brand-substring candidates (mostly sequels/movies)"],
            "conflicts": ["multiple brand candidates - needs franchise/season disambiguation"],
            "priority": "P0", "recommended_action": "MANUAL_REVIEW",
        }
    for c in sub[:3]:
        year_conflict(c)
        type_conflict(c)
    return {
        "identity_decision": MANUAL, "confidence": LOW,
        "evidence": ["brand-substring only (no exact chinese_title/alias equality)"],
        "conflicts": conflicts or ["substring evidence only"],
        "priority": "P1", "recommended_action": "MANUAL_REVIEW",
    }

