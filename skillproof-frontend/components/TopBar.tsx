'use client'
import NotificationBell from './NotificationBell'

interface TopBarProps {
  title: string
}

export default function TopBar({ title }: TopBarProps) {
  return (
    <header className="flex h-14 items-center justify-between border-b border-border bg-background px-6">
      <h1 className="text-lg font-semibold">{title}</h1>
      <div className="flex items-center gap-3">
        <NotificationBell />
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-xs font-bold text-primary-foreground">
          SP
        </div>
      </div>
    </header>
  )
}
