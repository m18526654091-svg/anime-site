export interface Anime {
  id: number;
  title: string;
  chinese_title?: string;
  slug?: string;
  cover: string;
  /** 兼容字段：部分数据源把封面放在 cover_url，前端优先读取它（无则回退 cover） */
  cover_url?: string;
  description: string;
  genre: string;
  tags?: string;
  year?: number | null;
  month?: number | null;
  region?: string;
  author?: string;
  studio?: string;
  status?: string;
  episodes?: number | null;
  score: number;
  seo_title?: string;
  seo_description?: string;
  quality_score?: number;
  is_indexable?: number;
  anime_seo_priority?: number;
  play_data?: string;
  updated_at?: string;
}

export interface AnimePage {
  items: Anime[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface User {
  id: number;
  username: string;
  email: string;
  is_admin: number;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Comment {
  id: number;
  anime_id: number;
  user_id: number;
  username: string;
  content: string;
}

export interface Episode {
  id: number;
  anime_id: number;
  episode_number: number;
  title: string;
  video_url: string;
  created_at: string;
}

export interface EpisodesResponse {
  items: Episode[];
  total: number;
}

export interface RatingsInfo {
  avg_score: number;
  rating_count: number;
  my_score: number | null;
}