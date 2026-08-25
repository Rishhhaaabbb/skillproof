# SkillProof — Final Phase 2 Blueprint

**Official title:** "SkillProof Beyond Keywords: Explainable AI for Developer Behaviour Verification"
**Budget:** ₹0 — every service below runs on a free tier.

---

## Part 1 — How to Use This Document

Paste this entire document into your AI coding assistant (Cursor, Windsurf, etc.) as your very first message, before writing any code. It gives the assistant full context on what's being built, why, and how everything fits together. After that, you'll work through the build day by day — you'll bring specific, smaller prompts for each day's work (generated separately), and the assistant will build against the context it already has from this document.

Every step in **Part 4** is tagged:

- **[AI]** — the coding assistant does this, from this document plus a prompt
- **[YOU]** — a human on your team has to do this; no AI tool can do it for you (accounts, secrets, clicking "deploy," manual testing, talking to your guide)
- **[BOTH]** — the AI writes something, but a human configures or runs it

---

## Part 2 — What We're Building

**SkillProof analyzes a candidate's real GitHub activity — commits, pull requests, code reviews — and produces a verified, explainable readiness assessment**, instead of relying on resumes or one-shot AI scoring. A candidate can check their readiness against a specific job description, get cross-examined by an adversarial evaluation process (not a single LLM opinion), be assigned a specific verifiable task to close any gap, and get automatic confirmation once that gap is actually closed — not just advice, evidence.

### The Three Core Objectives

**Objective 1 — Verify.** To design and implement an adaptive, multi-agent verification engine that evaluates a candidate's real-world engineering capability through behavioral GitHub analysis, targeted follow-up probing, and adversarial cross-examination — producing a calibrated readiness signal significantly harder to game than static resume or single-pass AI scoring.

**Objective 2 — Close the Loop.** To convert every identified skill gap into a specific, verifiable improvement task and automatically confirm real-world completion through continuous, scheduled re-analysis — closing the loop between diagnosis and demonstrated improvement, rather than leaving candidates with generic, unconfirmed advice.

**Objective 3 — Explain & Extend Trust.** To ensure every verdict is fully explainable and traceable to specific evidence — commits, pull requests, and reviews — and to make that verified assessment shareable in a form both candidates and recruiters can act on with confidence.

---

## Part 3 — System Architecture

```
┌───────────────────────────────────────────────────────────────────┐
│                FRONTEND — Next.js (mobile-first, PWA)               │
│  Dashboard · Target Roles · Verification Sessions · Chat · Share    │
└─────────────────────────────┬─────────────────────────────────────┘
                               │ REST / JSON, JWT auth
┌─────────────────────────────▼─────────────────────────────────────┐
│                        BACKEND — FastAPI                            │
│                                                                     │
│  OBJECTIVE 1 — VERIFY                                               │
│  ┌───────────┐ ┌────────────┐ ┌───────────────┐ ┌────────────────┐│
│  │  GitHub    │ │  Feature    │ │  TPR Scorer    │ │  Interview      ││
│  │  Fetcher   │ │  Extractor  │ │  (base signal) │ │  Agent (probes) ││
│  └───────────┘ └────────────┘ └───────────────┘ └────────────────┘│
│  ┌────────────────────────────────────────────────────────────────┐│
│  │  Adversarial Evaluator — Skeptic / Advocate / Judge               ││
│  └────────────────────────────────────────────────────────────────┘│
│                                                                     │
│  OBJECTIVE 2 — CLOSE THE LOOP                                       │
│  ┌───────────┐ ┌────────────┐ ┌──────────────────────────────────┐│
│  │  JD        │ │  Task       │ │  Scheduler (GitHub Actions cron)  ││
│  │  Analyzer  │ │  Service    │ │  → re-analyzes + checks tasks     ││
│  └───────────┘ └────────────┘ └──────────────────────────────────┘│
│                                                                     │
│  OBJECTIVE 3 — EXPLAIN & TRUST                                      │
│  ┌───────────┐ ┌────────────┐ ┌──────────────────────────────────┐│
│  │  LLM       │ │  Chat       │ │  Share (public read-only view)    ││
│  │  Generator │ │  Service    │ │                                    ││
│  │ (cites     │ │             │ │                                    ││
│  │  evidence) │ │             │ │                                    ││
│  └───────────┘ └────────────┘ └──────────────────────────────────┘│
└─────┬───────────────────────┬─────────────────────┬───────────────┘
      │                       │                     │
┌─────▼──────┐       ┌────────▼────────┐    ┌───────▼──────────┐
│ GitHub API │       │  PostgreSQL      │    │   Gemini API       │
│            │       │  (Supabase)      │    │   (free tier)      │
└────────────┘       └──────────────────┘    └─────────────────────┘
```

---

## Part 4 — The Master Build Sequence: Step 0 to Final Step

Work through these in order. Each phase references the detailed section it draws from.

### Phase 0 — Setup (before any code)
| Step | Who | What |
|---|---|---|
| 0.1 | **[YOU]** | Create a shared GitHub repo for the team (e.g. `skillproof`) |
| 0.2 | **[YOU]** | Confirm each teammate has GitHub Student Developer Pack access |
| 0.3 | **[YOU]** | Create a Google AI Studio account, generate a Gemini API key, confirm `gemini-3.5-flash` (or the current free-tier default — check first) is accessible |
| 0.4 | **[YOU]** | Create a Supabase account + project, save the PostgreSQL connection string |
| 0.5 | **[YOU]** | Create Vercel and Render accounts, link both to the GitHub repo |
| 0.6 | **[YOU]** | Agree on the team role split (Part 12) |
| 0.7 | **[YOU]** | Paste this entire document into your AI coding assistant as the first message |

### Phase 1 — Backend skeleton
| Step | Who | What |
|---|---|---|
| 1.1 | **[AI]** | Generate the FastAPI project folder structure (Part 7) |
| 1.2 | **[AI]** | Generate `config.py` and `requirements.txt` |
| 1.3 | **[YOU]** | Create a local `.env` file with your real keys — never commit this file |
| 1.4 | **[YOU]** | Install dependencies, run the server locally, confirm it boots |

### Phase 2 — Database
| Step | Who | What |
|---|---|---|
| 2.1 | **[AI]** | Generate `models/database.py` and `models/schemas.py` from Part 6 |
| 2.2 | **[YOU]** | Run `init_db()` against your Supabase database |
| 2.3 | **[YOU]** | Open the Supabase dashboard and confirm every table exists |

