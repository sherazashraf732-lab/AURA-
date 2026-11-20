import { useRef, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Bar, BarChart, CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { Download, Table2, Trash2, Upload } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Alert } from '@/components/ui/form'
import { Card, EmptyState, Spinner } from '@/components/ui/card'
import { api, ApiError } from '@/lib/api'
import { usePreferences } from '@/lib/preferences'
import { PageHeader } from '@/pages/AppPages'

interface Dataset { id: string; name: string; columns: string[]; row_count: number }
interface ColumnProfile { name: string; type: 'number' | 'text'; count: number; missing: number; mean?: number; min?: number; max?: number; median?: number; unique?: number }
interface Detail extends Dataset { preview: string[][]; profile: ColumnProfile[] }
interface ChartData { points: { x: string; y: number }[]; source: string }

function csrf() {
  const raw = document.cookie.split('; ').find((c) => c.startsWith('aura_csrf='))?.split('=')[1]
  return raw ? decodeURIComponent(raw) : ''
}

async function importFile(file: File): Promise<Dataset> {
  const body = new FormData()
  body.append('file', file)
  const res = await fetch('/api/v1/data/datasets?dedupe=true', { method: 'POST', body, credentials: 'same-origin', headers: { 'x-csrf-token': csrf() } })
  const data = (await res.json().catch(() => null)) as (Dataset & { error?: { code: string; message: string } }) | null
  if (!res.ok) throw new ApiError(res.status, data?.error?.code ?? 'import_failed', data?.error?.message ?? 'Import failed')
  return data as Dataset
}

const select = 'h-9 rounded-lg border border-border bg-surface px-2 text-sm'

