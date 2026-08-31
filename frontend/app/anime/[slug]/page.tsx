import AnimeDetailClient from "@/components/AnimeDetailClient";
import {
  fetchAnimeBySlug,
  fetchAnimeDetail,
  fetchRatings,
  fetchRelated,
  fetchCharactersByAnime,
} from "@/lib/api";
import { animePath, isNumericSlug } from "@/lib/slug";
import { matchWatchOrderFranchise } from "@/lib/watchOrder";
import { notFound, permanentRedirect } from "next/navigation";
import type { Anime, RatingsInfo } from "@/types";
import type { AnimeCharacter } from "@/lib/api";

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

// ---- SEO Growth Phase 1-A：英文自然 SEO title/description（面向美国 Google 搜索） ----

const GENRE_TITLE_SUFFIX: Record<string, string> = {
  动作: "Action, Plot & Characters",
  奇幻: "Fantasy World, Plot & Characters",
  恋爱: "Romance, Story & More",
  悬疑: "Mystery & Plot Twists",
  推理: "Mystery & Plot Twists",
  科幻: "Sci-Fi Story & More",
  热血: "Battle Scenes & Story",
  战斗: "Battle Scenes & Story",
  治愈: "Heartwarming Story & More",
  搞笑: "Comedy, Characters & More",
  异世界: "Isekai Adventure, Plot & More",
};

/** 纯 ASCII 标题 → 生成英文 SEO title（含 "Anime" 词 + Watch Order 条件后缀，三级长度控制） */
function buildEnglishSeoTitle(anime: Anime): string | null {
  const title = (anime.title || "").trim();
  if (!title || !/^[\x20-\x7E]+$/.test(title)) return null;
  const genre = (anime.genre || "").split("/").map((g) => g.trim()).find(Boolean) || "";
  const suffix = GENRE_TITLE_SUFFIX[genre] || "Episodes, Release Date & Characters";
  const watchBit = matchWatchOrderFranchise(anime.title, anime.chinese_title)
    ? ", Watch Order"
    : "";
  let t = `${title} Anime: ${suffix}${watchBit}`;
  if (t.length > 68) {
    // 第 2 级：去掉 Watch Order 后缀
    t = `${title} Anime: ${suffix}`;
  }
  if (t.length > 68) {
    // 第 3 级：超长标题（如 Re:ZERO 长系列名）用英文短 genre 压缩，避免 SERP 截断
    const short = GENRE_EN[genre] || "Anime";
    t = `${title} Anime: ${short}`;
  }
  return t;
}

/** 中文 genre 片段 → 英文（用于英文 meta description，避免中英混杂） */
const GENRE_EN: Record<string, string> = {
  动作: "action", 热血: "action", 战斗: "action", 奇幻: "fantasy", 异世界: "isekai",
  科幻: "sci-fi", 机甲: "mecha", 机战: "mecha", 恋爱: "romance", 校园: "school",
  日常: "slice of life", 治愈: "healing", 悬疑: "mystery", 推理: "mystery",
  心理: "psychological", 恐怖: "horror", 惊悚: "thriller", 搞笑: "comedy",
  喜剧: "comedy", 冒险: "adventure", 剧情: "drama", 历史: "historical",
  时代剧: "historical", 运动: "sports", 音乐: "music", 青春: "youth",
  战争: "war", 侦探: "detective", 黑暗: "dark", 魔法: "magic",
  超自然: "supernatural", 异能: "super power", 超能力: "super power",
  偶像: "idol", 博弈: "gambling", 生存: "survival", 竞技: "competitive",
  美食: "cooking", 格斗: "martial arts", 军事: "military", 魔法少女: "magical girl",
  黑帮: "mafia", 职场: "workplace", 福利: "ecchi",
};

/** 生成 150 字符内英文 meta description（含 episodes/characters/release/watch order 关键词，不超长截断） */
function buildEnglishSeoDescription(anime: Anime): string | null {
  const title = (anime.title || "").trim();
  if (!title || !/^[\x20-\x7E]+$/.test(title)) return null;
  const genres = (anime.genre || "")
    .split(/[/，,、\s]+/)
    .map((g) => g.trim())
    .filter(Boolean);
  const genreEn = genres.map((g) => GENRE_EN[g] || g).join(", ") || "anime";
  const yearBit = anime.year ? ` (${anime.year}` : "";
  const epsBit = anime.episodes ? `, ${anime.episodes} eps` : "";
  const watchOrder = matchWatchOrderFranchise(anime.title, anime.chinese_title);
  const watchText = watchOrder ? " + watch order" : "";
  // Phase 33：自然嵌入已验证别名（chinese_title 可能是日文原生名/中文名），便于多语言搜索者识别同一实体
  const altName =
    anime.chinese_title && anime.chinese_title.trim() !== title
      ? ` (${anime.chinese_title.trim()})`
      : "";
  const desc =
    `${title}${altName}: ${genreEn} anime${yearBit}${epsBit}${anime.year ? ")" : ""}. ` +
    `Episodes, characters, release date & watch info${watchText} on AnimeHub.`;
  return desc.length > 160 ? `${desc.slice(0, 157)}...` : desc;
}

