import Link from "next/link";

export const dynamic = "force-dynamic";

const CATEGORIES = [
  { slug: "isekai", label: "Best Isekai Anime" },
  { slug: "action", label: "Best Action Anime" },
  { slug: "romance", label: "Best Romance Anime" },
  { slug: "fantasy", label: "Best Fantasy Anime" },
  { slug: "horror", label: "Best Horror Anime" },
  { slug: "comedy", label: "Best Comedy Anime" },
];

const SITE_BASE = (process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000").replace(/\/$/, "");

export const metadata = {
  title: "Best Anime Lists: Top Shows by Genre",
  description:
    "Discover the best anime by genre — isekai, action, romance, fantasy, horror and comedy. Ranked by score, with release info and watch links.",
};

export default function BestAnimeIndexPage() {
  return (
    <div className="mx-auto max-w-4xl animate-fade-in px-4 py-10">
      <h1 className="text-3xl font-bold text-slate-900">Best Anime Lists</h1>
      <p className="mt-3 text-slate-600">
        Top-rated anime ranked by genre. Whether you love epic isekai adventures, high-octane
        action, heartfelt romance, or edge-of-your-seat horror — find the best shows to watch next.
      </p>
      <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2">
        {CATEGORIES.map((c) => (
          <Link
            key={c.slug}
            href={`/best-anime/${c.slug}/`}
            className="group rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:shadow-md"
          >
            <div className="text-lg font-semibold text-slate-900 group-hover:text-blue-600">
              {c.label}
            </div>
            <div className="mt-1 text-sm text-slate-500">Top shows ranked by score →</div>
          </Link>
        ))}
      </div>
      <div className="mt-8">
        <p className="text-sm text-slate-500">
          Sitemap: {`${SITE_BASE}/best-anime/`}
        </p>
      </div>
    </div>
  );
}
