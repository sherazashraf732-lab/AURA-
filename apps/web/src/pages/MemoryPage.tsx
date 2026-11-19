import { useState } from 'react'
import { Link } from 'react-router'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Alert, Input } from '@/components/ui/form'
import { Badge, Card, EmptyState, Spinner } from '@/components/ui/card'
import { api, ApiError } from '@/lib/api'
import { useAuth } from '@/lib/auth'
import { PageHeader, Toggle } from '@/pages/AppPages'

interface Memory {
  id: string
  content: string
  project_id: string | null
  source: string
  enabled: boolean
  updated_at: string
}

interface Summary {
  id: string
  conversation_id: string
  version: number
  content: Record<string, unknown>
  model: string
  created_at: string
}

function MemoryRow({ m }: { m: Memory }) {
  const qc = useQueryClient()
  const [editing, setEditing] = useState(false)
  const [text, setText] = useState(m.content)
  const done = () => void qc.invalidateQueries({ queryKey: ['memory'] })
  const update = useMutation({ mutationFn: (body: Partial<Memory>) => api(`/memory/${m.id}`, { method: 'PATCH', json: body }), onSuccess: done })
  const remove = useMutation({ mutationFn: () => api(`/memory/${m.id}`, { method: 'DELETE' }), onSuccess: done })
  return (
    <li className="flex items-center gap-3 rounded-lg border border-border bg-surface px-3 py-2">
      {editing ? (
        <form
          className="flex flex-1 gap-2"
          onSubmit={(e) => {
            e.preventDefault()
            update.mutate({ content: text })
            setEditing(false)
          }}
        >
          <Input value={text} maxLength={500} onChange={(e) => setText(e.target.value)} aria-label="Edit memory" autoFocus />
          <Button type="submit" size="sm">Save</Button>
        </form>
      ) : (
        <button type="button" className={`flex-1 text-left text-sm ${m.enabled ? '' : 'text-muted line-through'}`} onClick={() => setEditing(true)}>
          {m.content}
          {m.project_id ? <Badge className="ml-2">Project</Badge> : null}
        </button>
      )}
      <Toggle label={m.enabled ? 'Enabled' : 'Disabled'} checked={m.enabled} onChange={(v) => update.mutate({ enabled: v })} />
      <Button variant="ghost" size="icon" aria-label={`Delete memory: ${m.content}`} onClick={() => remove.mutate()}>
        <Trash2 className="h-4 w-4" />
      </Button>
    </li>
  )
}

export function MemoryPage() {
  const qc = useQueryClient()
  const { me, refresh } = useAuth()
  const [text, setText] = useState('')
  const memories = useQuery({ queryKey: ['memory'], queryFn: () => api<Memory[]>('/memory') })
  const summaries = useQuery({ queryKey: ['summaries'], queryFn: () => api<Summary[]>('/summaries') })
  const add = useMutation({
    mutationFn: () => api('/memory', { json: { content: text } }),
    onSuccess: () => {
      setText('')
      void qc.invalidateQueries({ queryKey: ['memory'] })
    },
  })
  const clearAll = useMutation({ mutationFn: () => api('/memory', { method: 'DELETE' }), onSuccess: () => void qc.invalidateQueries({ queryKey: ['memory'] }) })
  const delSummary = useMutation({
    mutationFn: (id: string) => api(`/summaries/${id}`, { method: 'DELETE' }),
    onSuccess: () => void qc.invalidateQueries({ queryKey: ['summaries'] }),
  })

  return (
    <div className="pb-10">
      <PageHeader title="Memory" subtitle="Durable memories are reused across chats. Continuation summaries are temporary and kept separately." />
      <div className="grid max-w-3xl gap-4 px-4 md:px-8">
        <Card className="space-y-4">
          <Toggle
            label="Use my memories in conversations"
            checked={me?.memory_enabled ?? true}
            onChange={(v) => void api('/auth/me', { method: 'PATCH', json: { memory_enabled: v } }).then(refresh)}
          />
          <form
            className="flex gap-2"
            onSubmit={(e) => {
              e.preventDefault()
              if (text.trim()) add.mutate()
            }}
          >
            <Input value={text} maxLength={500} placeholder="Something AURA should remember, e.g. 'I prefer short answers'" aria-label="New memory" onChange={(e) => setText(e.target.value)} />
            <Button type="submit" disabled={!text.trim() || add.isPending}>Add</Button>
          </form>
          {add.error ? <Alert tone="error">{add.error instanceof ApiError ? add.error.message : 'Could not add.'}</Alert> : null}
          <p className="text-xs text-muted">Don't store passwords, health or financial details here. Memories are only visible to you.</p>
        </Card>

        <Card className="space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="font-medium">Saved memories</h2>
            {memories.data?.length ? (
              <Button variant="ghost" size="sm" onClick={() => window.confirm('Delete all memories? This cannot be undone.') && clearAll.mutate()}>
                Delete all
              </Button>
            ) : null}
          </div>
          {memories.isPending ? <Spinner /> : null}
          {memories.data?.length === 0 ? <EmptyState title="No memories yet">Add one above.</EmptyState> : null}
          <ul className="space-y-2">{memories.data?.map((m) => <MemoryRow key={m.id} m={m} />)}</ul>
        </Card>

        <Card className="space-y-3">
          <h2 className="font-medium">Continuation summaries</h2>
          {summaries.data?.length === 0 ? <p className="text-sm text-muted">None yet. They appear when a long chat continues in a new one.</p> : null}
          <ul className="space-y-2">
            {summaries.data?.map((s) => (
              <li key={s.id} className="rounded-lg border border-border bg-surface p-3 text-sm">
                <div className="flex items-center gap-2">
                  <Link to={`/app/chat/${s.conversation_id}`} className="font-medium hover:underline">
                    {String(s.content.goal || 'Summary')} <span className="text-muted">v{s.version}</span>
                  </Link>
                  <Button variant="ghost" size="icon" className="ml-auto" aria-label="Delete summary" onClick={() => delSummary.mutate(s.id)}>
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
                <details className="mt-2 text-muted">
                  <summary className="cursor-pointer">Show details</summary>
                  <pre className="mt-2 whitespace-pre-wrap text-xs">{JSON.stringify(s.content, null, 2)}</pre>
                </details>
              </li>
            ))}
          </ul>
        </Card>
      </div>
    </div>
  )
}
