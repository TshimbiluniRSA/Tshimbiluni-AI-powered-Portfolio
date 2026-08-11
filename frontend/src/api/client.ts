// API Client for Tshimbiluni AI-powered Portfolio
import axios from 'axios';
import type { AxiosInstance } from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'https://tshimbiluni-ai-powered-portfolio.onrender.com';
const API_TIMEOUT = Number(import.meta.env.VITE_API_TIMEOUT) || 30000;

// Create axios instance with default config
const apiClient: AxiosInstance = axios.create({
  baseURL: API_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add any auth tokens here if needed
    // const token = localStorage.getItem('token');
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle errors globally
    if (error.response) {
      console.error('API Error:', error.response.data);
    } else if (error.request) {
      console.error('Network Error:', error.message);
    }
    return Promise.reject(error);
  }
);

// Types
export interface ChatMessage {
  id: number;
  session_id: string;
  message_type: 'user' | 'assistant' | 'system';
  content: string;
  created_at: string;
  updated_at: string;
  response_time_ms?: number;
  tokens_used?: number;
  model_used?: string;
  rating?: number;
  metadata?: Record<string, unknown>;
}

export interface ChatRequest {
  message: string;
  session_id?: string;
  model?: string;
  metadata?: Record<string, unknown>;
}

export interface GitHubStats {
  username: string; profile: { name?: string; avatar_url?: string; profile_url?: string; followers: number; following: number; public_repositories: number };
  repository_stats: { total_stars:number; total_forks:number; total_watchers:number; total_open_issues:number; total_repository_size_kb:number };
  contributions: { total:number; commits:number; pull_requests:number; issues:number; pull_request_reviews:number; period_start?:string; period_end?:string };
  top_languages: Array<{name:string; bytes:number; percentage:number}>; recent_repositories: Array<{name:string; url?:string; updated_at?:string; stars:number; forks:number}>; last_synced_at:string; stale?: boolean;
}

// API Methods
export const api = {
  // Chat endpoints
  chat: {
    sendMessage: async (data: ChatRequest): Promise<ChatMessage> => {
      const response = await apiClient.post('/chat/message', data);
      return response.data;
    },
  },
  
  // Cached portfolio-owner statistics (the browser never receives a GitHub token)
  github: {
    getStats: async (): Promise<GitHubStats> => (await apiClient.get('/github/stats')).data,
  },

  // CV endpoints
  cv: {
    download: async (): Promise<{download_url:string; expires_in:number; filename:string}> => {
      const response = await apiClient.get('/cv/download');
      return response.data;
    },
  },
  
  // Repository endpoints
  repositories: {
    getFeatured: async () => {
      const response = await apiClient.get('/api/repositories/featured');
      return response.data;
    },
  },
};

export default apiClient;
