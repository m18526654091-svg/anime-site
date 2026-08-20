import ListPageView from "@/components/ListPageView";
import { fetchAnimeByFilter } from "@/lib/api";
import type { AnimePage } from "@/types";

export const dynamic = "force-dynamic";

export async function generateMetadata() {
  return {
    title: "热门动漫排行榜 - 大家都在看的动漫",
    description:
      "AnimeHub 热门动漫排行榜，收录当前最受欢迎、热度最高的动漫作品，按人气与评分整理，实时更新，支持手机与电脑免费在线观看。",
  };
}

const PAGE_SIZE = 24;

export default async function TopAnimePage({
  searchParams,
}: {
  searchParams: { page?: string };
}) {
  const page = Math.max(1, parseInt(searchParams.page || "1", 10) || 1);

  let data: AnimePage = {
    items: [],
    total: 0,
    page: 1,
    page_size: PAGE_SIZE,
    pages: 0,
  };
  try {
    data = await fetchAnimeByFilter({ sort: "quality" }, page, PAGE_SIZE);
  } catch {
    // backend offline; render empty state
  }

  return (
    <ListPageView
      title="热门动漫排行榜"
      subtitle="当前人气最高的动漫作品，按热度与评分实时排序。"
      items={data.items}
      total={data.total}
      page={data.page}
      pages={data.pages}
      pageUrl={(p) => `/top-anime?page=${p}`}
    />
  );
}