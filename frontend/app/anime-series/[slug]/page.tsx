import Link from "next/link";
import { notFound } from "next/navigation";
import { fetchAnimePage } from "@/lib/api";
import { animePath } from "@/lib/slug";
import { FRANCHISE_DEFS, FRANCHISE_SLUGS } from "@/lib/franchise";
import { WATCH_ORDER_FRANCHISES } from "@/lib/watchOrder";
import type { Anime } from "@/types";

export const dynamic = "force-dynamic";

const SITE_BASE = (process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000").replace(/\/$/, "");
const PAGE_SIZE = 30;

export function generateStaticParams() {
  return FRANCHISE_SLUGS.map((slug) => ({ slug }));
}

function getSiteBase(): string {
  return SITE_BASE;
}

export async function generateMetadata({ params }: { params: { slug: string } }) {
  const def = FRANCHISE_DEFS[params.slug];
  if (!def) return { title: "Anime Series", robots: { index: false, follow: false } };
  const canonical = `${getSiteBase()}/anime-series/${def.slug}/`;
  const title = `${def.name} Franchise - Watch Order, Seasons & Anime List`;
  const description =
    `The complete ${def.name} franchise guide — every season, sequel, and movie in our database, ` +
    `with watch order, release years, and direct anime links.`;
  return {
    title: { absolute: title.slice(0, 68) },
    description: description.slice(0, 158),
    alternates: { canonical },
    openGraph: {
      type: "website",
      locale: "en_US",
      url: canonical,
      siteName: "AnimeHub",
      title: title.slice(0, 68),
      description: description.slice(0, 158),
    },
  };
}

async function fetchFranchiseAnime(match: string[]): Promise<Anime[]> {
  const seen = new Map<number, Anime>();
  for (const kw of match) {
    try {
      const page = await fetchAnimePage(kw, 1, PAGE_SIZE);
      for (const a of page.items) {
        if (!seen.has(a.id)) seen.set(a.id, a);
      }
    } catch {
      // ignore single keyword failure
    }
  }
  return Array.from(seen.values()).sort(
    (x, y) => (x.year || 0) - (y.year || 0) || (x.id || 0) - (y.id || 0)
  );
}

export default async function AnimeSeriesPage({ params }: { params: { slug: string } }) {
  const def = FRANCHISE_DEFS[params.slug];
  if (!def) notFound();

  const all = await fetchFranchiseAnime(def.match);
  const canonical = `${getSiteBase()}/anime-series/${def.slug}/`;

  const buckets = def.groups.map((g) => ({
    ...g,
    items: all.filter((a) => g.test(`${a.title} ${a.chinese_title || ""}`)),
  }));

  const itemList = all.map((a, i) => ({
    "@type": "ListItem",
    position: i + 1,
    url: `${getSiteBase()}${animePath(a)}/`,
    name: a.chinese_title || a.title,
  }));

  return (
    <div className="mx-auto max-w-5xl animate-fade-in px-4 py-10">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            itemListElement: [
              { "@type": "ListItem", position: 1, name: "Home", item: `${getSiteBase()}/` },
              { "@type": "ListItem", position: 2, name: `${def.name} Franchise`, item: canonical },
            ],
          }),
        }}
      />
      {all.length > 0 && (
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@type": "ItemList",
              name: `${def.name} Franchise`,
              numberOfItems: all.length,
              itemListElement: itemList,
            }),
          }}
        />
      )}

      <nav className="mb-4 text-sm text-slate-500">
        <Link href="/" className="hover:text-blue-600">Home</Link>
        <span className="mx-2">›</span>
        <span className="text-slate-700">{def.name} Franchise</span>
      </nav>

      <h1 className="text-3xl font-bold text-slate-900">{def.name} Franchise</h1>
      <p className="mt-3 max-w-3xl text-slate-600">{def.intro}</p>

      {all.length === 0 && (
        <p className="mt-8 text-slate-500">
          Series entries are being collected. Check back soon.
        </p>
      )}

      {/* Franchise Overview（基于 DB 字段统计，不编造） */}
      {all.length > 0 && (
        <div className="mt-6 rounded-xl border border-slate-200 bg-white p-4 text-sm text-slate-600">
          <span className="font-semibold text-slate-900">Franchise Overview: </span>
          {all.length} entries in our database
          {(() => {
            const years = Array.from(new Set(all.map((a) => a.year).filter(Boolean))).sort() as number[];
            return years.length ? ` · Released ${years[0]}–${years[years.length - 1]}` : "";
          })()}
          {(() => {
            const genres: string[] = [];
            for (const a of all) {
              for (const g of (a.genre || "").split(/[/，,、\s]+/)) {
                const t = g.trim();
                if (t && !genres.includes(t)) genres.push(t);
              }
            }
            return genres.length ? ` · Genres: ${genres.slice(0, 6).join(", ")}` : "";
          })()}
        </div>
      )}

      {/* Watch Order（若 franchise 有 watch-order 页） */}
      {WATCH_ORDER_FRANCHISES.includes(def.slug) && (
        <div className="mt-4">
          <Link
            href={`/watch-order/${def.slug}/`}
            className="rounded-full bg-indigo-600 px-5 py-2 text-sm font-semibold text-white transition hover:bg-indigo-500"
          >
            {def.name} Watch Order →
          </Link>
        </div>
      )}

      {buckets.map((group) => {
        if (group.items.length === 0) return null;
        return (
          <section key={group.key} className="mt-10">
            <h2 className="flex items-center gap-3 text-lg font-semibold text-slate-900">
              <span className="h-5 w-1 rounded-full bg-gradient-to-b from-indigo-500 to-purple-600" />
              {group.label}
            </h2>
            <div className="mt-4 space-y-3">
              {group.items.map((a) => (
                <div
                  key={a.id}
                  className="flex items-center gap-4 rounded-xl border border-slate-200 p-3 transition hover:shadow-md"
                >
                  <Link href={animePath(a)} className="shrink-0">
                    {a.cover ? (
                      <img
                        src={a.cover}
                        alt={a.chinese_title || a.title}
                        className="h-20 w-14 rounded-md object-cover"
                        loading="lazy"
                      />
                    ) : (
                      <div className="flex h-20 w-14 items-center justify-center rounded-md bg-gradient-to-br from-indigo-500 to-purple-600 text-white">
                        {(a.chinese_title || a.title || "A").charAt(0).toUpperCase()}
                      </div>
                    )}
                  </Link>
                  <div className="min-w-0 flex-1">
                    <Link
                      href={animePath(a)}
                      className="font-semibold text-slate-900 hover:text-blue-600"
                    >
                      {a.chinese_title || a.title}
                    </Link>
                    <div className="mt-1 text-xs text-slate-500">
                      {a.year ? `${a.year} · ` : ""}
                      {a.genre?.split("/").slice(0, 2).join(", ") || "Anime"}
                      {a.score ? ` · ★ ${a.score.toFixed(1)}` : ""}
                      {a.status ? ` · ${a.status === "完结" ? "Completed" : a.status}` : ""}
                    </div>
                  </div>
                  <Link
                    href={`/anime/${a.slug || a.id}/similar/`}
                    className="shrink-0 rounded-full border border-indigo-500/40 bg-indigo-500/10 px-3 py-1 text-xs font-medium text-indigo-700 transition hover:bg-indigo-500/20"
                  >
                    Similar →
                  </Link>
                </div>
              ))}
            </div>
          </section>
        );
      })}

      {/* Phase 31：Related Anime / More to explore（真实页面链接，非空区块） */}
      <section className="mt-10 rounded-2xl border border-slate-200 bg-white p-5">
        <h2 className="text-lg font-semibold text-slate-900">Related Anime &amp; More to Explore</h2>
        <p className="mt-1 text-sm text-slate-500">
          If you enjoyed the {def.name} series, these pages help you discover more anime.
        </p>
        <div className="mt-4 flex flex-wrap gap-2">
          <Link
            href="/trending-anime/"
            className="rounded-full border border-indigo-500/40 bg-indigo-500/10 px-4 py-1.5 text-sm font-medium text-indigo-700 transition hover:bg-indigo-500/20"
          >
            Trending Anime
          </Link>
          <Link
            href="/discover-anime/"
            className="rounded-full border border-indigo-500/40 bg-indigo-500/10 px-4 py-1.5 text-sm font-medium text-indigo-700 transition hover:bg-indigo-500/20"
          >
            Discover Anime
          </Link>
          <Link
            href="/seasons/"
            className="rounded-full border border-indigo-500/40 bg-indigo-500/10 px-4 py-1.5 text-sm font-medium text-indigo-700 transition hover:bg-indigo-500/20"
          >
            Seasonal Anime
          </Link>
          <Link
            href="/best-anime/"
            className="rounded-full border border-indigo-500/40 bg-indigo-500/10 px-4 py-1.5 text-sm font-medium text-indigo-700 transition hover:bg-indigo-500/20"
          >
            Best Anime Lists
          </Link>
          <Link
            href="/new-anime/"
            className="rounded-full border border-indigo-500/40 bg-indigo-500/10 px-4 py-1.5 text-sm font-medium text-indigo-700 transition hover:bg-indigo-500/20"
          >
            New Anime
          </Link>
          <Link
            href="/watch-order/"
            className="rounded-full border border-slate-300 px-4 py-1.5 text-sm font-medium text-slate-600 transition hover:border-indigo-400 hover:text-indigo-600"
          >
            View Watch Orders
          </Link>
        </div>
      </section>
    </div>
  );
}

