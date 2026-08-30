import Link from "next/link";
import { notFound } from "next/navigation";
import { fetchAnimeBySlug, fetchSimilarAnime } from "@/lib/api";
import { animePath, isNumericSlug } from "@/lib/slug";
import type { Anime } from "@/types";

export const dynamic = "force-dynamic";
export const revalidate = 3600;

const SITE_BASE = (process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000").replace(/\/$/, "");

function getSiteBase(): string {
  return SITE_BASE;
}

function displayName(a: Pick<Anime, "title" | "chinese_title">): string {
  return a.chinese_title || a.title;
}

export async function generateMetadata({ params }: { params: { slug: string } }) {
  try {
    const anime = await fetchAnimeBySlug(params.slug);
    const name = anime.title || anime.chinese_title || "Anime";
    const canonical = `${getSiteBase()}/anime/${anime.slug || anime.id}/similar/`;
    const title = `Anime Like ${name}: Best Similar Shows To Watch`;
    const description =
      `Looking for anime like ${name}? We found the best similar shows with the same genre, themes, and vibe — ` +
      `from ${anime.genre || "action"} hits to hidden gems.`;
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
        images: anime.cover ? [{ url: anime.cover, alt: name }] : undefined,
      },
      twitter: {
        card: "summary_large_image",
        title,
        description: description.slice(0, 158),
        images: anime.cover ? [anime.cover] : undefined,
      },
    };
  } catch {
    return { title: "Similar Anime", robots: { index: false, follow: false } };
  }
}

export default async function SimilarAnimePage({ params }: { params: { slug: string } }) {
  let anime: Anime | null = null;
  try {
    anime = await fetchAnimeBySlug(params.slug);
  } catch {
    notFound();
  }
  if (!anime) notFound();
  // 数字 slug 视为 id：跳转到规范 slug 的 similar 页
  if (isNumericSlug(params.slug) && anime.slug && !isNumericSlug(anime.slug)) {
    return (
      <div className="py-24 text-center text-slate-500">
        <Link className="text-blue-600 hover:underline" href={animePath(anime) + "/similar/"}>
          View Similar Anime
        </Link>
      </div>
    );
  }

  let similar: Awaited<ReturnType<typeof fetchSimilarAnime>> = [];
  try {
    similar = await fetchSimilarAnime(anime.id, 8);
  } catch {
    similar = [];
  }

  const name = anime.title || anime.chinese_title || "this anime";
  const similarUrl = `${getSiteBase()}/anime/${anime.slug || anime.id}/similar/`;
  const detailUrl = `${getSiteBase()}${animePath(anime)}/`;

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
              {
                "@type": "ListItem",
                position: 2,
                name: anime.title || anime.chinese_title || "Anime",
                item: detailUrl,
              },
              { "@type": "ListItem", position: 3, name: "Similar Anime", item: similarUrl },
            ],
          }),
        }}
      />
      {/* ItemList JSON-LD（推荐 anime 列表） */}
      {similar.length > 0 && (
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@type": "ItemList",
              name: `Anime Like ${name}`,
              numberOfItems: similar.length,
              itemListElement: similar.map((s, i) => ({
                "@type": "ListItem",
                position: i + 1,
                url: `${getSiteBase()}${animePath(s)}/`,
                name: s.chinese_title || s.title,
              })),
            }),
          }}
        />
      )}
      <nav className="mb-4 text-sm text-slate-500">
        <Link href="/" className="hover:text-blue-600">Home</Link>
        <span className="mx-2">›</span>
        <Link href={animePath(anime)} className="hover:text-blue-600">{displayName(anime)}</Link>
        <span className="mx-2">›</span>
        <span className="text-slate-700">Similar Anime</span>
      </nav>

      <h1 className="text-3xl font-bold text-slate-900">Anime Like {name}</h1>
      <p className="mt-3 max-w-3xl text-slate-600">
        Discover anime similar to <strong>{name}</strong>. Recommendations are based on shared
        genres, release period, and available anime metadata
        {anime.genre
          ? ` — from ${anime.genre.replace(/\//g, " and ")} to gripping storytelling`
          : ""}
        .
      </p>

      <div className="mt-8 space-y-6">
        {similar.length === 0 && (
          <p className="text-slate-500">No similar anime found yet. Check back soon.</p>
        )}
        {similar.map((s) => (
          <div
            key={s.id}
            className="flex items-start gap-4 rounded-xl border border-slate-200 p-4 shadow-sm transition hover:shadow-md"
          >
            <Link href={animePath(s)} className="shrink-0">
              {s.cover ? (
                <img
                  src={s.cover}
                  alt={s.chinese_title || s.title}
                  className="h-28 w-20 rounded-md object-cover"
                  loading="lazy"
                />
              ) : (
                <div className="flex h-28 w-20 items-center justify-center rounded-md bg-gradient-to-br from-indigo-500 to-purple-600 text-2xl text-white">
                  {s.title?.charAt(0).toUpperCase()}
                </div>
              )}
            </Link>
            <div className="min-w-0">
              <div className="flex flex-wrap items-center gap-2">
                <Link href={animePath(s)} className="text-lg font-semibold text-slate-900 hover:text-blue-600">
                  {s.chinese_title || s.title}
                </Link>
                <span className="rounded-full bg-blue-50 px-2 py-0.5 text-xs text-blue-700">
                  {Math.round(s.similarity_score)}% similar
                </span>
                <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs text-slate-600">
                  {s.genre || "Anime"}
                </span>
                {s.year ? (
                  <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs text-slate-600">
                    {s.year}
                  </span>
                ) : null}
              </div>
              {(() => {
                // Phase 17：基于字段计算 reason 徽章（不人工编造）
                const baseGenres = new Set(
                  (anime.genre || "").split(/[/，,、\s]+/).map((g) => g.trim()).filter(Boolean)
                );
                const sGenres = new Set(
                  (s.genre || "").split(/[/，,、\s]+/).map((g) => g.trim()).filter(Boolean)
                );
                const badges: string[] = [];
                if (Array.from(baseGenres).some((g) => sGenres.has(g))) badges.push("Shared genre");
                if (
                  anime.year &&
                  s.year &&
                  Math.abs((anime.year || 0) - (s.year || 0)) <= 2
                ) {
                  badges.push("Similar release period");
                }
                if (
                  anime.score &&
                  s.score &&
                  Math.abs((anime.score || 0) - (s.score || 0)) <= 0.5
                ) {
                  badges.push("Similar score range");
                }
                if (!badges.length) return null;
                return (
                  <div className="mt-1 flex flex-wrap gap-1">
                    {badges.map((b) => (
                      <span
                        key={b}
                        className="rounded bg-emerald-50 px-1.5 py-0.5 text-xs text-emerald-700"
                      >
                        {b}
                      </span>
                    ))}
                  </div>
                );
              })()}
              <p className="mt-1 text-sm text-slate-600">
                Why you may like it: {s.reason || (s.genre ? `It shares the ${s.genre.replace(/\//g, ", ")} vibe you enjoyed.` : "It shares similar themes and storytelling.")}
              </p>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-10 text-center">
        <Link
          href={animePath(anime)}
          className="text-blue-600 hover:underline"
        >
          ← Back to {displayName(anime)}
        </Link>
      </div>
    </div>
  );
}
