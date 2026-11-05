'use client'
import { useEffect, useState, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { Plus, Loader2, Trash2, TrendingUp, AlertCircle, X, Target } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { useJobPoller } from '@/lib/hooks/useJobPoller'
import api from '@/lib/api'
import type { TargetRole, JobStatus } from '@/lib/types'
import { cn } from '@/lib/utils'

const MAX_ROLES = 3

interface RoleAnalysisState {
  [roleId: number]: string | null // jobId or null
}

export default function TargetRolesPage() {
  const [roles, setRoles] = useState<TargetRole[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showAddPanel, setShowAddPanel] = useState(false)
  const [deleteConfirm, setDeleteConfirm] = useState<number | null>(null)
  
  // Analysis job tracking per role
  const [analysisJobs, setAnalysisJobs] = useState<RoleAnalysisState>({})

  // Form state
  const [formData, setFormData] = useState({
    role_title: '',
    company_name: '',
    jd_text: '',
  })
  const [formError, setFormError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const fetchRoles = useCallback(async () => {
    try {
      setError(null)
      const data = await api.get<TargetRole[]>('/api/target-roles')
      setRoles(data)
    } catch (err) {
      setError('Failed to load target roles')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchRoles()
  }, [fetchRoles])

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (submitting) return

    if (!formData.role_title.trim()) {
      setFormError('Role title is required')
      return
    }
    if (!formData.jd_text.trim()) {
      setFormError('Job description is required')
      return
    }

    setFormError(null)
    setSubmitting(true)

    try {
      await api.post<TargetRole>('/api/target-roles', {
        role_title: formData.role_title.trim(),
        company_name: formData.company_name.trim() || undefined,
        jd_text: formData.jd_text.trim(),
      })

      // Reset form and close panel
      setFormData({ role_title: '', company_name: '', jd_text: '' })
      setShowAddPanel(false)
      await fetchRoles()
    } catch (err: any) {
      const message = err?.response?.data?.detail || 'Failed to create target role'
      setFormError(message)
    } finally {
      setSubmitting(false)
    }
  }

  async function handleDelete(roleId: number) {
    try {
      await api.delete(`/api/target-roles/${roleId}`)
      setDeleteConfirm(null)
      await fetchRoles()
    } catch (err) {
      console.error('Failed to delete role:', err)
    }
  }

  async function triggerAnalysis(roleId: number) {
    if (analysisJobs[roleId]) return // Already running

    try {
      const job = await api.post<JobStatus>(`/api/target-roles/${roleId}/analyze`)
      setAnalysisJobs((prev) => ({ ...prev, [roleId]: job.id }))
    } catch (err: any) {
      const message = err?.response?.data?.detail || 'Failed to start analysis'
      alert(message)
    }
  }

  // Poll all active jobs and update roles when complete
  const activeJobs = Object.entries(analysisJobs).filter(([_, jobId]) => jobId !== null)

  return (
    <div className="flex h-full flex-col gap-6 overflow-y-auto p-6 pb-10">
      {/* ── Header ── */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Target Roles</h1>
          <p className="text-sm text-muted-foreground">
            Track your readiness for up to {MAX_ROLES} roles
          </p>
        </div>

        <div className="flex items-center gap-3">
          <span className="text-sm text-muted-foreground">
            {roles.length}/{MAX_ROLES} roles
          </span>
          <Button
            onClick={() => setShowAddPanel(true)}
            disabled={roles.length >= MAX_ROLES}
            size="sm"
            className="gap-1.5"
          >
            <Plus className="h-4 w-4" />
            Add Target Role
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

      {/* ── Loading skeleton ── */}
      {loading && (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-56 w-full rounded-xl" />
          ))}
        </div>
      )}

      {/* ── Role cards grid ── */}
      {!loading && roles.length > 0 && (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {roles.map((role) => (
            <RoleCard
              key={role.id}
              role={role}
              isAnalyzing={!!analysisJobs[role.id]}
              onAnalyze={() => triggerAnalysis(role.id)}
              onDelete={() => setDeleteConfirm(role.id)}
              jobId={analysisJobs[role.id]}
              onAnalysisComplete={() => {
                setAnalysisJobs((prev) => ({ ...prev, [role.id]: null }))
                fetchRoles()
              }}
            />
          ))}
        </div>
      )}

      {/* ── Empty state ── */}
      {!loading && roles.length === 0 && (
        <div className="flex flex-col items-center gap-4 rounded-xl border border-dashed border-border py-16 text-center">
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-muted">
            <Target className="h-6 w-6 text-muted-foreground" />
          </div>
          <div>
            <p className="font-semibold">No target roles yet</p>
            <p className="mt-1 text-sm text-muted-foreground">
              Add a role you're aiming for to track your readiness
            </p>
          </div>
          <Button onClick={() => setShowAddPanel(true)} className="gap-1.5">
            <Plus className="h-4 w-4" />
            Add Your First Role
          </Button>
        </div>
      )}

      {/* ── Add role slide-in panel ── */}
      {showAddPanel && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-40 bg-black/50 backdrop-blur-sm"
            onClick={() => !submitting && setShowAddPanel(false)}
          />

          {/* Panel */}
          <div className="fixed inset-y-0 right-0 z-50 w-full max-w-lg overflow-y-auto border-l border-border bg-background p-6 shadow-2xl sm:max-w-md">
            <div className="mb-6 flex items-center justify-between">
              <h2 className="text-lg font-semibold">Add Target Role</h2>
              <Button
                onClick={() => setShowAddPanel(false)}
                variant="ghost"
                size="icon-sm"
                disabled={submitting}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>

            <form onSubmit={handleSubmit} className="flex flex-col gap-4">
              {formError && (
                <div className="flex items-center gap-2 rounded-lg border border-destructive/30 bg-destructive/8 px-3 py-2 text-sm text-destructive">
                  <AlertCircle className="h-4 w-4 shrink-0" />
                  {formError}
                </div>
              )}

              <div className="flex flex-col gap-1.5">
                <label htmlFor="role_title" className="text-sm font-medium">
                  Role Title <span className="text-destructive">*</span>
                </label>
                <input
                  id="role_title"
                  type="text"
                  placeholder="e.g. Senior Frontend Engineer"
                  value={formData.role_title}
                  onChange={(e) => setFormData({ ...formData, role_title: e.target.value })}
                  disabled={submitting}
                  className="rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none focus:border-ring focus:ring-2 focus:ring-ring/20 disabled:opacity-50"
                />
              </div>

              <div className="flex flex-col gap-1.5">
                <label htmlFor="company_name" className="text-sm font-medium">
                  Company Name
                </label>
                <input
                  id="company_name"
                  type="text"
                  placeholder="e.g. Acme Corp"
                  value={formData.company_name}
                  onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
                  disabled={submitting}
                  className="rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none focus:border-ring focus:ring-2 focus:ring-ring/20 disabled:opacity-50"
                />
              </div>

              <div className="flex flex-col gap-1.5">
                <label htmlFor="jd_text" className="text-sm font-medium">
                  Job Description <span className="text-destructive">*</span>
                </label>
                <textarea
                  id="jd_text"
                  rows={12}
                  placeholder="Paste the full job description here..."
                  value={formData.jd_text}
                  onChange={(e) => setFormData({ ...formData, jd_text: e.target.value })}
                  disabled={submitting}
                  className="resize-none rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none focus:border-ring focus:ring-2 focus:ring-ring/20 disabled:opacity-50"
                />
                <p className="text-xs text-muted-foreground">
                  Copy-paste the entire job posting for best results
                </p>
              </div>

              <div className="flex gap-2 pt-2">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setShowAddPanel(false)}
                  disabled={submitting}
                  className="flex-1"
                >
                  Cancel
                </Button>
                <Button type="submit" disabled={submitting} className="flex-1 gap-1.5">
                  {submitting ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      Creating...
                    </>
                  ) : (
                    <>
                      <Plus className="h-4 w-4" />
                      Add Role
                    </>
                  )}
                </Button>
              </div>
            </form>
          </div>
        </>
      )}

      {/* ── Delete confirmation dialog ── */}
      {deleteConfirm !== null && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-40 bg-black/50 backdrop-blur-sm"
            onClick={() => setDeleteConfirm(null)}
          />

          {/* Dialog */}
          <div className="fixed left-1/2 top-1/2 z-50 w-full max-w-md -translate-x-1/2 -translate-y-1/2 rounded-xl border border-border bg-card p-6 shadow-2xl">
            <h3 className="mb-2 text-lg font-semibold">Delete Target Role?</h3>
            <p className="mb-6 text-sm text-muted-foreground">
              This will permanently delete this role and all associated analysis history, tasks, and comparisons. This action cannot be undone.
            </p>
            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={() => setDeleteConfirm(null)}
                className="flex-1"
              >
                Cancel
              </Button>
              <Button
                variant="destructive"
                onClick={() => handleDelete(deleteConfirm)}
                className="flex-1 gap-1.5"
              >
                <Trash2 className="h-4 w-4" />
                Delete
              </Button>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

// ============================================================================
// RoleCard component with circular progress and analysis state
// ============================================================================

interface RoleCardProps {
  role: TargetRole
  isAnalyzing: boolean
  onAnalyze: () => void
  onDelete: () => void
  jobId: string | null
  onAnalysisComplete: () => void
}

function RoleCard({
  role,
  isAnalyzing,
  onAnalyze,
  onDelete,
  jobId,
  onAnalysisComplete,
}: RoleCardProps) {
  const router = useRouter()
  const { status: jobStatus } = useJobPoller(jobId)

  // When job completes, notify parent
  useEffect(() => {
    if (jobStatus === 'complete') {
      onAnalysisComplete()
    }
  }, [jobStatus, onAnalysisComplete])

  const score = role.latest_readiness_score ?? null
  const lastAnalyzed = role.last_analyzed_at
    ? new Date(role.last_analyzed_at).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
      })
    : null

  const analyzing = isAnalyzing && (jobStatus === 'queued' || jobStatus === 'processing')

  return (
    <div className="flex flex-col gap-4 rounded-xl border border-border/60 bg-card p-5 transition-shadow hover:shadow-md">
      {/* Header */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 overflow-hidden">
          <h3 className="truncate font-semibold">{role.role_title}</h3>
          {role.company_name && (
            <p className="truncate text-sm text-muted-foreground">{role.company_name}</p>
          )}
        </div>
        <Button
          onClick={onDelete}
          variant="ghost"
          size="icon-sm"
          className="shrink-0 text-muted-foreground hover:text-destructive"
        >
          <Trash2 className="h-4 w-4" />
        </Button>
      </div>

      {/* Circular progress indicator */}
      <div className="flex items-center justify-center py-4">
        <CircularProgress score={score} analyzing={analyzing} />
      </div>

      {/* Last analyzed */}
      {lastAnalyzed && (
        <p className="text-center text-xs text-muted-foreground">
          Last analyzed: {lastAnalyzed}
        </p>
      )}

      {/* Actions */}
      <div className="flex gap-2">
        <Button
          onClick={onAnalyze}
          disabled={analyzing}
          variant="outline"
          size="sm"
          className="flex-1 gap-1.5"
        >
          {analyzing ? (
            <>
              <Loader2 className="h-3.5 w-3.5 animate-spin" />
              Analyzing...
            </>
          ) : (
            <>
              <TrendingUp className="h-3.5 w-3.5" />
              Analyze
            </>
          )}
        </Button>
        <Button
          onClick={() => router.push(`/target-roles/${role.id}`)}
          variant="outline"
          size="sm"
          className="flex-1"
        >
          View
        </Button>
      </div>
    </div>
  )
}

