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
  metadata?: Record<string, any>;
}

export interface ChatRequest {
  message: string;
  session_id?: string;
  model?: string;
  metadata?: Record<string, any>;
}

export interface ChatSession {
  session_id: string;
  messages: ChatMessage[];
  message_count: number;
  created_at: string;
  last_activity: string;
}

export interface GitHubProfile {
  username: string;
  bio?: string;
  public_repos?: number;
  followers?: number;
  following?: number;
  profile_url?: string;
  avatar_url?: string;
  name?: string;
  company?: string;
  location?: string;
  blog?: string;
  twitter_username?: string;
  hireable?: boolean;
  created_at: string;
  updated_at: string;
  last_fetched_at?: string;
  is_data_stale: boolean;
}

export interface LinkedInProfile {
  profile_url: string;
  full_name?: string;
  headline?: string;
  location?: string;
  about?: string;
  profile_image_url?: string;
  connections_count?: number;
  created_at: string;
  updated_at: string;
}

// API Methods
export const api = {
  // Chat endpoints
  chat: {
    sendMessage: async (data: ChatRequest): Promise<ChatMessage> => {
      const response = await apiClient.post('/chat/message', data);
      return response.data;
    },
    
    getSession: async (sessionId: string, limit: number = 50): Promise<ChatSession> => {
      const response = await apiClient.get(`/chat/sessions/${sessionId}`, {
        params: { limit },
      });
      return response.data;
    },
    
    listSessions: async (page: number = 1, size: number = 20) => {
      const response = await apiClient.get('/chat/sessions', {
        params: { page, size },
      });
      return response.data;
    },
    
    deleteSession: async (sessionId: string) => {
      const response = await apiClient.delete(`/chat/sessions/${sessionId}`);
      return response.data;
    },
    
    rateMessage: async (sessionId: string, messageId: number, rating: number) => {
      const response = await apiClient.post(`/chat/sessions/${sessionId}/rate`, {
        message_id: messageId,
        rating,
      });
      return response.data;
    },
  },
  
  // GitHub endpoints
  github: {
    sync: async (username: string) => {
      const response = await apiClient.post('/github/sync', { username });
      return response.data;
    },
    
    getProfile: async (username: string): Promise<GitHubProfile> => {
      const response = await apiClient.get(`/github/profiles/${username}`);
      return response.data;
    },
    
    listProfiles: async (page: number = 1, size: number = 20) => {
      const response = await apiClient.get('/github/profiles', {
        params: { page, size },
      });
      return response.data;
    },
  },
  
  // LinkedIn endpoints
  linkedin: {
    sync: async (profileUrl: string) => {
      const response = await apiClient.post('/linkedin/sync', {
        profile_url: profileUrl,
      });
      return response.data;
    },
    
    getProfile: async (profileUrl: string): Promise<LinkedInProfile> => {
      const encodedUrl = encodeURIComponent(profileUrl);
      const response = await apiClient.get(`/linkedin/profiles/${encodedUrl}`);
      return response.data;
    },
  },
  
  // Health check
  health: async () => {
    const response = await apiClient.get('/chat/health');
    return response.data;
  },
  
  // CV endpoints
  cv: {
    getInfo: async () => {
      const response = await apiClient.get('/api/cv/info');
      return response.data;
    },
    download: async () => {
      try {
        const downloadUrl = `${API_URL}/api/cv/download`;
        const result = window.open(downloadUrl, '_blank');
        if (!result) {
          // Fallback if popup blocker prevented the window from opening
          window.location.href = downloadUrl;
        }
      } catch (error) {
        console.error('Failed to download CV:', error);
        throw error;
      }
    },
  },
  
  // Repository endpoints
  repositories: {
    getFeatured: async () => {
      const response = await apiClient.get('/api/repositories/featured');
      return response.data;
    },
    getByUsername: async (username: string, page: number = 1, size: number = 20) => {
      const response = await apiClient.get(`/api/repositories/${username}`, {
        params: { page, size },
      });
      return response.data;
    },
    sync: async (username: string, forceRefresh: boolean = false) => {
      const response = await apiClient.post(`/api/repositories/sync/${username}`, null, {
        params: { force_refresh: forceRefresh },
      });
      return response.data;
    },
  },
};

export default apiClient;
