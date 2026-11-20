import { useRef, useState } from 'react'
import { useNavigate } from 'react-router'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Download, Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Alert, Field, Input, Textarea } from '@/components/ui/form'
import { Badge, Card, EmptyState, Spinner } from '@/components/ui/card'
import { api, ApiError } from '@/lib/api'
import type { ProviderInfo } from '@/lib/chat'
import { PageHeader, Toggle } from '@/pages/AppPages'

const errText = (e: unknown) => (e instanceof ApiError ? e.message : e ? 'Something went wrong.' : '')
const ErrorBox = ({ e }: { e: unknown }) => (e ? <Alert tone="error">{errText(e)}</Alert> : null)

function csrf() {
  const raw = document.cookie.split('; ').find((c) => c.startsWith('aura_csrf='))?.split('=')[1]
  return raw ? decodeURIComponent(raw) : ''
}

async function postForm<T>(path: string, form: FormData): Promise<T> {
  const res = await fetch(`/api/v1${path}`, { method: 'POST', body: form, credentials: 'same-origin', headers: { 'x-csrf-token': csrf() } })
  const data = (await res.json().catch(() => null)) as (T & { error?: { code: string; message: string } }) | null
  if (!res.ok) throw new ApiError(res.status, data?.error?.code ?? 'failed', data?.error?.message ?? 'Request failed')
  return data as T
}

function ModelSelect({ value, onChange, label = 'Model' }: { value: string; onChange: (v: string) => void; label?: string }) {
  const providers = useQuery({ queryKey: ['models'], queryFn: () => api<ProviderInfo[]>('/models') })
  return (
    <select aria-label={label} value={value} onChange={(e) => onChange(e.target.value)} className="h-9 rounded-lg border border-border bg-surface px-2 text-sm">
      {providers.data?.map((p) => p.models.map((m) => (
        <option key={`${p.id}|${m.id}`} value={`${p.id}|${m.id}`} disabled={!p.available}>{p.name} · {m.label}{!p.available ? ' (not configured)' : ''}</option>
      )))}
    </select>
  )
}
const split = (v: string) => { const [provider, ...m] = v.split('|'); return { provider, model: m.join('|') } }

// ---------------- Usage ----------------
export function UsagePage() {
  const q = useQuery({ queryKey: ['usage'], queryFn: () => api<{ today: Record<string, number>; daily_limit_per_provider: number; demo_daily_limit: number; paid_usage_enabled: boolean }>('/usage/me') })
  return (
    <div className="pb-10">
      <PageHeader title="Usage" subtitle="Requests you made today (UTC). Limits protect the shared free allowance." />
      <div className="grid max-w-3xl gap-4 px-4 md:px-8">
        {q.isPending ? <Spinner /> : null}
        {q.data ? (
          <Card className="space-y-3">
            {Object.keys(q.data.today).length === 0 ? <p className="text-sm text-muted">No requests yet today.</p> : null}
            {Object.entries(q.data.today).map(([p, n]) => {
              const limit = p === 'mock' ? q.data.demo_daily_limit : q.data.daily_limit_per_provider
              return (
                <div key={p}>
                  <div className="flex justify-between text-sm"><span>{p}</span><span>{n} / {limit}</span></div>
                  <div className="mt-1 h-2 rounded-full bg-surface-2" role="progressbar" aria-valuenow={n} aria-valuemax={limit} aria-label={`${p} usage`}>
                    <div className="h-2 rounded-full bg-primary" style={{ width: `${Math.min(100, (n / limit) * 100)}%` }} />
                  </div>
                </div>
              )
            })}
            <p className="text-xs text-muted">Paid providers: {q.data.paid_usage_enabled ? 'enabled by the administrator' : 'disabled'}. AURA never switches to a paid model on its own.</p>
          </Card>
        ) : null}
      </div>
    </div>
  )
}

