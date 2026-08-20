import Link from "next/link";
import { fetchYears } from "@/lib/api";

export const dynamic = "force-dynamic";

export async function generateMetadata() {
  return {
    title: "年份动漫大全 - 按年份浏览动漫",
    description:
      "按年份浏览 AnimeHub 收录的全部动漫，回顾历年经典番剧与年度新番，按年份查找动漫作品，免费在线观看。",
  };
}

export default async function YearsIndexPage() {
  let years: { year: number; count: number }[] = [];
  try {
    years = await fetchYears();
  } catch {
    // backend offline; render empty state
  }

  return (
    <div className="mx-auto max-w-7xl animate-fade-in px-4 py-8">
      <header className="mb-8">
        <h1 className="text-3xl font-black text-white">年份动漫大全</h1>
        <p className="mt-2 text-slate-400">按年份浏览全部动漫作品</p>
      </header>

      {years.length === 0 ? (
        <p className="py-20 text-center text-slate-500">暂无年份数据</p>
      ) : (
        <div className="flex flex-wrap gap-3">
          {years.map((y) => (
            <Link
              key={y.year}
              href={`/years/${y.year}`}
              className="group rounded-2xl border border-white/10 bg-white/5 px-6 py-4 text-center backdrop-blur transition hover:-translate-y-0.5 hover:border-pink-500/50 hover:shadow-glow"
            >
              <span className="block text-xl font-bold text-white group-hover:text-pink-300">
                {y.year}
              </span>
              <span className="mt-1 block text-xs text-slate-500">{y.count} 部</span>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}