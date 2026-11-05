'use client'
import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import {
  ShieldCheck, GitBranch, Flame, Trophy, Star, Zap,
  GitCommit, Users, CheckCircle2, TrendingUp, Send,
  Loader2, AlertCircle, ExternalLink,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { cn } from '@/lib/utils'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------
interface PublicProfile {
  candidate_name: string
  github_username?: string
  profile_headline?: string
  tpr_score: number
  tier_label: 'Strong' | 'Developing' | 'Early Stage'
  top_strengths: string[]
  skill_tags: { tag: string; source?: string }[]
  milestones: { label: string; key: string }[]
  current_streak: number
  share_token: string
}

// ---------------------------------------------------------------------------
// Tier config
// ---------------------------------------------------------------------------
const TIER = {
  Strong: {
    label: 'Strong',
    color: 'text-emerald-700 dark:text-emerald-400',
    bg: 'bg-emerald-500/10 border-emerald-500/30',
    ring: '#10b981',
  },
  Developing: {
    label: 'Developing',
    color: 'text-amber-700 dark:text-amber-400',
    bg: 'bg-amber-500/10 border-amber-500/30',
    ring: '#f59e0b',
  },
  'Early Stage': {
    label: 'Early Stage',
    color: 'text-blue-700 dark:text-blue-400',
    bg: 'bg-blue-500/10 border-blue-500/30',
    ring: '#6366f1',
  },
}

// ---------------------------------------------------------------------------
// Milestone icon map
// ---------------------------------------------------------------------------
const MILESTONE_ICONS: Record<string, React.ElementType> = {
  account_created: Star,
  first_analysis: Zap,
  streak_7: Flame,
  streak_30: Flame,
  pr_master: GitCommit,
  review_contributor: Users,
  task_complete: CheckCircle2,
  score_70: TrendingUp,
}

// ---------------------------------------------------------------------------
// Circular gauge (same SVG arc approach as detail page)
// ---------------------------------------------------------------------------
function ScoreGauge({ score, color }: { score: number; color: string }) {
  const size = 180
  const sw = 12
  const r = (size - sw) / 2 - 4
  const cx = size / 2
  const cy = size / 2 + 12
  const arcLen = Math.PI * r
  const progress = (score / 100) * arcLen

  return (
    <div className="relative mx-auto" style={{ width: size, height: size / 2 + 40 }}>
      <svg width={size} height={size / 2 + 40} overflow="visible">
        <path
          d={`M ${cx - r} ${cy} A ${r} ${r} 0 0 1 ${cx + r} ${cy}`}
          fill="none" stroke="hsl(var(--border))" strokeWidth={sw}
          strokeLinecap="round" opacity={0.2}
        />
        <path
          d={`M ${cx - r} ${cy} A ${r} ${r} 0 0 1 ${cx + r} ${cy}`}
          fill="none" stroke={color} strokeWidth={sw}
          strokeLinecap="round"
          strokeDasharray={`${progress} ${arcLen}`}
          style={{ transition: 'stroke-dasharray 0.8s ease' }}
        />
      </svg>
      <div className="absolute bottom-0 left-1/2 -translate-x-1/2 flex flex-col items-center">
        <p className="text-5xl font-bold tabular-nums" style={{ color }}>{Math.round(score)}</p>
        <p className="text-sm text-muted-foreground">/ 100</p>
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Connect request form
// ---------------------------------------------------------------------------
interface ConnectFormProps { token: string }

function ConnectForm({ token }: ConnectFormProps) {
  const [form, setForm] = useState({
    recruiter_name: '',
    recruiter_email: '',
    recruiter_company: '',
    message: '',
  })
  const [submitting, setSubmitting] = useState(false)
  const [submitted, setSubmitted] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const field = (id: keyof typeof form) => ({
    id,
    value: form[id],
    onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
      setForm(prev => ({ ...prev, [id]: e.target.value })),
  })

  const inputCls = 'h-9 w-full rounded-lg border border-border bg-background/60 px-3 text-sm outline-none transition-colors placeholder:text-muted-foreground/50 focus:border-ring focus:ring-2 focus:ring-ring/20'

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!form.recruiter_name.trim() || !form.recruiter_email.trim()) return
    setSubmitting(true)
    setError(null)
    try {
      const res = await fetch(`${API_BASE}/api/share/${token}/request`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          recruiter_name: form.recruiter_name.trim(),
          recruiter_email: form.recruiter_email.trim(),
          recruiter_company: form.recruiter_company.trim() || undefined,
          message: form.message.trim() || undefined,
        }),
      })
      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data?.detail ?? 'Failed to send request')
      }
      setSubmitted(true)
    } catch (err: any) {
      setError(err.message ?? 'Something went wrong. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  if (submitted) {
    return (
      <div className="flex flex-col items-center gap-3 py-8 text-center">
        <div className="flex h-12 w-12 items-center justify-center rounded-full bg-emerald-500/10">
          <CheckCircle2 className="h-6 w-6 text-emerald-500" />
        </div>
        <p className="text-lg font-semibold">Request sent!</p>
        <p className="text-sm text-muted-foreground">
          The candidate has been notified. They'll reach out if they're interested.
        </p>
      </div>
    )
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      {error && (
        <div className="flex items-center gap-2 rounded-lg border border-destructive/30 bg-destructive/8 px-3 py-2 text-sm text-destructive">
          <AlertCircle className="h-4 w-4 shrink-0" />{error}
        </div>
      )}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div className="flex flex-col gap-1.5">
          <label htmlFor="recruiter_name" className="text-sm font-medium">
            Your name <span className="text-destructive">*</span>
          </label>
          <input {...field('recruiter_name')} type="text" placeholder="Jane Smith" className={inputCls} />
        </div>
        <div className="flex flex-col gap-1.5">
          <label htmlFor="recruiter_email" className="text-sm font-medium">
            Your email <span className="text-destructive">*</span>
          </label>
          <input {...field('recruiter_email')} type="email" placeholder="jane@company.com" className={inputCls} />
        </div>
      </div>

      <div className="flex flex-col gap-1.5">
        <label htmlFor="recruiter_company" className="text-sm font-medium">Company</label>
        <input {...field('recruiter_company')} type="text" placeholder="Acme Corp" className={inputCls} />
      </div>

      <div className="flex flex-col gap-1.5">
        <label htmlFor="message" className="text-sm font-medium">Message</label>
        <textarea
          {...field('message')}
          rows={3}
          placeholder="Tell the candidate about the opportunity..."
          className="w-full resize-none rounded-lg border border-border bg-background/60 px-3 py-2 text-sm outline-none placeholder:text-muted-foreground/50 focus:border-ring focus:ring-2 focus:ring-ring/20"
        />
      </div>

      <Button
        type="submit"
        disabled={submitting || !form.recruiter_name.trim() || !form.recruiter_email.trim()}
        className="gap-2"
      >
        {submitting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
        {submitting ? 'Sending…' : 'Send connection request'}
      </Button>
    </form>
  )
}

// ---------------------------------------------------------------------------
// API base for unauthenticated calls — uses Next.js rewrite proxy (/api/...)
// which forwards to the backend. Falls back to direct backend URL in dev
// if NEXT_PUBLIC_API_URL is set.
// ---------------------------------------------------------------------------
const API_BASE =
  typeof window !== 'undefined'
    ? (process.env.NEXT_PUBLIC_API_URL ?? '')   // '' = relative = uses Next.js rewrite
    : (process.env.NEXT_PUBLIC_API_URL ?? '')

// ---------------------------------------------------------------------------
// Main public profile page
// ---------------------------------------------------------------------------
export default function SharedProfilePage() {
  const params = useParams()
  const token = params.token as string

  const [profile, setProfile] = useState<PublicProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [notFound, setNotFound] = useState(false)

  useEffect(() => {
    fetch(`${API_BASE}/api/share/${token}`)
      .then(async (res) => {
        if (!res.ok) { setNotFound(true); return }
        const data = await res.json()
        setProfile(data)
      })
      .catch(() => setNotFound(true))
      .finally(() => setLoading(false))
  }, [token])

  // ── Loading skeleton ──
  if (loading) {
    return (
      <div className="min-h-screen bg-background">
        <div className="mx-auto max-w-2xl px-4 py-12">
          <div className="flex flex-col items-center gap-6">
            <Skeleton className="h-12 w-48" />
            <Skeleton className="h-6 w-32" />
            <Skeleton className="h-24 w-24 rounded-full" />
            <Skeleton className="h-48 w-full rounded-2xl" />
            <Skeleton className="h-32 w-full rounded-2xl" />
          </div>
        </div>
      </div>
    )
  }

  // ── Not found ──
  if (notFound || !profile) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center bg-background px-4 text-center">
        <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-muted">
          <ShieldCheck className="h-7 w-7 text-muted-foreground" />
        </div>
        <h1 className="mt-4 text-xl font-bold">Profile not found</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          This share link is invalid, expired, or has been revoked.
        </p>
      </div>
    )
  }

  const tier = TIER[profile.tier_label] ?? TIER['Developing']

  return (
    <div className="min-h-screen bg-background">
      {/* ── Top bar branding ── */}
      <div className="border-b border-border/60 bg-card/80 backdrop-blur-sm">
        <div className="mx-auto flex max-w-2xl items-center justify-between px-4 py-3">
          <div className="flex items-center gap-2">
            <ShieldCheck className="h-5 w-5 text-primary" />
            <span className="text-sm font-bold">SkillProof</span>
          </div>
          <p className="text-xs text-muted-foreground">Developer Readiness Profile</p>
        </div>
      </div>

      <div className="mx-auto max-w-2xl px-4 py-10 sm:px-6">
        <div className="flex flex-col gap-6">

          {/* ── Hero ── */}
          <div className="flex flex-col items-center gap-3 text-center">
            {/* Avatar initial */}
            <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10 text-2xl font-bold text-primary">
              {(profile.candidate_name || profile.github_username || '?').charAt(0).toUpperCase()}
            </div>

            <div>
              <h1 className="text-2xl font-bold tracking-tight">
                {profile.candidate_name || profile.github_username}
              </h1>
              {profile.profile_headline && (
                <p className="mt-1 text-sm text-muted-foreground">{profile.profile_headline}</p>
              )}
              {profile.github_username && (
                <a
                  href={`https://github.com/${profile.github_username}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="mt-2 inline-flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground"
                >
                  <GitBranch className="h-3.5 w-3.5" />
                  {profile.github_username}
                  <ExternalLink className="h-3 w-3" />
                </a>
              )}
            </div>

            {/* Tier badge */}
            <span className={cn(
              'inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-semibold',
              tier.bg, tier.color,
            )}>
              <ShieldCheck className="h-3.5 w-3.5" />
              {tier.label} Developer
            </span>
          </div>

          {/* ── TPR Score Gauge ── */}
          <div className="rounded-2xl border border-border/60 bg-card px-6 py-8 text-center shadow-sm">
            <p className="mb-1 text-xs font-semibold uppercase tracking-widest text-muted-foreground">
              TPR Readiness Score
            </p>
            <ScoreGauge score={profile.tpr_score} color={tier.ring} />
            <p className="mt-3 text-sm text-muted-foreground">
              {profile.tpr_score >= 80
                ? 'Exceptional signal — ready to contribute immediately.'
                : profile.tpr_score >= 65
                ? 'Strong profile — proven engineering habits.'
                : profile.tpr_score >= 40
                ? 'Developing — building consistent engineering practices.'
                : 'Early stage — growing their GitHub presence.'}
            </p>
          </div>

          {/* ── Top Strengths ── */}
          {profile.top_strengths.length > 0 && (
            <div className="rounded-2xl border border-border/60 bg-card p-6 shadow-sm">
              <p className="mb-4 text-xs font-semibold uppercase tracking-widest text-muted-foreground">
                Top Strengths
              </p>
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
                {profile.top_strengths.map((s, i) => (
                  <div
                    key={i}
                    className="flex items-start gap-2 rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-3"
                  >
                    <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-500" />
                    <p className="text-sm leading-snug">{s}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* ── Skill Tags ── */}
          {profile.skill_tags.length > 0 && (
            <div className="rounded-2xl border border-border/60 bg-card p-6 shadow-sm">
              <p className="mb-4 text-xs font-semibold uppercase tracking-widest text-muted-foreground">
                Verified Skills
              </p>
              <div className="flex flex-wrap gap-2">
                {profile.skill_tags.map((t, i) => (
                  <span
                    key={i}
                    className="rounded-full border border-border/60 bg-muted/40 px-3 py-1 text-xs font-medium"
                  >
                    {t.tag}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* ── Streak + Milestones row ── */}
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            {/* Streak */}
            <div className="flex flex-col items-center gap-2 rounded-2xl border border-border/60 bg-card py-6 shadow-sm">
              <Flame className="h-8 w-8 text-orange-400" />
              <p className="text-3xl font-bold tabular-nums">{profile.current_streak}</p>
              <p className="text-xs text-muted-foreground">Day Streak</p>
            </div>

            {/* Milestones */}
            <div className="rounded-2xl border border-border/60 bg-card p-5 shadow-sm">
              <p className="mb-3 text-xs font-semibold uppercase tracking-widest text-muted-foreground">
                Milestones
              </p>
              {profile.milestones.length === 0 ? (
                <p className="text-xs text-muted-foreground">No milestones yet.</p>
              ) : (
                <div className="flex flex-wrap gap-2">
                  {profile.milestones.map((m, i) => {
                    const Icon = MILESTONE_ICONS[m.key] ?? Trophy
                    return (
                      <div
                        key={i}
                        title={m.label}
                        className="flex items-center gap-1.5 rounded-full border border-border/60 bg-muted/30 px-2.5 py-1"
                      >
                        <Icon className="h-3 w-3 text-amber-400" />
                        <span className="text-xs font-medium">{m.label}</span>
                      </div>
                    )
                  })}
                </div>
              )}
            </div>
          </div>

          {/* ── Connect form ── */}
          <div className="rounded-2xl border border-border/60 bg-card p-6 shadow-sm">
            <div className="mb-5 flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-primary/10">
                <Send className="h-4 w-4 text-primary" />
              </div>
              <div>
                <p className="text-sm font-semibold">Request to Connect</p>
                <p className="text-xs text-muted-foreground">
                  Interested in this candidate? Send them a message.
                </p>
              </div>
            </div>
            <ConnectForm token={token} />
          </div>

          {/* Footer */}
          <div className="flex items-center justify-center gap-2 pt-2 pb-8">
            <ShieldCheck className="h-4 w-4 text-muted-foreground/40" />
            <p className="text-xs text-muted-foreground/40">
              Verified by SkillProof · GitHub Behavioral Analysis
            </p>
          </div>

        </div>
      </div>
    </div>
  )
}
