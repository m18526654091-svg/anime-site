import Link from "next/link";

export const dynamic = "force-static";

const SITE_BASE = (process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000").replace(/\/$/, "");

export const metadata = {
  title: "Terms of Use - AnimeHub",
  description:
    "Terms of use for AnimeHub: acceptable use, content rights, data accuracy disclaimers, and liability limits for this fan-run anime database.",
  alternates: { canonical: `${SITE_BASE}/terms/` },
  robots: { index: true, follow: true },
};

export default function TermsPage() {
  const site = SITE_BASE;
  return (
    <div className="mx-auto max-w-3xl animate-fade-in px-4 py-10">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "WebPage",
            name: "Terms of Use",
            url: `${site}/terms/`,
            inLanguage: "en",
          }),
        }}
      />
      <nav className="mb-4 text-sm text-slate-500">
        <Link href="/" className="hover:text-blue-600">Home</Link>
        <span className="mx-2">›</span>
        <span className="text-slate-700">Terms of Use</span>
      </nav>

      <h1 className="text-3xl font-bold text-slate-900">Terms of Use</h1>
      <p className="mt-3 text-slate-600">
        By accessing AnimeHub, you agree to the following terms. If you do not agree, please do
        not use the site.
      </p>

      <h2 className="mt-8 text-xl font-semibold text-slate-900">1. Nature of the service</h2>
      <p className="mt-2 text-slate-600">
        AnimeHub is a fan-run catalog and recommendation website. It provides anime metadata
        such as titles, scores, genres, release years, and links to similar shows and watch
        orders. AnimeHub does not host or stream anime videos, and does not provide downloads.
      </p>

      <h2 className="mt-8 text-xl font-semibold text-slate-900">2. Acceptable use</h2>
      <ul className="mt-2 list-disc space-y-1.5 pl-5 text-slate-600">
        <li>Do not scrape, crawl, or bulk-download the site without permission.</li>
        <li>Do not attempt to disrupt, overload, or gain unauthorized access to the service.</li>
        <li>Do not post spam, abuse, or illegal content in any interactive feature.</li>
        <li>Do not use the site in any way that violates applicable law.</li>
      </ul>

      <h2 className="mt-8 text-xl font-semibold text-slate-900">3. Content and data accuracy</h2>
      <p className="mt-2 text-slate-600">
        Anime metadata is aggregated from public sources and may contain errors or become
        outdated. Some descriptions are automatically generated from metadata fields. AnimeHub
        makes no warranty about the accuracy, completeness, or reliability of any content on
        this site. Users should verify details against official or authoritative sources.
      </p>

      <h2 className="mt-8 text-xl font-semibold text-slate-900">4. Intellectual property</h2>
      <p className="mt-2 text-slate-600">
        All anime titles, characters, artwork, and related names are the property of their
        respective copyright holders. AnimeHub does not claim ownership of any third-party
        content displayed on the site. If you believe your copyrighted work is shown here
        inappropriately, contact us and we will review and remove it promptly.
      </p>

      <h2 className="mt-8 text-xl font-semibold text-slate-900">5. Disclaimer of warranties</h2>
      <p className="mt-2 text-slate-600">
        The service is provided &quot;as is&quot; and &quot;as available&quot; without warranties
        of any kind, whether express or implied, including but not limited to fitness for a
        particular purpose and non-infringement.
      </p>

      <h2 className="mt-8 text-xl font-semibold text-slate-900">6. Limitation of liability</h2>
      <p className="mt-2 text-slate-600">
        To the maximum extent permitted by law, AnimeHub and its operators shall not be liable
        for any indirect, incidental, special, consequential, or punitive damages arising from
        your use of the site.
      </p>

      <h2 className="mt-8 text-xl font-semibold text-slate-900">7. Changes to these terms</h2>
      <p className="mt-2 text-slate-600">
        We may update these terms from time to time. Continued use of the site after changes
        constitutes acceptance of the updated terms.
      </p>

      <div className="mt-10 border-t border-slate-200 pt-4 text-sm text-slate-500">
        <Link href="/about/" className="text-blue-600 hover:underline">About</Link>
        <span className="mx-2">·</span>
        <Link href="/privacy/" className="text-blue-600 hover:underline">Privacy Policy</Link>
        <span className="mx-2">·</span>
        <Link href="/contact/" className="text-blue-600 hover:underline">Contact</Link>
      </div>
    </div>
  );
}
