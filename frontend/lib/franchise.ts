/**
 * AnimeHub Phase 30: Franchise definitions (18 high-value franchises).
 * 罗列型目录页（区别于 watch-order 的"顺序指引"）。
 * 数据来自数据库条目（关键词匹配），不虚构 chronology/剧情。
 */

export interface FranchiseDef {
  slug: string;
  name: string;
  intro: string;
  /** DB 搜索关键词（title/chinese_title 子串） */
  match: string[];
  /** 分组标签（基于 title 可靠标记） */
  groups: { key: string; label: string; test: (title: string) => boolean }[];
}

const GROUPS = [
  { key: "tv", label: "TV Series & Seasons", test: (t: string) => !/movie|film|剧场版|劇場版/i.test(t) },
  { key: "movie", label: "Movies & Specials", test: (t: string) => /movie|film|剧场版|劇場版/i.test(t) },
];

export const FRANCHISE_DEFS: Record<string, FranchiseDef> = {
  "attack-on-titan": {
    slug: "attack-on-titan",
    name: "Attack on Titan",
    intro: "Attack on Titan is a popular anime franchise spanning multiple seasons, sequels, and movies. This page lists every Attack on Titan anime in our database \u2014 with release years, genres, and direct links to each title. It is a action and dark fantasy series.",
    match: [
      "attack on titan",
      "\u8fdb\u51fb\u7684\u5de8\u4eba",
      "shingeki"
    ],
    groups: GROUPS,
  },
  "my-hero-academia": {
    slug: "my-hero-academia",
    name: "My Hero Academia",
    intro: "My Hero Academia is a popular anime franchise spanning multiple seasons, sequels, and movies. This page lists every My Hero Academia anime in our database \u2014 with release years, genres, and direct links to each title. It is a superhero action series.",
    match: [
      "my hero academia",
      "\u6211\u7684\u82f1\u96c4\u5b66\u9662",
      "\u50d5\u306e\u30d2\u30fc\u30ed\u30fc"
    ],
    groups: GROUPS,
  },
  "rezero": {
    slug: "rezero",
    name: "Re:Zero",
    intro: "Re:Zero is a popular anime franchise spanning multiple seasons, sequels, and movies. This page lists every Re:Zero anime in our database \u2014 with release years, genres, and direct links to each title. It is a isekai fantasy series.",
    match: [
      "re:zero",
      "re zero",
      "re\u4ece\u96f6",
      "re\u5f9e\u96f6",
      "\u5f02\u4e16\u754c\u751f\u6d3b",
      "\u7570\u4e16\u754c\u751f\u6d3b",
      "\u4ece\u96f6\u5f00\u59cb"
    ],
    groups: GROUPS,
  },
  "jujutsu-kaisen": {
    slug: "jujutsu-kaisen",
    name: "Jujutsu Kaisen",
    intro: "Jujutsu Kaisen is a popular anime franchise spanning multiple seasons, sequels, and movies. This page lists every Jujutsu Kaisen anime in our database \u2014 with release years, genres, and direct links to each title. It is a supernatural action series.",
    match: [
      "jujutsu kaisen",
      "\u5492\u672f\u56de\u6218",
      "\u5492\u8853\u8ff4\u6230",
      "\u546a\u8853\u5efb\u6226"
    ],
    groups: GROUPS,
  },
  "one-punch-man": {
    slug: "one-punch-man",
    name: "One-Punch Man",
    intro: "One-Punch Man is a popular anime franchise spanning multiple seasons, sequels, and movies. This page lists every One-Punch Man anime in our database \u2014 with release years, genres, and direct links to each title. It is a action comedy series.",
    match: [
      "one-punch man",
      "one punch man",
      "\u4e00\u62f3\u8d85\u4eba"
    ],
    groups: GROUPS,
  },
  "slime": {
    slug: "slime",
    name: "That Time I Got Reincarnated as a Slime",
    intro: "That Time I Got Reincarnated as a Slime is a popular anime franchise spanning multiple seasons, sequels, and movies. This page lists every That Time I Got Reincarnated as a Slime anime in our database \u2014 with release years, genres, and direct links to each title. It is a isekai fantasy series.",
    match: [
      "slime",
      "\u8f6c\u751f\u53f2\u83b1\u59c6",
      "\u8ee2\u751f\u3057\u305f\u3089\u30b9\u30e9\u30a4\u30e0",
      "\u5173\u4e8e\u6211\u8f6c\u751f"
    ],
    groups: GROUPS,
  },
  "fire-force": {
    slug: "fire-force",
    name: "Fire Force",
    intro: "Fire Force is a popular anime franchise spanning multiple seasons, sequels, and movies. This page lists every Fire Force anime in our database \u2014 with release years, genres, and direct links to each title. It is a action supernatural series.",
    match: [
      "fire force",
      "\u708e\u708e\u6d88\u9632\u961f",
      "\u708e\u708e\u30ce\u6d88\u9632\u968a"
    ],
    groups: GROUPS,
  },
  "gintama": {
    slug: "gintama",
    name: "Gintama",
    intro: "Gintama is a popular anime franchise spanning multiple seasons, sequels, and movies. This page lists every Gintama anime in our database \u2014 with release years, genres, and direct links to each title. It is a action comedy series.",
    match: [
      "gintama",
      "\u94f6\u9b42",
      "\u9280\u9b42"
    ],
    groups: GROUPS,
  },
  "haikyuu": {
    slug: "haikyuu",
    name: "Haikyuu",
    intro: "Haikyuu is a popular anime franchise spanning multiple seasons, sequels, and movies. This page lists every Haikyuu anime in our database \u2014 with release years, genres, and direct links to each title. It is a sports series.",
    match: [
      "haikyuu",
      "\u6392\u7403\u5c11\u5e74",
      "\u30cf\u30a4\u30ad\u30e5\u30fc"
    ],
    groups: GROUPS,
  },
  "golden-kamuy": {
    slug: "golden-kamuy",
    name: "Golden Kamuy",
    intro: "Golden Kamuy is a popular anime franchise spanning multiple seasons, sequels, and movies. This page lists every Golden Kamuy anime in our database \u2014 with release years, genres, and direct links to each title. It is a historical adventure series.",
    match: [
      "golden kamuy",
      "\u9ec4\u91d1\u795e\u5a01",
      "\u30b4\u30fc\u30eb\u30c7\u30f3\u30ab\u30e0\u30a4"
    ],
    groups: GROUPS,
  },
  "monogatari": {
    slug: "monogatari",
    name: "Monogatari",
    intro: "Monogatari is a popular anime franchise spanning multiple seasons, sequels, and movies. This page lists every Monogatari anime in our database \u2014 with release years, genres, and direct links to each title. It is a character-driven fantasy series.",
    match: [
      "monogatari",
      "\u7269\u8bed",
      "\u7269\u8a9e"
    ],
    groups: GROUPS,
  },
  "bleach": {
    slug: "bleach",
    name: "Bleach",
    intro: "Bleach is a popular anime franchise spanning multiple seasons, sequels, and movies. This page lists every Bleach anime in our database \u2014 with release years, genres, and direct links to each title. It is a action adventure series.",
    match: [
      "bleach",
      "\u6b7b\u795e",
      "\u5343\u5e74\u8840\u6218",
      "\u5343\u5e74\u8840\u6226"
    ],
    groups: GROUPS,
  },
  "spy-family": {
    slug: "spy-family",
    name: "Spy x Family",
    intro: "Spy x Family is a popular anime franchise spanning multiple seasons, sequels, and movies. This page lists every Spy x Family anime in our database \u2014 with release years, genres, and direct links to each title. It is a comedy slice of life series.",
    match: [
      "spy x family",
      "spy family",
      "\u95f4\u8c0d\u8fc7\u5bb6\u5bb6",
      "\u30b9\u30d1\u30a4\u30d5\u30a1\u30df\u30ea\u30fc"
    ],
    groups: GROUPS,
  },
  "frieren": {
    slug: "frieren",
    name: "Frieren",
    intro: "Frieren is a popular anime franchise spanning multiple seasons, sequels, and movies. This page lists every Frieren anime in our database \u2014 with release years, genres, and direct links to each title. It is a fantasy adventure series.",
    match: [
      "frieren",
      "\u846c\u9001\u7684\u8299\u8389\u83b2",
      "\u846c\u9001\u306e\u30d5\u30ea\u30fc\u30ec\u30f3"
    ],
    groups: GROUPS,
  },
  "mushoku-tensei": {
    slug: "mushoku-tensei",
    name: "Mushoku Tensei",
    intro: "Mushoku Tensei is a popular anime franchise spanning multiple seasons, sequels, and movies. This page lists every Mushoku Tensei anime in our database \u2014 with release years, genres, and direct links to each title. It is a isekai fantasy series.",
    match: [
      "mushoku tensei",
      "\u65e0\u804c\u8f6c\u751f",
      "\u7121\u8077\u8ee2\u751f"
    ],
    groups: GROUPS,
  },
  "overlord": {
    slug: "overlord",
    name: "Overlord",
    intro: "Overlord is a popular anime franchise spanning multiple seasons, sequels, and movies. This page lists every Overlord anime in our database \u2014 with release years, genres, and direct links to each title. It is a isekai dark fantasy series.",
    match: [
      "overlord",
      "\u4e0d\u6b7b\u8005\u4e4b\u738b",
      "\u30aa\u30fc\u30d0\u30fc\u30ed\u30fc\u30c9"
    ],
    groups: GROUPS,
  },
  "one-piece": {
    slug: "one-piece",
    name: "One Piece",
    intro: "One Piece is a popular anime franchise spanning multiple seasons, sequels, and movies. This page lists every One Piece anime in our database \u2014 with release years, genres, and direct links to each title. It is a adventure action series.",
    match: [
      "one piece",
      "\u6d77\u8d3c\u738b",
      "\u822a\u6d77\u738b"
    ],
    groups: GROUPS,
  },
  "fate": {
    slug: "fate",
    name: "Fate",
    intro: "Fate is a popular anime franchise spanning multiple seasons, sequels, and movies. This page lists every Fate anime in our database \u2014 with release years, genres, and direct links to each title. It is a action fantasy series.",
    match: [
      "fate",
      "\u547d\u8fd0\u4e4b\u591c",
      "\u4f0a\u8389\u96c5",
      "\u9b54\u6cd5\u5c11\u5973\u4f0a\u8389\u96c5"
    ],
    groups: GROUPS,
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
