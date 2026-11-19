import { Link } from 'react-router'
import { motion } from 'motion/react'
import { useMutation } from '@tanstack/react-query'
import { Badge, Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Alert, Field, Input } from '@/components/ui/form'
import { useAuth, type Me } from '@/lib/auth'
import { MODULES } from '@/lib/modules'
import { usePreferences, type MotionLevel, type Theme } from '@/lib/preferences'
import { api, ApiError } from '@/lib/api'
import { useState } from 'react'

export function PageHeader({ title, subtitle, actions }: { title: string; subtitle?: string; actions?: React.ReactNode }) {
  return (
    <div className="flex flex-wrap items-end justify-between gap-3 px-4 pb-4 pt-6 md:px-8">
      <div>
        <h1 className="text-2xl font-semibold">{title}</h1>
        {subtitle ? <p className="mt-1 text-sm text-muted">{subtitle}</p> : null}
      </div>
      {actions}
    </div>
  )
}

export function DashboardPage() {
  const { me } = useAuth()
  const live = MODULES.filter((m) => m.status === 'live' && m.id !== 'dashboard' && m.id !== 'modules' && (!m.adminOnly || me?.role === 'admin'))
  return (
    <div className="pb-10">
      <PageHeader title={`Welcome, ${me?.display_name ?? ''}`} subtitle="Your AURA workspace." />
      <div className="grid gap-4 px-4 sm:grid-cols-2 md:px-8 xl:grid-cols-3">
        {live.map((m, i) => (
          <motion.div key={m.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }}>
            <Link to={m.path} className="block h-full">
              <Card className="h-full transition-shadow hover:shadow-glow">
                <m.icon className="mb-3 h-5 w-5 text-primary-strong" aria-hidden />
                <p className="font-medium">{m.name}</p>
                <p className="mt-1 text-sm text-muted">{m.summary}</p>
              </Card>
            </Link>
          </motion.div>
        ))}
        <Link to="/app/modules" className="block">
          <Card className="h-full border-dashed transition-shadow hover:shadow-glow">
            <p className="font-medium">All modules</p>
            <p className="mt-1 text-sm text-muted">
              {MODULES.filter((m) => m.status === 'planned').length} modules are still being built. See the roadmap.
            </p>
          </Card>
        </Link>
      </div>
    </div>
  )
}

export function ModulesPage() {
  return (
    <div className="pb-10">
      <PageHeader title="All modules" subtitle="Live modules work today. Planned modules are listed with the build phase that delivers them." />
      <div className="grid gap-3 px-4 md:grid-cols-2 md:px-8">
        {MODULES.filter((m) => m.id !== 'modules').map((m) => (
          <Card key={m.id} className="flex items-start gap-3">
            <m.icon className="mt-0.5 h-5 w-5 text-muted" aria-hidden />
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2">
                <p className="font-medium">{m.name}</p>
                {m.status === 'live' ? (
                  <Badge className="border-success/50 text-success">Live</Badge>
                ) : (
                  <Badge>Planned · phase {m.phase}</Badge>
                )}
              </div>
              <p className="mt-1 text-sm text-muted">{m.summary}</p>
            </div>
          </Card>
        ))}
      </div>
    </div>
  )
}

function Choice<T extends string>({ label, value, options, onChange }: { label: string; value: T; options: { v: T; label: string }[]; onChange: (v: T) => void }) {
  return (
    <fieldset>
      <legend className="mb-2 text-sm font-medium">{label}</legend>
      <div className="inline-flex rounded-lg border border-border p-1" role="radiogroup" aria-label={label}>
        {options.map((o) => (
          <button
            key={o.v}
            type="button"
            role="radio"
            aria-checked={value === o.v}
            onClick={() => onChange(o.v)}
            className={`rounded-md px-3 py-1.5 text-sm ${value === o.v ? 'bg-primary text-primary-fg' : 'text-muted hover:text-fg'}`}
          >
            {o.label}
          </button>
        ))}
      </div>
    </fieldset>
  )
}