### Phase 3 — Objective 1 core (base engine)
| Step | Who | What |
|---|---|---|
| 3.1 | **[AI]** | Generate `github_fetcher.py`, `feature_extractor.py`, `tpr_scorer.py` |
| 3.2 | **[YOU]** | Manually test against 2–3 real GitHub usernames you know well — does the output make sense to you? |
| 3.3 | **[AI]** | Generate auth (`security.py`, `auth/dependencies.py`, `auth/router.py`) |
| 3.4 | **[YOU]** | Manually test signup/login using the FastAPI auto-docs page (`/docs`) |

### Phase 4 — Objective 1: verification agents
| Step | Who | What |
|---|---|---|
| 4.1 | **[AI]** | Generate `interview_agent.py` (adaptive scenario generation) |
| 4.2 | **[AI]** | Generate `adversarial_evaluator.py` (Skeptic / Advocate / Judge) |
| 4.3 | **[YOU]** | Manually read 5–10 generated verdicts. Do they make sense? Are they citing real evidence, or inventing things? Flag bad outputs and refine the prompts with your AI tool |

### Phase 5 — Objective 2: close the loop
| Step | Who | What |
|---|---|---|
| 5.1 | **[AI]** | Generate `jd_analyzer.py` |
| 5.2 | **[AI]** | Generate `task_service.py` |
| 5.3 | **[AI]** | Generate/extend `scheduler.py` and the GitHub Actions workflow file |
| 5.4 | **[YOU]** | Add the `SCHEDULER_SECRET` as a GitHub Actions repo secret, manually trigger the workflow once, confirm it runs successfully |

### Phase 6 — Objective 3: explainability & sharing
| Step | Who | What |
|---|---|---|
| 6.1 | **[AI]** | Generate `llm_generator.py`, with every claim required to cite a specific commit/PR |
| 6.2 | **[AI]** | Generate `chat_service.py` |
| 6.3 | **[AI]** | Generate the share-token endpoints |
| 6.4 | **[YOU]** | Manually spot-check 5 generated reports — does every claim actually cite something real, or is it inventing citations? This matters a lot |

### Phase 7 — Frontend
| Step | Who | What |
|---|---|---|
| 7.1 | **[AI]** | Scaffold the Next.js app, pages per Part 10 |
| 7.2 | **[AI]** | Build each page and component |
| 7.3 | **[YOU]** | Manually test the entire flow on an actual phone browser — this is a mobile-first product |

### Phase 8 — Dataset & validation
| Step | Who | What |
|---|---|---|
| 8.1 | **[YOU]** | Collect ~100–150 GitHub usernames across 3 tiers (Part 11) — this is manual outreach and browsing, not something AI can do for you |
| 8.2 | **[AI]** | Write the evaluation script (Part 11) |
| 8.3 | **[YOU]** | Run it, review the results, discuss with your guide |
| 8.4 | **[AI], stretch goal** | Fit the lightweight learned model if time allows |

### Phase 9 — Deployment
| Step | Who | What |
|---|---|---|
| 9.1 | **[YOU]** | Deploy backend to Render, frontend to Vercel |
| 9.2 | **[YOU]** | Set every environment variable in both dashboards |
| 9.3 | **[BOTH]** | Test the live, deployed app end to end |

### Phase 10 — Polish & demo prep
| Step | Who | What |
|---|---|---|
| 10.1 | **[BOTH]** | Edge-case pass — private profiles, empty accounts, rate limits |
| 10.2 | **[YOU]** | Rehearse the demo script (Part 14) as a team |
| 10.3 | **[YOU]** | Prepare answers for likely viva questions — architecture choices, why no vector DB yet, dataset methodology |

---

## Part 5 — Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js (App Router) + TypeScript, Tailwind + shadcn/ui |
| Backend | FastAPI (Python 3.11+) |
| Auth | Custom JWT (passlib + python-jose) |
| Database | PostgreSQL via Supabase free tier |
| GitHub integration | PyGithub |
| LLM | Google Gemini API — verify the current free-tier model name before you start; Gemini model names retire quickly |
| Scheduling | GitHub Actions cron → protected backend endpoint |
| Deployment | Vercel (frontend) + Render (backend) |
| Data | pandas |

---

## Part 6 — Database Schema

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    github_username VARCHAR(255),
    full_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE analyses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    tpr_score FLOAT NOT NULL,
    confidence_level VARCHAR(20),
    breakdown JSONB NOT NULL,
    features JSONB NOT NULL,
    flags JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE target_roles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    role_title VARCHAR(255) NOT NULL,
    company_name VARCHAR(255),
    jd_text TEXT NOT NULL,
    latest_readiness_score FLOAT,
    latest_gap_analysis JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    last_analyzed_at TIMESTAMP
);

CREATE TABLE readiness_history (
    id SERIAL PRIMARY KEY,
    target_role_id INTEGER REFERENCES target_roles(id) ON DELETE CASCADE,
    readiness_score FLOAT NOT NULL,
    gap_summary JSONB,
    recorded_at TIMESTAMP DEFAULT NOW()
);

-- Objective 1: adversarial evaluation verdicts
CREATE TABLE evaluation_verdicts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    target_role_id INTEGER REFERENCES target_roles(id) ON DELETE CASCADE,
    skeptic_case TEXT,
    advocate_case TEXT,
    final_verdict TEXT,
    confidence FLOAT,
    surviving_skeptic_points JSONB,
    surviving_advocate_points JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Objective 1: adaptive verification sessions
CREATE TABLE verification_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    target_role_id INTEGER REFERENCES target_roles(id) ON DELETE SET NULL,
    scenario JSONB NOT NULL,
    candidate_answer TEXT,
    quality_score FLOAT,
    reasoning TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Objective 2: verifiable tasks
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    target_role_id INTEGER REFERENCES target_roles(id) ON DELETE CASCADE,
    missing_requirement TEXT NOT NULL,
    target_repo VARCHAR(255),
    task_description TEXT NOT NULL,
    verification_signal TEXT,
    status VARCHAR(20) DEFAULT 'assigned' CHECK (status IN ('assigned', 'verified_complete', 'expired')),
    created_at TIMESTAMP DEFAULT NOW(),
    verified_at TIMESTAMP
);

CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    target_role_id INTEGER REFERENCES target_roles(id) ON DELETE SET NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    target_role_id INTEGER REFERENCES target_roles(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE share_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(64) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP
);

