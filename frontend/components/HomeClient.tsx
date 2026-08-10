"use client";

import { useCallback, useEffect, useState } from "react";
import AnimeCard from "@/components/AnimeCard";
import {
  apiErrorMessage,
  fetchAnimeBySort,
  fetchAnimePage,
  fetchCategories,
} from "@/lib/api";
import type { AnimePage } from "@/types";

const PAGE_SIZE = 18;

export default function HomeClient({ initialPage }: { initialPage: AnimePage }) {
  const [pageData, setPageData] = useState<AnimePage>(initialPage);
  const [q, setQ] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [categories, setCategories] = useState<{ genre: string; count: number }[]>([]);
  const [latest, setLatest] = useState<AnimePage>({ items: [], total: 0, page: 1, page_size: 12, pages: 0 });
  const [hot, setHot] = useState<AnimePage>({ items: [], total: 0, page: 1, page_size: 12, pages: 0 });

  const load = useCallback(async (query: string, page: number) => {
    setLoading(true);
    setError("");
    try {
      const data = await fetchAnimePage(query || undefined, page, PAGE_SIZE);
      setPageData(data);
    } catch (err) {
      setPageData({ items: [], total: 0, page: 1, page_size: PAGE_SIZE, pages: 0 });
      setError(apiErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load("", 1);
  }, [load]);

  useEffect(() => {
    fetchCategories().then(setCategories).catch(() => {});
  }, []);

  useEffect(() => {
    fetchAnimeBySort("latest", 12).then(setLatest).catch(() => {});
  }, []);

  useEffect(() => {
    fetchAnimeBySort("score", 12).then(setHot).catch(() => {});
  }, []);

  const { items, total, pages } = pageData;
  const currentPage = pageData.page;

  const searching = q.trim().length > 0;

  function goToPage(p: number) {
    if (p < 1 || p > pages) return;
    load(q, p);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  const sectionTitle = (label: string, gradient: string) => (
    <h2 className="mb-5 flex items-center gap-3 text-xl font-bold text-white">
      <span className={`h-6 w-1 rounded-full bg-gradient-to-b ${gradient}`} />
      {label}
    </h2>
  );

  return (
    <div className="mx-auto max-w-7xl px-4 pb-16">
      {/* ===== Search & Categories ===== */}
      <section className="mt-6">
        <div className="flex flex-col gap-4 rounded-3xl border border-white/10 bg-white/5 p-5 sm:p-6 backdrop-blur">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              load(q, 1);
            }}
            className="flex gap-2"
          >
            <div className="relative flex-1">
              <span className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-slate-500">
                Search
              </span>
              <input
                value={q}
                onChange={(e) => setQ(e.target.value)}
                placeholder="Search anime..."
                className="w-full rounded-xl border border-white/10 bg-slate-950/70 py-3 pl-10 pr-4 text-white placeholder-slate-500 shadow-inner backdrop-blur focus:border-pink-500/60 focus:outline-none focus:ring-2 focus:ring-pink-500/40"
              />
            </div>
            <button
              type="submit"
              className="rounded-xl bg-gradient-to-r from-pink-600 to-fuchsia-600 px-6 py-3 font-semibold text-white shadow-glow transition hover:brightness-110"
            >
              Search
            </button>
          </form>

          {categories.length > 0 && (
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => {
                  setQ("");
                  load("", 1);
                }}
                className={`rounded-full px-4 py-1.5 text-sm font-medium transition ${
                  !searching
                    ? "bg-gradient-to-r from-pink-600 to-fuchsia-600 text-white"
                    : "border border-white/10 text-slate-300 hover:border-pink-500/60 hover:text-white"
                }`}
              >
                All
              </button>
              {categories.slice(0, 20).map((c) => (
                <button
                  key={c.genre}
                  onClick={() => {
                    setQ("");
                    load(c.genre, 1);
                  }}
                  className={`rounded-full px-4 py-1.5 text-sm font-medium transition ${
                    !searching && pageData.items[0]?.genre === c.genre
                      ? "bg-gradient-to-r from-pink-600 to-fuchsia-600 text-white"
                      : "border border-white/10 text-slate-300 hover:border-pink-500/60 hover:text-white"
                  }`}
                >
                  {c.genre} ({c.count})
                </button>
              ))}
            </div>
          )}
        </div>
      </section>

      {/* ===== Status ===== */}
      {loading && <p className="py-16 text-center text-slate-400">Loading...</p>}
      {!loading && error && <p className="py-16 text-center text-red-400">{error}</p>}

      {!loading && !error && (
        <div id="home-grid" className="mt-8 animate-fade-in">
          {/* ===== Search Results ===== */}
          {searching ? (
            <section className="mb-10">
              {sectionTitle(`Search Results (${total})`, "from-pink-500 to-indigo-500")}
              {items.length === 0 ? (
                <p className="py-16 text-center text-slate-500">No results for "{q}"</p>
              ) : (
                <div className="grid grid-cols-2 gap-5 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
                  {items.map((a) => (
                    <AnimeCard key={a.id} anime={a} />
                  ))}
                </div>
              )}
            </section>
          ) : (
            <>
              {/* ===== Latest ===== */}
              {latest.items.length > 0 && (
                <section className="mb-10">
                  {sectionTitle("Latest Updates", "from-sky-400 to-indigo-500")}
                  <div className="grid grid-cols-2 gap-5 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6">
                    {latest.items.map((a) => (
                      <AnimeCard key={a.id} anime={a} />
                    ))}
                  </div>
                </section>
              )}

              {/* ===== Hot ===== */}
              {hot.items.length > 0 && (
                <section className="mb-10">
                  {sectionTitle("Hot Picks", "from-amber-400 to-pink-500")}
                  <div className="grid grid-cols-2 gap-5 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6">
                    {hot.items.map((a) => (
                      <AnimeCard key={a.id} anime={a} />
                    ))}
                  </div>
                </section>
              )}

              {/* ===== All ===== */}
              <section className="mb-10">
                {sectionTitle(`All Anime (${total})`, "from-pink-500 to-indigo-500")}
                {items.length === 0 ? (
                  <p className="py-16 text-center text-slate-500">No data</p>
                ) : (
                  <div className="grid grid-cols-2 gap-5 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
                    {items.map((a) => (
                      <AnimeCard key={a.id} anime={a} />
                    ))}
                  </div>
                )}
              </section>
            </>
          )}

          {/* ===== Pagination ===== */}
          {pages > 1 && !error && (
            <div className="mt-10 flex flex-col items-center gap-3">
              <div className="flex flex-wrap items-center justify-center gap-2">
                <button
                  onClick={() => goToPage(currentPage - 1)}
                  disabled={currentPage <= 1}
                  className="rounded-xl border border-white/10 px-4 py-2 text-sm text-slate-300 transition hover:border-pink-500/60 hover:text-white disabled:cursor-not-allowed disabled:opacity-40"
                >
                  Prev
                </button>

                {Array.from({ length: pages }, (_, i) => i + 1)
                  .filter((p) => p === 1 || p === pages || Math.abs(p - currentPage) <= 2)
                  .reduce<Array<number | "...">>((acc, p, idx, arr) => {
                    if (idx > 0 && p - (arr[idx - 1] as number) > 1) acc.push("...");
                    acc.push(p);
                    return acc;
                  }, [])
                  .map((p, idx) =>
                    p === "..." ? (
                      <span key={`e-${idx}`} className="px-1 text-slate-500">
                        ...
                      </span>
                    ) : (
                      <button
                        key={p}
                        onClick={() => goToPage(p)}
                        className={`h-9 w-9 rounded-xl text-sm font-semibold transition ${
                          p === currentPage
                            ? "bg-gradient-to-br from-pink-600 to-fuchsia-600 text-white shadow-glow"
                            : "border border-white/10 text-slate-300 hover:border-pink-500/60 hover:text-white"
                        }`}
                      >
                        {p}
                      </button>
                    )
                  )}

                <button
                  onClick={() => goToPage(currentPage + 1)}
                  disabled={currentPage >= pages}
                  className="rounded-xl border border-white/10 px-4 py-2 text-sm text-slate-300 transition hover:border-pink-500/60 hover:text-white disabled:cursor-not-allowed disabled:opacity-40"
                >
                  Next
                </button>
              </div>
              <p className="text-xs text-slate-500">
                Page {currentPage} / {pages} · Total {total} items
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
