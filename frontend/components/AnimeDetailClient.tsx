"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import {
  addFavorite,
  fetchEpisodes,
  fetchFavorites,
  fetchRelated,
  removeFavorite,
} from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { animePath } from "@/lib/slug";
import { FRANCHISES, matchWatchOrderFranchise } from "@/lib/watchOrder";
import { FRANCHISE_DEFS, matchFranchise } from "@/lib/franchise";
import AdPlaceholder from "@/components/AdPlaceholder";
import AnimeCover from "@/components/AnimeCover";
import RatingWidget from "@/components/RatingWidget";
import type { Anime, Episode } from "@/types";
import type { AnimeCharacter } from "@/lib/api";

interface Props {
  anime: Anime | null;
  error: string;
  initialRelated?: Anime[];
  initialCharacters?: AnimeCharacter[];
}

const SEASON_LABEL: Record<string, string> = {
  spring: "Spring",
  summer: "Summer",
  autumn: "Fall",
  winter: "Winter",
};

/** 中文 genre 片段 → 英文（detail 正文 Genres 区块） */
const GENRE_EN: Record<string, string> = {
  动作: "Action", 热血: "Action", 战斗: "Action", 奇幻: "Fantasy", 异世界: "Isekai",
  科幻: "Sci-Fi", 机甲: "Mecha", 恋爱: "Romance", 校园: "School", 日常: "Slice of Life",
  治愈: "Healing", 悬疑: "Mystery", 推理: "Mystery", 心理: "Psychological",
  恐怖: "Horror", 惊悚: "Thriller", 搞笑: "Comedy", 喜剧: "Comedy", 冒险: "Adventure",
  剧情: "Drama", 历史: "Historical", 时代剧: "Historical", 运动: "Sports", 音乐: "Music",
  青春: "Youth", 战争: "War", 侦探: "Detective", 黑暗: "Dark", 魔法: "Magic",
};

/** anime genre（中文）→ best-anime 分类 slug + 英文 label（条件内链，只基于可靠 genre 字段） */
const BEST_GENRE_MAP: { match: string[]; slug: string; label: string }[] = [
  { match: ["异世界"], slug: "isekai", label: "Isekai" },
  { match: ["动作", "热血", "战斗"], slug: "action", label: "Action" },
  { match: ["恋爱"], slug: "romance", label: "Romance" },
  { match: ["奇幻"], slug: "fantasy", label: "Fantasy" },
  { match: ["恐怖"], slug: "horror", label: "Horror" },
  { match: ["搞笑", "喜剧"], slug: "comedy", label: "Comedy" },
  { match: ["心理", "悬疑", "推理"], slug: "psychological", label: "Psychological" },
  { match: ["日常", "治愈"], slug: "slice-of-life", label: "Slice of Life" },
];

function bestGenreEntry(genre?: string | null) {
  if (!genre) return null;
  const parts = genre.split(/[/，,、\s]+/).map((g) => g.trim());
  for (const p of parts) {
    const hit = BEST_GENRE_MAP.find((m) => m.match.includes(p));
    if (hit) return hit;
  }
  return null;
}

/** 基于 genre/score/year 生成安全的英文推荐句（不虚构剧情细节） */
function whoShouldWatchText(a: { genre?: string; score?: number; year?: number | null }): string {
  const genres = (a.genre || "")
    .split(/[/，,、\s]+/)
    .map((g) => g.trim())
    .filter(Boolean);
  const base = genres.length
    ? `If you enjoy ${genres.slice(0, 3).join(", ")} anime`
    : "If you are a fan of anime";
  const scoreBit = a.score
    ? ` — this title holds a ${Number(a.score).toFixed(1)}/10 fan rating`
    : "";
  const yearBit = a.year ? ` and first aired in ${a.year}` : "";
  return `${base}${scoreBit}${yearBit}, this is a show worth checking out.`;
}

function currentSeason(): { season: string; year: number; label: string } {
  const now = new Date();
  const m = now.getMonth() + 1;
  const y = now.getFullYear();
  const season =
    m >= 3 && m <= 5 ? "spring" : m >= 6 && m <= 8 ? "summer" : m >= 9 && m <= 11 ? "autumn" : "winter";
  return { season, year: y, label: `${SEASON_LABEL[season]} ${y}` };
}

