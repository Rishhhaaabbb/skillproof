'use client'
import { useEffect, useState, useCallback } from 'react'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts'
import {
  RefreshCw, BarChart2, Loader2, CheckCircle2, AlertCircle, Zap,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import TPRScoreCard from '@/components/TPRScoreCard'
import LRScoreCard from '@/components/LRScoreCard'
import StreakCounter from '@/components/StreakCounter'
import ActivityHeatmap from '@/components/ActivityHeatmap'
import SkillRadarChart from '@/components/SkillRadarChart'
import MilestoneBadges from '@/components/MilestoneBadges'
import { useJobPoller } from '@/lib/hooks/useJobPoller'
import api from '@/lib/api'
import type { Analysis, JobStatus, Milestone, User } from '@/lib/types'
import { cn } from '@/lib/utils'

interface HistoryPoint { tpr_score: number; created_at: string }

const ANALYSIS_STEPS = [
  'Fetching GitHub data',
  'Extracting features',
  'Scoring behaviour',
  'Generating insights',
]

export default function DashboardPage() {
  const [analysis, setAnalysis] = useState<Analysis | null>(null)
  const [history, setHistory] = useState<HistoryPoint[]>([])
  const [milestones, setMilestones] = useState<Milestone[]>([])
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Job polling state
  const [jobId, setJobId] = useState<string | null>(null)
  const [analysisStep, setAnalysisStep] = useState(0)
  const { status: jobStatus, result: jobResult } = useJobPoller(jobId)

  const fetchData = useCallback(async () => {
    try {
      const [analysisData, historyData, milestonesData, userData] = await Promise.allSettled([
        api.get<Analysis>('/api/analysis/latest'),
        api.get<HistoryPoint[]>('/api/analysis/history'),
        api.get<Milestone[]>('/api/analysis/streaks').then((r: unknown) => {
          const d = r as { milestones?: Milestone[] }
          return d?.milestones ?? []
        }),
        api.get<User>('/auth/me'),
      ])

      if (analysisData.status === 'fulfilled') setAnalysis(analysisData.value)
      if (historyData.status === 'fulfilled') setHistory(historyData.value)
      if (milestonesData.status === 'fulfilled') setMilestones(milestonesData.value)
      if (userData.status === 'fulfilled') setUser(userData.value)
    } catch {
      setError('Failed to load dashboard data')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchData() }, [fetchData])

  // Cycle through analysis steps while job is processing
  useEffect(() => {
    if (jobStatus === 'processing' || jobStatus === 'queued') {
      const t = setInterval(() => {
        setAnalysisStep(s => (s + 1) % ANALYSIS_STEPS.length)
      }, 2200)
      return () => clearInterval(t)
    }
  }, [jobStatus])

  // Job completed — refresh data
  useEffect(() => {
    if (jobStatus === 'complete') {
      setJobId(null)
      fetchData()
    }
  }, [jobStatus, jobResult, fetchData])

  async function runAnalysis() {
    if (jobId) return
    setAnalysisStep(0)
    try {
      const job = await api.post<JobStatus>('/api/analysis/trigger')
      setJobId(job.id)
    } catch {
      setError('Failed to start analysis. Check your GitHub username in Settings.')
    }
  }

  const isRunning = jobStatus === 'queued' || jobStatus === 'processing'
  const flags = analysis?.flags as { green_flags?: string[]; red_flags?: string[] } | undefined
  const totalAnalyses = history.length

  // Chart data
  const chartData = history.slice(-20).map((h, i) => ({
    name: i + 1,
    score: h.tpr_score,
    date: new Date(h.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
  }))

  return (
    <div className="flex flex-col gap-6 p-6 pb-10">
      {/* ── Header ── */}
      <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">
            {user?.full_name ? `Hey, ${user.full_name.split(' ')[0]} 👋` : 'Dashboard'}
          </h1>
          <p className="text-sm text-muted-foreground">
            Your developer readiness at a glance
          </p>
        </div>

        <div className="flex items-center gap-2">
          {isRunning && (
            <div className="flex items-center gap-2 rounded-lg border border-border/60 bg-card px-3 py-1.5 text-xs">
              <Loader2 className="h-3.5 w-3.5 animate-spin text-primary" />
              <span className="text-muted-foreground">{ANALYSIS_STEPS[analysisStep]}…</span>
            </div>
          )}
          {jobStatus === 'complete' && (
            <div className="flex items-center gap-1.5 rounded-lg border border-emerald-500/20 bg-emerald-500/10 px-3 py-1.5 text-xs text-emerald-500">
              <CheckCircle2 className="h-3.5 w-3.5" />
              Analysis complete
            </div>
          )}
          {jobStatus === 'failed' && (
            <div className="flex items-center gap-1.5 rounded-lg border border-destructive/20 bg-destructive/10 px-3 py-1.5 text-xs text-destructive">
              <AlertCircle className="h-3.5 w-3.5" />
              Analysis failed
            </div>
          )}
          <Button
            onClick={runAnalysis}
            disabled={isRunning}
            size="sm"
            className="gap-1.5"
          >
            {isRunning ? (
              <Loader2 className="h-3.5 w-3.5 animate-spin" />
            ) : (
              <Zap className="h-3.5 w-3.5" />
            )}
            {isRunning ? 'Analyzing…' : 'Run Analysis'}
          </Button>
        </div>
      </div>

      {/* ── Error ── */}
      {error && (
        <div className="flex items-center gap-2 rounded-lg border border-destructive/30 bg-destructive/8 px-4 py-3 text-sm text-destructive">
          <AlertCircle className="h-4 w-4 shrink-0" />
          {error}
        </div>
      )}

      {/* ── Top stats row ── */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <TPRScoreCard
          tprScore={analysis?.tpr_score}
          confidence={analysis?.confidence_level}
          isLoading={loading}
        />
        <LRScoreCard
          lrScore={analysis?.lr_score ?? undefined}
          confidenceLevel={analysis?.confidence_level ?? undefined}
          isLoading={loading}
        />
        <StreakCounter
          currentStreak={user?.current_streak}
          longestStreak={user?.longest_streak}
          isLoading={loading}
        />
        {/* Total analyses card */}
        {loading ? (
          <div className="flex flex-col gap-3 rounded-xl border border-border/60 bg-card p-5">
            <div className="h-4 w-24 animate-pulse rounded bg-muted" />
            <div className="h-8 w-12 animate-pulse rounded bg-muted" />
          </div>
        ) : (
          <div className="flex flex-col gap-2 rounded-xl border border-border/60 bg-card p-5">
            <div className="flex items-center gap-1.5">
              <BarChart2 className="h-3.5 w-3.5 text-muted-foreground" />
              <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Analyses</p>
            </div>
            <p className="text-3xl font-bold tabular-nums">{totalAnalyses}</p>
            <p className="text-xs text-muted-foreground">total runs</p>
          </div>
        )}
      </div>

      {/* ── Main two-column layout ── */}
      <div className="grid grid-cols-1 gap-4 xl:grid-cols-5">
        {/* Left column — heatmap + trend chart */}
        <div className="flex flex-col gap-4 xl:col-span-3">
          <ActivityHeatmap
            heatmapData={analysis?.heatmap_data ?? undefined}
            isLoading={loading}
          />

          {/* TPR trend line chart */}
          <div className="rounded-xl border border-border/60 bg-card p-5">
            <p className="mb-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">
              TPR Score Trend
            </p>
            {loading ? (
              <Skeleton className="h-48 w-full" />
            ) : chartData.length < 2 ? (
              <div className="flex h-48 items-center justify-center text-sm text-muted-foreground">
                Run at least 2 analyses to see your trend
              </div>
            ) : (
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={chartData} margin={{ top: 5, right: 10, bottom: 5, left: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.4} />
                  <XAxis dataKey="date" tick={{ fontSize: 11 }} stroke="hsl(var(--muted-foreground))" />
                  <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} stroke="hsl(var(--muted-foreground))" />
                  <Tooltip
                    contentStyle={{
                      background: 'hsl(var(--card))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px',
                      fontSize: '12px',
                    }}
                    formatter={(v: number) => [`${v}/100`, 'TPR Score']}
                  />
                  <Line
                    type="monotone"
                    dataKey="score"
                    stroke="#6366f1"
                    strokeWidth={2}
                    dot={{ r: 3, fill: '#6366f1' }}
                    activeDot={{ r: 5 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* Right column — radar + milestones */}
        <div className="flex flex-col gap-4 xl:col-span-2">
          <SkillRadarChart
            breakdown={analysis?.breakdown ?? undefined}
            isLoading={loading}
          />
          <MilestoneBadges milestones={milestones} isLoading={loading} />
        </div>
      </div>

      {/* ── Flags section ── */}
      {(flags?.green_flags?.length || flags?.red_flags?.length) ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          {/* Green flags */}
          {(flags?.green_flags?.length ?? 0) > 0 && (
            <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-5">
              <p className="mb-3 text-xs font-semibold uppercase tracking-wider text-emerald-500">
                ✓ Strengths
              </p>
              <div className="flex flex-wrap gap-2">
                {flags?.green_flags?.map((f, i) => (
                  <span
                    key={i}
                    className="rounded-full border border-emerald-500/20 bg-emerald-500/10 px-3 py-1 text-xs font-medium text-emerald-600 dark:text-emerald-400"
                  >
                    {f}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Red flags */}
          {(flags?.red_flags?.length ?? 0) > 0 && (
            <div className="rounded-xl border border-red-500/20 bg-red-500/5 p-5">
              <p className="mb-3 text-xs font-semibold uppercase tracking-wider text-red-500">
                ✗ Gaps to close
              </p>
              <div className="flex flex-wrap gap-2">
                {flags?.red_flags?.map((f, i) => (
                  <span
                    key={i}
                    className="rounded-full border border-red-500/20 bg-red-500/10 px-3 py-1 text-xs font-medium text-red-600 dark:text-red-400"
                  >
                    {f}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      ) : loading ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Skeleton className="h-24 w-full rounded-xl" />
          <Skeleton className="h-24 w-full rounded-xl" />
        </div>
      ) : null}

      {/* ── Empty state — no analysis yet ── */}
      {!loading && !analysis && !isRunning && (
        <div className="flex flex-col items-center gap-4 rounded-xl border border-dashed border-border py-16 text-center">
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-muted">
            <RefreshCw className="h-6 w-6 text-muted-foreground" />
          </div>
          <div>
            <p className="font-semibold">No analysis yet</p>
            <p className="mt-1 text-sm text-muted-foreground">
              Run your first analysis to see your developer readiness score
            </p>
          </div>
          <Button onClick={runAnalysis} className="gap-1.5">
            <Zap className="h-4 w-4" />
            Run First Analysis
          </Button>
        </div>
      )}
    </div>
  )
}
