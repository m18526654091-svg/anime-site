import Link from "next/link";
import type { Anime } from "@/types";

function AnimeCover({ anime }: { anime: Anime }) {
  if (anime.cover) {
    return (
      // eslint-disable-next-line @next/next/no-img-element
      <img
        src={anime.cover}
        alt={anime.title}
        className="h-52 w-full object-cover transition duration-500 group-hover:scale-110 sm:h-60"
      />
    );
  }
  return (
    <div className="flex h-52 w-full flex-col items-center justify-center gap-2 bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-600 transition duration-500 group-hover:scale-110 sm:h-60">
      <span className="text-6xl font-black text-white/85">
        {anime.title?.slice(0, 1) || "漫"}
      </span>
    </div>
  );
}

export default function AnimeCard({ anime }: { anime: Anime }) {
  const score = Number(anime.score ?? 0);

  return (
    <Link
      href={`/anime/${anime.id}`}
      className="group relative flex flex-col overflow-hidden rounded-2xl border border-white/10 bg-white/5 shadow-lg backdrop-blur transition duration-300 hover:-translate-y-1.5 hover:border-pink-500/50 hover:shadow-glow"
    >
      <div className="relative overflow-hidden">
        <AnimeCover anime={anime} />
        {/* gradient overlay */}
        <div className="pointer-events-none absolute inset-0 bg-gradient-to-t from-slate-950/90 via-transparent to-transparent" />
        {/* score badge */}
        <span className="absolute right-2 top-2 flex items-center gap-1 rounded-full bg-slate-950/80 px-2.5 py-1 text-xs font-bold text-amber-400 backdrop-blur">
          ★ {score.toFixed(1)}
        </span>
        {/* genre tag */}
        {anime.genre && (
          <span className="absolute left-2 top-2 rounded-full bg-pink-600/80 px-2.5 py-1 text-xs font-medium text-white backdrop-blur">
            {anime.genre}
          </span>
        )}
        {/* year badge */}
        {anime.year && (
          <span className="absolute bottom-2 left-2 rounded-md bg-slate-950/70 px-2 py-0.5 text-xs font-medium text-slate-200 backdrop-blur">
            📅 {anime.year}
          </span>
        )}
      </div>

      <div className="flex flex-1 flex-col p-3.5">
        <h3 className="truncate font-bold text-white transition group-hover:text-pink-300">
          {anime.title}
        </h3>
        <p className="mt-1.5 line-clamp-2 text-xs leading-relaxed text-slate-400">
          {anime.description || "暂无简介"}
        </p>
      </div>
    </Link>
  );
}