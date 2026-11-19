import type { ReactNode } from 'react'
import { Link } from 'react-router'
import { motion } from 'motion/react'
import { AuraMark } from '@/components/brand/AuraMark'

export function AuthLayout({ title, subtitle, children }: { title: string; subtitle?: string; children: ReactNode }) {
  return (
    <main className="aura-backdrop flex min-h-full items-center justify-center px-4 py-12">
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35, ease: 'easeOut' }}
        className="w-full max-w-md rounded-2xl border border-border bg-surface/90 p-8 shadow-glow backdrop-blur"
      >
        <Link to="/" className="mb-6 flex items-center gap-2 font-semibold tracking-wide">
          <AuraMark size={32} /> AURA
        </Link>
        <h1 className="text-2xl font-semibold">{title}</h1>
        {subtitle ? <p className="mt-1 text-sm text-muted">{subtitle}</p> : null}
        <div className="mt-6">{children}</div>
      </motion.div>
    </main>
  )
}
