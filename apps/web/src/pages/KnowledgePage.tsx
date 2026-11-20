import { useRef, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { FileText, Trash2, Upload } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Alert, Textarea } from '@/components/ui/form'
import { Card, EmptyState, Spinner } from '@/components/ui/card'
import { api, ApiError } from '@/lib/api'
import { PageHeader } from '@/pages/AppPages'

interface Source {
  id: string
  filename: string
  kind: string
  size_bytes: number
  chunk_count: number
  created_at: string
}

interface Answer {
  answer: string
  demo?: boolean
  citations: { n: number; filename: string; part: number; excerpt: string }[]
}

function csrf(): string {
  const raw = document.cookie.split('; ').find((c) => c.startsWith('aura_csrf='))?.split('=')[1]
  return raw ? decodeURIComponent(raw) : ''
}

async function uploadFile(file: File): Promise<Source> {
  const body = new FormData()
  body.append('file', file)
  const res = await fetch('/api/v1/knowledge/sources', { method: 'POST', body, credentials: 'same-origin', headers: { 'x-csrf-token': csrf() } })
  const data = (await res.json().catch(() => null)) as (Source & { error?: { code: string; message: string } }) | null
  if (!res.ok) throw new ApiError(res.status, data?.error?.code ?? 'upload_failed', data?.error?.message ?? 'Upload failed')
  return data as Source
}

export function KnowledgePage() {
  const qc = useQueryClient()
  const input = useRef<HTMLInputElement>(null)
  const [question, setQuestion] = useState('')
  const sources = useQuery({ queryKey: ['knowledge'], queryFn: () => api<Source[]>('/knowledge/sources') })
  const refresh = () => void qc.invalidateQueries({ queryKey: ['knowledge'] })
  const upload = useMutation({ mutationFn: uploadFile, onSuccess: refresh })
  const remove = useMutation({ mutationFn: (id: string) => api(`/knowledge/sources/${id}`, { method: 'DELETE' }), onSuccess: refresh })
  const ask = useMutation({ mutationFn: () => api<Answer>('/knowledge/ask', { json: { question } }) })
  const errMsg = (e: unknown) => (e instanceof ApiError ? e.message : 'Something went wrong.')

  return (
    <div className="pb-10">
      <PageHeader title="Knowledge Base" subtitle="Upload documents, then ask questions. Answers cite the passages they use." />
      <div className="grid max-w-4xl gap-4 px-4 md:px-8">
        <Card className="space-y-3">
          <div className="flex flex-wrap items-center gap-3">
            <input
              ref={input}
              type="file"
              accept=".txt,.md,.csv,.pdf,.docx"
              className="sr-only"
              aria-label="Choose document"
              onChange={(e) => {
                const f = e.target.files?.[0]
                if (f) upload.mutate(f)
                e.target.value = ''
              }}
            />
            <Button onClick={() => input.current?.click()} disabled={upload.isPending}>
              {upload.isPending ? <Spinner label="Uploading" /> : <><Upload className="h-4 w-4" /> Upload document</>}
            </Button>
            <span className="text-xs text-muted">.txt, .md, .csv, .pdf, .docx · only the text is stored · visible only to you</span>
          </div>
          {upload.error ? <Alert tone="error">{errMsg(upload.error)}</Alert> : null}
          {sources.isPending ? <Spinner /> : null}
          {sources.data?.length === 0 ? <EmptyState title="No documents yet" /> : null}
          <ul className="space-y-1">
            {sources.data?.map((s) => (
              <li key={s.id} className="flex items-center gap-3 rounded-lg px-2 py-1.5 text-sm hover:bg-surface-2">
                <FileText className="h-4 w-4 text-muted" aria-hidden />
                <span className="truncate">{s.filename}</span>
                <span className="text-xs text-muted">{s.chunk_count} parts · {(s.size_bytes / 1024).toFixed(0)} KB</span>
                <Button variant="ghost" size="icon" className="ml-auto" aria-label={`Delete ${s.filename}`} onClick={() => remove.mutate(s.id)}>
                  <Trash2 className="h-4 w-4" />
                </Button>
              </li>
            ))}
          </ul>
        </Card>

        <Card className="space-y-3">
          <form
            className="flex items-end gap-2"
            onSubmit={(e) => {
              e.preventDefault()
              if (question.trim().length >= 2) ask.mutate()
            }}
          >
            <Textarea rows={2} value={question} maxLength={2000} onChange={(e) => setQuestion(e.target.value)} aria-label="Question about your documents" placeholder="Ask about your documents…" />
            <Button type="submit" disabled={ask.isPending || question.trim().length < 2}>Ask</Button>
          </form>
          {ask.isPending ? <Spinner label="Searching documents" /> : null}
          {ask.error ? <Alert tone="error">{errMsg(ask.error)}</Alert> : null}
          {ask.data ? (
            <div className="space-y-3">
              {ask.data.demo ? <Alert tone="info">Demo answer from the offline model; the citations are real matches from your documents.</Alert> : null}
              <p className="whitespace-pre-wrap text-sm leading-relaxed">{ask.data.answer}</p>
              <ol className="space-y-2">
                {ask.data.citations.map((c) => (
                  <li key={c.n} className="rounded-lg border border-border bg-surface p-3 text-xs">
                    <p className="font-medium">[{c.n}] {c.filename} · part {c.part}</p>
                    <p className="mt-1 text-muted">{c.excerpt}</p>
                  </li>
                ))}
              </ol>
            </div>
          ) : null}
        </Card>
      </div>
    </div>
  )
}
