import ListPageView from "@/components/ListPageView";
import { fetchAnimeByFilter } from "@/lib/api";
import type { AnimePage } from "@/types";

export const dynamic = "force-dynamic";

export async function generateMetadata() {
  return {
    title: "高评分动漫 - 高分神作推荐",
    description:
      "AnimeHub 高评分动漫推荐，精选用户口碑与评分俱佳的动漫作品，高分神作一网打尽，按评分排序，免费在线观看。",
  };
}

const PAGE_SIZE = 24;

export default async function HighScorePage({
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
      title="高评分动漫"
      subtitle="口碑与评分俱佳的动漫佳作精选，按评分排序推荐。"
      items={data.items}
      total={data.total}
      page={data.page}
      pages={data.pages}
      pageUrl={(p) => `/high-score?page=${p}`}
    />
  );
}