# SkillProof — Day 10 Production Audit Report

Audit conducted against the full codebase (Days 1–9 output) before first deployment.

---

## Issues Fixed During This Audit

### 1. `AnalysisOut.flags` type mismatch (schema bug) ✅ Fixed
- **File:** `skillproof-backend/models/schemas.py`
- **Problem:** `flags` was typed as `Optional[List[str]]` but the database stores flags as `{"green_flags": [...], "red_flags": [...]}` — a dict of lists. This would cause Pydantic validation failures on every `GET /api/analysis/latest` response.
- **Fix:** Changed type to `Optional[Dict[str, List[str]]]`.

### 2. `next.config.ts` — next-pwa CJS import ✅ Fixed
- **File:** `skillproof-frontend/next.config.ts`
- **Problem:** `import withPWAInit from "next-pwa"` fails with TypeScript because `next-pwa` v5 ships only CommonJS types with no default export declaration.
- **Fix:** Replaced with `const withPWAInit = require("next-pwa")` with ESLint disable comment.

### 3. `vercel.json` hardcoded env var ✅ Fixed
- **File:** `skillproof-frontend/vercel.json`
- **Problem:** `env.NEXT_PUBLIC_API_URL` was hardcoded as a plaintext value — Vercel `env` blocks in `vercel.json` are committed to git and should not hold production URLs directly.
- **Fix:** Removed the `env` block. Set `NEXT_PUBLIC_API_URL` via Vercel dashboard → Environment Variables instead (documented in `DEPLOYMENT.md`). Added `/auth/:path*` rewrite alongside the existing `/api/:path*` one so the auth endpoints proxy correctly through Vercel.

---

## Route Coverage — All 14 API Endpoints

| Method | Path | Router File | Auth Guard | Status |
|---|---|---|---|---|
| POST | `/auth/signup` | `auth/router.py` | None (public) | ✅ |
| POST | `/auth/login` | `auth/router.py` | None (public) | ✅ Rate-limited (10/min) |
| POST | `/auth/refresh` | `auth/router.py` | None (refresh token) | ✅ |
| GET | `/auth/me` | `auth/router.py` | JWT Bearer | ✅ |
| POST | `/api/analysis/trigger` | `routers/analysis.py` | JWT Bearer | ✅ Async job |
| GET | `/api/analysis/latest` | `routers/analysis.py` | JWT Bearer | ✅ |
| GET | `/api/analysis/history` | `routers/analysis.py` | JWT Bearer | ✅ Paginated |
| GET | `/api/analysis/heatmap` | `routers/analysis.py` | JWT Bearer | ✅ |
| GET | `/api/analysis/skills` | `routers/analysis.py` | JWT Bearer | ✅ |
| GET | `/api/analysis/streaks` | `routers/analysis.py` | JWT Bearer | ✅ |
| GET | `/api/analysis/export/pdf` | `routers/analysis.py` | JWT Bearer | ✅ |
| POST | `/api/target-roles` | `routers/target_roles.py` | JWT Bearer | ✅ Max-3 enforced |
| GET | `/api/target-roles` | `routers/target_roles.py` | JWT Bearer | ✅ |
| GET | `/api/target-roles/{id}` | `routers/target_roles.py` | JWT Bearer | ✅ Ownership check |
| PATCH | `/api/target-roles/{id}` | `routers/target_roles.py` | JWT Bearer | ✅ Ownership check |
| DELETE | `/api/target-roles/{id}` | `routers/target_roles.py` | JWT Bearer | ✅ Ownership check |
| POST | `/api/target-roles/{id}/analyze` | `routers/target_roles.py` | JWT Bearer | ✅ Async job |
| GET | `/api/target-roles/{id}/history` | `routers/target_roles.py` | JWT Bearer | ✅ |
| GET | `/api/target-roles/{id}/verdict` | `routers/target_roles.py` | JWT Bearer | ✅ |
| GET | `/api/target-roles/{id}/tasks` | `routers/target_roles.py` | JWT Bearer | ✅ |
| GET | `/api/target-roles/{id}/comparison` | `routers/target_roles.py` | JWT Bearer | ✅ |
| POST | `/api/chat` | `routers/chat.py` | JWT Bearer | ✅ |
| GET | `/api/chat` | `routers/chat.py` | JWT Bearer | ✅ |
| DELETE | `/api/chat` | `routers/chat.py` | JWT Bearer | ✅ |
| GET | `/api/notifications` | `routers/notifications.py` | JWT Bearer | ✅ |
| GET | `/api/notifications/unread-count` | `routers/notifications.py` | JWT Bearer | ✅ |
| PATCH | `/api/notifications/{id}/read` | `routers/notifications.py` | JWT Bearer | ✅ Ownership check |
| PATCH | `/api/notifications/read-all` | `routers/notifications.py` | JWT Bearer | ✅ |
| DELETE | `/api/notifications/{id}` | `routers/notifications.py` | JWT Bearer | ✅ Ownership check |
| POST | `/api/share/token` | `routers/share.py` | JWT Bearer | ✅ |
| GET | `/api/share/token` | `routers/share.py` | JWT Bearer | ✅ |
| DELETE | `/api/share/token` | `routers/share.py` | JWT Bearer | ✅ |
| GET | `/api/share/{token}` | `routers/share.py` | None (public) | ✅ Token expiry checked |
| POST | `/api/share/{token}/request` | `routers/share.py` | None (public) | ✅ |
| GET | `/api/share/requests` | `routers/share.py` | JWT Bearer | ✅ |
| GET | `/u/{username}` | `routers/public_profile.py` | None (public) | ✅ `is_public` gate |
| PATCH | `/api/settings` | `routers/public_profile.py` | JWT Bearer | ✅ |
| GET | `/api/jobs/{job_id}` | `routers/jobs.py` | JWT Bearer | ✅ Ownership check |
| POST | `/api/internal/run-weekly-reanalysis` | `routers/scheduler.py` | Scheduler secret header | ✅ |
| GET | `/` | `main.py` | None | ✅ |
| GET | `/health` | `main.py` | None | ✅ Render health check |

