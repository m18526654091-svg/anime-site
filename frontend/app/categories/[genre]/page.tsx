import ListPageView from "@/components/ListPageView";
import { fetchAnimeByFilter } from "@/lib/api";
import type { AnimePage } from "@/types";

export const dynamic = "force-dynamic";

export async function generateMetadata({
  params,
}: {
  params: { genre: string };
}) {
  const genre = decodeURIComponent(params.genre);
  return {
    title: `${genre}动漫大全 - 在线观看免费${genre}`,
    description: `收录 ${genre} 类型的动漫作品，包括最新更新、高分动漫与经典番剧，实时更新，免费在线观看。`,
  };
}

const PAGE_SIZE = 24;

function pageUrl(genre: string, page: number) {
  return `/categories/${encodeURIComponent(genre)}?page=${page}`;
}

export default async function CategoryPage({
  params,
  searchParams,
}: {
  params: { genre: string };
  searchParams: { page?: string };
}) {
  const genre = decodeURIComponent(params.genre);
  const page = Math.max(1, parseInt(searchParams.page || "1", 10) || 1);

  let data: AnimePage = { items: [], total: 0, page: 1, page_size: PAGE_SIZE, pages: 0 };
  try {
    data = await fetchAnimeByFilter({ category: genre }, page, PAGE_SIZE);
  } catch {
    // backend offline; render empty state
  }

  return (
    <ListPageView
      title={`${genre}动漫`}
      subtitle={`共收录 ${data.total} 部「${genre}」类型作品`}
      items={data.items}
      total={data.total}
      page={data.page}
      pages={data.pages}
      pageUrl={(p) => pageUrl(genre, p)}
    />
  );
}