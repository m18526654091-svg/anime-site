// AnimeHub Phase 4: Watch Order franchise definitions.
// 顺序基于发行顺序与剧情逻辑人工定义（非自动生成），数据从 DB 按关键词匹配。

export interface WatchStep {
  /** DB 条目匹配关键词（title 或 chinese_title 子串） */
  match: string[];
  /** 顺序说明 */
  note: string;
}

export interface Franchise {
  slug: string;
  name: string;
  intro: string;
  steps: WatchStep[];
}

export const FRANCHISES: Record<string, Franchise> = {
  "attack-on-titan": {
    slug: "attack-on-titan",
    name: "Attack on Titan",
    intro:
      "Attack on Titan has a multi-season structure with a final arc split into parts. To follow the story in the correct order, watch the seasons below as they were released.",
    steps: [
      { match: ["attack on titan", "进击的巨人", "shingeki"], note: "The original 2013 season — where the story begins." },
      { match: ["season 2", "second season"], note: "Direct continuation of the first season." },
      { match: ["season 3"], note: "The political arc that reshapes the story." },
      { match: ["final season"], note: "The beginning of the final arc." },
      { match: ["final chapters"], note: "The concluding episodes — watch after all prior seasons." },
    ],
  },
  naruto: {
    slug: "naruto",
    name: "Naruto",
    intro:
      "Naruto's story spans three main series. Start with the original, move to Shippuden, then watch Boruto for the next generation.",
    steps: [
      { match: ["naruto", "火影忍者"], note: "The original Naruto series (2002)." },
      { match: ["shippuden", "疾风传"], note: "The direct sequel covering the main story." },
      { match: ["boruto", "博人传"], note: "Next-generation continuation set after the main saga." },
    ],
  },
  "code-geass": {
    slug: "code-geass",
    name: "Code Geass",
    intro:
      "Code Geass has two TV seasons plus movie continuations. Watch the TV series first, then the movies for the modern timeline.",
    steps: [
      { match: ["code geass", "反叛的鲁路修", "叛逆的鲁路修", "鲁路修"], note: "Season 1 — where the story begins." },
      { match: ["r2", "第二季"], note: "Season 2 — the direct continuation." },
      { match: ["akito", "阿基德"], note: "A side story set in an alternate timeline." },
      { match: ["re;surrection", "复活"], note: "The movie sequel continuing after Season 2." },
    ],
  },
  "one-piece": {
    slug: "one-piece",
    name: "One Piece",
    intro:
      "One Piece is one long continuous story. Watch the TV series in release order; the movies are optional side adventures set within the timeline.",
    steps: [
      { match: ["one piece", "海贼王"], note: "The main TV series — watch in order." },
      { match: ["film red", "剧场版"], note: "Standalone movies — watch anytime as side stories." },
      { match: ["fan letter", "粉丝来信"], note: "A special episode celebrating the series." },
    ],
  },
  "dragon-ball": {
    slug: "dragon-ball",
    name: "Dragon Ball",
    intro:
      "Dragon Ball spans multiple generations. Start with the original, continue with Z, and decide between GT and Super for the later storylines.",
    steps: [
      { match: ["dragon ball", "龙珠"], note: "The original series (1986) — Goku's childhood." },
      { match: ["dragon ball z", "龙珠z"], note: "The most iconic arc — from the Saiyan saga onward." },
      { match: ["dragon ball super", "龙珠超"], note: "The modern continuation after Z." },
      { match: ["dragon ball gt", "龙珠gt"], note: "An alternate ending — optional viewing." },
    ],
  },
  monogatari: {
    slug: "monogatari",
    name: "Monogatari",
    intro:
      "Monogatari is famous for its deliberately unusual episode order. The safest approach for a first watch is the original broadcast (aired) order, which matches the order the author and studio intended.",
    steps: [
      { match: ["化物语", "bakemonogatari", "monogatari"], note: "Start with Bakemonogatari (2009) — where the story begins." },
      { match: ["物语系列第二季", "セカンドシーズン", "second season", "monogatari series second"], note: "Monogatari Series Second Season (2013) continues the timeline." },
      { match: ["凭物语", "tsukimonogatari"], note: "Tsukimonogatari (2014) — a short but important 'ghost' arc." },
      { match: ["终物语", "owarimonogatari"], note: "Owarimonogatari (2015) advances the main story." },
      { match: ["历物语", "koyomimonogatari"], note: "Koyomimonogatari (2016) — 12 short episodes that bridge arcs." },
      { match: ["伤物语", "kizumonogatari"], note: "Kizumonogatari films (2016-2017) — the prequel trilogy, best watched after the earlier seasons." },
      { match: ["终物语下", "owarimonogatari second", "終物語（下）"], note: "Owarimonogatari Second Season (2017) — the final part of the main story." },
      { match: ["终物语续", "zoku owarimonogatari", "終物語続"], note: "Zoku Owarimonogatari (2019) — the aftermath." },
      { match: ["off season", "off monster", "off&monster", "オフ"], note: "OFF & MONSTER Season (2024) — the newest chapter." },
    ],
  },
  bleach: {
    slug: "bleach",
    name: "Bleach",
    intro:
      "Bleach's story is straightforward in the main arcs, but the anime includes filler arcs you can safely skip. The Thousand-Year Blood War (TYBW) is split into multiple cours — follow the order below.",
    steps: [
      { match: ["bleach", "死神"], note: "Start with the original Bleach (2004) TV series." },
      { match: ["thousand-year blood war", "千年血战"], note: "The final arc — Thousand-Year Blood War (2022)." },
      { match: ["separation", "诀别", "訣別"], note: "TYBW Part 2: The Separation (2023)." },
      { match: ["conflict", "相克", "相剋"], note: "TYBW Part 3: The Conflict (2024)." },
      { match: ["calamity", "祸进", "禍進"], note: "TYBW Part 4: The Calamity (2026, ongoing)." },
    ],
  },
  rezero: {
    slug: "rezero",
    name: "Re:Zero",
    intro:
      "Re:Zero has a single continuous timeline across seasons plus an optional prequel movie. Watch the seasons in release order — the movie is a side story, not required for the main plot.",
    steps: [
      { match: ["从零开始的异世界生活", "異世界生活", "re:zero", "re zero"], note: "Start with the 2016 first season." },
      { match: ["冰结之绊", "frozen bond"], note: "Re:Zero Movie: The Frozen Bond (2019) — optional prequel." },
      { match: ["从零开始的异世界生活第二季", "2nd season", "異世界生活 2nd"], note: "Season 2 (2020) — the Sanctuary arc." },
      { match: ["part 2", "part2"], note: "Season 2 Part 2 (2021) — continues the Sanctuary arc." },
      { match: ["从零开始的异世界生活第三季", "third season", "異世界生活 3"], note: "Season 3 (2024)." },
      { match: ["从零开始的异世界生活第四季", "4th season", "異世界生活 4"], note: "Season 4 (2026) — the newest season." },
    ],
  },
};

export const WATCH_ORDER_FRANCHISES = Object.keys(FRANCHISES);

/**
 * 判断一部动漫是否属于某个 watch-order 系列（基于 title/chinese_title 关键词匹配）。
 * 命中时返回 franchise slug，否则返回 null。供详情页条件内链使用。
 */
export function matchWatchOrderFranchise(
  title?: string | null,
  chineseTitle?: string | null
): string | null {
  const haystack = [title || "", chineseTitle || ""]
    .join(" ")
    .toLowerCase()
    .trim();
  if (!haystack) return null;
  for (const slug of WATCH_ORDER_FRANCHISES) {
    const fr = FRANCHISES[slug];
    const matched = fr.steps.some((step) =>
      step.match.some((kw) => haystack.includes(kw.toLowerCase()))
    );
    if (matched) return slug;
  }
  return null;
}