CREATE INDEX idx_analyses_user ON analyses(user_id);
CREATE INDEX idx_target_roles_user ON target_roles(user_id);
CREATE INDEX idx_tasks_user ON tasks(user_id);
CREATE INDEX idx_share_token ON share_tokens(token);
```

---

## Part 7 — Backend Folder Structure

```
skillproof-backend/
├── main.py
├── requirements.txt
├── .env.example
├── config.py
├── auth/
│   ├── dependencies.py
│   ├── router.py
├── services/
│   ├── github_fetcher.py
│   ├── feature_extractor.py
│   ├── tpr_scorer.py
│   ├── interview_agent.py         # Objective 1
│   ├── adversarial_evaluator.py   # Objective 1
│   ├── jd_analyzer.py             # Objective 2
│   ├── task_service.py            # Objective 2
│   ├── llm_generator.py           # Objective 3 — shared LLM entry point
│   └── chat_service.py            # Objective 3
├── routers/
│   ├── target_roles.py
│   └── scheduler.py
├── models/
│   ├── database.py
│   └── schemas.py
├── utils/
│   └── security.py
└── evaluation/
    ├── labeled_profiles.csv
    └── run_validation.py
```

---

## Part 8 — Backend Code

### 8.1 `config.py`

```python
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")  # verify current free-tier model before deploying
    DATABASE_URL = os.getenv("DATABASE_URL")
    JWT_SECRET = os.getenv("JWT_SECRET")
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRE_MINUTES = 60 * 24 * 7
    SCHEDULER_SECRET = os.getenv("SCHEDULER_SECRET")
    MAX_TARGET_ROLES_PER_USER = 3

settings = Settings()
```

### 8.2 `models/database.py`

```python
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, Boolean, TIMESTAMP, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.sql import func
from config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    github_username = Column(String(255))
    full_name = Column(String(255))
    created_at = Column(TIMESTAMP, server_default=func.now())

