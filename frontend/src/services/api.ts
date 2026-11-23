import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios';
import type {
  User,
  LoginRequest,
  RegisterRequest,
  SetApiKeyRequest,
  ApiKeyStatus,
  Paper,
  PaginatedResponse,
  Question,
  QuestionFilters,
  AnalysisResult,
  RunAnalysisRequest,
  Prediction,
  GeneratePredictionsRequest,
  MockExam,
  GenerateMockRequest,
  ExamAttempt,
  SubmitAttemptRequest,
  AttemptResult,
} from '../types';

// ─── Axios Instance ──────────────────────────────────────────────────────────

const api = axios.create({
  baseURL: '/api',
  withCredentials: true,
  headers: { 'Content-Type': 'application/json' },
});

// Helper to read cookie value
function getCookie(name: string): string | null {
  const match = document.cookie.match(new RegExp('(^|;\\s*)(' + name + ')=([^;]*)'));
  return match ? decodeURIComponent(match[3]) : null;
}

// Request interceptor — attach CSRF / auth token if stored
api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = localStorage.getItem('access_token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  const csrf = getCookie('csrf_token');
  if (csrf && config.headers) {
    config.headers['X-CSRF-Token'] = csrf;
  }
  return config;
});

// Response interceptor — handle 401 globally
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ detail?: string }>) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      if (
        window.location.pathname !== '/login' &&
        window.location.pathname !== '/register'
      ) {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  },
);

// ─── Auth API ────────────────────────────────────────────────────────────────

export const authApi = {
  register: async (data: RegisterRequest): Promise<User> => {
    const res = await api.post<{ access_token: string; user: User }>('/auth/register', data);
    if (res.data.access_token) {
      localStorage.setItem('access_token', res.data.access_token);
    }
    return res.data.user;
  },

  login: async (data: LoginRequest): Promise<{ access_token: string; user: User }> => {
    const res = await api.post<{ access_token: string; user: User }>(
      '/auth/login',
      data,
    );
    if (res.data.access_token) {
      localStorage.setItem('access_token', res.data.access_token);
    }
    return res.data;
  },

  logout: async (): Promise<void> => {
    await api.post('/auth/logout');
    localStorage.removeItem('access_token');
  },

  getMe: async (): Promise<User> => {
    const res = await api.get<User>('/auth/me');
    return res.data;
  },
};

// ─── API Keys API ────────────────────────────────────────────────────────────

export const apiKeysApi = {
  setSessionKey: async (
    data: Omit<SetApiKeyRequest, 'save'>,
  ): Promise<{ status: string }> => {
    const res = await api.post<{ status: string }>('/keys/session', data);
    return res.data;
  },

  saveKey: async (data: SetApiKeyRequest): Promise<{ status: string }> => {
    const res = await api.post<{ status: string }>('/keys/save', data);
    return res.data;
  },

  deleteKey: async (_provider?: string): Promise<void> => {
    await api.delete('/keys');
  },

  getKeyStatus: async (): Promise<ApiKeyStatus[]> => {
    const res = await api.get<ApiKeyStatus | ApiKeyStatus[]>('/keys/status');
    return Array.isArray(res.data) ? res.data : [res.data];
  },
};

// ─── Papers API ──────────────────────────────────────────────────────────────