---

## Security Checklist

| Item | Status | Notes |
|---|---|---|
| All auth routes use JWT Bearer via `get_current_user` | ✅ | HTTPBearer dependency, returns 401 on failure |
| All ownership checks (user_id filter on queries) | ✅ | Every `/{id}` endpoint filters by `user.id` |
| Public endpoints don't leak private data | ✅ | `/u/{username}` requires `is_public=True`; `/api/share/{token}` returns limited fields only |
| Job ownership enforced | ✅ | `jobs.py` returns 404 for jobs belonging to other users |
| Scheduler endpoint protected | ✅ | X-Scheduler-Secret header required, returns 403 on mismatch |
| Login rate limiting | ✅ | 10 attempts per email per 60-second window |
| Password minimum length | ✅ | 8 characters, enforced in signup |
| Same error message for wrong email vs wrong password | ✅ | Prevents user enumeration |
| CORS locked in production | ✅ | Set CORS_ORIGINS to Vercel URL in Render env |
| HTTPS enforced | ✅ | Render and Vercel serve HTTPS by default |
| Refresh token rotation | ✅ | New pair issued on every refresh call |
| Security headers | ✅ | X-Frame-Options, X-Content-Type-Options, Referrer-Policy set in vercel.json |
| Secrets never in code | ✅ | All secrets via env vars; .env in .gitignore |

---

## Edge-Case Handling Checklist

| Case | Handler | Notes |
|---|---|---|
| Private GitHub profile | `github_fetcher.py` | Raises `ValueError` with clear message; router returns 400 |
| GitHub rate limit hit | `github_fetcher.py` | Returns `data_quality: "rate_limited"` with reset time; partial data returned, no crash |
| Empty GitHub account (no commits/PRs) | `feature_extractor.py` + `tpr_scorer.py` | All feature extractors return 0-filled defaults; TPR scores to 0 gracefully |
| User has no GitHub username linked | `analysis.py`, `target_roles.py` | Returns HTTP 400 with clear message before any GitHub fetch |
| Max 3 target roles enforced | `target_roles.py` | Returns HTTP 400 with count message |
| LLM (Gemini) failure | All service files | Try/except returns fallback text or empty lists; never crashes the endpoint |
| LLM citation hallucination | `llm_generator.py` | Evidence citations validated against actual repo/PR names; unmatched citations stripped |
| Job not found / belongs to other user | `jobs.py` | Returns HTTP 404 (indistinguishable to prevent enumeration) |
| Share token expired | `share.py` | Returns HTTP 404 with expiry message |
| Share token revoked | `share.py` | Previous token deleted when new one is created |
| Scheduler secret mismatch | `scheduler.py` | Returns HTTP 403 |
| Render cold start (free tier spin-down) | GitHub Actions workflow | Warm-up job pings `/health` up to 5× before triggering analysis |
| Database connection (PgBouncer vs direct) | `database.py` | Auto-detects port 6543 vs 5432, uses NullPool for PgBouncer |

---

## Remaining [YOU] Steps Before Launch

1. Install Xcode Command Line Tools: open Terminal → `xcode-select --install` → click Install
2. Pull latest from remote: `git pull origin main`
3. Push all Day 10 changes: `git add -A && git commit -m "Day 10: PWA, CORS, Render/Vercel deploy config" && git push`
4. Follow `DEPLOYMENT.md` step by step
5. After Render deploys — update `skillproof-api.onrender.com` placeholder in `vercel.json` with your actual Render service name, commit and push
6. Generate PWA icons: place `public/icons/icon-source.png`, run `npm install --save-dev sharp && node scripts/generate-icons.mjs`
7. Run the smoke test checklist in `DEPLOYMENT.md §8`
