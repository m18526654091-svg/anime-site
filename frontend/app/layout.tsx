import type { Metadata, Viewport } from "next";
import Link from "next/link";
import "./globals.css";
import Providers from "@/components/Providers";
import Navbar from "@/components/Navbar";

// Next.js 14: themeColor 应放在独立 viewport export（避免 metadata 警告）
export const viewport: Viewport = {
  themeColor: "#0f172a",
};

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000"),
  title: {
    default: "AnimeHub - Anime Database, Recommendations & Watch Orders",
    template: "%s | AnimeHub",
  },
  description:
    "AnimeHub is an anime database and recommendation hub: anime details, similar shows, watch orders, best lists, and seasonal lineups.",
  keywords: [
    "anime database",
    "anime recommendations",
    "similar anime",
    "anime watch order",
    "best anime",
    "seasonal anime",
    "trending anime",
  ],
  authors: [{ name: "AnimeHub" }],
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  openGraph: {
    type: "website",
    locale: "en_US",
    url: process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000",
    siteName: "AnimeHub",
    title: "AnimeHub - Anime Database, Recommendations & Watch Orders",
    description:
      "Discover anime, similar shows, watch orders, best lists, and seasonal lineups on AnimeHub.",
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        alt: "AnimeHub - Anime Database, Recommendations & Watch Orders",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "AnimeHub - Anime Database, Recommendations & Watch Orders",
    description:
      "Discover anime, similar shows, watch orders, best lists, and seasonal lineups on AnimeHub.",
    images: ["/og-image.png"],
  },
  // favicon 由 Next.js App Router 约定自动生成：
  //   app/icon.svg + app/icon.png（浏览器标签页）、app/apple-icon.png（Apple touch）、
  //   public/favicon.ico（旧浏览器兼容）。
  alternates: {
    canonical: process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN">
      <body>
        <Providers>
          <Navbar />
          <main>{children}</main>
                    <footer className="mt-16 border-t border-white/10 py-10">
            <div className="mx-auto max-w-7xl px-4">
              <div className="grid grid-cols-1 gap-8 sm:grid-cols-4">
                <div>
                  <div className="mb-3 flex items-center gap-2 text-lg font-extrabold text-white">
                    <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-pink-500 to-indigo-600 text-sm font-black text-white">
                    A
                  </span>
                    Anime<span className="text-pink-500">Hub</span>
                  </div>
                  <p className="text-xs text-slate-400">
                    Anime database &amp; recommendations — no video streaming or downloads.
                  </p>
                </div>

                <div>
                  <p className="mb-3 text-sm font-bold text-white">Explore</p>
                  <ul className="space-y-2 text-sm text-slate-300">
                    <li>
                      <Link href="/trending-anime/" className="hover:text-pink-400">Trending Anime</Link>
                    </li>
                    <li>
                      <Link href="/discover-anime/" className="hover:text-pink-400">Discover Anime</Link>
                    </li>
                    <li>
                      <Link href="/top-anime/" className="hover:text-pink-400">Top Anime</Link>
                    </li>
                    <li>
                      <Link href="/best-anime/" className="hover:text-pink-400">Best Anime Lists</Link>
                    </li>
                    <li>
                      <Link href="/watch-order/" className="hover:text-pink-400">Watch Orders</Link>
                    </li>
                  </ul>
                </div>

                <div>
                  <p className="mb-3 text-sm font-bold text-white">Popular Genres</p>
                  <ul className="flex flex-wrap gap-2 text-sm">
                    {["热血", "奇幻", "战斗", "校园", "恋爱", "悬疑", "科幻", "日常"].map(
                      (g) => (
                        <li key={g}>
                          <Link
                            href={`/categories/${encodeURIComponent(g)}/`}
                            className="rounded-md bg-white/5 px-2.5 py-1 text-slate-300 transition hover:bg-white/10 hover:text-pink-300"
                          >
                            {g}
                          </Link>
                        </li>
                      )
                    )}
                  </ul>
                </div>

                <div>
                  <p className="mb-3 text-sm font-bold text-white">年份</p>
                  <ul className="flex flex-wrap gap-2 text-sm">
                    {[2024, 2023, 2022, 2021, 2020].map((y) => (
                      <li key={y}>
                        <Link
                          href={`/years/${y}/`}
                          className="rounded-md bg-white/5 px-2.5 py-1 text-slate-300 transition hover:bg-white/10 hover:text-pink-300"
                        >
                          {y}
                        </Link>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              <div className="mt-8 border-t border-white/10 pt-5 text-center text-sm text-slate-500">
                <p>
                  Anime<span className="text-pink-500">Hub</span> © 2026 · Free anime directory · Data from real backend API
                </p>
                <div className="mt-3 flex flex-wrap items-center justify-center gap-x-5 gap-y-1 text-xs text-slate-400">
                  <Link href="/about" className="hover:text-pink-400">About</Link>
                  <Link href="/terms" className="hover:text-pink-400">Terms of Use</Link>
                  <Link href="/privacy" className="hover:text-pink-400">Privacy Policy</Link>
                  <Link href="/contact" className="hover:text-pink-400">Contact</Link>
                  <Link href="/copyright" className="hover:text-pink-400">Copyright / DMCA</Link>
                </div>
              </div>
            </div>
          </footer>
        </Providers>
      </body>
    </html>
  );
}