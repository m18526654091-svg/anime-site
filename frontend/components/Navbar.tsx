"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useState } from "react";
import { useAuth } from "@/lib/auth";

const NAV_ITEMS = [
  { label: "首页", href: "/" },
  { label: "最新更新", href: "/latest-anime" },
  { label: "排行", href: "/ranking" },
  { label: "分类", href: "/categories" },
  { label: "年份", href: "/years" },
];

export default function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
    const [kw, setKw] = useState("");
  const { isLoggedIn, user, logout, hydrated } = useAuth();

  const navLink = (href: string) =>
    `whitespace-nowrap rounded-lg px-3 py-2 text-sm font-medium transition ${
      pathname === href
        ? "bg-gradient-to-r from-pink-600/30 to-fuchsia-600/30 text-white"
        : "text-slate-300 hover:bg-white/5 hover:text-white"
    }`;

  function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    router.push(kw.trim() ? `/search?q=${encodeURIComponent(kw.trim())}` : "/search");
  }

  return (
    <header className="sticky top-0 z-50 border-b border-white/10 bg-slate-950/80 backdrop-blur-xl">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-3">
        <Link href="/" className="group flex shrink-0 items-center gap-2">
          <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-pink-500 to-indigo-600 text-sm font-black text-white shadow-glow transition group-hover:scale-110">
            A
          </span>
          <span className="text-xl font-extrabold tracking-tight text-white">
            Anime<span className="text-gradient">Hub</span>
          </span>
        </Link>

        <nav className="hidden items-center gap-1 md:flex">
          {NAV_ITEMS.map((item) => (
            <Link key={item.href} href={item.href} className={navLink(item.href)}>
              {item.label}
            </Link>
          ))}
        </nav>

        <form onSubmit={onSubmit} className="flex max-w-xs flex-1 items-center gap-2">
          <div className="relative flex-1">
            <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 text-sm">
              🔍
            </span>
            <input
              value={kw}
              onChange={(e) => setKw(e.target.value)}
              placeholder="搜索动漫..."
              className="w-full rounded-full border border-white/10 bg-slate-900/60 py-2 pl-9 pr-4 text-sm text-white placeholder-slate-500 backdrop-blur transition focus:border-pink-500/60 focus:outline-none focus:ring-2 focus:ring-pink-500/30"
            />
          </div>
          <button
            type="submit"
            className="hidden rounded-full bg-gradient-to-r from-pink-600 to-fuchsia-600 px-4 py-2 text-sm font-semibold text-white shadow-glow transition hover:brightness-110 sm:inline-block"
          >
            搜索
          </button>
                </form>

        <div className="flex items-center gap-1">
          <Link
            href="/favorites"
            aria-label="我的收藏"
            className="flex h-9 w-9 items-center justify-center rounded-lg text-slate-300 transition hover:bg-white/5 hover:text-pink-400"
          >
            ❤️
          </Link>

          {hydrated && isLoggedIn ? (
            <div className="flex items-center gap-1 text-sm">
              <span className="hidden text-slate-300 sm:inline">
                👤 {user?.username}
              </span>
              <button
                type="button"
                onClick={() => {
                  logout();
                  router.replace("/");
                }}
                className="rounded-lg px-2 py-1 text-pink-400 transition hover:text-pink-300"
                aria-label="退出登录"
              >
                退出
              </button>
            </div>
          ) : hydrated && !isLoggedIn ? (
            <>
              <Link
                href="/login"
                aria-label="登录"
                className="flex h-9 w-9 items-center justify-center rounded-lg text-slate-300 transition hover:bg-white/5 hover:text-pink-400 sm:hidden"
              >
                👤
              </Link>
              <div className="hidden items-center gap-1 sm:flex">
                <Link href="/login" className={navLink("/login")}>
                  登录
                </Link>
                <Link href="/register" className={navLink("/register")}>
                  注册
                </Link>
              </div>
            </>
          ) : null}
        </div>
      </div>
    </header>
  );
}