import Link from "next/link";
import { fetchAnimeBySort, fetchAnimeByFilter } from "@/lib/api";
import TrendingCard from "@/components/TrendingCard";
import type { Anime } from "@/types";

export const dynamic = "force-dynamic";

const SITE_BASE = (process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000").replace(/\/$/, "");
const PAGE_SIZE = 24;

const SEASON_LABEL: Record<string, string> = {
  spring: "Spring",
  summer: "Summer",
  autumn: "Fall",
  winter: "Winter",
};

/** 根据服务器时间推算当前季度（用于 Current Season 入口链接）。 */
function currentSeason(): { season: string; year: number; label: string } {
  const now = new Date();
  const m = now.getMonth() + 1; // 1-12
  const y = now.getFullYear();
  const season =
    m >= 3 && m <= 5 ? "spring" : m >= 6 && m <= 8 ? "summer" : m >= 9 && m <= 11 ? "autumn" : "winter";
  return { season, year: y, label: `${SEASON_LABEL[season]} ${y}` };
}

export const metadata = {
  title: "Trending & Popular Anime Right Now: Top Shows To Watch",
  description:
    "See the most popular anime on AnimeHub right now — ranked by a mix of popularity, user scores, and recent seasons. Find trending anime, similar shows, and seasonal releases.",
  alternates: { canonical: `${SITE_BASE}/trending-anime/` },
};

export default async function TrendingAnimePage() {
  const site = SITE_BASE;
  const { season, year, label } = currentSeason();

  let trending: Anime[] = [];
  let seasonHits: Anime[] = [];
  try {
    const t = await fetchAnimeBySort("quality", PAGE_SIZE);
    trending = t.items ?? [];
  } catch {
    trending = [];
  }
  try {
    const s = await fetchAnimeByFilter({ year, season, sort: "score" }, 1, 8);
    seasonHits = s.items ?? [];
  } catch {
    seasonHits = [];
  }

  const canonical = `${site}/trending-anime/`;

  const itemList = trending.map((a, i) => ({
    "@type": "ListItem",
    position: i + 1,
    url: `${site}/anime/${a.slug || a.id}/`,
    name: a.title || a.chinese_title || "Anime",
  }));

  return (
    <div className="mx-auto max-w-7xl animate-fade-in px-4 py-10">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            itemListElement: [
              { "@type": "ListItem", position: 1, name: "Home", item: `${site}/` },
              { "@type": "ListItem", position: 2, name: "Trending Anime", item: canonical },
            ],
          }),
        }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "ItemList",
            name: "Trending & Popular Anime",
            numberOfItems: itemList.length,
            itemListElement: itemList,
          }),
        }}
      />

      <nav className="mb-4 text-sm text-slate-500">
        <Link href="/" className="hover:text-blue-600">Home</Link>
        <span className="mx-2">›</span>
        <span className="text-slate-700">Trending Anime</span>
      </nav>

      <h1 className="text-3xl font-bold text-slate-900">Trending &amp; Popular Anime</h1>
      <p className="mt-3 max-w-3xl text-slate-600">
        The anime everyone is talking about right now. This ranking combines popularity signals
        from our database, community scores, and how recent each show is — refreshed daily. Not
        a live chart, just the shows worth watching this week.
      </p>

      <div className="mt-6 flex flex-wrap gap-2">
        <Link
          href={`/season/${season}-${year}-anime/`}
          className="rounded-full bg-indigo-600 px-4 py-1.5 text-sm font-semibold text-white transition hover:bg-indigo-500"
        >
          {label} Anime →
        </Link>
        <Link
          href="/new-anime/"
          className="rounded-full border border-slate-300 px-4 py-1.5 text-sm font-medium text-slate-600 transition hover:border-indigo-400 hover:text-indigo-600"
        >
          New Anime
        </Link>
        <Link
          href="/upcoming-anime/"
          className="rounded-full border border-slate-300 px-4 py-1.5 text-sm font-medium text-slate-600 transition hover:border-indigo-400 hover:text-indigo-600"
        >
          Upcoming Anime
        </Link>
        <Link
          href="/discover-anime/"
          className="rounded-full border border-slate-300 px-4 py-1.5 text-sm font-medium text-slate-600 transition hover:border-indigo-400 hover:text-indigo-600"
        >
          Discover More Anime
        </Link>
      </div>

      <section className="mt-8">
        <div className="grid grid-cols-2 gap-5 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6">
          {trending.map((a) => (
            <TrendingCard key={a.id} anime={a} />
          ))}
        </div>
        {trending.length === 0 && (
          <p className="text-slate-500">Trending anime are loading. Check back shortly.</p>
        )}
      </section>

      {seasonHits.length > 0 && (
        <section className="mt-12">
          <div className="flex items-center justify-between">
            <h2 className="flex items-center gap-3 text-lg font-semibold text-slate-900">
              <span className="h-5 w-1 rounded-full bg-gradient-to-b from-pink-500 to-indigo-500" />
              Popular This Season ({label})
            </h2>
            <Link
              href={`/season/${season}-${year}-anime/`}
              className="text-sm font-medium text-blue-600 hover:underline"
            >
              View full season →
            </Link>
          </div>
          <div className="mt-4 grid grid-cols-2 gap-5 sm:grid-cols-3 md:grid-cols-4">
            {seasonHits.map((a) => (
              <TrendingCard key={a.id} anime={a} />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
