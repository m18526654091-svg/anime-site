import Link from "next/link";
import { notFound } from "next/navigation";
import { fetchAnimeByFilter } from "@/lib/api";
import { animePath } from "@/lib/slug";
import type { AnimePage } from "@/types";

export const dynamic = "force-dynamic";
export const revalidate = 3600;

const SITE_BASE = (process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000").replace(/\/$/, "");
const PAGE_SIZE = 24;

const SEASON_LABEL: Record<string, string> = {
  spring: "Spring",
  summer: "Summer",
  autumn: "Fall",
  winter: "Winter",
};

const SEASON_MONTHS: Record<string, string> = {
  spring: "March to May",
  summer: "June to August",
  autumn: "September to November",
  winter: "December to February",
};

function parseSlug(slug: string): { season: string; year: number } | null {
  const m = slug.match(/^(winter|spring|summer|autumn)-(\d{4})-anime$/i);
  if (!m) return null;
  const year = parseInt(m[2], 10);
  if (!Number.isFinite(year) || year < 1990 || year > 2030) return null;
  return { season: m[1].toLowerCase(), year };
}

function getSiteBase(): string {
  return SITE_BASE;
}

export async function generateMetadata({ params }: { params: { slug: string } }) {
  const parsed = parseSlug(params.slug);
  if (!parsed) {
    return { title: "Seasonal Anime", robots: { index: false, follow: false } };
  }
  const label = `${SEASON_LABEL[parsed.season]} ${parsed.year}`;
  const canonical = `${getSiteBase()}/season/${params.slug}/`;
  const title = `${label} Anime: New Shows, Release Dates & More`;
  const description =
    `${label} anime lineup — discover the best new shows this season, with release dates, ` +
    `genres, scores, and where to watch. Updated daily.`;
  return {
    title: { absolute: title },
    description: description.slice(0, 158),
    alternates: { canonical },
    openGraph: {
      type: "website",
      locale: "en_US",
      url: canonical,
      siteName: "AnimeHub",
      title,
      description: description.slice(0, 158),
    },
    twitter: { card: "summary_large_image", title, description: description.slice(0, 158) },
  };
}

export default async function SeasonSlugPage({ params }: { params: { slug: string } }) {
  const parsed = parseSlug(params.slug);
  if (!parsed) notFound();

  let data: AnimePage = { items: [], total: 0, page: 1, page_size: PAGE_SIZE, pages: 0 };
  try {
    data = await fetchAnimeByFilter(
      { year: parsed.year, season: parsed.season, sort: "score" },
      1,
      PAGE_SIZE
    );
  } catch {
    // backend offline
  }

  const label = `${SEASON_LABEL[parsed.season]} ${parsed.year}`;
  const months = SEASON_MONTHS[parsed.season];

  return (
    <div className="mx-auto max-w-7xl animate-fade-in px-4 py-10">
      <nav className="mb-4 text-sm text-slate-500">
        <Link href="/" className="hover:text-blue-600">Home</Link>
        <span className="mx-2">›</span>
        <Link href="/seasons/" className="hover:text-blue-600">Seasonal Anime</Link>
        <span className="mx-2">›</span>
        <span className="text-slate-700">{label} Anime</span>
      </nav>

      <h1 className="text-3xl font-bold text-slate-900">{label} Anime</h1>
      <p className="mt-2 max-w-3xl text-slate-600">
        The complete {label} anime lineup ({months}). Browse new releases, top-rated shows, and
        hidden gems airing this season — with scores, genres, and release years.
      </p>

      <div className="mt-8 grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4">
        {data.items.map((a) => (
          <Link
            key={a.id}
            href={animePath(a)}
            className="group overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm transition hover:shadow-md"
          >
            {a.cover ? (
              <img
                src={a.cover}
                alt={a.chinese_title || a.title}
                className="h-40 w-full object-cover transition group-hover:scale-105"
                loading="lazy"
              />
            ) : (
              <div className="flex h-40 items-center justify-center bg-gradient-to-br from-indigo-500 to-purple-600 text-white">
                {(a.chinese_title || a.title).charAt(0).toUpperCase()}
              </div>
            )}
            <div className="p-3">
              <div className="line-clamp-2 text-sm font-semibold text-slate-900 group-hover:text-blue-600">
                {a.chinese_title || a.title}
              </div>
              <div className="mt-1 flex flex-wrap gap-1 text-xs text-slate-500">
                <span className="rounded bg-slate-100 px-1.5 py-0.5">{a.genre?.split("/")[0]}</span>
                {a.score ? <span className="text-amber-600">★ {a.score}</span> : null}
              </div>
            </div>
          </Link>
        ))}
      </div>

      {data.items.length === 0 && (
        <p className="mt-8 text-slate-500">
          No anime listed for {label} yet. Check back soon — new titles are added daily.
        </p>
      )}
    </div>
  );
}