class Analysis(Base):
    __tablename__ = "analyses"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    tpr_score = Column(Float, nullable=False)
    confidence_level = Column(String(20))
    breakdown = Column(JSON, nullable=False)
    features = Column(JSON, nullable=False)
    flags = Column(JSON, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

class TargetRole(Base):
    __tablename__ = "target_roles"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    role_title = Column(String(255), nullable=False)
    company_name = Column(String(255))
    jd_text = Column(Text, nullable=False)
    latest_readiness_score = Column(Float)
    latest_gap_analysis = Column(JSON)
    created_at = Column(TIMESTAMP, server_default=func.now())
    last_analyzed_at = Column(TIMESTAMP)
    history = relationship("ReadinessHistory", backref="target_role", cascade="all, delete-orphan")

class ReadinessHistory(Base):
    __tablename__ = "readiness_history"
    id = Column(Integer, primary_key=True)
    target_role_id = Column(Integer, ForeignKey("target_roles.id", ondelete="CASCADE"))
    readiness_score = Column(Float, nullable=False)
    gap_summary = Column(JSON)
    recorded_at = Column(TIMESTAMP, server_default=func.now())

class EvaluationVerdict(Base):
    __tablename__ = "evaluation_verdicts"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    target_role_id = Column(Integer, ForeignKey("target_roles.id", ondelete="CASCADE"))
    skeptic_case = Column(Text)
    advocate_case = Column(Text)
    final_verdict = Column(Text)
    confidence = Column(Float)
    surviving_skeptic_points = Column(JSON)
    surviving_advocate_points = Column(JSON)
    created_at = Column(TIMESTAMP, server_default=func.now())

class VerificationSession(Base):
    __tablename__ = "verification_sessions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    target_role_id = Column(Integer, ForeignKey("target_roles.id", ondelete="SET NULL"), nullable=True)
    scenario = Column(JSON, nullable=False)
    candidate_answer = Column(Text)
    quality_score = Column(Float)
    reasoning = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    target_role_id = Column(Integer, ForeignKey("target_roles.id", ondelete="CASCADE"))
    missing_requirement = Column(Text, nullable=False)
    target_repo = Column(String(255))
    task_description = Column(Text, nullable=False)
    verification_signal = Column(Text)
    status = Column(String(20), default="assigned")
    created_at = Column(TIMESTAMP, server_default=func.now())
    verified_at = Column(TIMESTAMP)

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    target_role_id = Column(Integer, ForeignKey("target_roles.id", ondelete="SET NULL"), nullable=True)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    target_role_id = Column(Integer, ForeignKey("target_roles.id", ondelete="CASCADE"))
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

class ShareToken(Base):
    __tablename__ = "share_tokens"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    token = Column(String(64), unique=True, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    expires_at = Column(TIMESTAMP)

def init_db():
    Base.metadata.create_all(bind=engine)
```

### 8.3 `models/schemas.py`

```python
from pydantic import BaseModel
from typing import Optional, Dict, List

class SignupRequest(BaseModel):
    email: str
    password: str
    github_username: str
    full_name: Optional[str] = None

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TargetRoleCreate(BaseModel):
    role_title: str
    company_name: Optional[str] = None
    jd_text: str

class JDGapResponse(BaseModel):
    matched_requirements: List[Dict]   # each: {"requirement": str, "evidence_citation": str}
    missing_requirements: List[str]
    recommended_actions: List[str]
    readiness_estimate: int

class ChatRequest(BaseModel):
    question: str
    target_role_id: Optional[int] = None

class ChatResponse(BaseModel):
    answer: str
```

### 8.4 `utils/security.py`

```python
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    return jwt.encode({"sub": str(user_id), "exp": expire}, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def decode_token(token: str) -> int:
    payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    return int(payload["sub"])
```

### 8.5 `auth/dependencies.py`

```python
from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session
from models.database import SessionLocal, User
from utils.security import decode_token

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(authorization: str = Header(...), db: Session = Depends(get_db)) -> User:
    try:
        token = authorization.replace("Bearer ", "")
        user_id = decode_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
```

### 8.6 `auth/router.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import User
from models.schemas import SignupRequest, LoginRequest, TokenResponse
from utils.security import hash_password, verify_password, create_access_token
from auth.dependencies import get_db

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=TokenResponse)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=payload.email, password_hash=hash_password(payload.password),
                github_username=payload.github_username, full_name=payload.full_name)
    db.add(user); db.commit(); db.refresh(user)
    return TokenResponse(access_token=create_access_token(user.id))

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return TokenResponse(access_token=create_access_token(user.id))
```

### 8.7 `services/github_fetcher.py`

```python
from github import Github
from typing import Dict
from datetime import datetime, timedelta
from config import settings

class GitHubFetcher:
    def __init__(self):
        self.github = Github(settings.GITHUB_TOKEN)

    def get_user_data(self, username: str) -> Dict:
        try:
            user = self.github.get_user(username)
            return {
                "username": username, "name": user.name, "bio": user.bio,
                "public_repos": user.public_repos, "created_at": user.created_at,
                "repos": self._get_significant_repos(user),
                "commits": self._get_recent_commits(user),
                "pull_requests": self._get_pull_requests(user),
                "code_reviews": self._get_code_reviews(user),
            }
        except Exception as e:
            raise ValueError(f"Error fetching GitHub data for '{username}': {str(e)}")

    def _get_significant_repos(self, user, limit=10):
        repos = user.get_repos(sort="updated", direction="desc")
        result = []
        for repo in list(repos)[:limit]:
            if not repo.fork:
                result.append({"name": repo.name, "description": repo.description,
                                "language": repo.language, "stars": repo.stargazers_count,
                                "updated_at": repo.updated_at})
        return result

    def _get_recent_commits(self, user, days=180):
        since = datetime.now() - timedelta(days=days)
        commits = []
        for repo in user.get_repos():
            try:
                for commit in list(repo.get_commits(author=user, since=since))[:50]:
                    commits.append({"repo": repo.name, "message": commit.commit.message,
                                     "date": commit.commit.author.date,
                                     "additions": commit.stats.additions, "deletions": commit.stats.deletions,
                                     "files_changed": len(commit.files)})
            except Exception:
                continue
        return commits

    def _get_pull_requests(self, user):
        prs = self.github.search_issues(f"author:{user.login} is:pr", sort="created", order="desc")
        return [{"title": pr.title, "state": pr.state, "created_at": pr.created_at,
                  "closed_at": pr.closed_at, "comments": pr.comments,
                  "body": (pr.body or "")[:500], "repo": pr.repository.name if pr.repository else None}
                for pr in list(prs)[:30]]

    def _get_code_reviews(self, user):
        reviewed = self.github.search_issues(f"commenter:{user.login} is:pr", sort="created", order="desc")
        return [{"pr_title": pr.title, "comment_count": pr.comments} for pr in list(reviewed)[:20]]
```

### 8.8 `services/feature_extractor.py`

```python
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List

class FeatureExtractor:
    def extract_all_features(self, github_data: Dict) -> Dict:
        return {
            "commit_features": self._extract_commit_features(github_data.get("commits", [])),
            "pr_features": self._extract_pr_features(github_data.get("pull_requests", [])),
            "collaboration_features": self._extract_collaboration_features(
                github_data.get("code_reviews", []), github_data.get("pull_requests", [])),
            "activity_features": self._extract_activity_features(github_data),
        }

    def _extract_commit_features(self, commits: List[Dict]) -> Dict:
        if not commits:
            return {"avg_commit_size": 0, "monolithic_commit_ratio": 0, "commits_per_week": 0,
                    "avg_message_quality": 0, "incremental_ratio": 0, "total_commits_analyzed": 0}
        df = pd.DataFrame(commits)
        df["total_changes"] = df["additions"] + df["deletions"]
        monolithic_ratio = (df["total_changes"] > df["total_changes"].quantile(0.9)).sum() / len(commits)
        df["date"] = pd.to_datetime(df["date"])
        df["week"] = df["date"].dt.isocalendar().week
        commits_per_week = df.groupby("week").size().mean()

        def message_quality(msg):
            if not msg: return 0
            m = msg.lower()
            score = sum(1 for w in ["fix","add","update","refactor","improve","implement"] if w in m)
            score -= sum(1 for w in ["wip","temp","test","asdf","..."] if w in m)
            return max(0, score + (1 if len(msg) > 20 else 0))

        df["msg_quality"] = df["message"].apply(message_quality)
        incremental_commits = (df["files_changed"] <= 5).sum()
        return {
            "avg_commit_size": float(df["total_changes"].mean()),
            "monolithic_commit_ratio": float(monolithic_ratio),
            "commits_per_week": float(commits_per_week),
            "avg_message_quality": float(df["msg_quality"].mean()),
            "incremental_ratio": float(incremental_commits / len(commits)),
            "total_commits_analyzed": len(commits),
        }

    def _extract_pr_features(self, prs: List[Dict]) -> Dict:
        if not prs:
            return {"avg_pr_description_quality": 0, "avg_comments_per_pr": 0, "pr_merge_rate": 0, "total_prs_analyzed": 0}
        df = pd.DataFrame(prs)

        def desc_quality(body):
            if not body or len(body) < 20: return 0
            score = 2 if len(body) > 100 else 1
            score += 1 if "```" in body else 0
            score += 1 if any(w in body.lower() for w in ["why","because","fix","implement"]) else 0
            return score

        df["desc_quality"] = df["body"].apply(desc_quality)
        merged = df[df["state"] == "closed"]
        return {
            "avg_pr_description_quality": float(df["desc_quality"].mean()),
            "avg_comments_per_pr": float(df["comments"].mean()),
            "pr_merge_rate": float(len(merged) / len(prs)),
            "total_prs_analyzed": len(prs),
        }

    def _extract_collaboration_features(self, reviews: List[Dict], prs: List[Dict]) -> Dict:
        review_count, pr_count = len(reviews), len(prs)
        return {"code_reviews_given": review_count,
                "review_to_pr_ratio": float(review_count / pr_count) if pr_count > 0 else 0,
                "collaboration_score": min(10, review_count)}

    def _extract_activity_features(self, github_data: Dict) -> Dict:
        repos = github_data.get("repos", [])
        created_at = github_data.get("created_at") or datetime.now()
        account_age_days = (datetime.now() - created_at.replace(tzinfo=None)).days
        six_months_ago = datetime.now() - timedelta(days=180)
        active_repos = sum(1 for r in repos if r.get("updated_at") and r["updated_at"].replace(tzinfo=None) > six_months_ago)
        return {"account_age_days": account_age_days, "total_public_repos": len(repos),
                "active_repos_ratio": float(active_repos / len(repos)) if repos else 0,
                "avg_repo_stars": (sum(r.get("stars", 0) for r in repos) / len(repos)) if repos else 0}
```

### 8.9 `services/tpr_scorer.py`

```python
from typing import Dict, Tuple, List

class TPRScorer:
    """Objective 1's base signal. Weights are hand-set for Phase 2's MVP and
    validated against the labeled dataset in Part 11 — see Part 11 for the
    stretch goal of replacing these with weights learned from that dataset."""

    WEIGHTS = {"commit_quality": 0.30, "pr_quality": 0.35, "collaboration": 0.20, "activity": 0.15}

    def calculate_tpr_score(self, features: Dict) -> Tuple[float, str, Dict]:
        c, p, cl, a = (self._score_commits(features["commit_features"]),
                       self._score_prs(features["pr_features"]),
                       self._score_collaboration(features["collaboration_features"]),
                       self._score_activity(features["activity_features"]))
        tpr = (c * self.WEIGHTS["commit_quality"] + p * self.WEIGHTS["pr_quality"] +
               cl * self.WEIGHTS["collaboration"] + a * self.WEIGHTS["activity"])
        data_points = (features["commit_features"]["total_commits_analyzed"] +
                       features["pr_features"]["total_prs_analyzed"] +
                       features["collaboration_features"]["code_reviews_given"])
        confidence = "low" if data_points < 10 else "medium" if data_points < 30 else "high"
        breakdown = {"commit_score": round(c,1), "pr_score": round(p,1),
                     "collaboration_score": round(cl,1), "activity_score": round(a,1), "data_points": data_points}
        return round(tpr, 1), confidence, breakdown

    def _score_commits(self, f: Dict) -> float:
        if f["total_commits_analyzed"] == 0: return 0
        score = f["incremental_ratio"] * 30 + min(f["avg_message_quality"] * 10, 25)
        score -= f["monolithic_commit_ratio"] * 20
        score += 20 if f["commits_per_week"] > 2 else (10 if f["commits_per_week"] > 0.5 else 0)
        score += 25 if 50 < f["avg_commit_size"] < 500 else (15 if f["avg_commit_size"] < 50 else 0)
        return max(0, min(100, score))

    def _score_prs(self, f: Dict) -> float:
        if f["total_prs_analyzed"] == 0: return 50
        score = min(f["avg_pr_description_quality"] * 15, 40)
        score += 30 if f["avg_comments_per_pr"] > 3 else (15 if f["avg_comments_per_pr"] > 1 else 0)
        return max(0, min(100, score + f["pr_merge_rate"] * 30))

    def _score_collaboration(self, f: Dict) -> float:
        score = min(f["code_reviews_given"] * 8, 50)
        score += 30 if 0.3 < f["review_to_pr_ratio"] < 3 else (15 if f["review_to_pr_ratio"] > 0 else 0)
        return max(0, min(100, score + f["collaboration_score"] * 2))

    def _score_activity(self, f: Dict) -> float:
        score = f["active_repos_ratio"] * 40
        n = f["total_public_repos"]
        score += 30 if n > 10 else (20 if n > 5 else (10 if n > 2 else 0))
        score += 30 if f["avg_repo_stars"] > 5 else (15 if f["avg_repo_stars"] > 0 else 0)
        return max(0, min(100, score))

    def generate_flags(self, features: Dict) -> Dict[str, List[str]]:
        green, red = [], []
        c, p, cl = features["commit_features"], features["pr_features"], features["collaboration_features"]
        if c["incremental_ratio"] > 0.7: green.append("Consistent incremental development pattern")
        if c["monolithic_commit_ratio"] > 0.3: red.append("Frequent large, monolithic commits")
        if c["avg_message_quality"] > 3: green.append("Clear, descriptive commit messages")
        elif c["avg_message_quality"] < 1: red.append("Vague or minimal commit messages")
        if p["avg_pr_description_quality"] > 3: green.append("Well-documented pull requests")
        if p["pr_merge_rate"] > 0.7: green.append("High PR acceptance rate")
        elif p["pr_merge_rate"] < 0.3 and p["total_prs_analyzed"] > 5: red.append("Low PR merge rate")
        if cl["code_reviews_given"] > 10: green.append("Actively contributes to code reviews")
        elif cl["code_reviews_given"] == 0: red.append("No evidence of peer code reviews")
        if c["commits_per_week"] > 5: green.append("Highly active contributor")
        elif c["commits_per_week"] < 0.5: red.append("Low commit frequency")
        return {"green_flags": green, "red_flags": red}
```

### 8.10 `services/llm_generator.py` (Objective 3 — every claim must cite evidence)

```python
import google.generativeai as genai
import json
from typing import Dict, List
from config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)

