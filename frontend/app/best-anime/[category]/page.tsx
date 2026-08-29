import Link from "next/link";
import { notFound } from "next/navigation";
import { fetchAnimeByFilter } from "@/lib/api";
import { animePath } from "@/lib/slug";
import { shortReason } from "@/components/TrendingCard";
import type { Anime } from "@/types";

export const dynamic = "force-dynamic";
export const revalidate = 3600;

const SITE_BASE = (process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000").replace(/\/$/, "");
const PAGE_SIZE = 24;

const CATEGORY_META: Record<string, { title: string; genres: string[]; intro: string; filter: string }> = {
  isekai: {
    title: "Isekai",
    genres: ["异世界", "穿越"],
    filter: "genre",
    intro:
      "Isekai anime transport heroes to fantastical other worlds — from epic reincarnation adventures to dungeon-crawling quests. These are the highest-rated isekai shows ranked by score.",
  },
  action: {
    title: "Action",
    genres: ["动作", "战斗", "热血"],
    filter: "genre",
    intro:
      "High-octane action anime deliver jaw-dropping fights, power systems, and unstoppable heroes. Here are the top action series ranked by score.",
  },
  romance: {
    title: "Romance",
    genres: ["恋爱", "爱情"],
    filter: "genre",
    intro:
      "Heartfelt romance anime capture the thrill of first love, emotional confessions, and character-driven drama. These are the best romance shows ranked by score.",
  },
  fantasy: {
    title: "Fantasy",
    genres: ["奇幻", "魔法"],
    filter: "genre",
    intro:
      "Immersive fantasy anime build rich worlds full of magic, mythical creatures, and epic quests. Here are the highest-rated fantasy series ranked by score.",
  },
  horror: {
    title: "Horror",
    genres: ["恐怖", "惊悚"],
    filter: "genre",
    intro:
      "Tense, unsettling horror anime keep you on edge with supernatural dread and psychological twists. These are the best horror shows ranked by score.",
  },
  comedy: {
    title: "Comedy",
    genres: ["搞笑", "喜剧"],
    filter: "genre",
    intro:
      "Sharp, hilarious comedy anime deliver laugh-out-loud moments and unforgettable characters. Here are the top comedy series ranked by score.",
  },
  psychological: {
    title: "Psychological",
    genres: ["心理", "悬疑", "黑暗"],
    filter: "genre",
    intro: "Mind-bending psychological anime dive into the human mind — paranoia, moral dilemmas, and twists that keep you thinking long after the credits.",
  },
  "slice-of-life": {
    title: "Slice of Life",
    genres: ["日常", "治愈"],
    filter: "genre",
    intro: "Warm, calming slice-of-life anime capture everyday moments, friendship, and the small joys of life. Perfect for a relaxing binge.",
  },
  short: {
    title: "Short",
    genres: ["恋爱", "奇幻", "日常", "悬疑"],
    filter: "short",
    intro: "Great anime that respect your time — complete, satisfying stories in 12 to 24 episodes. Ideal for newcomers and busy viewers.",
  },
  beginners: {
    title: "Beginner",
    genres: ["热血", "恋爱", "奇幻", "动作", "治愈"],
    filter: "beginner",
    intro: "The best anime for beginners — universally beloved, easy to get into, and the perfect starting point for anyone new to the medium.",
  },
  saddest: {
    title: "Saddest",
    genres: ["治愈", "恋爱", "青春"],
    filter: "saddest",
    intro: "Emotionally devastating anime that will make you cry — beautiful stories about loss, love, and the things we hold onto.",
  },
  "happy-ending-romance": {
    title: "Romance With Happy Ending",
    genres: ["恋爱"],
    filter: "romance-happy",
    intro: "Heartwarming romance anime with satisfying, happy endings. Feel-good love stories you can watch without the heartbreak.",
  },
  mystery: {
    title: "Mystery",
    genres: ["悬疑", "推理", "侦探"],
    filter: "genre",
    intro: "Mystery anime revolve around crimes, puzzles, and cases waiting to be solved — whodunits, detective stories, and mind-bending riddles ranked by score.",
  },
  mecha: {
    title: "Mecha",
    genres: ["机甲", "机器人"],
    filter: "genre",
    intro: "Mecha anime center on piloted robots — from war epics and political dramas to classic super-robot battles. Here are the top mecha series ranked by score.",
  },
  sports: {
    title: "Sports",
    genres: ["运动"],
    filter: "genre",
    intro: "Sports anime capture the thrill of competition — underdog comebacks, team bonds, and relentless training. The best sports shows ranked by score.",
  },
  school: {
    title: "School",
    genres: ["校园"],
    filter: "genre",
    intro: "School anime are set in classrooms, clubs, and campuses — romance, drama, and comedy under the same school roof. The top school-set shows ranked by score.",
  },
  adventure: {
    title: "Adventure",
    genres: ["冒险"],
    filter: "genre",
    intro: "Adventure anime take heroes on journeys across new worlds — quests, discoveries, and growth along the road. The best adventure series ranked by score.",
  },
  underrated: {
    title: "Underrated",
    genres: ["动作", "奇幻", "恋爱", "悬疑", "科幻", "日常"],
    filter: "underrated",
    intro: "Underrated anime that deserve more attention — high-quality shows with strong scores that often fly under the radar. Hidden gems worth discovering.",
  },
  historical: {
    title: "Historical",
    genres: ["历史", "时代剧", "战国", "武士"],
    filter: "genre",
    intro: "Historical anime bring the past to life — samurai epics, war dramas, and period pieces grounded in real history. The best historical shows ranked by score.",
  },
};

function getSiteBase(): string {
  return SITE_BASE;
}

export async function generateMetadata({ params }: { params: { category: string } }) {
  const meta = CATEGORY_META[params.category];
  if (!meta) {
    return { title: "Best Anime", robots: { index: false, follow: false } };
  }
  const canonical = `${getSiteBase()}/best-anime/${params.category}/`;
  const title = `Best ${meta.title} Anime: Top Shows To Watch`;
  const description = `Looking for the best ${meta.title.toLowerCase()} anime? We ranked the top shows by score — with genres, release years, and watch links.`;
  return {
    title: { absolute: title },
    description: description.slice(0, 158),
    alternates: { canonical },
    openGraph: {
      type: "website",
      locale: "en_US",
      url: canonical,
      siteName: "AnimeHub",
      title,
      description: description.slice(0, 158),
    },
    twitter: { card: "summary_large_image", title, description: description.slice(0, 158) },
  };
}

async function fetchRanked(genres: string[], filter: string): Promise<Anime[]> {
  const seen = new Map<number, Anime>();
  for (const g of genres) {
    try {
      const page = await fetchAnimeByFilter({ category: g, sort: "score" }, 1, PAGE_SIZE);
      for (const a of page.items) {
        if (!seen.has(a.id)) seen.set(a.id, a);
      }
    } catch {
      // ignore single-genre failure
    }
  }
  let list = Array.from(seen.values());
  if (filter === "short") {
    list = list.filter((a) => (a.episodes ?? 99) <= 26);
  } else if (filter === "beginner") {
    list = list.filter((a) => (a.episodes ?? 99) <= 60);
  } else if (filter === "underrated") {
    // 高分但曝光低（seo_priority 低）= 值得被发现的隐藏佳作
    list = list.filter((a) => (a.score || 0) >= 7.5 && (a.anime_seo_priority || 0) < 60);
  }
  return list.sort((x, y) => (y.score || 0) - (x.score || 0)).slice(0, PAGE_SIZE);
}
export default async function BestAnimeCategoryPage({ params }: { params: { category: string } }) {
  const meta = CATEGORY_META[params.category];
  if (!meta) notFound();

  const list = await fetchRanked(meta.genres, meta.filter);
  const canonical = `${getSiteBase()}/best-anime/${params.category}/`;

  return (
    <div className="mx-auto max-w-5xl animate-fade-in px-4 py-10">
      {/* BreadcrumbList JSON-LD */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            itemListElement: [
              { "@type": "ListItem", position: 1, name: "Home", item: `${getSiteBase()}/` },
              { "@type": "ListItem", position: 2, name: "Best Anime", item: `${getSiteBase()}/best-anime/` },
              { "@type": "ListItem", position: 3, name: `Best ${meta.title} Anime`, item: canonical },
            ],
          }),
        }}
      />
      {/* ItemList JSON-LD */}
      {list.length > 0 && (
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@type": "ItemList",
              name: `Best ${meta.title} Anime`,
              numberOfItems: list.length,
              itemListElement: list.map((a, i) => ({
                "@type": "ListItem",
                position: i + 1,
                url: `${getSiteBase()}${animePath(a)}/`,
                name: a.chinese_title || a.title,
              })),
            }),
          }}
        />
      )}

      <nav className="mb-4 text-sm text-slate-500">
        <Link href="/" className="hover:text-blue-600">Home</Link>
        <span className="mx-2">›</span>
        <Link href="/best-anime/" className="hover:text-blue-600">Best Anime</Link>
        <span className="mx-2">›</span>
        <span className="text-slate-700">Best {meta.title} Anime</span>
      </nav>

      <h1 className="text-3xl font-bold text-slate-900">Best {meta.title} Anime: Top Shows To Watch</h1>
      <p className="mt-3 max-w-3xl text-slate-600">{meta.intro}</p>

      <div className="mt-8 space-y-4">
        {list.length === 0 && <p className="text-slate-500">No {meta.title.toLowerCase()} anime found yet.</p>}
        {list.map((a, idx) => (
          <div
            key={a.id}
            className="flex items-center gap-4 rounded-xl border border-slate-200 p-4 shadow-sm transition hover:shadow-md"
          >
            <div className="w-10 shrink-0 text-center text-2xl font-black text-slate-300">
              {idx + 1}
            </div>
            <Link href={animePath(a)} className="shrink-0">
              {a.cover ? (
                <img src={a.cover} alt={a.chinese_title || a.title}
                     className="h-24 w-16 rounded-md object-cover" loading="lazy" />
              ) : (
                <div className="flex h-24 w-16 items-center justify-center rounded-md bg-gradient-to-br from-indigo-500 to-purple-600 text-xl text-white">
                  {(a.chinese_title || a.title).charAt(0).toUpperCase()}
                </div>
              )}
            </Link>
            <div className="min-w-0">
              <Link href={animePath(a)} className="text-lg font-semibold text-slate-900 hover:text-blue-600">
                {a.chinese_title || a.title}
              </Link>
              <div className="mt-1 flex flex-wrap gap-1.5 text-xs text-slate-500">
                <span className="rounded bg-slate-100 px-1.5 py-0.5">{a.genre}</span>
                {a.year ? <span className="rounded bg-slate-100 px-1.5 py-0.5">{a.year}</span> : null}
                {a.score ? <span className="rounded bg-amber-50 px-1.5 py-0.5 text-amber-700">★ {a.score.toFixed(1)}</span> : null}
              </div>
              <p className="mt-1 text-xs text-slate-500">{shortReason(a)}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

