/**
 * Season 索引质量工具（Final SEO Deployment）。
 *
 * 问题：production 120 的 month 字段全空，后端 season 筛选「month 空保留该年全部作品」，
 * 导致同一年的 spring/summer/autumn/winter 四个 /season/{year}/{season} 页面
 * 展示完全相同的 Anime ID 集合 → 重复页面（浪费 crawl budget）。
 *
 * 规则：
 * - 若某季的 Anime ID 集合与同年另一季完全相同 → 该季页冗余 → noindex + 不进 sitemap。
 * - 有独立内容的 season → 保持 index + canonical。
 */
import { fetchAnimeByFilter } from "./api";

export const SEASONS = ["spring", "summer", "autumn", "winter"] as const;

async function seasonIds(year: number, season: string): Promise<number[]> {
  const ids: number[] = [];
  let page = 1;
  for (;;) {
    const data = await fetchAnimeByFilter({ year, season }, page, 100);
    ids.push(...data.items.map((a) => a.id));
    if (page >= (data.pages || 1) || data.items.length === 0) break;
    page++;
  }
  return Array.from(new Set(ids));
}

function sameSet(a: number[], b: number[]): boolean {
  if (a.length === 0 || a.length !== b.length) return false;
  const sortedA = [...a].sort((x, y) => x - y);
  const sortedB = [...b].sort((x, y) => x - y);
  return sortedA.every((id, i) => id === sortedB[i]);
}

/** 该 season 页是否冗余（与同年另一季 ID 集合完全相同）。 */
export async function isSeasonRedundant(year: number, season: string): Promise<boolean> {
  if (!SEASONS.includes(season as (typeof SEASONS)[number])) return false;
  let mine: number[] = [];
  try {
    mine = await seasonIds(year, season);
  } catch {
    return false;
  }
  if (mine.length === 0) return true; // 空季度 → 不索引（sitemap 也由 filterRedundantSeasons 排除）
  for (const other of SEASONS) {
    if (other === season) continue;
    try {
      if (sameSet(mine, await seasonIds(year, other))) return true;
    } catch {
      continue;
    }
  }
  return false;
}

/** 过滤冗余 season 组合（按年分组拉取，避免 N×4 次请求）。 */
export async function filterRedundantSeasons(
  combos: { year: number; season: string }[],
): Promise<{ year: number; season: string }[]> {
  const byYear: Record<number, string[]> = {};
  for (const c of combos) {
    (byYear[c.year] ??= []).push(c.season);
  }
  const out: { year: number; season: string }[] = [];
  for (const [yearStr, seasons] of Object.entries(byYear)) {
    const year = Number(yearStr);
    const idsMap: Record<string, number[]> = {};
    await Promise.all(
      SEASONS.map(async (s) => {
        try {
          idsMap[s] = await seasonIds(year, s);
        } catch {
          idsMap[s] = [];
        }
      }),
    );
    for (const s of seasons) {
      const mine = idsMap[s] ?? [];
      if (mine.length === 0) continue; // 空季度不进 sitemap
      let redundant = false;
      for (const other of SEASONS) {
        if (other === s) continue;
        if (sameSet(mine, idsMap[other] ?? [])) {
          redundant = true;
          break;
        }
      }
      if (!redundant) out.push({ year, season: s });
    }
  }
  return out;
}
