"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import AnimeCard from "@/components/AnimeCard";
import HeroBanner from "@/components/HeroBanner";
import type { FeaturedAnime, TrendingItem } from "@/components/HeroBanner";
import {
  apiErrorMessage,
  fetchAnimeByFilter,
  fetchAnimeBySort,
  fetchAnimePage,
} from "@/lib/api";
import type { Anime, AnimePage } from "@/types";
import { getCover } from "@/lib/cover";

const PAGE_SIZE = 18;

// 热门分类标签（按流行类型筛选）：label 显示英文，value 用于后端中文 genre 匹配
const CATEGORIES: { label: string; value: string }[] = [
  { label: "All", value: "全部" },
  { label: "Action", value: "热血" },
  { label: "Fantasy", value: "奇幻" },
  { label: "Battle", value: "战斗" },
  { label: "School", value: "校园" },
  { label: "Romance", value: "恋爱" },
  { label: "Mystery", value: "悬疑" },
  { label: "Sci-Fi", value: "科幻" },
  { label: "Slice of Life", value: "日常" },
  { label: "Magic", value: "魔法" },
  { label: "Healing", value: "治愈" },
  { label: "Historical", value: "历史" },
];

// 后端 Anime -> HeroBanner FeaturedAnime 适配
function toFeatured(a: Anime): FeaturedAnime {
  return {
    id: a.id,
    title: a.title,
    chinese_title: a.chinese_title,
    slug: a.slug,
    cover: getCover(a),
    description: a.description || "",
    genre: a.genre || "",
    year: typeof a.year === "number" ? a.year : undefined,
    score: Number(a.score ?? 0),
    status: a.status,
  };
}

// 后端 Anime[] -> HeroBanner TrendingItem[] 适配
function toTrending(list: Anime[]): TrendingItem[] {
  return list
    .filter((a) => a && a.id)
    .map((a) => ({
      id: a.id,
      title: a.chinese_title || a.title,
      slug: a.slug,
      cover: getCover(a),
      score: Number(a.score ?? 0),
      tag: a.status || a.genre || "",
    }));
}

// 分类匹配：按 genre 字符串模糊匹配
function genreMatch(a: Anime, cat: string): boolean {
  if (cat === "全部") return true;
  const g = (a.genre || "").toLowerCase();
  return g.includes(cat.toLowerCase());
}

// ---------------- 区块标题 + 横向滚动卡片带 ----------------
function ScrollRow({
  title,
  gradient,
  items,
  loading,
  href,
}: {
  title: string;
  gradient: string;
  items: Anime[];
  loading: boolean;
  href?: string;
}) {
  return (
    <section className="mt-10">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="flex items-center gap-3 text-xl font-bold text-white">
          <span className={`h-6 w-1 rounded-full bg-gradient-to-b ${gradient}`} />
          {title}
        </h2>
        {href && (
          <Link href={href} className="shrink-0 text-sm text-pink-400 hover:underline">
            View all →
          </Link>
        )}
      </div>
      {loading ? (
        <div className="flex gap-4 overflow-x-auto pb-2">
          {Array.from({ length: 6 }).map((_, i) => (
            <div
              key={i}
              className="flex w-40 shrink-0 flex-col gap-2 animate-pulse sm:w-44"
            >
              <div className="h-52 rounded-2xl bg-white/10" />
              <div className="h-3 w-1/3 rounded bg-white/10" />
            </div>
          ))}
        </div>
      ) : items.length === 0 ? (
        <p className="py-8 text-center text-sm text-slate-500">No anime found</p>
      ) : (
        <div className="flex gap-4 overflow-x-auto pb-2">
          {items.map((a) => (
            <div key={a.id} className="w-40 shrink-0 sm:w-44">
              <AnimeCard anime={a} />
            </div>
          ))}
        </div>
      )}
    </section>
  );
}

// 分类芯片栏
function CategoryBar({ active }: { active: string }) {
  return (
    <nav className="mt-8 flex gap-2 overflow-x-auto py-1 no-scrollbar">
      {CATEGORIES.map((c) => {
        const same = c.value === active;
        return (
          <Link
            key={c.value}
            href={c.value === "全部" ? "/" : `/?category=${encodeURIComponent(c.value)}`}
            className={`shrink-0 rounded-full border px-4 py-1.5 text-sm font-medium transition ${
              same
                ? "border-pink-500 bg-gradient-to-r from-pink-500 to-fuchsia-600 text-white shadow-glow"
                : "border-white/10 bg-white/5 text-slate-300 hover:border-white/20 hover:text-white"
            }`}
          >
            {c.label}
          </Link>
        );
      })}
    </nav>
  );
}

