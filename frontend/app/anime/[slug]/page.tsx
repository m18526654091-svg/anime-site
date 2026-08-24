import AnimeDetailClient from "@/components/AnimeDetailClient";
import { fetchAnimeBySlug, fetchAnimeDetail, fetchRatings } from "@/lib/api";
import { animePath, isNumericSlug } from "@/lib/slug";
import { notFound, permanentRedirect } from "next/navigation";
import type { Anime, RatingsInfo } from "@/types";

// Render on demand with real backend data.
export const revalidate = 600;
export const dynamicParams = true;

// =====================================================================
// /anime/[slug]
//  - SEO 规范 URL 使用 slug；向后兼容纯数字（视为 anime id）。
//  - 旧 /anime/{id} 链接保持可用：数字 slug 走 id 查询分支。
// =====================================================================

function getSiteBase(): string {
  return (process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000").replace(/\/$/, "");
}

function trimText(s: string, max = 150): string {
  return s.length > max ? s.slice(0, max) + "…" : s;
}

function buildKeywords(anime: Anime): string[] {
  const list: string[] = [anime.title, "在线观看", "免费动漫"];
  if (anime.genre) list.push(anime.genre);
  if (anime.tags) list.push(...anime.tags.split(/[，,、\/\s]+/).filter(Boolean));
  if (anime.year) list.push(`${anime.year}年动漫`, `动漫${anime.year}`);
  if (anime.region) list.push(anime.region);
  if (anime.author) list.push(anime.author);
  return Array.from(new Set(list)).filter(Boolean);
}

export async function generateMetadata({ params }: { params: { slug: string } }) {
  try {
        const anime = await fetchAnimeBySlug(params.slug);
    const seoTitle = (anime.seo_title || "").trim();
    const rawTitle = anime.chinese_title || anime.title;
    // seo_title 已是完整优化标题（含品牌），直接使用；否则用规则生成。
    const pageTitle = seoTitle || `${rawTitle} - 在线观看 - AnimeHub`;
    const rawDesc = anime.seo_description || anime.description || "";
    const description =
      trimText(rawDesc) || `${rawTitle}在线观看，提供动漫简介、类型、年份与选集信息。`;
    const canonical = `${getSiteBase()}${animePath(anime)}/`;
    const keywords = buildKeywords(anime);
    // 低质量页面（quality_score < 50）使用 noindex，避免 Google 收录大量低质内容
    const lowQuality = (anime.quality_score ?? 100) < 50;

    return {
      title: { absolute: pageTitle },
      description,
      keywords,
      robots: lowQuality ? { index: false, follow: true } : { index: true, follow: true },
      alternates: { canonical },
      openGraph: {
        type: "article",
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
  } catch (error) {
    console.error("[generateMetadata] fetchAnimeBySlug failed:", error instanceof Error ? error.message : error, (error as { response?: { status?: number } })?.response?.status);
    // 不存在 / 后端不可达：绝不可索引、不生成 canonical（由页面 notFound() 返回真 404）
    return {
      title: "动漫不存在",
      robots: { index: false, follow: false },
    };
  }
}

export default async function AnimeDetailPage({
  params,
}: {
  params: { slug: string };
}) {
      let anime: Anime | null = null;
  let error = "";

  const isIdSlug = isNumericSlug(params.slug);

  try {
    // Numeric slug: legacy /anime/{id}. Look up by id, then issue a 301
    // (permanentRedirect) to the canonical SEO /anime/{slug}/ if available,
    // so link equity consolidates on the slug URL.
    if (isIdSlug) {
      const byId = await fetchAnimeDetail(Number(params.slug));
      const canonicalSlug = (byId?.slug || "").trim();
      if (canonicalSlug && !isNumericSlug(canonicalSlug) && canonicalSlug !== params.slug) {
        permanentRedirect(`${animePath(byId)}/`);
      }
      anime = byId;
    } else {
      anime = await fetchAnimeBySlug(params.slug);
    }
  } catch (error) {
    error = "Anime not found or backend unavailable";
    console.error("[AnimeDetailPage] fetch anime failed:", error instanceof Error ? error.message : error, (error as { response?: { status?: number } })?.response?.status);
    // 不存在 / 后端不可达 → 真 404（不再是可索引的 soft-404）
    notFound();
  }

    const schemaType = anime && anime.episodes && anime.episodes > 1 ? "TVSeries" : "Movie";

  // 评分信息（用于 aggregateRating 结构化数据），获取失败则忽略。
  let ratings: RatingsInfo | null = null;
  if (anime) {
    try {
      ratings = await fetchRatings(anime.id);
    } catch {
      ratings = null;
    }
  }

  // 仅当存在评分时才输出 aggregateRating，保证结构化数据合法。
  const aggregateRating =
    anime && anime.score
      ? {
          "@type": "Rating",
          ratingValue: Number(ratings?.avg_score || anime.score || 0),
          bestRating: 10,
          ...(ratings?.rating_count ? { ratingCount: Number(ratings.rating_count) } : {}),
        }
      : undefined;

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
              name: anime.chinese_title || anime.title,
              description: anime.seo_description || anime.description,
              ...(anime.cover ? { image: anime.cover } : {}),
              ...(anime.genre ? { genre: anime.genre } : {}),
              ...(anime.studio ? { productionCompany: { "@type": "Organization", name: anime.studio } } : {}),
              ...(anime.year ? { datePublished: `${anime.year}-01-01` } : {}),
                            ...(anime.episodes && anime.episodes > 1
                ? { numberOfEpisodes: anime.episodes }
                : {}),
              ...(aggregateRating ? { aggregateRating } : {}),
              inLanguage: "zh-CN",
              url: `${getSiteBase()}${animePath(anime)}`,
            }),
          }}
        />
      )}

      {/* FAQ — 基于真实字段生成，不虚构剧情 */}
      {anime && (
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@type": "FAQPage",
              mainEntity: [
                {
                  "@type": "Question",
                  name: `${anime.chinese_title || anime.title}是什么动漫？`,
                  acceptedAnswer: {
                    "@type": "Answer",
                    text: [
                      anime.chinese_title || anime.title,
                      anime.year ? `${anime.year}年播出` : "",
                      anime.genre ? `${anime.genre}题材动漫` : "动漫作品",
                      anime.studio ? `由${anime.studio}制作` : "",
                    ].filter(Boolean).join("，") + "。",
                  },
                },
                {
                  "@type": "Question",
                  name: `${anime.chinese_title || anime.title}一共有多少集？`,
                  acceptedAnswer: {
                    "@type": "Answer",
                    text: anime.episodes
                      ? `${anime.chinese_title || anime.title}共${anime.episodes}集，可在 AnimeHub 在线观看。`
                      : `${anime.chinese_title || anime.title}的剧集信息可在 AnimeHub 在线查看。`,
                  },
                },
              ],
            }),
          }}
        />
      )}

      {/* BreadcrumbList — 面包屑（首页 > 类型 > 年份 > 动漫名） */}
      {anime && (
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@type": "BreadcrumbList",
              itemListElement: (() => {
                const crumbs: Array<{
                  "@type": string;
                  position: number;
                  name: string;
                  item: string;
                }> = [
                  {
                    "@type": "ListItem",
                    position: 1,
                    name: "首页",
                    item: `${getSiteBase()}/`,
                  },
                ];
                let pos = 2;
                const primaryGenre = (anime.genre || "")
                  .split("/")
                  .map((g) => g.trim())
                  .find(Boolean);
                if (primaryGenre) {
                  crumbs.push({
                    "@type": "ListItem",
                    position: pos++,
                    name: primaryGenre,
                    item: `${getSiteBase()}/categories/${encodeURIComponent(primaryGenre)}`,
                  });
                }
                if (anime.year) {
                  crumbs.push({
                    "@type": "ListItem",
                    position: pos++,
                    name: `${anime.year}年动漫`,
                    item: `${getSiteBase()}/years/${anime.year}`,
                  });
                }
                crumbs.push({
                  "@type": "ListItem",
                  position: pos,
                  name: anime.chinese_title || anime.title,
                  item: `${getSiteBase()}${animePath(anime)}`,
                });
                return crumbs;
              })(),
            }),
          }}
        />
      )}
    </>
  );
}