export default function AnimeDetailClient({ anime, error, initialRelated = [], initialCharacters = [] }: Props) {
  const router = useRouter();
  const { isLoggedIn } = useAuth();
  const [related, setRelated] = useState<Anime[]>(initialRelated);
  const [favorited, setFavorited] = useState(false);
  const [favLoading, setFavLoading] = useState(false);
  const [dbEpisodes, setDbEpisodes] = useState<Episode[]>([]);
  const [loadingEpisodes, setLoadingEpisodes] = useState(false);

  useEffect(() => {
    if (!anime) return;
    let cancelled = false;
    fetchRelated(anime.id)
      .then((list) => {
        if (!cancelled) setRelated(list);
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, [anime]);

  useEffect(() => {
    if (!anime) return;
    let cancelled = false;
    setLoadingEpisodes(true);
    fetchEpisodes(anime.id)
      .then((data) => {
        if (!cancelled) setDbEpisodes(data.items || []);
      })
      .catch(() => {
        if (!cancelled) setDbEpisodes([]);
      })
      .finally(() => {
        if (!cancelled) setLoadingEpisodes(false);
      });
    return () => {
      cancelled = true;
    };
  }, [anime]);

  // Load the user's favorite state for this anime once authenticated.
  useEffect(() => {
    if (!anime || !isLoggedIn) return;
    let cancelled = false;
    fetchFavorites()
      .then((list) => {
        if (!cancelled) setFavorited(list.some((a) => a && a.id === anime.id));
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, [anime, isLoggedIn]);

  const toggleFavorite = async () => {
    if (!anime) return;
    if (!isLoggedIn) {
      router.push("/login");
      return;
    }
    if (favLoading) return;
    setFavLoading(true);
    const prev = favorited;
    try {
      if (favorited) {
        await removeFavorite(anime.id);
        setFavorited(false);
      } else {
        await addFavorite(anime.id);
        setFavorited(true);
      }
    } catch {
      setFavorited(prev);
    } finally {
      setFavLoading(false);
    }
  };

  if (error || !anime) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-24 text-center">
        <p className="text-4xl">😢</p>
        <p className="mt-4 text-slate-400">{error || "Anime not found"}</p>
        <Link
          href="/"
          className="mt-6 inline-block rounded-lg bg-white/5 px-5 py-2 text-pink-400 transition hover:bg-white/10"
        >
          ← Back to Home
        </Link>
      </div>
    );
  }

  const score = Number(anime.score ?? 0);

  const tags = useMemo(() => {
    if (!anime.tags) return [];
    return anime.tags.split(/[，,、\s]+/).filter(Boolean).slice(0, 8);
  }, [anime.tags]);

  const seoText = anime.seo_description || anime.description || "";

  const friendlyText = useMemo(() => {
    const parts = [
      anime.title,
      anime.genre ? `Genre: ${anime.genre}` : "",
      anime.year ? `Year: ${anime.year}` : "",
      anime.region ? `Region: ${anime.region}` : "",
      anime.author ? `Author: ${anime.author}` : "",
      anime.studio ? `Studio: ${anime.studio}` : "",
      anime.status ? `Status: ${anime.status}` : "",
      anime.episodes ? `Episodes: ${anime.episodes}` : "",
    ].filter(Boolean);

    const intro = parts.join(" | ");
    const desc = seoText || "No detailed description available.";
    const extras = tags.length > 0 ? `  Tags: ${tags.join(", ")}.` : "";
    const related = `如果你喜欢 ${anime.title}, 你可能会喜欢其他 ${anime.genre || "同类型动漫"}.`;

    return `${intro}. ${desc}${extras} ${related}`;
  }, [anime, tags, seoText]);

  // ---- Play data parsing ----
  const playData = useMemo(() => {
    if (!anime.play_data) return null;
    try {
      const parsed = JSON.parse(anime.play_data);
      if (
        parsed &&
        Array.isArray(parsed.lines) &&
        parsed.lines.length > 0 &&
        parsed.lines.every((l: { episodes?: unknown }) => l && Array.isArray(l.episodes))
      ) {
        return parsed as { lines: { name: string; episodes: { ep: number; title?: string; url: string }[] }[] };
      }
      return null;
    } catch {
      return null;
    }
  }, [anime.play_data]);

  const [activeLine, setActiveLine] = useState(0);
  const [activeEp, setActiveEp] = useState(0);

  const currentLine = playData?.lines[activeLine];
  const episodes = currentLine?.episodes ?? [];
  const playUrl = episodes[activeEp]?.url;

  const switchLine = (i: number) => {
    setActiveLine(i);
    setActiveEp(0);
  };

  return (
    <div id="anime-detail" className="mx-auto max-w-6xl animate-fade-in px-4 py-8">
      {/* ===== 面包屑导航（视觉）===== */}
      {anime && (() => {
        const primaryGenre = (anime.genre || "")
          .split("/")
          .map((g) => g.trim())
          .find(Boolean);
        return (
          <nav
            aria-label="Breadcrumb"
            className="mb-6 flex flex-wrap items-center gap-1.5 text-sm text-slate-400"
          >
            <Link href="/" className="hover:text-pink-400">
              Home
            </Link>
            {primaryGenre && (
              <>
                <span className="text-slate-600">/</span>
                <Link
                  href={`/categories/${encodeURIComponent(primaryGenre)}`}
                  className="hover:text-pink-400"
                >
                  {primaryGenre}
                </Link>
              </>
            )}
            {anime.year && (
              <>
                <span className="text-slate-600">/</span>
                <Link
                  href={`/years/${anime.year}`}
                  className="hover:text-pink-400"
                >
                  {anime.year} Anime
                </Link>
              </>
            )}
            <span className="text-slate-600">/</span>
            <span className="truncate text-slate-200">
              {anime.chinese_title || anime.title}
            </span>
          </nav>
        );
      })()}
      {/* ===== Main info card ===== */}
      <div className="relative overflow-hidden rounded-3xl border border-white/10 bg-white/5 shadow-2xl backdrop-blur">
        <div className="absolute inset-x-0 top-0 h-40 bg-gradient-to-r from-pink-600/25 to-indigo-600/25" />

        <div className="relative flex flex-col gap-6 p-6 sm:p-8 md:flex-row">
          {/* Poster */}
          <div className="mx-auto w-52 shrink-0 sm:mx-0 sm:w-56">
            <AnimeCover
              anime={anime}
              className="aspect-[3/4] w-full rounded-2xl border border-white/10 object-cover shadow-glow-indigo"
              priority
            />
          </div>

          {/* Info */}
          <div className="flex-1">
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <h1 className="text-3xl font-black leading-tight text-white sm:text-4xl">
                  {anime.chinese_title || anime.title}
                </h1>
                {(() => {
                  const gs = (anime.genre || "")
                    .split(/[/，,、\s]+/)
                    .map((g) => g.trim())
                    .filter(Boolean);
                  const genresEn = gs.map((g) => GENRE_EN[g] || g).join(", ") || "anime";
                  const m = anime.month ?? null;
                  const seasonEn = m
                    ? m <= 2 || m === 12
                      ? "Winter"
                      : m <= 5
                      ? "Spring"
                      : m <= 8
                      ? "Summer"
                      : "Fall"
                    : null;
                  const release = anime.year
                    ? seasonEn
                      ? `${seasonEn} ${anime.year}`
                      : String(anime.year)
                    : "release date not announced";
                  const eps = anime.episodes
                    ? `${anime.episodes} episodes`
                    : "episode count not announced";
                  const statusEn =
                    anime.status === "完结"
                      ? "Completed"
                      : anime.status === "连载" || anime.status === "连载中"
                      ? "Airing"
                      : anime.status === "未上映"
                      ? "Not yet aired"
                      : anime.status
                      ? anime.status
                      : "Unknown";
                  const scoreText = anime.score
                    ? `${Number(anime.score).toFixed(1)}/10`
                    : "not rated";
                  const name = anime.title || anime.chinese_title || "This anime";
                  return (
                    <p className="mt-2 text-sm leading-relaxed text-slate-300">
                      {name} is a {genresEn} anime released in {release}. Episodes: {eps} ·
                      Status: {statusEn} · Genres: {genresEn} · Score: {scoreText}.
                    </p>
                  );
                })()}
                {!loadingEpisodes && dbEpisodes.length > 0 && (
                  <div className="mt-2">
                    <Link
                      href={`/watch/${anime.id}`}
                      className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-pink-600 to-fuchsia-600 px-5 py-2.5 text-sm font-semibold text-white shadow-glow transition hover:from-pink-500 hover:to-fuchsia-500"
                    >
                      Watch Now
                    </Link>
                  </div>
                )}
              </div>
              <button
                type="button"
                onClick={toggleFavorite}
                disabled={favLoading}
                className={`shrink-0 rounded-xl border px-4 py-2 text-sm font-semibold transition ${
                  favorited
                    ? "border-pink-500 bg-pink-500/15 text-pink-400"
                    : "border-white/10 bg-white/5 text-slate-300 hover:border-pink-500/60 hover:text-white"
                }`}
              >
                {favorited ? "★ Favorited" : "☆ Favorite"}
              </button>
            </div>

            <div className="mt-4 flex flex-wrap items-center gap-3">
              <span className="inline-flex items-center gap-1.5 rounded-full bg-amber-500/15 px-3 py-1 text-sm font-semibold text-amber-400">
                ★ {score.toFixed(1)}
              </span>
              {anime.genre && (() => {
                const primaryGenre = (anime.genre || "")
                  .split("/")
                  .map((g) => g.trim())
                  .find(Boolean);
                return (
                  <Link
                    href={primaryGenre ? `/categories/${encodeURIComponent(primaryGenre)}` : "/categories"}
                    className="rounded-full bg-white/5 px-3 py-1 text-sm text-slate-300 transition hover:bg-pink-500/15 hover:text-pink-300"
                  >
                    Genre: {anime.genre}
                  </Link>
                );
              })()}
              {anime.year && (
                <Link
                  href={`/years/${anime.year}`}
                  className="rounded-full bg-white/5 px-3 py-1 text-sm text-slate-300 transition hover:bg-pink-500/15 hover:text-pink-300"
                >
                  Year: {anime.year}
                </Link>
              )}
              {anime.region && (
                <span className="rounded-full bg-white/5 px-3 py-1 text-sm text-slate-300">
                  Region: {anime.region}
                </span>
              )}
              {anime.status && (
                <span className="rounded-full bg-white/5 px-3 py-1 text-sm text-slate-300">
                  Status: {anime.status}
                </span>
              )}
              {anime.episodes && (
                <span className="rounded-full bg-white/5 px-3 py-1 text-sm text-slate-300">
                  Episodes: {anime.episodes}
                </span>
              )}
            </div>

            {/* Phase 11：Anime Information 结构化英文模块（仅基于 DB 字段） */}
            {(() => {
              const m = anime.month ?? 1;
              const seasonEn =
                m <= 2 || m === 12 ? "Winter" : m <= 5 ? "Spring" : m <= 8 ? "Summer" : "Fall";
              const release = anime.year
                ? `${seasonEn} ${anime.year}`
                : "Not announced";
              const statusEn =
                anime.status === "完结"
                  ? "Completed"
                  : anime.status === "连载" || anime.status === "连载中"
                  ? "Airing"
                  : anime.status === "未上映"
                  ? "Not yet aired"
                  : anime.status
                  ? anime.status
                  : "Unknown";
              const epCount = anime.episodes
                ? `${anime.episodes} episodes`
                : "Not announced";
              const typeEn =
                anime.episodes && anime.episodes > 1
                  ? "TV Series"
                  : anime.episodes === 1
                  ? "Movie"
                  : "Unknown";
              const gs = (anime.genre || "")
                .split(/[/，,、\s]+/)
                .map((g) => g.trim())
                .filter(Boolean);
              const genresEn = gs.map((g) => GENRE_EN[g] || g).join(", ") || "Anime";
              const updated = anime.updated_at
                ? new Date(anime.updated_at).toISOString().slice(0, 10)
                : null;
              return (
                <div className="mt-4 rounded-xl border border-white/10 bg-white/5 p-4">
                  <div className="text-sm font-semibold text-white">Anime Information</div>
                  <dl className="mt-2 grid grid-cols-1 gap-1.5 text-xs leading-relaxed text-slate-300 sm:grid-cols-2">
                    <div>
                      <dt className="inline font-semibold text-slate-200">Type: </dt>
                      <dd className="inline">{typeEn}</dd>
                    </div>
                    <div>
                      <dt className="inline font-semibold text-slate-200">Episodes: </dt>
                      <dd className="inline">
                        <Link
                          href={`/anime/${anime.slug || anime.id}/episodes/`}
                          className="text-indigo-300 transition hover:text-white hover:underline"
                        >
                          {epCount}
                        </Link>
                      </dd>
                    </div>
                    <div>
                      <dt className="inline font-semibold text-slate-200">Status: </dt>
                      <dd className="inline">{statusEn}</dd>
                    </div>
                    <div>
                      <dt className="inline font-semibold text-slate-200">Release period: </dt>
                      <dd className="inline">{release}</dd>
                    </div>
                    <div>
                      <dt className="inline font-semibold text-slate-200">Genres: </dt>
                      <dd className="inline">{genresEn}</dd>
                    </div>
                    <div>
                      <dt className="inline font-semibold text-slate-200">Score: </dt>
                      <dd className="inline">★ {score.toFixed(1)} / 10</dd>
                    </div>
                  </dl>
                  {updated && (
                    <div className="mt-2 border-t border-white/10 pt-2 text-xs text-slate-500">
                      Last updated: {updated}
                    </div>
                  )}
                </div>
              );
            })()}

            {/* Phase 11：Why This Anime Appears Here（数据信号说明，不写剧情） */}
            {(() => {
              const gs = (anime.genre || "")
                .split(/[/，,、\s]+/)
                .map((g) => g.trim())
                .filter(Boolean);
              const genresEn = gs.map((g) => GENRE_EN[g] || g).join(" and ") || "anime";
              const yearBit = anime.year ? ` from ${anime.year}` : "";
              const scoreBit = anime.score
                ? ` with a ${Number(anime.score).toFixed(1)}/10 fan rating`
                : "";
              return (
                <p className="mt-3 text-xs leading-relaxed text-slate-400">
                  <span className="font-semibold text-slate-300">
                    Why this anime appears here:{" "}
                  </span>
                  Recommended because it is a {genresEn} anime{yearBit}
                  {scoreBit}, selected from our database based on genre and audience signals.
                </p>
              );
            })()}

            {/* Phase 10：英文 Genres 区块（结构化，链接分类页） */}
            {(() => {
              const gs = (anime.genre || "")
                .split(/[/，,、\s]+/)
                .map((g) => g.trim())
                .filter(Boolean);
              if (gs.length === 0) return null;
              return (
                <div className="mt-5">
                  <h2 className="text-lg font-semibold text-white">Genres</h2>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {gs.map((g) => {
                      const en = GENRE_EN[g] || g;
                      const bg = bestGenreEntry(g);
                      const href = bg ? `/best-anime/${bg.slug}/` : `/categories/${encodeURIComponent(g)}/`;
                      return (
                        <Link
                          key={g}
                          href={href}
                          className="rounded-full bg-white/5 px-3 py-1 text-xs font-medium text-slate-300 transition hover:bg-indigo-500/20 hover:text-white"
                        >
                          {en}
                        </Link>
                      );
                    })}
                  </div>
                </div>
              );
            })()}

            {/* Phase 9：英文 SEO 内容区块（About / Who Should Watch，基于字段，不编造剧情） */}
            <h2 className="mt-5 text-lg font-semibold text-white">About This Anime</h2>
            <p className="mt-2 leading-relaxed text-slate-300">
              {anime.seo_description || anime.description || "Synopsis coming soon."}
            </p>

            <h2 className="mt-5 text-lg font-semibold text-white">Who Should Watch This Anime</h2>
            <p className="mt-2 leading-relaxed text-slate-300">{whoShouldWatchText(anime)}</p>

            {/* Meta list */}
            <div className="mt-5 grid grid-cols-1 gap-3 sm:grid-cols-2">
              {anime.author && (
                <div className="rounded-xl border border-white/10 bg-white/5 p-3 text-sm text-slate-300">
                  <span className="text-slate-500">Author:</span> {anime.author}
                </div>
              )}
              {anime.studio && (
                <Link
                  href={`/studio/${encodeURIComponent(anime.studio)}`}
                  className="rounded-xl border border-white/10 bg-white/5 p-3 text-sm text-slate-300 transition hover:border-pink-500/40 hover:text-white"
                >
                  <span className="text-slate-500">Studio:</span> {anime.studio}
                </Link>
              )}
            </div>

            {/* 简介 */}
            <h2 className="mt-5 text-lg font-semibold text-white">Synopsis</h2>
            <p className="mt-2 whitespace-pre-line leading-relaxed text-slate-300">
              {anime.description || "No synopsis available."}
            </p>

            {/* SEO Growth：Anime Like {title} 入口（简介下方） */}
            <Link
              href={`/anime/${anime.slug || anime.id}/similar/`}
              className="mt-4 inline-flex items-center gap-2 rounded-xl border border-indigo-500/40 bg-indigo-500/10 px-4 py-2.5 text-sm font-semibold text-indigo-300 transition hover:border-indigo-400 hover:bg-indigo-500/20 hover:text-white"
            >
              Anime Like {anime.title || anime.chinese_title}
              <span aria-hidden="true">→</span>
            </Link>

            {/* 详情 (SEO text) */}
            <h2 className="mt-6 text-lg font-semibold text-white">Details</h2>
            <p className="mt-2 whitespace-pre-line text-sm leading-relaxed text-slate-300">
              {friendlyText}
            </p>

            {/* Tags */}
            {tags.length > 0 && (
              <div className="mt-4 flex flex-wrap gap-2">
                {tags.map((t) => (
                  <Link
                    key={t}
                    href={`/tags/${encodeURIComponent(t)}`}
                    className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-medium text-slate-300 transition hover:border-pink-500/50 hover:text-pink-300"
                  >
                    {t}
                  </Link>
                ))}
              </div>
            )}

            {/* Admin */}
            {/* Admin link removed for launch */}
          </div>
        </div>
      </div>

      {/* 用户评分 */}
      <RatingWidget animeId={anime.id} />

      {/* ===== Play ===== */}
      <section className="mt-6 rounded-3xl border border-white/10 bg-white/5 p-5 backdrop-blur sm:p-6">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="flex items-center gap-3 text-lg font-semibold text-white">
            <span className="h-5 w-1 rounded-full bg-gradient-to-b from-pink-500 to-indigo-500" />
            Watch Online
          </h2>
          {playData && episodes.length > 0 && (
            <span className="text-xs text-slate-400">
              Total {episodes.length} episodes · Currently on episode {activeEp + 1}
            </span>
          )}
        </div>

        {!playData ? (
          <div className="py-12 text-center">
            <p className="text-4xl">🎬</p>
            <p className="mt-3 text-sm text-slate-500">No streaming source available</p>
          </div>
        ) : (
          <>
            {/* 线路切换 */}
            {playData.lines.length > 1 && (
              <div className="mb-4 flex gap-2 overflow-x-auto pb-1">
                {playData.lines.map((line, i) => (
                  <button
                    key={i}
                    type="button"
                    onClick={() => switchLine(i)}
                    className={`shrink-0 rounded-full px-4 py-2 text-sm font-medium transition ${
                      activeLine === i
                        ? "bg-gradient-to-r from-pink-600 to-fuchsia-600 text-white shadow-glow"
                        : "bg-white/5 text-slate-300 hover:bg-white/10"
                    }`}
                  >
                    {line.name || `Server ${i + 1}`}
                  </button>
                ))}
              </div>
            )}

            {/* 选集 */}
            {episodes.length > 0 ? (
              <div className="grid grid-cols-4 gap-2 sm:grid-cols-6 md:grid-cols-8 lg:grid-cols-10">
                {episodes.map((ep, idx) => (
                  <button
                    key={ep.ep}
                    type="button"
                    onClick={() => {
                      setActiveEp(idx);
                      if (ep.url) window.open(ep.url, "_blank", "noopener,noreferrer");
                    }}
                    className={`flex items-center justify-center rounded-lg py-2.5 text-sm font-medium transition ${
                      activeEp === idx
                        ? "bg-gradient-to-br from-pink-600 to-fuchsia-600 text-white shadow-glow"
                        : "bg-white/5 text-slate-300 hover:bg-white/10"
                    }`}
                  >
                    {ep.title || `Episode ${ep.ep}`}
                  </button>
                ))}
              </div>
            ) : (
              <div className="py-8 text-center">
                <p className="text-sm text-slate-500">No episodes listed</p>
              </div>
            )}
          </>
        )}
      </section>

      {/* 广告位已隐藏，保留 AdPlaceholder 组件供未来接入真实广告时使用 */}

      {/* ===== Characters（Sprint 6-D：SSR 实体内链 anime→character→voice-actor）===== */}
      {initialCharacters.length > 0 && (
        <section className="mt-10">
          <h2 className="mb-5 flex items-center gap-3 text-xl font-bold text-white">
            <span className="h-6 w-1 rounded-full bg-gradient-to-b from-pink-500 to-indigo-500" />
            Characters
          </h2>
          <div className="grid grid-cols-2 gap-5 sm:grid-cols-3 md:grid-cols-4">
            {initialCharacters.map((ch) => (
              <div
                key={ch.id}
                className="flex flex-col rounded-2xl border border-white/10 bg-white/5 p-4 backdrop-blur transition duration-300 hover:border-pink-500/50 hover:shadow-glow"
              >
                <Link
                  href={`/character/${ch.slug}/`}
                  className="truncate font-bold text-white transition hover:text-pink-300"
                >
                  {ch.name}
                </Link>
                {Array.isArray(ch.voice_actors) && ch.voice_actors.length > 0 && (
                  <p className="mt-2 text-xs leading-relaxed text-slate-400">
                    Voiced by: 
                    {(ch.voice_actors || []).map((va, idx) => (
                      <span key={va.id}>
                        {idx > 0 && <span className="text-slate-600"> / </span>}
                        <Link
                          href={`/voice-actor/${va.slug}/`}
                          className="text-pink-400 hover:underline"
                        >
                          {va.name}
                        </Link>
                      </span>
                    ))}
                  </p>
                )}
              </div>
            ))}
          </div>
        </section>
      )}

      {/* ===== Related ===== */}
      {related.length > 0 && (
        <section className="mt-10">
          <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
            <h2 className="flex items-center gap-3 text-xl font-bold text-white">
              <span className="h-6 w-1 rounded-full bg-gradient-to-b from-pink-500 to-indigo-500" />
              Related Anime
            </h2>
            <Link
              href={`/anime/${anime.slug || anime.id}/similar/`}
              className="inline-flex items-center gap-1.5 rounded-lg border border-indigo-500/40 bg-indigo-500/10 px-3 py-1.5 text-xs font-semibold text-indigo-300 transition hover:border-indigo-400 hover:bg-indigo-500/20 hover:text-white"
            >
              Anime Like {anime.title || anime.chinese_title}
              <span aria-hidden="true">→</span>
            </Link>
          </div>
          <div className="grid grid-cols-2 gap-5 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6">
            {related.map((a) => (
              <Link key={a.id} href={animePath(a)} className="group relative flex flex-col overflow-hidden rounded-2xl border border-white/10 bg-white/5 shadow-lg backdrop-blur transition duration-300 hover:-translate-y-1.5 hover:border-pink-500/50 hover:shadow-glow">
                <div className="relative h-40 w-full overflow-hidden">
                  <AnimeCover
                    anime={a}
                    className="h-40 w-full object-cover transition duration-500 group-hover:scale-110"
                  />
                  <div className="pointer-events-none absolute inset-0 bg-gradient-to-t from-slate-950/90 via-transparent to-transparent" />
                  <span className="absolute right-2 top-2 flex items-center gap-1 rounded-full bg-slate-950/80 px-2.5 py-1 text-xs font-bold text-amber-400 backdrop-blur">
                    ★ {Number(a.score ?? 0).toFixed(1)}
                  </span>
                </div>
                <div className="flex flex-1 flex-col p-3">
                  <h3 className="truncate font-bold text-white transition group-hover:text-pink-300">{a.title}</h3>
                  <p className="mt-1.5 line-clamp-2 text-xs leading-relaxed text-slate-400">{a.description || "暂无简介"}</p>
                </div>
              </Link>
            ))}
          </div>
        </section>
      )}

      {/* SEO Growth Phase 2 Task 4：详情页 -> 列表页 -> 详情页 内链网络 */}
      <section className="mt-10 rounded-3xl border border-white/10 bg-white/5 p-5 backdrop-blur sm:p-6">
        <h2 className="flex items-center gap-3 text-lg font-semibold text-white">
          <span className="h-5 w-1 rounded-full bg-gradient-to-b from-pink-500 to-indigo-500" />
          Explore More Anime
        </h2>
        <div className="mt-4 flex flex-wrap gap-2">
          <Link
            href="/trending-anime/"
            className="rounded-full border border-indigo-500/40 bg-indigo-500/10 px-4 py-1.5 text-sm font-medium text-indigo-300 transition hover:bg-indigo-500/20 hover:text-white"
          >
            Trending Anime
          </Link>
          <Link
            href="/discover-anime/"
            className="rounded-full border border-indigo-500/40 bg-indigo-500/10 px-4 py-1.5 text-sm font-medium text-indigo-300 transition hover:bg-indigo-500/20 hover:text-white"
          >
            Discover Anime
          </Link>
          <Link
            href="/best-anime/"
            className="rounded-full border border-indigo-500/40 bg-indigo-500/10 px-4 py-1.5 text-sm font-medium text-indigo-300 transition hover:bg-indigo-500/20 hover:text-white"
          >
            Best Anime Lists
          </Link>
          {(() => {
            const bg = bestGenreEntry(anime.genre);
            if (!bg) return null;
            return (
              <Link
                href={`/best-anime/${bg.slug}/`}
                className="rounded-full border border-indigo-500/40 bg-indigo-500/10 px-4 py-1.5 text-sm font-medium text-indigo-300 transition hover:bg-indigo-500/20 hover:text-white"
              >
                Popular {bg.label} Anime
              </Link>
            );
          })()}
          {(() => {
            const fslug = matchFranchise(anime.title, anime.chinese_title);
            if (!fslug) return null;
            return (
              <Link
                href={`/anime-series/${fslug}/`}
                className="rounded-full border border-amber-500/40 bg-amber-500/10 px-4 py-1.5 text-sm font-medium text-amber-300 transition hover:bg-amber-500/20 hover:text-white"
              >
                {FRANCHISE_DEFS[fslug].name} Series
              </Link>
            );
          })()}
          <Link
            href={`/anime/${anime.slug || anime.id}/similar/`}
            className="rounded-full border border-indigo-500/40 bg-indigo-500/10 px-4 py-1.5 text-sm font-medium text-indigo-300 transition hover:bg-indigo-500/20 hover:text-white"
          >
            Similar Anime
          </Link>
          <Link
            href="/seasons/"
            className="rounded-full border border-indigo-500/40 bg-indigo-500/10 px-4 py-1.5 text-sm font-medium text-indigo-300 transition hover:bg-indigo-500/20 hover:text-white"
          >
            Season Pages
          </Link>
          <Link
            href={`/season/${(() => { const cs = currentSeason(); return `${cs.season}-${cs.year}-anime`; })()}/`}
            className="rounded-full border border-indigo-500/40 bg-indigo-500/10 px-4 py-1.5 text-sm font-medium text-indigo-300 transition hover:bg-indigo-500/20 hover:text-white"
          >
            {(() => { const cs = currentSeason(); return `Popular This ${cs.label}`; })()}
          </Link>
          <Link
            href="/new-anime/"
            className="rounded-full border border-indigo-500/40 bg-indigo-500/10 px-4 py-1.5 text-sm font-medium text-indigo-300 transition hover:bg-indigo-500/20 hover:text-white"
          >
            New Anime
          </Link>
          {anime.year && (
            <Link
              href={`/years/${anime.year}`}
              className="rounded-full border border-indigo-500/40 bg-indigo-500/10 px-4 py-1.5 text-sm font-medium text-indigo-300 transition hover:bg-indigo-500/20 hover:text-white"
            >
              {anime.year} Anime
            </Link>
          )}
          {(() => {
            const wslug = matchWatchOrderFranchise(anime.title, anime.chinese_title);
            if (!wslug) return null;
            return (
              <Link
                href={`/watch-order/${wslug}/`}
                className="rounded-full border border-amber-500/40 bg-amber-500/10 px-4 py-1.5 text-sm font-medium text-amber-300 transition hover:bg-amber-500/20 hover:text-white"
              >
                {FRANCHISES[wslug].name} Watch Order
              </Link>
            );
          })()}
        </div>
      </section>

      {/* 广告位已隐藏，保留 AdPlaceholder 组件供未来接入真实广告时使用 */}
    </div>
  );
}