// ============================================================================
// CircularProgress component
// ============================================================================

interface CircularProgressProps {
  score: number | null
  analyzing: boolean
}

function CircularProgress({ score, analyzing }: CircularProgressProps) {
  const size = 120
  const strokeWidth = 8
  const radius = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius

  if (analyzing) {
    // Pulsing "Analyzing..." state
    return (
      <div
        className="flex flex-col items-center justify-center rounded-full border-4 border-primary/20"
        style={{ width: size, height: size }}
      >
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
        <p className="mt-1 text-xs font-medium text-primary">Analyzing</p>
      </div>
    )
  }

  if (score === null) {
    // Not yet analyzed
    return (
      <div
        className="flex flex-col items-center justify-center rounded-full border-4 border-dashed border-border"
        style={{ width: size, height: size }}
      >
        <p className="text-xs font-medium text-muted-foreground">Not analyzed</p>
      </div>
    )
  }

  // Scored — show circular progress
  const progress = (score / 100) * circumference
  const color =
    score >= 80 ? '#10b981' : score >= 60 ? '#f59e0b' : score >= 40 ? '#f97316' : '#ef4444'

  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="hsl(var(--border))"
          strokeWidth={strokeWidth}
          opacity={0.2}
        />
        {/* Progress circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={circumference - progress}
          strokeLinecap="round"
          className="transition-all duration-500"
        />
      </svg>
      {/* Score text */}
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <p className="text-2xl font-bold tabular-nums" style={{ color }}>
          {score}
        </p>
        <p className="text-xs text-muted-foreground">readiness</p>
      </div>
    </div>
  )
}
