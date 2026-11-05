'use client'
import { useEffect, useState, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { Bell } from 'lucide-react'
import api from '@/lib/api'
import { cn } from '@/lib/utils'

const POLL_INTERVAL_MS = 60_000

export default function NotificationBell() {
  const router = useRouter()
  const [unreadCount, setUnreadCount] = useState(0)
  const [pulse, setPulse] = useState(false)

  const fetchCount = useCallback(async () => {
    try {
      const data = await api.get<{ unread_count: number }>('/api/notifications/unread-count')
      setUnreadCount((prev) => {
        // Trigger pulse animation when count increases
        if (data.unread_count > prev) setPulse(true)
        return data.unread_count
      })
    } catch {
      // Silently fail — bell is non-critical
    }
  }, [])

  useEffect(() => {
    fetchCount()
    const interval = setInterval(fetchCount, POLL_INTERVAL_MS)
    return () => clearInterval(interval)
  }, [fetchCount])

  // Reset pulse after animation completes
  useEffect(() => {
    if (!pulse) return
    const t = setTimeout(() => setPulse(false), 600)
    return () => clearTimeout(t)
  }, [pulse])

  return (
    <button
      onClick={() => router.push('/notifications')}
      className={cn(
        'relative flex h-8 w-8 items-center justify-center rounded-lg transition-colors',
        'text-muted-foreground hover:bg-muted hover:text-foreground',
      )}
      aria-label={
        unreadCount > 0
          ? `${unreadCount} unread notification${unreadCount !== 1 ? 's' : ''}`
          : 'Notifications'
      }
    >
      <Bell className={cn('h-4 w-4', pulse && 'animate-wiggle')} />

      {unreadCount > 0 && (
        <span
          className={cn(
            'absolute -right-0.5 -top-0.5 flex h-4 min-w-4 items-center justify-center',
            'rounded-full bg-red-500 px-1 text-[10px] font-bold tabular-nums text-white',
            'ring-2 ring-background',
            pulse && 'animate-bounce-once',
          )}
        >
          {unreadCount > 99 ? '99+' : unreadCount}
        </span>
      )}
    </button>
  )
}
