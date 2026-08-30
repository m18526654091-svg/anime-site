import Link from "next/link";
import { notFound } from "next/navigation";
import { fetchAnimePage } from "@/lib/api";
import { animePath } from "@/lib/slug";
import { FRANCHISES, WATCH_ORDER_FRANCHISES } from "@/lib/watchOrder";
import { FRANCHISE_DEFS } from "@/lib/franchise";
import type { Anime } from "@/types";

export const dynamic = "force-dynamic";
export const revalidate = 3600;

const SITE_BASE = (process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000").replace(/\/$/, "");

function getSiteBase(): string {
  return SITE_BASE;
}

export async function generateMetadata({ params }: { params: { slug: string } }) {
  const fr = FRANCHISES[params.slug];
  if (!fr) {
    return { title: "Watch Order", robots: { index: false, follow: false } };
  }
  const canonical = `${getSiteBase()}/watch-order/${fr.slug}/`;
  const title = `${fr.name} Watch Order: How to Watch in the Correct Order`;
  const description = `The complete ${fr.name} watch order — every season, movie, and special in the correct viewing sequence, with release years and episode counts.`;
  return {
    title: { absolute: title },
    description: description.slice(0, 158),
    alternates: { canonical },
    openGraph: {
      type: "article",
      locale: "en_US",
      url: canonical,
      siteName: "AnimeHub",
      title,
      description: description.slice(0, 158),
    },
    twitter: { card: "summary_large_image", title, description: description.slice(0, 158) },
  };
}

/** 从后往前把条目归属到最具体的 step（final > season N > base） */
function assignStep(match: string[][], anime: Anime): number {
  const title = `${anime.title} ${anime.chinese_title || ""}`.toLowerCase();
  for (let i = match.length - 1; i >= 0; i--) {
    for (const kw of match[i]) {
      if (title.includes(kw.toLowerCase())) return i;
    }
  }
  return 0;
}

async function fetchStepAnime(stepMatch: string[]): Promise<Anime[]> {
  const seen = new Map<number, Anime>();
  for (const kw of stepMatch) {
    try {
      const page = await fetchAnimePage(kw, 1, 30);
      for (const a of page.items) {
        if (!seen.has(a.id)) seen.set(a.id, a);
      }
    } catch {
      // ignore
    }
  }
  return Array.from(seen.values());
}
export default async function WatchOrderPage({ params }: { params: { slug: string } }) {
  const fr = FRANCHISES[params.slug];
  if (!fr) notFound();

  const canonical = `${getSiteBase()}/watch-order/${fr.slug}/`;
  const allSeen = new Map<number, Anime>();
  for (let i = 0; i < fr.steps.length; i++) {
    for (const a of await fetchStepAnime(fr.steps[i].match)) {
      if (!allSeen.has(a.id)) allSeen.set(a.id, a);
    }
  }
  const all = Array.from(allSeen.values());
  const buckets: Anime[][] = fr.steps.map(() => []);
  for (const a of all) {
    const s = assignStep(fr.steps.map((st) => st.match), a);
    if (buckets[s].length < 6) buckets[s].push(a);
  }

  return (
    <div className="mx-auto max-w-4xl animate-fade-in px-4 py-10">
      {/* BreadcrumbList JSON-LD */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            itemListElement: [
              { "@type": "ListItem", position: 1, name: "Home", item: `${getSiteBase()}/` },
              { "@type": "ListItem", position: 2, name: "Watch Order", item: `${getSiteBase()}/watch-order/` },
              { "@type": "ListItem", position: 3, name: `${fr.name} Watch Order`, item: canonical },
            ],
          }),
        }}
      />

      <nav className="mb-4 text-sm text-slate-500">
        <Link href="/" className="hover:text-blue-600">Home</Link>
        <span className="mx-2">›</span>
        <Link href="/watch-order/" className="hover:text-blue-600">Watch Order</Link>
        <span className="mx-2">›</span>
        <span className="text-slate-700">{fr.name} Watch Order</span>
      </nav>

      <h1 className="text-3xl font-bold text-slate-900">{fr.name} Watch Order</h1>
      <p className="mt-3 max-w-3xl text-slate-600">{fr.intro}</p>

      <div className="mt-8 space-y-6">
        {fr.steps.map((step, i) => (
          <div key={i} className="rounded-xl border border-slate-200 p-5 shadow-sm">
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 font-black text-white">
                {i + 1}
              </div>
              <div>
                <h2 className="text-lg font-semibold text-slate-900">Step {i + 1}</h2>
                <p className="text-sm text-slate-500">{step.note}</p>
              </div>
            </div>
            <div className="mt-4 space-y-2">
              {buckets[i].length === 0 && <p className="text-sm text-slate-400">Details coming soon.</p>}
              {buckets[i].map((a) => (
                <Link key={a.id} href={animePath(a)}
                      className="flex items-center gap-3 rounded-lg border border-slate-100 p-2 transition hover:border-indigo-300 hover:bg-indigo-50/50">
                  {a.cover ? (
                    <img src={a.cover} alt={a.chinese_title || a.title} className="h-16 w-11 rounded object-cover" loading="lazy" />
                  ) : null}
                  <div className="min-w-0">
                    <div className="font-medium text-slate-900">{a.chinese_title || a.title}</div>
                    <div className="text-xs text-slate-500">
                      {a.year ? `${a.year} · ` : ""}
                      {a.genre?.split("/").slice(0, 2).join(", ")}
                      {a.episodes ? ` · ${a.episodes} eps` : ""}
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        ))}
      </div>

      <section className="mt-10 rounded-xl border border-slate-200 p-5">
        <h2 className="text-lg font-semibold text-slate-900">FAQ</h2>
        <div className="mt-3 space-y-3 text-sm text-slate-600">
          <div>
            <strong>What is the best order to watch {fr.name}?</strong>
            <p className="mt-1">Follow the numbered steps above — they match the official release and story order.</p>
          </div>
          <div>
            <strong>Can I skip movies and specials?</strong>
            <p className="mt-1">Movies are usually optional side stories. Check each entry for its place in the order.</p>
          </div>
        </div>
      </section>

      <div className="mt-8">
        <h2 className="mb-3 text-lg font-semibold text-slate-900">More Watch Orders</h2>
        <div className="flex flex-wrap gap-2">
          {WATCH_ORDER_FRANCHISES.filter((s) => s !== fr.slug).map((s) => (
            <Link key={s} href={`/watch-order/${s}/`}
                  className="rounded-full border border-slate-200 px-4 py-1.5 text-sm text-slate-600 hover:border-blue-400 hover:text-blue-600">
              {FRANCHISES[s].name} Watch Order
            </Link>
          ))}
        </div>
      </div>

      {/* Phase 30：Franchise Hub 链接（watch order → franchise 目录页） */}
      {FRANCHISE_DEFS[fr.slug] && (
        <div className="mt-6">
          <Link
            href={`/anime-series/${fr.slug}/`}
            className="inline-block rounded-xl border border-indigo-200 bg-indigo-50 px-5 py-3 text-sm text-indigo-700 transition hover:bg-indigo-100"
          >
            Browse the {FRANCHISE_DEFS[fr.slug].name} Franchise — every season &amp; movie →
          </Link>
        </div>
      )}
    </div>
  );
}

