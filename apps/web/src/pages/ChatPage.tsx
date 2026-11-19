import { useEffect, useMemo, useRef, useState, type FormEvent, type KeyboardEvent } from 'react'
import { useNavigate, useParams } from 'react-router'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { AnimatePresence, motion } from 'motion/react'
import * as Dialog from '@radix-ui/react-dialog'
import { Archive, Download, Info, Pencil, Plus, Send, Square, Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Alert, Input, Textarea } from '@/components/ui/form'
import { Badge, EmptyState, Spinner } from '@/components/ui/card'
import { api, ApiError } from '@/lib/api'
import { useAuth } from '@/lib/auth'
import { streamMessage, type ChatMessage, type Conversation, type ProviderInfo } from '@/lib/chat'
import { cn } from '@/lib/utils'

const LANG_LABEL: Record<string, string> = { en: 'English', ur: 'اردو', 'ur-Latn': 'Roman Urdu', mixed: 'Mixed', unknown: '' }

function ConsentDialog({ provider, onAccept, onCancel }: { provider: ProviderInfo; onAccept: () => void; onCancel: () => void }) {
  return (
    <Dialog.Root open onOpenChange={(o) => !o && onCancel()}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-40 bg-black/60" />
        <Dialog.Content className="fixed left-1/2 top-1/2 z-50 w-[min(520px,92vw)] -translate-x-1/2 -translate-y-1/2 space-y-4 rounded-xl border border-border bg-bg-elevated p-6">
          <Dialog.Title className="text-lg font-semibold">Before you use {provider.name}</Dialog.Title>
          <Dialog.Description asChild>
            <div className="space-y-3 text-sm text-muted">
              <p>Your messages in this chat will be sent to an external AI provider to generate replies.</p>
              <p className="rounded-lg border border-warning/40 bg-warning/10 p-3 text-fg">{provider.data_policy}</p>
              <p>{provider.free_tier_note}</p>
              <p>You can withdraw this consent at any time in Settings. The offline demo model never sends data anywhere.</p>
            </div>
          </Dialog.Description>
          <div className="flex justify-end gap-2">
            <Button variant="secondary" onClick={onCancel}>Cancel</Button>
            <Button onClick={onAccept}>I understand and agree</Button>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}

function ConversationList({ activeId }: { activeId?: string }) {
  const nav = useNavigate()
  const [q, setQ] = useState('')
  const list = useQuery({
    queryKey: ['conversations', q],
    queryFn: () => api<Conversation[]>(`/conversations${q ? `?q=${encodeURIComponent(q)}` : ''}`),
  })
  return (
    <div className="flex h-full flex-col gap-3">
      <Button onClick={() => nav('/app/chat')} className="w-full"><Plus className="h-4 w-4" /> New chat</Button>
      <Input placeholder="Search chats" aria-label="Search chats" value={q} onChange={(e) => setQ(e.target.value)} />
      <ul className="min-h-0 flex-1 space-y-1 overflow-auto" aria-label="Chats">
        {list.isPending ? <li><Spinner /></li> : null}
        {list.data?.length === 0 ? <li className="px-2 text-sm text-muted">{q ? 'No matches.' : 'No chats yet.'}</li> : null}
        {list.data?.map((c) => (
          <li key={c.id}>
            <button
              type="button"
              onClick={() => nav(`/app/chat/${c.id}`)}
              className={cn('w-full truncate rounded-lg px-3 py-2 text-left text-sm', c.id === activeId ? 'bg-primary/15 text-fg' : 'text-muted hover:bg-surface-2 hover:text-fg')}
            >
              {c.title}
            </button>
          </li>
        ))}
      </ul>
    </div>
  )
}

function ModelPicker({ providers, value, onChange }: { providers: ProviderInfo[]; value: string; onChange: (provider: string, model: string) => void }) {
  return (
    <select
      aria-label="Model"
      value={value}
      onChange={(e) => {
        const [p, ...m] = e.target.value.split('|')
        onChange(p, m.join('|'))
      }}
      className="h-9 rounded-lg border border-border bg-surface px-2 text-sm"
    >
      {providers.map((p) =>
        p.models.map((m) => (
          <option key={`${p.id}|${m.id}`} value={`${p.id}|${m.id}`} disabled={!p.available}>
            {p.name} · {m.label}
            {!p.available ? ' (not configured)' : ''}
          </option>
        )),
      )}
    </select>
  )
}

interface LiveMessage extends Partial<ChatMessage> {
  key: string
  role: 'user' | 'assistant'
  content: string
  streaming?: boolean
}

export function ChatPage() {
  const { conversationId } = useParams()
  // Remount per conversation so local streaming state never leaks between chats.
  return <ChatView key={conversationId ?? 'new'} conversationId={conversationId} />
}

function ChatView({ conversationId }: { conversationId?: string }) {
  const nav = useNavigate()
  const qc = useQueryClient()
  const { me, refresh } = useAuth()
  const [draft, setDraft] = useState('')
  const [live, setLive] = useState<LiveMessage[]>([])
  const [error, setError] = useState<string | null>(null)
  const [notice, setNotice] = useState<string | null>(null)
  const [consentFor, setConsentFor] = useState<ProviderInfo | null>(null)
  const [picked, setSelected] = useState<{ provider: string; model: string } | null>(null)
  const [renaming, setRenaming] = useState(false)
  const abort = useRef<AbortController | null>(null)
  const bottom = useRef<HTMLDivElement>(null)

  const providers = useQuery({ queryKey: ['models'], queryFn: () => api<ProviderInfo[]>('/models') })
  const conv = useQuery({
    queryKey: ['conversation', conversationId],
    queryFn: () => api<Conversation>(`/conversations/${conversationId}`),
    enabled: !!conversationId,
  })
  const history = useQuery({
    queryKey: ['messages', conversationId],
    queryFn: () => api<ChatMessage[]>(`/conversations/${conversationId}/messages`),
    enabled: !!conversationId,
  })

  const selected = picked ?? (conv.data ? { provider: conv.data.provider, model: conv.data.model } : { provider: 'mock', model: 'aura-mock-1' })
  useEffect(() => bottom.current?.scrollIntoView({ block: 'end' }), [live, history.data])

  const streaming = live.some((m) => m.streaming)
  const providerId = selected.provider
  const providerInfo = useMemo(() => providers.data?.find((p) => p.id === providerId), [providers.data, providerId])

  const patch = useMutation({
    mutationFn: (body: Record<string, unknown>) => api<Conversation>(`/conversations/${conversationId}`, { method: 'PATCH', json: body }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['conversation', conversationId] })
      void qc.invalidateQueries({ queryKey: ['conversations'] })
    },
  })

  async function ensureConversation(): Promise<string> {
    if (conversationId) {
      if (conv.data && (conv.data.provider !== selected.provider || conv.data.model !== selected.model)) {
        await patch.mutateAsync({ provider: selected.provider, model: selected.model })
      }
      return conversationId
    }
    const c = await api<Conversation>('/conversations', { json: selected })
    void qc.invalidateQueries({ queryKey: ['conversations'] })
    return c.id
  }

  async function send(text: string) {
    if (!me?.email_verified) return setError('Verify your email to start chatting.')
    if (providerInfo?.requires_consent && !me.provider_consent_at) return setConsentFor(providerInfo)
    setError(null)
    setNotice(null)
    let cid: string
    try {
      cid = await ensureConversation()
    } catch (e) {
      return setError(e instanceof ApiError ? e.message : 'Could not start the chat.')
    }
    const userKey = crypto.randomUUID()
    const botKey = crypto.randomUUID()
    setLive((l) => [...l, { key: userKey, role: 'user', content: text }, { key: botKey, role: 'assistant', content: '', streaming: true }])
    setDraft('')
    const ctrl = new AbortController()
    abort.current = ctrl
    let target = cid
    try {
      await streamMessage(
        cid,
        text,
        (e) => {
          if (e.event === 'delta') setLive((l) => l.map((m) => (m.key === botKey ? { ...m, content: m.content + e.data.text } : m)))
          else if (e.event === 'meta') setLive((l) => l.map((m) => (m.key === userKey ? { ...m, language: e.data.language } : m)))
          else if (e.event === 'continued') {
            target = e.data.conversation_id
            setNotice('This chat was getting long, so AURA continued it in a new chat from a summary. The original chat is kept.')
          } else if (e.event === 'notice') setNotice(e.data.message)
          else if (e.event === 'error') setError(e.data.message)
        },
        ctrl.signal,
      )
    } catch (e) {
      if (!(e instanceof DOMException && e.name === 'AbortError')) setError(e instanceof ApiError ? e.message : 'The reply failed. Please try again.')
      if (e instanceof ApiError && e.code === 'consent_required' && providerInfo) setConsentFor(providerInfo)
    } finally {
      setLive((l) => l.map((m) => (m.key === botKey ? { ...m, streaming: false } : m)))
      abort.current = null
      void qc.invalidateQueries({ queryKey: ['conversations'] })
      void qc.invalidateQueries({ queryKey: ['messages', target] })
      void qc.invalidateQueries({ queryKey: ['conversation', target] })
      if (target !== conversationId) nav(`/app/chat/${target}`)
      else {
        await qc.refetchQueries({ queryKey: ['messages', target] })
        setLive([])
      }
    }
  }

  const submit = (e?: FormEvent) => {
    e?.preventDefault()
    const text = draft.trim()
    if (text && !streaming) void send(text)
  }
  const onKey = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      submit()
    }
  }

  const messages: LiveMessage[] = [
    ...(history.data ?? []).map((m) => ({ ...m, key: m.id })),
    ...live,
  ]

  return (
    <div className="flex h-full">
      <aside className="hidden w-72 shrink-0 border-r border-border p-4 lg:block">
        <ConversationList activeId={conversationId} />
      </aside>
      <section className="flex min-w-0 flex-1 flex-col">
        <div className="flex flex-wrap items-center gap-2 border-b border-border px-4 py-2">
          {renaming && conv.data ? (
            <form
              className="flex gap-2"
              onSubmit={(e) => {
                e.preventDefault()
                const t = new FormData(e.currentTarget).get('title') as string
                if (t.trim()) patch.mutate({ title: t.trim() })
                setRenaming(false)
              }}
            >
              <Input name="title" defaultValue={conv.data.title} aria-label="Chat title" className="h-9 w-64" autoFocus />
              <Button size="sm" type="submit">Save</Button>
            </form>
          ) : (
            <h1 className="truncate text-sm font-medium">{conv.data?.title ?? 'New chat'}</h1>
          )}
          {conv.data?.continued_from_id ? (
            <Button variant="ghost" size="sm" onClick={() => nav(`/app/chat/${conv.data!.continued_from_id}`)}>
              <Info className="h-3.5 w-3.5" /> Continued from earlier chat
            </Button>
          ) : null}
          <div className="ml-auto flex items-center gap-1">
            {providers.data ? (
              <ModelPicker providers={providers.data} value={`${selected.provider}|${selected.model}`} onChange={(provider, model) => setSelected({ provider, model })} />
            ) : null}
            {conversationId ? (
              <>
                <Button variant="ghost" size="icon" aria-label="Rename chat" onClick={() => setRenaming(true)}><Pencil className="h-4 w-4" /></Button>
                <Button
                  variant="ghost"
                  size="icon"
                  aria-label="Export chat"
                  onClick={() =>
                    void api<unknown>(`/conversations/${conversationId}/export`).then((data) => {
                      const url = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' }))
                      const a = Object.assign(document.createElement('a'), { href: url, download: `aura-chat-${conversationId}.json` })
                      a.click()
                      URL.revokeObjectURL(url)
                    })
                  }
                >
                  <Download className="h-4 w-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  aria-label="Archive chat"
                  onClick={() => void patch.mutateAsync({ archived: true }).then(() => nav('/app/chat'))}
                >
                  <Archive className="h-4 w-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  aria-label="Delete chat"
                  onClick={() => {
                    if (window.confirm('Delete this chat permanently? This cannot be undone.'))
                      void api(`/conversations/${conversationId}`, { method: 'DELETE' }).then(() => {
                        void qc.invalidateQueries({ queryKey: ['conversations'] })
                        nav('/app/chat')
                      })
                  }}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </>
            ) : null}
          </div>
        </div>

        <div className="min-h-0 flex-1 overflow-auto px-4 py-6" aria-live="polite">
          <div className="mx-auto flex max-w-3xl flex-col gap-4">
            {conv.isError ? <Alert tone="error">This chat could not be loaded.</Alert> : null}
            {messages.length === 0 && !conv.isPending ? (
              <EmptyState title="Start a conversation">
                Write in English, اردو or Roman Urdu. AURA replies in the same language.
                {selected.provider === 'mock' ? <p className="mt-2">You are using the offline demo model: replies are canned, not real AI.</p> : null}
              </EmptyState>
            ) : null}
            <AnimatePresence initial={false}>
              {messages.map((m) => (
                <motion.div
                  key={m.key}
                  initial={{ opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={cn('flex flex-col gap-1', m.role === 'user' ? 'items-end' : 'items-start')}
                >
                  <div
                    lang={m.language === 'ur' ? 'ur' : undefined}
                    className={cn(
                      'max-w-[85%] whitespace-pre-wrap break-words rounded-2xl px-4 py-2.5 text-sm leading-relaxed',
                      m.role === 'user' ? 'bg-primary text-primary-fg' : 'border border-border bg-surface',
                      m.status === 'error' && 'border-danger/50',
                    )}
                  >
                    {m.content || (m.streaming ? <span className="inline-block h-4 w-2 animate-pulse bg-primary-strong align-middle" aria-label="AURA is typing" /> : <em className="text-muted">No reply</em>)}
                  </div>
                  <div className="flex gap-2 text-[11px] text-muted">
                    {m.language && LANG_LABEL[m.language] ? <span>{LANG_LABEL[m.language]}</span> : null}
                    {m.role === 'assistant' && m.model ? <span>{m.model}</span> : null}
                    {m.status === 'stopped' ? <span>Stopped</span> : null}
                    {m.status === 'error' ? <span className="text-danger">Failed</span> : null}
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
            <div ref={bottom} />
          </div>
        </div>

        <div className="border-t border-border p-4">
          <div className="mx-auto max-w-3xl space-y-2">
            {notice ? <Alert tone="info">{notice}</Alert> : null}
            {error ? <Alert tone="error">{error}</Alert> : null}
            <form onSubmit={submit} className="flex items-end gap-2">
              <Textarea
                aria-label="Message"
                placeholder="Message AURA… (Enter to send, Shift+Enter for a new line)"
                rows={2}
                maxLength={20000}
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
                onKeyDown={onKey}
                className="max-h-48 min-h-12 resize-y"
              />
              {streaming ? (
                <Button type="button" variant="secondary" size="icon" aria-label="Stop generating" onClick={() => abort.current?.abort()}>
                  <Square className="h-4 w-4" />
                </Button>
              ) : (
                <Button type="submit" size="icon" aria-label="Send" disabled={!draft.trim()}>
                  <Send className="h-4 w-4" />
                </Button>
              )}
            </form>
            {providerInfo ? (
              <p className="text-[11px] text-muted">
                <Badge className="mr-1">{providerInfo.paid ? 'Paid' : 'Free tier'}</Badge>
                {providerInfo.free_tier_note}
              </p>
            ) : null}
          </div>
        </div>
      </section>
      {consentFor ? (
        <ConsentDialog
          provider={consentFor}
          onCancel={() => setConsentFor(null)}
          onAccept={() =>
            void api('/auth/me', { method: 'PATCH', json: { provider_consent: true } }).then(async () => {
              setConsentFor(null)
              await refresh()
            })
          }
        />
      ) : null}
    </div>
  )
}
