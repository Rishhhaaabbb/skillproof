'use client'
import {
  Radar, RadarChart, PolarGrid, PolarAngleAxis, ResponsiveContainer, Tooltip,
} from 'recharts'

interface SkillRadarChartProps {
  breakdown?: Record<string, unknown>
  isLoading?: boolean
}

function extractScore(val: unknown): number {
  if (typeof val === 'number') return Math.round(val)
  if (val && typeof val === 'object') {
    const v = val as Record<string, unknown>
    if (typeof v.raw_score === 'number') return Math.round(v.raw_score)
    if (typeof v.score === 'number') return Math.round(v.score)
  }
  return 0
}

const DIMENSION_LABELS: Record<string, string> = {
  commit_quality: 'Commit Quality',
  pr_collaboration: 'PR Collaboration',
  code_review: 'Code Review',
  consistency: 'Consistency',
  repo_depth: 'Repo Depth',
}

export default function SkillRadarChart({ breakdown, isLoading }: SkillRadarChartProps) {
  if (isLoading) {
    return (
      <div className="flex flex-col gap-3 rounded-xl border border-border/60 bg-card p-5">
        <div className="h-4 w-28 animate-pulse rounded bg-muted mb-2" />
        <div className="h-48 w-full animate-pulse rounded bg-muted" />
      </div>
    )
  }

  const data = Object.entries(DIMENSION_LABELS).map(([key, label]) => ({
    subject: label,
    score: extractScore(breakdown?.[key]),
    fullMark: 100,
  }))

  const hasData = data.some(d => d.score > 0)

  return (
    <div className="rounded-xl border border-border/60 bg-card p-5">
      <p className="mb-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">
        Skill Dimensions
      </p>
      {!hasData ? (
        <div className="flex h-48 items-center justify-center text-sm text-muted-foreground">
          Run an analysis to see your skill radar
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={220}>
          <RadarChart data={data} margin={{ top: 10, right: 20, bottom: 10, left: 20 }}>
            <PolarGrid stroke="currentColor" className="text-border/40" />
            <PolarAngleAxis
              dataKey="subject"
              tick={{ fontSize: 11, fill: 'hsl(var(--muted-foreground))' }}
            />
            <Tooltip
              contentStyle={{
                background: 'hsl(var(--card))',
                border: '1px solid hsl(var(--border))',
                borderRadius: '8px',
                fontSize: '12px',
              }}
              formatter={(v: number) => [`${v}/100`, 'Score']}
            />
            <Radar
              name="Score"
              dataKey="score"
              stroke="#6366f1"
              fill="#6366f1"
              fillOpacity={0.15}
              strokeWidth={2}
            />
          </RadarChart>
        </ResponsiveContainer>
      )}
    </div>
  )
}
