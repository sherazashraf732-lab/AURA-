import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ArrowDown, ArrowUp, Plus, Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Alert, Input, Textarea } from '@/components/ui/form'
import { Badge, Card, EmptyState } from '@/components/ui/card'
import { api, ApiError } from '@/lib/api'
import { PageHeader } from '@/pages/AppPages'

type Step =
  | { type: 'llm'; name: string; prompt: string }
  | { type: 'approval'; name: string; message?: string }
  | { type: 'template'; name: string; template: string }
interface Workflow { id: string; name: string; version: number; steps: Step[] }
interface Run { id: string; status: string; step_index: number; input: string; log: { name: string; type: string; output?: string; error?: string; served_by?: string }[]; error: string | null }

const NEW_STEP: Record<Step['type'], Step> = {
  llm: { type: 'llm', name: 'AI step', prompt: 'Summarise: {{previous}}' },
  approval: { type: 'approval', name: 'Approval' },
  template: { type: 'template', name: 'Text', template: '{{input}}' },
}

function Editor({ initial, onSaved }: { initial?: Workflow; onSaved: () => void }) {
  const [name, setName] = useState(initial?.name ?? 'My workflow')
  const [steps, setSteps] = useState<Step[]>(initial?.steps ?? [NEW_STEP.template, NEW_STEP.llm, NEW_STEP.approval])
  const save = useMutation({
    mutationFn: () =>
      initial ? api(`/workflows/${initial.id}`, { method: 'PUT', json: { name, steps } }) : api('/workflows', { json: { name, steps } }),
    onSuccess: onSaved,
  })
  const set = (i: number, s: Step) => setSteps(steps.map((x, j) => (j === i ? s : x)))
  const move = (i: number, d: number) => {
    const next = [...steps]
    ;[next[i], next[i + d]] = [next[i + d], next[i]]
    setSteps(next)
  }
  return (
    <Card className="space-y-3">
      <Input value={name} maxLength={120} onChange={(e) => setName(e.target.value)} aria-label="Workflow name" />
      <ol className="space-y-2">
        {steps.map((s, i) => (
          <li key={i} className="space-y-2 rounded-lg border border-border p-3">
            <div className="flex items-center gap-2">
              <Badge>{i + 1} · {s.type}</Badge>
              <Input className="h-8" value={s.name} maxLength={80} onChange={(e) => set(i, { ...s, name: e.target.value })} aria-label={`Step ${i + 1} name`} />
              <Button variant="ghost" size="icon" aria-label="Move up" disabled={i === 0} onClick={() => move(i, -1)}><ArrowUp className="h-4 w-4" /></Button>
              <Button variant="ghost" size="icon" aria-label="Move down" disabled={i === steps.length - 1} onClick={() => move(i, 1)}><ArrowDown className="h-4 w-4" /></Button>
              <Button variant="ghost" size="icon" aria-label={`Delete step ${i + 1}`} onClick={() => setSteps(steps.filter((_, j) => j !== i))}><Trash2 className="h-4 w-4" /></Button>
            </div>
            {s.type === 'llm' ? <Textarea rows={2} value={s.prompt} maxLength={4000} onChange={(e) => set(i, { ...s, prompt: e.target.value })} aria-label={`Step ${i + 1} prompt`} /> : null}
            {s.type === 'template' ? <Textarea rows={2} value={s.template} maxLength={8000} onChange={(e) => set(i, { ...s, template: e.target.value })} aria-label={`Step ${i + 1} text`} /> : null}
            {s.type === 'approval' ? <p className="text-xs text-muted">The run pauses here until you approve it.</p> : null}
          </li>
        ))}
      </ol>
      <p className="text-xs text-muted">Use {'{{input}}'} for the run input and {'{{previous}}'} for the previous step's output.</p>
      <div className="flex flex-wrap gap-2">
        {(['llm', 'template', 'approval'] as const).map((t) => (
          <Button key={t} variant="secondary" size="sm" onClick={() => setSteps([...steps, NEW_STEP[t]])} disabled={steps.length >= 20}><Plus className="h-4 w-4" /> {t}</Button>
        ))}
        <Button className="ml-auto" onClick={() => save.mutate()} disabled={save.isPending || !steps.length || !name.trim()}>Save</Button>
      </div>
      {save.error ? <Alert tone="error">{save.error instanceof ApiError ? save.error.message : 'Could not save.'}</Alert> : null}
    </Card>
  )
}

