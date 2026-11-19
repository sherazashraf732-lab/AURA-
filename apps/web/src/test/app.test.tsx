import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { AppRoutes } from '@/App'
import { AuthProvider } from '@/lib/auth'
import { PreferencesProvider } from '@/lib/preferences'
import { MODULES } from '@/lib/modules'

function mockFetch(routes: Record<string, unknown>) {
  const calls: { url: string; init?: RequestInit }[] = []
  vi.stubGlobal(
    'fetch',
    vi.fn(async (url: string, init?: RequestInit) => {
      calls.push({ url, init })
      const key = Object.keys(routes).find((k) => url.endsWith(k))
      return new Response(JSON.stringify(key ? routes[key] : null), { status: 200, headers: { 'content-type': 'application/json' } })
    }),
  )
  return calls
}

function renderAt(path: string) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={qc}>
      <PreferencesProvider>
        <AuthProvider>
          <MemoryRouter initialEntries={[path]}>
            <AppRoutes />
          </MemoryRouter>
        </AuthProvider>
      </PreferencesProvider>
    </QueryClientProvider>,
  )
}

const me = {
  id: '1', email: 'u@example.com', display_name: 'Sam', role: 'user', email_verified: true,
  language_override: null, memory_enabled: true, auto_continuation: true, provider_consent_at: null,
}

afterEach(() => vi.unstubAllGlobals())

describe('AURA web shell', () => {
  it('landing page offers sign up when signed out', async () => {
    mockFetch({ '/auth/me': null })
    renderAt('/')
    expect(await screen.findByRole('heading', { name: 'Your AI Powerhouse' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Join the beta' })).toHaveAttribute('href', '/signup')
  })

  it('protected routes redirect to sign in', async () => {
    mockFetch({ '/auth/me': null })
    renderAt('/app')
    expect(await screen.findByRole('heading', { name: 'Welcome back' })).toBeInTheDocument()
  })

  it('sidebar only shows live modules', async () => {
    mockFetch({ '/auth/me': me })
    renderAt('/app')
    const nav = await screen.findByRole('navigation', { name: 'Main' })
    for (const m of MODULES) {
      const shown = m.status === 'live' && !m.adminOnly
      if (shown) expect(nav).toHaveTextContent(m.name)
      else expect(nav).not.toHaveTextContent(new RegExp(`^${m.name}$`))
    }
  })

  it('login posts credentials with the CSRF header', async () => {
    document.cookie = 'aura_csrf=tok123'
    const calls = mockFetch({ '/auth/me': null, '/auth/login': me })
    renderAt('/login')
    await userEvent.type(await screen.findByLabelText('Email'), 'u@example.com')
    await userEvent.type(screen.getByLabelText('Password'), 'correct-horse-1')
    await userEvent.click(screen.getByRole('button', { name: 'Sign in' }))
    await waitFor(() => expect(calls.some((c) => c.url.endsWith('/auth/login'))).toBe(true))
    const login = calls.find((c) => c.url.endsWith('/auth/login'))!
    expect(new Headers(login.init?.headers).get('x-csrf-token')).toBe('tok123')
    expect(JSON.parse(String(login.init?.body))).toEqual({ email: 'u@example.com', password: 'correct-horse-1' })
  })

  it('theme toggle switches the document theme', async () => {
    mockFetch({ '/auth/me': me })
    renderAt('/app')
    await userEvent.click(await screen.findByRole('button', { name: 'Switch to light theme' }))
    expect(document.documentElement.dataset.theme).toBe('light')
  })
})
