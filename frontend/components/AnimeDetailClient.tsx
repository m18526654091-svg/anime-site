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
import AdPlaceholder from "@/components/AdPlaceholder";
import AnimeCover from "@/components/AnimeCover";
import RatingWidget from "@/components/RatingWidget";
import type { Anime, Episode } from "@/types";

interface Props {
  anime: Anime | null;
  error: string;
  initialRelated?: Anime[];
}

export default function AnimeDetailClient({ anime, error, initialRelated = [] }: Props) {
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
        <p className="mt-4 text-slate-400">{error || "动漫不存在"}</p>
        <Link
          href="/"
          className="mt-6 inline-block rounded-lg bg-white/5 px-5 py-2 text-pink-400 transition hover:bg-white/10"
        >
          ← 返回首页
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
      anime.genre ? `类型: ${anime.genre}` : "",
      anime.year ? `年份: ${anime.year}` : "",
      anime.region ? `地区: ${anime.region}` : "",
      anime.author ? `作者: ${anime.author}` : "",
      anime.studio ? `制作公司: ${anime.studio}` : "",
      anime.status ? `状态: ${anime.status}` : "",
      anime.episodes ? `集数: ${anime.episodes}` : "",
    ].filter(Boolean);

    const intro = parts.join(" | ");
    const desc = seoText || "暂无详细介绍。";
    const extras = tags.length > 0 ? ` 标签: ${tags.join(", ")}.` : "";
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
            aria-label="面包屑"
            className="mb-6 flex flex-wrap items-center gap-1.5 text-sm text-slate-400"
          >
            <Link href="/" className="hover:text-pink-400">
              首页
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
                  {anime.year}年动漫
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
                {!loadingEpisodes && dbEpisodes.length > 0 && (
                  <div className="mt-2">
                    <Link
                      href={`/watch/${anime.id}`}
                      className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-pink-600 to-fuchsia-600 px-5 py-2.5 text-sm font-semibold text-white shadow-glow transition hover:from-pink-500 hover:to-fuchsia-500"
                    >
                      开始播放
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
                {favorited ? "★ 已收藏" : "☆ 收藏"}
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
                    类型: {anime.genre}
                  </Link>
                );
              })()}
              {anime.year && (
                <Link
                  href={`/years/${anime.year}`}
                  className="rounded-full bg-white/5 px-3 py-1 text-sm text-slate-300 transition hover:bg-pink-500/15 hover:text-pink-300"
                >
                  年份: {anime.year}
                </Link>
              )}
              {anime.region && (
                <span className="rounded-full bg-white/5 px-3 py-1 text-sm text-slate-300">
                  地区: {anime.region}
                </span>
              )}
              {anime.status && (
                <span className="rounded-full bg-white/5 px-3 py-1 text-sm text-slate-300">
                  状态: {anime.status}
                </span>
              )}
              {anime.episodes && (
                <span className="rounded-full bg-white/5 px-3 py-1 text-sm text-slate-300">
                  集数: {anime.episodes}
                </span>
              )}
            </div>

            {/* Meta list */}
            <div className="mt-5 grid grid-cols-1 gap-3 sm:grid-cols-2">
              {anime.author && (
                <div className="rounded-xl border border-white/10 bg-white/5 p-3 text-sm text-slate-300">
                  <span className="text-slate-500">作者:</span> {anime.author}
                </div>
              )}
              {anime.studio && (
                <Link
                  href={`/studio/${encodeURIComponent(anime.studio)}`}
                  className="rounded-xl border border-white/10 bg-white/5 p-3 text-sm text-slate-300 transition hover:border-pink-500/40 hover:text-white"
                >
                  <span className="text-slate-500">制作公司:</span> {anime.studio}
                </Link>
              )}
            </div>

            {/* 简介 */}
            <h2 className="mt-5 text-lg font-semibold text-white">简介</h2>
            <p className="mt-2 whitespace-pre-line leading-relaxed text-slate-300">
              {anime.description || "暂无简介"}
            </p>

            {/* 详情 (SEO text) */}
            <h2 className="mt-6 text-lg font-semibold text-white">详情</h2>
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
            在线播放
          </h2>
          {playData && episodes.length > 0 && (
            <span className="text-xs text-slate-400">
              共 {episodes.length} 集 · 当前第 {activeEp + 1} 集
            </span>
          )}
        </div>

        {!playData ? (
          <div className="py-12 text-center">
            <p className="text-4xl">🎬</p>
            <p className="mt-3 text-sm text-slate-500">暂无播放资源</p>
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
                    {line.name || `线路${i + 1}`}
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
                    {ep.title || `第${ep.ep}集`}
                  </button>
                ))}
              </div>
            ) : (
              <div className="py-8 text-center">
                <p className="text-sm text-slate-500">暂无选集</p>
              </div>
            )}
          </>
        )}
      </section>

      {/* 广告位已隐藏，保留 AdPlaceholder 组件供未来接入真实广告时使用 */}

      {/* ===== Related ===== */}
      {related.length > 0 && (
        <section className="mt-10">
          <h2 className="mb-5 flex items-center gap-3 text-xl font-bold text-white">
            <span className="h-6 w-1 rounded-full bg-gradient-to-b from-pink-500 to-indigo-500" />
            相关推荐
          </h2>
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

      {/* 广告位已隐藏，保留 AdPlaceholder 组件供未来接入真实广告时使用 */}
    </div>
  );
}
