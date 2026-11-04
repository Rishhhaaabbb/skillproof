'use client'
import { TrendingUp } from 'lucide-react'

interface LRScoreCardProps {
  lrScore?: number
  confidenceLevel?: string
  isLoading?: boolean
}

export default function LRScoreCard({ lrScore, confidenceLevel, isLoading }: LRScoreCardProps) {
  if (isLoading) {
    return (
      <div className="flex flex-col gap-3 rounded-xl border border-border/60 bg-card p-5">
        <div className="h-4 w-28 animate-pulse rounded bg-muted" />
        <div className="h-8 w-16 animate-pulse rounded bg-muted" />
        <div className="h-3 w-20 animate-pulse rounded bg-muted" />
      </div>
    )
  }

  const score = lrScore ?? null

  return (
    <div className="flex flex-col gap-2 rounded-xl border border-border/60 bg-card p-5">
      <div className="flex items-center gap-1.5">
        <TrendingUp className="h-3.5 w-3.5 text-muted-foreground" />
        <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">ML Readiness</p>
      </div>
      <p className="text-3xl font-bold tabular-nums">
        {score !== null ? `${score}` : <span className="text-muted-foreground">—</span>}
        {score !== null && <span className="text-lg font-normal text-muted-foreground">/100</span>}
      </p>
      {confidenceLevel ? (
        <p className="text-xs text-muted-foreground">{confidenceLevel} confidence</p>
      ) : (
        <p className="text-xs text-muted-foreground">Train model to unlock</p>
      )}
    </div>
  )
}