export default function HomeClient({ initialPage }: { initialPage: AnimePage }) {
  const searchParams = useSearchParams();
  const q = (searchParams.get("q") || "").trim();
  const category = searchParams.get("category") || "全部";

  const [searchResults, setSearchResults] = useState<AnimePage | null>(null);
  const [searchLoading, setSearchLoading] = useState(false);

  const [hot, setHot] = useState<Anime[]>([]);
  const [latest, setLatest] = useState<Anime[]>(initialPage.items || []);
  const [high, setHigh] = useState<Anime[]>([]);
  const [featuredList, setFeaturedList] = useState<Anime[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // 并行加载首页数据
  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    Promise.allSettled([
      fetchAnimeBySort("quality", 8), // 热门动漫（质量优先）
      fetchAnimeBySort("quality", 12), // 最新更新（质量优先）
      fetchAnimeByFilter({ sort: "quality" }, 2, 12), // 高分推荐（第二页）
      fetchAnimeBySort("quality", 10), // HeroBanner 精选 + 排行榜
    ]).then(([hotR, latestR, highR, heroR]) => {
      if (cancelled) return;
      if (hotR.status === "fulfilled") setHot(hotR.value.items || []);
      if (latestR.status === "fulfilled") setLatest(latestR.value.items || []);
      if (highR.status === "fulfilled") setHigh(highR.value.items || []);
      if (heroR.status === "fulfilled" && heroR.value.items.length > 0) {
        setFeaturedList(heroR.value.items);
      }
      const rejected = [hotR, latestR, highR, heroR].filter(
        (r) => r.status === "rejected",
      );
      if (rejected.length === 4) {
        setError(apiErrorMessage((rejected[0] as PromiseRejectedResult).reason));
      } else if (rejected.length > 0) {
        setError("部分内容加载失败，已显示可用数据");
      }
      setLoading(false);
    });
    return () => {
      cancelled = true;
    };
  }, []);

  // 搜索
  useEffect(() => {
    if (!q) {
      setSearchResults(null);
      return;
    }
    let cancelled = false;
    setSearchLoading(true);
    fetchAnimePage(q, 1, PAGE_SIZE)
      .then((d) => {
        if (!cancelled) setSearchResults(d);
      })
      .catch(() => {
        if (!cancelled)
          setSearchResults({
            items: [],
            total: 0,
            page: 1,
            page_size: PAGE_SIZE,
            pages: 0,
          });
      })
      .finally(() => {
        if (!cancelled) setSearchLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [q]);

  // 分类过滤后的列表
  const hotF = hot.filter((a) => genreMatch(a, category));
  const latestF = latest.filter((a) => genreMatch(a, category));
  const highF = high.filter((a) => genreMatch(a, category));
  // 完结动漫 = 最热中的已完结作品
  const completedF = hot.filter(
    (a) => genreMatch(a, category) && (a.status || "").includes("完结"),
  );
  const featured = featuredList.filter((a) => genreMatch(a, category));

  // ===== 搜索结果显示 =====
  if (q) {
    const items = searchResults?.items ?? [];
    return (
      <div className="mx-auto max-w-7xl animate-fade-in px-4 py-8">
        <h1 className="mb-6 text-2xl font-black text-white">
          Search results for <span className="text-pink-400">“{q}”</span>
        </h1>
        {searchLoading ? (
          <p className="py-16 text-center text-slate-400">Searching...</p>
        ) : items.length === 0 ? (
          <p className="py-16 text-center text-slate-500">No anime found</p>
        ) : (
          <div className="grid grid-cols-2 gap-5 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
            {items.map((a) => (
              <AnimeCard key={a.id} anime={a} />
            ))}
          </div>
        )}
      </div>
    );
  }

    // ===== 首页主体布局 =====
  return (
    <div className="mx-auto max-w-7xl px-4 pb-16">
      {/* 页头口号 — 英文主定位（Anime Database / Recommendations / Watch Orders） */}
      <section className="mb-8 text-center">
        <h1 className="text-3xl font-extrabold text-white sm:text-4xl">
          Anime Database, Recommendations &amp; Watch Orders
        </h1>
        <p className="mt-3 max-w-2xl text-slate-300">
          Discover popular anime, best lists, similar shows, watch orders and seasonal new
          releases — ranked by score with genres, years and episode details.
        </p>
      </section>

      {/* 顶部主视觉轮播图 */}
      <div className="mt-6">
        {loading ? (
          <div className="flex min-h-[340px] animate-pulse items-center justify-center rounded-3xl border border-white/10 bg-white/5 text-slate-500">
            Loading...
          </div>
        ) : (
          <HeroBanner
            featured={featured.map(toFeatured)}
            trending={toTrending(featuredList)}
          />
        )}
      </div>

      {/* 加载失败提示 */}
      {error && !loading && (
        <p className="mt-4 rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-400">
          ⚠️ {error}
        </p>
      )}

      {/* 分类筛选栏 */}
      <CategoryBar active={category} />

      {/* 热门动漫（横向滚动） */}
      <ScrollRow
        title="Popular Anime"
        gradient="from-pink-500 to-fuchsia-600"
        items={hotF}
        loading={loading}
        href="/top-anime"
      />

      {/* 最新更新（横向滚动） */}
      <ScrollRow
        title="Latest Anime"
        gradient="from-cyan-400 to-indigo-500"
        items={latestF}
        loading={loading}
        href="/latest-anime"
      />

      {/* 高分推荐（横向滚动） */}
      <ScrollRow
        title="Top Rated"
        gradient="from-amber-400 to-pink-500"
        items={highF}
        loading={loading}
        href="/high-score"
      />

      {/* 季度新番入口 */}
      <section className="mt-10">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="flex items-center gap-3 text-xl font-bold text-white">
            <span className="h-6 w-1 rounded-full bg-gradient-to-b from-sky-400 to-indigo-500" />
            Seasonal Anime
          </h2>
          <Link href="/seasons" className="shrink-0 text-sm text-pink-400 hover:underline">
            View all →
          </Link>
        </div>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          {(["winter", "spring", "summer", "autumn"] as const).map((s) => {
            const year = new Date().getFullYear();
            const seasonEn = { winter: "Winter", spring: "Spring", summer: "Summer", autumn: "Fall" }[s];
            return (
              <Link
                key={s}
                href={`/season/${year}/${s}`}
                className="rounded-2xl border border-white/10 bg-white/5 p-4 text-center transition hover:border-pink-500/50 hover:bg-pink-500/5"
              >
                <p className="font-bold text-white">{seasonEn} {year}</p>
                <p className="mt-1 text-sm text-slate-400">Seasonal anime</p>
              </Link>
            );
          })}
        </div>
      </section>

      {/* 类型入口 */}
      <section className="mt-10">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="flex items-center gap-3 text-xl font-bold text-white">
            <span className="h-6 w-1 rounded-full bg-gradient-to-b from-pink-500 to-fuchsia-600" />
            Genres
          </h2>
          <Link href="/genres" className="shrink-0 text-sm text-pink-400 hover:underline">
            View all →
          </Link>
        </div>
        <div className="flex flex-wrap gap-2">
          {CATEGORIES.filter((c) => c.value !== "全部").slice(0, 10).map((c) => (
            <Link
              key={c.value}
              href={`/categories/${encodeURIComponent(c.value)}`}
              className="rounded-full border border-white/10 bg-white/5 px-4 py-1.5 text-sm text-slate-300 transition hover:border-pink-500/50 hover:text-white"
            >
              {c.label}
            </Link>
          ))}
        </div>
      </section>

      {/* 制作公司入口 */}
      <section className="mt-10">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="flex items-center gap-3 text-xl font-bold text-white">
            <span className="h-6 w-1 rounded-full bg-gradient-to-b from-emerald-400 to-teal-500" />
            Studios
          </h2>
          <Link href="/studios" className="shrink-0 text-sm text-pink-400 hover:underline">
            View all →
          </Link>
        </div>
        <div className="flex flex-wrap gap-2">
          {["MAPPA", "ufotable", "WIT STUDIO", "Bones", "MADHOUSE", "京都动画", "A-1 Pictures", "东映动画"].map((s) => (
            <Link
              key={s}
              href={`/studio/${encodeURIComponent(s)}`}
              className="rounded-full border border-white/10 bg-white/5 px-4 py-1.5 text-sm text-slate-300 transition hover:border-pink-500/50 hover:text-white"
            >
              {s}
            </Link>
          ))}
        </div>
      </section>

      {/* 完结动漫（横向滚动） */}
      <ScrollRow
        title="Completed Anime"
        gradient="from-emerald-400 to-indigo-500"
        items={completedF}
        loading={loading}
        href="/completed-anime"
      />
    </div>
  );
}

