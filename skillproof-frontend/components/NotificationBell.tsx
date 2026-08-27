// Task 12: Bell icon with unread count badge linking to notifications page
'use client';

interface NotificationBellProps {
  unreadCount?: number;
}

export default function NotificationBell({ unreadCount = 0 }: NotificationBellProps) {
  return (
    <button className="relative p-2" aria-label={`${unreadCount} unread notifications`}>
      <span>🔔</span>
      {unreadCount > 0 && (
        <span className="absolute right-0 top-0 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-xs text-white">
          {unreadCount > 9 ? '9+' : unreadCount}
        </span>
      )}
      {/* Full implementation in Task 12 */}
    </button>
  );
}
