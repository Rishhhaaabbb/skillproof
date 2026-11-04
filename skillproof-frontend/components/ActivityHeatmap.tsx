'use client'
import { useState } from 'react'
import { cn } from '@/lib/utils'

interface ActivityHeatmapProps {
  heatmapData?: Record<string, number>
  isLoading?: boolean
}

const DAYS = ['Mon', 'Wed', 'Fri']
const MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

function getColor(count: number): string {
  if (count === 0) return 'bg-muted/50'
  if (count <= 2) return 'bg-emerald-900/60'
  if (count <= 5) return 'bg-emerald-700/70'
  if (count <= 9) return 'bg-emerald-500/80'
  return 'bg-emerald-400'
}

export default function ActivityHeatmap({ heatmapData, isLoading }: ActivityHeatmapProps) {
  const [tooltip, setTooltip] = useState<{ x: number; y: number; label: string } | null>(null)

  if (isLoading) {
    return (
      <div className="rounded-xl border border-border/60 bg-card p-5">
        <div className="h-4 w-32 animate-pulse rounded bg-muted mb-4" />
        <div className="flex gap-1">
          {Array.from({ length: 52 }).map((_, i) => (
            <div key={i} className="flex flex-col gap-1">
              {Array.from({ length: 7 }).map((_, j) => (
                <div key={j} className="h-3 w-3 animate-pulse rounded-sm bg-muted" />
              ))}
            </div>
          ))}
        </div>
      </div>
    )
  }

  // Build 52 weeks × 7 days grid from the heatmap data
  const weeks: { key: string; count: number; date: Date }[][] = []
  const today = new Date()

  for (let w = 51; w >= 0; w--) {
    const week: { key: string; count: number; date: Date }[] = []
    for (let d = 6; d >= 0; d--) {
      const date = new Date(today)
      date.setDate(today.getDate() - (w * 7 + d))
      const iso = date.toISOString().split('T')[0]
      // Try both the ISO date key and the week key formats
      const weekNum = getISOWeek(date)
      const weekKey = `${date.getFullYear()}-W${String(weekNum).padStart(2, '0')}`
      const count = heatmapData?.[weekKey] ?? heatmapData?.[iso] ?? 0
      week.push({ key: iso, count, date })
    }
    weeks.push(week)
  }

  // Month labels — find first week of each month
  const monthLabels: { month: string; col: number }[] = []
  weeks.forEach((week, col) => {
    const firstDay = week[week.length - 1].date
    if (firstDay.getDate() <= 7) {
      monthLabels.push({ month: MONTHS[firstDay.getMonth()], col })
    }
  })

  return (
    <div className="relative rounded-xl border border-border/60 bg-card p-5">
      <p className="mb-3 text-xs font-medium text-muted-foreground uppercase tracking-wider">
        Activity — last 52 weeks
      </p>

      <div className="flex gap-1 overflow-x-auto pb-1">
        {/* Day labels */}
        <div className="flex flex-col justify-between pt-5 pr-1 shrink-0">
          {[0,1,2].map(i => (
            <span key={i} className="text-[10px] text-muted-foreground leading-3">{DAYS[i]}</span>
          ))}
        </div>

        <div className="flex flex-col gap-0.5">
          {/* Month labels */}
          <div className="flex gap-1 mb-1 h-4">
            {monthLabels.map(({ month, col }) => (
              <span
                key={`${month}-${col}`}
                className="text-[10px] text-muted-foreground"
                style={{ marginLeft: col === 0 ? 0 : undefined }}
              >
                {month}
              </span>
            ))}
          </div>

          {/* Grid */}
          <div className="flex gap-1">
            {weeks.map((week, wi) => (
              <div key={wi} className="flex flex-col gap-1">
                {week.map((cell) => (
                  <div
                    key={cell.key}
                    className={cn('h-3 w-3 rounded-sm cursor-default transition-opacity hover:opacity-80', getColor(cell.count))}
                    onMouseEnter={(e) => {
                      const rect = e.currentTarget.getBoundingClientRect()
                      setTooltip({
                        x: rect.left,
                        y: rect.top,
                        label: `${cell.count} commits · ${cell.date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}`,
                      })
                    }}
                    onMouseLeave={() => setTooltip(null)}
                  />
                ))}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Tooltip */}
      {tooltip && (
        <div
          className="pointer-events-none fixed z-50 rounded-md border border-border bg-popover px-2.5 py-1.5 text-xs text-popover-foreground shadow-md"
          style={{ left: tooltip.x, top: tooltip.y - 36 }}
        >
          {tooltip.label}
        </div>
      )}

      {/* Legend */}
      <div className="mt-2 flex items-center gap-1.5 justify-end">
        <span className="text-[10px] text-muted-foreground">Less</span>
        {[0, 2, 5, 9, 15].map(n => (
          <div key={n} className={cn('h-2.5 w-2.5 rounded-sm', getColor(n))} />
        ))}
        <span className="text-[10px] text-muted-foreground">More</span>
      </div>
    </div>
  )
}

function getISOWeek(date: Date): number {
  const d = new Date(date)
  d.setHours(0, 0, 0, 0)
  d.setDate(d.getDate() + 4 - (d.getDay() || 7))
  const yearStart = new Date(d.getFullYear(), 0, 1)
  return Math.ceil(((d.getTime() - yearStart.getTime()) / 86400000 + 1) / 7)
}
