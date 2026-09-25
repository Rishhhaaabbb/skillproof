# Task 1: Pydantic request/response schemas — validators added in later tasks
from __future__ import annotations

from datetime import datetime, date
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    github_username: Optional[str] = None
    full_name: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------


class UserBase(BaseModel):
    email: EmailStr
    github_username: Optional[str] = None
    full_name: Optional[str] = None
    is_public: bool = False
    profile_headline: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: int
    current_streak: int
    longest_streak: int
    last_streak_date: Optional[date] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    profile_headline: Optional[str] = None
    is_public: Optional[bool] = None
    github_username: Optional[str] = None


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------


class AnalysisOut(BaseModel):
    id: int
    user_id: int
    tpr_score: float
    lr_score: Optional[float] = None
    confidence_level: Optional[str] = None
    breakdown: Optional[Dict[str, Any]] = None
    features: Optional[Dict[str, Any]] = None
    # flags is stored as {"green_flags": [...], "red_flags": [...]}
    flags: Optional[Dict[str, List[str]]] = None
    heatmap_data: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TriggerAnalysisRequest(BaseModel):
    github_username: Optional[str] = None


# ---------------------------------------------------------------------------
# Target Roles
# ---------------------------------------------------------------------------


class TargetRoleCreate(BaseModel):
    role_title: str
    company_name: Optional[str] = None
    jd_text: str


class TargetRoleUpdate(BaseModel):
    role_title: Optional[str] = None
    company_name: Optional[str] = None
    jd_text: Optional[str] = None


class TargetRoleOut(BaseModel):
    id: int
    user_id: int
    role_title: str
    company_name: Optional[str] = None
    jd_text: str
    latest_readiness_score: Optional[float] = None
    latest_gap_analysis: Optional[Dict[str, Any]] = None
    created_at: datetime
    last_analyzed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ReadinessHistoryOut(BaseModel):
    id: int
    target_role_id: int
    readiness_score: float
    gap_summary: Optional[Dict[str, Any]] = None
    recorded_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Evaluation Verdict
# ---------------------------------------------------------------------------


class EvaluationVerdictOut(BaseModel):
    id: int
    user_id: int
    target_role_id: int
    skeptic_case: Optional[str] = None
    advocate_case: Optional[str] = None
    final_verdict: Optional[str] = None
    confidence: Optional[float] = None
    surviving_skeptic_points: Optional[List[str]] = None
    surviving_advocate_points: Optional[List[str]] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Verification Session
# ---------------------------------------------------------------------------


class VerificationSessionOut(BaseModel):
    id: int
    user_id: int
    target_role_id: Optional[int] = None
    scenario: Optional[Dict[str, Any]] = None
    candidate_answer: Optional[str] = None
    quality_score: Optional[float] = None
    reasoning: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SubmitAnswerRequest(BaseModel):
    candidate_answer: str


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------


class TaskOut(BaseModel):
    id: int
    user_id: int
    target_role_id: int
    missing_requirement: str
    target_repo: Optional[str] = None
    task_description: str
    verification_signal: Optional[Dict[str, Any]] = None
    status: str  # 'assigned' | 'verified_complete' | 'expired'
    created_at: datetime
    verified_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------------


class ChatMessageOut(BaseModel):
    id: int
    user_id: int
    target_role_id: Optional[int] = None
    role: str  # 'user' | 'assistant'
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    message: str
    target_role_id: Optional[int] = None


# ---------------------------------------------------------------------------
# Notification
# ---------------------------------------------------------------------------


class NotificationOut(BaseModel):
    id: int
    user_id: int
    target_role_id: Optional[int] = None
    message: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Share Token
# ---------------------------------------------------------------------------


class ShareTokenOut(BaseModel):
    id: int
    user_id: int
    token: str
    created_at: datetime
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Skill Tag
# ---------------------------------------------------------------------------


class SkillTagOut(BaseModel):
    id: int
    user_id: int
    tag: str
    confidence: Optional[float] = None
    source: Optional[str] = None
    last_updated: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Milestone
# ---------------------------------------------------------------------------


class MilestoneOut(BaseModel):
    id: int
    user_id: int
    milestone_key: str
    milestone_label: str
    earned_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Job Status
# ---------------------------------------------------------------------------


class JobStatusOut(BaseModel):
    id: str
    user_id: int
    job_type: str
    status: str  # 'queued' | 'processing' | 'complete' | 'failed'
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Comparison
# ---------------------------------------------------------------------------


class ComparisonResultOut(BaseModel):
    id: int
    user_id: int
    target_role_id: int
    before_analysis_id: Optional[int] = None
    after_analysis_id: Optional[int] = None
    before_readiness: Optional[float] = None
    after_readiness: Optional[float] = None
    newly_matched: Optional[List[str]] = None
    resolved_flags: Optional[List[str]] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Recruiter Request
# ---------------------------------------------------------------------------


class RecruiterRequestCreate(BaseModel):
    recruiter_name: str
    recruiter_email: str
    recruiter_company: Optional[str] = None
    message: Optional[str] = None


class RecruiterRequestOut(BaseModel):
    id: int
    share_token_id: int
    candidate_user_id: int
    recruiter_name: str
    recruiter_email: str
    recruiter_company: Optional[str] = None
    message: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
