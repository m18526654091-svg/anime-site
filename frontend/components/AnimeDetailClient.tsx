"use client";

import Image from "next/image";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { fetchRelated } from "@/lib/api";
import AdPlaceholder from "@/components/AdPlaceholder";
import type { Anime } from "@/types";

interface Props {
  anime: Anime | null;
  error: string;
}

export default function AnimeDetailClient({ anime, error }: Props) {
  const [related, setRelated] = useState<Anime[]>([]);

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

  if (error || !anime) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-24 text-center">
        <p className="text-4xl">😢</p>
        <p className="mt-4 text-slate-400">{error || "Anime not found"}</p>
        <Link
          href="/"
          className="mt-6 inline-block rounded-lg bg-white/5 px-5 py-2 text-pink-400 transition hover:bg-white/10"
        >
          ← Back to home
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
    const desc = seoText || "Detailed anime information page.";
    const extras = tags.length > 0 ? ` Tags: ${tags.join(", ")}.` : "";
    const related = `If you like ${anime.title}, you may also like other anime in ${anime.genre || "this genre"}.`;

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
      {/* ===== Main info card ===== */}
      <div className="relative overflow-hidden rounded-3xl border border-white/10 bg-white/5 shadow-2xl backdrop-blur">
        <div className="absolute inset-x-0 top-0 h-40 bg-gradient-to-r from-pink-600/25 to-indigo-600/25" />

        <div className="relative flex flex-col gap-6 p-6 sm:p-8 md:flex-row">
          {/* Poster */}
          <div className="mx-auto w-52 shrink-0 sm:mx-0 sm:w-56">
            {anime.cover ? (
              <Image
                src={anime.cover}
                alt={anime.title}
                width={224}
                height={298}
                priority
                className="aspect-[3/4] w-full rounded-2xl border border-white/10 object-cover shadow-glow-indigo"
              />
            ) : (
              <div className="flex aspect-[3/4] w-full items-center justify-center rounded-2xl bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-600 shadow-glow-indigo">
                <span className="text-8xl font-black text-white/80">
                  {anime.title.slice(0, 1)}
                </span>
              </div>
            )}
          </div>

          {/* Info */}
          <div className="flex-1">
            <h1 className="text-3xl font-black leading-tight text-white sm:text-4xl">
              {anime.title}
            </h1>

            <div className="mt-4 flex flex-wrap items-center gap-3">
              <span className="inline-flex items-center gap-1.5 rounded-full bg-amber-500/15 px-3 py-1 text-sm font-semibold text-amber-400">
                ★ {score.toFixed(1)}
              </span>
              {anime.genre && (
                <span className="rounded-full bg-white/5 px-3 py-1 text-sm text-slate-300">
                  Genre: {anime.genre}
                </span>
              )}
              {anime.year && (
                <span className="rounded-full bg-white/5 px-3 py-1 text-sm text-slate-300">
                  Year: {anime.year}
                </span>
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

            {/* Meta list */}
            <div className="mt-5 grid grid-cols-1 gap-3 sm:grid-cols-2">
              {anime.author && (
                <div className="rounded-xl border border-white/10 bg-white/5 p-3 text-sm text-slate-300">
                  <span className="text-slate-500">Author:</span> {anime.author}
                </div>
              )}
              {anime.studio && (
                <div className="rounded-xl border border-white/10 bg-white/5 p-3 text-sm text-slate-300">
                  <span className="text-slate-500">Studio:</span> {anime.studio}
                </div>
              )}
            </div>

            {/* Synopsis */}
            <h2 className="mt-5 text-lg font-semibold text-white">Synopsis</h2>
            <p className="mt-2 whitespace-pre-line leading-relaxed text-slate-300">
              {anime.description || "No description"}
            </p>

            {/* Details (SEO text) */}
            <h2 className="mt-6 text-lg font-semibold text-white">Details</h2>
            <p className="mt-2 whitespace-pre-line text-sm leading-relaxed text-slate-300">
              {friendlyText}
            </p>

            {/* Tags */}
            {tags.length > 0 && (
              <div className="mt-4 flex flex-wrap gap-2">
                {tags.map((t) => (
                  <span
                    key={t}
                    className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-medium text-slate-300"
                  >
                    {t}
                  </span>
                ))}
              </div>
            )}

            {/* Admin */}
            {/* Admin link removed for launch */}
          </div>
        </div>
      </div>

      {/* ===== Play ===== */}
      <section className="mt-6 rounded-3xl border border-white/10 bg-white/5 p-5 backdrop-blur sm:p-6">
        <h2 className="mb-4 flex items-center gap-3 text-lg font-semibold text-white">
          <span className="h-5 w-1 rounded-full bg-gradient-to-b from-pink-500 to-indigo-500" />
          在线播放
        </h2>

        {!playData ? (
          <p className="py-8 text-center text-sm text-slate-500">暂无播放资源</p>
        ) : (
          <>
            {/* 线路切换 */}
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
                        ? "bg-gradient-to-br from-pink-600 to-fuchsia-600 text-white"
                        : "bg-white/5 text-slate-300 hover:bg-white/10"
                    }`}
                  >
                    {ep.title || `第${ep.ep}集`}
                  </button>
                ))}
              </div>
            ) : (
              <p className="py-4 text-center text-sm text-slate-500">暂无选集</p>
            )}
          </>
        )}
      </section>

      {/* ===== Ad (middle) ===== */}
      <div className="mt-6">
        <AdPlaceholder />
      </div>

      {/* ===== Related ===== */}
      {related.length > 0 && (
        <section className="mt-10">
          <h2 className="mb-5 flex items-center gap-3 text-xl font-bold text-white">
            <span className="h-6 w-1 rounded-full bg-gradient-to-b from-pink-500 to-indigo-500" />
            Related Anime
          </h2>
          <div className="grid grid-cols-2 gap-5 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6">
            {related.map((a) => (
              <Link key={a.id} href={`/anime/${a.id}`} className="group relative flex flex-col overflow-hidden rounded-2xl border border-white/10 bg-white/5 shadow-lg backdrop-blur transition duration-300 hover:-translate-y-1.5 hover:border-pink-500/50 hover:shadow-glow">
                <div className="relative h-40 w-full overflow-hidden">
                  {a.cover ? (
                    <Image
                      src={a.cover}
                      alt={a.title}
                      fill
                      loading="lazy"
                      sizes="(max-width: 640px) 50vw, (max-width: 768px) 33vw, (max-width: 1024px) 25vw, 16.667vw"
                      className="object-cover transition duration-500 group-hover:scale-110"
                    />
                  ) : (
                    <div className="flex h-40 w-full items-center justify-center bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-600 transition duration-500 group-hover:scale-110">
                      <span className="text-4xl font-black text-white/85">{a.title?.slice(0, 1) || "A"}</span>
                    </div>
                  )}
                  <div className="pointer-events-none absolute inset-0 bg-gradient-to-t from-slate-950/90 via-transparent to-transparent" />
                  <span className="absolute right-2 top-2 flex items-center gap-1 rounded-full bg-slate-950/80 px-2.5 py-1 text-xs font-bold text-amber-400 backdrop-blur">
                    ★ {Number(a.score ?? 0).toFixed(1)}
                  </span>
                </div>
                <div className="flex flex-1 flex-col p-3">
                  <h3 className="truncate font-bold text-white transition group-hover:text-pink-300">{a.title}</h3>
                  <p className="mt-1.5 line-clamp-2 text-xs leading-relaxed text-slate-400">{a.description || "No description"}</p>
                </div>
              </Link>
            ))}
          </div>
        </section>
      )}

      {/* ===== Ad (bottom) ===== */}
      <div className="mt-6">
        <AdPlaceholder />
      </div>
    </div>
  );
}
