import { Suspense } from "react";
import HomeClient from "@/components/HomeClient";
import { fetchAnimeByFilter } from "@/lib/api";
import type { AnimePage } from "@/types";

// Server-render with real data from the backend on every request.
export const dynamic = "force-dynamic";

const SITE_BASE = (
  process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000"
).replace(/\/$/, "");

export const metadata = {
  title: "AnimeHub - 热门动漫与最新更新",
  description:
    "浏览 AnimeHub 收录的热门动漫、最新更新与分类精选，支持搜索、分类与排行榜浏览。",
  robots: { index: true, follow: true },
  openGraph: {
    type: "website",
    locale: "zh_CN",
    url: SITE_BASE,
    siteName: "AnimeHub",
    title: "AnimeHub - 热门动漫与最新更新",
    description:
      "浏览 AnimeHub 收录的热门动漫、最新更新与分类精选，支持搜索、分类与排行榜浏览。",
  },
};

const PAGE_SIZE = 18;

// 首页结构化数据：WebSite + SearchAction + 各内容区 ItemList，
// 便于 Google 理解站点搜索与站点板块架构。
function HomeJsonLd() {
  const data = {
    "@context": "https://schema.org",
    "@type": "WebSite",
    name: "AnimeHub",
    url: `${SITE_BASE}/`,
    description: "AnimeHub - 免费在线动漫资料站，收录热门新番、分类精选与高分佳作",
    inLanguage: "zh-CN",
    potentialAction: {
      "@type": "SearchAction",
      target: `${SITE_BASE}/?q={search_term_string}`,
      "query-input": "required name=search_term_string",
    },
    hasPart: [
      {
        "@type": "ItemList",
        name: "热门动漫榜单",
        url: `${SITE_BASE}/top-anime/`,
        position: 1,
      },
      {
        "@type": "ItemList",
        name: "最新更新",
        url: `${SITE_BASE}/latest-anime/`,
        position: 2,
      },
      {
        "@type": "ItemList",
        name: "高分推荐",
        url: `${SITE_BASE}/high-score/`,
        position: 3,
      },
      {
        "@type": "ItemList",
        name: "动漫分类",
        url: `${SITE_BASE}/categories/`,
        position: 4,
      },
    ],
  };
  return (
    <script
      type="application/ld+json"
      // eslint-disable-next-line react/no-danger
      dangerouslySetInnerHTML={{ __html: JSON.stringify(data) }}
    />
  );
}

export default async function HomePage() {
  let initialPage: AnimePage = {
    items: [],
    total: 0,
    page: 1,
    page_size: PAGE_SIZE,
    pages: 0,
  };
  try {
    // 首页初始数据按内容质量排序，避免首屏展示低质量模板动漫
    initialPage = await fetchAnimeByFilter({ sort: "quality" }, 1, PAGE_SIZE);
  } catch {
    // Backend offline: HomeClient will try to reload and show an error message.
  }
  return (
    <>
      <HomeJsonLd />
      <Suspense
        fallback={
          <div className="py-24 text-center text-slate-400">加载中...</div>
        }
      >
        <HomeClient initialPage={initialPage} />
      </Suspense>
    </>
  );
}
