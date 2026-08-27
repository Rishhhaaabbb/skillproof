# Task 1: SQLAlchemy ORM models and database initialisation
import uuid
from datetime import datetime, date

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
    create_engine,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

from config import settings

Base = declarative_base()

# ---------------------------------------------------------------------------
# Engine / Session factory
# ---------------------------------------------------------------------------

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    # SQLite-only kwarg guard — safe to keep for Postgres
    connect_args={} if not settings.DATABASE_URL.startswith("sqlite") else {"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Yield a database session and close it when done."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables that do not yet exist. Safe to call on every startup."""
    Base.metadata.create_all(bind=engine)


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    github_username = Column(String(100), nullable=True)
    full_name = Column(String(255), nullable=True)
    is_public = Column(Boolean, default=False, nullable=False)
    profile_headline = Column(String(500), nullable=True)
    current_streak = Column(Integer, default=0, nullable=False)
    longest_streak = Column(Integer, default=0, nullable=False)
    last_streak_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    analyses = relationship("Analysis", back_populates="user", cascade="all, delete-orphan")
    target_roles = relationship("TargetRole", back_populates="user", cascade="all, delete-orphan")
    evaluation_verdicts = relationship("EvaluationVerdict", back_populates="user", cascade="all, delete-orphan")
    verification_sessions = relationship("VerificationSession", back_populates="user", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    share_tokens = relationship("ShareToken", back_populates="user", cascade="all, delete-orphan")
    skill_tags = relationship("SkillTag", back_populates="user", cascade="all, delete-orphan")
    milestones = relationship("Milestone", back_populates="user", cascade="all, delete-orphan")
    recruiter_requests = relationship("RecruiterRequest", back_populates="candidate_user", cascade="all, delete-orphan")
    analysis_comparisons = relationship("AnalysisComparison", back_populates="user", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="user", cascade="all, delete-orphan")


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tpr_score = Column(Float, nullable=False)
    lr_score = Column(Float, nullable=True)
    confidence_level = Column(String(20), nullable=True)
    breakdown = Column(JSON, nullable=True)
    features = Column(JSON, nullable=True)
    flags = Column(JSON, nullable=True)
    heatmap_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="analyses")


class TargetRole(Base):
    __tablename__ = "target_roles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role_title = Column(String(255), nullable=False)
    company_name = Column(String(255), nullable=True)
    jd_text = Column(Text, nullable=False)
    latest_readiness_score = Column(Float, nullable=True)
    latest_gap_analysis = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_analyzed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="target_roles")
    readiness_history = relationship("ReadinessHistory", back_populates="target_role", cascade="all, delete-orphan")
    evaluation_verdicts = relationship("EvaluationVerdict", back_populates="target_role", cascade="all, delete-orphan")
    verification_sessions = relationship("VerificationSession", back_populates="target_role", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="target_role", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="target_role", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="target_role", cascade="all, delete-orphan")
    analysis_comparisons = relationship("AnalysisComparison", back_populates="target_role", cascade="all, delete-orphan")


class ReadinessHistory(Base):
    __tablename__ = "readiness_history"

    id = Column(Integer, primary_key=True, index=True)
    target_role_id = Column(Integer, ForeignKey("target_roles.id"), nullable=False)
    readiness_score = Column(Float, nullable=False)
    gap_summary = Column(JSON, nullable=True)
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    target_role = relationship("TargetRole", back_populates="readiness_history")


class EvaluationVerdict(Base):
    __tablename__ = "evaluation_verdicts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    target_role_id = Column(Integer, ForeignKey("target_roles.id"), nullable=False)
    skeptic_case = Column(Text, nullable=True)
    advocate_case = Column(Text, nullable=True)
    final_verdict = Column(Text, nullable=True)
    confidence = Column(Float, nullable=True)
    surviving_skeptic_points = Column(JSON, nullable=True)
    surviving_advocate_points = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="evaluation_verdicts")
    target_role = relationship("TargetRole", back_populates="evaluation_verdicts")


class VerificationSession(Base):
    __tablename__ = "verification_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    target_role_id = Column(Integer, ForeignKey("target_roles.id"), nullable=True)
    scenario = Column(JSON, nullable=True)
    candidate_answer = Column(Text, nullable=True)
    quality_score = Column(Float, nullable=True)
    reasoning = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="verification_sessions")
    target_role = relationship("TargetRole", back_populates="verification_sessions")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    target_role_id = Column(Integer, ForeignKey("target_roles.id"), nullable=False)
    missing_requirement = Column(Text, nullable=False)
    target_repo = Column(String(255), nullable=True)
    task_description = Column(Text, nullable=False)
    verification_signal = Column(JSON, nullable=True)
    status = Column(String(20), default="assigned", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    verified_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="tasks")
    target_role = relationship("TargetRole", back_populates="tasks")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    target_role_id = Column(Integer, ForeignKey("target_roles.id"), nullable=True)
    role = Column(String(20), nullable=False)  # 'user' | 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="chat_messages")
    target_role = relationship("TargetRole", back_populates="chat_messages")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    target_role_id = Column(Integer, ForeignKey("target_roles.id"), nullable=True)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="notifications")
    target_role = relationship("TargetRole", back_populates="notifications")


class ShareToken(Base):
    __tablename__ = "share_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String(64), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="share_tokens")
    recruiter_requests = relationship("RecruiterRequest", back_populates="share_token", cascade="all, delete-orphan")


class SkillTag(Base):
    __tablename__ = "skill_tags"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tag = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=True)
    source = Column(String(50), nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="skill_tags")


class Milestone(Base):
    __tablename__ = "milestones"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    milestone_key = Column(String(100), nullable=False)
    milestone_label = Column(String(255), nullable=False)
    earned_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (UniqueConstraint("user_id", "milestone_key", name="uq_user_milestone"),)

    # Relationships
    user = relationship("User", back_populates="milestones")


class RecruiterRequest(Base):
    __tablename__ = "recruiter_requests"

    id = Column(Integer, primary_key=True, index=True)
    share_token_id = Column(Integer, ForeignKey("share_tokens.id"), nullable=False)
    candidate_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recruiter_name = Column(String(255), nullable=False)
    recruiter_email = Column(String(255), nullable=False)
    recruiter_company = Column(String(255), nullable=True)
    message = Column(Text, nullable=True)
    status = Column(String(20), default="pending", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    share_token = relationship("ShareToken", back_populates="recruiter_requests")
    candidate_user = relationship("User", back_populates="recruiter_requests")


class AnalysisComparison(Base):
    __tablename__ = "analysis_comparisons"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    target_role_id = Column(Integer, ForeignKey("target_roles.id"), nullable=False)
    before_analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=True)
    after_analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=True)
    before_readiness = Column(Float, nullable=True)
    after_readiness = Column(Float, nullable=True)
    newly_matched = Column(JSON, nullable=True)
    resolved_flags = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="analysis_comparisons")
    target_role = relationship("TargetRole", back_populates="analysis_comparisons")


class Job(Base):
    __tablename__ = "jobs"

    # String UUID primary key — generate with str(uuid.uuid4()) before insert
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_type = Column(String(50), nullable=False)
    status = Column(String(20), default="queued", nullable=False)
    result = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="jobs")


# ---------------------------------------------------------------------------
# Indexes
# ---------------------------------------------------------------------------

Index("idx_analyses_user", Analysis.user_id)
Index("idx_target_roles_user", TargetRole.user_id)
Index("idx_tasks_user", Task.user_id)
Index("idx_share_token", ShareToken.token)
Index("idx_jobs_user", Job.user_id)
