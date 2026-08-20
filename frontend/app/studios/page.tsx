import Link from "next/link";
import { fetchStudios } from "@/lib/api";

export const dynamic = "force-dynamic";

const SITE_BASE = (process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000").replace(/\/$/, "");

export async function generateMetadata() {
  return {
    title: "动漫制作公司大全 - AnimeHub",
    description:
      "浏览 AnimeHub 收录的全部动漫制作公司（工作室），按作品数量排序，查看各家公司的代表作品，免费在线观看。",
    alternates: { canonical: `${SITE_BASE}/studios` },
    openGraph: {
      type: "website",
      locale: "zh_CN",
      url: `${SITE_BASE}/studios`,
      siteName: "AnimeHub",
      title: "动漫制作公司大全 - AnimeHub",
      description: "按制作公司浏览动漫作品。",
    },
  };
}

export default async function StudiosPage() {
  let studios: { studio: string; count: number }[] = [];
  try {
    studios = await fetchStudios();
  } catch {
    // backend offline
  }

  return (
    <div className="mx-auto max-w-7xl animate-fade-in px-4 py-8">
      {/* JSON-LD: CollectionPage */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            name: "动漫制作公司大全",
            url: `${SITE_BASE}/studios`,
            description: "按制作公司浏览动漫作品。",
            mainEntity: {
              "@type": "ItemList",
              numberOfItems: studios.length,
              itemListElement: studios.slice(0, 50).map((s, i) => ({
                "@type": "ListItem",
                position: i + 1,
                url: `${SITE_BASE}/studio/${encodeURIComponent(s.studio)}`,
                name: `${s.studio}制作动漫`,
              })),
            },
          }),
        }}
      />

      <header className="mb-8">
        <h1 className="text-3xl font-black text-white">动漫制作公司大全</h1>
        <p className="mt-2 text-slate-400">
          收录 {studios.length} 家动漫制作公司，点击查看各公司出品的动漫作品。
        </p>
      </header>

      {studios.length === 0 ? (
        <p className="py-20 text-center text-slate-500">暂无制作公司数据</p>
      ) : (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
          {studios.map((s) => (
            <Link
              key={s.studio}
              href={`/studio/${encodeURIComponent(s.studio)}`}
              className="rounded-2xl border border-white/10 bg-white/5 p-5 transition hover:border-pink-500/50 hover:bg-pink-500/5"
            >
              <p className="truncate font-bold text-white">{s.studio}</p>
              <p className="mt-1 text-sm text-slate-400">{s.count} 部作品</p>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
