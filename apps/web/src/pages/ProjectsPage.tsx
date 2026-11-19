import { useState } from 'react'
import { useNavigate, useParams } from 'react-router'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { MessageSquarePlus } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Alert, Field, Input, Textarea } from '@/components/ui/form'
import { Card, EmptyState, Spinner } from '@/components/ui/card'
import { api, ApiError } from '@/lib/api'
import type { Conversation } from '@/lib/chat'
import { PageHeader } from '@/pages/AppPages'

interface Project {
  id: string
  name: string
  description: string
  instructions: string
  archived: boolean
  updated_at: string
}

export function ProjectsPage() {
  const nav = useNavigate()
  const qc = useQueryClient()
  const [name, setName] = useState('')
  const list = useQuery({ queryKey: ['projects'], queryFn: () => api<Project[]>('/projects') })
  const create = useMutation({
    mutationFn: () => api<Project>('/projects', { json: { name } }),
    onSuccess: (p) => {
      void qc.invalidateQueries({ queryKey: ['projects'] })
      nav(`/app/projects/${p.id}`)
    },
  })
  return (
    <div className="pb-10">
      <PageHeader title="Projects" subtitle="Keep chats, instructions and memory for one piece of work together." />
      <div className="grid max-w-4xl gap-4 px-4 md:px-8">
        <form
          className="flex gap-2"
          onSubmit={(e) => {
            e.preventDefault()
            if (name.trim()) create.mutate()
          }}
        >
          <Input value={name} maxLength={120} placeholder="New project name" aria-label="New project name" onChange={(e) => setName(e.target.value)} />
          <Button type="submit" disabled={!name.trim()}>Create</Button>
        </form>
        {list.isPending ? <Spinner /> : null}
        {list.data?.length === 0 ? <EmptyState title="No projects yet" /> : null}
        <div className="grid gap-3 sm:grid-cols-2">
          {list.data?.map((p) => (
            <button key={p.id} type="button" onClick={() => nav(`/app/projects/${p.id}`)} className="text-left">
              <Card className="h-full transition-shadow hover:shadow-glow">
                <p className="font-medium">{p.name}</p>
                <p className="mt-1 line-clamp-2 text-sm text-muted">{p.description || 'No description'}</p>
              </Card>
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

export function ProjectDetailPage() {
  const { projectId } = useParams()
  const nav = useNavigate()
  const qc = useQueryClient()
  const project = useQuery({ queryKey: ['project', projectId], queryFn: () => api<Project>(`/projects/${projectId}`) })
  const chats = useQuery({ queryKey: ['conversations', 'project', projectId], queryFn: () => api<Conversation[]>(`/conversations?project_id=${projectId}`) })
  const [form, setForm] = useState<Partial<Project> | null>(null)
  const values = { ...project.data, ...form }
  const save = useMutation({
    mutationFn: () => api<Project>(`/projects/${projectId}`, { method: 'PATCH', json: form }),
    onSuccess: () => {
      setForm(null)
      void qc.invalidateQueries({ queryKey: ['project', projectId] })
      void qc.invalidateQueries({ queryKey: ['projects'] })
    },
  })
  const newChat = useMutation({
    mutationFn: () => api<Conversation>('/conversations', { json: { provider: 'mock', model: 'aura-mock-1', project_id: projectId } }),
    onSuccess: (c) => nav(`/app/chat/${c.id}`),
  })

  if (project.isPending) return <div className="p-8"><Spinner /></div>
  if (project.isError) return <div className="p-8"><Alert tone="error">Project not found.</Alert></div>

  return (
    <div className="pb-10">
      <PageHeader
        title={project.data.name}
        actions={<Button onClick={() => newChat.mutate()}><MessageSquarePlus className="h-4 w-4" /> New chat in project</Button>}
      />
      <div className="grid max-w-4xl gap-4 px-4 md:px-8">
        {save.error ? <Alert tone="error">{save.error instanceof ApiError ? save.error.message : 'Could not save.'}</Alert> : null}
        {newChat.error ? <Alert tone="error">{newChat.error instanceof ApiError ? newChat.error.message : 'Could not create chat.'}</Alert> : null}
        <Card className="space-y-4">
          <Field label="Name" htmlFor="p-name">
            <Input id="p-name" value={values.name ?? ''} maxLength={120} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          </Field>
          <Field label="Description" htmlFor="p-desc">
            <Textarea id="p-desc" rows={2} value={values.description ?? ''} maxLength={2000} onChange={(e) => setForm({ ...form, description: e.target.value })} />
          </Field>
          <Field label="Instructions for AURA in this project" htmlFor="p-ins" hint="Used in every chat inside this project.">
            <Textarea id="p-ins" rows={5} value={values.instructions ?? ''} maxLength={8000} onChange={(e) => setForm({ ...form, instructions: e.target.value })} />
          </Field>
          <div className="flex gap-2">
            <Button disabled={!form || save.isPending} onClick={() => save.mutate()}>Save</Button>
            <Button
              variant="danger"
              onClick={() =>
                window.confirm('Delete this project? Its chats are kept but no longer grouped.') &&
                void api(`/projects/${projectId}`, { method: 'DELETE' }).then(() => {
                  void qc.invalidateQueries({ queryKey: ['projects'] })
                  nav('/app/projects')
                })
              }
            >
              Delete project
            </Button>
          </div>
        </Card>
        <Card className="space-y-2">
          <h2 className="font-medium">Chats</h2>
          {chats.data?.length === 0 ? <p className="text-sm text-muted">No chats in this project yet.</p> : null}
          <ul className="space-y-1">
            {chats.data?.map((c) => (
              <li key={c.id}>
                <button type="button" className="w-full rounded-lg px-3 py-2 text-left text-sm hover:bg-surface-2" onClick={() => nav(`/app/chat/${c.id}`)}>
                  {c.title}
                </button>
              </li>
            ))}
          </ul>
        </Card>
      </div>
    </div>
  )
}
