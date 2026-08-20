import AnimeCard from "@/components/AnimeCard";
import { fetchAnimeBySort, fetchAnimePage } from "@/lib/api";
import type { AnimePage } from "@/types";

export const dynamic = "force-dynamic";

const PAGE_SIZE = 24;

export async function generateMetadata({
  searchParams,
}: {
  searchParams: { q?: string };
}) {
  const q = (searchParams?.q || "").trim();
  const base = (process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000").replace(/\/$/, "");
  if (!q) {
    return {
      title: "动漫搜索 - AnimeHub",
      description: "在 AnimeHub 搜索动漫，按名称快速找到想看的作品，支持中文名、英文名与模糊匹配。",
      alternates: { canonical: `${base}/search` },
      robots: { index: false, follow: true },
    };
  }
  return {
    title: `搜索 ${q} 动漫结果 - AnimeHub`,
    description: `「${q}」动漫搜索结果：包含热门新番、高分佳作与分类精选，一键在线浏览。`,
    alternates: { canonical: `${base}/search?q=${encodeURIComponent(q)}` },
    robots: { index: true, follow: true },
  };
}

export default async function SearchPage({
  searchParams,
}: {
  searchParams: { q?: string };
}) {
  const q = (searchParams?.q || "").trim();
  const base = (process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000").replace(/\/$/, "");

  let data: AnimePage = { items: [], total: 0, page: 1, page_size: PAGE_SIZE, pages: 0 };
  let hot: AnimePage = { items: [], total: 0, page: 1, page_size: PAGE_SIZE, pages: 0 };
  if (q) {
    try {
      data = await fetchAnimePage(q, 1, PAGE_SIZE);
    } catch {
      // backend offline
    }
  }
  // 无结果时提供热门高分推荐，避免搜索死胡同
  if (q && data.total === 0) {
    try {
      hot = await fetchAnimeBySort("score", 12);
    } catch {
      // ignore
    }
  }

  return (
    <div className="mx-auto max-w-7xl animate-fade-in px-4 py-8">
      {/* 搜索页 JSON-LD：SearchAction 帮助 Google 理解站内搜索 */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "WebSite",
            name: "AnimeHub",
            url: `${base}/`,
            potentialAction: {
              "@type": "SearchAction",
              target: `${base}/search?q={search_term_string}`,
              "query-input": "required name=search_term_string",
            },
          }),
        }}
      />

      <header className="mb-8">
        <h1 className="text-3xl font-black text-white">
          {q ? (
            <>
              搜索「<span className="text-pink-400">{q}</span>」
            </>
          ) : (
            "动漫搜索"
          )}
        </h1>
        {q && (
          <p className="mt-2 text-slate-400">共找到 {data.total} 部相关作品</p>
        )}
      </header>

      {q && data.items.length > 0 ? (
        <div className="grid grid-cols-2 gap-5 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6">
          {data.items.map((a) => (
            <AnimeCard key={a.id} anime={a} />
          ))}
        </div>
      ) : q ? (
        <div>
          <div className="rounded-2xl border border-white/10 bg-white/5 p-10 text-center">
            <p className="mt-3 text-lg font-semibold text-white">
              未找到与「{q}」相关的动漫
            </p>
            <p className="mt-1 text-sm text-slate-400">
              试试其他关键词，或浏览以下高分推荐
            </p>
          </div>
          {hot.items.length > 0 && (
            <section className="mt-10">
              <h2 className="mb-5 flex items-center gap-3 text-xl font-bold text-white">
                <span className="h-6 w-1 rounded-full bg-gradient-to-b from-amber-400 to-pink-500" />
                高分推荐
              </h2>
              <div className="grid grid-cols-2 gap-5 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6">
                {hot.items.map((a) => (
                  <AnimeCard key={a.id} anime={a} />
                ))}
              </div>
            </section>
          )}
        </div>
      ) : (
        <div className="rounded-2xl border border-white/10 bg-white/5 p-16 text-center">
          <p className="mt-4 text-lg text-slate-300">
            输入动漫名称开始搜索，支持中文名、英文名与模糊匹配
          </p>
        </div>
      )}
    </div>
  );
}
