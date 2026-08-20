"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";

const SORTS: { key: string; label: string }[] = [
  { key: "quality", label: "综合排序" },
  { key: "score", label: "按评分" },
  { key: "latest", label: "更新时间" },
  { key: "year", label: "按年份" },
];

/**
 * 移动端右下角悬浮筛选按钮：点击展开排序选项（专业简洁风格）。
 */
export default function SeasonSortFAB() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const current = searchParams.get("sort") || "quality";
  const [open, setOpen] = useState(false);

  function pick(key: string) {
    setOpen(false);
    const sp = new URLSearchParams(searchParams.toString());
    sp.set("sort", key);
    router.push(`?${sp.toString()}`, { scroll: false });
  }

  return (
    <>
      {/* 排序选项面板 */}
      {open && (
        <div
          className="fixed inset-0 z-40 bg-slate-950/40"
          onClick={() => setOpen(false)}
          aria-hidden
        />
      )}
      <div className="fixed bottom-5 right-5 z-50">
        {open && (
          <div className="mb-2 overflow-hidden rounded-2xl border border-white/10 bg-slate-900/95 shadow-2xl backdrop-blur">
            {SORTS.map((s) => (
              <button
                key={s.key}
                type="button"
                onClick={() => pick(s.key)}
                className={`block w-full px-5 py-2.5 text-left text-sm transition ${
                  s.key === current
                    ? "bg-pink-600/20 font-semibold text-pink-300"
                    : "text-slate-300 hover:bg-white/5 hover:text-white"
                }`}
              >
                {s.label}
              </button>
            ))}
          </div>
        )}
        <button
          type="button"
          onClick={() => setOpen((v) => !v)}
          aria-label="筛选排序"
          className="flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-pink-600 to-fuchsia-600 text-xl text-white shadow-glow transition hover:brightness-110"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M3 6h18M7 12h10M10 18h4" strokeLinecap="round" />
          </svg>
        </button>
      </div>
    </>
  );
}