export async function generateMetadata({ params }: { params: { slug: string } }) {
  try {
        const anime = await fetchAnimeBySlug(params.slug);
    const seoTitle = (anime.seo_title || "").trim();
    const rawTitle = anime.chinese_title || anime.title;
    // SEO Growth Phase 1-A：英文标题条目 → 生成英文自然 SEO 标题/描述
    const enTitle = buildEnglishSeoTitle(anime);
    const enDesc = buildEnglishSeoDescription(anime);
    // seo_title 已是完整优化标题（含品牌），直接使用；否则用规则生成。
    const pageTitle = enTitle || seoTitle || `${rawTitle} - 在线观看 - AnimeHub`;
    const rawDesc = anime.seo_description || anime.description || "";
    const description =
      enDesc || trimText(rawDesc) || `${rawTitle}在线观看，提供动漫简介、类型、年份与选集信息。`;
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

  // 服务端获取相关推荐（SSR 渲染 → 爬虫可见 anime→anime 内链，增强 crawler discovery）
  let initialRelated: Anime[] = [];
  if (anime) {
    try {
      initialRelated = await fetchRelated(anime.id, 8);
    } catch {
      initialRelated = [];
    }
  }

  // Sprint 6-D：服务端获取角色+声优（SSR 渲染 → 爬虫可见 anime→character→voice-actor 实体内链）
  // 无角色动漫返回空数组，页面不渲染该区块，保持不变。
  let initialCharacters: AnimeCharacter[] = [];
  if (anime) {
    try {
      initialCharacters = await fetchCharactersByAnime(anime.id);
    } catch {
      initialCharacters = [];
    }
  }

  return (
    <>
      <AnimeDetailClient anime={anime} error={error} initialRelated={initialRelated} initialCharacters={initialCharacters} />
            {anime && (
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@type": schemaType,
              name: anime.chinese_title || anime.title,
              ...(() => {
                const raw = [anime.title, anime.chinese_title]
                  .map((n) => (n || "").trim())
                  .filter(Boolean);
                const unique = Array.from(new Set(raw));
                return unique.length >= 2 ? { alternateName: unique } : {};
              })(),
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

      {/* FAQ — 数据驱动英文 FAQ（仅当字段真实存在时生成，不虚构） */}
      {anime && (
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@type": "FAQPage",
              mainEntity: (() => {
                const name = anime.title || anime.chinese_title || "This anime";
                const faq: Array<{ "@type": string; name: string; acceptedAnswer: { "@type": string; text: string } }> = [];
                // 1. What is — 仅当有 genre/year/studio 至少一个事实时
                if (anime.genre || anime.year || anime.studio) {
                  const parts = [
                    `${name} is an anime`,
                    anime.genre ? ` with genres ${anime.genre.split(/[/，,、\s]+/).map((g) => g.trim()).filter(Boolean).join(", ")}` : "",
                    anime.year ? ` released in ${anime.year}` : "",
                    anime.studio ? `, produced by ${anime.studio}` : "",
                  ].filter(Boolean).join("");
                  faq.push({
                    "@type": "Question",
                    name: `What is ${name}?`,
                    acceptedAnswer: { "@type": "Answer", text: parts + "." },
                  });
                }
                // 2. How many episodes — 仅当 episodes 字段存在
                if (anime.episodes && anime.episodes > 0) {
                  faq.push({
                    "@type": "Question",
                    name: `How many episodes does ${name} have?`,
                    acceptedAnswer: {
                      "@type": "Answer",
                      text: `${name} has ${anime.episodes} episode${anime.episodes > 1 ? "s" : ""}. See the full episode list on AnimeHub.`,
                    },
                  });
                }
                // 3. When released — 仅当 year 存在
                if (anime.year) {
                  faq.push({
                    "@type": "Question",
                    name: `When was ${name} released?`,
                    acceptedAnswer: {
                      "@type": "Answer",
                      text: `${name} was released in ${anime.year}.`,
                    },
                  });
                }
                // 4. Watch order — 仅当 franchise 有 watch-order 页
                const wo = matchWatchOrderFranchise(anime.title, anime.chinese_title);
                if (wo) {
                  faq.push({
                    "@type": "Question",
                    name: `Where can I find the ${name} watch order?`,
                    acceptedAnswer: {
                      "@type": "Answer",
                      text: `See the complete watch order guide for the ${name} franchise on AnimeHub.`,
                    },
                  });
                }
                return faq;
              })(),
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