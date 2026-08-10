import AnimeDetailClient from "@/components/AnimeDetailClient";
import { fetchAnimeDetail } from "@/lib/api";
import type { Anime } from "@/types";

// Render on demand with real backend data.
export const dynamic = "force-dynamic";

function getSiteBase(): string {
  return (process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000").replace(/\/$/, "");
}

function trimText(s: string, max = 150): string {
  return s.length > max ? s.slice(0, max) + "…" : s;
}

function buildKeywords(anime: Anime): string[] {
  const list = [anime.title];
  if (anime.genre) list.push(anime.genre);
  if (anime.tags) list.push(...anime.tags.split(/[，,、\/\s]+/).filter(Boolean));
  return Array.from(new Set(list)).filter(Boolean);
}

export async function generateMetadata({ params }: { params: { id: string } }) {
  const id = Number(params.id);
  if (!Number.isFinite(id)) {
    return { title: "动漫不存在" };
  }

  try {
    const anime = await fetchAnimeDetail(id);
    const rawTitle = anime.seo_title || anime.title;
    const pageTitle = `${rawTitle} - 在线观看 - AnimeHub`;
    const rawDesc = anime.seo_description || anime.description || "";
    const description =
      trimText(rawDesc) || `${rawTitle}在线观看，提供动漫简介、类型、年份与选集信息。`;
    const canonical = `${getSiteBase()}/anime/${id}/`;
    const keywords = buildKeywords(anime);

    return {
      title: { absolute: pageTitle },
      description,
      keywords,
      alternates: { canonical },
      openGraph: {
        type: "website",
        locale: "zh_CN",
        url: canonical,
        siteName: "AnimeHub",
        title: pageTitle,
        description,
        images: anime.cover ? [{ url: anime.cover, alt: rawTitle }] : undefined,
      },
      twitter: {
        card: "summary_large_image",
        title: pageTitle,
        description,
        images: anime.cover ? [anime.cover] : undefined,
      },
    };
  } catch {
    return { title: "动漫不存在" };
  }
}

export default async function AnimeDetailPage({
  params,
}: {
  params: { id: string };
}) {
  const id = Number(params.id);
  let anime: Anime | null = null;
  let error = "";

  if (!Number.isFinite(id)) {
    error = "Invalid link parameter";
  } else {
    try {
      anime = await fetchAnimeDetail(id);
    } catch {
      error = "Anime not found or backend unavailable";
    }
  }

  const schemaType = anime && anime.episodes && anime.episodes > 1 ? "TVSeries" : "Movie";

  return (
    <>
      <AnimeDetailClient anime={anime} error={error} />
      {anime && (
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@type": schemaType,
              name: anime.title,
              description: anime.seo_description || anime.description,
              ...(anime.cover ? { image: anime.cover } : {}),
              ...(anime.genre ? { genre: anime.genre } : {}),
              ...(anime.year ? { datePublished: `${anime.year}-01-01` } : {}),
              ...(anime.episodes && anime.episodes > 1
                ? { numberOfEpisodes: anime.episodes }
                : {}),
            }),
          }}
        />
      )}
    </>
  );
}