export const papersApi = {
  upload: async (
    file: File,
    metadata: { title: string; year: number; slot?: string; section?: string; source?: string },
  ): Promise<Paper> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('year', String(metadata.year));
    if (metadata.slot) formData.append('slot', metadata.slot);
    formData.append('source_name', metadata.title || 'Official CAT Paper');
    if (metadata.source) formData.append('source_type', metadata.source);

    const res = await api.post<Paper>('/papers/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },

  list: async (
    params?: { page?: number; page_size?: number; year?: number; section?: string },
  ): Promise<PaginatedResponse<Paper>> => {
    const res = await api.get<PaginatedResponse<Paper>>('/papers', { params });
    return res.data;
  },

  get: async (id: string): Promise<Paper> => {
    const res = await api.get<Paper>(`/papers/${id}`);
    return res.data;
  },

  extract: async (id: string): Promise<{ status: string; task_id: string }> => {
    const res = await api.post<{ status: string; task_id: string }>(
      `/papers/${id}/extract`,
    );
    return res.data;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/papers/${id}`);
  },
};

// ─── Questions API ───────────────────────────────────────────────────────────

export const questionsApi = {
  list: async (
    filters?: QuestionFilters,
  ): Promise<PaginatedResponse<Question>> => {
    const res = await api.get<PaginatedResponse<Question>>('/questions', {
      params: filters,
    });
    return res.data;
  },

  get: async (id: string): Promise<Question> => {
    const res = await api.get<Question>(`/questions/${id}`);
    return res.data;
  },

  verify: async (
    id: string,
    data: { status: 'correct' | 'incorrect' | 'flagged'; notes?: string },
  ): Promise<Question> => {
    const res = await api.post<Question>(`/questions/${id}/verify`, data);
    return res.data;
  },

  getStats: async (): Promise<{
    total: number;
    verified: number;
    unverified: number;
    by_section: Record<string, number>;
    by_difficulty: Record<string, number>;
  }> => {
    const res = await api.get('/questions/stats');
    return res.data;
  },
};

// ─── Analysis API ────────────────────────────────────────────────────────────

export const analysisApi = {
  getBySection: async (section: string, decay_factor?: number): Promise<AnalysisResult | null> => {
    try {
      const res = await api.get<AnalysisResult>(`/analysis/${section}`, {
        params: decay_factor !== undefined ? { decay_factor } : undefined,
      });
      return res.data;
    } catch (err) {
      const axiosErr = err as AxiosError;
      if (axiosErr.response?.status === 404) return null;
      throw err;
    }
  },

  run: async (data: RunAnalysisRequest): Promise<AnalysisResult> => {
    const res = await api.post<AnalysisResult>('/analysis/run', data);
    return res.data;
  },

  getSummary: async (): Promise<{
    sections_analyzed: string[];
    total_questions_analyzed: number;
    last_analysis_at: string | null;
  }> => {
    const res = await api.get('/analysis/summary');
    return res.data;
  },
};

// ─── Predictions API ─────────────────────────────────────────────────────────

export const predictionsApi = {
  list: async (params?: {
    section?: string;
    topic?: string;
    min_confidence?: number;
  }): Promise<Prediction[]> => {
    const res = await api.get<{ predictions: Prediction[] }>('/predictions', { params });
    return res.data.predictions || [];
  },

  generate: async (data: GeneratePredictionsRequest): Promise<Prediction[]> => {
    const res = await api.post<{ predictions: Prediction[] }>('/predictions/generate', data);
    return res.data.predictions || [];
  },

  getEvidence: async (id: string): Promise<Prediction> => {
    const res = await api.get<Prediction>(`/predictions/${id}/evidence`);
    return res.data;
  },
};

// ─── Mock Exams API ──────────────────────────────────────────────────────────

export const mockExamsApi = {
  generate: async (data: GenerateMockRequest): Promise<MockExam> => {
    const res = await api.post<MockExam>('/mocks/generate', data);
    return res.data;
  },

  list: async (_params?: {
    page?: number;
    page_size?: number;
    exam_type?: string;
  }): Promise<PaginatedResponse<MockExam>> => {
    const res = await api.get<MockExam[]>('/mocks');
    return {
      items: res.data || [],
      total: res.data?.length || 0,
      page: 1,
      page_size: 50,
      total_pages: 1,
    };
  },

  get: async (id: string): Promise<MockExam> => {
    const res = await api.get<MockExam>(`/mocks/${id}`);
    return res.data;
  },

  startAttempt: async (examId: string): Promise<ExamAttempt> => {
    return {
      id: `attempt_${examId}`,
      exam_id: examId,
      user_id: 'current_user',
      answers: {},
      started_at: new Date().toISOString(),
      submitted_at: null,
      time_taken_seconds: null,
    };
  },

  submitAttempt: async (
    examId: string,
    _attemptId: string,
    data: SubmitAttemptRequest,
  ): Promise<AttemptResult> => {
    const res = await api.post<AttemptResult>(
      `/mocks/${examId}/attempt`,
      {
        responses: data.answers,
        time_spent_seconds: data.time_taken_seconds,
      },
    );
    return res.data;
  },

  getResults: async (
    examId: string,
    _attemptId: string,
  ): Promise<AttemptResult> => {
    const res = await api.get<AttemptResult>(
      `/mocks/${examId}/attempt`,
    );
    return res.data;
  },
};

export default api;
