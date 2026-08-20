import Link from "next/link";
import { fetchSeasons } from "@/lib/api";

export const dynamic = "force-dynamic";

const SITE_BASE = (process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000").replace(/\/$/, "");
const SEASON_CN: Record<string, string> = {
  spring: "春季",
  summer: "夏季",
  autumn: "秋季",
  winter: "冬季",
};

export async function generateMetadata() {
  return {
    title: "季度新番大全 - 按季度浏览动漫 - AnimeHub",
    description:
      "按季度浏览历年新番动漫，从春季到冬季、从新番到经典，按播出季度快速定位你想看的作品。",
    alternates: { canonical: `${SITE_BASE}/seasons` },
    openGraph: {
      type: "website",
      locale: "zh_CN",
      url: `${SITE_BASE}/seasons`,
      siteName: "AnimeHub",
      title: "季度新番大全 - AnimeHub",
      description: "按季度浏览动漫新番。",
    },
  };
}

export default async function SeasonsPage() {
  let seasons: { year: number; season: string }[] = [];
  try {
    seasons = await fetchSeasons();
  } catch {
    // backend offline
  }

  // 按年份分组
  const byYear = new Map<number, { year: number; season: string }[]>();
  for (const s of seasons) {
    const arr = byYear.get(s.year) || [];
    arr.push(s);
    byYear.set(s.year, arr);
  }
  const years = Array.from(byYear.keys()).sort((a, b) => b - a);

  return (
    <div className="mx-auto max-w-7xl animate-fade-in px-4 py-8">
      {/* JSON-LD */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            name: "季度新番大全",
            url: `${SITE_BASE}/seasons`,
            description: "按季度浏览动漫新番。",
            mainEntity: {
              "@type": "ItemList",
              numberOfItems: seasons.length,
              itemListElement: seasons.slice(0, 60).map((s, i) => ({
                "@type": "ListItem",
                position: i + 1,
                url: `${SITE_BASE}/season/${s.year}/${s.season}`,
                name: `${s.year}年${SEASON_CN[s.season] || s.season}新番`,
              })),
            },
          }),
        }}
      />

      <header className="mb-8">
        <h1 className="text-3xl font-black text-white">季度新番大全</h1>
        <p className="mt-2 text-slate-400">按播出季度浏览历年新番动漫。</p>
      </header>

      {years.length === 0 ? (
        <p className="py-20 text-center text-slate-500">暂无季度数据</p>
      ) : (
        <div className="space-y-8">
          {years.map((y) => (
            <section key={y}>
              <h2 className="mb-4 flex items-center gap-3 text-xl font-bold text-white">
                <span className="h-6 w-1 rounded-full bg-gradient-to-b from-cyan-400 to-indigo-500" />
                {y}年
              </h2>
              <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
                {byYear.get(y)!.map((s) => (
                  <Link
                    key={`${y}-${s.season}`}
                    href={`/season/${y}/${s.season}`}
                    className="rounded-2xl border border-white/10 bg-white/5 p-4 text-center transition hover:border-pink-500/50 hover:bg-pink-500/5"
                  >
                    <p className="font-bold text-white">
                      {y}年{SEASON_CN[s.season] || s.season}
                    </p>
                    <p className="mt-1 text-sm text-slate-400">新番动漫</p>
                  </Link>
                ))}
              </div>
            </section>
          ))}
        </div>
      )}
    </div>
  );
}
