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
  evidence_type: string;
  evidence_text: string;
  weight: number;
  reference_years: number[];
  factor?: string;
  description?: string;
  supporting_data?: string;
}

export interface Prediction {
  id: string;
  section: string;
  topic_name: string;
  subtopic_name?: string | null;
  predicted_archetype: string;
  statistical_score: number;
  calibrated_confidence: number;
  explanation: string;
  uncertainty_and_limitations: string;
  historical_evidence: PredictionEvidence[];
  backtesting_baseline_comparison?: string | null;
  created_at: string;
  // Aliases for component backwards-compatibility
  topic?: string;
  subtopic?: string | null;
  predicted_count?: number;
  confidence?: number;
  difficulty_prediction?: 'easy' | 'medium' | 'hard';
  reasoning?: string;
  evidence?: PredictionEvidence[];
  generated_at?: string;
}

export interface PredictionListResponse {
  predictions: Prediction[];
  total: number;
  methodology_statement: string;
  last_updated: string;
}

// ─── Mock Exams ──────────────────────────────────────────────────────────────

export interface MockQuestionOption {
  label: string;
  text: string;
}

export interface MockQuestion {
  id: string;
  mock_exam_id?: string;
  question_number: number;
  question_text: string;
  question_type: string;
  options?: MockQuestionOption[] | null;
  correct_answer: string;
  solution_text: string;
  topic: string;
  subtopic?: string | null;
  difficulty: string;
  estimated_time_seconds: number;
  marks_positive: number;
  marks_negative: number;
  verification_status: string;
  verification_details?: Record<string, any> | null;
  // Legacy aliases
  answer_key?: AnswerKey;
  solution?: Solution | null;
  classification?: QuestionClassification;
  source_question_id?: string | null;
}

export interface MockExam {
  id: string;
  title: string;
  exam_type: 'full' | 'sectional' | 'topic';
  section: string | null;
  topic: string | null;
  duration_minutes: number;
  total_marks: number;
  total_questions?: number;
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
  title?: string;
  section?: string;
  topic?: string;
  question_count?: number;
  duration_minutes?: number;
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


// ─── Shared Corpus & Deduplication Types ─────────────────────────────────────

export interface SharedHistoricalPaper {
  id: string;
  year: number;
  slot: string | null;
  paper_title: string;
  file_fingerprint: string;
  total_questions: number;
  is_verified: boolean;
  source_provenance: string | null;
  created_at: string;
  updated_at: string;
}

export interface SharedQuestionOption {
  id: string;
  option_label: string;
  option_text: string;
  is_correct: boolean;
}

export interface SharedQuestionSource {
  id: string;
  year: number;
  slot: string | null;
  question_number: number | null;
  source_name: string | null;
  source_type: string;
  provenance_notes: string | null;
}

export interface SharedQuestion {
  id: string;
  canonical_hash: string;
  question_number: number;
  question_text: string;
  question_type: string;
  section: string;
  difficulty: string;
  marks_positive: number;
  marks_negative: number;
  has_image: boolean;
  has_table: boolean;
  has_passage: boolean;
  passage_text: string | null;
  dataset_text: string | null;
  primary_year: number;
  primary_slot: string | null;
  verification_status: string;
  verification_confidence: number;
  options: SharedQuestionOption[];
  correct_answer: string | null;
  solution_text: string | null;
  sources: SharedQuestionSource[];
  created_at: string;
}

export interface SharedQuestionFilters {
  section?: string;
  year?: number;
  slot?: string;
  difficulty?: string;
  question_type?: string;
  limit?: number;
  offset?: number;
}

export interface SharedCorpusStats {
  total_verified_papers: number;
  total_unique_verified_questions: number;
  total_duplicates_prevented: number;
  total_sources_linked: number;
  section_breakdown: Record<string, number>;
  year_breakdown: Record<string, number>;
  topic_breakdown: Array<Record<string, any>>;
  recent_approved_questions: SharedQuestion[];
}

export interface UserProcessingHistoryItem {
  id: string;
  paper_id: string;
  stage: string;
  status: string;
  details?: Record<string, any> | null;
  created_at: string;
}

export interface PaperContributionSummary {
  paper_id: string;
  year: number;
  slot: string | null;
  status: string;
  total_extracted: number;
  total_verified: number;
  total_duplicate: number;
  total_rejected: number;
  promoted_to_shared: number;
  shared_paper_id: string | null;
  sharing_status: string;
}
