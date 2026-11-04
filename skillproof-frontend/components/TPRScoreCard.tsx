'use client'
import { cn } from '@/lib/utils'

interface TPRScoreCardProps {
  tprScore?: number
  confidence?: string
  isLoading?: boolean
}

export default function TPRScoreCard({ tprScore, confidence, isLoading }: TPRScoreCardProps) {
  const score = tprScore ?? 0
  const radius = 36
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (score / 100) * circumference

  const color =
    score >= 65 ? '#22c55e' : score >= 35 ? '#f59e0b' : '#ef4444'

  if (isLoading) {
    return (
      <div className="flex flex-col gap-3 rounded-xl border border-border/60 bg-card p-5">
        <div className="h-4 w-24 animate-pulse rounded bg-muted" />
        <div className="h-20 w-20 animate-pulse rounded-full bg-muted mx-auto" />
        <div className="h-3 w-16 animate-pulse rounded bg-muted mx-auto" />
      </div>
    )
  }

  return (
    <div className="flex flex-col items-center gap-2 rounded-xl border border-border/60 bg-card p-5">
      <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">TPR Score</p>
      <div className="relative flex items-center justify-center">
        <svg width="100" height="100" className="-rotate-90">
          <circle cx="50" cy="50" r={radius} stroke="currentColor" strokeWidth="7"
            className="text-muted/40" fill="none" />
          <circle cx="50" cy="50" r={radius}
            stroke={color} strokeWidth="7" fill="none"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            style={{ transition: 'stroke-dashoffset 1s ease' }}
          />
        </svg>
        <span className="absolute text-2xl font-bold" style={{ color }}>{score}</span>
      </div>
      {confidence && (
        <span className={cn(
          'rounded-full px-2 py-0.5 text-xs font-medium',
          confidence === 'high' ? 'bg-emerald-500/10 text-emerald-500' :
          confidence === 'medium' ? 'bg-amber-500/10 text-amber-500' :
          'bg-red-500/10 text-red-500'
        )}>
          {confidence} confidence
        </span>
      )}
    </div>
  )
}
