'use client'
import { useEffect, useState, useCallback } from 'react'
import {
  Trophy, TrendingUp, CheckCircle2, TrendingDown,
  Bell, BellOff, CheckCheck, AlertCircle,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import api from '@/lib/api'
import type { Notification } from '@/lib/types'
import { cn } from '@/lib/utils'

// ---------------------------------------------------------------------------
// Relative timestamp helper
// ---------------------------------------------------------------------------
function relativeTime(isoDate: string): string {
  const diff = Date.now() - new Date(isoDate).getTime()
  const mins = Math.floor(diff / 60_000)
  if (mins < 1) return 'just now'
  if (mins < 60) return `${mins}m ago`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  if (days < 7) return `${days}d ago`
  return new Date(isoDate).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

// ---------------------------------------------------------------------------
// Icon classification from notification message text
// ---------------------------------------------------------------------------
function getIcon(message: string) {
  const m = message.toLowerCase()
  if (m.includes('milestone') || m.includes('badge') || m.includes('earned') || m.includes('account'))
    return { Icon: Trophy, color: 'text-amber-500', bg: 'bg-amber-500/10' }
  if (m.includes('improved') || m.includes('increased') || m.includes('up'))
    return { Icon: TrendingUp, color: 'text-emerald-500', bg: 'bg-emerald-500/10' }
  if (m.includes('complete') || m.includes('verified') || m.includes('done'))
    return { Icon: CheckCircle2, color: 'text-emerald-500', bg: 'bg-emerald-500/10' }
  if (m.includes('drop') || m.includes('decreased') || m.includes('fell') || m.includes('low'))
    return { Icon: TrendingDown, color: 'text-red-500', bg: 'bg-red-500/10' }
  return { Icon: Bell, color: 'text-primary', bg: 'bg-primary/10' }
}

// ---------------------------------------------------------------------------
// Single notification row
// ---------------------------------------------------------------------------
function NotificationItem({
  notification,
  onMarkRead,
  index,
}: {
  notification: Notification
  onMarkRead: (id: number) => void
  index: number
}) {
  const { Icon, color, bg } = getIcon(notification.message)

  return (
    <div
      className={cn(
        'flex cursor-pointer items-start gap-4 rounded-xl border px-4 py-3.5 transition-all',
        'opacity-0 translate-y-2',             // start state for animation
        'animate-slide-in',
        notification.is_read
          ? 'border-border/40 bg-card/50 hover:bg-card'
          : 'border-primary/20 bg-primary/5 hover:bg-primary/8',
      )}
      style={{ animationDelay: `${index * 40}ms`, animationFillMode: 'forwards' }}
      onClick={() => !notification.is_read && onMarkRead(notification.id)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && !notification.is_read && onMarkRead(notification.id)}
    >
      {/* Icon */}
      <div className={cn('mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full', bg)}>
        <Icon className={cn('h-4 w-4', color)} />
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <p className={cn('text-sm leading-snug', !notification.is_read && 'font-medium')}>
          {notification.message}
        </p>
        <p className="mt-1 text-xs text-muted-foreground">
          {relativeTime(notification.created_at)}
        </p>
      </div>

      {/* Unread dot */}
      {!notification.is_read && (
        <div className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-primary" />
      )}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Main page
// ---------------------------------------------------------------------------
type Filter = 'all' | 'unread'

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filter, setFilter] = useState<Filter>('all')
  const [markingAll, setMarkingAll] = useState(false)

  const fetchNotifications = useCallback(async () => {
    setError(null)
    try {
      const data = await api.get<Notification[]>('/api/notifications?limit=100')
      setNotifications(data)
    } catch {
      setError('Failed to load notifications')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchNotifications() }, [fetchNotifications])

  const unreadCount = notifications.filter((n) => !n.is_read).length

  async function markRead(id: number) {
    // Optimistic update
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
    )
    try {
      await api.patch(`/api/notifications/${id}/read`)
    } catch {
      // Revert on failure
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: false } : n))
      )
    }
  }

  async function markAllRead() {
    if (markingAll || unreadCount === 0) return
    setMarkingAll(true)
    // Optimistic
    setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })))
    try {
      await api.patch('/api/notifications/read-all')
    } catch {
      fetchNotifications()
    } finally {
      setMarkingAll(false)
    }
  }

  const displayed = filter === 'unread'
    ? notifications.filter((n) => !n.is_read)
    : notifications

  return (
    <div className="flex h-full flex-col overflow-y-auto">
      <div className="mx-auto w-full max-w-2xl px-4 py-6 sm:px-6">

        {/* ── Header ── */}
        <div className="mb-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold tracking-tight">Notifications</h1>
            {unreadCount > 0 && (
              <Badge className="tabular-nums">{unreadCount} unread</Badge>
            )}
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={markAllRead}
            disabled={unreadCount === 0 || markingAll}
            className="gap-1.5"
          >
            <CheckCheck className="h-3.5 w-3.5" />
            Mark all read
          </Button>
        </div>

        {/* ── Filter tabs ── */}
        <div className="mb-4 flex gap-1 rounded-lg border border-border/60 bg-muted/30 p-1 w-fit">
          {(['all', 'unread'] as Filter[]).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={cn(
                'rounded-md px-3.5 py-1.5 text-sm font-medium capitalize transition-colors',
                filter === f
                  ? 'bg-background text-foreground shadow-sm'
                  : 'text-muted-foreground hover:text-foreground',
              )}
            >
              {f}
              {f === 'unread' && unreadCount > 0 && (
                <span className="ml-1.5 rounded-full bg-primary px-1.5 py-0.5 text-[10px] text-primary-foreground tabular-nums">
                  {unreadCount}
                </span>
              )}
            </button>
          ))}
        </div>

        {/* ── Error ── */}
        {error && (
          <div className="mb-4 flex items-center gap-2 rounded-lg border border-destructive/30 bg-destructive/8 px-4 py-3 text-sm text-destructive">
            <AlertCircle className="h-4 w-4 shrink-0" />
            {error}
          </div>
        )}

        {/* ── Loading skeleton ── */}
        {loading && (
          <div className="flex flex-col gap-2">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="flex items-start gap-4 rounded-xl border border-border/40 px-4 py-3.5">
                <Skeleton className="h-8 w-8 shrink-0 rounded-full" />
                <div className="flex-1 space-y-2">
                  <Skeleton className="h-3.5 w-3/4" />
                  <Skeleton className="h-3 w-1/4" />
                </div>
              </div>
            ))}
          </div>
        )}

        {/* ── Empty state ── */}
        {!loading && displayed.length === 0 && (
          <div className="flex flex-col items-center gap-4 rounded-xl border border-dashed border-border py-16 text-center">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-muted">
              <BellOff className="h-5 w-5 text-muted-foreground" />
            </div>
            <div>
              <p className="font-semibold">
                {filter === 'unread' ? 'All caught up!' : 'No notifications yet'}
              </p>
              <p className="mt-1 text-sm text-muted-foreground">
                {filter === 'unread'
                  ? 'You have no unread notifications.'
                  : 'Notifications appear here when your scores change or tasks complete.'}
              </p>
            </div>
            {filter === 'unread' && (
              <button
                onClick={() => setFilter('all')}
                className="text-sm text-primary underline-offset-4 hover:underline"
              >
                View all notifications
              </button>
            )}
          </div>
        )}

        {/* ── Notification list ── */}
        {!loading && displayed.length > 0 && (
          <div className="flex flex-col gap-2">
            {displayed.map((n, i) => (
              <NotificationItem
                key={n.id}
                notification={n}
                onMarkRead={markRead}
                index={i}
              />
            ))}
          </div>
        )}

      </div>
    </div>
  )
}
