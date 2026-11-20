import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { motion } from 'motion/react'
import { CheckCircle2, CircleDashed, ExternalLink, OctagonX, XCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Alert, Textarea } from '@/components/ui/form'
import { Badge, Card, EmptyState, Spinner } from '@/components/ui/card'
import { api, ApiError } from '@/lib/api'
import type { ProviderInfo } from '@/lib/chat'
import { PageHeader } from '@/pages/AppPages'
import { cn } from '@/lib/utils'

interface Step {
  seq: number
  name: string
  tool: string | null
  status: 'running' | 'ok' | 'error' | 'skipped'
  summary: string
}

interface Source {
  title: string
  url: string
  published: string
  retrieved_at: string
}

export interface Run {
  id: string
  kind: 'research' | 'fact_check'
  title: string
  provider: string
  model: string
  search_provider: string
  status: 'queued' | 'running' | 'succeeded' | 'failed' | 'cancelled'
  current_step: string | null
  error: string | null
  created_at: string
  finished_at: string | null
  result: {
    report?: string
    cited?: number[]
    sources?: Source[]
    verdict?: string
    explanation?: string
    supporting?: number[]
    contradicting?: number[]
    demo?: boolean
  } | null
  steps: Step[]
}

const STATUS_TONE: Record<Run['status'], string> = {
  queued: 'text-muted',
  running: 'text-accent',
  succeeded: 'text-success',
  failed: 'text-danger',
  cancelled: 'text-warning',
}

const VERDICT_LABEL: Record<string, string> = {
  supported: 'Supported',
  contradicted: 'Contradicted',
  mixed: 'Mixed evidence',
  insufficient_evidence: 'Insufficient evidence',
}

export function NewRunPage({ kind }: { kind: Run['kind'] }) {
  const nav = useNavigate()
  const [text, setText] = useState('')
  const [model, setModel] = useState('mock|aura-mock-1')
  const providers = useQuery({ queryKey: ['models'], queryFn: () => api<ProviderInfo[]>('/models') })
  const runs = useQuery({ queryKey: ['runs', kind], queryFn: () => api<Run[]>(`/agent-runs?kind=${kind}`) })
  const create = useMutation({
    mutationFn: () => {
      const [provider, ...m] = model.split('|')
      return api<Run>('/agent-runs', { json: { kind, text, provider, model: m.join('|') } })
    },
    onSuccess: (r) => nav(`/app/agents/${r.id}`),
  })
  const research = kind === 'research'
  return (
    <div className="pb-10">
      <PageHeader
        title={research ? 'AI Research' : 'Fact Checker'}
        subtitle={research ? 'AURA plans searches, reads sources and writes a report where every claim is cited.' : 'Check a claim against supporting and contradicting sources.'}
      />
      <div className="grid max-w-4xl gap-4 px-4 md:px-8">
        <Card className="space-y-3">
          <form
            className="space-y-3"
            onSubmit={(e) => {
              e.preventDefault()
              if (text.trim().length >= 3) create.mutate()
            }}
          >
            <Textarea
              rows={3}
              maxLength={2000}
              value={text}
              onChange={(e) => setText(e.target.value)}
              aria-label={research ? 'Research question' : 'Claim to check'}
              placeholder={research ? 'What do you want to research?' : 'Paste a claim, e.g. "Lahore is the largest city in Pakistan."'}
            />
            <div className="flex flex-wrap items-center gap-2">
              <select aria-label="Model" value={model} onChange={(e) => setModel(e.target.value)} className="h-9 rounded-lg border border-border bg-surface px-2 text-sm">
                {providers.data?.map((p) =>
                  p.models.map((m) => (
                    <option key={`${p.id}|${m.id}`} value={`${p.id}|${m.id}`} disabled={!p.available}>
                      {p.name} · {m.label}
                      {!p.available ? ' (not configured)' : ''}
                    </option>
                  )),
                )}
              </select>
              <Button type="submit" className="ml-auto" disabled={create.isPending || text.trim().length < 3}>
                {research ? 'Start research' : 'Check claim'}
              </Button>
            </div>
          </form>
          {create.error ? <Alert tone="error">{create.error instanceof ApiError ? create.error.message : 'Could not start.'}</Alert> : null}
          <p className="text-xs text-muted">Without a configured search provider AURA uses clearly labelled offline demo sources.</p>
        </Card>
        <RunList runs={runs.data} loading={runs.isPending} />
      </div>
    </div>
  )
}

function RunList({ runs, loading }: { runs?: Run[]; loading: boolean }) {
  if (loading) return <Spinner />
  if (!runs?.length) return <EmptyState title="No runs yet" />
  return (
    <Card className="space-y-1">
      <h2 className="mb-2 font-medium">Recent runs</h2>
      {runs.map((r) => (
        <Link key={r.id} to={`/app/agents/${r.id}`} className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm hover:bg-surface-2">
          <span className="truncate">{r.title}</span>
          <span className={cn('ml-auto text-xs', STATUS_TONE[r.status])}>{r.status}</span>
        </Link>
      ))}
    </Card>
  )
}

export function ControlRoomPage() {
  const runs = useQuery({ queryKey: ['runs', 'all'], queryFn: () => api<Run[]>('/agent-runs'), refetchInterval: 3000 })
  return (
    <div className="pb-10">
      <PageHeader title="Agent Control Room" subtitle="Every agent task, its steps, tools and status." />
      <div className="grid max-w-4xl gap-4 px-4 md:px-8">
        <div className="flex gap-2">
          <Button asChild variant="secondary"><Link to="/app/research">New research</Link></Button>
          <Button asChild variant="secondary"><Link to="/app/fact-check">New fact check</Link></Button>
        </div>
        <RunList runs={runs.data} loading={runs.isPending} />
      </div>
    </div>
  )
}

