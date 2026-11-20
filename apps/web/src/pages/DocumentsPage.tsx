import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Download, Plus, Trash2, Wand2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Alert, Field, Input, Textarea } from '@/components/ui/form'
import { Card, Spinner } from '@/components/ui/card'
import { api, ApiError } from '@/lib/api'
import { PageHeader } from '@/pages/AppPages'

interface Section {
  heading: string
  paragraphs: string[]
  bullets: string[]
  table: { columns: string[]; rows: string[][] } | null
}
interface Doc {
  title: string
  sections: Section[]
}

const FORMATS = ['docx', 'pptx', 'xlsx', 'pdf'] as const
const EMPTY: Doc = { title: 'Untitled document', sections: [{ heading: '', paragraphs: [''], bullets: [], table: null }] }

function csrf(): string {
  const raw = document.cookie.split('; ').find((c) => c.startsWith('aura_csrf='))?.split('=')[1]
  return raw ? decodeURIComponent(raw) : ''
}

async function download(format: string, content: Doc) {
  const res = await fetch('/api/v1/documents/render', {
    method: 'POST',
    credentials: 'same-origin',
    headers: { 'content-type': 'application/json', 'x-csrf-token': csrf() },
    body: JSON.stringify({ format, content }),
  })
  if (!res.ok) {
    const e = (await res.json().catch(() => null)) as { error?: { code: string; message: string } } | null
    throw new ApiError(res.status, e?.error?.code ?? 'render_failed', e?.error?.message ?? 'Export failed')
  }
  const url = URL.createObjectURL(await res.blob())
  const a = Object.assign(document.createElement('a'), { href: url, download: `${content.title || 'document'}.${format}` })
  a.click()
  URL.revokeObjectURL(url)
}

/** Paragraphs are edited as blank-line separated text; bullets one per line. */
const toLines = (v: string, sep: RegExp) => v.split(sep).map((s) => s.trim()).filter(Boolean)

export function DocumentsPage() {
  const [doc, setDoc] = useState<Doc>(EMPTY)
  const [prompt, setPrompt] = useState('')
  const [version, setVersion] = useState(0) // remounts the uncontrolled text areas after a new draft
  const draft = useMutation({
    mutationFn: () => api<Doc>('/documents/draft', { json: { prompt } }),
    onSuccess: (d) => {
      setDoc(d)
      setVersion((v) => v + 1)
    },
  })
  const exp = useMutation({ mutationFn: (f: string) => download(f, doc) })
  const setSection = (i: number, patch: Partial<Section>) =>
    setDoc((d) => ({ ...d, sections: d.sections.map((s, j) => (j === i ? { ...s, ...patch } : s)) }))
  const err = (e: unknown) => (e instanceof ApiError ? e.message : 'Something went wrong.')

  return (
    <div className="pb-10">
      <PageHeader title="Document Studio" subtitle="Draft with AI or write yourself, then export editable Word, PowerPoint, Excel or PDF files." />
      <div className="grid max-w-4xl gap-4 px-4 md:px-8">
        <Card className="space-y-3">
          <form
            className="flex items-end gap-2"
            onSubmit={(e) => {
              e.preventDefault()
              if (prompt.trim().length >= 3) draft.mutate()
            }}
          >
            <Textarea rows={2} value={prompt} maxLength={4000} onChange={(e) => setPrompt(e.target.value)} aria-label="Describe the document" placeholder="Describe the document you need…" />
            <Button type="submit" disabled={draft.isPending || prompt.trim().length < 3}>
              {draft.isPending ? <Spinner label="Drafting" /> : <><Wand2 className="h-4 w-4" /> Draft</>}
            </Button>
          </form>
          {draft.error ? <Alert tone="error">{err(draft.error)}</Alert> : null}
          <p className="text-xs text-muted">The demo model returns a placeholder draft; choose a real provider in Chat settings once configured.</p>
        </Card>

        <Card className="space-y-4">
          <Field label="Title" htmlFor="doc-title">
            <Input id="doc-title" value={doc.title} maxLength={300} onChange={(e) => setDoc({ ...doc, title: e.target.value })} />
          </Field>
          {doc.sections.map((s, i) => (
            <div key={`${version}-${i}`} className="space-y-2 rounded-lg border border-border p-3">
              <div className="flex gap-2">
                <Input value={s.heading} maxLength={300} placeholder="Section heading" aria-label={`Section ${i + 1} heading`} onChange={(e) => setSection(i, { heading: e.target.value })} />
                <Button variant="ghost" size="icon" aria-label={`Remove section ${i + 1}`} onClick={() => setDoc({ ...doc, sections: doc.sections.filter((_, j) => j !== i) })}>
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
              <Textarea
                rows={3}
                aria-label={`Section ${i + 1} text`}
                placeholder="Paragraphs (separate with a blank line)"
                defaultValue={s.paragraphs.join('\n\n')}
                onBlur={(e) => setSection(i, { paragraphs: toLines(e.target.value, /\n\s*\n/) })}
              />
              <Textarea
                rows={2}
                aria-label={`Section ${i + 1} bullets`}
                placeholder="Bullet points (one per line)"
                defaultValue={s.bullets.join('\n')}
                onBlur={(e) => setSection(i, { bullets: toLines(e.target.value, /\n/) })}
              />
              {s.table ? <p className="text-xs text-muted">Includes a table with {s.table.rows.length} rows ({s.table.columns.join(', ')}).</p> : null}
            </div>
          ))}
          <Button variant="secondary" onClick={() => setDoc({ ...doc, sections: [...doc.sections, { heading: '', paragraphs: [], bullets: [], table: null }] })}>
            <Plus className="h-4 w-4" /> Add section
          </Button>
        </Card>

        <Card className="flex flex-wrap items-center gap-2">
          <span className="text-sm font-medium">Export</span>
          {FORMATS.map((f) => (
            <Button key={f} variant="secondary" disabled={exp.isPending || !doc.title.trim()} onClick={() => exp.mutate(f)}>
              <Download className="h-4 w-4" /> {f.toUpperCase()}
            </Button>
          ))}
          {exp.error ? <div className="w-full"><Alert tone="error">{err(exp.error)}</Alert></div> : null}
          <p className="w-full text-xs text-muted">PDF export does not yet render Urdu script correctly; use DOCX or PPTX for Urdu text.</p>
        </Card>
      </div>
    </div>
  )
}
