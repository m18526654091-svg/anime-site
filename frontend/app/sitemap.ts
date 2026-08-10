import { MetadataRoute } from "next";
import { API_URL } from "@/lib/api";

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const base = (process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000").replace(/\/$/, "") + "/";
  const animeList: MetadataRoute.Sitemap = [{ url: base, changeFrequency: "always", priority: 1 }];

  try {
    const res = await fetch(`${API_URL}/api/anime?page_size=1000`, { next: { revalidate: 3600 } });
    if (res.ok) {
      const data = await res.json();
      const items = Array.isArray(data) ? data : data.items || [];
      for (const a of items) {
        const lastModStr = a.updated_at || a.created_at;
        animeList.push({
          url: `${base}anime/${a.id}`,
          ...(lastModStr ? { lastModified: new Date(lastModStr) } : {}),
          changeFrequency: "weekly",
          priority: 0.8,
        });
      }
    }
  } catch {
    // ignore sitemap fetch errors
  }

  try {
    const res = await fetch(`${API_URL}/api/anime/categories`, { next: { revalidate: 3600 } });
    if (res.ok) {
      const categories = await res.json();
      for (const c of categories) {
        animeList.push({
          url: `${base}categories/${encodeURIComponent(c.genre)}`,
          changeFrequency: "daily",
          priority: 0.6,
        });
      }
    }
  } catch {
    // ignore sitemap fetch errors
  }

  try {
    const res = await fetch(`${API_URL}/api/anime/years`, { next: { revalidate: 3600 } });
    if (res.ok) {
      const years = await res.json();
      for (const y of years) {
        animeList.push({
          url: `${base}years/${y.year}`,
          changeFrequency: "monthly",
          priority: 0.5,
        });
      }
    }
  } catch {
    // ignore sitemap fetch errors
  }

  try {
    const res = await fetch(`${API_URL}/api/anime/tags`, { next: { revalidate: 3600 } });
    if (res.ok) {
      const tags = await res.json();
      for (const t of tags) {
        animeList.push({
          url: `${base}tags/${encodeURIComponent(t.tag)}`,
          changeFrequency: "monthly",
          priority: 0.5,
        });
      }
    }
  } catch {
    // ignore sitemap fetch errors
  }

  return animeList;
}