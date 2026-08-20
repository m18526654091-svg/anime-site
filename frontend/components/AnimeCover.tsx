"use client";

import { useState } from "react";
import { getCover } from "@/lib/cover";

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

/**
 * 统一动漫封面组件。
 * - 优先读取 cover_url / cover；
 * - 图片加载失败（外链防盗链、404、超时）时自动回退到站内 CSS 渐变占位，
 *   避免浏览器显示「图片问号」，保证界面始终专业统一；
 * - 无封面时直接渲染渐变占位。
 */
export default function AnimeCover({
  anime,
  className = "aspect-[2/3] w-full object-cover",
  priority = false,
}: AnimeCoverProps) {
  const cover = getCover(anime);
  const [failed, setFailed] = useState(false);
  const alt = anime.chinese_title || anime.title || "";

  if (cover && !failed) {
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

  return (
    <div
      className={`${className} flex items-center justify-center bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-600`}
    >
      <span className="text-4xl font-black text-white/85">
        {anime.title?.slice(0, 1) || "漫"}
      </span>
    </div>
  );
}
