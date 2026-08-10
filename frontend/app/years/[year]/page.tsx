import ListPageView from "@/components/ListPageView";
import { fetchAnimeByFilter } from "@/lib/api";
import type { AnimePage } from "@/types";

export const dynamic = "force-dynamic";

export async function generateMetadata({
  params,
}: {
  params: { year: string };
}) {
  const year = parseInt(params.year, 10);
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
  if (!Number.isFinite(year)) {
    return <p className="py-24 text-center text-slate-500">参数错误</p>;
  }
  const page = Math.max(1, parseInt(searchParams.page || "1", 10) || 1);

  let data: AnimePage = { items: [], total: 0, page: 1, page_size: PAGE_SIZE, pages: 0 };
  try {
    data = await fetchAnimeByFilter({ year }, page, PAGE_SIZE);
  } catch {
    // backend offline; render empty state
  }

  return (
    <ListPageView
      title={`${year}年动漫`}
      subtitle={`共收录 ${data.total} 部${year}年动漫作品`}
      items={data.items}
      total={data.total}
      page={data.page}
      pages={data.pages}
      pageUrl={(p) => `/years/${year}?page=${p}`}
    />
  );
}