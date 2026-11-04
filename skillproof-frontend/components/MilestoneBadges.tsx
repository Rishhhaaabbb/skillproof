'use client'
import type { Milestone } from '@/lib/types'
import { Trophy, Star, Zap, GitCommit, Users, CheckCircle2, TrendingUp, Flame } from 'lucide-react'

const MILESTONE_ICONS: Record<string, React.ElementType> = {
  account_created: Star,
  first_analysis: Zap,
  streak_7: Flame,
  streak_30: Flame,
  pr_master: GitCommit,
  review_contributor: Users,
  task_complete: CheckCircle2,
  score_70: TrendingUp,
  default: Trophy,
}

interface MilestoneBadgesProps {
  milestones?: Milestone[]
  isLoading?: boolean
}

export default function MilestoneBadges({ milestones = [], isLoading }: MilestoneBadgesProps) {
  if (isLoading) {
    return (
      <div className="rounded-xl border border-border/60 bg-card p-5">
        <div className="h-4 w-24 animate-pulse rounded bg-muted mb-3" />
        <div className="flex flex-wrap gap-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-8 w-28 animate-pulse rounded-full bg-muted" />
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="rounded-xl border border-border/60 bg-card p-5">
      <p className="mb-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">
        Milestones <span className="ml-1 text-foreground">{milestones.length}</span>
      </p>
      {milestones.length === 0 ? (
        <p className="text-sm text-muted-foreground">Complete tasks to earn badges</p>
      ) : (
        <div className="flex flex-wrap gap-2">
          {milestones.map((m) => {
            const Icon = MILESTONE_ICONS[m.milestone_key] ?? MILESTONE_ICONS.default
            return (
              <div
                key={m.id}
                className="flex items-center gap-1.5 rounded-full border border-border/60 bg-muted/30 px-2.5 py-1"
                title={new Date(m.earned_at).toLocaleDateString()}
              >
                <Icon className="h-3 w-3 text-amber-400" />
                <span className="text-xs font-medium">{m.milestone_label}</span>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
