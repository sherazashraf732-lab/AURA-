import { useState } from 'react'
import { Navigate } from 'react-router'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { Alert, Input } from '@/components/ui/form'
import { Badge, Card, Spinner } from '@/components/ui/card'
import { api, ApiError } from '@/lib/api'
import { useAuth } from '@/lib/auth'
import { PageHeader } from '@/pages/AppPages'

interface Stats {
  users: number; verified_users: number; suspended_users: number; active_today: number; failed_runs_today: number
  usage_today: { provider: string; requests: number; tokens_in: number; tokens_out: number; daily_cap: number | null }[]
  providers: { id: string; name: string; configured: boolean; paid: boolean }[]
  paid_usage_enabled: boolean
}
interface AdminUser { id: string; email: string; display_name: string; role: string; email_verified_at: string | null; suspended_at: string | null; created_at: string }

export function AdminPage() {
  const { me } = useAuth()
  const qc = useQueryClient()
  const [q, setQ] = useState('')
  const stats = useQuery({ queryKey: ['admin-stats'], queryFn: () => api<Stats>('/admin/stats'), enabled: me?.role === 'admin', refetchInterval: 30000 })
  const users = useQuery({ queryKey: ['admin-users', q], queryFn: () => api<AdminUser[]>(`/admin/users${q ? `?q=${encodeURIComponent(q)}` : ''}`), enabled: me?.role === 'admin' })
  const auditLog = useQuery({ queryKey: ['admin-audit'], queryFn: () => api<{ at: string; action: string; target: string | null; detail: string | null }[]>('/admin/audit?limit=50'), enabled: me?.role === 'admin' })
  const suspend = useMutation({
    mutationFn: (v: { id: string; suspended: boolean }) => api(`/admin/users/${v.id}/suspend`, { json: { suspended: v.suspended, reason: v.suspended ? window.prompt('Reason (optional)') ?? '' : '' } }),
    onSuccess: () => { void qc.invalidateQueries({ queryKey: ['admin-users'] }); void qc.invalidateQueries({ queryKey: ['admin-audit'] }) },
  })
  if (me?.role !== 'admin') return <Navigate to="/app" replace />
  const s = stats.data
  return (
    <div className="pb-10">
      <PageHeader title="Admin" subtitle="Service health, usage, users and moderation." />
      <div className="grid gap-4 px-4 md:px-8">
        {stats.isPending ? <Spinner /> : null}
        {s ? (
          <>
            <div className="grid gap-3 sm:grid-cols-5">
              {([['Users', s.users], ['Verified', s.verified_users], ['Suspended', s.suspended_users], ['Active today', s.active_today], ['Failed runs today', s.failed_runs_today]] as const).map(([l, v]) => (
                <Card key={l}><p className="text-xs text-muted">{l}</p><p className="text-2xl font-semibold">{v}</p></Card>
              ))}
            </div>
            <div className="grid gap-4 lg:grid-cols-2">
              <Card className="space-y-2">
                <h2 className="font-medium">Usage today</h2>
                {s.usage_today.length === 0 ? <p className="text-sm text-muted">No requests yet.</p> : null}
                {s.usage_today.map((u) => <p key={u.provider} className="text-sm">{u.provider}: {u.requests}{u.daily_cap ? ` / ${u.daily_cap}` : ''} requests · {u.tokens_in + u.tokens_out} tokens</p>)}
                <p className="text-xs text-muted">Paid usage: {s.paid_usage_enabled ? 'ENABLED' : 'disabled'}</p>
              </Card>
              <Card className="space-y-1">
                <h2 className="font-medium">Providers</h2>
                {s.providers.map((p) => <p key={p.id} className="flex items-center gap-2 text-sm">{p.name} <Badge className={p.configured ? 'border-success/50 text-success' : ''}>{p.configured ? 'configured' : 'no key'}</Badge></p>)}
              </Card>
            </div>
          </>
        ) : null}
        <Card className="space-y-2 overflow-auto">
          <div className="flex items-center gap-2"><h2 className="font-medium">Users</h2><Input className="ml-auto h-8 w-60" placeholder="Search email or name" value={q} onChange={(e) => setQ(e.target.value)} aria-label="Search users" /></div>
          {suspend.error ? <Alert tone="error">{suspend.error instanceof ApiError ? suspend.error.message : 'Failed.'}</Alert> : null}
          <table className="w-full text-left text-xs">
            <thead className="text-muted"><tr><th className="p-1">Email</th><th className="p-1">Name</th><th className="p-1">Status</th><th className="p-1">Joined</th><th /></tr></thead>
            <tbody>{users.data?.map((u) => (
              <tr key={u.id} className="border-t border-border">
                <td className="p-1">{u.email}</td><td className="p-1">{u.display_name}</td>
                <td className="p-1">{u.suspended_at ? 'suspended' : u.email_verified_at ? 'verified' : 'unverified'}{u.role === 'admin' ? ' · admin' : ''}</td>
                <td className="p-1">{new Date(u.created_at).toLocaleDateString()}</td>
                <td className="p-1 text-right">{u.id !== me.id ? <Button size="sm" variant={u.suspended_at ? 'secondary' : 'danger'} onClick={() => suspend.mutate({ id: u.id, suspended: !u.suspended_at })}>{u.suspended_at ? 'Unsuspend' : 'Suspend'}</Button> : null}</td>
              </tr>
            ))}</tbody>
          </table>
        </Card>
        <Card className="space-y-1">
          <h2 className="font-medium">Audit log</h2>
          <ul className="max-h-72 space-y-1 overflow-auto text-xs">{auditLog.data?.map((e, i) => <li key={i}><span className="text-muted">{new Date(e.at).toLocaleString()}</span> · {e.action}{e.target ? ` · ${e.target}` : ''}{e.detail ? ` · ${e.detail}` : ''}</li>)}</ul>
        </Card>
      </div>
    </div>
  )
}