class LLMGenerator:
    def __init__(self):
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)

    def generate_executive_summary(self, tpr_score, confidence, breakdown, flags) -> str:
        prompt = f"""You are a mentor writing directly to a developer about their own GitHub activity.
TPR SCORE: {tpr_score}/100 — Confidence: {confidence}
COMPONENTS: {breakdown}
GREEN FLAGS: {flags['green_flags'] or 'None identified'}
RED FLAGS: {flags['red_flags'] or 'None identified'}
Write 150-200 words, second person, covering: what the score means, top 2 strengths (specific), top area to improve, one thing to do this week."""
        try:
            return self.model.generate_content(prompt).text
        except Exception:
            strengths = "; ".join(flags["green_flags"][:2]) or "Not enough data yet"
            return f"Your TPR score is {tpr_score}/100. Strengths: {strengths}."

    def generate_jd_gap_analysis(self, jd_text: str, tpr_score: float, breakdown: Dict,
                                   flags: Dict, top_repos: List[Dict], top_prs: List[Dict]) -> Dict:
        repo_summary = "\n".join(f"- {r['name']}: {r.get('description','')} ({r.get('language','')})" for r in top_repos[:5])
        pr_summary = "\n".join(f"- {p['title']}" for p in top_prs[:5])
        prompt = f"""Analyze this candidate's GitHub evidence against a job description.
JOB DESCRIPTION:\n{jd_text}
TPR: {tpr_score}/100, breakdown: {breakdown}, flags: {flags}
REPOSITORIES:\n{repo_summary}
PULL REQUESTS:\n{pr_summary}

CRITICAL RULE: every matched requirement MUST cite a specific repo or PR name from above as evidence. Never assert a match without naming exactly which repo/PR proves it. If you cannot find real evidence, put the requirement in missing_requirements instead.

Return valid JSON only:
{{"matched_requirements": [{{"requirement": "...", "evidence_citation": "exact repo or PR name from above"}}],
  "missing_requirements": ["..."], "recommended_actions": ["...", "...", "..."],
  "readiness_estimate": <0-100>}}"""
        try:
            r = self.model.generate_content(prompt)
            text = r.text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            result = json.loads(text)
            valid_names = {r["name"] for r in top_repos} | {p["title"] for p in top_prs}
            result["matched_requirements"] = [
                m for m in result.get("matched_requirements", []) if m.get("evidence_citation") in valid_names
            ]
            return result
        except Exception as e:
            return {"matched_requirements": [], "missing_requirements": [],
                    "recommended_actions": ["Analysis temporarily unavailable — try again."],
                    "readiness_estimate": tpr_score, "error": str(e)}

    def generate_chat_response(self, question: str, analysis_context: Dict, chat_history: List[Dict]) -> str:
        history_text = "\n".join(f"{m['role']}: {m['content']}" for m in chat_history[-6:])
        prompt = f"""Answer the candidate's question about their OWN analysis, citing specific numbers/examples — never generic advice.
ANALYSIS: {analysis_context}
RECENT CONVERSATION:\n{history_text}
QUESTION: {question}
Answer in under 120 words."""
        try:
            return self.model.generate_content(prompt).text
        except Exception:
            return "Couldn't generate a response just now — try again."
