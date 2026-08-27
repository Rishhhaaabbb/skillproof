# SkillProof

> Beyond keywords: explainable AI for developer behaviour verification.

SkillProof analyzes a candidate's real GitHub activity — commits, pull requests, code reviews — and produces a verified, explainable readiness assessment against a specific job description.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14 (App Router) + TypeScript, Tailwind CSS + shadcn/ui |
| Backend | FastAPI (Python 3.11+) |
| Auth | Custom JWT (passlib + python-jose) |
| Database | PostgreSQL via Supabase |
| GitHub Integration | PyGithub |
| LLM | Google Gemini API (gemini-3.7-flash) |
| Scheduling | GitHub Actions cron |
| Deployment | Vercel (frontend) + Render (backend) |

## Getting Started

### Backend

```bash
cd skillproof-backend
pip install -r requirements.txt
cp .env.example .env
# Fill in your real values in .env
uvicorn main:app --reload
```

### Frontend

```bash
cd skillproof-frontend
npm install
cp .env.local.example .env.local
npm run dev
```

### Verify

- Backend health check: http://localhost:8000
- API docs: http://localhost:8000/docs
- Frontend: http://localhost:3000
