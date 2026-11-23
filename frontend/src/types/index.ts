// ─── Auth ────────────────────────────────────────────────────────────────────

export interface User {
  id: string;
  email: string;
  full_name: string;
  created_at: string;
  updated_at: string;
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

// ─── API Keys ────────────────────────────────────────────────────────────────

export interface ApiKeyStatus {
  provider: string;
  is_set: boolean;
  is_saved: boolean;
  masked_key: string | null;
}

// ─── Papers ──────────────────────────────────────────────────────────────────

export type PaperSource = 'official' | 'coaching' | 'community' | 'unknown';

export type ExtractionStatus =
  | 'pending'
  | 'processing'
  | 'completed'
  | 'failed';

export interface Paper {
  id: string;
  title: string;
  year: number;
  slot: string | null;
  section: string | null;
  source: PaperSource;
  file_path: string;
  extraction_status: ExtractionStatus;
  question_count: number;
  uploaded_by: string;
  created_at: string;
  updated_at: string;
}

// ─── Questions ───────────────────────────────────────────────────────────────

export interface QuestionOption {
  label: string;
  text: string;
  is_correct: boolean;
}

export interface AnswerKey {
  correct_option: string | null;
  correct_value: number | null;
  marks_positive: number;
  marks_negative: number;
}

export interface Solution {
  method: string;
  steps: string[];
  latex: string | null;
}

export interface QuestionClassification {
  section: string;
  topic: string;
  subtopic: string | null;
  difficulty: 'easy' | 'medium' | 'hard';
  cognitive_level: string;
}

export interface Question {
  id: string;
  paper_id: string;
  question_number: number;
  question_text: string;
  question_type: 'mcq' | 'tita';
  options: QuestionOption[];
  answer_key: AnswerKey;
  solution: Solution | null;
  classification: QuestionClassification;
  is_verified: boolean;
  verification_records: VerificationRecord[];
  created_at: string;
  updated_at: string;
}

export interface VerificationRecord {
  id: string;
  verified_by: string;
  verified_at: string;
  status: 'correct' | 'incorrect' | 'flagged';
  notes: string | null;
}

// ─── Topics ──────────────────────────────────────────────────────────────────

export interface Topic {
  id: string;
  name: string;
  section: string;
  parent_id: string | null;
  question_count: number;
}

// ─── Analysis ────────────────────────────────────────────────────────────────

export interface TopicFrequency {
  topic: string;
  subtopic: string | null;
  total_count: number;
  percentage: number;
  year_distribution: Record<string, number>;
  recency_weighted_score: number;
  avg_difficulty: string;
}

export interface DifficultyDistribution {
  easy_count: number;
  medium_count: number;
  hard_count: number;
  easy_pct: number;
  medium_pct: number;
  hard_pct: number;
}

export interface QuestionTypeDistribution {
  mcq_count: number;
  tita_count: number;
  mcq_pct: number;
  tita_pct: number;
}

export interface AnalysisResult {
  section: string;
  total_verified_questions: number;
  years_covered: number[];
  top_topics: TopicFrequency[];
  difficulty_distribution: DifficultyDistribution;
  question_type_distribution: QuestionTypeDistribution;
  recurring_archetypes: string[];
  methodology: string;
}

export interface RunAnalysisRequest {
  section?: string;
  recency_decay_factor?: number;
}

// ─── Predictions ─────────────────────────────────────────────────────────────

export interface PredictionEvidence {
  factor: string;
  description: string;
  weight: number;
  supporting_data: string;
}

export interface Prediction {
  id: string;
  section: string;
  topic: string;
  subtopic: string | null;
  predicted_count: number;
  confidence: number;
  difficulty_prediction: 'easy' | 'medium' | 'hard';
  reasoning: string;
  evidence: PredictionEvidence[];
  generated_at: string;
}

// ─── Mock Exams ──────────────────────────────────────────────────────────────

export interface MockQuestion {
  id: string;
  question_text: string;
  question_type: 'mcq' | 'tita';
  options: QuestionOption[];
  answer_key: AnswerKey;
  solution: Solution | null;
  classification: QuestionClassification;
  source_question_id: string | null;
}

export interface MockExam {
  id: string;
  title: string;
  exam_type: 'full' | 'sectional' | 'topic';
  section: string | null;
  topic: string | null;
  duration_minutes: number;
  total_marks: number;
  questions: MockQuestion[];
  created_by: string;
  created_at: string;
}

export interface ExamAttempt {
  id: string;
  exam_id: string;
  user_id: string;
  answers: Record<string, string | number | null>;
  started_at: string;
  submitted_at: string | null;
  time_taken_seconds: number | null;
}

export interface AttemptResult {
  attempt_id: string;
  exam_id: string;
  total_score: number;
  max_score: number;
  percentage: number;
  correct_count: number;
  incorrect_count: number;
  unattempted_count: number;
  section_scores: Record<string, { score: number; max: number }>;
  topic_scores: Record<string, { score: number; max: number }>;
  time_taken_seconds: number;
  percentile_estimate: number | null;
  question_results: QuestionResult[];
}

export interface QuestionResult {
  question_id: string;
  user_answer: string | number | null;
  correct_answer: string | number | null;
  is_correct: boolean;
  marks_obtained: number;
}

// ─── API Request / Response helpers ──────────────────────────────────────────

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
}

export interface SetApiKeyRequest {
  provider: string;
  api_key: string;
  save: boolean;
}

export interface GenerateMockRequest {
  exam_type: 'full' | 'sectional' | 'topic';
  section?: string;
  topic?: string;
  question_count?: number;
  difficulty_mix?: Record<string, number>;
}

export interface SubmitAttemptRequest {
  answers: Record<string, string | number | null>;
  time_taken_seconds: number;
}

export interface GeneratePredictionsRequest {
  section: string;
  target_year: number;
}

export interface QuestionFilters {
  section?: string;
  topic?: string;
  difficulty?: string;
  paper_id?: string;
  is_verified?: boolean;
  page?: number;
  page_size?: number;
}
