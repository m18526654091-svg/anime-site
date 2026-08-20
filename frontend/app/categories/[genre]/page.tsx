import Link from "next/link";
import ListPageView from "@/components/ListPageView";
import { fetchAnimeByFilter } from "@/lib/api";
import { animePath } from "@/lib/slug";
import { getSiteBase } from "@/lib/site";
import type { AnimePage } from "@/types";

export const dynamic = "force-dynamic";

const PAGE_SIZE = 24;

function pageUrl(genre: string, page: number) {
  return `/categories/${encodeURIComponent(genre)}?page=${page}`;
}

/** 分类简介（静态兜底，未来可迁移到后台管理）。 */
const CATEGORY_INTRO: Record<string, string> = {
  动作: "热血激斗、视觉冲击的动作题材，展现英雄的成长与冒险旅程。",
  热血: "情感爆发、激情四溅的热血动漫，充满战斗与成长的节奏。",
  奇幻: "异界幻境、魔法龙战的奇幻题材，讲述超乎想象的冒险故事。",
  科幻: "未来世界、机甲科幻题材，探索科技与人性的碰撞。",
  悬疑: "悬念迭起、反差剧的悬疑题材，带你一步步揭开谜底。",
  恋爱: "感情纠葛、甜蜜回忆的恋爱动漫，记录青春与爱的故事。",
  校园: "学生时代的校园故事，友情、成长与热血的纯净叙事。",
  战斗: "武侠格斗、拳拳到肉的战斗题材，展现爆拳与内功的精彩。",
  日常: "普通生活中的小确幸，轻松搞笑的日常题材。",
};

function categoryDescription(genre: string): string {
  return (
    CATEGORY_INTRO[genre] ||
    `AnimeHub 收录的${genre}类型动漫资源，按热度与评分排序，免费在线观看。`
  );
}

/** JSON-LD: WebPage + ItemList（收录本页动漫） */
function buildCategoryJsonLd(genre: string, page: AnimePage) {
  const base = getSiteBase();
  const list = Array.isArray(page.items) ? page.items : [];
  const page_size = page.page_size || PAGE_SIZE;
  const itemListElement = list.map((a, i) => ({
    "@type": "ListItem",
    position: (page.page - 1) * page_size + i + 1,
    url: `${base}${animePath(a)}`,
    name: a.chinese_title || a.title,
  }));
  return {
    "@context": "https://schema.org",
    "@type": "WebPage",
    name: `${genre}动漫推荐 - AnimeHub`,
    description: categoryDescription(genre),
    url: `${base}/categories/${encodeURIComponent(genre)}`,
    ...(list.length
      ? {
          mainEntity: {
            "@type": "ItemList",
            name: `${genre}动漫列表`,
            numberOfItems: page.total,
            itemListElement,
          },
        }
      : {}),
  };
}

export async function generateMetadata({ params }: { params: { genre: string } }) {
  const genre = decodeURIComponent(params.genre);
  const base = getSiteBase();
  const desc = categoryDescription(genre);
  return {
    title: `${genre}动漫推荐 - AnimeHub`,
    description: desc.slice(0, 160),
    alternates: {
      canonical: `${base}/categories/${encodeURIComponent(genre)}`,
    },
    openGraph: {
      type: "website",
      locale: "zh_CN",
      url: `${base}/categories/${encodeURIComponent(genre)}`,
      siteName: "AnimeHub",
      title: `${genre}动漫推荐 - AnimeHub`,
      description: desc.slice(0, 160),
    },
  };
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

  let data: AnimePage = {
    items: [],
    total: 0,
    page: 1,
    page_size: PAGE_SIZE,
    pages: 0,
  };
  try {
    data = await fetchAnimeByFilter({ category: genre }, page, PAGE_SIZE);
  } catch {
    // backend offline; render empty state
  }

  return (
    <div className="mx-auto max-w-7xl animate-fade-in px-4 py-8">
      {/* 分类简介 */}
      <section className="mb-8">
        <h1 className="text-3xl font-black text-white">
          {genre}动漫推荐
        </h1>
        <p className="mt-2 max-w-3xl text-slate-300">
          {categoryDescription(genre)}
        </p>
      </section>

      {/* 站内导航：热门/高分/最新入口（增强爬虫路径） */}
      <div className="mb-6 flex flex-wrap gap-2 text-sm">
        <Link href="/top-anime" className="rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-slate-300 transition hover:border-pink-500/50 hover:text-white">
          热门动漫
        </Link>
        <Link href="/high-score" className="rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-slate-300 transition hover:border-pink-500/50 hover:text-white">
          高分推荐
        </Link>
        <Link href="/latest-anime" className="rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-slate-300 transition hover:border-pink-500/50 hover:text-white">
          最新更新
        </Link>
        <Link href="/genres" className="rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-slate-300 transition hover:border-pink-500/50 hover:text-white">
          全部类型
        </Link>
      </div>

      {/* 分类页 JSON-LD (WebPage + ItemList) */}
      <script
        type="application/ld+json"
        // eslint-disable-next-line react/no-danger
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(buildCategoryJsonLd(genre, data)),
        }}
      />

      <ListPageView
        title={`${genre}动漫`}
        subtitle={`「${genre}」题材动漫精选，按热度与评分排序。`}
        items={data.items}
        total={data.total}
        page={data.page}
        pages={data.pages}
        pageUrl={(p) => pageUrl(genre, p)}
      />
    </div>
  );
}
