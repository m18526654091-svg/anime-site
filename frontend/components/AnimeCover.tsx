"use client";

import { useState } from "react";
import { getCover, isPlaceholderCover } from "@/lib/cover";

interface AnimeCoverProps {
  anime: {
    title?: string;
    chinese_title?: string;
    cover?: string | null;
    cover_url?: string | null;
  };
  /** 传入 img 的 className；占位块会自动叠加 flex 居中。 */
  className?: string;
  priority?: boolean;
}

/** 校验封面 URL 是否为可加载的 http(s) 地址，避免无效 URL 触发浏览器 broken-image（问号）。 */
function isValidCoverUrl(url: string): boolean {
  return /^https?:\/\/[^"\s]+$/i.test(url.trim());
}

/**
 * 统一动漫封面组件。
 * - 优先读取 cover_url / cover；
 * - 仅当 URL 合法且**不是占位图服务**时才渲染 <img>：
 *   placehold.co 等占位图 URL 虽合法，但渲染中文时会因字体缺失显示 ??????，
 *   一律视为“无真实封面”，走站内 fallback；
 * - 图片加载失败（防盗链/404/超时）由 onError 回退到站内 fallback；
 * - fallback：深色紫粉渐变 + 品牌光晕 + 中央「A」+ 底部简洁标题（CSS 字体，正常显示）。
 */
export default function AnimeCover({
  anime,
  className = "aspect-[2/3] w-full object-cover",
  priority = false,
}: AnimeCoverProps) {
  const cover = getCover(anime);
  const [failed, setFailed] = useState(false);
  const alt = anime.chinese_title || anime.title || "";
  const title = anime.chinese_title || anime.title || "";
  const canRenderImg = isValidCoverUrl(cover) && !failed && !isPlaceholderCover(cover);

  if (canRenderImg) {
    return (
      // eslint-disable-next-line @next/next/no-img-element
      <img
        src={cover}
        alt={alt}
        loading={priority ? "eager" : "lazy"}
        onError={() => setFailed(true)}
        className={className}
      />
    );
  }

  // 专业占位：深色紫粉渐变 + 光晕 + 中央品牌「A」+ 底部简洁标题
  return (
    <div
      className={`${className} relative overflow-hidden bg-gradient-to-br from-slate-900 via-indigo-950 to-purple-950`}
    >
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_28%_18%,rgba(236,72,153,0.30),transparent_55%)]" />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_75%_82%,rgba(99,102,241,0.25),transparent_55%)]" />
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-pink-500 to-indigo-600 text-lg font-black text-white shadow-lg shadow-pink-500/30">
          A
        </span>
      </div>
      {title && (
        <div className="absolute inset-x-0 bottom-1.5 flex justify-center px-1.5">
          <span className="max-w-full truncate text-[10px] font-medium leading-none text-white/70">
            {title}
          </span>
        </div>
      )}
    </div>
  );
}


