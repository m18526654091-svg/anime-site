import Script from "next/script";
import { getGoogleAnalyticsId } from "@/lib/analytics";

/**
 * GA4 就绪层：仅在 NEXT_PUBLIC_GA_ID 存在时注入 gtag script。
 * strategy="afterInteractive" → 页面交互后加载，不阻塞首屏（不影响 SSR/SEO/CWV）。
 * anonymize_ip 保护隐私，降低合规风险。
 */
export default function GoogleAnalytics() {
  const gaId = getGoogleAnalyticsId();
  if (!gaId) return null;
  return (
    <>
      <Script
        src={`https://www.googletagmanager.com/gtag/js?id=${gaId}`}
        strategy="afterInteractive"
      />
      <Script
        id="ga4-init"
        strategy="afterInteractive"
        dangerouslySetInnerHTML={{
          __html: `window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','${gaId}',{anonymize_ip:true});`,
        }}
      />
    </>
  );
}