function StepIcon({ status }: { status: Step['status'] }) {
  if (status === 'ok') return <CheckCircle2 className="h-4 w-4 text-success" aria-label="Done" />
  if (status === 'error') return <XCircle className="h-4 w-4 text-danger" aria-label="Failed" />
  return <CircleDashed className="h-4 w-4 animate-spin text-accent" aria-label="Running" />
}

/** Render report text with [n] citations as links to the source list. Text is rendered as text (no HTML). */
function CitedText({ text, sources }: { text: string; sources: Source[] }) {
  const parts = text.split(/(\[\d{1,3}\])/g)
  return (
    <p className="whitespace-pre-wrap text-sm leading-relaxed">
      {parts.map((p, i) => {
        const m = /^\[(\d{1,3})\]$/.exec(p)
        const src = m ? sources[Number(m[1]) - 1] : undefined
        return src ? (
          <a key={i} href={`#source-${m![1]}`} className="text-primary-strong hover:underline" title={src.title}>
            {p}
          </a>
        ) : (
          <span key={i}>{p}</span>
        )
      })}
    </p>
  )
}

export function RunDetailPage() {
  const { runId } = useParams()
  const qc = useQueryClient()
  const nav = useNavigate()
  const run = useQuery({ queryKey: ['run', runId], queryFn: () => api<Run>(`/agent-runs/${runId}`) })
  const active = run.data?.status === 'queued' || run.data?.status === 'running'

  useEffect(() => {
    if (!active) return
    const es = new EventSource(`/api/v1/agent-runs/${runId}/events`, { withCredentials: true })
    es.addEventListener('run', (e) => qc.setQueryData(['run', runId], JSON.parse((e as MessageEvent).data) as Run))
    es.onerror = () => es.close()
    return () => es.close()
  }, [active, runId, qc])

  const cancel = useMutation({ mutationFn: () => api<Run>(`/agent-runs/${runId}/cancel`, { method: 'POST' }), onSuccess: (r) => qc.setQueryData(['run', runId], r) })

  if (run.isPending) return <div className="p-8"><Spinner /></div>
  if (run.isError) return <div className="p-8"><Alert tone="error">Run not found.</Alert></div>
  const r = run.data
  const sources = r.result?.sources ?? []

  return (
    <div className="pb-10">
      <PageHeader
        title={r.title}
        subtitle={`${r.kind === 'research' ? 'Research' : 'Fact check'} · ${r.model} · search: ${r.search_provider}`}
        actions={
          active ? (
            <Button variant="danger" onClick={() => cancel.mutate()} disabled={cancel.isPending}>
              <OctagonX className="h-4 w-4" /> Cancel
            </Button>
          ) : (
            <Button
              variant="ghost"
              onClick={() => void api(`/agent-runs/${runId}`, { method: 'DELETE' }).then(() => nav('/app/agents'))}
            >
              Delete
            </Button>
          )
        }
      />
      <div className="grid max-w-4xl gap-4 px-4 md:px-8">
        <Card>
          <div className="mb-3 flex items-center gap-2">
            <h2 className="font-medium">Steps</h2>
            <span className={cn('text-sm', STATUS_TONE[r.status])}>{r.status}</span>
            {r.current_step ? <span className="text-sm text-muted">· {r.current_step}</span> : null}
          </div>
          <ol className="space-y-2">
            {r.steps.map((s) => (
              <motion.li key={s.seq} initial={{ opacity: 0, x: -6 }} animate={{ opacity: 1, x: 0 }} className="flex items-start gap-3 text-sm">
                <StepIcon status={s.status} />
                <div>
                  <p>{s.name} {s.tool ? <Badge className="ml-1">{s.tool}</Badge> : null}</p>
                  {s.summary ? <p className="text-xs text-muted">{s.summary}</p> : null}
                </div>
              </motion.li>
            ))}
            {r.steps.length === 0 && active ? <li><Spinner label="Starting" /></li> : null}
          </ol>
          {r.error ? <div className="mt-3"><Alert tone="error">{r.error}</Alert></div> : null}
        </Card>

        {r.result ? (
          <Card className="space-y-4">
            {r.result.demo ? <Alert tone="info">Demo result: generated with the offline demo model and/or placeholder sources, not real research.</Alert> : null}
            {r.result.verdict ? (
              <div>
                <p className="text-lg font-semibold">{VERDICT_LABEL[r.result.verdict] ?? r.result.verdict}</p>
                <CitedText text={r.result.explanation ?? ''} sources={sources} />
              </div>
            ) : null}
            {r.result.report ? <CitedText text={r.result.report} sources={sources} /> : null}
            <div>
              <h3 className="mb-2 text-sm font-medium">Sources</h3>
              <ol className="space-y-2 text-sm">
                {sources.map((s, i) => (
                  <li key={s.url} id={`source-${i + 1}`} className="flex gap-2">
                    <span className="text-muted">[{i + 1}]</span>
                    <div className="min-w-0">
                      <a href={s.url} target="_blank" rel="noopener noreferrer nofollow" className="inline-flex items-center gap-1 text-primary-strong hover:underline">
                        {s.title || s.url} <ExternalLink className="h-3 w-3" aria-hidden />
                      </a>
                      <p className="truncate text-xs text-muted">
                        {s.url} · retrieved {new Date(s.retrieved_at).toLocaleString()}
                        {s.published ? ` · published ${s.published}` : ''}
                      </p>
                    </div>
                  </li>
                ))}
              </ol>
            </div>
          </Card>
        ) : null}
      </div>
    </div>
  )
}
