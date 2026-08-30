import ListPageView from "@/components/ListPageView";
import { fetchAnimeByFilter } from "@/lib/api";
import type { AnimePage } from "@/types";

export const dynamic = "force-dynamic";

export async function generateMetadata() {
  return {
    title: "Top Rated Anime: Best High-Score Shows",
    description:
      "AnimeHub top-rated anime — the highest-scored shows, ranked by fan rating.",
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
      title="Top Rated Anime"
      subtitle="The best-loved shows with the highest scores, ranked for you."
      items={data.items}
      total={data.total}
      page={data.page}
      pages={data.pages}
      pageUrl={(p) => `/high-score?page=${p}`}
    />
  );
}