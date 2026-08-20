import Link from "next/link";
import { fetchTags } from "@/lib/api";

export const dynamic = "force-dynamic";

export async function generateMetadata() {
  return {
    title: "动漫标签大全 - 按标签浏览动漫",
    description:
      "按标签浏览 AnimeHub 收录的全部动漫，包含热血、治愈、悬疑、恋爱等热门标签，快速找到感兴趣题材，免费在线观看。",
  };
}

export default async function TagsIndexPage() {
  let tags: { tag: string; count: number }[] = [];
  try {
    tags = await fetchTags();
  } catch {
    // backend offline; render empty state
  }

  return (
    <div className="mx-auto max-w-7xl animate-fade-in px-4 py-8">
      <header className="mb-8">
        <h1 className="text-3xl font-black text-white">动漫标签大全</h1>
        <p className="mt-2 text-slate-400">按标签浏览全部动漫作品</p>
      </header>

      {tags.length === 0 ? (
        <p className="py-20 text-center text-slate-500">暂无标签数据</p>
      ) : (
        <div className="flex flex-wrap gap-3">
          {tags.map((t) => (
            <Link
              key={t.tag}
              href={`/tags/${encodeURIComponent(t.tag)}`}
              className="group rounded-full border border-white/10 bg-white/5 px-5 py-2.5 text-sm font-medium text-slate-300 backdrop-blur transition hover:border-pink-500/60 hover:text-white hover:shadow-glow"
            >
              {t.tag}
              <span className="ml-1.5 text-xs text-slate-500">{t.count}</span>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}