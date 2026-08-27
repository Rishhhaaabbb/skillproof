// Task 1: TypeScript interfaces for all SkillProof domain types

// ---------------------------------------------------------------------------
// Auth
// ---------------------------------------------------------------------------

export interface LoginRequest {
  email: string;
  password: string;
}

export interface SignupRequest {
  email: string;
  password: string;
  github_username?: string;
  full_name?: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

// ---------------------------------------------------------------------------
// User
// ---------------------------------------------------------------------------

export interface User {
  id: number;
  email: string;
  github_username?: string;
  full_name?: string;
  is_public: boolean;
  profile_headline?: string;
  current_streak: number;
  longest_streak: number;
  last_streak_date?: string; // ISO date string
  created_at: string;
}

// ---------------------------------------------------------------------------
// Analysis
// ---------------------------------------------------------------------------

export interface Analysis {
  id: number;
  user_id: number;
  tpr_score: number;
  lr_score?: number;
  confidence_level?: string;
  breakdown?: Record<string, unknown>;
  features?: Record<string, number>;
  flags?: string[];
  heatmap_data?: Record<string, number>;
  created_at: string;
}

// ---------------------------------------------------------------------------
// Target Role
// ---------------------------------------------------------------------------

export interface TargetRole {
  id: number;
  user_id: number;
  role_title: string;
  company_name?: string;
  jd_text: string;
  latest_readiness_score?: number;
  latest_gap_analysis?: Record<string, unknown>;
  created_at: string;
  last_analyzed_at?: string;
}

export interface ReadinessHistory {
  id: number;
  target_role_id: number;
  readiness_score: number;
  gap_summary?: Record<string, unknown>;
  recorded_at: string;
}

// ---------------------------------------------------------------------------
// Evaluation Verdict
// ---------------------------------------------------------------------------

export interface EvaluationVerdict {
  id: number;
  user_id: number;
  target_role_id: number;
  skeptic_case?: string;
  advocate_case?: string;
  final_verdict?: string;
  confidence?: number;
  surviving_skeptic_points?: string[];
  surviving_advocate_points?: string[];
  created_at: string;
}

// ---------------------------------------------------------------------------
// Verification Session
// ---------------------------------------------------------------------------

export interface VerificationSession {
  id: number;
  user_id: number;
  target_role_id?: number;
  scenario?: Record<string, unknown>;
  candidate_answer?: string;
  quality_score?: number;
  reasoning?: string;
  created_at: string;
}

// ---------------------------------------------------------------------------
// Task
// ---------------------------------------------------------------------------

export interface Task {
  id: number;
  user_id: number;
  target_role_id: number;
  missing_requirement: string;
  target_repo?: string;
  task_description: string;
  verification_signal?: Record<string, unknown>;
  status: 'assigned' | 'verified_complete' | 'expired';
  created_at: string;
  verified_at?: string;
}

// ---------------------------------------------------------------------------
// Chat
// ---------------------------------------------------------------------------

export interface ChatMessage {
  id: number;
  user_id: number;
  target_role_id?: number;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

// ---------------------------------------------------------------------------
// Notification
// ---------------------------------------------------------------------------

export interface Notification {
  id: number;
  user_id: number;
  target_role_id?: number;
  message: string;
  is_read: boolean;
  created_at: string;
}

// ---------------------------------------------------------------------------
// Share Token
// ---------------------------------------------------------------------------

export interface ShareToken {
  id: number;
  user_id: number;
  token: string;
  created_at: string;
  expires_at?: string;
}

// ---------------------------------------------------------------------------
// Skill Tag
// ---------------------------------------------------------------------------

export interface SkillTag {
  id: number;
  user_id: number;
  tag: string;
  confidence?: number;
  source?: string;
  last_updated: string;
}

// ---------------------------------------------------------------------------
// Milestone
// ---------------------------------------------------------------------------

export interface Milestone {
  id: number;
  user_id: number;
  milestone_key: string;
  milestone_label: string;
  earned_at: string;
}

// ---------------------------------------------------------------------------
// Job Status
// ---------------------------------------------------------------------------

export interface JobStatus {
  id: string;
  user_id: number;
  job_type: string;
  status: 'queued' | 'processing' | 'complete' | 'failed';
  result?: unknown;
  error?: string;
  created_at: string;
  completed_at?: string;
}

// ---------------------------------------------------------------------------
// Comparison Result
// ---------------------------------------------------------------------------

export interface ComparisonResult {
  id: number;
  user_id: number;
  target_role_id: number;
  before_analysis_id?: number;
  after_analysis_id?: number;
  before_readiness?: number;
  after_readiness?: number;
  newly_matched?: string[];
  resolved_flags?: string[];
  created_at: string;
}

// ---------------------------------------------------------------------------
// Recruiter Request
// ---------------------------------------------------------------------------

export interface RecruiterRequest {
  id: number;
  share_token_id: number;
  candidate_user_id: number;
  recruiter_name: string;
  recruiter_email: string;
  recruiter_company?: string;
  message?: string;
  status: string;
  created_at: string;
}

// ---------------------------------------------------------------------------
// API response wrappers
// ---------------------------------------------------------------------------

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export interface ApiError {
  detail: string;
  status_code?: number;
}
