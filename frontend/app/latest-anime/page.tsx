import ListPageView from "@/components/ListPageView";
import { fetchAnimeByFilter } from "@/lib/api";
import type { AnimePage } from "@/types";

export const dynamic = "force-dynamic";

export async function generateMetadata() {
  return {
    title: "Latest Anime Updates - New Shows Daily",
    description:
      "AnimeHub latest anime — newly added shows and recent updates, refreshed daily.",
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
      title="Latest Anime"
      subtitle="New shows and sequels added regularly — see the latest updates first."
      items={data.items}
      total={data.total}
      page={data.page}
      pages={data.pages}
      pageUrl={(p) => `/latest-anime?page=${p}`}
    />
  );
}