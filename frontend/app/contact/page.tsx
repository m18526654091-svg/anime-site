import type { Metadata } from "next";

const SITE_BASE = (process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000").replace(/\/$/, "");

export const metadata: Metadata = {
  title: "联系我们 - AnimeHub",
  description: "通过 AnimeHub 开源项目仓库提交 Issue 或联系维护者，反馈问题与建议。",
  alternates: { canonical: `${SITE_BASE}/contact` },
  robots: { index: true, follow: true },
};

export default function ContactPage() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-12">
      <h1 className="text-2xl font-black text-white">联系我们</h1>
      <p className="mt-2 text-sm text-slate-400">反馈问题、建议或安全事项</p>

      <section className="mt-8 space-y-6 text-sm leading-7 text-slate-300">
        <div>
          <h2 className="mb-2 text-base font-bold text-white">公开渠道</h2>
          <p>
            本站为开源项目 AnimeHub，源代码与问题跟踪托管在 GitHub。如需反馈问题（数据错误、
            链接失效、安全漏洞）或提出建议，请在项目仓库提交 Issue：
          </p>
          <p className="mt-2">
            <a
              href="https://github.com/m18526654091-svg/anime-site/issues"
              target="_blank"
              rel="noopener noreferrer"
              className="text-pink-400 underline-offset-4 hover:underline"
            >
              https://github.com/m18526654091-svg/anime-site/issues
            </a>
          </p>
        </div>

        <div>
          <h2 className="mb-2 text-base font-bold text-white">处理时效</h2>
          <p>我们会在合理时间内查看并处理 Issue 中反馈的问题。</p>
        </div>
      </section>
    </div>
  );
}
