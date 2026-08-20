import ListPageView from "@/components/ListPageView";
import { fetchAnimeByFilter } from "@/lib/api";
import type { AnimePage } from "@/types";

export const dynamic = "force-dynamic";

export async function generateMetadata({
  params,
}: {
  params: { tag: string };
}) {
  const tag = decodeURIComponent(params.tag);
  return {
    title: `${tag}动漫推荐 - ${tag}标签动漫大全`,
    description: `浏览标记为「${tag}」标签的动漫作品，按热度与更新时间整理，方便你快速找到感兴趣的${tag}题材动漫。`,
  };
}

const PAGE_SIZE = 24;

function pageUrl(tag: string, page: number) {
  return `/tags/${encodeURIComponent(tag)}?page=${page}`;
}

export default async function TagPage({
  params,
  searchParams,
}: {
  params: { tag: string };
  searchParams: { page?: string };
}) {
  const tag = decodeURIComponent(params.tag);
  const page = Math.max(1, parseInt(searchParams.page || "1", 10) || 1);

  let data: AnimePage = { items: [], total: 0, page: 1, page_size: PAGE_SIZE, pages: 0 };
  try {
    data = await fetchAnimeByFilter({ tag }, page, PAGE_SIZE);
  } catch {
    // backend offline; render empty state
  }

  return (
    <ListPageView
      title={`「${tag}」动漫`}
      subtitle={`与「${tag}」标签相关的动漫作品精选。`}
      items={data.items}
      total={data.total}
      page={data.page}
      pages={data.pages}
      pageUrl={(p) => pageUrl(tag, p)}
    />
  );
}