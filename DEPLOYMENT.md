# SkillProof — Deployment Checklist

Complete every step in order. Steps marked **[YOU]** require a human action in a browser or terminal.

---

## 1. Supabase (Database) — do this first

- [ ] **[YOU]** Log in to [supabase.com](https://supabase.com) and open your project.
- [ ] **[YOU]** Confirm all tables exist (users, analyses, target_roles, readiness_history, evaluation_verdicts, verification_sessions, tasks, chat_messages, notifications, share_tokens). If not, run `init_db()` locally against the production DATABASE_URL.
- [ ] **[YOU]** Copy the **URI** connection string from Project Settings → Database → Connection string. Use **Session mode** (port 5432).

---

## 2. Backend — Render

- [ ] **[YOU]** Go to [render.com](https://render.com) → New → Web Service → connect your GitHub repo (`Rishhhaaabbb/skillproof`).
- [ ] **[YOU]** Set **Root Directory** to `skillproof-backend` — or use the `render.yaml` at the repo root (Render will auto-detect it).
- [ ] **[YOU]** Set **Build Command**: `pip install -r requirements.txt`
- [ ] **[YOU]** Set **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- [ ] **[YOU]** Set **Health Check Path**: `/health`
- [ ] **[YOU]** Add every environment variable below in Render dashboard → Environment:

  | Variable | Value |
  |---|---|
  | `GITHUB_TOKEN` | Your GitHub PAT |
  | `GEMINI_API_KEY` | Your Gemini key |
  | `GEMINI_MODEL` | `gemini-2.0-flash` |
  | `GEMINI_FALLBACK_MODEL` | `gemini-2.0-flash-lite` |
  | `DATABASE_URL` | Supabase session-mode URI |
  | `JWT_SECRET` | 32-byte hex secret |
  | `JWT_REFRESH_SECRET` | 32-byte hex secret (different from JWT_SECRET) |
  | `SCHEDULER_SECRET` | 32-byte hex secret |
  | `CORS_ORIGINS` | Your Vercel URL, e.g. `https://skillproof.vercel.app` |
  | `USE_LLM_MOCK` | `false` |

- [ ] **[YOU]** Deploy — wait for the build to succeed (check the Render logs).
- [ ] **[YOU]** Note your service URL, e.g. `https://skillproof-api.onrender.com`. You'll need it for the next steps.
- [ ] **[YOU]** Verify: `curl https://skillproof-api.onrender.com/health` returns `{"status":"ok"}`.

---

## 3. Frontend — Vercel

- [ ] **[YOU]** Go to [vercel.com](https://vercel.com) → New Project → Import `Rishhhaaabbb/skillproof`.
- [ ] **[YOU]** Set **Root Directory** to `skillproof-frontend`.
- [ ] **[YOU]** Set **Framework Preset**: Next.js (auto-detected).
- [ ] **[YOU]** Add environment variable in Vercel dashboard → Settings → Environment Variables:

  | Variable | Value |
  |---|---|
  | `NEXT_PUBLIC_API_URL` | Your Render backend URL, e.g. `https://skillproof-api.onrender.com` |

- [ ] **[YOU]** Deploy — wait for the build to succeed.
- [ ] **[YOU]** Note your Vercel URL, e.g. `https://skillproof.vercel.app`.

---

## 4. Lock CORS to Vercel URL — do this after both are deployed

- [ ] **[YOU]** In Render dashboard → Environment → update `CORS_ORIGINS` to your exact Vercel URL:
  ```
  https://skillproof.vercel.app
  ```
  If you have a custom domain too:
  ```
  https://skillproof.vercel.app,https://www.skillproof.app
  ```
- [ ] **[YOU]** Trigger a Render redeploy so the new CORS_ORIGINS takes effect.
- [ ] **[YOU]** Also update `vercel.json` → `rewrites[0].destination` and `env.NEXT_PUBLIC_API_URL` with the real Render URL, commit and push.

---

## 5. Update `vercel.json` with real Render URL

- [ ] Open `skillproof-frontend/vercel.json`.
- [ ] Replace every occurrence of `skillproof-api.onrender.com` with your actual Render service hostname.
- [ ] Commit and push — Vercel will redeploy automatically.

---

## 6. GitHub Actions Secrets

- [ ] **[YOU]** Go to GitHub repo → Settings → Secrets and variables → Actions → New repository secret.
- [ ] Add `BACKEND_URL` = `https://your-render-service.onrender.com` (no trailing slash).
- [ ] Add `SCHEDULER_SECRET` = same value you set on Render.
- [ ] **[YOU]** Manually trigger the workflow once: Actions → Weekly Re-analysis → Run workflow. Confirm it returns HTTP 200.

---

## 7. PWA Icons

- [ ] **[YOU]** Place a 512×512 PNG logo at `skillproof-frontend/public/icons/icon-source.png`.
- [ ] Run `npm install --save-dev sharp` inside `skillproof-frontend/`.
- [ ] Run `node scripts/generate-icons.mjs` to generate all icon sizes.
- [ ] Commit the generated `public/icons/*.png` files.

---

## 8. End-to-End Smoke Test (after everything is live)

Test each flow manually from a real phone browser:

- [ ] Sign up with a real GitHub username → confirm redirect to dashboard.
- [ ] Dashboard loads TPR score, trend chart, and flags.
- [ ] Add a target role with a real JD → click Analyze → gap analysis and verdict appear.
- [ ] Open an assigned task → verify its status card.
- [ ] Send a chat message → get a contextual response.
- [ ] Generate a share token → open the public URL in an incognito tab → recruiter view loads.
- [ ] Check notifications bell shows at least one entry after analysis.
- [ ] On Android Chrome: tap the browser menu → "Add to Home Screen" — SkillProof installs as a PWA.
- [ ] Test with a private GitHub profile → app shows a graceful error, not a 500.
- [ ] Test with a brand-new empty GitHub account → scores default to 0 gracefully.

---

## 9. Known Free-Tier Constraints

| Service | Limit | Mitigation |
|---|---|---|
| Render free web service | Spins down after 15 min inactivity | GitHub Actions warm-up job pings `/health` before scheduler runs |
| Supabase free tier | 500 MB storage, 2 GB egress/month | Sufficient for Phase 2 demo scale |
| Gemini free tier | 15 RPM / 1,500 RPD (flash model) | `USE_LLM_MOCK=true` for local dev; single analysis per user session |
| GitHub API unauthenticated | 60 req/hr | GITHUB_TOKEN raises limit to 5,000/hr |
| Vercel free tier | 100 GB bandwidth / month | Fine for demo |

---

## Quick-Reference: Generate Secrets Locally

```bash
python -c "import secrets; print('JWT_SECRET=', secrets.token_hex(32))"
python -c "import secrets; print('JWT_REFRESH_SECRET=', secrets.token_hex(32))"
python -c "import secrets; print('SCHEDULER_SECRET=', secrets.token_hex(32))"
```
