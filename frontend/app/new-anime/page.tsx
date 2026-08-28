import Link from "next/link";
import { fetchAnimeByFilter } from "@/lib/api";
import { animePath } from "@/lib/slug";
import type { Anime } from "@/types";

export const dynamic = "force-dynamic";
export const revalidate = 3600;

const SITE_BASE = (process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000").replace(/\/$/, "");
const PAGE_SIZE = 24;
const YEARS = [2026, 2025, 2024];

function getSiteBase(): string {
  return SITE_BASE;
}

export const metadata = {
  title: "New Anime 2026: Upcoming Shows and Release Dates",
  description:
    "New anime in 2025 and 2026 — the latest shows ranked by score, with genres, release years, and where to watch. Updated daily.",
};

async function fetchNew(): Promise<Anime[]> {
  const seen = new Map<number, Anime>();
  for (const y of YEARS) {
    try {
      const page = await fetchAnimeByFilter({ year: y, sort: "score" }, 1, PAGE_SIZE);
      for (const a of page.items) {
        if (!seen.has(a.id)) seen.set(a.id, a);
      }
    } catch {
      // ignore
    }
  }
  return Array.from(seen.values()).sort((x, y) => (y.year || 0) - (x.year || 0) || (y.score || 0) - (x.score || 0)).slice(0, PAGE_SIZE);
}

export default async function NewAnimePage() {
  const list = await fetchNew();
  return (
    <div className="mx-auto max-w-5xl animate-fade-in px-4 py-10">
      {/* BreadcrumbList JSON-LD */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            itemListElement: [
              { "@type": "ListItem", position: 1, name: "Home", item: `${getSiteBase()}/` },
              { "@type": "ListItem", position: 2, name: "New Anime", item: `${getSiteBase()}/new-anime/` },
            ],
          }),
        }}
      />
      {/* ItemList JSON-LD */}
      {list.length > 0 && (
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@type": "ItemList",
              name: "New Anime 2025-2026",
              numberOfItems: list.length,
              itemListElement: list.map((a, i) => ({
                "@type": "ListItem",
                position: i + 1,
                url: `${getSiteBase()}${animePath(a)}/`,
                name: a.chinese_title || a.title,
              })),
            }),
          }}
        />
      )}

      <nav className="mb-4 text-sm text-slate-500">
        <Link href="/" className="hover:text-blue-600">Home</Link>
        <span className="mx-2">›</span>
        <span className="text-slate-700">New Anime</span>
      </nav>

      <h1 className="text-3xl font-bold text-slate-900">New Anime 2026: Upcoming Shows and Release Dates</h1>
      <p className="mt-3 max-w-3xl text-slate-600">
        The latest anime from 2025 and 2026 — newly released and upcoming shows ranked by score.
        Explore fresh releases, sequels, and brand-new series with genres, years, and watch links.
      </p>
      <div className="mt-4 flex flex-wrap gap-2">
        <Link href="/upcoming-anime/" className="rounded-full border border-slate-200 px-4 py-1.5 text-sm text-slate-600 hover:border-blue-400 hover:text-blue-600">
          Upcoming Anime →
        </Link>
      </div>

      <div className="mt-8 space-y-4">
        {list.length === 0 && <p className="text-slate-500">No recent anime found yet.</p>}
        {list.map((a, idx) => (
          <div key={a.id} className="flex items-center gap-4 rounded-xl border border-slate-200 p-4 shadow-sm transition hover:shadow-md">
            <div className="w-10 shrink-0 text-center text-2xl font-black text-slate-300">{idx + 1}</div>
            <Link href={animePath(a)} className="shrink-0">
              {a.cover ? (
                <img src={a.cover} alt={a.chinese_title || a.title} className="h-24 w-16 rounded-md object-cover" loading="lazy" />
              ) : (
                <div className="flex h-24 w-16 items-center justify-center rounded-md bg-gradient-to-br from-indigo-500 to-purple-600 text-xl text-white">
                  {(a.chinese_title || a.title).charAt(0).toUpperCase()}
                </div>
              )}
            </Link>
            <div className="min-w-0">
              <Link href={animePath(a)} className="text-lg font-semibold text-slate-900 hover:text-blue-600">
                {a.chinese_title || a.title}
              </Link>
              <div className="mt-1 flex flex-wrap gap-1.5 text-xs text-slate-500">
                <span className="rounded bg-slate-100 px-1.5 py-0.5">{a.genre}</span>
                {a.year ? <span className="rounded bg-slate-100 px-1.5 py-0.5">{a.year}</span> : null}
                {a.score ? <span className="rounded bg-amber-50 px-1.5 py-0.5 text-amber-700">★ {a.score.toFixed(1)}</span> : null}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
