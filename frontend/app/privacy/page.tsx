import type { Metadata } from "next";

const SITE_BASE = (process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000").replace(/\/$/, "");

export const metadata: Metadata = {
  title: "隐私政策 - AnimeHub",
  description: "AnimeHub 隐私政策：说明本站当前的数据处理方式、Cookie 使用、第三方服务，以及未来接入广告后的数据处理说明。",
  alternates: { canonical: `${SITE_BASE}/privacy` },
  robots: { index: true, follow: true },
};

export default function PrivacyPage() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-12">
      <h1 className="text-2xl font-black text-white">隐私政策</h1>
      <p className="mt-2 text-sm text-slate-400">更新日期：以部署版本为准（开源项目 AnimeHub）</p>

      <section className="mt-8 space-y-6 text-sm leading-7 text-slate-300">
        <div>
          <h2 className="mb-2 text-base font-bold text-white">1. 我们处理的数据</h2>
          <p>
            本站是一个动漫资料与播放索引站（开源项目）。目前我们仅处理以下数据：
            账户登录信息（用户名、邮箱、密码哈希，仅在你主动注册时收集）；收藏、评分、
            评论等由你主动提交的内容；以及浏览器在访问网页时产生的常规日志（IP、UA、时间戳，
            用于基础安全与故障排查）。
          </p>
        </div>

        <div>
          <h2 className="mb-2 text-base font-bold text-white">2. Cookie 与本地存储</h2>
          <p>
            我们使用 Cookie / 本地存储保存登录令牌（JWT）和少量前端状态（如收藏标记）。
            这些仅用于让你保持登录与记住偏好，不用于跨站跟踪。本站目前不部署任何第三方分析脚本。
          </p>
        </div>

        <div>
          <h2 className="mb-2 text-base font-bold text-white">3. 第三方服务</h2>
          <p>
            视频内容来自第三方公开资源，本站不储存视频文件。若未来接入第三方广告（如 Google
            AdSense）或其他外部服务，我们会在上线前更新本政策，并说明涉及的第三方及其数据处理。
          </p>
        </div>

        <div>
          <h2 className="mb-2 text-base font-bold text-white">4. 你的权利</h2>
          <p>
            你可以随时删除账户或通过联系我们页面提出的方式，要求删除与你的账户相关的个人数据。
          </p>
        </div>
      </section>
    </div>
  );
}