```

### 8.11 `services/interview_agent.py` (Objective 1)

```python
from services.llm_generator import LLMGenerator
import json

class InterviewAgent:
    """Generates a short, personalized verification scenario from a specific
    gap in the candidate's own repo — not a generic interview question."""

    def __init__(self):
        self.llm = LLMGenerator()

    def generate_scenario(self, top_repos: list, flags: dict, jd_text: str = None) -> dict:
        context = f"Target role context:\n{jd_text}\n" if jd_text else ""
        repo_summary = "\n".join(f"- {r['name']}: {r.get('description','')} ({r.get('language','')})" for r in top_repos[:5])
        prompt = f"""{context}
CANDIDATE'S TOP REPOSITORIES:\n{repo_summary}
RED FLAGS: {flags.get('red_flags', [])}

Pick ONE specific gap and design a short, concrete scenario the candidate can answer in a few sentences or a short snippet, grounded in one of their actual repos above. Not a generic algorithm question.

Return valid JSON only:
{{"target_repo": "repo name used", "scenario": "2-4 sentence question/task", "what_a_strong_answer_shows": "..."}}"""
        try:
            r = self.llm.model.generate_content(prompt)
            text = r.text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            return json.loads(text)
        except Exception:
            return {"target_repo": None, "scenario": "Could not generate a scenario right now.", "what_a_strong_answer_shows": None}

    def evaluate_response(self, scenario: dict, candidate_answer: str) -> dict:
        prompt = f"""SCENARIO: {scenario['scenario']}
WHAT A STRONG ANSWER SHOWS: {scenario.get('what_a_strong_answer_shows')}
CANDIDATE'S ANSWER: {candidate_answer}

Return valid JSON only: {{"quality_score": <0-100>, "reasoning": "1-2 sentences, specific to this answer"}}"""
        try:
            r = self.llm.model.generate_content(prompt)
            text = r.text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            return json.loads(text)
        except Exception:
            return {"quality_score": 50, "reasoning": "Evaluation temporarily unavailable."}
```

### 8.12 `services/adversarial_evaluator.py` (Objective 1)

```python
from services.llm_generator import LLMGenerator
import json

class AdversarialEvaluator:
    """Three prompted passes on the same model — Skeptic, Advocate, Judge —
    instead of one one-shot opinion. Same model, different roles: this is
    what 'multi-agent' means here, not multiple model vendors."""

    def __init__(self):
        self.llm = LLMGenerator()

    def _run_role(self, instruction: str, evidence: dict) -> str:
        prompt = f"""{instruction}
EVIDENCE:
TPR: {evidence['tpr_score']}/100, breakdown: {evidence['breakdown']}
Green flags: {evidence['flags']['green_flags']}
Red flags: {evidence['flags']['red_flags']}
Top repos: {[r['name'] for r in evidence.get('top_repos', [])]}
Give your case in under 120 words. Cite only evidence listed above — never invent anything."""
        try:
            return self.llm.model.generate_content(prompt).text
        except Exception:
            return "Unavailable."

    def evaluate(self, evidence: dict) -> dict:
        skeptic = self._run_role("You are a skeptical reviewer. Argue the strongest honest case for why this candidate might NOT be production-ready.", evidence)
        advocate = self._run_role("You are an advocate reviewer. Argue the strongest honest case for why this candidate IS production-ready.", evidence)

        judge_prompt = f"""Two reviewers examined the same evidence.
SKEPTIC: {skeptic}
ADVOCATE: {advocate}
Weigh both, note which points from each actually hold up against the evidence, give a final calibrated verdict.
Return valid JSON only: {{"final_verdict": "1-2 sentences", "confidence": <0-100>, "surviving_skeptic_points": ["..."], "surviving_advocate_points": ["..."]}}"""
        try:
            r = self.llm.model.generate_content(judge_prompt)
            text = r.text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            judge = json.loads(text)
        except Exception:
            judge = {"final_verdict": "Unavailable", "confidence": 0, "surviving_skeptic_points": [], "surviving_advocate_points": []}
        return {"skeptic_case": skeptic, "advocate_case": advocate, **judge}
```

### 8.13 `services/jd_analyzer.py` (Objective 2)

```python
from services.llm_generator import LLMGenerator

class JDAnalyzer:
    def __init__(self):
        self.llm = LLMGenerator()

    def analyze(self, jd_text, tpr_score, breakdown, flags, top_repos, top_prs) -> dict:
        return self.llm.generate_jd_gap_analysis(jd_text, tpr_score, breakdown, flags, top_repos, top_prs)
```

### 8.14 `services/task_service.py` (Objective 2)

```python
from services.llm_generator import LLMGenerator
import json

class TaskService:
    def __init__(self):
        self.llm = LLMGenerator()

    def generate_task(self, missing_requirement: str, top_repos: list) -> dict:
        repo_summary = "\n".join(f"- {r['name']}: {r.get('description','')} ({r.get('language','')})" for r in top_repos[:5])
        prompt = f"""A candidate is missing evidence for: "{missing_requirement}"
THEIR REPOS:\n{repo_summary}
Design ONE specific, scoped, verifiable micro-task tied to an actual repo above where possible, completable in a few hours.
Return valid JSON only: {{"target_repo": "repo name or 'new repo'", "task_description": "specific instructions", "verification_signal": "what a re-scan should look for, e.g. a new test file or specific commit content"}}"""
        try:
            r = self.llm.model.generate_content(prompt)
            text = r.text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            return json.loads(text)
        except Exception:
            return {"target_repo": None, "task_description": "Could not generate a task right now.", "verification_signal": None}

    def check_completion(self, task: dict, github_data: dict) -> bool:
        """Deliberately simple heuristic for Phase 2: keyword match against
        recent commits in the target repo — not full static analysis."""
        target_repo, signal = task.get("target_repo"), (task.get("verification_signal") or "").lower()
        if not target_repo or not signal:
            return False
        for commit in github_data.get("commits", []):
            if commit["repo"] == target_repo:
                if any(word in commit["message"].lower() for word in signal.split() if len(word) > 4):
                    return True
        return False
```

### 8.15 `services/chat_service.py`

```python
from services.llm_generator import LLMGenerator