// ---------------- Security Center ----------------
export function SecurityPage() {
  const qc = useQueryClient()
  const nav = useNavigate()
  const sessions = useQuery({ queryKey: ['sessions'], queryFn: () => api<{ id: string; created_at: string; last_seen_at: string; user_agent: string | null; current: boolean }[]>('/security/sessions') })
  const auditLog = useQuery({ queryKey: ['audit'], queryFn: () => api<{ at: string; action: string; detail: string | null }[]>('/security/audit') })
  const revoke = useMutation({ mutationFn: (id?: string) => (id ? api(`/security/sessions/${id}`, { method: 'DELETE' }) : api('/security/sessions/revoke-others', { method: 'POST' })), onSuccess: () => void qc.invalidateQueries({ queryKey: ['sessions'] }) })
  const [pw, setPw] = useState('')
  const [confirm, setConfirm] = useState('')
  const del = useMutation({ mutationFn: () => api('/security/delete-account', { json: { password: pw, confirm } }), onSuccess: () => { qc.clear(); nav('/') } })
  return (
    <div className="pb-10">
      <PageHeader title="Security Center" subtitle="Your sessions, activity, data export and account deletion." />
      <div className="grid max-w-3xl gap-4 px-4 md:px-8">
        <Card className="space-y-2">
          <div className="flex items-center justify-between"><h2 className="font-medium">Active sessions</h2><Button size="sm" variant="secondary" onClick={() => revoke.mutate(undefined)}>Sign out other sessions</Button></div>
          {sessions.data?.map((s) => (
            <div key={s.id} className="flex items-center gap-2 text-sm">
              <span className="truncate">{s.user_agent || 'Unknown device'}</span>
              {s.current ? <Badge>This device</Badge> : <Button size="sm" variant="ghost" className="ml-auto" onClick={() => revoke.mutate(s.id)}>Sign out</Button>}
            </div>
          ))}
        </Card>
        <Card className="space-y-2">
          <h2 className="font-medium">Your data</h2>
          <Button asChild variant="secondary"><a href="/api/v1/security/export"><Download className="h-4 w-4" /> Download all my data (JSON)</a></Button>
        </Card>
        <Card className="space-y-2">
          <h2 className="font-medium">Recent security activity</h2>
          <ul className="max-h-64 space-y-1 overflow-auto text-xs">{auditLog.data?.map((e, i) => <li key={i}><span className="text-muted">{new Date(e.at).toLocaleString()}</span> · {e.action}{e.detail ? ` · ${e.detail}` : ''}</li>)}</ul>
        </Card>
        <Card className="space-y-3 border-danger/40">
          <h2 className="font-medium text-danger">Delete account</h2>
          <p className="text-sm text-muted">This permanently deletes your account and everything in it. It cannot be undone.</p>
          <Field label="Password" htmlFor="del-pw"><Input id="del-pw" type="password" value={pw} onChange={(e) => setPw(e.target.value)} /></Field>
          <Field label='Type "DELETE" to confirm' htmlFor="del-confirm"><Input id="del-confirm" value={confirm} onChange={(e) => setConfirm(e.target.value)} /></Field>
          <Button variant="danger" disabled={confirm !== 'DELETE' || !pw || del.isPending} onClick={() => del.mutate()}>Delete my account</Button>
          <ErrorBox e={del.error} />
        </Card>
      </div>
    </div>
  )
}

// ---------------- Model Arena ----------------
type ArenaResult = { provider: string; model: string; served_by: string | null; output: string; error: string | null; latency_ms: number; tokens_in: number; tokens_out: number }
export function ArenaPage() {
  const [prompt, setPrompt] = useState('')
  const [models, setModels] = useState(['mock|aura-mock-1', 'mock|aura-mock-1'])
  const run = useMutation({ mutationFn: () => api<{ results: ArenaResult[]; note: string }>('/arena', { json: { prompt, contenders: models.map(split) } }) })
  return (
    <div className="pb-10">
      <PageHeader title="Model Arena" subtitle="Send one prompt to several models and compare their answers side by side." />
      <div className="grid gap-4 px-4 md:px-8">
        <Card className="space-y-3">
          <Textarea rows={3} value={prompt} maxLength={8000} onChange={(e) => setPrompt(e.target.value)} aria-label="Prompt" placeholder="Prompt for all models…" />
          <div className="flex flex-wrap items-center gap-2">
            {models.map((m, i) => <ModelSelect key={i} label={`Model ${i + 1}`} value={m} onChange={(v) => setModels(models.map((x, j) => (j === i ? v : x)))} />)}
            {models.length < 3 ? <Button size="sm" variant="secondary" onClick={() => setModels([...models, 'mock|aura-mock-1'])}>Add model</Button> : null}
            <Button className="ml-auto" disabled={!prompt.trim() || run.isPending} onClick={() => run.mutate()}>{run.isPending ? <Spinner label="Comparing" /> : 'Compare'}</Button>
          </div>
          <ErrorBox e={run.error} />
        </Card>
        {run.data ? (
          <div className="grid gap-4 md:grid-cols-3">
            {run.data.results.map((r, i) => (
              <Card key={i} className="space-y-2">
                <p className="text-sm font-medium">{r.served_by ?? `${r.provider}/${r.model}`}</p>
                <p className="text-xs text-muted">{r.latency_ms} ms · {r.tokens_in}→{r.tokens_out} tokens</p>
                {r.error ? <Alert tone="error">{r.error}</Alert> : <p className="whitespace-pre-wrap text-sm">{r.output}</p>}
              </Card>
            ))}
            <p className="text-xs text-muted md:col-span-3">{run.data.note}</p>
          </div>
        ) : null}
      </div>
    </div>
  )
}

