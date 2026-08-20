import axios from "axios";
import type { Anime, AnimePage, AuthResponse, Comment, EpisodesResponse, RatingsInfo, User } from "@/types";
import { isNumericSlug } from "@/lib/slug";

export const TOKEN_KEY = "animehub_token";
export const USER_KEY = "animehub_user";

// Service-side (SSR/SSG) calls FastAPI directly via loopback.
const INTERNAL_API_URL = "http://127.0.0.1:8000";

// Browser-side calls should go through same-origin /api proxy
// to avoid CORS / loopback issues in production.
export const API_URL =
  typeof window === "undefined"
    ? process.env.NEXT_PUBLIC_API_URL || INTERNAL_API_URL
    : "";

// ---------- JWT / auth storage ----------

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function setAuth(data: AuthResponse): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(TOKEN_KEY, data.access_token);
  localStorage.setItem(USER_KEY, JSON.stringify(data.user));
}

export function clearAuth(): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

export function getStoredUser(): User | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem(USER_KEY);
    return raw ? (JSON.parse(raw) as User) : null;
  } catch {
    return null;
  }
}

// ---------- axios instance (auto attaches Bearer token) ----------

export const api = axios.create({
  baseURL: API_URL,
  timeout: 15000,
});

api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ---------- API calls (all hit the real backend) ----------

export async function fetchAnime(q?: string): Promise<Anime[]> {
  const { data } = await api.get<Anime[]>("/api/anime", {
    params: q ? { q } : {},
  });
  return data;
}

export async function fetchAnimePage(
  q?: string,
  page = 1,
  pageSize = 18
): Promise<AnimePage> {
  const { data } = await api.get<AnimePage>("/api/anime", {
    params: {
      q: q || undefined,
      page,
      page_size: pageSize,
    },
  });
  return data;
}

export async function fetchAnimeByFilter(
  filter: {
    category?: string;
    tag?: string;
    year?: number;
    region?: string;
    status?: string;
    letter?: string;
    studio?: string;
    season?: string;
    sort?: "latest" | "score" | "year" | "quality";
  },
  page = 1,
  pageSize = 24
): Promise<AnimePage> {
  const { data } = await api.get<AnimePage>("/api/anime", {
    params: {
      category: filter.category || undefined,
      tag: filter.tag || undefined,
      year: filter.year || undefined,
      region: filter.region || undefined,
      status: filter.status || undefined,
      letter: filter.letter || undefined,
      studio: filter.studio || undefined,
      season: filter.season || undefined,
      sort: filter.sort || "latest",
      page,
      page_size: pageSize,
    },
  });
  return data;
}

export async function fetchAnimeBySort(sort: "latest" | "score" | "year" | "quality" = "quality", pageSize = 12): Promise<AnimePage> {
  const { data } = await api.get<AnimePage>("/api/anime", {
    params: { sort, page: 1, page_size: pageSize },
  });
  return data;
}

export async function fetchCategories(): Promise<{ genre: string; count: number }[]> {
  const { data } = await api.get<{ genre: string; count: number }[]>("/api/anime/categories");
  return data;
}

export async function fetchRegions(): Promise<{ region: string; count: number }[]> {
  const { data } = await api.get<{ region: string; count: number }[]>("/api/anime/regions");
  return data;
}

export async function fetchStatuses(): Promise<{ status: string; count: number }[]> {
  const { data } = await api.get<{ status: string; count: number }[]>("/api/anime/statuses");
  return data;
}

export async function fetchLetters(): Promise<{ letter: string; count: number }[]> {
  const { data } = await api.get<{ letter: string; count: number }[]>("/api/anime/letters");
  return data;
}

export async function fetchTags(): Promise<{ tag: string; count: number }[]> {
  const { data } = await api.get<{ tag: string; count: number }[]>("/api/anime/tags");
  return data;
}

export async function fetchYears(): Promise<{ year: number; count: number }[]> {
  const { data } = await api.get<{ year: number; count: number }[]>("/api/anime/years");
  return data;
}

export async function fetchStudios(): Promise<{ studio: string; count: number }[]> {
  const { data } = await api.get<{ studio: string; count: number }[]>("/api/anime/studios");
  return data;
}

export async function fetchSeasons(): Promise<{ year: number; season: string }[]> {
  const { data } = await api.get<{ year: number; season: string }[]>("/api/anime/seasons");
  return data;
}

export async function fetchAnimeDetail(id: number): Promise<Anime> {
  const { data } = await api.get<Anime>(`/api/anime/${id}`);
  return data;
}

/** 按 SEO slug 读取详情；slug 为空时自动按 id 读取 */
export async function fetchAnimeBySlug(slug: string): Promise<Anime> {
  const s = (slug || "").trim();
  if (isNumericSlug(s)) {
    return fetchAnimeDetail(Number(s));
  }
  // 直接使用原始 slug 拼入 URL，由 axios 统一编码一次。
  // 不要预 encodeURIComponent：Next.js 打包后的 axios 会对已编码的
  // %E6%... 再次编码为 %25E6%...，导致后端 404（中文 slug 详情页全部失效）。
  const { data } = await api.get<Anime>(`/api/anime/by-slug/${s}`);
  return data;
}

