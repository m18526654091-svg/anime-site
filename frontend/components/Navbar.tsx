"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Navbar() {
  const pathname = usePathname();

  const navLink = (base: string) =>
    `rounded-lg px-4 py-2 font-medium transition ${
      pathname === base
        ? "bg-white/10 text-white"
        : "text-slate-300 hover:bg-white/5 hover:text-white"
    }`;

  return (
    <header className="sticky top-0 z-50 border-b border-white/10 bg-slate-950/70 backdrop-blur-xl">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <Link href="/" className="group flex items-center gap-2">
          <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-pink-500 to-indigo-600 text-xl shadow-glow transition group-hover:scale-110">
            🎬
          </span>
          <span className="text-xl font-extrabold tracking-tight text-white">
            Anime<span className="text-gradient">Hub</span>
          </span>
        </Link>

        <nav className="flex items-center gap-1 text-sm sm:gap-2">
          <Link href="/" className={navLink("/")}>
            Home
          </Link>

          {pathname.startsWith("/anime") && (
            <span className="hidden rounded-lg px-4 py-2 font-medium text-slate-300 md:inline">
              Detail
            </span>
          )}
        </nav>
      </div>
    </header>
  );
}