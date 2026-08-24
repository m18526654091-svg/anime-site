import type { Metadata } from "next";

const SITE_BASE = (process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000").replace(/\/$/, "");

export const metadata: Metadata = {
  title: "版权声明与侵权通知 - AnimeHub",
  description: "AnimeHub 版权声明：本站不储存视频，若发现侵权内容，请通过开源仓库提交侵权通知。",
  alternates: { canonical: `${SITE_BASE}/copyright` },
  robots: { index: true, follow: true },
};

export default function CopyrightPage() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-12">
      <h1 className="text-2xl font-black text-white">版权声明（Copyright / DMCA）</h1>
      <p className="mt-2 text-sm text-slate-400">AnimeHub 不储存视频文件</p>

      <section className="mt-8 space-y-6 text-sm leading-7 text-slate-300">
        <div>
          <h2 className="mb-2 text-base font-bold text-white">1. 内容说明</h2>
          <p>
            本站是动漫资料与播放索引站。视频内容由第三方公开资源提供，本站不存储、不传输任何视频
            文件，不制作任何作品的副本。动漫标题、简介、封面等展示信息可能来自公开资料，版权归
            各自权利人所有。
          </p>
        </div>

        <div>
          <h2 className="mb-2 text-base font-bold text-white">2. 侵权通知渠道</h2>
          <p>
            如你是版权权利人，认为本站索引或展示的内容侵犯了你的权利，请通过开源项目仓库提交
            Issue 描述具体情况（作品名称、涉嫌侵权的页面 URL、你的权利说明与联系方式）：
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
          <h2 className="mb-2 text-base font-bold text-white">3. 处理原则</h2>
          <p>
            收到有效通知后，我们会在合理时间内核实并移除相关索引/展示内容，并在可能的情况下
            通知相关第三方来源。本声明不构成任何法律实体或授权代理关系。
          </p>
        </div>
      </section>
    </div>
  );
}