export function SettingsPage() {
  const { theme, setTheme, motion, setMotion } = usePreferences()
  const { me, refresh } = useAuth()
  const [name, setName] = useState(me?.display_name ?? '')
  const save = useMutation({
    mutationFn: (body: Partial<Record<string, unknown>>) => api<Me>('/auth/me', { method: 'PATCH', json: body }),
    onSuccess: () => void refresh(),
  })
  const err = save.error instanceof ApiError ? save.error.message : save.error ? 'Could not save.' : null

  return (
    <div className="pb-10">
      <PageHeader title="Settings" />
      <div className="grid max-w-3xl gap-4 px-4 md:px-8">
        {err ? <Alert tone="error">{err}</Alert> : null}
        {save.isSuccess ? <Alert tone="success">Saved.</Alert> : null}
        <Card className="space-y-5">
          <h2 className="font-medium">Appearance</h2>
          <Choice<Theme> label="Theme" value={theme} onChange={setTheme} options={[{ v: 'dark', label: 'Dark' }, { v: 'light', label: 'Light' }]} />
          <Choice<MotionLevel>
            label="Animation"
            value={motion}
            onChange={setMotion}
            options={[{ v: 'full', label: 'Full' }, { v: 'reduced', label: 'Reduced' }, { v: 'off', label: 'Off' }]}
          />
          <p className="text-xs text-muted">Your system's reduced-motion setting is always respected.</p>
        </Card>
        <Card className="space-y-4">
          <h2 className="font-medium">Profile</h2>
          <form
            className="flex items-end gap-2"
            onSubmit={(e) => {
              e.preventDefault()
              save.mutate({ display_name: name })
            }}
          >
            <div className="flex-1">
              <Field label="Display name" htmlFor="display-name">
                <Input id="display-name" value={name} maxLength={80} onChange={(e) => setName(e.target.value)} />
              </Field>
            </div>
            <Button type="submit" disabled={save.isPending || !name.trim()}>Save</Button>
          </form>
        </Card>
        <Card className="space-y-5">
          <h2 className="font-medium">Language and memory</h2>
          <Choice
            label="Reply language"
            value={(me?.language_override ?? 'auto') as 'auto' | 'en' | 'ur' | 'ur-Latn'}
            onChange={(v) => save.mutate({ language_override: v })}
            options={[
              { v: 'auto', label: 'Automatic' },
              { v: 'en', label: 'English' },
              { v: 'ur', label: 'اردو' },
              { v: 'ur-Latn', label: 'Roman Urdu' },
            ]}
          />
          <Toggle label="Remember useful details across chats" checked={me?.memory_enabled ?? true} onChange={(v) => save.mutate({ memory_enabled: v })} />
          <Toggle
            label="Continue long chats automatically from a summary"
            checked={me?.auto_continuation ?? true}
            onChange={(v) => save.mutate({ auto_continuation: v })}
          />
        </Card>
        <Card className="space-y-3">
          <h2 className="font-medium">Privacy</h2>
          <Toggle
            label="Allow sending my chat messages to external free-tier AI providers"
            checked={!!me?.provider_consent_at}
            onChange={(v) => save.mutate({ provider_consent: v })}
          />
          <p className="text-xs text-muted">
            Free-tier providers may use and review what you send. Without this consent you can still use the offline demo model.
          </p>
        </Card>
      </div>
    </div>
  )
}

export function Toggle({ label, checked, onChange }: { label: string; checked: boolean; onChange: (v: boolean) => void }) {
  return (
    <label className="flex cursor-pointer items-center justify-between gap-4 text-sm">
      <span>{label}</span>
      <button
        type="button"
        role="switch"
        aria-checked={checked}
        aria-label={label}
        onClick={() => onChange(!checked)}
        className={`relative h-6 w-11 rounded-full transition-colors ${checked ? 'bg-primary' : 'bg-surface-2 border border-border'}`}
      >
        <span className={`absolute top-0.5 h-5 w-5 rounded-full bg-white transition-transform ${checked ? 'translate-x-5' : 'translate-x-0.5'}`} />
      </button>
    </label>
  )
}

export function NotFoundPage() {
  return (
    <main className="aura-backdrop flex min-h-full flex-col items-center justify-center gap-4 p-8 text-center">
      <p className="text-5xl font-semibold">404</p>
      <p className="text-muted">This page does not exist.</p>
      <Button asChild><Link to="/">Go home</Link></Button>
    </main>
  )
}