// ---------------- Evaluation Center ----------------
type EvalSet = { id: string; name: string; cases: { input: string; expected: string }[] }
type EvalRun = { id: string; provider: string; model: string; passed: number; total: number; avg_latency_ms: number; created_at: string; results: { output: string; expected: string; passed: boolean; error: string | null }[] }
export function EvaluationPage() {
  const qc = useQueryClient()
  const sets = useQuery({ queryKey: ['evalsets'], queryFn: () => api<EvalSet[]>('/evaluations/datasets') })
  const [name, setName] = useState('My test set')
  const [cases, setCases] = useState('What is 2+2? => 4\nCapital of Pakistan? => Islamabad')
  const [active, setActive] = useState<string | null>(null)
  const [model, setModel] = useState('mock|aura-mock-1')
  const parsed = cases.split('\n').map((l) => l.split('=>').map((s) => s.trim())).filter((p) => p.length === 2 && p[0] && p[1]).map(([input, expected]) => ({ input, expected }))
  const create = useMutation({ mutationFn: () => api<EvalSet>('/evaluations/datasets', { json: { name, cases: parsed } }), onSuccess: (s) => { void qc.invalidateQueries({ queryKey: ['evalsets'] }); setActive(s.id) } })
  const runs = useQuery({ queryKey: ['evalruns', active], queryFn: () => api<EvalRun[]>(`/evaluations/datasets/${active}/runs`), enabled: !!active })
  const run = useMutation({ mutationFn: () => api(`/evaluations/datasets/${active}/runs`, { json: { ...split(model) } }), onSuccess: () => void qc.invalidateQueries({ queryKey: ['evalruns', active] }) })
  return (
    <div className="pb-10">
      <PageHeader title="Evaluation Center" subtitle="Repeatable checks: each case passes when the answer contains the expected text." />
      <div className="grid gap-4 px-4 md:px-8 lg:grid-cols-2">
        <Card className="space-y-3">
          <h2 className="font-medium">New test set</h2>
          <Input value={name} maxLength={120} onChange={(e) => setName(e.target.value)} aria-label="Test set name" />
          <Textarea rows={5} value={cases} onChange={(e) => setCases(e.target.value)} aria-label="Cases" className="font-mono text-xs" />
          <p className="text-xs text-muted">One case per line: <code>input =&gt; expected text</code>. Use synthetic data, not private content.</p>
          <Button disabled={!parsed.length || create.isPending} onClick={() => create.mutate()}>Save {parsed.length} cases</Button>
          <ErrorBox e={create.error} />
          <ul className="space-y-1">{sets.data?.map((s) => <li key={s.id}><button type="button" className={`w-full rounded-lg px-2 py-1.5 text-left text-sm ${s.id === active ? 'bg-primary/15' : 'hover:bg-surface-2'}`} onClick={() => setActive(s.id)}>{s.name} <span className="text-xs text-muted">({s.cases.length})</span></button></li>)}</ul>
        </Card>
        <Card className="space-y-3">
          {!active ? <EmptyState title="Select a test set" /> : (
            <>
              <div className="flex gap-2"><ModelSelect value={model} onChange={setModel} /><Button disabled={run.isPending} onClick={() => run.mutate()}>{run.isPending ? <Spinner label="Running" /> : 'Run evaluation'}</Button></div>
              <ErrorBox e={run.error} />
              {runs.data?.map((r) => (
                <details key={r.id} className="rounded-lg border border-border p-3 text-sm">
                  <summary className="cursor-pointer"><strong>{r.passed}/{r.total}</strong> passed · {r.provider}/{r.model} · {r.avg_latency_ms} ms avg</summary>
                  <ol className="mt-2 space-y-1 text-xs">{r.results.map((c, i) => <li key={i} className={c.passed ? 'text-success' : 'text-danger'}>{c.passed ? 'PASS' : 'FAIL'} · expected "{c.expected}" · {c.error ?? c.output.slice(0, 120)}</li>)}</ol>
                </details>
              ))}
            </>
          )}
        </Card>
      </div>
    </div>
  )
}

