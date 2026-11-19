import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import { MotionConfig } from 'motion/react'

export type Theme = 'dark' | 'light'
export type MotionLevel = 'full' | 'reduced' | 'off'

interface Prefs {
  theme: Theme
  motion: MotionLevel
  setTheme: (t: Theme) => void
  setMotion: (m: MotionLevel) => void
}

const PrefsContext = createContext<Prefs | null>(null)

function load<T extends string>(key: string, allowed: readonly T[], fallback: T): T {
  try {
    const v = localStorage.getItem(key)
    return v && (allowed as readonly string[]).includes(v) ? (v as T) : fallback
  } catch {
    return fallback
  }
}

function save(key: string, value: string) {
  try {
    localStorage.setItem(key, value)
  } catch {
    /* storage may be blocked; preference simply won't persist */
  }
}

export function PreferencesProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<Theme>(() => load('aura.theme', ['dark', 'light'], 'dark'))
  const [motion, setMotion] = useState<MotionLevel>(() =>
    load('aura.motion', ['full', 'reduced', 'off'], 'full'),
  )

  useEffect(() => {
    document.documentElement.dataset.theme = theme
    save('aura.theme', theme)
  }, [theme])

  useEffect(() => {
    document.documentElement.dataset.motion = motion
    save('aura.motion', motion)
  }, [motion])

  const value = useMemo(() => ({ theme, motion, setTheme, setMotion }), [theme, motion])
  return (
    <PrefsContext.Provider value={value}>
      {/* "user" honours the OS reduced-motion setting; AURA's own setting can only reduce further. */}
      <MotionConfig reducedMotion={motion === 'full' ? 'user' : 'always'}>{children}</MotionConfig>
    </PrefsContext.Provider>
  )
}

// eslint-disable-next-line react-refresh/only-export-components
export function usePreferences(): Prefs {
  const ctx = useContext(PrefsContext)
  if (!ctx) throw new Error('usePreferences must be used inside PreferencesProvider')
  return ctx
}
