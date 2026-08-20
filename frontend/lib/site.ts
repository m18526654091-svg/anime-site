// AnimeHub 站点基础信息
//
// 轻量工具模块：提供 SSR/CSR 均可用的站点基础 URL，用于 JSON-LD 与
// canonical 网址生成。未来国际化时，这里可以扩展为 per-locale 的 base URL。

const ENV_SITE_URL =
  process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000";

/** 返回站点基础 URL（无尾部斜杠）。浏览器端优先用当前 origin 保持一致。 */
export function getSiteBase(): string {
  if (typeof window !== "undefined") {
    return window.location.origin;
  }
  return String(ENV_SITE_URL).replace(/\/+$/, "");
}

/** 站点名称 */
export function getSiteName(): string {
  return "AnimeHub";
}

/** 站点默认描述 */
export function getSiteDescription(): string {
  return (
    "AnimeHub 是免费的在线动漫资料站，提供热门动漫、最新更新、分类浏览与详细动漫资料。" +
    "不储存视频，聚合优质动漫信息，支持手机与电脑访问。"
  );
}

/** 去除尾部斜杠的安全拼接 */
export function joinUrl(base: string, path: string): string {
  return `${String(base).replace(/\/+$/, "")}${path.startsWith("/") ? path : `/${path}`}`;
}
