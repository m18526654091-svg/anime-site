// AnimeHub 封面地址读取工具
//
// 兼容性说明：
//  - 后端 FastAPI 当前返回 `cover` 字段（见 backend/app/models.py 与 schemas.py）。
//  - 为向前兼容，前端统一优先读取 `cover_url`；若不存在则回退到 `cover`；
//  - 若两者都为空，返回空字符串，由调用方（组件）使用默认渐变占位图。

export interface CoverSource {
  cover_url?: string | null;
  cover?: string | null;
}

// 占位图服务特征（与后端 scripts/normalize.py 的 PLACEHOLDER_MARKERS 一致）。
// 这些 URL 不是真实海报：placehold.co 渲染中文时常因字体缺失显示 ??????。
const PLACEHOLDER_MARKERS = [
  "placehold.co",
  "placeholdit",
  "dummyimage",
  "via.placeholder",
  "placeholder.com",
];

/**
 * 判断是否为占位图服务 URL（非真实封面）。
 * 命中时调用方应使用站内 AnimeHub fallback，绝不直接加载占位图。
 */
export function isPlaceholderCover(cover?: string | null): boolean {
  const c = (cover || "").trim().toLowerCase();
  if (!c) return false;
  return PLACEHOLDER_MARKERS.some((m) => c.includes(m));
}

/**
 * 返回最合适的封面图片地址。
 * 优先级：cover_url > cover > ""（空串表示“无封面，用默认占位”）
 */
export function getCover(src: CoverSource | null | undefined): string {
  const url = src?.cover_url?.trim() || "";
  if (url) return url;
  return src?.cover?.trim() || "";
}