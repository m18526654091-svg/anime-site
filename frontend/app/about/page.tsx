import Link from "next/link";

export const dynamic = "force-static";

const SITE_BASE = (process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000").replace(/\/$/, "");

export const metadata = {
  title: "About AnimeHub - Anime Database, Recommendations & Watch Orders",
  description:
    "AnimeHub is a fan-run anime database and recommendation hub: anime details, similar shows, watch orders, best lists and seasonal lineups.",
  alternates: { canonical: `${SITE_BASE}/about/` },
  robots: { index: true, follow: true },
};

export default function AboutPage() {
  const site = SITE_BASE;
  return (
    <div className="mx-auto max-w-3xl animate-fade-in px-4 py-10">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "AboutPage",
            name: "About AnimeHub",
            url: `${site}/about/`,
            inLanguage: "en",
            mainEntity: {
              "@type": "WebSite",
              name: "AnimeHub",
              url: site,
              description:
                "Anime database with details, similar anime, watch orders, best lists and seasonal lineups.",
            },
          }),
        }}
      />
      <nav className="mb-4 text-sm text-slate-500">
        <Link href="/" className="hover:text-blue-600">Home</Link>
        <span className="mx-2">›</span>
        <span className="text-slate-700">About</span>
      </nav>

      <h1 className="text-3xl font-bold text-slate-900">About AnimeHub</h1>
      <p className="mt-3 text-slate-600">
        AnimeHub is a fan-maintained anime database and recommendation hub. It helps you find
        your next favorite show through anime details, similar anime, watch orders, best lists,
        and seasonal lineups.
      </p>

      <h2 className="mt-8 text-xl font-semibold text-slate-900">What you can do here</h2>
      <ul className="mt-3 list-disc space-y-1.5 pl-5 text-slate-600">
        <li>Browse anime details — scores, genres, release years, studios, and synopses.</li>
        <li>Find <Link href="/best-anime/" className="text-blue-600 hover:underline">best anime</Link> by genre and theme.</li>
        <li>Discover <Link href="/anime/" className="text-blue-600 hover:underline">similar anime</Link> for any title.</li>
        <li>Follow <Link href="/watch-order/" className="text-blue-600 hover:underline">watch orders</Link> for long-running franchises.</li>
        <li>Check <Link href="/seasons/" className="text-blue-600 hover:underline">seasonal lineups</Link>, new anime, and upcoming releases.</li>
        <li>See <Link href="/trending-anime/" className="text-blue-600 hover:underline">trending and popular anime</Link> right now.</li>
      </ul>

      <h2 className="mt-8 text-xl font-semibold text-slate-900">About our data</h2>
      <p className="mt-3 text-slate-600">
        Anime metadata (titles, genres, years, scores, studios, and episode counts) is sourced
        from public anime databases such as AniList and MyAnimeList and is stored in our own
        database. Synopses and descriptions may be automatically generated from metadata fields
        and may not always be accurate. For authoritative information, please refer to the
        original sources.
      </p>
      <p className="mt-3 text-slate-600">
        AnimeHub does not host or stream anime. We are a catalog and recommendation site only.
        All anime, character names, and artwork belong to their respective rights holders.
      </p>

      <h2 className="mt-8 text-xl font-semibold text-slate-900">Project status</h2>
      <p className="mt-3 text-slate-600">
        AnimeHub is a small, independent fan project. There is no company behind it, and no
        fictional team information is presented. The site is provided as-is for anime fans to
        discover and organize shows.
      </p>

      <h2 className="mt-8 text-xl font-semibold text-slate-900">Contact</h2>
      <p className="mt-3 text-slate-600">
        For content corrections, removal requests (e.g. if you hold rights to content shown
        here), or general questions, please contact us via the domain email address of this
        site&apos;s operator, or reach out through a ticket at your hosting provider&apos;s
        contact form. We typically respond within a few days.
      </p>

      <div className="mt-10 border-t border-slate-200 pt-4 text-sm text-slate-500">
        <Link href="/terms/" className="text-blue-600 hover:underline">Terms of Use</Link>
        <span className="mx-2">·</span>
        <Link href="/privacy/" className="text-blue-600 hover:underline">Privacy Policy</Link>
        <span className="mx-2">·</span>
        <Link href="/contact/" className="text-blue-600 hover:underline">Contact</Link>
      </div>
    </div>
  );
}
