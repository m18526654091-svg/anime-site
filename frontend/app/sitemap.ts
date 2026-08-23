import { MetadataRoute } from "next";
import {
  fetchAnimePage,
  fetchCategories,
  fetchSeasons,
  fetchStudios,
  fetchYears,
} from "@/lib/api";
import type { Anime } from "@/types";
import { animePath } from "@/lib/slug";

export const dynamic = "force-dynamic";
export const revalidate = 3600;

// Backend caps page_size at 100 (see backend/app/api/anime.py), so we paginate
// with this size and merge all pages to cover 1000+ anime in the sitemap.
const SITEMAP_PAGE_SIZE = 100;
// Concurrent requests per batch: balances generation latency vs backend load.
const SITEMAP_FETCH_CONCURRENCY = 6;

/**
 * Fetch ALL anime across all pages, deduplicated by id.
 * Required because the backend clamps page_size to 100, so a single
 * fetchAnimePage("", 1, big) only ever returns the first 100 records.
 */
async function fetchAllAnimePages(): Promise<Anime[]> {
  const pageSize = SITEMAP_PAGE_SIZE;

  // First page gives us total/pages so we know how many more to fetch.
  const first = await fetchAnimePage("", 1, pageSize);
  const all: Anime[] = [...first.items];
  const totalPages = (first.pages || 1) ?? Math.ceil((first.total || first.items.length) / pageSize);

  // Fetch remaining pages in small concurrent batches.
  const remaining = Array.from({ length: Math.max(0, totalPages - 1) }, (_, i) => i + 2);
  for (let i = 0; i < remaining.length; i += SITEMAP_FETCH_CONCURRENCY) {
    const batch = remaining.slice(i, i + SITEMAP_FETCH_CONCURRENCY);
    const results = await Promise.all(
      batch.map((p) => fetchAnimePage("", p, pageSize)),
    );
    for (const page of results) {
      all.push(...page.items);
    }
  }

  // Dedupe by id (defensive; slugs could theoretically repeat across pages).
  const seen = new Set<number>();
  return all.filter((a) => {
    if (seen.has(a.id)) return false;
    seen.add(a.id);
    return true;
  });
}

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const siteBase = (process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000").replace(/\/$/, "");
  const lastModified = new Date();

  const staticPages: MetadataRoute.Sitemap = [
    { url: siteBase, lastModified, changeFrequency: "always", priority: 1 },
    { url: `${siteBase}/top-anime/`, lastModified, changeFrequency: "daily", priority: 0.9 },
    { url: `${siteBase}/latest-anime/`, lastModified, changeFrequency: "daily", priority: 0.9 },
    { url: `${siteBase}/high-score/`, lastModified, changeFrequency: "daily", priority: 0.9 },
    { url: `${siteBase}/ranking/`, lastModified, changeFrequency: "daily", priority: 0.8 },
    { url: `${siteBase}/categories/`, lastModified, changeFrequency: "daily", priority: 0.8 },
    { url: `${siteBase}/genres/`, lastModified, changeFrequency: "daily", priority: 0.8 },
    { url: `${siteBase}/tags/`, lastModified, changeFrequency: "daily", priority: 0.8 },
    { url: `${siteBase}/years/`, lastModified, changeFrequency: "daily", priority: 0.8 },
    { url: `${siteBase}/seasons/`, lastModified, changeFrequency: "daily", priority: 0.8 },
    { url: `${siteBase}/studios/`, lastModified, changeFrequency: "daily", priority: 0.8 },
  ];

  let animePages: MetadataRoute.Sitemap = [];
  try {
    const allAnime = await fetchAllAnimePages();
    // 只提交高质量页面（quality_score >= 70）到 sitemap；
    // 低质量（quality<50）页面由详情页 noindex 控制，避免 Google 收录大量低质页。
    const indexable = allAnime.filter((a) => (a.quality_score ?? 100) >= 70);
    // Build unique URLs defensively (DB slug uniqueness is enforced, but guard
    // against edge cases so sitemap never contains duplicate <loc>).
    const seenUrls = new Set<string>();
    const deduped: MetadataRoute.Sitemap = [];
    for (const anime of indexable) {
      if (!(anime.slug || "").trim()) {
        console.warn("Sitemap: anime without slug (using numeric id):", anime.id, anime.title);
      }
      const url = `${siteBase}${animePath(anime)}/`;
      if (seenUrls.has(url)) continue;
      seenUrls.add(url);
      deduped.push({
        url,
        lastModified: anime.updated_at ? new Date(anime.updated_at) : lastModified,
        changeFrequency: "weekly",
        priority: 0.7,
      });
    }
    animePages = deduped;
  } catch (error) {
    console.error("Failed to fetch anime for sitemap:", error);
  }

  let categoryPages: MetadataRoute.Sitemap = [];
  try {
    const cats = await fetchCategories();
    categoryPages = cats
      .filter((c) => (c.genre || "").trim() && c.count >= 5) // Stage 10-B：<5 部组合不进 sitemap
      .map((c) => ({
        url: `${siteBase}/categories/${encodeURIComponent(c.genre)}/`,
        lastModified,
        changeFrequency: "daily",
        priority: 0.6,
      }));
  } catch (error) {
    console.error("Failed to fetch categories for sitemap:", error);
  }

  // Stage 10-B：tag 页全部 noindex，不进 sitemap（与 genre 高度重叠，避免重复/薄页）
  let tagPages: MetadataRoute.Sitemap = [];

  let yearPages: MetadataRoute.Sitemap = [];
  try {
    const years = await fetchYears();
    yearPages = years
      .filter((y) => y.year != null)
      .map((y) => ({
        url: `${siteBase}/years/${y.year}/`,
        lastModified,
        changeFrequency: "daily",
        priority: 0.5,
      }));
  } catch (error) {
    console.error("Failed to fetch years for sitemap:", error);
  }

  let studioPages: MetadataRoute.Sitemap = [];
  try {
    const studios = await fetchStudios();
    studioPages = studios
      .filter((s) => (s.studio || "").trim() && s.count >= 3) // Stage 10-B：<3 部不进 sitemap
      .map((s) => ({
        url: `${siteBase}/studio/${encodeURIComponent(s.studio)}/`,
        lastModified,
        changeFrequency: "weekly",
        priority: 0.6,
      }));
  } catch (error) {
    console.error("Failed to fetch studios for sitemap:", error);
  }

  let seasonPages: MetadataRoute.Sitemap = [];
  try {
    const seasons = await fetchSeasons();
    seasonPages = seasons
      .filter((s) => s.year != null && (s.season || "").trim())
      .map((s) => ({
        url: `${siteBase}/season/${s.year}/${s.season}/`,
        lastModified,
        changeFrequency: "weekly",
        priority: 0.5,
      }));
  } catch (error) {
    console.error("Failed to fetch seasons for sitemap:", error);
  }

  return [...staticPages, ...categoryPages, ...tagPages, ...yearPages, ...studioPages, ...seasonPages, ...animePages];
}
