/**
 * AnimeHub Phase 9: Franchise definitions.
 * Fate franchise: 罗列型目录页（区别于 watch-order 的"顺序指引"）。
 * 数据来自数据库条目（关键词匹配），不虚构 chronology。
 */

export interface FranchiseDef {
  slug: string;
  name: string;
  intro: string;
  /** DB 搜索关键词（title/chinese_title/slug 子串） */
  match: string[];
  /** 分组标签（用于目录分组，基于可靠 title 关键词） */
  groups: { key: string; label: string; test: (title: string) => boolean }[];
}

const FATE_GROUPS = [
  { key: "stay-night", label: "Fate/stay night (Main Line)", test: (t: string) => /stay night|ubw|heaven's feel|天之杯|无限剑制/i.test(t) },
  { key: "zero", label: "Fate/Zero (Prequel)", test: (t: string) => /fate\/zero|fate zero/i.test(t) },
  { key: "spin-off", label: "Spin-offs & Side Stories", test: (_t: string) => true },
];

export const FRANCHISE_DEFS: Record<string, FranchiseDef> = {
  fate: {
    slug: "fate",
    name: "Fate",
    intro:
      "Fate is a sprawling franchise built around the Holy Grail War — mages summon legendary heroes (Servants) to battle for a wish-granting artifact. The anime spans multiple timelines: the stay night series, the Zero prequel, and several spin-offs set in alternate worlds. This page lists every Fate anime in our database, grouped by timeline. Viewing order is intentionally left open — Fate's timeline is debated by fans, so we present the works rather than forcing a single sequence.",
    match: [
      "fate/stay night",
      "fate/zero",
      "fate kaleid",
      "fate/apocrypha",
      "fate/extra",
      "fate/strange fake",
      "命运之夜",
      "魔法少女伊莉雅",
    ],
    groups: FATE_GROUPS,
  },
};

export const FRANCHISE_SLUGS = Object.keys(FRANCHISE_DEFS);

/** 判断一部动漫是否属于某个 franchise（基于 title/chinese_title 匹配） */
export function matchFranchise(
  title?: string | null,
  chineseTitle?: string | null
): string | null {
  const haystack = [title || "", chineseTitle || ""].join(" ").toLowerCase().trim();
  if (!haystack) return null;
  for (const slug of FRANCHISE_SLUGS) {
    const def = FRANCHISE_DEFS[slug];
    if (def.match.some((kw) => haystack.includes(kw.toLowerCase()))) return slug;
  }
  return null;
}
