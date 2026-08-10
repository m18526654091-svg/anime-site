import HomeClient from "@/components/HomeClient";
import AdPlaceholder from "@/components/AdPlaceholder";
import { fetchAnimePage } from "@/lib/api";
import type { AnimePage } from "@/types";

// Server-render with real data from the backend on every request.
export const dynamic = "force-dynamic";
export const metadata = {
  title: "首页 - 热门动漫与最新更新",
  description: "浏览 AnimeHub 收录的热门动漫、最新更新与分类精选。",
};

const PAGE_SIZE = 18;

export default async function HomePage() {
  let initialPage: AnimePage = {
    items: [],
    total: 0,
    page: 1,
    page_size: PAGE_SIZE,
    pages: 0,
  };
  try {
    initialPage = await fetchAnimePage("", 1, PAGE_SIZE);
  } catch {
    // Backend offline: HomeClient will try to reload and show an error message.
  }
  return (
    <>
      <div className="mx-auto max-w-7xl px-4 pt-4">
        <AdPlaceholder />
      </div>
      <HomeClient initialPage={initialPage} />
    </>
  );
}
