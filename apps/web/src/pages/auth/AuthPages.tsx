import { useEffect, useRef, useState, type FormEvent } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router'
import { Button } from '@/components/ui/button'
import { Alert, Field, Input } from '@/components/ui/form'
import { Spinner } from '@/components/ui/card'
import { api, ApiError } from '@/lib/api'
import { useAuth } from '@/lib/auth'
import { AuthLayout } from './AuthLayout'

function useSubmit() {
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const run = async (fn: () => Promise<void>) => {
    setBusy(true)
    setError(null)
    try {
      await fn()
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Something went wrong. Please try again.')
    } finally {
      setBusy(false)
    }
  }
  return { busy, error, run }
}

export function LoginPage() {
  const nav = useNavigate()
  const { refresh } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const { busy, error, run } = useSubmit()

  const submit = (e: FormEvent) => {
    e.preventDefault()
    void run(async () => {
      await api('/auth/login', { json: { email, password } })
      await refresh()
      nav('/app')
    })
  }

  return (
    <AuthLayout title="Welcome back" subtitle="Sign in to your AURA workspace.">
      <form onSubmit={submit} className="space-y-4" noValidate>
        {error ? <Alert tone="error">{error}</Alert> : null}
        <Field label="Email" htmlFor="email">
          <Input id="email" type="email" autoComplete="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
        </Field>
        <Field label="Password" htmlFor="password">
          <Input id="password" type="password" autoComplete="current-password" required value={password} onChange={(e) => setPassword(e.target.value)} />
        </Field>
        <Button type="submit" className="w-full" disabled={busy || !email || !password}>
          {busy ? <Spinner label="Signing in" /> : 'Sign in'}
        </Button>
        <div className="flex justify-between text-sm">
          <Link className="text-primary-strong hover:underline" to="/forgot-password">Forgot password?</Link>
          <Link className="text-primary-strong hover:underline" to="/signup">Create account</Link>
        </div>
      </form>
    </AuthLayout>
  )
}

export function SignupPage() {
  const [email, setEmail] = useState('')
  const [name, setName] = useState('')
  const [password, setPassword] = useState('')
  const [terms, setTerms] = useState(false)
  const [website, setWebsite] = useState('') // honeypot, invisible to people
  const [done, setDone] = useState<string | null>(null)
  const { busy, error, run } = useSubmit()
  const tooShort = password.length > 0 && password.length < 10

  const submit = (e: FormEvent) => {
    e.preventDefault()
    void run(async () => {
      const r = await api<{ message: string }>('/auth/signup', { json: { email, password, display_name: name, accept_terms: terms, website } })
      setDone(r.message)
    })
  }

  if (done)
    return (
      <AuthLayout title="Check your inbox" subtitle={done}>
        <p className="text-sm text-muted">Open the link we sent to <strong className="text-fg">{email}</strong> to activate your account.</p>
        <Button asChild variant="secondary" className="mt-6 w-full"><Link to="/login">Go to sign in</Link></Button>
      </AuthLayout>
    )

  return (
    <AuthLayout title="Create your account" subtitle="Free during the beta. Usage limits apply.">
      <form onSubmit={submit} className="space-y-4" noValidate>
        {error ? <Alert tone="error">{error}</Alert> : null}
        <Field label="Name" htmlFor="name">
          <Input id="name" autoComplete="name" value={name} maxLength={80} onChange={(e) => setName(e.target.value)} />
        </Field>
        <Field label="Email" htmlFor="email">
          <Input id="email" type="email" autoComplete="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
        </Field>
        <Field label="Password" htmlFor="password" error={tooShort ? 'Use at least 10 characters.' : undefined} hint="At least 10 characters.">
          <Input id="password" type="password" autoComplete="new-password" required value={password} onChange={(e) => setPassword(e.target.value)} />
        </Field>
        <input type="text" name="website" tabIndex={-1} autoComplete="off" aria-hidden="true" className="hidden" value={website} onChange={(e) => setWebsite(e.target.value)} />
        <label className="flex items-start gap-2 text-sm">
          <input type="checkbox" checked={terms} onChange={(e) => setTerms(e.target.checked)} className="mt-1" />
          <span>I agree to the <Link className="text-primary-strong hover:underline" to="/terms" target="_blank">Terms</Link> and <Link className="text-primary-strong hover:underline" to="/privacy" target="_blank">Privacy Policy</Link>.</span>
        </label>
        <Button type="submit" className="w-full" disabled={busy || !email || password.length < 10 || !terms}>
          {busy ? <Spinner label="Creating account" /> : 'Create account'}
        </Button>
        <p className="text-center text-sm text-muted">
          Already have an account? <Link className="text-primary-strong hover:underline" to="/login">Sign in</Link>
        </p>
      </form>
    </AuthLayout>
  )
}