class ChatService:
    def __init__(self):
        self.llm = LLMGenerator()

    def respond(self, question: str, analysis_context: dict, chat_history: list) -> str:
        return self.llm.generate_chat_response(question, analysis_context, chat_history)
```

### 8.16 `routers/target_roles.py` — representative full router

All other routers (analysis, chat, notifications, share) follow this exact same pattern: auth via `get_current_user`, a service call, a Pydantic response.

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import TargetRole, ReadinessHistory, EvaluationVerdict, Task, User
from models.schemas import TargetRoleCreate, JDGapResponse
from auth.dependencies import get_current_user, get_db
from config import settings
from services.github_fetcher import GitHubFetcher
from services.feature_extractor import FeatureExtractor
from services.tpr_scorer import TPRScorer
from services.jd_analyzer import JDAnalyzer
from services.adversarial_evaluator import AdversarialEvaluator
from services.task_service import TaskService

router = APIRouter(prefix="/api/target-roles", tags=["target-roles"])

@router.post("")
def create_target_role(payload: TargetRoleCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if db.query(TargetRole).filter(TargetRole.user_id == user.id).count() >= settings.MAX_TARGET_ROLES_PER_USER:
        raise HTTPException(status_code=400, detail=f"Maximum {settings.MAX_TARGET_ROLES_PER_USER} target roles allowed")
    role = TargetRole(user_id=user.id, role_title=payload.role_title, company_name=payload.company_name, jd_text=payload.jd_text)
    db.add(role); db.commit(); db.refresh(role)
    return role

@router.get("")
def list_target_roles(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(TargetRole).filter(TargetRole.user_id == user.id).all()

@router.post("/{role_id}/analyze", response_model=JDGapResponse)
def analyze_target_role(role_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    role = db.query(TargetRole).filter(TargetRole.id == role_id, TargetRole.user_id == user.id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Target role not found")

    github_data = GitHubFetcher().get_user_data(user.github_username)
    features = FeatureExtractor().extract_all_features(github_data)
    tpr_score, confidence, breakdown = TPRScorer().calculate_tpr_score(features)
    flags = TPRScorer().generate_flags(features)

    gap = JDAnalyzer().analyze(role.jd_text, tpr_score, breakdown, flags, github_data["repos"], github_data["pull_requests"])

    verdict = AdversarialEvaluator().evaluate({"tpr_score": tpr_score, "breakdown": breakdown, "flags": flags, "top_repos": github_data["repos"]})
    db.add(EvaluationVerdict(user_id=user.id, target_role_id=role.id, skeptic_case=verdict["skeptic_case"],
                               advocate_case=verdict["advocate_case"], final_verdict=verdict["final_verdict"],
                               confidence=verdict["confidence"], surviving_skeptic_points=verdict["surviving_skeptic_points"],
                               surviving_advocate_points=verdict["surviving_advocate_points"]))

    task_service = TaskService()
    for missing in gap.get("missing_requirements", [])[:2]:  # cap at 2 open tasks per analysis
        task = task_service.generate_task(missing, github_data["repos"])
        db.add(Task(user_id=user.id, target_role_id=role.id, missing_requirement=missing,
                     target_repo=task.get("target_repo"), task_description=task["task_description"],
                     verification_signal=task.get("verification_signal")))

    role.latest_readiness_score = gap["readiness_estimate"]
    role.latest_gap_analysis = gap
    db.add(ReadinessHistory(target_role_id=role.id, readiness_score=gap["readiness_estimate"], gap_summary=gap))
    db.commit()
    return gap
```

### 8.17 `routers/scheduler.py` — weekly re-analysis, now also checking task completion

```python
from fastapi import APIRouter, Header, HTTPException
from config import settings
from models.database import SessionLocal, TargetRole, ReadinessHistory, Notification, Task, User
from services.github_fetcher import GitHubFetcher
from services.feature_extractor import FeatureExtractor
from services.tpr_scorer import TPRScorer
from services.jd_analyzer import JDAnalyzer
from services.task_service import TaskService
from datetime import datetime

router = APIRouter()

@router.post("/api/internal/run-weekly-reanalysis")
def run_weekly_reanalysis(x_scheduler_secret: str = Header(...)):
    if x_scheduler_secret != settings.SCHEDULER_SECRET:
        raise HTTPException(status_code=401, detail="Invalid scheduler secret")

    db = SessionLocal()
    fetcher, extractor, scorer, jd_analyzer, task_service = (
        GitHubFetcher(), FeatureExtractor(), TPRScorer(), JDAnalyzer(), TaskService())
    processed = 0

    for role in db.query(TargetRole).all():
        user = db.query(User).get(role.user_id)
        if not user.github_username:
            continue
        try:
            github_data = fetcher.get_user_data(user.github_username)

            # check open tasks for this role
            open_tasks = db.query(Task).filter(Task.target_role_id == role.id, Task.status == "assigned").all()
            for task in open_tasks:
                task_dict = {"target_repo": task.target_repo, "verification_signal": task.verification_signal}
                if task_service.check_completion(task_dict, github_data):
                    task.status = "verified_complete"
                    task.verified_at = datetime.utcnow()
                    db.add(Notification(user_id=user.id, target_role_id=role.id,
                                          message=f"Verified: you completed the task addressing '{task.missing_requirement}'."))

            features = extractor.extract_all_features(github_data)
            tpr_score, confidence, breakdown = scorer.calculate_tpr_score(features)
            flags = scorer.generate_flags(features)
            gap = jd_analyzer.analyze(role.jd_text, tpr_score, breakdown, flags, github_data["repos"], github_data["pull_requests"])

            previous = role.latest_readiness_score
            role.latest_readiness_score = gap["readiness_estimate"]
            role.latest_gap_analysis = gap
            db.add(ReadinessHistory(target_role_id=role.id, readiness_score=gap["readiness_estimate"], gap_summary=gap))

            if previous is not None and abs(gap["readiness_estimate"] - previous) >= 10:
                direction = "improved" if gap["readiness_estimate"] > previous else "dropped"
                db.add(Notification(user_id=role.user_id, target_role_id=role.id,
                                      message=f"Readiness for {role.role_title} {direction} to {gap['readiness_estimate']}%."))
            processed += 1
        except Exception:
            continue

    db.commit()
    db.close()
    return {"processed": processed}
```

**`.github/workflows/weekly-reanalysis.yml`:**

```yaml
name: Weekly Re-analysis
on:
  schedule:
    - cron: "0 3 * * 1"
  workflow_dispatch: {}
jobs:
  trigger:
    runs-on: ubuntu-latest
    steps:
      - name: Call backend scheduler endpoint
        run: |
          curl -X POST https://your-backend.onrender.com/api/internal/run-weekly-reanalysis \
            -H "X-Scheduler-Secret: ${{ secrets.SCHEDULER_SECRET }}"
```

