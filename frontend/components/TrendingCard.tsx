import Link from "next/link";
import type { Anime } from "@/types";
import AnimeCover from "@/components/AnimeCover";
import { animePath } from "@/lib/slug";

/**
 * Trending / Discover 页使用的英文标题卡片。
 * 包含：score、genre、year、详情链接、Similar 链接 —— 支持
 * Detail -> Detail 与 Detail -> Similar 的发现路径。
 */
export default function TrendingCard({ anime }: { anime: Anime }) {
  const score = Number(anime.score ?? 0);
  const slug = anime.slug || String(anime.id);
  return (
    <div className="group relative flex flex-col overflow-hidden rounded-2xl border border-white/10 bg-white/5 shadow-lg backdrop-blur transition-all duration-300 hover:-translate-y-1.5 hover:border-pink-500/50 hover:shadow-pink-500/20 hover:shadow-2xl">
      <Link href={animePath(anime)} aria-label={anime.title || anime.chinese_title}>
        <div className="relative overflow-hidden">
          <AnimeCover
            anime={anime}
            className="aspect-[2/3] w-full object-cover transition duration-500 group-hover:scale-110"
          />
          <div className="pointer-events-none absolute inset-0 bg-gradient-to-t from-slate-950/90 via-transparent to-transparent" />
          <span className="absolute right-2 top-2 flex items-center gap-1 rounded-full bg-slate-950/80 px-2.5 py-1 text-xs font-bold text-amber-400 backdrop-blur-sm">
            ★ {score.toFixed(1)}
          </span>
          {anime.genre && (
            <span className="absolute left-2 top-2 rounded-full bg-pink-600/90 px-2.5 py-1 text-xs font-medium text-white backdrop-blur-sm">
              {anime.genre}
            </span>
          )}
          {anime.year && (
            <span className="absolute bottom-2 left-2 rounded-md bg-slate-950/70 px-2 py-0.5 text-xs font-medium text-slate-200 backdrop-blur-sm">
              📅 {anime.year}
            </span>
          )}
        </div>
      </Link>
      <div className="flex flex-1 flex-col p-3.5">
        <Link href={animePath(anime)}>
          <h3 className="truncate font-bold text-white transition group-hover:text-pink-300">
            {anime.title || anime.chinese_title}
          </h3>
        </Link>
        <p className="mt-1.5 line-clamp-2 text-xs leading-relaxed text-slate-400">
          {anime.description || ""}
        </p>
        <div className="mt-auto pt-2.5">
          <Link
            href={`/anime/${slug}/similar/`}
            className="inline-flex items-center gap-1 rounded-full border border-indigo-500/40 bg-indigo-500/10 px-3 py-1 text-xs font-semibold text-indigo-300 transition hover:bg-indigo-500/20 hover:text-white"
          >
            Similar Anime →
          </Link>
        </div>
      </div>
    </div>
  );
}
