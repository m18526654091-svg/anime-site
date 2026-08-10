"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { apiErrorMessage, createAnime, deleteAnime, fetchAnime } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import type { Anime } from "@/types";

interface FormState {
  title: string;
  genre: string;
  score: string;
  cover: string;
  description: string;
}

const EMPTY_FORM: FormState = { title: "", genre: "", score: "", cover: "", description: "" };

const inputCls =
  "w-full rounded-xl border border-white/10 bg-slate-950/60 px-4 py-2.5 text-white placeholder-slate-500 transition focus:border-pink-500/60 focus:outline-none focus:ring-2 focus:ring-pink-500/40";

export default function AdminPage() {
  const { isLoggedIn, isAdmin, hydrated } = useAuth();
  const router = useRouter();

  const [list, setList] = useState<Anime[]>([]);
  const [form, setForm] = useState<FormState>(EMPTY_FORM);
  const [msg, setMsg] = useState("");
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (hydrated && !isLoggedIn) router.replace("/login");
  }, [hydrated, isLoggedIn, router]);

  useEffect(() => {
    if (!isAdmin) return;
    fetchAnime()
      .then((data) => setList(data))
      .catch((e) => setErr(apiErrorMessage(e)));
  }, [isAdmin]);

  async function handleAdd(e: React.FormEvent) {
    e.preventDefault();
    setMsg("");
    setErr("");
    setLoading(true);
    try {
      await createAnime({
        title: form.title.trim(),
        genre: form.genre.trim(),
        description: form.description.trim(),
        score: form.score ? Number(form.score) : 0,
        cover: form.cover.trim(),
      });
      setForm(EMPTY_FORM);
      setMsg("✅ 添加成功");
      setList(await fetchAnime());
    } catch (e2) {
      setErr(apiErrorMessage(e2));
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(id: number) {
    if (!window.confirm("确认删除该动漫？此操作不可恢复。")) return;
    setMsg("");
    setErr("");
    try {
      await deleteAnime(id);
      setMsg("🗑️ 已删除");
      setList(await fetchAnime());
    } catch (e3) {
      setErr(apiErrorMessage(e3));
    }
  }

  if (!hydrated) {
    return <p className="py-24 text-center text-slate-400">加载中…</p>;
  }
  if (!isLoggedIn) {
    return <p className="py-24 text-center text-slate-400">正在跳转到登录页…</p>;
  }
  if (!isAdmin) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-24 text-center">
        <p className="text-6xl">🔒</p>
        <p className="mt-4 text-slate-400">你没有管理员权限</p>
        <a
          href="/"
          className="mt-6 inline-block rounded-lg bg-white/5 px-5 py-2 text-pink-400 transition hover:bg-white/10"
        >
          ← 返回首页
        </a>
      </div>
    );
  }

  const avgScore = list.length
    ? (list.reduce((s, a) => s + Number(a.score ?? 0), 0) / list.length).toFixed(1)
    : "0.0";

  return (
    <div className="mx-auto max-w-6xl animate-fade-in px-4 py-8">
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-black text-white">🛠️ 管理后台</h1>
          <p className="mt-1 text-slate-400">管理动漫内容，掌控全站数据</p>
        </div>
        <a
          href="/"
          className="inline-flex w-fit items-center rounded-xl border border-white/10 px-4 py-2 text-sm text-slate-300 transition hover:border-pink-500/60 hover:text-white"
        >
          ← 返回首页
        </a>
      </div>

      {/* 数据概览 */}
      <div className="mb-8 grid grid-cols-2 gap-4 sm:grid-cols-3">
        <div className="glass rounded-2xl p-5">
          <p className="text-sm text-slate-400">动漫总数</p>
          <p className="mt-1 text-3xl font-black text-white">{list.length}</p>
        </div>
        <div className="glass rounded-2xl p-5">
          <p className="text-sm text-slate-400">平均评分</p>
          <p className="mt-1 text-3xl font-black text-amber-400">★ {avgScore}</p>
        </div>
        <div className="glass rounded-2xl p-5">
          <p className="text-sm text-slate-400">管理身份</p>
          <p className="mt-1 text-2xl font-black text-pink-400">管理员</p>
        </div>
      </div>

      <div className="grid gap-8 lg:grid-cols-2">
        {/* 添加动漫 */}
        <section className="rounded-3xl border border-white/10 bg-white/5 p-6 backdrop-blur">
          <h2 className="mb-5 flex items-center gap-2 text-lg font-bold text-white">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-pink-600 to-fuchsia-600 text-white">
              ➕
            </span>
            添加动漫
          </h2>

          {(msg || err) && (
            <p
              className={`mb-4 rounded-lg px-3 py-2 text-sm ${
                err
                  ? "bg-red-500/10 text-red-400"
                  : "bg-emerald-500/10 text-emerald-400"
              }`}
            >
              {err || msg}
            </p>
          )}

          <form onSubmit={handleAdd} className="space-y-4">
            <div>
              <label className="mb-1.5 block text-sm font-medium text-slate-300">
                标题 *
              </label>
              <input
                className={inputCls}
                value={form.title}
                onChange={(e) => setForm({ ...form, title: e.target.value })}
                required
                placeholder="动漫名称"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="mb-1.5 block text-sm font-medium text-slate-300">
                  题材
                </label>
                <input
                  className={inputCls}
                  value={form.genre}
                  onChange={(e) => setForm({ ...form, genre: e.target.value })}
                  placeholder="如：冒险/热血"
                />
              </div>
              <div>
                <label className="mb-1.5 block text-sm font-medium text-slate-300">
                  评分
                </label>
                <input
                  className={inputCls}
                  type="number"
                  step="0.1"
                  min="0"
                  max="10"
                  value={form.score}
                  onChange={(e) => setForm({ ...form, score: e.target.value })}
                  placeholder="如：8.5"
                />
              </div>
            </div>
            <div>
              <label className="mb-1.5 block text-sm font-medium text-slate-300">
                封面图 URL（可选）
              </label>
              <input
                className={inputCls}
                value={form.cover}
                onChange={(e) => setForm({ ...form, cover: e.target.value })}
                placeholder="https://…"
              />
            </div>
            <div>
              <label className="mb-1.5 block text-sm font-medium text-slate-300">
                简介
              </label>
              <textarea
                className={`${inputCls} resize-none`}
                rows={4}
                value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
                placeholder="作品简介"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-xl bg-gradient-to-r from-pink-600 to-fuchsia-600 py-3 font-bold text-white shadow-glow transition hover:brightness-110 disabled:opacity-50"
            >
              {loading ? "提交中…" : "添加动漫"}
            </button>
          </form>
        </section>

        {/* 动漫管理列表 */}
        <section className="rounded-3xl border border-white/10 bg-white/5 p-6 backdrop-blur">
          <h2 className="mb-5 flex items-center gap-2 text-lg font-bold text-white">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-sky-600 to-indigo-600 text-white">
              📚
            </span>
            动漫管理（{list.length}）
          </h2>

          <div className="max-h-[600px] space-y-2.5 overflow-y-auto pr-1">
            {list.length === 0 && (
              <p className="py-8 text-center text-slate-500">暂无动漫，先添加一部吧</p>
            )}
            {list.map((a) => (
              <div
                key={a.id}
                className="flex items-center gap-3 rounded-xl border border-white/10 bg-slate-950/50 p-3 transition hover:border-pink-500/40"
              >
                <div className="flex h-11 w-11 shrink-0 items-center justify-center overflow-hidden rounded-lg bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-600 text-base font-black text-white/85">
                  {a.title?.slice(0, 1) || "漫"}
                </div>
                <div className="min-w-0 flex-1">
                  <p className="truncate font-semibold text-slate-100">
                    #{a.id} {a.title}
                  </p>
                  <p className="truncate text-xs text-slate-500">
                    {a.genre || "未知题材"}
                    {a.year ? ` · ${a.year} 年` : ""} · ★{" "}
                    {Number(a.score ?? 0).toFixed(1)}
                  </p>
                </div>
                <div className="flex shrink-0 gap-2">
                  <a
                    href={`/anime/${a.id}`}
                    className="rounded-lg border border-white/10 px-3 py-1.5 text-xs text-slate-300 transition hover:border-pink-500/60 hover:text-white"
                  >
                    查看
                  </a>
                  <button
                    onClick={() => handleDelete(a.id)}
                    className="rounded-lg bg-red-600/80 px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-red-500"
                  >
                    删除
                  </button>
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}