// ---------------- OCR / Vision / Audio ----------------
const MEDIA = {
  ocr: { title: 'OCR', sub: 'Extract text from an image. Images are re-encoded first, which removes hidden metadata such as location.', path: '/media/ocr', accept: 'image/*', engines: [['mock', 'Offline demo'], ['local', 'Tesseract (if installed)'], ['gemini', 'Google Gemini (free tier)']] },
  vision: { title: 'Vision', sub: 'Ask a question about an image.', path: '/media/vision', accept: 'image/*', engines: [['mock', 'Offline demo'], ['gemini', 'Google Gemini (free tier)']] },
  audio: { title: 'Audio', sub: 'Transcribe an audio file (mp3, wav, m4a, ogg, webm, flac).', path: '/media/transcribe', accept: 'audio/*', engines: [['mock', 'Offline demo'], ['groq', 'Groq Whisper (free tier)']] },
} as const
export function MediaPage({ kind }: { kind: keyof typeof MEDIA }) {
  const cfg = MEDIA[kind]
  const input = useRef<HTMLInputElement>(null)
  const [engine, setEngine] = useState('mock')
  const [question, setQuestion] = useState('Describe this image.')
  const run = useMutation({
    mutationFn: (file: File) => {
      const f = new FormData()
      f.append('file', file)
      f.append('engine', engine)
      if (kind === 'vision') f.append('question', question)
      return postForm<{ text?: string; answer?: string; demo: boolean; image?: Record<string, unknown> }>(cfg.path, f)
    },
  })
  return (
    <div className="pb-10">
      <PageHeader title={cfg.title} subtitle={cfg.sub} />
      <div className="grid max-w-3xl gap-4 px-4 md:px-8">
        <Card className="space-y-3">
          <select aria-label="Engine" value={engine} onChange={(e) => setEngine(e.target.value)} className="h-9 rounded-lg border border-border bg-surface px-2 text-sm">
            {cfg.engines.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
          </select>
          {kind === 'vision' ? <Input value={question} maxLength={2000} onChange={(e) => setQuestion(e.target.value)} aria-label="Question" /> : null}
          <input ref={input} type="file" accept={cfg.accept} className="sr-only" aria-label="Choose file" onChange={(e) => { const f = e.target.files?.[0]; if (f) run.mutate(f); e.target.value = '' }} />
          <Button onClick={() => input.current?.click()} disabled={run.isPending}>{run.isPending ? <Spinner label="Processing" /> : 'Choose file'}</Button>
          <p className="text-xs text-muted">External engines need your consent in Settings and send the file to that provider.</p>
          <ErrorBox e={run.error} />
        </Card>
        {run.data ? (
          <Card className="space-y-2">
            {run.data.demo ? <Alert tone="info">Demo result from the offline engine.</Alert> : null}
            <pre className="whitespace-pre-wrap text-sm">{run.data.text ?? run.data.answer}</pre>
            {run.data.image ? <p className="text-xs text-muted">{String(run.data.image.width)}×{String(run.data.image.height)} {String(run.data.image.format)}{run.data.image.had_exif ? ' · metadata removed' : ''}</p> : null}
          </Card>
        ) : null}
      </div>
    </div>
  )
}

// ---------------- Integrations ----------------
export function IntegrationsPage() {
  const qc = useQueryClient()
  const tools = useQuery({ queryKey: ['tools'], queryFn: () => api<{ id: string; name: string; description: string; scopes: string[]; enabled: boolean }[]>('/integrations') })
  const grant = useMutation({ mutationFn: (v: { id: string; enabled: boolean }) => api(`/integrations/${v.id}`, { method: 'PUT', json: { enabled: v.enabled } }), onSuccess: () => void qc.invalidateQueries({ queryKey: ['tools'] }) })
  const [query, setQuery] = useState<Record<string, string>>({})
  const invoke = useMutation({ mutationFn: (id: string) => api<unknown>(`/integrations/${id}/invoke`, { json: { query: query[id] ?? '' } }) })
  return (
    <div className="pb-10">
      <PageHeader title="Integrations" subtitle="Approved read-only tools. Each one must be enabled by you, and every use is logged in the Security Center." />
      <div className="grid max-w-3xl gap-4 px-4 md:px-8">
        {tools.data?.map((t) => (
          <Card key={t.id} className="space-y-3">
            <Toggle label={t.name} checked={t.enabled} onChange={(v) => grant.mutate({ id: t.id, enabled: v })} />
            <p className="text-sm text-muted">{t.description}</p>
            <div className="flex flex-wrap gap-1">{t.scopes.map((s) => <Badge key={s}>{s}</Badge>)}</div>
            {t.enabled ? (
              <div className="flex gap-2">
                <Input value={query[t.id] ?? ''} onChange={(e) => setQuery({ ...query, [t.id]: e.target.value })} placeholder={t.id === 'web_fetch' ? 'https://…' : 'Search text'} aria-label={`${t.name} input`} />
                <Button onClick={() => invoke.mutate(t.id)} disabled={(query[t.id] ?? '').length < 2}>Try</Button>
              </div>
            ) : null}
          </Card>
        ))}
        <ErrorBox e={invoke.error} />
        {invoke.data ? <Card><pre className="max-h-80 overflow-auto whitespace-pre-wrap text-xs">{JSON.stringify(invoke.data, null, 2)}</pre></Card> : null}
        <p className="text-xs text-muted">Connecting external MCP servers is not available in the beta for security reasons.</p>
      </div>
    </div>
  )
}

// ---------------- Knowledge Graph ----------------
type Graph = { note: string; entities: { id: string; name: string; mentions: number }[]; links: { a: string; b: string; weight: number; provenance: { document: string; part: number; sentence: string }[] }[] }
export function GraphPage() {
  const qc = useQueryClient()
  const g = useQuery({ queryKey: ['graph'], queryFn: () => api<Graph>('/graph') })
  const build = useMutation({ mutationFn: () => api<{ entities: number; links: number }>('/graph/build', { method: 'POST' }), onSuccess: () => void qc.invalidateQueries({ queryKey: ['graph'] }) })
  const del = useMutation({ mutationFn: (id: string) => api(`/graph/entities/${id}`, { method: 'DELETE' }), onSuccess: () => void qc.invalidateQueries({ queryKey: ['graph'] }) })
  const name = (id: string) => g.data?.entities.find((e) => e.id === id)?.name ?? '?'
  return (
    <div className="pb-10">
      <PageHeader title="Knowledge Graph" subtitle="People, places and organisations found in your Knowledge Base documents." actions={<Button onClick={() => build.mutate()} disabled={build.isPending}>{build.isPending ? <Spinner label="Building" /> : 'Rebuild from documents'}</Button>} />
      <div className="grid gap-4 px-4 md:px-8 lg:grid-cols-2">
        <ErrorBox e={build.error} />
        <Card className="space-y-2">
          <h2 className="font-medium">Entities</h2>
          {g.data?.entities.length === 0 ? <EmptyState title="Nothing yet">Upload documents, then rebuild.</EmptyState> : null}
          <ul className="flex flex-wrap gap-2">{g.data?.entities.map((e) => (
            <li key={e.id} className="flex items-center gap-1 rounded-full border border-border px-2 py-0.5 text-xs">{e.name} <span className="text-muted">{e.mentions}</span>
              <button type="button" aria-label={`Remove ${e.name}`} onClick={() => del.mutate(e.id)} className="text-muted hover:text-danger"><Trash2 className="h-3 w-3" /></button></li>
          ))}</ul>
        </Card>
        <Card className="space-y-2">
          <h2 className="font-medium">Links</h2>
          <p className="text-xs text-muted">{g.data?.note}</p>
          <ul className="max-h-[32rem] space-y-2 overflow-auto text-sm">{g.data?.links.slice(0, 100).map((l, i) => (
            <li key={i}><strong>{name(l.a)}</strong> ↔ <strong>{name(l.b)}</strong> <span className="text-xs text-muted">×{l.weight}</span>
              <p className="text-xs text-muted">“{l.provenance[0]?.sentence}” — {l.provenance[0]?.document}, part {l.provenance[0]?.part}</p></li>
          ))}</ul>
        </Card>
      </div>
    </div>
  )
}
