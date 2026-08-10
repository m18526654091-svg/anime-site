import axios from "axios";
import type { Anime, AnimePage, AuthResponse, Comment, User } from "@/types";

export const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const TOKEN_KEY = "animehub_token";
export const USER_KEY = "animehub_user";

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
    sort?: "latest" | "score" | "year";
  },
  page = 1,
  pageSize = 24
): Promise<AnimePage> {
  const { data } = await api.get<AnimePage>("/api/anime", {
    params: {
      category: filter.category || undefined,
      tag: filter.tag || undefined,
      year: filter.year || undefined,
      sort: filter.sort || "latest",
      page,
      page_size: pageSize,
    },
  });
  return data;
}

export async function fetchAnimeBySort(sort: "latest" | "score" | "year" = "latest", pageSize = 12): Promise<AnimePage> {
  const { data } = await api.get<AnimePage>("/api/anime", {
    params: { sort, page: 1, page_size: pageSize },
  });
  return data;
}

export async function fetchCategories(): Promise<{ genre: string; count: number }[]> {
  const { data } = await api.get<{ genre: string; count: number }[]>("/api/anime/categories");
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

export async function fetchAnimeDetail(id: number): Promise<Anime> {
  const { data } = await api.get<Anime>(`/api/anime/${id}`);
  return data;
}

export async function fetchRelated(animeId: number, limit = 6): Promise<Anime[]> {
  // Try to get current anime info for context
  let current: { genre?: string; year?: number | null } = {};
  try {
    const detail = await fetchAnimeDetail(animeId);
    current.genre = detail.genre;
    current.year = detail.year;
  } catch {
    // fallback: no context
  }

  // 1) Same genre first
  const seen = new Set<number>();
  const results: Anime[] = [];
  if (current.genre) {
    try {
      const page = await fetchAnimeByFilter({ category: current.genre, sort: "score" }, 1, limit);
      for (const a of page.items) {
        if (a.id !== animeId && !seen.has(a.id)) {
          seen.add(a.id);
          results.push(a);
        }
      }
    } catch {
      // ignore
    }
  }

  // 2) Same year fallback
  if (results.length < limit && current.year) {
    try {
      const page = await fetchAnimeByFilter({ year: current.year, sort: "score" }, 1, limit);
      for (const a of page.items) {
        if (a.id !== animeId && !seen.has(a.id)) {
          seen.add(a.id);
          results.push(a);
        }
      }
    } catch {
      // ignore
    }
  }

  return results.slice(0, limit);
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