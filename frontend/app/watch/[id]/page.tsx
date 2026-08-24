import { notFound } from "next/navigation";
import Link from "next/link";
import { fetchAnimeDetail, fetchEpisodes } from "@/lib/api";
import type { Anime, Episode } from "@/types";
import { animePath } from "@/lib/slug";
import type { Metadata } from "next";

export const dynamic = "force-dynamic";

const SITE_BASE = (process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000").replace(/\/$/, "");

// watch 播放页不独立作为 SEO 落地页：noindex（搜索入口统一走 /anime/[slug] 详情页）
// 策略在下方 generateMetadata 中统一声明（含不存在时的 noindex）

export async function generateMetadata({
  params,
}: {
  params: { id: string };
}): Promise<Metadata> {
  const id = Number(params.id);
  if (!Number.isFinite(id)) {
    return { title: "动漫不存在", robots: { index: false, follow: false } };
  }
  try {
    const anime = await fetchAnimeDetail(id);
    return {
      title: `${anime.chinese_title || anime.title} 在线观看 - AnimeHub`,
      description: `在线播放 ${anime.chinese_title || anime.title}。`,
      robots: { index: false, follow: true },
      // canonical 指向 SEO 详情页，避免 /watch/{id} 被当作重复落地页
      alternates: { canonical: `${SITE_BASE}${animePath(anime)}/` },
    };
  } catch {
    return { title: "动漫不存在", robots: { index: false, follow: false } };
  }
}

export default async function WatchPage({
  params,
  searchParams,
}: {
  params: { id: string };
  searchParams: { ep?: string };
}) {
  const id = Number(params.id);
  if (!Number.isFinite(id)) {
    notFound();
  }

  let anime: Anime | null = null;
  let episodes: Episode[] = [];

  try {
    anime = await fetchAnimeDetail(id);
  } catch {
    notFound(); // 动漫不存在 / 后端不可达 → 真 404
  }
  try {
    const data = await fetchEpisodes(id);
    episodes = data.items;
  } catch {
    episodes = []; // 播放资源获取失败 → 显示「暂无播放资源」
  }

  const requestedEp = Number(searchParams?.ep);
  const currentEpisode = episodes.find((ep) => ep.episode_number === requestedEp) ?? episodes[0];
  const title = anime.chinese_title || anime.title;

  return (
    <div className="mx-auto max-w-6xl animate-fade-in px-4 py-8">
      {/* Video Player Area */}
      <div className="relative w-full rounded-3xl border border-white/10 bg-black/80 backdrop-blur">
        {currentEpisode ? (
          <div className="relative aspect-video w-full">
            <video
              key={currentEpisode.id}
              controls
              autoPlay
              className="h-full w-full rounded-3xl"
              poster={anime.cover || undefined}
            >
              <source src={currentEpisode.video_url} type="video/mp4" />
              您的浏览器不支持视频播放
            </video>
          </div>
        ) : (
          <div className="flex aspect-video w-full items-center justify-center">
            <div className="text-center">
              <p className="text-4xl">🎬</p>
              <p className="mt-3 text-slate-400">暂无播放资源</p>
            </div>
          </div>
        )}
      </div>

      {/* Info */}
      <div className="mt-6">
        <h1 className="text-2xl font-black text-white sm:text-3xl">{title}</h1>
        {currentEpisode && (
          <p className="mt-2 text-slate-400">
            正在播放：第 {currentEpisode.episode_number} 集 {currentEpisode.title ? `- ${currentEpisode.title}` : ""}
          </p>
        )}
      </div>

      {/* Episode List */}
      {episodes.length > 0 ? (
        <section className="mt-8">
          <h2 className="mb-4 text-xl font-bold text-white">选集</h2>
          <div className="grid grid-cols-4 gap-3 sm:grid-cols-6 md:grid-cols-8 lg:grid-cols-10">
            {episodes.map((ep) => (
              <Link
                key={ep.id}
                href={`/watch/${id}?ep=${ep.episode_number}`}
                className={`flex items-center justify-center rounded-lg py-3 text-sm font-medium transition ${
                  ep.id === currentEpisode?.id
                    ? "bg-gradient-to-br from-pink-600 to-fuchsia-600 text-white shadow-glow"
                    : "bg-white/5 text-slate-300 hover:bg-white/10"
                }`}
              >
                {ep.title || `第${ep.episode_number}集`}
              </Link>
            ))}
          </div>
        </section>
      ) : (
        <div className="mt-8 rounded-3xl border border-white/10 bg-white/5 p-8 text-center">
          <p className="text-slate-400">暂无剧集</p>
        </div>
      )}

      {/* Back Button */}
      <div className="mt-8">
        <Link
          href={`/anime/${id}`}
          className="inline-flex items-center gap-2 rounded-xl bg-white/5 px-5 py-2.5 text-sm font-medium text-slate-300 transition hover:bg-white/10 hover:text-white"
        >
          ← 返回详情页
        </Link>
      </div>
    </div>
  );
}
