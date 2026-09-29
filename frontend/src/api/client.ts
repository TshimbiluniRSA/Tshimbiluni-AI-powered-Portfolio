// API client for the portfolio backend.
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'https://api.tshimbiluniportfolio.tech';
const API_TIMEOUT = Number(import.meta.env.VITE_API_TIMEOUT) || 30000;

const apiClient = axios.create({
  baseURL: API_URL,
  timeout: API_TIMEOUT,
  headers: { 'Content-Type': 'application/json' },
});

export interface ChatMessage {
  id: number;
  session_id: string;
  message_type: 'user' | 'assistant' | 'system';
  content: string;
  created_at: string;
  updated_at: string;
  response_time_ms?: number;
  model_used?: string;
}

export interface ChatRequest {
  message: string;
  session_id?: string;
}

/** Keep in sync with ChatRequest.message max_length in backend/src/schemas.py. */
export const CHAT_MESSAGE_MAX_LENGTH = 1000;

/** Returns the API's user-facing error message, if it sent one. */
export function apiErrorMessage(error: unknown): string | undefined {
  if (axios.isAxiosError(error)) {
    const detail = (error.response?.data as { detail?: unknown } | undefined)?.detail;
    if (typeof detail === 'string') return detail;
  }
  return undefined;
}

export interface GitHubStats {
  username: string;
  contributions: { total: number };
  top_languages: Array<{ name: string; bytes: number; percentage: number }>;
  last_synced_at: string;
  stale?: boolean;
}

export const api = {
  chat: {
    sendMessage: async (data: ChatRequest): Promise<ChatMessage> =>
      (await apiClient.post('/chat/message', data)).data,
  },
  // Cached statistics for the portfolio owner; the browser never sees a GitHub token.
  github: {
    getStats: async (): Promise<GitHubStats> => (await apiClient.get('/github/stats')).data,
  },
  cv: {
    download: async (): Promise<{ download_url: string; expires_in: number; filename: string }> =>
      (await apiClient.get('/cv/download')).data,
  },
};
