'use client'
import {
  useEffect, useState, useCallback, useRef, useLayoutEffect,
} from 'react'
import {
  ShieldCheck, Send, MessageSquare, ChevronDown, Sparkles,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import api from '@/lib/api'
import type { TargetRole, ChatMessage } from '@/lib/types'
import { cn } from '@/lib/utils'

// ---------------------------------------------------------------------------
// Suggested starter questions shown in empty state
// ---------------------------------------------------------------------------
const STARTERS = [
  "What's my biggest gap for a senior backend role?",
  'Which of my repos shows the strongest signal to a recruiter?',
  'What should I commit to this week to improve my TPR score?',
]

// ---------------------------------------------------------------------------
// Inline markdown renderer — bold + inline code only, no dep needed
// ---------------------------------------------------------------------------
function RenderMessage({ text }: { text: string }) {
  // Split on **bold** and `code` patterns
  const parts: { type: 'text' | 'bold' | 'code'; content: string }[] = []
  const regex = /(\*\*[^*]+\*\*|`[^`]+`)/g
  let last = 0
  let match: RegExpExecArray | null

  while ((match = regex.exec(text)) !== null) {
    if (match.index > last) {
      parts.push({ type: 'text', content: text.slice(last, match.index) })
    }
    const raw = match[0]
    if (raw.startsWith('**')) {
      parts.push({ type: 'bold', content: raw.slice(2, -2) })
    } else {
      parts.push({ type: 'code', content: raw.slice(1, -1) })
    }
    last = match.index + raw.length
  }
  if (last < text.length) {
    parts.push({ type: 'text', content: text.slice(last) })
  }

  return (
    <>
      {parts.map((p, i) => {
        if (p.type === 'bold') return <strong key={i}>{p.content}</strong>
        if (p.type === 'code') return (
          <code
            key={i}
            className="rounded bg-black/10 px-1 py-0.5 font-mono text-[0.8em] dark:bg-white/10"
          >
            {p.content}
          </code>
        )
        // Preserve newlines
        return (
          <span key={i}>
            {p.content.split('\n').map((line, j, arr) => (
              <span key={j}>{line}{j < arr.length - 1 && <br />}</span>
            ))}
          </span>
        )
      })}
    </>
  )
}

// ---------------------------------------------------------------------------
// Typing indicator — three bouncing dots
// ---------------------------------------------------------------------------
function TypingIndicator() {
  return (
    <div className="flex items-end gap-3">
      {/* Avatar */}
      <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-primary/10">
        <ShieldCheck className="h-3.5 w-3.5 text-primary" />
      </div>
      <div className="flex items-center gap-1 rounded-2xl rounded-bl-sm border border-border/60 bg-muted/50 px-4 py-3">
        {[0, 1, 2].map((i) => (
          <span
            key={i}
            className="h-1.5 w-1.5 rounded-full bg-muted-foreground/60"
            style={{ animation: `bounce 1.2s ease-in-out ${i * 0.2}s infinite` }}
          />
        ))}
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Single message bubble
// ---------------------------------------------------------------------------
function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === 'user'

  return (
    <div className={cn('flex items-end gap-3', isUser && 'flex-row-reverse')}>
      {/* Avatar — only for assistant */}
      {!isUser && (
        <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-primary/10">
          <ShieldCheck className="h-3.5 w-3.5 text-primary" />
        </div>
      )}

      <div
        className={cn(
          'max-w-[75%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed',
          isUser
            ? 'rounded-br-sm bg-foreground text-background'
            : 'rounded-bl-sm border border-border/60 bg-card text-foreground',
        )}
      >
        <RenderMessage text={message.content} />
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Sidebar conversation list
// ---------------------------------------------------------------------------
interface SidebarProps {
  roles: TargetRole[]
  activeRoleId: number | null
  onSelect: (id: number | null) => void
  loading: boolean
}

function ConversationSidebar({ roles, activeRoleId, onSelect, loading }: SidebarProps) {
  return (
    <div className="flex h-full w-56 shrink-0 flex-col border-r border-border/60 bg-card/50">
      <div className="border-b border-border/60 px-4 py-3">
        <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          Conversations
        </p>
      </div>

      <div className="flex flex-col gap-0.5 overflow-y-auto p-2">
        {/* General */}
        <button
          onClick={() => onSelect(null)}
          className={cn(
            'flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-left text-sm transition-colors',
            activeRoleId === null
              ? 'bg-primary/10 font-medium text-primary'
              : 'text-muted-foreground hover:bg-muted hover:text-foreground',
          )}
        >
          <Sparkles className="h-3.5 w-3.5 shrink-0" />
          General
        </button>

        {/* Separator */}
        {roles.length > 0 && (
          <p className="mt-2 px-3 pb-1 text-[10px] font-medium uppercase tracking-widest text-muted-foreground/60">
            By Role
          </p>
        )}

        {/* Role-specific conversations */}
        {loading
          ? [1, 2].map((i) => (
              <div key={i} className="flex items-center gap-2 rounded-lg px-3 py-2">
                <Skeleton className="h-3 w-3 rounded-full" />
                <Skeleton className="h-3 flex-1 rounded" />
              </div>
            ))
          : roles.map((role) => (
              <button
                key={role.id}
                onClick={() => onSelect(role.id)}
                className={cn(
                  'flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-left text-sm transition-colors',
                  activeRoleId === role.id
                    ? 'bg-primary/10 font-medium text-primary'
                    : 'text-muted-foreground hover:bg-muted hover:text-foreground',
                )}
              >
                <MessageSquare className="h-3.5 w-3.5 shrink-0" />
                <span className="truncate">{role.role_title}</span>
              </button>
            ))}
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Main chat page
// ---------------------------------------------------------------------------
export default function ChatPage() {
  const [roles, setRoles] = useState<TargetRole[]>([])
  const [rolesLoading, setRolesLoading] = useState(true)

  const [activeRoleId, setActiveRoleId] = useState<number | null>(null)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [historyLoading, setHistoryLoading] = useState(true)

  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)

  const bottomRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // ------------------------------------------------------------------
  // Load roles
  // ------------------------------------------------------------------
  useEffect(() => {
    api.get<TargetRole[]>('/api/target-roles')
      .then(setRoles)
      .catch(() => {})
      .finally(() => setRolesLoading(false))
  }, [])

  // ------------------------------------------------------------------
  // Load message history whenever active role changes
  // ------------------------------------------------------------------
  const loadHistory = useCallback(async (roleId: number | null) => {
    setHistoryLoading(true)
    setMessages([])
    try {
      const url = roleId != null
        ? `/api/chat?target_role_id=${roleId}&limit=100`
        : `/api/chat?limit=100`
      const data = await api.get<ChatMessage[]>(url)
      setMessages(data)
    } catch {
      setMessages([])
    } finally {
      setHistoryLoading(false)
    }
  }, [])

  useEffect(() => { loadHistory(activeRoleId) }, [activeRoleId, loadHistory])

  // ------------------------------------------------------------------
  // Scroll to bottom whenever messages change
  // ------------------------------------------------------------------
  useLayoutEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, sending])

  // ------------------------------------------------------------------
  // Auto-resize textarea up to 4 lines
  // ------------------------------------------------------------------
  useEffect(() => {
    const ta = textareaRef.current
    if (!ta) return
    ta.style.height = 'auto'
    const lineHeight = 24
    const maxHeight = lineHeight * 4 + 24 // 4 lines + padding
    ta.style.height = `${Math.min(ta.scrollHeight, maxHeight)}px`
  }, [input])

  // ------------------------------------------------------------------
  // Send message
  // ------------------------------------------------------------------
  async function sendMessage(text: string) {
    const trimmed = text.trim()
    if (!trimmed || sending) return

    const optimistic: ChatMessage = {
      id: Date.now(),
      user_id: 0,
      role: 'user',
      content: trimmed,
      target_role_id: activeRoleId ?? undefined,
      created_at: new Date().toISOString(),
    }

    setMessages((prev) => [...prev, optimistic])
    setInput('')
    setSending(true)

    try {
      const response = await api.post<ChatMessage>('/api/chat', {
        message: trimmed,
        target_role_id: activeRoleId,
      })
      setMessages((prev) => [
        ...prev.filter((m) => m.id !== optimistic.id),
        { ...optimistic },
        response,
      ])
    } catch {
      setMessages((prev) => prev.filter((m) => m.id !== optimistic.id))
    } finally {
      setSending(false)
    }
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage(input)
    }
  }

  // Active role name for the header
  const activeRole = roles.find((r) => r.id === activeRoleId)
  const contextLabel = activeRole ? activeRole.role_title : 'General'

  return (
    <div className="flex h-full overflow-hidden">

      {/* ── Sidebar ── */}
      <ConversationSidebar
        roles={roles}
        activeRoleId={activeRoleId}
        onSelect={(id) => setActiveRoleId(id)}
        loading={rolesLoading}
      />

      {/* ── Main chat area ── */}
      <div className="flex flex-1 flex-col overflow-hidden">

        {/* Top bar */}
        <div className="flex items-center gap-3 border-b border-border/60 bg-card/50 px-5 py-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10">
            <ShieldCheck className="h-4 w-4 text-primary" />
          </div>
          <div>
            <p className="text-sm font-semibold">SkillProof AI</p>
            <p className="text-xs text-muted-foreground">
              Context: {contextLabel}
            </p>
          </div>
          <div className="ml-auto flex h-2 w-2 rounded-full bg-emerald-500" />
        </div>

        {/* Message thread */}
        <div className="flex-1 overflow-y-auto px-4 py-5 sm:px-6">
          <div className="mx-auto flex max-w-2xl flex-col gap-5">

            {/* Loading history skeleton */}
            {historyLoading && (
              <>
                <div className="flex items-end gap-3">
                  <Skeleton className="h-7 w-7 rounded-full" />
                  <Skeleton className="h-14 w-64 rounded-2xl" />
                </div>
                <div className="flex flex-row-reverse items-end gap-3">
                  <Skeleton className="h-10 w-48 rounded-2xl" />
                </div>
                <div className="flex items-end gap-3">
                  <Skeleton className="h-7 w-7 rounded-full" />
                  <Skeleton className="h-20 w-72 rounded-2xl" />
                </div>
              </>
            )}

            {/* Empty state */}
            {!historyLoading && messages.length === 0 && !sending && (
              <div className="flex flex-col items-center gap-6 pt-10 text-center">
                <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/10">
                  <ShieldCheck className="h-7 w-7 text-primary" />
                </div>
                <div>
                  <p className="text-lg font-semibold">SkillProof AI</p>
                  <p className="mt-1 text-sm text-muted-foreground">
                    Ask me anything about your GitHub profile, readiness score, or how to close skill gaps.
                  </p>
                </div>
                {/* Starter questions */}
                <div className="flex w-full flex-col gap-2">
                  {STARTERS.map((q) => (
                    <button
                      key={q}
                      onClick={() => sendMessage(q)}
                      className="w-full rounded-xl border border-border/60 bg-card px-4 py-3 text-left text-sm text-muted-foreground transition-colors hover:border-primary/30 hover:bg-primary/5 hover:text-foreground"
                    >
                      {q}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Message list */}
            {!historyLoading && messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} />
            ))}

            {/* Typing indicator */}
            {sending && <TypingIndicator />}

            {/* Scroll anchor */}
            <div ref={bottomRef} />
          </div>
        </div>

        {/* ── Sticky input bar ── */}
        <div className="border-t border-border/60 bg-card/80 px-4 py-3 backdrop-blur-sm sm:px-6">
          <div className="mx-auto max-w-2xl">

            {/* Role selector (shown when no sidebar role is active) */}
            {activeRoleId === null && roles.length > 0 && (
              <div className="mb-2 flex items-center gap-2">
                <p className="text-xs text-muted-foreground">Ask about a specific role:</p>
                <div className="relative">
                  <select
                    value={activeRoleId ?? ''}
                    onChange={(e) => setActiveRoleId(e.target.value ? Number(e.target.value) : null)}
                    className="appearance-none rounded-lg border border-border bg-background py-1 pl-2.5 pr-7 text-xs outline-none focus:border-ring focus:ring-2 focus:ring-ring/20"
                  >
                    <option value="">General</option>
                    {roles.map((r) => (
                      <option key={r.id} value={r.id}>{r.role_title}</option>
                    ))}
                  </select>
                  <ChevronDown className="pointer-events-none absolute right-2 top-1/2 h-3 w-3 -translate-y-1/2 text-muted-foreground" />
                </div>
              </div>
            )}

            <div className="flex items-end gap-2">
              <textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={`Ask SkillProof AI${activeRole ? ` about ${activeRole.role_title}` : ''}…`}
                rows={1}
                disabled={sending}
                className={cn(
                  'flex-1 resize-none rounded-xl border border-border bg-background px-3.5 py-2.5 text-sm outline-none transition-colors',
                  'placeholder:text-muted-foreground/50',
                  'focus:border-ring focus:ring-2 focus:ring-ring/20',
                  'disabled:opacity-50',
                )}
                style={{ overflowY: 'auto' }}
              />
              <Button
                onClick={() => sendMessage(input)}
                disabled={!input.trim() || sending}
                size="icon"
                className="mb-0 shrink-0"
              >
                <Send className="h-4 w-4" />
              </Button>
            </div>
            <p className="mt-1.5 text-center text-[10px] text-muted-foreground/50">
              Shift+Enter for new line · Enter to send
            </p>
          </div>
        </div>

      </div>
    </div>
  )
}
