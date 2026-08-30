import ListPageView from "@/components/ListPageView";
import { fetchAnimeByFilter } from "@/lib/api";
import type { AnimePage } from "@/types";

export const dynamic = "force-dynamic";

export async function generateMetadata() {
  return {
    title: "Top Anime: Most Popular Shows",
    description:
      "AnimeHub top anime — the most popular and highest-rated shows, ranked by popularity and score.",
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
      title="Top Anime"
      subtitle="The most popular anime right now, ranked by fan score."
      items={data.items}
      total={data.total}
      page={data.page}
      pages={data.pages}
      pageUrl={(p) => `/top-anime?page=${p}`}
    />
  );
}