export function VerifyEmailPage() {
  const [params] = useSearchParams()
  const token = params.get('token') ?? ''
  const { refresh } = useAuth()
  const [state, setState] = useState<'working' | 'ok' | 'error'>(token ? 'working' : 'error')
  const [message, setMessage] = useState('This verification link is missing its token.')
  const started = useRef(false)

  useEffect(() => {
    if (!token || started.current) return
    started.current = true // tokens are single-use; never submit twice (React StrictMode re-runs effects)
    api('/auth/verify-email', { json: { token } })
      .then(async () => {
        setState('ok')
        await refresh()
      })
      .catch((e: unknown) => {
        setState('error')
        setMessage(e instanceof ApiError ? e.message : 'Verification failed.')
      })
  }, [token, refresh])

  return (
    <AuthLayout title="Email verification">
      {state === 'working' ? <Spinner label="Verifying" /> : null}
      {state === 'ok' ? <Alert tone="success">Your email is verified. You can now use AURA.</Alert> : null}
      {state === 'error' ? <Alert tone="error">{message}</Alert> : null}
      {state !== 'working' ? (
        <Button asChild className="mt-6 w-full"><Link to="/app">Continue</Link></Button>
      ) : null}
    </AuthLayout>
  )
}

export function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [done, setDone] = useState<string | null>(null)
  const { busy, error, run } = useSubmit()
  return (
    <AuthLayout title="Reset password" subtitle="We will email you a single-use reset link.">
      {done ? (
        <Alert tone="success">{done}</Alert>
      ) : (
        <form
          className="space-y-4"
          onSubmit={(e) => {
            e.preventDefault()
            void run(async () => setDone((await api<{ message: string }>('/auth/request-password-reset', { json: { email } })).message))
          }}
        >
          {error ? <Alert tone="error">{error}</Alert> : null}
          <Field label="Email" htmlFor="email">
            <Input id="email" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
          </Field>
          <Button type="submit" className="w-full" disabled={busy || !email}>Send reset link</Button>
        </form>
      )}
      <p className="mt-4 text-center text-sm"><Link className="text-primary-strong hover:underline" to="/login">Back to sign in</Link></p>
    </AuthLayout>
  )
}

export function ResetPasswordPage() {
  const [params] = useSearchParams()
  const nav = useNavigate()
  const [password, setPassword] = useState('')
  const { busy, error, run } = useSubmit()
  return (
    <AuthLayout title="Choose a new password" subtitle="All your other sessions will be signed out.">
      <form
        className="space-y-4"
        onSubmit={(e) => {
          e.preventDefault()
          void run(async () => {
            await api('/auth/reset-password', { json: { token: params.get('token') ?? '', password } })
            nav('/login')
          })
        }}
      >
        {error ? <Alert tone="error">{error}</Alert> : null}
        <Field label="New password" htmlFor="password" hint="At least 10 characters.">
          <Input id="password" type="password" autoComplete="new-password" value={password} onChange={(e) => setPassword(e.target.value)} />
        </Field>
        <Button type="submit" className="w-full" disabled={busy || password.length < 10}>Update password</Button>
      </form>
    </AuthLayout>
  )
}
