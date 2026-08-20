import Link from "next/link";
import AnimeCard from "@/components/AnimeCard";
import { fetchAnimeByFilter } from "@/lib/api";
import type { AnimePage } from "@/types";

export const dynamic = "force-dynamic";

const PAGE_SIZE = 24;
const SITE_BASE = (process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000").replace(/\/$/, "");

/** 显示名：英文 studio 首字母大写，中文保持不变 */
function displayName(raw: string): string {
  const s = (raw || "").trim();
  if (!s) return s;
  return /^[a-zA-Z]/.test(s) ? s.charAt(0).toUpperCase() + s.slice(1) : s;
}

export async function generateMetadata({ params }: { params: { studio: string } }) {
  const studio = displayName(params.studio);
  const canonical = `${SITE_BASE}/studio/${encodeURIComponent(params.studio)}`;
  return {
    title: `${studio}制作动漫大全 - AnimeHub`,
    description: `${studio}制作的动漫作品大全，收录${studio}出品的经典与新番，按评分与热度整理，支持免费在线观看。`,
    alternates: { canonical },
    openGraph: {
      type: "website",
      locale: "zh_CN",
      url: canonical,
      siteName: "AnimeHub",
      title: `${studio}制作动漫大全 - AnimeHub`,
      description: `${studio}制作的动漫作品精选。`,
    },
  };
}

/** 拉取该 studio 全部分页（用于年份分布统计） */
async function fetchAllByStudio(studio: string, pageSize = 100): Promise<AnimePage> {
  const first = await fetchAnimeByFilter({ studio, sort: "score" }, 1, pageSize);
  const all = { ...first, items: [...first.items] };
  const pages = first.pages || 1;
  for (let p = 2; p <= pages; p++) {
    try {
      const data = await fetchAnimeByFilter({ studio, sort: "score" }, p, pageSize);
      all.items.push(...data.items);
    } catch {
      break;
    }
  }
  all.total = all.items.length;
  all.pages = Math.max(1, Math.ceil(all.items.length / PAGE_SIZE));
  return all;
}

export default async function StudioPage({
  params,
  searchParams,
}: {
  params: { studio: string };
  searchParams: { page?: string };
}) {
  const studio = params.studio;
  const display = displayName(studio);
  const page = Math.max(1, parseInt(searchParams.page || "1", 10) || 1);

  let data: AnimePage = { items: [], total: 0, page: 1, page_size: PAGE_SIZE, pages: 0 };
  let allForYears: AnimePage = { items: [], total: 0, page: 1, page_size: 100, pages: 0 };
  try {
    data = await fetchAnimeByFilter({ studio, sort: "score" }, page, PAGE_SIZE);
    allForYears = await fetchAllByStudio(studio);
  } catch {
    // backend offline
  }

  // 年份分布
  const yearMap = new Map<number, number>();
  for (const a of allForYears.items) {
    if (a.year) yearMap.set(a.year, (yearMap.get(a.year) || 0) + 1);
  }
  const yearDist = Array.from(yearMap.entries()).sort((a, b) => b[0] - a[0]);

  return (
    <div className="mx-auto max-w-7xl animate-fade-in px-4 py-8">
      {/* JSON-LD: CollectionPage + ItemList */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            name: `${display}制作动漫大全`,
            url: `${SITE_BASE}/studio/${encodeURIComponent(studio)}`,
            description: `${display}制作的动漫作品精选。`,
            mainEntity: {
              "@type": "ItemList",
              numberOfItems: allForYears.total,
              itemListElement: allForYears.items.slice(0, 30).map((a, i) => ({
                "@type": "ListItem",
                position: i + 1,
                url: `${SITE_BASE}/anime/${a.slug || a.id}`,
                name: a.chinese_title || a.title,
              })),
            },
          }),
        }}
      />

      <header className="mb-8">
        <h1 className="text-3xl font-black text-white">{display}制作动漫大全</h1>
        <p className="mt-2 max-w-3xl text-slate-400">
          {display} 出品的动漫作品，共 {allForYears.total} 部，按评分与热度整理。
        </p>
      </header>

      {/* 年份分布 */}
      {yearDist.length > 0 && (
        <div className="mb-8 flex flex-wrap gap-2">
          {yearDist.map(([y, cnt]) => (
            <Link
              key={y}
              href={`/years/${y}`}
              className="rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-xs font-medium text-slate-300 transition hover:border-pink-500/50 hover:text-white"
            >
              {y}年（{cnt}部）
            </Link>
          ))}
        </div>
      )}

      {data.items.length === 0 ? (
        <div className="rounded-2xl border border-white/10 bg-white/5 p-16 text-center">
          <p className="text-slate-400">该制作公司暂无收录作品</p>
          <Link href="/" className="mt-4 inline-block text-sm text-pink-400 hover:underline">
            返回首页浏览 →
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-5 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6">
          {data.items.map((a) => (
            <AnimeCard key={a.id} anime={a} />
          ))}
        </div>
      )}

      {/* 分页 */}
      {data.pages > 1 && (
        <nav className="mt-12 flex items-center justify-center gap-2">
          {Array.from({ length: data.pages }, (_, i) => i + 1)
            .filter((p) => p === 1 || p === data.pages || Math.abs(p - page) <= 2)
            .map((p) => (
              <Link
                key={p}
                href={`/studio/${encodeURIComponent(studio)}?page=${p}`}
                className={`flex h-9 w-9 items-center justify-center rounded-xl border border-white/10 text-sm font-semibold transition ${
                  p === page
                    ? "bg-gradient-to-br from-pink-600 to-fuchsia-600 text-white"
                    : "text-slate-300 hover:border-pink-500/60 hover:text-white"
                }`}
              >
                {p}
              </Link>
            ))}
        </nav>
      )}
    </div>
  );
}
