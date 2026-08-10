import type { Metadata } from "next";
import "./globals.css";
import Providers from "@/components/Providers";
import Navbar from "@/components/Navbar";

export const metadata: Metadata = {
  title: {
    default: "AnimeHub - 免费在线动漫资源站",
    template: "%s | AnimeHub",
  },
  description: "AnimeHub 是免费的在线动漫资源站，提供热门动漫、最新更新、分类浏览与详细动漫资料。每天更新，支持手机与电脑访问。",
  keywords: ["动漫", "在线动漫", "动漫资源站", "新番", "动漫排行榜", "免费动漫", "动漫详情", "热门动漫"],
  authors: [{ name: "AnimeHub" }],
  openGraph: {
    type: "website",
    locale: "zh_CN",
    url: process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000",
    siteName: "AnimeHub",
    title: "AnimeHub - 免费在线动漫资源站",
    description: "收录热门动漫与最新更新，分类清晰，即点即看。",
  },
  twitter: {
    card: "summary_large_image",
    title: "AnimeHub - 免费在线动漫资源站",
    description: "收录热门动漫与最新更新，分类清晰，即点即看。",
  },
  icons: {
    icon: "/favicon.ico",
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
          <footer className="mt-12 border-t border-white/10 py-6 text-center text-sm text-slate-500">
            <p>
              Anime<span className="text-pink-500">Hub</span> © 2026 · Free anime directory · Data from real backend API
            </p>
          </footer>
        </Providers>
      </body>
    </html>
  );
}