import Link from "next/link";
import ListPageView from "@/components/ListPageView";
import { fetchAnimeByFilter } from "@/lib/api";
import { notFound } from "next/navigation";
import type { AnimePage } from "@/types";

export const dynamic = "force-dynamic";

export async function generateMetadata({
  params,
}: {
  params: { year: string };
}) {
  const year = parseInt(params.year, 10);
  if (!Number.isFinite(year) || year < 1900 || year > 2100) {
    // 无效年份：绝不可索引（页面 notFound() 返回真 404）
    return { title: "年份不存在", robots: { index: false, follow: false } };
  }
  return {
    title: `${year}年动漫大全 - ${year}年新番动漫`,
    description: `盘点 ${year} 年播出与收录的动漫作品，含热血、奇幻、恋爱等全类型新番，按年份浏览${year}年动漫。`,
  };
}

const PAGE_SIZE = 24;

export default async function YearPage({
  params,
  searchParams,
}: {
  params: { year: string };
  searchParams: { page?: string };
}) {
  const year = parseInt(params.year, 10);
  if (!Number.isFinite(year) || year < 1900 || year > 2100) {
    notFound(); // 无效年份 → 真 404
  }
  const page = Math.max(1, parseInt(searchParams.page || "1", 10) || 1);

  let data: AnimePage = { items: [], total: 0, page: 1, page_size: PAGE_SIZE, pages: 0 };
  try {
    data = await fetchAnimeByFilter({ year }, page, PAGE_SIZE);
  } catch {
    // backend offline; render empty state
  }

  return (
    <div>
      {/* 站内导航：高分/季度/年份入口 */}
      <div className="mx-auto flex max-w-7xl flex-wrap gap-2 px-4 pt-6 text-sm">
        <Link href="/high-score" className="rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-slate-300 transition hover:border-pink-500/50 hover:text-white">
          高分推荐
        </Link>
        <Link href="/seasons" className="rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-slate-300 transition hover:border-pink-500/50 hover:text-white">
          季度新番
        </Link>
        <Link href="/years" className="rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-slate-300 transition hover:border-pink-500/50 hover:text-white">
          全部年份
        </Link>
      </div>
      <ListPageView
        title={`${year}年动漫`}
        subtitle={`${year} 年播出与收录的动漫作品精选。`}
        items={data.items}
        total={data.total}
        page={data.page}
        pages={data.pages}
        pageUrl={(p) => `/years/${year}?page=${p}`}
      />
    </div>
  );
}