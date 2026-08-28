import Link from "next/link";
import { FRANCHISES, WATCH_ORDER_FRANCHISES } from "@/lib/watchOrder";

export const dynamic = "force-dynamic";

export const metadata = {
  title: "Anime Watch Orders: How to Watch in the Correct Order",
  description:
    "Find the correct watch order for popular anime — Attack on Titan, Naruto, Code Geass, One Piece and Dragon Ball, with seasons, movies and specials in order.",
  alternates: {
    canonical: `${process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000"}/watch-order/`,
  },
};

export default function WatchOrderIndexPage() {
  return (
    <div className="mx-auto max-w-4xl animate-fade-in px-4 py-10">
      <h1 className="text-3xl font-bold text-slate-900">Anime Watch Orders</h1>
      <p className="mt-3 text-slate-600">
        Long-running and multi-season anime can be confusing to watch in order. We break down the
        correct viewing sequence for each franchise — every season, movie, and special, in the
        order that makes the story make sense.
      </p>
      <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2">
        {WATCH_ORDER_FRANCHISES.map((slug) => (
          <Link
            key={slug}
            href={`/watch-order/${slug}/`}
            className="group rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:shadow-md"
          >
            <div className="text-lg font-semibold text-slate-900 group-hover:text-blue-600">
              {FRANCHISES[slug].name} Watch Order
            </div>
            <div className="mt-1 line-clamp-2 text-sm text-slate-500">{FRANCHISES[slug].intro}</div>
          </Link>
        ))}
      </div>
      <div className="mt-8">
        <Link href="/best-anime/" className="text-blue-600 hover:underline">
          Browse Best Anime Lists →
        </Link>
      </div>
    </div>
  );
}
