import Link from "next/link";
import type { Anime } from "@/types";
import AnimeCover from "@/components/AnimeCover";
import { animePath } from "@/lib/slug";

export default function AnimeCard({ anime }: { anime: Anime }) {
  const score = Number(anime.score ?? 0);

    return (
    <Link
      href={animePath(anime)}
      aria-label={`观看 ${anime.chinese_title || anime.title} - AnimeHub`}
      className="group relative flex flex-col overflow-hidden rounded-2xl border border-white/10 bg-white/5 shadow-lg backdrop-blur transition-all duration-300 hover:-translate-y-1.5 hover:border-pink-500/50 hover:shadow-pink-500/20 hover:shadow-2xl"
    >
      {/* Cover area */}
      <div className="relative overflow-hidden">
        <AnimeCover
          anime={anime}
          className="aspect-[2/3] w-full object-cover transition duration-500 group-hover:scale-110"
        />

        {/* Dark gradient overlay to make badges pop */}
        <div className="pointer-events-none absolute inset-0 bg-gradient-to-t from-slate-950/90 via-transparent to-transparent" />

        {/* Score badge — top right */}
        <span className="absolute right-2 top-2 flex items-center gap-1 rounded-full bg-slate-950/80 px-2.5 py-1 text-xs font-bold text-amber-400 backdrop-blur-sm">
          ★ {score.toFixed(1)}
        </span>

        {/* Genre tag — top left */}
        {anime.genre && (
          <span className="absolute left-2 top-2 rounded-full bg-pink-600/90 px-2.5 py-1 text-xs font-medium text-white backdrop-blur-sm">
            {anime.genre}
          </span>
        )}

        {/* Year badge — bottom left */}
        {anime.year && (
          <span className="absolute bottom-2 left-2 rounded-md bg-slate-950/70 px-2 py-0.5 text-xs font-medium text-slate-200 backdrop-blur-sm">
            📅 {anime.year}
          </span>
        )}

        {/* Hover 播放提示（纯渐变遮罩，专业风格） */}
        <div className="pointer-events-none absolute inset-0 bg-gradient-to-t from-slate-950/20 via-transparent to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100" />
      </div>

      {/* Info area */}
      <div className="flex flex-1 flex-col p-3.5">
        <div className="flex items-center gap-2">
          <h3 className="truncate font-bold text-white transition group-hover:text-pink-300">
            {anime.chinese_title || anime.title}
          </h3>
          {anime.status && (
            <span
              className={`shrink-0 rounded-full px-2 py-0.5 text-xs font-medium ${
                anime.status.includes("完结")
                  ? "bg-emerald-500/15 text-emerald-400"
                  : anime.status.includes("连载")
                  ? "bg-sky-500/15 text-sky-400"
                  : "bg-white/5 text-slate-300"
              }`}
            >
              {anime.status}
            </span>
          )}
        </div>
        <p className="mt-1.5 line-clamp-2 text-xs leading-relaxed text-slate-400">
          {anime.description || "暂无简介"}
        </p>
      </div>
    </Link>
  );
}