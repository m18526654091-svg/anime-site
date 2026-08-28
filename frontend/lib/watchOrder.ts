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
};

export const WATCH_ORDER_FRANCHISES = Object.keys(FRANCHISES);
