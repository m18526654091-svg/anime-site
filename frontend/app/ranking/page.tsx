import Link from "next/link";
import AnimeCard from "@/components/AnimeCard";
import { fetchAnimeByFilter, fetchAnimeBySort } from "@/lib/api";
import type { AnimePage } from "@/types";

export const dynamic = "force-dynamic";

const PAGE_SIZE = 24;
const SITE_BASE = (process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000").replace(/\/$/, "");

export async function generateMetadata() {
  const canonical = `${SITE_BASE}/ranking`;
  return {
    title: "Anime Rankings: Top & Popular Shows",
    description:
      "AnimeHub rankings — highest-scored, most popular, and yearly anime charts.",
    alternates: { canonical },
    openGraph: {
      type: "website",
      locale: "zh_CN",
      url: canonical,
      siteName: "AnimeHub",
      title: "Anime Rankings - AnimeHub",
      description: "Highest-scored and most popular anime rankings.",
    },
  };
}

async function fetchPage(fn: () => Promise<AnimePage>): Promise<AnimePage> {
  try {
    return await fn();
  } catch {
    return { items: [], total: 0, page: 1, page_size: PAGE_SIZE, pages: 0 };
  }
}

export default async function RankingPage() {
  const thisYear = new Date().getFullYear();
  const [scoreTop, hotTop, yearThis, yearPrev] = await Promise.all([
    fetchPage(() => fetchAnimeBySort("score", 12)),
    fetchPage(() => fetchAnimeBySort("quality", 12)),
    fetchPage(() => fetchAnimeByFilter({ year: thisYear, sort: "score" }, 1, 12)),
    fetchPage(() => fetchAnimeByFilter({ year: thisYear - 1, sort: "score" }, 1, 12)),
  ]);

  const blocks = [
    { title: "Top Rated", items: scoreTop.items, href: "/high-score" },
    { title: "Popular Anime", items: hotTop.items, href: "/top-anime" },
    { title: `${thisYear}年动漫排行`, items: yearThis.items, href: `/years/${thisYear}` },
    { title: `${thisYear - 1}年动漫排行`, items: yearPrev.items, href: `/years/${thisYear - 1}` },
  ];

  return (
    <div className="mx-auto max-w-7xl animate-fade-in px-4 py-8">
      {/* JSON-LD */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            name: "动漫排行榜",
            url: `${SITE_BASE}/ranking`,
            description: "评分最高与热门动漫排行榜。",
            mainEntity: blocks.flatMap((b, bi) =>
              b.items.slice(0, 10).map((a, i) => ({
                "@type": "ListItem",
                position: bi * 10 + i + 1,
                url: `${SITE_BASE}/anime/${a.slug || a.id}`,
                name: a.chinese_title || a.title,
              })),
            ),
          }),
        }}
      />

      <header className="mb-8">
        <h1 className="text-3xl font-black text-white">动漫排行榜</h1>
        <p className="mt-2 text-slate-400">
          评分最高、人气最旺、历年新番排行，发现值得一看的动漫佳作。
        </p>
      </header>

      {blocks.map((b) => (
        <section key={b.title} className="mb-10">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="flex items-center gap-3 text-xl font-bold text-white">
              <span className="h-6 w-1 rounded-full bg-gradient-to-b from-pink-500 to-fuchsia-600" />
              {b.title}
            </h2>
            <Link href={b.href} className="shrink-0 text-sm text-pink-400 hover:underline">
              查看全部 →
            </Link>
          </div>
          {b.items.length === 0 ? (
            <p className="py-8 text-center text-slate-500">暂无数据</p>
          ) : (
            <div className="grid grid-cols-2 gap-5 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6">
              {b.items.map((a, i) => (
                <div key={a.id} className="relative">
                  <span className="absolute -left-1 -top-1 z-10 flex h-7 w-7 items-center justify-center rounded-full bg-gradient-to-br from-pink-600 to-fuchsia-600 text-xs font-black text-white shadow">
                    {String(i + 1).padStart(2, "0")}
                  </span>
                  <AnimeCard anime={a} />
                </div>
              ))}
            </div>
          )}
        </section>
      ))}
    </div>
  );
}
