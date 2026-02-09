import axios from 'axios';
import type { AxiosInstance } from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient: AxiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
}

export interface ChatSession {
  session_id: string;
  created_at: string;
  last_message?: string;
}

export interface ChatRequest {
  message: string;
  session_id?: string;
}

export interface ChatResponse {
  response: string;
  session_id: string;
}

export interface GitHubProfile {
  login: string;
  name: string;
  bio: string;
  avatar_url: string;
  html_url: string;
  public_repos: number;
  followers: number;
  following: number;
  location?: string;
  company?: string;
  blog?: string;
  twitter_username?: string;
}

export interface LinkedInProfile {
  name: string;
  headline: string;
  summary?: string;
  profile_url?: string;
}

export const chatAPI = {
  sendMessage: async (data: ChatRequest): Promise<ChatResponse> => {
    const response = await apiClient.post('/chat', data);
    return response.data;
  },

  getSessions: async (): Promise<ChatSession[]> => {
    const response = await apiClient.get('/chat/sessions');
    return response.data;
  },

  deleteSession: async (sessionId: string): Promise<void> => {
    await apiClient.delete(`/chat/sessions/${sessionId}`);
  },
};

export const githubAPI = {
  syncProfile: async (username: string): Promise<GitHubProfile> => {
    const response = await apiClient.post('/github/sync', { username });
    return response.data;
  },

  getProfile: async (username: string): Promise<GitHubProfile> => {
    const response = await apiClient.get(`/github/profile/${username}`);
    return response.data;
  },
};

export const linkedinAPI = {
  getProfile: async (): Promise<LinkedInProfile> => {
    const response = await apiClient.get('/linkedin/profile');
    return response.data;
  },
};

export default apiClient;
