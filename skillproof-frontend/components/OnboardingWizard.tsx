'use client'
import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'
import {
  GitBranch, Zap, Target, CheckCircle2, ArrowRight,
  ArrowLeft, Loader2, AlertCircle, SkipForward,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import api from '@/lib/api'
import { useJobPoller } from '@/lib/hooks/useJobPoller'
import type { JobStatus, User } from '@/lib/types'
import { cn } from '@/lib/utils'

// ---------------------------------------------------------------------------
// Step config
// ---------------------------------------------------------------------------
const STEPS = [
  { id: 1, label: 'GitHub',   icon: GitBranch },
  { id: 2, label: 'Analysis', icon: Zap       },
  { id: 3, label: 'First Role', icon: Target   },
]

// Analysis progress messages — cycle through while job runs
const ANALYSIS_STEPS = [
  { text: 'Fetching GitHub data',   icon: GitBranch },
  { text: 'Extracting features',    icon: Zap       },
  { text: 'Scoring behaviour',      icon: Zap       },
  { text: 'Generating insights',    icon: CheckCircle2 },
]

interface OnboardingWizardProps {
  onComplete?: () => void
}

// ---------------------------------------------------------------------------
// Progress bar
// ---------------------------------------------------------------------------
function ProgressBar({ step, total }: { step: number; total: number }) {
  const pct = ((step - 1) / (total - 1)) * 100
  return (
    <div className="mb-8">
      <div className="mb-3 flex items-center justify-between text-xs text-muted-foreground">
        {STEPS.map((s) => (
          <div key={s.id} className={cn(
            'flex items-center gap-1 transition-colors',
            step >= s.id ? 'text-primary font-medium' : 'text-muted-foreground',
          )}>
            <div className={cn(
              'flex h-5 w-5 items-center justify-center rounded-full border text-[10px] font-bold transition-all',
              step > s.id
                ? 'border-primary bg-primary text-primary-foreground'
                : step === s.id
                  ? 'border-primary text-primary'
                  : 'border-border text-muted-foreground',
            )}>
              {step > s.id ? <CheckCircle2 className="h-3 w-3" /> : s.id}
            </div>
            <span className="hidden sm:inline">{s.label}</span>
          </div>
        ))}
      </div>
      <div className="h-1.5 overflow-hidden rounded-full bg-muted">
        <div
          className="h-full rounded-full bg-primary transition-all duration-500"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Step 1 — GitHub username confirm
// ---------------------------------------------------------------------------
function Step1GitHub({
  initialUsername,
  onNext,
}: {
  initialUsername: string
  onNext: (username: string) => void
}) {
  const [username, setUsername] = useState(initialUsername)
  const [repoCount, setRepoCount] = useState<number | null>(null)
  const [checking, setChecking] = useState(false)
  const [checkError, setCheckError] = useState<string | null>(null)
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const [saving, setSaving] = useState(false)

  // Debounce preview fetch
  useEffect(() => {
    if (!username.trim()) { setRepoCount(null); setCheckError(null); return }
    if (debounceRef.current) clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(async () => {
      setChecking(true)
      setCheckError(null)
      setRepoCount(null)
      try {
        const res = await fetch(`https://api.github.com/users/${username.trim()}`)
        if (!res.ok) throw new Error('User not found')
        const data = await res.json()
        setRepoCount(data.public_repos)
      } catch {
        setCheckError('GitHub user not found. Check the username.')
      } finally {
        setChecking(false)
      }
    }, 600)
    return () => { if (debounceRef.current) clearTimeout(debounceRef.current) }
  }, [username])

  async function handleNext() {
    if (!username.trim() || checkError) return
    setSaving(true)
    try {
      await api.patch('/api/settings', { github_username: username.trim() })
    } catch { /* best-effort */ }
    setSaving(false)
    onNext(username.trim())
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h2 className="text-xl font-bold">Confirm your GitHub username</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          We use your public GitHub activity to calculate your readiness score.
        </p>
      </div>

      <div className="flex flex-col gap-2">
        <label htmlFor="github_username" className="text-sm font-medium">
          GitHub username
        </label>
        <div className="relative">
          <div className="pointer-events-none absolute inset-y-0 left-3 flex items-center">
            <GitBranch className="h-4 w-4 text-muted-foreground" />
          </div>
          <input
            id="github_username"
            type="text"
            value={username}
            onChange={e => setUsername(e.target.value)}
            placeholder="your-github-handle"
            className="h-10 w-full rounded-lg border border-border bg-background pl-9 pr-4 text-sm outline-none focus:border-ring focus:ring-2 focus:ring-ring/20"
          />
          {checking && (
            <div className="absolute inset-y-0 right-3 flex items-center">
              <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
            </div>
          )}
        </div>

        {/* Preview */}
        {repoCount !== null && !checkError && (
          <div className="flex items-center gap-2 rounded-lg border border-emerald-500/20 bg-emerald-500/8 px-3 py-2 text-sm text-emerald-600 dark:text-emerald-400">
            <CheckCircle2 className="h-4 w-4 shrink-0" />
            Found! <span className="font-semibold">{repoCount}</span> public repositories
          </div>
        )}
        {checkError && (
          <div className="flex items-center gap-2 rounded-lg border border-destructive/30 bg-destructive/8 px-3 py-2 text-sm text-destructive">
            <AlertCircle className="h-4 w-4 shrink-0" />
            {checkError}
          </div>
        )}
      </div>

      <Button
        onClick={handleNext}
        disabled={!username.trim() || !!checkError || checking || saving}
        className="gap-2"
      >
        {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
        Continue
        <ArrowRight className="h-4 w-4" />
      </Button>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Step 2 — Run first analysis
// ---------------------------------------------------------------------------
function Step2Analysis({ onNext }: { onNext: () => void }) {
  const [jobId, setJobId] = useState<string | null>(null)
  const [starting, setStarting] = useState(false)
  const [startError, setStartError] = useState<string | null>(null)
  const [stepIdx, setStepIdx] = useState(0)

  const { status: jobStatus } = useJobPoller(jobId)
  const isRunning = jobStatus === 'queued' || jobStatus === 'processing'
  const isDone = jobStatus === 'complete'
  const isFailed = jobStatus === 'failed'

  // Cycle through progress labels
  useEffect(() => {
    if (!isRunning) return
    const t = setInterval(() => {
      setStepIdx(i => Math.min(i + 1, ANALYSIS_STEPS.length - 1))
    }, 2500)
    return () => clearInterval(t)
  }, [isRunning])

  async function startAnalysis() {
    setStarting(true)
    setStartError(null)
    setStepIdx(0)
    try {
      const job = await api.post<JobStatus>('/api/analysis/trigger')
      setJobId(job.id)
    } catch (err: any) {
      setStartError(err?.response?.data?.detail ?? 'Failed to start analysis')
    } finally {
      setStarting(false)
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h2 className="text-xl font-bold">Run your first analysis</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          We'll scan your GitHub activity and calculate your developer readiness score.
          Takes about 30–60 seconds.
        </p>
      </div>

      {startError && (
        <div className="flex items-center gap-2 rounded-lg border border-destructive/30 bg-destructive/8 px-3 py-2 text-sm text-destructive">
          <AlertCircle className="h-4 w-4 shrink-0" />
          {startError}
        </div>
      )}

      {/* Progress steps */}
      <div className="flex flex-col gap-2">
        {ANALYSIS_STEPS.map((s, i) => {
          const Icon = s.icon
          const isActive = isRunning && i === stepIdx
          const isComplete = isDone || (isRunning && i < stepIdx)
          return (
            <div
              key={i}
              className={cn(
                'flex items-center gap-3 rounded-lg border px-4 py-3 transition-all duration-300',
                isActive && 'border-primary/30 bg-primary/8',
                isComplete && 'border-emerald-500/20 bg-emerald-500/5',
                !isActive && !isComplete && 'border-border/40 opacity-50',
              )}
            >
              <div className={cn(
                'flex h-6 w-6 shrink-0 items-center justify-center rounded-full',
                isComplete ? 'bg-emerald-500/20' : isActive ? 'bg-primary/15' : 'bg-muted',
              )}>
                {isComplete
                  ? <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
                  : isActive
                    ? <Loader2 className="h-3.5 w-3.5 animate-spin text-primary" />
                    : <Icon className="h-3.5 w-3.5 text-muted-foreground" />
                }
              </div>
              <span className={cn(
                'text-sm',
                isComplete && 'font-medium text-emerald-600 dark:text-emerald-400',
                isActive && 'font-medium text-primary',
              )}>
                {s.text}
              </span>
            </div>
          )
        })}
      </div>

      {/* Action area */}
      {!jobId && !isDone && (
        <Button onClick={startAnalysis} disabled={starting} size="lg" className="gap-2">
          {starting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Zap className="h-4 w-4" />}
          {starting ? 'Starting…' : 'Run analysis'}
        </Button>
      )}

      {isFailed && (
        <div className="flex flex-col gap-3">
          <div className="flex items-center gap-2 rounded-lg border border-destructive/30 bg-destructive/8 px-3 py-2 text-sm text-destructive">
            <AlertCircle className="h-4 w-4 shrink-0" />
            Analysis failed. Make sure your GitHub username is correct in the previous step.
          </div>
          <Button variant="outline" onClick={startAnalysis} className="gap-2">
            <Zap className="h-4 w-4" />
            Try again
          </Button>
        </div>
      )}

      {isDone && (
        <div className="flex flex-col gap-4">
          <div className="flex items-center gap-2 rounded-xl border border-emerald-500/20 bg-emerald-500/8 px-4 py-3 text-sm font-medium text-emerald-600 dark:text-emerald-400">
            <CheckCircle2 className="h-4 w-4 shrink-0" />
            Analysis complete! Your readiness score is ready.
          </div>
          <Button onClick={onNext} size="lg" className="gap-2">
            Continue
            <ArrowRight className="h-4 w-4" />
          </Button>
        </div>
      )}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Step 3 — Add first target role (optional)
// ---------------------------------------------------------------------------
function Step3Role({ onComplete }: { onComplete: () => void }) {
  const [roleTitle, setRoleTitle] = useState('')
  const [companyName, setCompanyName] = useState('')
  const [jdText, setJdText] = useState('')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const inputCls = 'h-9 w-full rounded-lg border border-border bg-background px-3 text-sm outline-none focus:border-ring focus:ring-2 focus:ring-ring/20 placeholder:text-muted-foreground/50'

  async function handleAdd() {
    if (!roleTitle.trim() || !jdText.trim()) return
    setSaving(true)
    setError(null)
    try {
      await api.post('/api/target-roles', {
        role_title: roleTitle.trim(),
        company_name: companyName.trim() || undefined,
        jd_text: jdText.trim(),
      })
      onComplete()
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? 'Failed to create role')
      setSaving(false)
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h2 className="text-xl font-bold">Add your first target role</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Paste a job description and we'll analyse your readiness for it. You can skip this and add roles later.
        </p>
      </div>

      {error && (
        <div className="flex items-center gap-2 rounded-lg border border-destructive/30 bg-destructive/8 px-3 py-2 text-sm text-destructive">
          <AlertCircle className="h-4 w-4 shrink-0" />{error}
        </div>
      )}

      <div className="flex flex-col gap-4">
        <div className="flex flex-col gap-1.5">
          <label className="text-sm font-medium">
            Role title <span className="text-destructive">*</span>
          </label>
          <input
            type="text"
            value={roleTitle}
            onChange={e => setRoleTitle(e.target.value)}
            placeholder="e.g. Senior Frontend Engineer"
            className={inputCls}
          />
        </div>

        <div className="flex flex-col gap-1.5">
          <label className="text-sm font-medium">Company name</label>
          <input
            type="text"
            value={companyName}
            onChange={e => setCompanyName(e.target.value)}
            placeholder="e.g. Acme Corp"
            className={inputCls}
          />
        </div>

        <div className="flex flex-col gap-1.5">
          <label className="text-sm font-medium">
            Job description <span className="text-destructive">*</span>
          </label>
          <textarea
            rows={8}
            value={jdText}
            onChange={e => setJdText(e.target.value)}
            placeholder="Paste the full job posting here…"
            className="w-full resize-none rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none placeholder:text-muted-foreground/50 focus:border-ring focus:ring-2 focus:ring-ring/20"
          />
          <p className="text-xs text-muted-foreground">
            The more detail, the more accurate the gap analysis.
          </p>
        </div>
      </div>

      <div className="flex flex-col gap-2">
        <Button
          onClick={handleAdd}
          disabled={!roleTitle.trim() || !jdText.trim() || saving}
          size="lg"
          className="gap-2"
        >
          {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Target className="h-4 w-4" />}
          {saving ? 'Adding…' : 'Add role and go to dashboard'}
        </Button>
        <Button
          variant="ghost"
          onClick={onComplete}
          className="gap-2 text-muted-foreground"
        >
          <SkipForward className="h-4 w-4" />
          Skip for now
        </Button>
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Main wizard
// ---------------------------------------------------------------------------
export default function OnboardingWizard({ onComplete }: OnboardingWizardProps) {
  const router = useRouter()
  const [step, setStep] = useState(1)
  const [githubUsername, setGithubUsername] = useState('')

  // Pre-fill GitHub username from the logged-in user
  useEffect(() => {
    api.get<User>('/auth/me')
      .then(u => setGithubUsername(u.github_username ?? ''))
      .catch(() => {})
  }, [])

  function handleComplete() {
    if (onComplete) {
      onComplete()
    } else {
      router.replace('/dashboard')
    }
  }

  return (
    <div className="mx-auto w-full max-w-lg px-4">
      <ProgressBar step={step} total={STEPS.length} />

      {/* Step back button (steps 2+) */}
      {step > 1 && step < 3 && (
        <button
          onClick={() => setStep(s => s - 1)}
          className="mb-4 flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          Back
        </button>
      )}

      {/* Steps */}
      {step === 1 && (
        <Step1GitHub
          initialUsername={githubUsername}
          onNext={(u) => { setGithubUsername(u); setStep(2) }}
        />
      )}
      {step === 2 && (
        <Step2Analysis onNext={() => setStep(3)} />
      )}
      {step === 3 && (
        <Step3Role onComplete={handleComplete} />
      )}
    </div>
  )
}
