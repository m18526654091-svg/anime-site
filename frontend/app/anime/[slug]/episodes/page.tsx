import Link from "next/link";
import { notFound } from "next/navigation";
import { fetchAnimeBySlug, fetchEpisodes } from "@/lib/api";
import { animePath } from "@/lib/slug";
import { matchFranchise, FRANCHISE_DEFS } from "@/lib/franchise";
import { matchWatchOrderFranchise, FRANCHISES } from "@/lib/watchOrder";
import type { Episode } from "@/types";

export const dynamic = "force-dynamic";
export const revalidate = 3600;

const SITE_BASE = (process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000").replace(/\/$/, "");

function getSiteBase(): string {
  return SITE_BASE;
}

export async function generateMetadata({ params }: { params: { slug: string } }) {
  try {
    const anime = await fetchAnimeBySlug(params.slug);
    const name = anime.title || anime.chinese_title || "Anime";
    const canonical = `${getSiteBase()}/anime/${anime.slug || anime.id}/episodes/`;
    const eps = anime.episodes ? ` — ${anime.episodes} episodes` : "";
    const title = `${name} Episodes: Complete Episode List${eps}`;
    const description =
      `All episodes of ${name}${eps ? ` (${anime.episodes} total)` : ""}. Browse the complete episode list with ` +
      `release information and details on AnimeHub.`;
    return {
      title: { absolute: title.slice(0, 65) },
      description: description.slice(0, 158),
      alternates: { canonical },
      robots: { index: true, follow: true },
    };
  } catch {
    return { title: "Episodes", robots: { index: false, follow: false } };
  }
}

export default async function EpisodesPage({ params }: { params: { slug: string } }) {
  let anime;
  try {
    anime = await fetchAnimeBySlug(params.slug);
  } catch {
    notFound();
  }
  if (!anime) notFound();

  let eps: Episode[] = [];
  try {
    const data = await fetchEpisodes(anime.id);
    eps = (data?.items || []).sort(
      (a, b) => (a.episode_number || 0) - (b.episode_number || 0)
    );
  } catch {
    eps = [];
  }

  const canonical = `${getSiteBase()}/anime/${anime.slug || anime.id}/episodes/`;
  const name = anime.title || anime.chinese_title || "Anime";

  const itemList = eps.map((e, i) => ({
    "@type": "ListItem",
    position: i + 1,
    name: e.title || `Episode ${e.episode_number}`,
    url: `${getSiteBase()}${animePath(anime)}/episodes/#episode-${e.episode_number}`,
  }));

  return (
    <div className="mx-auto max-w-4xl animate-fade-in px-4 py-10">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            itemListElement: [
              { "@type": "ListItem", position: 1, name: "Home", item: `${getSiteBase()}/` },
              { "@type": "ListItem", position: 2, name: name, item: `${getSiteBase()}${animePath(anime)}/` },
              { "@type": "ListItem", position: 3, name: "Episodes", item: canonical },
            ],
          }),
        }}
      />
      {itemList.length > 0 && (
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@type": "ItemList",
              name: `${name} Episodes`,
              numberOfItems: itemList.length,
              itemListElement: itemList,
            }),
          }}
        />
      )}

      <nav className="mb-4 text-sm text-slate-500">
        <Link href="/" className="hover:text-blue-600">Home</Link>
        <span className="mx-2">›</span>
        <Link href={animePath(anime)} className="hover:text-blue-600">{name}</Link>
        <span className="mx-2">›</span>
        <span className="text-slate-700">Episodes</span>
      </nav>

      <h1 className="text-3xl font-bold text-slate-900">{name} Episodes</h1>
      <p className="mt-3 max-w-3xl text-slate-600">
        {anime.episodes
          ? `This anime has ${anime.episodes} episodes in our database.`
          : "Episode count is not announced for this title."}
        {eps.length > 0 && ` Below is the episode list.`}
      </p>

      <div className="mt-6 flex flex-wrap gap-2">
        <Link
          href={animePath(anime)}
          className="rounded-full bg-indigo-600 px-4 py-1.5 text-sm font-semibold text-white transition hover:bg-indigo-500"
        >
          View Anime Details →
        </Link>
        <Link
          href={`${animePath(anime)}/similar/`}
          className="rounded-full border border-slate-300 px-4 py-1.5 text-sm font-medium text-slate-600 transition hover:border-indigo-400 hover:text-indigo-600"
        >
          Similar Anime
        </Link>
        {(() => {
          const fs = matchFranchise(anime.title, anime.chinese_title);
          if (!fs) return null;
          return (
            <Link
              href={`/anime-series/${fs}/`}
              className="rounded-full border border-amber-500/50 bg-amber-50 px-4 py-1.5 text-sm font-medium text-amber-700 transition hover:bg-amber-100"
            >
              {FRANCHISE_DEFS[fs].name} Franchise
            </Link>
          );
        })()}
        {(() => {
          const ws = matchWatchOrderFranchise(anime.title, anime.chinese_title);
          if (!ws) return null;
          return (
            <Link
              href={`/watch-order/${ws}/`}
              className="rounded-full border border-amber-500/50 bg-amber-50 px-4 py-1.5 text-sm font-medium text-amber-700 transition hover:bg-amber-100"
            >
              {FRANCHISES[ws].name} Watch Order
            </Link>
          );
        })()}
      </div>

      <section className="mt-8">
        {eps.length === 0 ? (
          <p className="rounded-xl border border-slate-200 p-5 text-slate-500">
            Episode list not available for this title yet.
          </p>
        ) : (
          <ul className="space-y-2">
            {eps.map((e) => (
              <li
                key={e.id}
                id={`episode-${e.episode_number}`}
                className="flex items-center gap-4 rounded-xl border border-slate-200 p-3 transition hover:shadow-md"
              >
                <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 font-bold text-white">
                  {e.episode_number}
                </span>
                <div className="min-w-0">
                  <div className="font-medium text-slate-900">
                    {e.title || `Episode ${e.episode_number}`}
                  </div>
                  {anime.year ? (
                    <div className="text-xs text-slate-500">{anime.year}</div>
                  ) : null}
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
