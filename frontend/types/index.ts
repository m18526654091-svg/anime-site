export interface Anime {
  id: number;
  title: string;
  cover: string;
  description: string;
  genre: string;
  tags?: string;
  year?: number | null;
  region?: string;
  author?: string;
  studio?: string;
  status?: string;
  episodes?: number | null;
  score: number;
  seo_title?: string;
  seo_description?: string;
  play_data?: string;
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