/**
 * Phase 44.1: Similar Anime page copy helpers.
 * Pure functions (no React) so the lede/franchise-diversity logic is testable
 * with node --test and shared only by the Similar page.
 *
 * Lede facts are strictly limited to fields actually available for the anime
 * (genre/year/episodes/studio) — nothing semantic is invented.
 */

import { formatGenres } from "./genreLabels";
import { matchFranchise } from "./franchise";

export interface LedeSource {
  title?: string;
  chinese_title?: string;
  genre?: string;
  year?: number | null;
  episodes?: number | null;
  studio?: string;
}

/** Max same-franchise entries shown on a Similar page (presentation rule). */
export const MAX_PER_FRANCHISE = 2;

/** Build the lede's first sentence from factual fields only. */
export function buildLedeIntro(anime: LedeSource): string {
  const name = anime.title || anime.chinese_title || "this anime";
  const genreLabel = formatGenres(anime.genre, "", 3);
  const bits: string[] = [];
  if (genreLabel) bits.push(`a ${genreLabel} title`);
  if (anime.episodes && anime.episodes > 0) {
    bits.push(`with ${anime.episodes} episode${anime.episodes > 1 ? "s" : ""}`);
  }
  if (anime.year) bits.push(`from ${anime.year}`);
  const studio = (anime.studio || "").trim();
  // Studio names may be raw Chinese in the DB; never leak CJK into English copy.
  if (studio && /^[\x00-\x7F]+$/.test(studio)) bits.push(`by ${studio}`);
  if (!bits.length) return `If you enjoyed ${name}`;
  return `${name} is ${bits.join(" ")}`;
}

/** Reason fallback when the API supplies no reason: English genres or neutral text. */
export function buildReasonFallback(genre?: string): string {
  const en = formatGenres(genre, "", 2);
  return en ? `It shares the ${en} qualities you enjoyed.` : "It shares similar themes and storytelling.";
}

/**
 * Presentation-level franchise diversity: keep the ranked candidate order but
 * cap same-franchise entries so one franchise does not dominate the visible
 * set. Non-franchise titles are never capped. Stored data / scores untouched.
 */
export function diversifyFranchises<T extends { title?: string; chinese_title?: string }>(
  candidates: T[],
  target: number,
): T[] {
  const seen = new Map<string, number>();
  const visible: T[] = [];
  for (const c of candidates) {
    const key = matchFranchise(c.title ?? "", c.chinese_title) ?? "none";
    const count = seen.get(key) ?? 0;
    if (key !== "none" && count >= MAX_PER_FRANCHISE) continue;
    seen.set(key, count + 1);
    visible.push(c);
    if (visible.length >= target) break;
  }
  return visible;
}
