"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import AnimeCover from "@/components/AnimeCover";
import { animePath } from "@/lib/slug";

// ------------------------------------------------------------------
// HeroCarousel 数据类型
// 与 backend `Anime` 字段对齐，首页只传真实数据即可。
// ------------------------------------------------------------------

export interface FeaturedAnime {
  id: number;
  title: string;
  chinese_title?: string;
  slug?: string;
  cover: string;
  /** 兼容字段：优先读取的封面地址（无则回退 cover） */
  cover_url?: string;
  description: string;
  genre: string;
  year?: number;
  score: number;
  status?: string;
}

export interface TrendingItem {
  id: number;
  title: string;
  chinese_title?: string;
  slug?: string;
  cover: string;
  /** 兼容字段：优先读取的封面地址（无则回退 cover） */
  cover_url?: string;
  score: number;
  tag: string; // 热度关键词，如「新番」「完结」
}

interface Props {
  /** 轮播的精选动漫列表（自动循环）。 */
  featured?: FeaturedAnime[];
  /** 右侧热门排行榜。 */
  trending?: TrendingItem[];
}

const RANK_COLORS = [
  "text-amber-300",
  "text-slate-300",
  "text-orange-400",
  "text-slate-400",
  "text-slate-500",
];

type AnyAnime = FeaturedAnime | TrendingItem;

export default function HeroBanner({ featured = [], trending = [] }: Props) {
  const router = useRouter();
  const [index, setIndex] = useState(0);
  const [liked, setLiked] = useState(false);

  // 自动轮播（无限循环）
  useEffect(() => {
    if (!featured.length) return;
    const id = setInterval(
      () => setIndex((i) => (i + 1) % featured.length),
      6000
    );
    return () => clearInterval(id);
  }, [featured.length]);

  if (featured.length === 0) {
    return null;
  }

  const data = featured[index] || featured[0];
  const score = Number(data.score ?? 0);
  const title = data.chinese_title || data.title;
  const year = data.year ?? null;
  const badges = (data.genre || "")
    .split("/")
    .map((g) => g.trim())
    .filter(Boolean);

  return (
    <section className="relative isolate overflow-hidden rounded-3xl border border-white/10 shadow-2xl shadow-pink-500/10 min-h-[360px] lg:min-h-[420px]">
      {/* 背景封面（整张幅，渐变遮罩保证文字可读） */}
      <AnimeCover
        anime={data}
        className="absolute inset-0 h-full w-full object-cover object-center"
        priority
      />
      <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/70 to-transparent" />

      {/* 搜索区域 */}
      <div className="relative z-10 mx-4 sm:mx-6">
        <div className="flex items-center gap-2">
          <svg
            className="h-5 w-5 text-slate-400 hover:text-pink-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            strokeWidth={2}
          >
            <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            type="text"
            placeholder="搜索动漫名称..."
            className="flex-1 pr-4 py-2.5 rounded-full bg-slate-900/70 border border-white/10 focus:outline-none focus:bg-slate-900/80 focus:border-pink-500 transition placeholder:text-slate-400"
          />
        </div>
      </div>

      {/* 主内容区 - Netflix式布局：左文字/右排行榜 */}
      <div className="relative z-10 flex flex-col lg:flex-row">
        {/* 左侧：文字信息区 */}
        <div className="flex-1 px-4 py-6 sm:px-6 lg:px-8 lg:py-12 lg:pr-0">
          <div className="inline-flex items-center gap-2 rounded-full border border-amber-400/20 bg-amber-400/10 px-2.5 py-1 text-xs font-bold text-amber-300">
            ★ {score.toFixed(1)} 热门推荐
          </div>
          <h2 className="mt-4 text-balance text-3xl font-black text-white sm:text-4xl lg:text-5xl">
            <span className="text-gradient">{title}</span>
          </h2>
          {year && (
            <span className="mt-2 block text-sm text-slate-400">
              {year} 年 • {badges.join(" / ")}
            </span>
          )}
          {data.description && (
            <p className="mt-3 max-w-xl line-clamp-3 text-sm leading-relaxed text-slate-300">
              {data.description}
            </p>
          )}
          <div className="mt-6 flex flex-wrap gap-3">
            <button
              type="button"
              onClick={(e) => {
                e.preventDefault();
                router.push(animePath(data));
              }}
              className="inline-flex items-center justify-center gap-2 rounded-xl bg-gradient-to-b from-pink-600 to-purple-600 px-6 py-3 text-sm font-semibold text-white transition"
            >
              立即观看
            </button>
            <button
              type="button"
              onClick={(e) => {
                e.preventDefault();
                setLiked((v) => !v);
              }}
              className={`inline-flex items-center justify-center gap-2 rounded-xl border px-5 py-2.5 text-sm font-semibold transition ${
                liked
                  ? "border-pink-500 bg-pink-500/15 text-pink-400"
                  : "border-white/20 bg-white/5 text-slate-200 backdrop-blur hover:border-pink-500/60 hover:text-white"
              }`}
            >
              {liked ? "已收藏" : "收藏"}
            </button>
          </div>
        </div>

        {/* 右侧：滚动排行榜 */}
        <section className="rounded-3xl border border-white/10 bg-white/[.03] p-4 backdrop-blur lg:ml-6 lg:mt-12 lg:w-96">
          <div className="mb-4 flex items-center justify-between">
            <h3 className="flex items-center gap-2 text-base font-bold text-white">
              <span className="h-5 w-1.5 rounded-full bg-gradient-to-b from-amber-400 to-pink-500" />
              热门排行榜
            </h3>
            <Link
              href="/top-anime"
              className="text-xs text-pink-400 hover:underline"
            >
              查看全部
            </Link>
          </div>
          <ol className="space-y-1.5">
            {trending.slice(0, 8).map((item, idx) => (
              <li key={item.id}>
                <Link
                  href={animePath(item)}
                  className="group flex items-center gap-3 rounded-xl px-2 py-1.5 text-sm transition hover:bg-white/5"
                >
                  <span
                    className={`w-7 shrink-0 text-center text-base font-black leading-tight tabular-nums ${
                      RANK_COLORS[idx] || "text-slate-500"
                    }`}
                  >
                    {String(idx + 1).padStart(2, "0")}
                  </span>
                  <AnimeCover
                    anime={item}
                    className="h-10 w-7 shrink-0 rounded-md object-cover"
                  />
                  <span className="min-w-0 flex-1 truncate text-slate-200 transition group-hover:text-pink-300">
                    {item.title}
                  </span>
                  <span className="shrink-0 text-xs font-semibold text-amber-400">
                    ★ {Number(item.score ?? 0).toFixed(1)}
                  </span>
                </Link>
              </li>
            ))}
          </ol>
        </section>
      </div>

      {/* 轮播指示点 */}
      <div className="absolute bottom-4 left-1/2 flex -translate-x-1/2 gap-1.5">
        {featured.map((f, i) => (
          <button
            key={f.id}
            type="button"
            aria-label={`切到第 ${i + 1} 张`}
            onClick={() => setIndex(i)}
            className={`h-1.5 rounded-full transition-all ${
              i === index
                ? "w-7 bg-pink-400"
                : "w-5 bg-white/20 hover:bg-white/40"
            }`}
          />
        ))}
      </div>
    </section>
  );
}

