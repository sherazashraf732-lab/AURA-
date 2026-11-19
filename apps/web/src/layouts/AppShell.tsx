import { useEffect, useMemo, useState } from 'react'
import { Navigate, NavLink, Outlet, useLocation, useNavigate } from 'react-router'
import { AnimatePresence, motion } from 'motion/react'
import * as Dialog from '@radix-ui/react-dialog'
import { LogOut, Menu, Moon, Search, Sun, X } from 'lucide-react'
import { AuraMark } from '@/components/brand/AuraMark'
import { Button } from '@/components/ui/button'
import { Alert } from '@/components/ui/form'
import { Spinner } from '@/components/ui/card'
import { useAuth } from '@/lib/auth'
import { MODULES } from '@/lib/modules'
import { usePreferences } from '@/lib/preferences'
import { api } from '@/lib/api'
import { cn } from '@/lib/utils'

function NavItems({ onNavigate }: { onNavigate?: () => void }) {
  const { me } = useAuth()
  const items = MODULES.filter((m) => m.status === 'live' && (!m.adminOnly || me?.role === 'admin'))
  return (
    <nav aria-label="Main" className="flex flex-col gap-1">
      {items.map((m) => (
        <NavLink
          key={m.id}
          to={m.path}
          end={m.path === '/app'}
          onClick={onNavigate}
          className={({ isActive }) =>
            cn(
              'flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors',
              isActive ? 'bg-primary/15 text-fg shadow-[inset_2px_0_0_var(--primary)]' : 'text-muted hover:bg-surface-2 hover:text-fg',
            )
          }
        >
          <m.icon className="h-4 w-4" aria-hidden /> {m.name}
        </NavLink>
      ))}
    </nav>
  )
}

function CommandPalette({ open, onOpenChange }: { open: boolean; onOpenChange: (o: boolean) => void }) {
  const nav = useNavigate()
  const { me } = useAuth()
  const [q, setQ] = useState('')
  const results = useMemo(
    () =>
      MODULES.filter((m) => m.status === 'live' && (!m.adminOnly || me?.role === 'admin')).filter((m) =>
        `${m.name} ${m.summary}`.toLowerCase().includes(q.toLowerCase()),
      ),
    [q, me],
  )
  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-40 bg-black/50 backdrop-blur-sm" />
        <Dialog.Content className="fixed left-1/2 top-24 z-50 w-[min(560px,92vw)] -translate-x-1/2 rounded-xl border border-border bg-bg-elevated p-2 shadow-glow">
          <Dialog.Title className="sr-only">Command palette</Dialog.Title>
          <Dialog.Description className="sr-only">Search pages and jump to them.</Dialog.Description>
          <input
            autoFocus
            value={q}
            onChange={(e) => setQ(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && results[0]) {
                nav(results[0].path)
                onOpenChange(false)
              }
            }}
            placeholder="Go to…"
            aria-label="Search pages"
            className="h-11 w-full rounded-lg bg-transparent px-3 text-sm outline-none"
          />
          <ul className="max-h-72 overflow-auto">
            {results.map((m) => (
              <li key={m.id}>
                <button
                  type="button"
                  className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left text-sm hover:bg-surface-2"
                  onClick={() => {
                    nav(m.path)
                    onOpenChange(false)
                  }}
                >
                  <m.icon className="h-4 w-4 text-muted" aria-hidden />
                  <span>{m.name}</span>
                  <span className="ml-auto truncate text-xs text-muted">{m.summary}</span>
                </button>
              </li>
            ))}
            {results.length === 0 ? <li className="px-3 py-4 text-sm text-muted">No matches.</li> : null}
          </ul>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}

function VerifyBanner() {
  const { me } = useAuth()
  const [sent, setSent] = useState(false)
  if (!me || me.email_verified) return null
  return (
    <div className="px-4 pt-4 md:px-8">
      <Alert tone="info">
        Verify your email to start using AI features.{' '}
        {sent ? (
          'A new link was sent.'
        ) : (
          <button
            type="button"
            className="font-medium text-primary-strong underline"
            onClick={() => void api('/auth/resend-verification', { json: { email: me.email } }).then(() => setSent(true))}
          >
            Resend link
          </button>
        )}
      </Alert>
    </div>
  )
}

export function AppShell() {
  const { me, loading, logout } = useAuth()
  const { theme, setTheme } = usePreferences()
  const [palette, setPalette] = useState(false)
  const [mobileNav, setMobileNav] = useState(false)
  const location = useLocation()
  const nav = useNavigate()

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault()
        setPalette((p) => !p)
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [])

  if (loading)
    return (
      <div className="flex h-full items-center justify-center">
        <Spinner label="Loading workspace" />
      </div>
    )
  if (!me) return <Navigate to="/login" replace />

  return (
    <div className="aura-backdrop flex h-full">
      <aside className="hidden w-64 shrink-0 flex-col border-r border-border bg-bg-elevated/70 p-4 backdrop-blur md:flex">
        <div className="mb-6 flex items-center gap-2 px-2 font-semibold tracking-wide">
          <AuraMark size={30} /> AURA
        </div>
        <NavItems />
      </aside>

      <Dialog.Root open={mobileNav} onOpenChange={setMobileNav}>
        <Dialog.Portal>
          <Dialog.Overlay className="fixed inset-0 z-40 bg-black/50 md:hidden" />
          <Dialog.Content className="fixed inset-y-0 left-0 z-50 w-72 border-r border-border bg-bg-elevated p-4 md:hidden">
            <Dialog.Title className="mb-4 flex items-center justify-between font-semibold">
              <span className="flex items-center gap-2"><AuraMark size={28} /> AURA</span>
              <Dialog.Close asChild><Button variant="ghost" size="icon" aria-label="Close menu"><X className="h-4 w-4" /></Button></Dialog.Close>
            </Dialog.Title>
            <Dialog.Description className="sr-only">Main navigation</Dialog.Description>
            <NavItems onNavigate={() => setMobileNav(false)} />
          </Dialog.Content>
        </Dialog.Portal>
      </Dialog.Root>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-14 items-center gap-2 border-b border-border bg-bg-elevated/60 px-4 backdrop-blur">
          <Button variant="ghost" size="icon" className="md:hidden" aria-label="Open menu" onClick={() => setMobileNav(true)}>
            <Menu className="h-4 w-4" />
          </Button>
          <button
            type="button"
            onClick={() => setPalette(true)}
            className="flex h-9 w-full max-w-sm items-center gap-2 rounded-lg border border-border bg-surface px-3 text-sm text-muted hover:border-primary/50"
          >
            <Search className="h-4 w-4" aria-hidden /> Search
            <kbd className="ml-auto rounded border border-border px-1.5 text-[10px]">Ctrl K</kbd>
          </button>
          <div className="ml-auto flex items-center gap-1">
            <Button
              variant="ghost"
              size="icon"
              aria-label={theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme'}
              onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
            >
              {theme === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </Button>
            <span className="hidden px-2 text-sm text-muted sm:inline">{me.display_name}</span>
            <Button
              variant="ghost"
              size="icon"
              aria-label="Sign out"
              onClick={() => void logout().then(() => nav('/login'))}
            >
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        </header>
        <VerifyBanner />
        <main id="main" className="min-h-0 flex-1 overflow-auto">
          <AnimatePresence mode="wait">
            <motion.div
              key={location.pathname}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="h-full"
            >
              <Outlet />
            </motion.div>
          </AnimatePresence>
        </main>
      </div>
      <CommandPalette open={palette} onOpenChange={setPalette} />
    </div>
  )
}
