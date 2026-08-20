import Link from "next/link";
import { fetchCategories } from "@/lib/api";
import { getSiteBase } from "@/lib/site";

export const dynamic = "force-dynamic";

export async function generateMetadata() {
  const base = getSiteBase();
  const title = "动漫分类大全 - 按类型浏览动漫 | AnimeHub";
  const description =
    "AnimeHub 按题材类型整理动漫，包含热血、奇幻、科幻、恋爱、校园等，分类清晰、即点即看，免费在线观看。";
  return {
    title,
    description,
    alternates: { canonical: `${base}/categories` },
    openGraph: {
      type: "website",
      locale: "zh_CN",
      url: `${base}/categories`,
      siteName: "AnimeHub",
      title,
      description,
    },
  };
}

export default async function CategoriesIndexPage() {
  let categories: { genre: string; count: number }[] = [];
  try {
    categories = await fetchCategories();
  } catch {
    // backend offline; render empty state
  }

  const breadcrumb = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: [
      {
        "@type": "ListItem",
        position: 1,
        name: "首页",
        id: `${getSiteBase()}/`,
      },
      {
        "@type": "ListItem",
        position: 2,
        name: "动漫分类",
        id: `${getSiteBase()}/categories`,
      },
    ],
  };

  return (
    <div className="mx-auto max-w-7xl animate-fade-in px-4 py-8">
      <script
        type="application/ld+json"
        // eslint-disable-next-line react/no-danger
        dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumb) }}
      />

      <header className="mb-8">
        <h1 className="text-3xl font-black text-white">动漫分类大全</h1>
        <p className="mt-2 max-w-3xl text-slate-400">
          AnimeHub 把动漫按题材类型整理清晰，点击即可进入对应题材的热门动漫列表。
        </p>
      </header>

      {categories.length === 0 ? (
        <p className="py-20 text-center text-slate-500">暂无分类数据</p>
      ) : (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6">
          {categories.map((c) => (
            <Link
              key={c.genre}
              href={`/categories/${encodeURIComponent(c.genre)}`}
              className="group flex flex-col items-center justify-center gap-2 rounded-2xl border border-white/10 bg-white/5 p-6 text-center transition hover:-translate-y-1 hover:border-pink-500/50 hover:shadow-glow"
            >
              <span className="text-2xl font-bold text-white group-hover:text-pink-300">
                {c.genre}
              </span>
              <span className="text-xs text-slate-400">{c.count} 部作品</span>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
