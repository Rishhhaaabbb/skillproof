'use client'
import { useEffect, useState, useCallback, useRef } from 'react'
import { useParams, useRouter } from 'next/navigation'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts'
import {
  ArrowLeft, RefreshCw, Loader2, CheckCircle2, XCircle, AlertCircle,
  TrendingUp, Send, BarChart2, ShieldAlert, ShieldCheck, Scale,
  GitBranch, Clock, CheckCheck, Ban,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import { useJobPoller } from '@/lib/hooks/useJobPoller'
import api from '@/lib/api'
import type { TargetRole, JobStatus, ChatMessage } from '@/lib/types'
import { cn } from '@/lib/utils'

// ---------------------------------------------------------------------------
// Types for API responses
// ---------------------------------------------------------------------------

interface GapAnalysis {
  readiness_estimate: number
  matched_requirements: Array<string | { requirement: string; evidence?: string }>
  missing_requirements: string[]
  citation_hallucination_rate?: number
}

interface Verdict {
  skeptic_case: string
  advocate_case: string
  final_verdict: string
  confidence: number
  surviving_skeptic_points: string[]
  surviving_advocate_points: string[]
}

interface Task {
  id: number
  missing_requirement: string
  target_repo?: string
  task_description: string
  verification_signal?: Record<string, unknown>
  status: 'assigned' | 'verified_complete' | 'expired'
  created_at: string
}

interface HistoryPoint {
  readiness_score: number
  recorded_at: string
}

// ---------------------------------------------------------------------------
// Helper: parse a matched requirement (string or object)
// ---------------------------------------------------------------------------
function parseMatched(item: string | { requirement: string; evidence?: string }) {
  if (typeof item === 'string') return { requirement: item, evidence: undefined }
  return { requirement: item.requirement, evidence: item.evidence }
}

// ---------------------------------------------------------------------------
// Main page
// ---------------------------------------------------------------------------
export default function TargetRoleDetailPage() {
  const params = useParams()
  const router = useRouter()
  const roleId = Number(params.id)

  const [role, setRole] = useState<TargetRole | null>(null)
  const [verdict, setVerdict] = useState<Verdict | null>(null)
  const [tasks, setTasks] = useState<Task[]>([])
  const [history, setHistory] = useState<HistoryPoint[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Analysis job
  const [jobId, setJobId] = useState<string | null>(null)
  const { status: jobStatus } = useJobPoller(jobId)

  const fetchAll = useCallback(async () => {
    setError(null)
    try {
      const [roleData, verdictData, tasksData, historyData] = await Promise.allSettled([
        api.get<TargetRole>(`/api/target-roles/${roleId}`),
        api.get<Verdict>(`/api/target-roles/${roleId}/verdict`),
        api.get<Task[]>(`/api/target-roles/${roleId}/tasks`),
        api.get<HistoryPoint[]>(`/api/target-roles/${roleId}/history`),
      ])
      if (roleData.status === 'fulfilled') setRole(roleData.value)
      else setError('Failed to load role')
      if (verdictData.status === 'fulfilled') setVerdict(verdictData.value)
      if (tasksData.status === 'fulfilled') setTasks(tasksData.value)
      if (historyData.status === 'fulfilled') setHistory(historyData.value)
    } finally {
      setLoading(false)
    }
  }, [roleId])

  useEffect(() => { fetchAll() }, [fetchAll])

  // When job completes refresh all data
  useEffect(() => {
    if (jobStatus === 'complete') {
      setJobId(null)
      fetchAll()
    }
  }, [jobStatus, fetchAll])

  async function triggerAnalysis() {
    if (jobId) return
    try {
      const job = await api.post<JobStatus>(`/api/target-roles/${roleId}/analyze`)
      setJobId(job.id)
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? 'Failed to start analysis')
    }
  }

  const isAnalyzing = jobStatus === 'queued' || jobStatus === 'processing'
  const gap = role?.latest_gap_analysis as GapAnalysis | undefined

  return (
    <div className="flex h-full flex-col gap-0 overflow-y-auto pb-10">
      {/* ── Header ── */}
      <div className="flex flex-col gap-3 border-b border-border/60 bg-card/50 px-6 py-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={() => router.push('/target-roles')}
            className="text-muted-foreground"
          >
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            {loading ? (
              <Skeleton className="h-6 w-48" />
            ) : (
              <h1 className="text-xl font-bold tracking-tight">{role?.role_title}</h1>
            )}
            {role?.company_name && (
              <p className="text-sm text-muted-foreground">{role.company_name}</p>
            )}
          </div>
        </div>

        <div className="flex items-center gap-2">
          {jobStatus === 'complete' && (
            <div className="flex items-center gap-1.5 rounded-lg border border-emerald-500/20 bg-emerald-500/10 px-3 py-1.5 text-xs text-emerald-600 dark:text-emerald-400">
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
            onClick={triggerAnalysis}
            disabled={isAnalyzing}
            size="sm"
            className="gap-1.5"
          >
            {isAnalyzing
              ? <><Loader2 className="h-3.5 w-3.5 animate-spin" />Analyzing…</>
              : <><RefreshCw className="h-3.5 w-3.5" />Re-analyze</>
            }
          </Button>
        </div>
      </div>

      {/* ── Error ── */}
      {error && (
        <div className="mx-6 mt-4 flex items-center gap-2 rounded-lg border border-destructive/30 bg-destructive/8 px-4 py-3 text-sm text-destructive">
          <AlertCircle className="h-4 w-4 shrink-0" />
          {error}
        </div>
      )}

      {/* ── Tabs ── */}
      <div className="px-6 pt-4">
        <Tabs defaultValue="overview">
          <TabsList className="mb-6 w-full sm:w-auto">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="verdict">Verdict</TabsTrigger>
            <TabsTrigger value="tasks">
              Tasks
              {tasks.filter(t => t.status === 'assigned').length > 0 && (
                <Badge variant="secondary" className="ml-1 h-4 min-w-4 px-1 text-[10px]">
                  {tasks.filter(t => t.status === 'assigned').length}
                </Badge>
              )}
            </TabsTrigger>
            <TabsTrigger value="progress">Progress</TabsTrigger>
          </TabsList>

          {/* ── OVERVIEW TAB ── */}
          <TabsContent value="overview">
            <OverviewTab role={role} gap={gap} loading={loading} />
          </TabsContent>

          {/* ── VERDICT TAB ── */}
          <TabsContent value="verdict">
            <VerdictTab verdict={verdict} loading={loading} />
          </TabsContent>

          {/* ── TASKS TAB ── */}
          <TabsContent value="tasks">
            <TasksTab tasks={tasks} roleId={roleId} loading={loading} />
          </TabsContent>

          {/* ── PROGRESS TAB ── */}
          <TabsContent value="progress">
            <ProgressTab history={history} loading={loading} />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}

// ===========================================================================
// OVERVIEW TAB
// ===========================================================================
function OverviewTab({
  role, gap, loading,
}: { role: TargetRole | null; gap: GapAnalysis | undefined; loading: boolean }) {
  const score = role?.latest_readiness_score ?? gap?.readiness_estimate ?? null

  return (
    <div className="flex flex-col gap-6">
      {/* Readiness Gauge */}
      <div className="flex flex-col items-center gap-4 rounded-xl border border-border/60 bg-card p-6 sm:flex-row sm:items-start sm:gap-8">
        {loading ? (
          <div className="flex h-36 w-36 shrink-0 items-center justify-center">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        ) : (
          <ReadinessGauge score={score} />
        )}
        <div className="flex flex-col gap-2 text-center sm:text-left">
          <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
            Readiness Score
          </p>
          {loading ? (
            <>
              <Skeleton className="h-8 w-32" />
              <Skeleton className="h-4 w-48" />
            </>
          ) : score !== null ? (
            <>
              <p className="text-4xl font-bold tabular-nums">{Math.round(score)}%</p>
              <p className="text-sm text-muted-foreground">
                {score >= 80
                  ? 'You\'re well-positioned for this role.'
                  : score >= 60
                  ? 'Strong foundation — close a few gaps to stand out.'
                  : score >= 40
                  ? 'Good start. Several areas to strengthen before applying.'
                  : 'Significant gaps remain. Run tasks to build readiness.'}
              </p>
              {role?.last_analyzed_at && (
                <p className="text-xs text-muted-foreground">
                  Last analyzed:{' '}
                  {new Date(role.last_analyzed_at).toLocaleDateString('en-US', {
                    month: 'long', day: 'numeric', year: 'numeric',
                  })}
                </p>
              )}
            </>
          ) : (
            <p className="text-sm text-muted-foreground">
              Run an analysis to see your readiness score.
            </p>
          )}
        </div>
      </div>

      {/* Gap Analysis Panel */}
      {loading ? (
        <div className="flex flex-col gap-3">
          <Skeleton className="h-6 w-40" />
          <Skeleton className="h-20 w-full rounded-xl" />
          <Skeleton className="h-20 w-full rounded-xl" />
        </div>
      ) : gap ? (
        <GapAnalysisPanel gap={gap} />
      ) : (
        <div className="flex flex-col items-center gap-3 rounded-xl border border-dashed border-border py-12 text-center">
          <BarChart2 className="h-8 w-8 text-muted-foreground/40" />
          <p className="text-sm font-medium">No gap analysis yet</p>
          <p className="text-xs text-muted-foreground">
            Click Re-analyze to run the full gap analysis pipeline.
          </p>
        </div>
      )}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Readiness Gauge — semicircle SVG
// ---------------------------------------------------------------------------
function ReadinessGauge({ score }: { score: number | null }) {
  const size = 160
  const strokeWidth = 12
  const radius = (size - strokeWidth) / 2 - 4
  // Semicircle: from 180° to 0° (left to right along the top)
  const cx = size / 2
  const cy = size / 2 + 10  // shift center down so semicircle fits

  const arcLength = Math.PI * radius
  const progress = score !== null ? (score / 100) * arcLength : 0

  const color =
    score === null ? 'hsl(var(--muted))'
      : score >= 80 ? '#10b981'
      : score >= 60 ? '#f59e0b'
      : score >= 40 ? '#f97316'
      : '#ef4444'

  // Build semicircle path (180° arc)
  const startX = cx - radius
  const startY = cy
  const endX = cx + radius
  const endY = cy

  return (
    <div className="relative shrink-0" style={{ width: size, height: size / 2 + 30 }}>
      <svg width={size} height={size / 2 + 30} overflow="visible">
        {/* Background arc */}
        <path
          d={`M ${startX} ${startY} A ${radius} ${radius} 0 0 1 ${endX} ${endY}`}
          fill="none"
          stroke="hsl(var(--border))"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          opacity={0.25}
        />
        {/* Progress arc using stroke-dasharray */}
        {score !== null && (
          <path
            d={`M ${startX} ${startY} A ${radius} ${radius} 0 0 1 ${endX} ${endY}`}
            fill="none"
            stroke={color}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={`${progress} ${arcLength}`}
            style={{ transition: 'stroke-dasharray 0.6s ease' }}
          />
        )}
      </svg>
      {/* Center label */}
      <div
        className="absolute bottom-0 left-1/2 -translate-x-1/2 flex flex-col items-center"
      >
        {score !== null ? (
          <p className="text-3xl font-bold tabular-nums" style={{ color }}>
            {Math.round(score)}
          </p>
        ) : (
          <p className="text-sm text-muted-foreground">—</p>
        )}
        <p className="text-xs text-muted-foreground">/ 100</p>
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Gap Analysis Panel
// ---------------------------------------------------------------------------
function GapAnalysisPanel({ gap }: { gap: GapAnalysis }) {
  const matched = gap.matched_requirements ?? []
  const missing = gap.missing_requirements ?? []

  return (
    <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
      {/* Matched */}
      <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-5">
        <div className="mb-4 flex items-center gap-2">
          <CheckCircle2 className="h-4 w-4 text-emerald-500" />
          <p className="text-sm font-semibold text-emerald-700 dark:text-emerald-400">
            Matched Requirements
          </p>
          <Badge variant="secondary" className="ml-auto text-xs">
            {matched.length}
          </Badge>
        </div>
        {matched.length === 0 ? (
          <p className="text-xs text-muted-foreground">No matched requirements found.</p>
        ) : (
          <ul className="flex flex-col gap-3">
            {matched.map((item, i) => {
              const { requirement, evidence } = parseMatched(item)
              return (
                <li key={i} className="flex flex-col gap-0.5">
                  <div className="flex items-start gap-2">
                    <CheckCircle2 className="mt-0.5 h-3.5 w-3.5 shrink-0 text-emerald-500" />
                    <span className="text-sm">{requirement}</span>
                  </div>
                  {evidence && (
                    <p className="ml-5.5 text-xs text-muted-foreground italic">
                      ↳ {evidence}
                    </p>
                  )}
                </li>
              )
            })}
          </ul>
        )}
      </div>

      {/* Missing */}
      <div className="rounded-xl border border-red-500/20 bg-red-500/5 p-5">
        <div className="mb-4 flex items-center gap-2">
          <XCircle className="h-4 w-4 text-red-500" />
          <p className="text-sm font-semibold text-red-700 dark:text-red-400">
            Missing Requirements
          </p>
          <Badge variant="secondary" className="ml-auto text-xs">
            {missing.length}
          </Badge>
        </div>
        {missing.length === 0 ? (
          <p className="text-xs text-muted-foreground">
            No missing requirements — you tick all the boxes!
          </p>
        ) : (
          <ul className="flex flex-col gap-2">
            {missing.map((req, i) => (
              <li key={i} className="flex items-start gap-2">
                <XCircle className="mt-0.5 h-3.5 w-3.5 shrink-0 text-red-500" />
                <span className="text-sm">{req}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}

// ===========================================================================
// VERDICT TAB
// ===========================================================================
function VerdictTab({ verdict, loading }: { verdict: Verdict | null; loading: boolean }) {
  if (loading) {
    return (
      <div className="flex flex-col gap-4">
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
          <Skeleton className="h-64 rounded-xl" />
          <Skeleton className="h-64 rounded-xl" />
          <Skeleton className="h-64 rounded-xl" />
        </div>
      </div>
    )
  }

  if (!verdict) {
    return (
      <div className="flex flex-col items-center gap-3 rounded-xl border border-dashed border-border py-16 text-center">
        <Scale className="h-8 w-8 text-muted-foreground/40" />
        <p className="text-sm font-medium">No verdict yet</p>
        <p className="text-xs text-muted-foreground">
          Run an analysis to generate the adversarial evaluation.
        </p>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-6">
      {/* Three verdict cards */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        {/* Skeptic */}
        <VerdictCard
          icon={<ShieldAlert className="h-4 w-4 text-red-500" />}
          title="Skeptic"
          titleColor="text-red-700 dark:text-red-400"
          borderColor="border-red-500/20"
          bgColor="bg-red-500/5"
          body={verdict.skeptic_case}
          points={verdict.surviving_skeptic_points}
          pointsLabel="Surviving concerns"
          pointsColor="text-red-600 dark:text-red-400"
          pointIcon={<XCircle className="mt-0.5 h-3.5 w-3.5 shrink-0 text-red-500" />}
        />

        {/* Advocate */}
        <VerdictCard
          icon={<ShieldCheck className="h-4 w-4 text-emerald-500" />}
          title="Advocate"
          titleColor="text-emerald-700 dark:text-emerald-400"
          borderColor="border-emerald-500/20"
          bgColor="bg-emerald-500/5"
          body={verdict.advocate_case}
          points={verdict.surviving_advocate_points}
          pointsLabel="Strongest arguments"
          pointsColor="text-emerald-600 dark:text-emerald-400"
          pointIcon={<CheckCircle2 className="mt-0.5 h-3.5 w-3.5 shrink-0 text-emerald-500" />}
        />

        {/* Judge */}
        <div className="flex flex-col rounded-xl border border-border/60 bg-card p-5">
          <div className="mb-3 flex items-center gap-2">
            <Scale className="h-4 w-4 text-primary" />
            <p className="text-sm font-semibold">Judge</p>
            <Badge variant="secondary" className="ml-auto text-xs">
              {Math.round(verdict.confidence * 100)}% confidence
            </Badge>
          </div>
          <p className="text-sm leading-relaxed text-foreground/80">{verdict.final_verdict}</p>
        </div>
      </div>
    </div>
  )
}

interface VerdictCardProps {
  icon: React.ReactNode
  title: string
  titleColor: string
  borderColor: string
  bgColor: string
  body: string
  points: string[]
  pointsLabel: string
  pointsColor: string
  pointIcon: React.ReactNode
}

function VerdictCard({
  icon, title, titleColor, borderColor, bgColor, body,
  points, pointsLabel, pointsColor, pointIcon,
}: VerdictCardProps) {
  return (
    <div className={cn('flex flex-col rounded-xl border p-5', borderColor, bgColor)}>
      <div className="mb-3 flex items-center gap-2">
        {icon}
        <p className={cn('text-sm font-semibold', titleColor)}>{title}</p>
      </div>
      <p className="mb-4 text-sm leading-relaxed text-foreground/80">{body}</p>
      {points?.length > 0 && (
        <>
          <p className={cn('mb-2 text-xs font-medium uppercase tracking-wider', pointsColor)}>
            {pointsLabel}
          </p>
          <ul className="flex flex-col gap-1.5">
            {points.map((pt, i) => (
              <li key={i} className="flex items-start gap-2 text-xs text-foreground/70">
                {pointIcon}
                {pt}
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  )
}

// ===========================================================================
// TASKS TAB
// ===========================================================================
function TasksTab({
  tasks, roleId, loading,
}: { tasks: Task[]; roleId: number; loading: boolean }) {
  return (
    <div className="grid grid-cols-1 gap-4 lg:grid-cols-5">
      {/* Task list — left 3/5 */}
      <div className="flex flex-col gap-4 lg:col-span-3">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold">Active Tasks</h2>
          <p className="text-xs text-muted-foreground">
            Complete these to close your skill gaps
          </p>
        </div>

        {loading ? (
          <>
            <Skeleton className="h-36 rounded-xl" />
            <Skeleton className="h-36 rounded-xl" />
          </>
        ) : tasks.length === 0 ? (
          <div className="flex flex-col items-center gap-3 rounded-xl border border-dashed border-border py-12 text-center">
            <CheckCheck className="h-8 w-8 text-muted-foreground/40" />
            <p className="text-sm font-medium">No tasks yet</p>
            <p className="text-xs text-muted-foreground">
              Run an analysis to generate targeted tasks from your gap analysis.
            </p>
          </div>
        ) : (
          tasks.map((task) => <TaskCard key={task.id} task={task} />)
        )}
      </div>

      {/* Inline chat — right 2/5 */}
      <div className="lg:col-span-2">
        <ChatPanel roleId={roleId} />
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Task Card
// ---------------------------------------------------------------------------
function TaskCard({ task }: { task: Task }) {
  const statusConfig = {
    assigned: {
      label: 'Assigned',
      className: 'border-amber-500/30 bg-amber-500/10 text-amber-700 dark:text-amber-400',
      icon: <Clock className="h-3 w-3" />,
    },
    verified_complete: {
      label: 'Verified Complete',
      className: 'border-emerald-500/30 bg-emerald-500/10 text-emerald-700 dark:text-emerald-400',
      icon: <CheckCheck className="h-3 w-3" />,
    },
    expired: {
      label: 'Expired',
      className: 'border-border bg-muted/50 text-muted-foreground',
      icon: <Ban className="h-3 w-3" />,
    },
  }[task.status]

  const signal = task.verification_signal as Record<string, unknown> | undefined

  return (
    <div className="flex flex-col gap-3 rounded-xl border border-border/60 bg-card p-5">
      {/* Header row */}
      <div className="flex items-start justify-between gap-3">
        <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
          {task.missing_requirement}
        </p>
        <span className={cn(
          'flex shrink-0 items-center gap-1 rounded-full border px-2 py-0.5 text-xs font-medium',
          statusConfig.className,
        )}>
          {statusConfig.icon}
          {statusConfig.label}
        </span>
      </div>

      {/* Task description */}
      <p className="text-sm leading-relaxed">{task.task_description}</p>

      {/* Target repo */}
      {task.target_repo && (
        <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
          <GitBranch className="h-3.5 w-3.5" />
          <span className="font-mono">{task.target_repo}</span>
        </div>
      )}

      {/* Verification signal */}
      {signal && Object.keys(signal).length > 0 && (
        <div className="rounded-lg border border-border/50 bg-muted/30 p-3">
          <p className="mb-1.5 text-xs font-medium text-muted-foreground">Verification Signal</p>
          <ul className="flex flex-col gap-1">
            {Object.entries(signal).map(([k, v]) => (
              <li key={k} className="flex gap-1.5 text-xs">
                <span className="font-medium text-foreground/70">{k}:</span>
                <span className="text-muted-foreground">{String(v)}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Inline Chat Panel
// ---------------------------------------------------------------------------
function ChatPanel({ roleId }: { roleId: number }) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [loadingHistory, setLoadingHistory] = useState(true)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    api.get<ChatMessage[]>(`/api/chat?target_role_id=${roleId}&limit=50`)
      .then(setMessages)
      .catch(() => {})
      .finally(() => setLoadingHistory(false))
  }, [roleId])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function sendMessage(e: React.FormEvent) {
    e.preventDefault()
    const text = input.trim()
    if (!text || sending) return

    // Optimistic user message
    const optimistic: ChatMessage = {
      id: Date.now(),
      user_id: 0,
      role: 'user',
      content: text,
      target_role_id: roleId,
      created_at: new Date().toISOString(),
    }
    setMessages((prev) => [...prev, optimistic])
    setInput('')
    setSending(true)

    try {
      const response = await api.post<ChatMessage>('/api/chat', {
        message: text,
        target_role_id: roleId,
      })
      // Replace optimistic + add assistant reply
      setMessages((prev) => [
        ...prev.filter((m) => m.id !== optimistic.id),
        { ...optimistic, id: optimistic.id },
        response,
      ])
    } catch {
      setMessages((prev) => prev.filter((m) => m.id !== optimistic.id))
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="flex h-[520px] flex-col rounded-xl border border-border/60 bg-card">
      {/* Header */}
      <div className="flex items-center gap-2 border-b border-border/60 px-4 py-3">
        <div className="flex h-2 w-2 rounded-full bg-emerald-500" />
        <p className="text-sm font-medium">Role Assistant</p>
        <p className="ml-auto text-xs text-muted-foreground">Ask anything about this role</p>
      </div>

      {/* Messages */}
      <div className="flex flex-1 flex-col gap-3 overflow-y-auto p-4">
        {loadingHistory ? (
          <div className="flex flex-col gap-2">
            <Skeleton className="h-10 w-4/5 rounded-2xl" />
            <Skeleton className="ml-auto h-8 w-3/5 rounded-2xl" />
          </div>
        ) : messages.length === 0 ? (
          <div className="flex h-full flex-col items-center justify-center gap-2 text-center">
            <p className="text-sm font-medium text-muted-foreground">
              Ask me about this role
            </p>
            <p className="text-xs text-muted-foreground/70">
              e.g. "What should I focus on this week?"
            </p>
          </div>
        ) : (
          messages.map((msg) => (
            <ChatBubble key={msg.id} message={msg} />
          ))
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <form
        onSubmit={sendMessage}
        className="flex items-center gap-2 border-t border-border/60 p-3"
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about this role…"
          disabled={sending}
          className="flex-1 rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none focus:border-ring focus:ring-2 focus:ring-ring/20 disabled:opacity-50"
        />
        <Button
          type="submit"
          size="icon-sm"
          disabled={!input.trim() || sending}
        >
          {sending ? (
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
          ) : (
            <Send className="h-3.5 w-3.5" />
          )}
        </Button>
      </form>
    </div>
  )
}

function ChatBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === 'user'
  return (
    <div className={cn('flex', isUser ? 'justify-end' : 'justify-start')}>
      <div
        className={cn(
          'max-w-[85%] rounded-2xl px-3.5 py-2.5 text-sm leading-relaxed',
          isUser
            ? 'rounded-br-sm bg-primary text-primary-foreground'
            : 'rounded-bl-sm border border-border/60 bg-muted/50 text-foreground',
        )}
      >
        {message.content}
      </div>
    </div>
  )
}

// ===========================================================================
// PROGRESS TAB
// ===========================================================================
function ProgressTab({
  history, loading,
}: { history: HistoryPoint[]; loading: boolean }) {
  const chartData = history.map((h, i) => ({
    index: i + 1,
    score: Math.round(h.readiness_score),
    date: new Date(h.recorded_at).toLocaleDateString('en-US', {
      month: 'short', day: 'numeric',
    }),
  }))

  return (
    <div className="flex flex-col gap-6">
      {/* Summary stats */}
      {!loading && history.length > 0 && (
        <div className="grid grid-cols-3 gap-4">
          {[
            {
              label: 'Latest',
              value: `${Math.round(history.at(-1)!.readiness_score)}%`,
            },
            {
              label: 'Best',
              value: `${Math.round(Math.max(...history.map(h => h.readiness_score)))}%`,
            },
            {
              label: 'Analyses',
              value: String(history.length),
            },
          ].map(({ label, value }) => (
            <div
              key={label}
              className="flex flex-col items-center gap-1 rounded-xl border border-border/60 bg-card py-5"
            >
              <p className="text-2xl font-bold tabular-nums">{value}</p>
              <p className="text-xs text-muted-foreground">{label}</p>
            </div>
          ))}
        </div>
      )}

      {/* Chart */}
      <div className="rounded-xl border border-border/60 bg-card p-5">
        <p className="mb-4 text-xs font-medium uppercase tracking-wider text-muted-foreground">
          Readiness Over Time
        </p>
        {loading ? (
          <Skeleton className="h-56 w-full" />
        ) : chartData.length < 2 ? (
          <div className="flex h-56 flex-col items-center justify-center gap-2 text-center">
            <TrendingUp className="h-8 w-8 text-muted-foreground/30" />
            <p className="text-sm text-muted-foreground">
              Run at least 2 analyses to see your progress trend.
            </p>
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={220}>
            <LineChart
              data={chartData}
              margin={{ top: 5, right: 10, bottom: 5, left: 0 }}
            >
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="hsl(var(--border))"
                opacity={0.4}
              />
              <XAxis
                dataKey="date"
                tick={{ fontSize: 11 }}
                stroke="hsl(var(--muted-foreground))"
              />
              <YAxis
                domain={[0, 100]}
                tick={{ fontSize: 11 }}
                stroke="hsl(var(--muted-foreground))"
                tickFormatter={(v) => `${v}%`}
              />
              <Tooltip
                contentStyle={{
                  background: 'hsl(var(--card))',
                  border: '1px solid hsl(var(--border))',
                  borderRadius: '8px',
                  fontSize: '12px',
                }}
                formatter={(v: any) => [`${v ?? 0}%`, 'Readiness']}
              />
              <Line
                type="monotone"
                dataKey="score"
                stroke="#6366f1"
                strokeWidth={2.5}
                dot={{ r: 4, fill: '#6366f1', strokeWidth: 0 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  )
}