function DatasetView({ id }: { id: string }) {
  const { motion } = usePreferences()
  const detail = useQuery({ queryKey: ['dataset', id], queryFn: () => api<Detail>(`/data/datasets/${id}`) })
  const [x, setX] = useState('')
  const [y, setY] = useState('')
  const [agg, setAgg] = useState('sum')
  const [kind, setKind] = useState<'bar' | 'line'>('bar')
  const d = detail.data
  const numeric = d?.profile.filter((c) => c.type === 'number').map((c) => c.name) ?? []
  const xCol = x || d?.columns[0] || ''
  const yCol = y || numeric[0] || ''
  const chart = useQuery({
    queryKey: ['chart', id, xCol, yCol, agg],
    queryFn: () => api<ChartData>(`/data/datasets/${id}/chart?x=${encodeURIComponent(xCol)}${yCol && agg !== 'count' ? `&y=${encodeURIComponent(yCol)}` : ''}&agg=${agg}`),
    enabled: !!xCol,
  })
  if (detail.isPending) return <Spinner />
  if (!d) return <Alert tone="error">Dataset not found.</Alert>
  const yLabel = agg === 'count' ? 'Count of rows' : `${agg} of ${yCol}`

  return (
    <div className="space-y-4">
      <Card className="space-y-3">
        <div className="flex flex-wrap items-center gap-2">
          <label className="text-sm">X <select className={select} value={xCol} onChange={(e) => setX(e.target.value)}>{d.columns.map((c) => <option key={c}>{c}</option>)}</select></label>
          <label className="text-sm">Y <select className={select} value={yCol} onChange={(e) => setY(e.target.value)} disabled={agg === 'count' || !numeric.length}>{numeric.map((c) => <option key={c}>{c}</option>)}</select></label>
          <label className="text-sm">Aggregate <select className={select} value={agg} onChange={(e) => setAgg(e.target.value)}>{['sum', 'mean', 'count', 'min', 'max'].map((a) => <option key={a}>{a}</option>)}</select></label>
          <label className="text-sm">Chart <select className={select} value={kind} onChange={(e) => setKind(e.target.value as 'bar' | 'line')}><option value="bar">Bar</option><option value="line">Line</option></select></label>
        </div>
        <figure>
          <div className="h-72" role="img" aria-label={`${kind} chart of ${yLabel} by ${xCol}`}>
            {chart.data ? (
              <ResponsiveContainer>
                {kind === 'bar' ? (
                  <BarChart data={chart.data.points}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                    <XAxis dataKey="x" stroke="var(--text-muted)" fontSize={12} />
                    <YAxis stroke="var(--text-muted)" fontSize={12} />
                    <Tooltip contentStyle={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)' }} />
                    <Bar dataKey="y" name={yLabel} fill="var(--primary)" isAnimationActive={motion !== 'off'} />
                  </BarChart>
                ) : (
                  <LineChart data={chart.data.points}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                    <XAxis dataKey="x" stroke="var(--text-muted)" fontSize={12} />
                    <YAxis stroke="var(--text-muted)" fontSize={12} />
                    <Tooltip contentStyle={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)' }} />
                    <Line dataKey="y" name={yLabel} stroke="var(--accent)" isAnimationActive={motion !== 'off'} />
                  </LineChart>
                )}
              </ResponsiveContainer>
            ) : <Spinner />}
          </div>
          <figcaption className="text-xs text-muted">{yLabel} by {xCol} · source: {d.name} ({d.row_count} rows; top 50 groups)</figcaption>
        </figure>
        {chart.error ? <Alert tone="error">{chart.error instanceof ApiError ? chart.error.message : 'Chart failed.'}</Alert> : null}
      </Card>

      <Card className="overflow-auto">
        <h2 className="mb-2 font-medium">Column summary</h2>
        <table className="w-full text-left text-xs">
          <thead className="text-muted"><tr>{['Column', 'Type', 'Values', 'Missing', 'Mean', 'Min', 'Max', 'Unique'].map((h) => <th key={h} className="px-2 py-1">{h}</th>)}</tr></thead>
          <tbody>
            {d.profile.map((c) => (
              <tr key={c.name} className="border-t border-border">
                <td className="px-2 py-1 font-medium">{c.name}</td><td className="px-2 py-1">{c.type}</td><td className="px-2 py-1">{c.count}</td><td className="px-2 py-1">{c.missing}</td>
                <td className="px-2 py-1">{c.mean ?? ''}</td><td className="px-2 py-1">{c.min ?? ''}</td><td className="px-2 py-1">{c.max ?? ''}</td><td className="px-2 py-1">{c.unique ?? ''}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>

      <Card className="overflow-auto">
        <h2 className="mb-2 font-medium">Preview (first 50 rows)</h2>
        <table className="w-full text-left text-xs">
          <thead className="text-muted"><tr>{d.columns.map((c) => <th key={c} className="px-2 py-1">{c}</th>)}</tr></thead>
          <tbody>{d.preview.map((r, i) => <tr key={i} className="border-t border-border">{r.map((v, j) => <td key={j} className="px-2 py-1">{v}</td>)}</tr>)}</tbody>
        </table>
      </Card>
    </div>
  )
}

export function DataPage() {
  const qc = useQueryClient()
  const input = useRef<HTMLInputElement>(null)
  const [active, setActive] = useState<string | null>(null)
  const list = useQuery({ queryKey: ['datasets'], queryFn: () => api<Dataset[]>('/data/datasets') })
  const refresh = () => void qc.invalidateQueries({ queryKey: ['datasets'] })
  const imp = useMutation({ mutationFn: importFile, onSuccess: (d) => { refresh(); setActive(d.id) } })
  const del = useMutation({ mutationFn: (id: string) => api(`/data/datasets/${id}`, { method: 'DELETE' }), onSuccess: () => { refresh(); setActive(null) } })
  const current = active ?? list.data?.[0]?.id ?? null

  return (
    <div className="pb-10">
      <PageHeader title="Data Studio" subtitle="Import CSV or Excel, see column statistics, chart it and export cleaned data." />
      <div className="grid gap-4 px-4 md:px-8 lg:grid-cols-[16rem_1fr]">
        <Card className="space-y-2 self-start">
          <input ref={input} type="file" accept=".csv,.xlsx" className="sr-only" aria-label="Choose table" onChange={(e) => { const f = e.target.files?.[0]; if (f) imp.mutate(f); e.target.value = '' }} />
          <Button className="w-full" onClick={() => input.current?.click()} disabled={imp.isPending}>
            {imp.isPending ? <Spinner label="Importing" /> : <><Upload className="h-4 w-4" /> Import CSV / XLSX</>}
          </Button>
          {imp.error ? <Alert tone="error">{imp.error instanceof ApiError ? imp.error.message : 'Import failed.'}</Alert> : null}
          <p className="text-xs text-muted">Up to 50,000 rows. Blank and duplicate rows are removed.</p>
          {list.data?.length === 0 ? <EmptyState title="No datasets" /> : null}
          <ul className="space-y-1">
            {list.data?.map((d) => (
              <li key={d.id} className="flex items-center gap-1">
                <button type="button" onClick={() => setActive(d.id)} className={`flex flex-1 items-center gap-2 truncate rounded-lg px-2 py-1.5 text-left text-sm ${d.id === current ? 'bg-primary/15' : 'hover:bg-surface-2'}`}>
                  <Table2 className="h-4 w-4 shrink-0 text-muted" aria-hidden /> <span className="truncate">{d.name}</span>
                </button>
                <a className="rounded p-1 text-muted hover:text-fg" href={`/api/v1/data/datasets/${d.id}/export?format=xlsx`} aria-label={`Export ${d.name} as Excel`}><Download className="h-4 w-4" /></a>
                <button type="button" className="rounded p-1 text-muted hover:text-fg" aria-label={`Delete ${d.name}`} onClick={() => del.mutate(d.id)}><Trash2 className="h-4 w-4" /></button>
              </li>
            ))}
          </ul>
        </Card>
        <div>{current ? <DatasetView key={current} id={current} /> : <EmptyState title="Import a table to begin" />}</div>
      </div>
    </div>
  )
}
