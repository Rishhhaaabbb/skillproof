'use client'

interface StreakCounterProps {
  currentStreak?: number
  longestStreak?: number
  isLoading?: boolean
}

export default function StreakCounter({ currentStreak, longestStreak, isLoading }: StreakCounterProps) {
  if (isLoading) {
    return (
      <div className="flex flex-col gap-3 rounded-xl border border-border/60 bg-card p-5">
        <div className="h-4 w-20 animate-pulse rounded bg-muted" />
        <div className="h-8 w-14 animate-pulse rounded bg-muted" />
        <div className="h-3 w-24 animate-pulse rounded bg-muted" />
      </div>
    )
  }

  const current = currentStreak ?? 0

  return (
    <div className="flex flex-col gap-2 rounded-xl border border-border/60 bg-card p-5">
      <div className="flex items-center gap-1.5">
        <span className="text-base">🔥</span>
        <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Streak</p>
      </div>
      <p className="text-3xl font-bold tabular-nums">
        {current}
        <span className="text-lg font-normal text-muted-foreground"> days</span>
      </p>
      <p className="text-xs text-muted-foreground">
        Best: <span className="font-medium text-foreground">{longestStreak ?? 0} days</span>
      </p>
    </div>
  )
}