### 8.18 `main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models.database import init_db
from auth.router import router as auth_router
from routers.target_roles import router as target_roles_router
from routers.scheduler import router as scheduler_router
# add these as you build them, same pattern:
# from routers.analysis import router as analysis_router
# from routers.chat import router as chat_router
# from routers.notifications import router as notifications_router
# from routers.share import router as share_router

app = FastAPI(title="SkillProof API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
init_db()

app.include_router(auth_router)
app.include_router(target_roles_router)
app.include_router(scheduler_router)

@app.get("/")
def root():
    return {"message": "SkillProof API — Phase 2"}
```

---

## Part 9 — API Endpoint Reference

| Method | Path | Purpose |
|---|---|---|
| POST | `/auth/signup` | Create account |
| POST | `/auth/login` | Returns JWT |
| POST | `/api/analyze` | Base GitHub analysis, stores history |
| GET | `/api/analysis/latest` | Latest base analysis |
| GET | `/api/analysis/history` | Trend chart data |
| POST | `/api/target-roles` | Save a JD (max 3) |
| GET | `/api/target-roles` | List saved roles |
| POST | `/api/target-roles/{id}/analyze` | Gap analysis + adversarial verdict + tasks |
| GET | `/api/target-roles/{id}/history` | Readiness trend for one role |
| POST | `/api/chat` | Ask a question |
| GET | `/api/notifications` | List notifications |
| POST | `/api/share/create` | Generate a share token |
| GET | `/api/share/{token}` | Public recruiter view |
| POST | `/api/internal/run-weekly-reanalysis` | Cron-only, secret-protected |

---

## Part 10 — Frontend Pages & Components

```
app/
├── (auth)/signup/page.tsx
├── (auth)/login/page.tsx
├── dashboard/page.tsx           # TPR score, trend, flags
├── target-roles/page.tsx        # saved JDs list + add new
├── target-roles/[id]/page.tsx   # gap analysis, verdict, tasks, chat for this role
├── chat/page.tsx                # general chat
├── share/[token]/page.tsx       # public recruiter view
└── layout.tsx
```

Key components: `TPRScoreCard`, `TrendChart`, `GapAnalysisPanel` (matched with citations / missing / actions), `VerdictPanel` (skeptic vs advocate vs judge, shown as three short cards), `TaskCard` (with status badge), `ChatWindow`, `NotificationBell`. Build mobile-first.

---

## Part 11 — Dataset & Validation Plan

**Purpose:** validate that the TPR scorer and adversarial evaluator actually separate strong candidates from weak ones — not just claim to.

**Building the dataset (manual, ~100–150 profiles):**
- ~40 established open-source contributors (public, easy to find on popular repos) — proxy label `"strong"`
- ~70 batch/college peers (your actual target population) — proxy label `"mid"`
- ~30 brand-new or tutorial-only accounts — proxy label `"beginner"`

Be explicit in your report: these are **proxy labels**, not verified hire/no-hire outcomes — standard, honest practice given a student team cannot access real hiring outcome data.

**`evaluation/run_validation.py`:**

```python
import csv
from services.github_fetcher import GitHubFetcher
from services.feature_extractor import FeatureExtractor
from services.tpr_scorer import TPRScorer

def run():
    fetcher, extractor, scorer = GitHubFetcher(), FeatureExtractor(), TPRScorer()
    results = []
    with open("evaluation/labeled_profiles.csv") as f:
        for row in csv.DictReader(f):  # columns: username,tier
            try:
                data = fetcher.get_user_data(row["username"])
                features = extractor.extract_all_features(data)
                tpr_score, _, _ = scorer.calculate_tpr_score(features)
                results.append({"username": row["username"], "tier": row["tier"], "tpr_score": tpr_score})
            except Exception as e:
                print(f"Skipped {row['username']}: {e}")

    for tier in ["strong", "mid", "beginner"]:
        scores = [r["tpr_score"] for r in results if r["tier"] == tier]
        if scores:
            print(f"{tier}: n={len(scores)}, avg={sum(scores)/len(scores):.1f}, min={min(scores)}, max={max(scores)}")

if __name__ == "__main__":
    run()
```

**Minimum bar:** the three tiers' average scores should be clearly separated and in the expected order. Report this chart — it's stronger evidence than another feature.

**Stretch goal, only if time allows:** instead of the hand-set weights in `TPRScorer.WEIGHTS`, fit a small logistic regression on the labeled dataset's extracted features to *learn* the weighting. 100–150 labeled examples is enough for a model this simple. This turns "we picked weights that felt right" into a reportable, validated ML result — without touching the product's architecture.

---

## Part 12 — Suggested Team Split (4 members)

- **Member A — Core engine & data:** GitHub fetcher, feature extractor, TPR scorer, database, auth, the evaluation dataset and script
- **Member B — Verification agents:** interview agent, adversarial evaluator, prompt iteration
- **Member C — Close-the-loop & explainability:** JD analyzer, task service, llm_generator, chat service
- **Member D — Frontend, infra & quality:** all frontend pages, deployment, scheduler + GitHub Actions, edge-case handling

---

## Part 13 — Deployment

- **Frontend:** Vercel, env var `NEXT_PUBLIC_API_URL`
- **Backend:** Render free web service — build `pip install -r requirements.txt`, start `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Database:** Supabase free-tier PostgreSQL
- **Secrets:** `GITHUB_TOKEN`, `GEMINI_API_KEY`, `JWT_SECRET`, `SCHEDULER_SECRET`, `DATABASE_URL`
- **PWA:** add `manifest.json` + `next-pwa` for "add to home screen" on Android — this is the pragmatic mobile-app path, not a native Play Store build

---

## Part 14 — Demo Script

**30-second pitch:** "SkillProof verifies a candidate's real engineering readiness against a specific job — not with a single AI opinion, but through adversarial cross-examination of their actual GitHub evidence. When a gap is found, it assigns a specific task and automatically confirms when that gap is actually closed."

**Live walkthrough:**
1. Dashboard — TPR score, trend
2. Paste a real JD → gap analysis with cited evidence
3. Show the Skeptic / Advocate / Judge verdict panel
4. Show an assigned task and its verified-complete status
5. Show the chat, then the recruiter share link

**Be ready to explain:** why adversarial multi-agent evaluation instead of one LLM call, why no vector DB yet, the dataset methodology from Part 11, and the TPR weighting rationale.
