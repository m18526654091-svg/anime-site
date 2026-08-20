import ListPageView from "@/components/ListPageView";
import { fetchAnimeByFilter } from "@/lib/api";
import type { AnimePage } from "@/types";

export const dynamic = "force-dynamic";

export async function generateMetadata() {
  return {
    title: "最新更新动漫 - 每日更新抢先看",
    description:
      "AnimeHub 最新更新动漫，每天实时更新最新剧集与新增作品，第一时间看到新番与续作，分类清晰，免费在线观看。",
  };
}

const PAGE_SIZE = 24;

export default async function LatestAnimePage({
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
      title="最新更新动漫"
      subtitle="新番与续作持续更新，第一时间掌握最新剧集动态。"
      items={data.items}
      total={data.total}
      page={data.page}
      pages={data.pages}
      pageUrl={(p) => `/latest-anime?page=${p}`}
    />
  );
}