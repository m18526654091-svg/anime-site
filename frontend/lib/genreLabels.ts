/**
 * Phase 44.1: shared Chinese -> English genre label mapping + safe helpers.
 *
 * Single source of truth for title-case genre labels (English-facing pages).
 * Extracted from components/AnimeDetailClient so Server Components (e.g. the
 * Similar Anime page) can render the same English labels without duplicating
 * the mapping or leaking raw Chinese genre strings into English copy.
 *
 * Leakage policy: tokens without an English mapping are DROPPED by
 * genreToEnglish/formatGenres. English-facing pages must never fall back to
 * raw Chinese genre text.
 */

export const GENRE_EN: Record<string, string> = {
  动作: "Action", 热血: "Action", 战斗: "Action", 奇幻: "Fantasy", 异世界: "Isekai",
  科幻: "Sci-Fi", 机甲: "Mecha", 机战: "Mecha", 恋爱: "Romance", 校园: "School",
  日常: "Slice of Life", 治愈: "Healing", 悬疑: "Mystery", 推理: "Mystery",
  心理: "Psychological", 恐怖: "Horror", 惊悚: "Thriller", 搞笑: "Comedy",
  喜剧: "Comedy", 冒险: "Adventure", 剧情: "Drama", 历史: "Historical",
  时代剧: "Historical", 运动: "Sports", 音乐: "Music", 青春: "Youth",
  战争: "War", 侦探: "Detective", 黑暗: "Dark", 魔法: "Magic",
  超自然: "Supernatural", 异能: "Super Power", 超能力: "Super Power",
  偶像: "Idol", 博弈: "Gambling", 生存: "Survival", 竞技: "Competitive",
  美食: "Cooking", 格斗: "Martial Arts", 军事: "Military", 魔法少女: "Magical Girl",
  黑帮: "Mafia", 职场: "Workplace", 福利: "Ecchi",
};

/** Split a DB genre string (Chinese, '/' / '，' / ',' / whitespace separated) into tokens. */
export function splitGenres(genre?: string | null): string[] {
  if (!genre) return [];
  return genre
    .split(/[/，,、\s]+/)
    .map((g) => g.trim())
    .filter(Boolean);
}

/**
 * Map a genre string to English labels.
 * Unmappable tokens are dropped — raw Chinese never leaks into English copy.
 * Returns an empty array when nothing can be mapped.
 */
export function genreToEnglish(genre?: string | null): string[] {
  const seen = new Set<string>();
  return splitGenres(genre)
    .map((g) => GENRE_EN[g])
    .filter((v): v is string => Boolean(v))
    .filter((v) => (seen.has(v) ? false : (seen.add(v), true)));
}

/**
 * Format genres as a comma-joined English phrase.
 * `fallback` is used only when NO token maps to English (never a Chinese token).
 * `max` caps the number of labels (e.g. 3) for compact copy.
 */
export function formatGenres(genre?: string | null, fallback = "anime", max?: number): string {
  const list = genreToEnglish(genre);
  const slice = typeof max === "number" && list.length > max ? list.slice(0, max) : list;
  return slice.join(", ") || fallback;
}
