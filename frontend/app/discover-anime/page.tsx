import Link from "next/link";
import { fetchAnimeBySort, fetchAnimeByFilter } from "@/lib/api";
import type { Anime } from "@/types";
import TrendingCard from "@/components/TrendingCard";

export const dynamic = "force-dynamic";

const SITE_BASE = (process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000").replace(/\/$/, "");
const MODULE_SIZE = 8;

const SEASON_LABEL: Record<string, string> = {
  spring: "Spring",
  summer: "Summer",
  autumn: "Fall",
  winter: "Winter",
};

function currentSeason(): { season: string; year: number; label: string } {
  const now = new Date();
  const m = now.getMonth() + 1;
  const y = now.getFullYear();
  const season =
    m >= 3 && m <= 5 ? "spring" : m >= 6 && m <= 8 ? "summer" : m >= 9 && m <= 11 ? "autumn" : "winter";
  return { season, year: y, label: `${SEASON_LABEL[season]} ${y}` };
}

const GENRE_LINKS = [
  { slug: "isekai", label: "Best Isekai Anime" },
  { slug: "action", label: "Best Action Anime" },
  { slug: "romance", label: "Best Romance Anime" },
  { slug: "fantasy", label: "Best Fantasy Anime" },
  { slug: "horror", label: "Best Horror Anime" },
  { slug: "comedy", label: "Best Comedy Anime" },
  { slug: "psychological", label: "Best Psychological Anime" },
  { slug: "slice-of-life", label: "Best Slice of Life Anime" },
];

export const metadata = {
  title: "Discover Anime: Find Your Next Favorite Show",
  description:
    "A starting point for anime discovery: trending shows, popular this season, top-rated picks, best anime by genre, and recently added — all in one hub.",
  alternates: { canonical: `${SITE_BASE}/discover-anime/` },
};

export default async function DiscoverAnimePage() {
  const site = SITE_BASE;
  const { season, year, label } = currentSeason();

  let trending: Anime[] = [];
  let topScore: Anime[] = [];
  let latest: Anime[] = [];
  let seasonHits: Anime[] = [];
  let upcoming: Anime[] = [];

  try {
    const [t, s, l, sh] = await Promise.all([
      fetchAnimeBySort("quality", MODULE_SIZE),
      fetchAnimeBySort("score", MODULE_SIZE),
      fetchAnimeBySort("latest", MODULE_SIZE),
      fetchAnimeByFilter({ year, season, sort: "score" }, 1, MODULE_SIZE),
    ]);
    trending = t.items ?? [];
    topScore = s.items ?? [];
    latest = l.items ?? [];
    seasonHits = sh.items ?? [];
  } catch {
    // backend offline: render hub links only
  }
  // Upcoming：未来年份 + 未上映状态（与 /upcoming-anime/ 同口径，仅取前 8）
  {
    const seen = new Map<number, Anime>();
    try {
      const [u1, u2, u3] = await Promise.all([
        fetchAnimeByFilter({ year: year + 1, sort: "score" }, 1, MODULE_SIZE),
        fetchAnimeByFilter({ year, sort: "score" }, 1, MODULE_SIZE),
        fetchAnimeByFilter({ status: "未上映", sort: "score" }, 1, MODULE_SIZE),
      ]);
      for (const pg of [u1, u2, u3]) {
        for (const a of pg.items ?? []) {
          if (!seen.has(a.id)) seen.set(a.id, a);
        }
      }
    } catch {
      // ignore
    }
    upcoming = Array.from(seen.values()).slice(0, MODULE_SIZE);
  }

  const canonical = `${site}/discover-anime/`;

  const SectionTitle = ({ children }: { children: React.ReactNode }) => (
    <h2 className="flex items-center gap-3 text-lg font-semibold text-slate-900">
      <span className="h-5 w-1 rounded-full bg-gradient-to-b from-pink-500 to-indigo-500" />
      {children}
    </h2>
  );

  const MoreLink = ({ href, children }: { href: string; children: React.ReactNode }) => (
    <Link href={href} className="text-sm font-medium text-blue-600 hover:underline">
      {children} →
    </Link>
  );

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
              { "@type": "ListItem", position: 2, name: "Discover Anime", item: canonical },
            ],
          }),
        }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            name: "Discover Anime",
            url: canonical,
            inLanguage: "en",
            description:
              "Trending anime, popular this season, top-rated picks, best anime by genre, and recently added shows.",
          }),
        }}
      />

      <nav className="mb-4 text-sm text-slate-500">
        <Link href="/" className="hover:text-blue-600">Home</Link>
        <span className="mx-2">›</span>
        <span className="text-slate-700">Discover Anime</span>
      </nav>

      <h1 className="text-3xl font-bold text-slate-900">Discover Anime</h1>
      <p className="mt-3 max-w-3xl text-slate-600">
        Not sure what to watch next? Start here: trending shows, what&apos;s popular this season,
        top-rated favorites, and the best anime by genre. Every title links to its detail page,
        where you&apos;ll find similar anime to keep the chain going.
      </p>

      {/* Trending module */}
      <section className="mt-10">
        <div className="flex items-center justify-between">
          <SectionTitle>Trending &amp; Popular Anime</SectionTitle>
          <MoreLink href="/trending-anime/">View all trending</MoreLink>
        </div>
        <div className="mt-4 grid grid-cols-2 gap-5 sm:grid-cols-4 md:grid-cols-4">
          {trending.map((a) => (
            <TrendingCard key={a.id} anime={a} />
          ))}
        </div>
      </section>

      {/* Current season module */}
      {seasonHits.length > 0 && (
        <section className="mt-12">
          <div className="flex items-center justify-between">
            <SectionTitle>Popular This Season ({label})</SectionTitle>
            <MoreLink href={`/season/${season}-${year}-anime/`}>View full season</MoreLink>
          </div>
          <div className="mt-4 grid grid-cols-2 gap-5 sm:grid-cols-4 md:grid-cols-4">
            {seasonHits.map((a) => (
              <TrendingCard key={a.id} anime={a} />
            ))}
          </div>
        </section>
      )}

      {/* Top rated module */}
      {topScore.length > 0 && (
        <section className="mt-12">
          <div className="flex items-center justify-between">
            <SectionTitle>Anime You May Like (Top Rated)</SectionTitle>
            <MoreLink href="/top-anime/">View all top anime</MoreLink>
          </div>
          <div className="mt-4 grid grid-cols-2 gap-5 sm:grid-cols-4 md:grid-cols-4">
            {topScore.map((a) => (
              <TrendingCard key={a.id} anime={a} />
            ))}
          </div>
        </section>
      )}

      {/* Upcoming module */}
      {upcoming.length > 0 && (
        <section className="mt-12">
          <div className="flex items-center justify-between">
            <SectionTitle>Upcoming Anime</SectionTitle>
            <MoreLink href="/upcoming-anime/">View all upcoming</MoreLink>
          </div>
          <div className="mt-4 grid grid-cols-2 gap-5 sm:grid-cols-4 md:grid-cols-4">
            {upcoming.map((a) => (
              <TrendingCard key={a.id} anime={a} />
            ))}
          </div>
        </section>
      )}

      {/* Popular by genre */}
      <section className="mt-12">
        <SectionTitle>Popular by Genre</SectionTitle>
        <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {GENRE_LINKS.map((g) => (
            <Link
              key={g.slug}
              href={`/best-anime/${g.slug}/`}
              className="group rounded-2xl border border-slate-200 bg-white p-4 shadow-sm transition hover:border-indigo-300 hover:shadow-md"
            >
              <div className="font-semibold text-slate-900 group-hover:text-indigo-600">
                {g.label}
              </div>
              <div className="mt-0.5 text-xs text-slate-500">Top shows ranked by score →</div>
            </Link>
          ))}
        </div>
      </section>



      {/* Recently added module */}
      {latest.length > 0 && (
        <section className="mt-12">
          <div className="flex items-center justify-between">
            <SectionTitle>Recently Added</SectionTitle>
            <MoreLink href="/latest-anime/">View all new entries</MoreLink>
          </div>
          <div className="mt-4 grid grid-cols-2 gap-5 sm:grid-cols-4 md:grid-cols-4">
            {latest.map((a) => (
              <TrendingCard key={a.id} anime={a} />
            ))}
          </div>
        </section>
      )}

      {/* Evergreen hub */}
      <section className="mt-12 rounded-3xl border border-slate-200 bg-white p-6">
        <SectionTitle>Always-On Lists</SectionTitle>
        <p className="mt-2 text-sm text-slate-600">
          Evergreen collections that stay useful no matter the season.
        </p>
        <div className="mt-4 flex flex-wrap gap-2">
          <Link
            href="/best-anime/"
            className="rounded-full border border-indigo-500/40 bg-indigo-500/10 px-4 py-1.5 text-sm font-medium text-indigo-700 transition hover:bg-indigo-500/20"
          >
            Best Anime Lists
          </Link>
          <Link
            href="/watch-order/"
            className="rounded-full border border-indigo-500/40 bg-indigo-500/10 px-4 py-1.5 text-sm font-medium text-indigo-700 transition hover:bg-indigo-500/20"
          >
            Watch Orders
          </Link>
          <Link
            href="/new-anime/"
            className="rounded-full border border-indigo-500/40 bg-indigo-500/10 px-4 py-1.5 text-sm font-medium text-indigo-700 transition hover:bg-indigo-500/20"
          >
            New Anime
          </Link>
          <Link
            href="/upcoming-anime/"
            className="rounded-full border border-indigo-500/40 bg-indigo-500/10 px-4 py-1.5 text-sm font-medium text-indigo-700 transition hover:bg-indigo-500/20"
          >
            Upcoming Anime
          </Link>
          <Link
            href="/seasons/"
            className="rounded-full border border-indigo-500/40 bg-indigo-500/10 px-4 py-1.5 text-sm font-medium text-indigo-700 transition hover:bg-indigo-500/20"
          >
            Season Archive
          </Link>
        </div>
      </section>
    </div>
  );
}
