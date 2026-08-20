"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import AnimeCard from "@/components/AnimeCard";
import { apiErrorMessage, fetchFavorites } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import type { Anime } from "@/types";

export default function FavoritesClient() {
  const router = useRouter();
  const { isLoggedIn, user, logout, hydrated } = useAuth();
  const [items, setItems] = useState<Anime[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    if (!hydrated) return;
    if (!isLoggedIn) {
      router.replace(`/login?next=/favorites`);
      return;
    }

    let cancelled = false;
    (async () => {
      setLoading(true);
      setError("");
      try {
        const data = await fetchFavorites();
        if (!cancelled) {
          setItems(data);
          setError("");
        }
      } catch (e) {
        if (!cancelled) setError(apiErrorMessage(e));
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [isLoggedIn, hydrated, router]);

  // Not hydrated yet: avoid rendering a flash of empty state.
  if (!hydrated) {
    return (
      <main className="mx-auto max-w-7xl px-4 py-16 text-center">
        <p className="text-slate-400">加载中…</p>
      </main>
    );
  }

  // Not logged in: redirecting to login.
  if (!isLoggedIn) {
    return (
      <main className="mx-auto max-w-7xl px-4 py-16 text-center">
        <p className="text-slate-400">正在跳转到登录页…</p>
      </main>
    );
  }

  // Error (e.g. token expired mid-session).
  if (error) {
    return (
      <main className="mx-auto max-w-7xl px-4 py-16 text-center">
        <div className="mx-auto max-w-md rounded-xl border border-red-500/20 bg-red-500/5 px-4 py-3 text-sm text-red-400">
          {error}
        </div>
      </main>
    );
  }

  // Loading state while fetching the list.
  if (loading && items.length === 0) {
    return (
      <main className="mx-auto max-w-7xl px-4 py-12">
        <p className="mb-4 text-slate-300">加载收藏…</p>
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6">
          {Array.from({ length: 12 }).map((_, i) => (
            <div
              key={i}
              className="aspect-[2/3] w-full animate-pulse rounded-2xl bg-white/10"
            />
          ))}
        </div>
      </main>
    );
  }

  // Empty state.
  if (items.length === 0) {
    return (
      <main className="mx-auto max-w-3xl px-4 py-20 text-center">
        <div className="mb-2 text-5xl">🖤</div>
        <h1 className="mb-2 text-xl font-black text-white">我的收藏</h1>
        <p className="mb-6 text-slate-400">
          暂时没有收藏任何动漫。前往首页发现喜欢的动画吧！
        </p>
        <Link
          href="/"
          className="inline rounded-xl bg-gradient-to-r from-indigo-600 to-pink-600 px-5 py-2.5 font-bold text-white shadow-glow-indigo transition hover:brightness-110"
        >
          ← 去首页发现
        </Link>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-7xl px-4 py-8">
      <header className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-black text-white">我的收藏</h1>
        {user ? (
          <span className="flex items-center gap-2 text-sm text-slate-400">
            <span>👤 {user.username}</span>
            <button
              onClick={() => {
                logout();
                router.replace("/");
              }}
              className="rounded-lg px-2 py-1 text-pink-400 transition hover:underline"
            >
              退出
            </button>
          </span>
        ) : null}
      </header>

      <ul className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6">
        {items.map((a) => (
          <li key={a.id}>
            <AnimeCard anime={a} />
          </li>
        ))}
      </ul>
    </main>
  );
}
