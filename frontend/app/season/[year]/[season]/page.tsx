import Link from "next/link";
import AnimeCard from "@/components/AnimeCard";
import SeasonSortFAB from "@/components/SeasonSortFAB";
import { fetchAnimeByFilter } from "@/lib/api";
import { isSeasonRedundant } from "@/lib/seasonIndex";
import type { AnimePage } from "@/types";

export const dynamic = "force-dynamic";

const PAGE_SIZE = 24;
const SITE_BASE = (process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000").replace(/\/$/, "");

const SEASON_CN: Record<string, string> = {
  spring: "春季",
  summer: "夏季",
  autumn: "秋季",
  winter: "冬季",
};
const VALID_SEASONS = ["spring", "summer", "autumn", "winter"];

export function generateStaticParams() {
  return [];
}

export async function generateMetadata({
  params,
}: {
  params: { year: string; season: string };
}) {
  const year = params.year;
  const season = params.season;
  const seasonCn = SEASON_CN[season] || season;
  const canonical = `${SITE_BASE}/season/${year}/${season}`;
  // 同年 4 季 ID 集合完全相同 → 重复页 noindex（Final SEO Deployment）
  const redundant = await isSeasonRedundant(Number(year), season);
  if (redundant) {
    return {
      title: `${year}年${seasonCn}新番动漫大全 - AnimeHub`,
      description: `${year}年${seasonCn}新番动漫盘点，收录该季度播出与收录的动漫作品。`,
      robots: { index: false, follow: true },
    };
  }
  return {
    title: `${year}年${seasonCn}新番动漫大全 - AnimeHub`,
    description: `${year}年${seasonCn}新番动漫盘点，收录该季度播出与收录的动漫作品，含热血、奇幻、恋爱等全类型，按热度与评分排序。`,
    alternates: { canonical },
    openGraph: {
      type: "website",
      locale: "zh_CN",
      url: canonical,
      siteName: "AnimeHub",
      title: `${year}年${seasonCn}新番动漫大全 - AnimeHub`,
      description: `${year}年${seasonCn}新番动漫精选。`,
    },
  };
}

export default async function SeasonPage({
  params,
  searchParams,
}: {
  params: { year: string; season: string };
  searchParams: { page?: string; sort?: string | string[] };
}) {
  const year = parseInt(params.year, 10);
  const season = params.season;
  const seasonCn = SEASON_CN[season] || season;

  if (!Number.isFinite(year) || !VALID_SEASONS.includes(season)) {
    return (
      <div className="py-24 text-center text-slate-500">
        参数错误，请检查季度与年份。
      </div>
    );
  }

  const page = Math.max(1, parseInt(searchParams.page || "1", 10) || 1);
  // 排序参数（quality/score/latest/year），非法值回退综合排序
  const VALID_SORTS = ["quality", "score", "latest", "year"] as const;
  const rawSort = Array.isArray(searchParams.sort)
    ? searchParams.sort[0]
    : (searchParams.sort || "quality");
  const sortKey: (typeof VALID_SORTS)[number] = (VALID_SORTS as readonly string[]).includes(rawSort)
    ? (rawSort as (typeof VALID_SORTS)[number])
    : "quality";
  let data: AnimePage = { items: [], total: 0, page: 1, page_size: PAGE_SIZE, pages: 0 };
  try {
    data = await fetchAnimeByFilter({ year, season, sort: sortKey }, page, PAGE_SIZE);
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
            name: `${year}年${seasonCn}新番动漫大全`,
            url: `${SITE_BASE}/season/${year}/${season}`,
            description: `${year}年${seasonCn}新番动漫作品精选。`,
            mainEntity: {
              "@type": "ItemList",
              numberOfItems: data.total,
              itemListElement: data.items.slice(0, 30).map((a, i) => ({
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
        <h1 className="text-3xl font-black text-white">
          {year}年{seasonCn}新番动漫大全
        </h1>
        <p className="mt-2 max-w-3xl text-slate-400">
          {year}年{seasonCn}播出的动漫作品精选，共 {data.total} 部。
        </p>
      </header>

      {data.items.length === 0 ? (
        <div className="rounded-2xl border border-white/10 bg-white/5 p-16 text-center">
          <p className="text-slate-400">该季度暂无收录作品，数据持续扩充中。</p>
          <Link href={`/years/${year}`} className="mt-4 inline-block text-sm text-pink-400 hover:underline">
            查看 {year} 年全部动漫 →
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
                href={`/season/${year}/${season}?page=${p}`}
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

      {/* 移动端悬浮筛选按钮 */}
      <SeasonSortFAB />
    </div>
  );
}
