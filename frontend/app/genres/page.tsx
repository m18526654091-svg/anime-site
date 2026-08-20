import Link from "next/link";
import { fetchCategories } from "@/lib/api";

export const dynamic = "force-dynamic";

const SITE_BASE = (process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000").replace(/\/$/, "");

export async function generateMetadata() {
  return {
    title: "动漫类型大全 - 全部分类入口 - AnimeHub",
    description:
      "浏览 AnimeHub 收录的全部动漫类型与题材分类，热血、奇幻、恋爱、科幻、悬疑等，按类型快速找到你喜欢的动漫。",
    alternates: { canonical: `${SITE_BASE}/genres` },
    openGraph: {
      type: "website",
      locale: "zh_CN",
      url: `${SITE_BASE}/genres`,
      siteName: "AnimeHub",
      title: "动漫类型大全 - AnimeHub",
      description: "按类型浏览动漫作品。",
    },
  };
}

export default async function GenresPage() {
  let genres: { genre: string; count: number }[] = [];
  try {
    genres = await fetchCategories();
  } catch {
    // backend offline
  }

  return (
    <div className="mx-auto max-w-7xl animate-fade-in px-4 py-8">
      {/* JSON-LD */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            name: "动漫类型大全",
            url: `${SITE_BASE}/genres`,
            description: "按类型浏览动漫作品。",
            mainEntity: {
              "@type": "ItemList",
              numberOfItems: genres.length,
              itemListElement: genres.slice(0, 50).map((g, i) => ({
                "@type": "ListItem",
                position: i + 1,
                url: `${SITE_BASE}/categories/${encodeURIComponent(g.genre)}`,
                name: `${g.genre}动漫`,
              })),
            },
          }),
        }}
      />

      <header className="mb-8">
        <h1 className="text-3xl font-black text-white">动漫类型大全</h1>
        <p className="mt-2 text-slate-400">
          收录 {genres.length} 种动漫类型，点击查看该类型的全部作品。
        </p>
      </header>

      {genres.length === 0 ? (
        <p className="py-20 text-center text-slate-500">暂无类型数据</p>
      ) : (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
          {genres.map((g) => (
            <Link
              key={g.genre}
              href={`/categories/${encodeURIComponent(g.genre)}`}
              className="rounded-2xl border border-white/10 bg-white/5 p-5 transition hover:border-pink-500/50 hover:bg-pink-500/5"
            >
              <p className="truncate font-bold text-white">{g.genre}</p>
              <p className="mt-1 text-sm text-slate-400">{g.count} 部作品</p>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
