/**
 * AdPlaceholder.jsx
 * 广告位占位组件：100% 宽、90px 高、浅灰背景、居中显示「广告位」。
 *
 * 未来接入真实广告（如 Google AdSense）时，替换本组件内部内容即可，
 * 无需改动放置位置。保持轻量：无 JS、无请求、无状态，
 * 不影响移动端加载速度与 SEO。
 */
export default function AdPlaceholder() {
  return (
    <div
      className="flex w-full items-center justify-center rounded-lg bg-slate-100 text-sm text-slate-400"
      style={{ height: "90px" }}
    >
      广告位
    </div>
  );
}