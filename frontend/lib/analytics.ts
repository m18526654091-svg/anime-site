/**
 * Analytics 配置层（Phase 22）。
 * - 未设置 NEXT_PUBLIC_GA_ID 时：不加载任何 analytics script（GA disabled）。
 * - 设置后：由 GoogleAnalytics 组件以 afterInteractive 策略加载，不影响 SSR/SEO/CWV。
 */
export function getGoogleAnalyticsId(): string | undefined {
  const id = process.env.NEXT_PUBLIC_GA_ID?.trim();
  return id ? id : undefined;
}