export async function fetchRelated(animeId: number, limit = 8): Promise<Anime[]> {
  // 获取当前动漫上下文（genre/tags/studio/year/month）
  let current: { genre?: string; tags?: string; studio?: string; year?: number | null; month?: number | null } = {};
  try {
    const detail = await fetchAnimeDetail(animeId);
    current.genre = detail.genre;
    current.tags = detail.tags;
    current.studio = detail.studio;
    current.year = detail.year;
    current.month = detail.month;
  } catch {
    // fallback: no context
  }

  const seen = new Set<number>();
  const results: Anime[] = [];
  const add = (list: Anime[], max: number) => {
    for (const a of list) {
      if (a.id !== animeId && !seen.has(a.id)) {
        seen.add(a.id);
        results.push(a);
        if (results.length >= max) return;
      }
    }
  };

  // 1) 相同 genre
  if (current.genre) {
    try {
      const page = await fetchAnimeByFilter({ category: current.genre, sort: "score" }, 1, limit);
      add(page.items, limit);
    } catch {
      // ignore
    }
  }
  // 2) 相同 tags（取第一个标签）
  if (results.length < limit && current.tags) {
    const tag = current.tags.split("/")[0].trim();
    if (tag) {
      try {
        const page = await fetchAnimeByFilter({ tag, sort: "score" }, 1, limit);
        add(page.items, limit);
      } catch {
        // ignore
      }
    }
  }
  // 3) 相同 studio
  if (results.length < limit && current.studio) {
    try {
      const page = await fetchAnimeByFilter({ studio: current.studio, sort: "score" }, 1, limit);
      add(page.items, limit);
    } catch {
      // ignore
    }
  }
  // 4) 同季度（同年同季新番）
  if (results.length < limit && current.year && current.month) {
    const season = monthToSeason(current.month);
    if (season) {
      try {
        const page = await fetchAnimeByFilter({ year: current.year, season, sort: "score" }, 1, limit);
        add(page.items, limit);
      } catch {
        // ignore
      }
    }
  }
  // 5) 相近年份
  if (results.length < limit && current.year) {
    for (const y of [current.year, current.year - 1, current.year + 1]) {
      if (results.length >= limit) break;
      try {
        const page = await fetchAnimeByFilter({ year: y, sort: "score" }, 1, limit);
        add(page.items, limit);
      } catch {
        // ignore
      }
    }
  }

  return results.slice(0, limit);
}

/** 月份(1-12) → 季度（spring/summer/autumn/winter），未知返回 null */
function monthToSeason(month: number): string | null {
  if (month >= 3 && month <= 5) return "spring";
  if (month >= 6 && month <= 8) return "summer";
  if (month >= 9 && month <= 11) return "autumn";
  if (month === 12 || month === 1 || month === 2) return "winter";
  return null;
}

export async function createAnime(payload: Partial<Anime>): Promise<Anime> {
  const { data } = await api.post<Anime>("/api/anime", payload);
  return data;
}

export async function deleteAnime(id: number): Promise<void> {
  await api.delete(`/api/anime/${id}`);
}

export async function fetchComments(animeId: number): Promise<Comment[]> {
  const { data } = await api.get<Comment[]>(`/api/anime/${animeId}/comments`);
  return data;
}

export async function fetchEpisodes(animeId: number): Promise<EpisodesResponse> {
  const { data } = await api.get<EpisodesResponse>(`/api/anime/${animeId}/episodes`);
  return data;
}

export async function postComment(
  animeId: number,
  content: string
): Promise<Comment> {
  const { data } = await api.post<Comment>(`/api/anime/${animeId}/comments`, {
    content,
  });
  return data;
}

export async function fetchFavorites(): Promise<Anime[]> {
  const { data } = await api.get<Anime[]>("/api/favorites");
  return data;
}

export async function addFavorite(animeId: number): Promise<void> {
  await api.post(`/api/favorites/${animeId}`);
}

export async function removeFavorite(animeId: number): Promise<void> {
  await api.delete(`/api/favorites/${animeId}`);
}

export async function fetchRatings(animeId: number): Promise<RatingsInfo> {
  const { data } = await api.get<RatingsInfo>(`/api/anime/${animeId}/ratings`);
  return data;
}

export async function rateAnime(animeId: number, score: number): Promise<void> {
  await api.post(`/api/anime/${animeId}/ratings`, { score });
}

export async function loginRequest(
  username: string,
  password: string
): Promise<AuthResponse> {
  const { data } = await api.post<AuthResponse>("/api/login", {
    username,
    password,
  });
  return data;
}

export async function registerRequest(payload: {
  username: string;
  email: string;
  password: string;
}): Promise<AuthResponse> {
  const { data } = await api.post<AuthResponse>("/api/register", payload);
  return data;
}

export function apiErrorMessage(err: unknown): string {
  if (axios.isAxiosError(err)) {
    const detail = (err.response?.data as { detail?: string } | undefined)?.detail;
    if (detail) return detail;
    if (!err.response) return "无法连接服务器，请确认后端已启动";
    return `请求失败 (${err.response.status})`;
  }
  return "发生未知错误";
}