function Runs({ wf }: { wf: Workflow }) {
  const qc = useQueryClient()
  const [input, setInput] = useState('')
  const key = ['wf-runs', wf.id]
  const runs = useQuery({ queryKey: key, queryFn: () => api<Run[]>(`/workflows/${wf.id}/runs`) })
  const done = () => void qc.invalidateQueries({ queryKey: key })
  const start = useMutation({ mutationFn: () => api<Run>(`/workflows/${wf.id}/runs`, { json: { input } }), onSuccess: done })
  const decide = useMutation({ mutationFn: (v: { id: string; approve: boolean }) => api(`/workflows/runs/${v.id}/decision`, { json: { approve: v.approve } }), onSuccess: done })
  const err = start.error ?? decide.error
  return (
    <Card className="space-y-3">
      <div className="flex gap-2">
        <Input value={input} maxLength={8000} onChange={(e) => setInput(e.target.value)} placeholder="Run input" aria-label="Run input" />
        <Button onClick={() => start.mutate()} disabled={start.isPending}>Run</Button>
      </div>
      {err ? <Alert tone="error">{err instanceof ApiError ? err.message : 'Failed.'}</Alert> : null}
      {runs.data?.map((r) => (
        <div key={r.id} className="space-y-2 rounded-lg border border-border p-3 text-sm">
          <div className="flex items-center gap-2"><Badge>{r.status}</Badge><span className="truncate text-muted">{r.input}</span></div>
          <ol className="space-y-1 text-xs">
            {r.log.map((l, i) => <li key={i}><strong>{l.name}</strong> ({l.type}){l.error ? <span className="text-danger"> {l.error}</span> : l.output ? <span className="text-muted"> → {l.output.slice(0, 300)}</span> : null}</li>)}
          </ol>
          {r.status === 'waiting_for_approval' ? (
            <div className="flex gap-2">
              <Button size="sm" onClick={() => decide.mutate({ id: r.id, approve: true })}>Approve and continue</Button>
              <Button size="sm" variant="secondary" onClick={() => decide.mutate({ id: r.id, approve: false })}>Reject</Button>
            </div>
          ) : null}
        </div>
      ))}
    </Card>
  )
}

export function WorkflowsPage() {
  const qc = useQueryClient()
  const list = useQuery({ queryKey: ['workflows'], queryFn: () => api<Workflow[]>('/workflows') })
  const [selected, setSelected] = useState<string | 'new' | null>(null)
  const refresh = () => void qc.invalidateQueries({ queryKey: ['workflows'] })
  const del = useMutation({ mutationFn: (id: string) => api(`/workflows/${id}`, { method: 'DELETE' }), onSuccess: () => { refresh(); setSelected(null) } })
  const wf = list.data?.find((w) => w.id === selected)
  return (
    <div className="pb-10">
      <PageHeader title="Workflows" subtitle="Chain AI and text steps, with approval checkpoints. Workflows cannot take actions outside AURA." actions={<Button onClick={() => setSelected('new')}><Plus className="h-4 w-4" /> New workflow</Button>} />
      <div className="grid gap-4 px-4 md:px-8 lg:grid-cols-[16rem_1fr]">
        <Card className="space-y-1 self-start">
          {list.data?.length === 0 ? <EmptyState title="No workflows" /> : null}
          {list.data?.map((w) => (
            <div key={w.id} className="flex items-center gap-1">
              <button type="button" onClick={() => setSelected(w.id)} className={`flex-1 truncate rounded-lg px-2 py-1.5 text-left text-sm ${w.id === selected ? 'bg-primary/15' : 'hover:bg-surface-2'}`}>{w.name} <span className="text-xs text-muted">v{w.version}</span></button>
              <button type="button" aria-label={`Delete ${w.name}`} className="rounded p-1 text-muted hover:text-fg" onClick={() => del.mutate(w.id)}><Trash2 className="h-4 w-4" /></button>
            </div>
          ))}
        </Card>
        <div className="space-y-4">
          {selected === 'new' ? <Editor onSaved={() => { refresh(); setSelected(null) }} /> : null}
          {wf ? <><Editor key={`${wf.id}-${wf.version}`} initial={wf} onSaved={refresh} /><Runs wf={wf} /></> : null}
          {!selected ? <EmptyState title="Select or create a workflow" /> : null}
        </div>
      </div>
    </div>
  )
}
