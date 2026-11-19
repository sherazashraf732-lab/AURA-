import { createContext, useContext, type ReactNode } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'

export interface Me {
  id: string
  email: string
  display_name: string
  role: 'user' | 'admin'
  email_verified: boolean
  language_override: 'en' | 'ur' | 'ur-Latn' | null
  memory_enabled: boolean
  auto_continuation: boolean
  provider_consent_at: string | null
}

interface AuthState {
  me: Me | null
  loading: boolean
  refresh: () => Promise<void>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthState | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const qc = useQueryClient()
  const q = useQuery({ queryKey: ['me'], queryFn: () => api<Me | null>('/auth/me'), staleTime: 60_000 })
  const value: AuthState = {
    me: q.data ?? null,
    loading: q.isPending,
    refresh: async () => {
      await qc.invalidateQueries({ queryKey: ['me'] })
    },
    logout: async () => {
      await api('/auth/logout', { method: 'POST' })
      qc.clear()
      await qc.invalidateQueries({ queryKey: ['me'] })
    },
  }
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth(): AuthState {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
