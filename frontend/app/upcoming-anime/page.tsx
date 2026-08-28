import Link from "next/link";
import { fetchAnimeByFilter } from "@/lib/api";
import { animePath } from "@/lib/slug";
import type { Anime } from "@/types";

export const dynamic = "force-dynamic";
export const revalidate = 3600;

const SITE_BASE = (process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000").replace(/\/$/, "");
const PAGE_SIZE = 24;

function getSiteBase(): string {
  return SITE_BASE;
}

export const metadata = {
  title: "Upcoming Anime 2026: New Releases and Release Dates",
  description:
    "Upcoming anime 2026 — see what's coming next: new shows, sequels, and their release dates. Bookmark what to watch this season.",
};

async function fetchUpcoming(): Promise<Anime[]> {
  const seen = new Map<number, Anime>();
  // 未来年份 + 未上映状态
  for (const y of [2027, 2026]) {
    try {
      const page = await fetchAnimeByFilter({ year: y, sort: "score" }, 1, PAGE_SIZE);
      for (const a of page.items) {
        if (!seen.has(a.id)) seen.set(a.id, a);
      }
    } catch {
      // ignore
    }
  }
  try {
    const page = await fetchAnimeByFilter({ status: "未上映", sort: "score" }, 1, PAGE_SIZE);
    for (const a of page.items) {
      if (!seen.has(a.id)) seen.set(a.id, a);
    }
  } catch {
    // ignore
  }
  return Array.from(seen.values()).sort((x, y) => (x.year || 0) - (y.year || 0)).slice(0, PAGE_SIZE);
}

export default async function UpcomingAnimePage() {
  const list = await fetchUpcoming();
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
              { "@type": "ListItem", position: 2, name: "Upcoming Anime", item: `${getSiteBase()}/upcoming-anime/` },
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
              name: "Upcoming Anime 2026",
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
        <span className="text-slate-700">Upcoming Anime</span>
      </nav>

      <h1 className="text-3xl font-bold text-slate-900">Upcoming Anime 2026: New Releases and Release Dates</h1>
      <p className="mt-3 max-w-3xl text-slate-600">
        The next wave of anime — newly announced sequels and fresh series arriving in 2026.
        Keep track of release dates and add the most anticipated shows to your watchlist.
      </p>
      <div className="mt-4 flex flex-wrap gap-2">
        <Link href="/new-anime/" className="rounded-full border border-slate-200 px-4 py-1.5 text-sm text-slate-600 hover:border-blue-400 hover:text-blue-600">
          Recent New Anime →
        </Link>
      </div>

      <div className="mt-8 space-y-4">
        {list.length === 0 && <p className="text-slate-500">No upcoming anime listed yet. New titles are added as they are announced.</p>}
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
                {a.status ? <span className="rounded bg-slate-100 px-1.5 py-0.5">{a.status}</span> : null}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
