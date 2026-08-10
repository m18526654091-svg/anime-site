import Link from "next/link";
import AnimeCard from "./AnimeCard";
import type { Anime } from "@/types";

interface Props {
  title: string;
  subtitle?: string;
  items: Anime[];
  total: number;
  page: number;
  pages: number;
  pageUrl: (page: number) => string;
}

export default function ListPageView({
  title,
  subtitle,
  items,
  total,
  page,
  pages,
  pageUrl,
}: Props) {
  const linkCls =
    "h-9 w-9 rounded-xl border border-white/10 text-sm font-semibold text-slate-300 transition hover:border-pink-500/60 hover:text-white";

  return (
    <div className="mx-auto max-w-7xl animate-fade-in px-4 py-8">
      <header className="mb-8">
        <h1 className="text-3xl font-black text-white">{title}</h1>
        {subtitle && <p className="mt-2 text-slate-400">{subtitle}</p>}
      </header>

      {items.length === 0 ? (
        <p className="py-20 text-center text-slate-500">暂无内容，敬请期待。</p>
      ) : (
        <div className="grid grid-cols-2 gap-5 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6">
          {items.map((a) => (
            <AnimeCard key={a.id} anime={a} />
          ))}
        </div>
      )}

      {pages > 1 && (
        <nav className="mt-12 flex flex-wrap items-center justify-center gap-2">
          {page > 1 && (
            <Link href={pageUrl(page - 1)} className={linkCls}>
              ←
            </Link>
          )}
          {Array.from({ length: pages }, (_, i) => i + 1)
            .filter((p) => p === 1 || p === pages || Math.abs(p - page) <= 2)
            .reduce<Array<number | "…">>((acc, p, idx, arr) => {
              if (idx > 0 && p - (arr[idx - 1] as number) > 1) acc.push("…");
              acc.push(p);
              return acc;
            }, [])
            .map((p, idx) =>
              p === "…" ? (
                <span key={`e-${idx}`} className="px-1 text-slate-500">
                  …
                </span>
              ) : (
                <Link
                  key={p}
                  href={pageUrl(p)}
                  className={`${linkCls} ${
                    p === page
                      ? "bg-gradient-to-br from-pink-600 to-fuchsia-600 text-white shadow-glow"
                      : ""
                  }`}
                >
                  {p}
                </Link>
              )
            )}
          {page < pages && (
            <Link href={pageUrl(page + 1)} className={linkCls}>
              →
            </Link>
          )}
        </nav>
      )}

      <p className="mt-4 text-center text-xs text-slate-500">
        共 {total} 部作品
      </p>
    </div>
  );
}