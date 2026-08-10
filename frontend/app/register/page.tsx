"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { apiErrorMessage, registerRequest } from "@/lib/api";
import { useAuth } from "@/lib/auth";

export default function RegisterPage() {
  const router = useRouter();
  const { saveAuth } = useAuth();
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    if (password !== confirm) {
      setError("两次输入的密码不一致");
      return;
    }
    if (password.length < 6) {
      setError("密码长度至少 6 位");
      return;
    }
    setLoading(true);
    try {
      const data = await registerRequest({
        username: username.trim(),
        email: email.trim(),
        password,
      });
      saveAuth(data);
      router.push("/");
      router.refresh();
    } catch (err) {
      setError(apiErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="relative mx-auto flex min-h-[70vh] max-w-lg items-center px-4 py-16">
      <div className="pointer-events-none absolute left-1/2 top-16 -z-10 h-72 w-72 -translate-x-1/2 rounded-full bg-indigo-600/20 blur-3xl" />

      <div className="w-full animate-fade-up">
        <div className="relative overflow-hidden rounded-3xl border border-white/10 bg-white/5 p-8 shadow-2xl backdrop-blur-xl">
          <div className="absolute inset-x-0 top-0 h-1.5 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500" />

          <div className="mb-8 text-center">
            <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-indigo-500 to-pink-600 text-2xl shadow-glow-indigo">
              🎉
            </div>
            <h1 className="text-2xl font-black text-white">创建账号</h1>
            <p className="mt-1 text-sm text-slate-400">加入 AnimeHub，开启追番之旅</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="mb-1.5 block text-sm font-medium text-slate-300">
                用户名
              </label>
              <input
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                placeholder="设置用户名"
                className="w-full rounded-xl border border-white/10 bg-slate-950/60 px-4 py-3 text-white placeholder-slate-500 transition focus:border-pink-500/60 focus:outline-none focus:ring-2 focus:ring-pink-500/40"
              />
            </div>
            <div>
              <label className="mb-1.5 block text-sm font-medium text-slate-300">
                邮箱
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="you@example.com"
                className="w-full rounded-xl border border-white/10 bg-slate-950/60 px-4 py-3 text-white placeholder-slate-500 transition focus:border-pink-500/60 focus:outline-none focus:ring-2 focus:ring-pink-500/40"
              />
            </div>
            <div>
              <label className="mb-1.5 block text-sm font-medium text-slate-300">
                密码
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                placeholder="至少 6 位"
                className="w-full rounded-xl border border-white/10 bg-slate-950/60 px-4 py-3 text-white placeholder-slate-500 transition focus:border-pink-500/60 focus:outline-none focus:ring-2 focus:ring-pink-500/40"
              />
            </div>
            <div>
              <label className="mb-1.5 block text-sm font-medium text-slate-300">
                确认密码
              </label>
              <input
                type="password"
                value={confirm}
                onChange={(e) => setConfirm(e.target.value)}
                required
                placeholder="再次输入密码"
                className="w-full rounded-xl border border-white/10 bg-slate-950/60 px-4 py-3 text-white placeholder-slate-500 transition focus:border-pink-500/60 focus:outline-none focus:ring-2 focus:ring-pink-500/40"
              />
            </div>

            {error && (
              <p className="rounded-lg bg-red-500/10 px-3 py-2 text-sm text-red-400">
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-xl bg-gradient-to-r from-indigo-600 to-pink-600 py-3 font-bold text-white shadow-glow-indigo transition hover:brightness-110 disabled:opacity-50"
            >
              {loading ? "注册中…" : "注 册"}
            </button>
          </form>

          <p className="mt-4 text-center text-xs text-slate-500">
            提示：系统第一个注册的用户自动成为管理员
          </p>
          <p className="mt-3 text-center text-sm text-slate-400">
            已有账号？
            <Link href="/login" className="ml-1 font-medium text-pink-400 hover:underline">
              去登录
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}