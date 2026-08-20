// Server wrapper: keeps Next.js metadata (including noindex) out of the
// client component tree. The actual UI is auth-gated and rendered by
// FavoritesClient.
import FavoritesClient from "@/components/FavoritesClient";

export const metadata = {
  title: "我的收藏 - AnimeHub",
  description: "查看您收藏的动漫列表。登录后即可在这里看到收藏的动画封面、标题、题材类型与评分。",
  robots: { index: false, follow: false },
};

export default function FavoritesPage() {
  return <FavoritesClient />;
}
