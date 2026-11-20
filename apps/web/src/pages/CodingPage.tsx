import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { Alert, Input, Textarea } from '@/components/ui/form'
import { Card, Spinner } from '@/components/ui/card'
import { api, ApiError } from '@/lib/api'
import { PageHeader } from '@/pages/AppPages'

const TASKS = [
  { v: 'explain', label: 'Explain' },
  { v: 'review', label: 'Review' },
  { v: 'debug', label: 'Debug' },
  { v: 'tests', label: 'Write tests' },
  { v: 'generate', label: 'Generate' },
] as const

export function CodingPage() {
  const [task, setTask] = useState<(typeof TASKS)[number]['v']>('explain')
  const [code, setCode] = useState('')
  const [notes, setNotes] = useState('')
  const [lang, setLang] = useState('')
  const run = useMutation({
    mutationFn: () => api<{ result: string; served_by: string; demo: boolean }>('/coding/assist', { json: { task, code, notes, language: lang } }),
  })
  return (
    <div className="pb-10">
      <PageHeader title="Coding Lab" subtitle="Explain, review, debug and test code. AURA never runs your code in the beta." />
      <div className="grid max-w-5xl gap-4 px-4 md:px-8">
        <Card className="space-y-3">
          <div className="flex flex-wrap gap-2" role="radiogroup" aria-label="Task">
            {TASKS.map((t) => (
              <Button key={t.v} role="radio" aria-checked={task === t.v} variant={task === t.v ? 'primary' : 'secondary'} size="sm" onClick={() => setTask(t.v)}>
                {t.label}
              </Button>
            ))}
            <Input className="ml-auto h-8 w-40" value={lang} maxLength={40} onChange={(e) => setLang(e.target.value)} placeholder="Language (e.g. Python)" aria-label="Programming language" />
          </div>
          <Textarea rows={12} value={code} maxLength={60000} onChange={(e) => setCode(e.target.value)} className="font-mono text-xs" aria-label="Code" placeholder="Paste code here…" spellCheck={false} />
          <Textarea rows={2} value={notes} maxLength={4000} onChange={(e) => setNotes(e.target.value)} aria-label="Notes" placeholder={task === 'generate' ? 'Describe the code you need' : 'Error message, expected behaviour or context (optional)'} />
          <Button onClick={() => run.mutate()} disabled={run.isPending || (!code.trim() && !notes.trim())}>{run.isPending ? <Spinner label="Working" /> : 'Run'}</Button>
        </Card>
        {run.error ? <Alert tone="error">{run.error instanceof ApiError ? run.error.message : 'Request failed.'}</Alert> : null}
        {run.data ? (
          <Card className="space-y-2">
            {run.data.demo ? <Alert tone="info">Demo reply from the offline model.</Alert> : null}
            <pre className="whitespace-pre-wrap break-words text-sm">{run.data.result}</pre>
            <p className="text-xs text-muted">Answered by {run.data.served_by}. Not executed.</p>
          </Card>
        ) : null}
      </div>
    </div>
  )
}
