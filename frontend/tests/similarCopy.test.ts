import { test } from "node:test";
import assert from "node:assert/strict";
import { formatGenres, genreToEnglish, splitGenres } from "../lib/genreLabels";
import {
  buildLedeIntro,
  buildReasonFallback,
  diversifyFranchises,
  MAX_PER_FRANCHISE,
} from "../lib/similarCopy";

// --- A. No raw Chinese genre leakage on English copy ---

test("formatGenres maps Chinese genres to English, never leaks Chinese", () => {
  assert.equal(formatGenres("动作/剧情/奇幻"), "Action, Drama, Fantasy");
  assert.equal(formatGenres("悬疑/心理"), "Mystery, Psychological");
  const out = formatGenres("动作/剧情/奇幻");
  assert.ok(!/[\u4e00-\u9fff]/.test(out), "output must not contain Chinese");
});

test("formatGenres drops unknown tokens (safe fallback, no hybrid phrases)", () => {
  // 未知 token 混合可映射 token：只输出英文
  assert.equal(formatGenres("动作/完全未知标签"), "Action");
  // 全部未知：fallback
  assert.equal(formatGenres("完全未知"), "anime");
  assert.equal(formatGenres(""), "anime");
  assert.equal(formatGenres(undefined), "anime");
  assert.equal(formatGenres(null), "anime");
  const out = formatGenres("完全未知");
  assert.ok(!/[\u4e00-\u9fff]/.test(out), "fallback must not contain Chinese");
});

test("formatGenres dedupes English labels (动作/热血 -> single Action) and caps at max", () => {
  assert.equal(formatGenres("动作/热血/战斗"), "Action");
  assert.equal(formatGenres("搞笑/喜剧/日常", "anime", 2), "Comedy, Slice of Life");
});

test("genreToEnglish and splitGenres behave", () => {
  assert.deepEqual(splitGenres("动作,剧情 奇幻/悬疑"), ["动作", "剧情", "奇幻", "悬疑"]);
  assert.deepEqual(genreToEnglish("动作,剧情"), ["Action", "Drama"]);
  assert.deepEqual(genreToEnglish("未知"), []);
  assert.deepEqual(genreToEnglish(null), []);
});

// --- B/C/D. Lede uses only factual available fields, no fabrication ---

test("buildLedeIntro uses only present facts (genre/year/episodes/studio)", () => {
  const lede = buildLedeIntro({
    title: "Monster",
    chinese_title: "怪物",
    genre: "悬疑/心理",
    year: 2004,
    episodes: 74,
    studio: "MADHOUSE",
  });
  assert.equal(
    lede,
    "Monster is a Mystery, Psychological title with 74 episodes from 2004 by MADHOUSE",
  );
});

test("buildLedeIntro omits missing fields", () => {
  const lede = buildLedeIntro({ title: "AoT", genre: "动作", year: 2013 });
  assert.equal(lede, "AoT is a Action title from 2013");
});

test("buildLedeIntro never leaks non-ASCII studio names", () => {
  const zh = buildLedeIntro({ title: "DBZ", genre: "动作", studio: "东映动画" });
  assert.ok(!/[\u4e00-\u9fff]/.test(zh), "Chinese studio dropped");
  assert.equal(zh, "DBZ is a Action title");
  const en = buildLedeIntro({ title: "Monster", genre: "心理", studio: "MADHOUSE" });
  assert.ok(en.endsWith("by MADHOUSE"), "ASCII studio kept");
});

test("buildLedeIntro falls back without inventing facts when nothing is available", () => {
  assert.equal(buildLedeIntro({ title: "X" }), "If you enjoyed X");
  // unknown genres are dropped; only real episode count is used; no Chinese
  const lede2 = buildLedeIntro({ title: "X", genre: "未知标签", episodes: 12 });
  assert.ok(!/[\u4e00-\u9fff]/.test(lede2), "no Chinese in lede");
  assert.ok(lede2.includes("12 episodes"), "uses only factual episode count");
  assert.ok(!lede2.includes("未知"), "unknown genre never rendered");
});

// --- E. Reason fallback: English or neutral, never Chinese ---

test("buildReasonFallback uses English genres when mappable", () => {
  assert.equal(
    buildReasonFallback("搞笑/日常"),
    "It shares the Comedy, Slice of Life qualities you enjoyed.",
  );
  assert.equal(buildReasonFallback("未知"), "It shares similar themes and storytelling.");
  assert.equal(buildReasonFallback(undefined), "It shares similar themes and storytelling.");
});

// --- F/G. Presentation-level franchise diversity ---

interface Sim {
  title?: string;
  chinese_title?: string;
}

const AOT = (t: string): Sim => ({ title: t, chinese_title: t });
const NON = (i: number): Sim => ({ title: `Other Anime ${i}`, chinese_title: `其他${i}` });

test("diversifyFranchises caps same-franchise entries to MAX_PER_FRANCHISE", () => {
  const candidates: Sim[] = [
    ...["Attack on Titan", "Attack on Titan Season 2", "Attack on Titan Season 3", "Attack on Titan OVA"].map(AOT),
    NON(1),
    NON(2),
    NON(3),
    NON(4),
    NON(5),
    NON(6),
  ];
  const out = diversifyFranchises(candidates, 8);
  const aotCount = out.filter((c) => matchKey(c)).length;
  assert.equal(out.length, 8);
  assert.ok(aotCount <= MAX_PER_FRANCHISE, `AoT entries capped at ${MAX_PER_FRANCHISE}`);
  // order preserved: first two are still the two highest-ranked AoT entries
  assert.equal(out[0].title, "Attack on Titan");
  assert.equal(out[1].title, "Attack on Titan Season 2");
});

function matchKey(c: Sim): boolean {
  const title = `${c.title ?? ""} ${c.chinese_title ?? ""}`.toLowerCase();
  return title.includes("attack on titan") || title.includes("进击的巨人") || title.includes("shingeki");
}

test("diversifyFranchises never caps non-franchise titles and returns target count", () => {
  const candidates = Array.from({ length: 12 }, (_, i) => NON(i));
  const out = diversifyFranchises(candidates, 8);
  assert.equal(out.length, 8);
});

test("diversifyFranchises preserves ranked order", () => {
  const candidates: Sim[] = [AOT("Attack on Titan"), NON(0), AOT("Attack on Titan Season 2"), NON(1)];
  const out = diversifyFranchises(candidates, 8);
  assert.deepEqual(out.map((c) => c.title), ["Attack on Titan", "Other Anime 0", "Attack on Titan Season 2", "Other Anime 1"]);
});

test("diversifyFranchises returns fewer when candidates run out (no phantom fill)", () => {
  const out = diversifyFranchises([AOT("Attack on Titan"), AOT("Attack on Titan Season 2"), AOT("Attack on Titan Season 3")], 8);
  assert.equal(out.length, 2);
});

// --- H. Technical SEO surface (rendered checks are covered by SSR audit) ---
// --- I. Global English content unchanged: AnimeDetailClient still uses GENRE_EN ---
test("GENRE_EN mapping retained for detail page (single source of truth)", () => {
  const { GENRE_EN } = require("../lib/genreLabels") as typeof import("../lib/genreLabels");
  assert.equal(GENRE_EN["动作"], "Action");
  assert.equal(GENRE_EN["超自然"], "Supernatural");
});
