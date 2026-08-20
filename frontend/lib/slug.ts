// AnimeHub SEO 工具：URL slug 生成与解析
//
// 约定：
//  - `/anime/[slug]`：slug 为纯数字时视为向后兼容的 id，否则按 SEO slug 解析。
//  - slugify 与后端 scripts/normalize.py 的 make_slug 规则保持一致。

/**
 * 生成 URL 安全的 slug。
 * 优先使用英文/拼音（罗马字符）转小写并用 "-" 连接；
 * 无 ASCII 时降级为 Unicode（中文）slug。
 */
export function slugify(raw: string): string {
  const s = (raw || "").trim();
  if (!s) return "";
  const ascii = s
    .replace(/[：:，,、·・．。!！?？（）()]/g, " ")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .replace(/-{2,}/g, "-");
  if (ascii) return ascii;
  // 无 ASCII（纯中文等）时返回紧凑的 Unicode slug
  const unicode = s.replace(/\s+/g, "-").replace(/[^a-zA-Z0-9\u4e00-\u9fa5-]/g, "").replace(/-{2,}/g, "-");
  return unicode.replace(/^-+|-+$/g, "");
}

/** 判断 slug 是否为纯数字（此时视为向上兼容的 anime id） */
export function isNumericSlug(slug: string): boolean {
  return /^\d+$/.test((slug || "").trim());
}

/** 生成详情页规范 URL 路径：优先 slug，无则用 id */
export function animePath(a: { slug?: string; id: number }): string {
  const slug = (a?.slug || "").trim();
  return slug && !isNumericSlug(slug) ? `/anime/${slug}` : `/anime/${a.id}`;
}