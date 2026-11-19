import { Link } from 'react-router'
import { motion } from 'motion/react'
import { BookOpen, Brain, Languages, MessagesSquare, Search, ShieldCheck } from 'lucide-react'
import { AuraMark } from '@/components/brand/AuraMark'
import { Button } from '@/components/ui/button'
import { useAuth } from '@/lib/auth'

const FEATURES = [
  { icon: MessagesSquare, title: 'One assistant, many models', body: 'Choose between free-tier AI providers in one workspace.' },
  { icon: Search, title: 'Research with sources', body: 'Answers that show where every claim came from.' },
  { icon: Brain, title: 'Memory you control', body: 'See, edit, pause or delete anything AURA remembers.' },
  { icon: Languages, title: 'English, اردو, Roman Urdu', body: 'AURA replies in the language and style you write in.' },
  { icon: BookOpen, title: 'Your documents', body: 'Ask questions about files you upload.' },
  { icon: ShieldCheck, title: 'Private by design', body: 'Your data stays in your account and is never shared with other users.' },
]

export function LandingPage() {
  const { me } = useAuth()
  return (
    <main className="aura-backdrop min-h-full">
      <header className="mx-auto flex max-w-6xl items-center justify-between px-4 py-5">
        <span className="flex items-center gap-2 font-semibold tracking-wide"><AuraMark size={32} /> AURA</span>
        <nav className="flex gap-2">
          {me ? (
            <Button asChild><Link to="/app">Open workspace</Link></Button>
          ) : (
            <>
              <Button asChild variant="ghost"><Link to="/login">Sign in</Link></Button>
              <Button asChild><Link to="/signup">Join the beta</Link></Button>
            </>
          )}
        </nav>
      </header>
      <section className="mx-auto max-w-6xl px-4 pb-16 pt-12 text-center md:pt-20">
        <motion.div initial={{ scale: 0.8, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} transition={{ duration: 0.6 }} className="mx-auto mb-8 w-fit">
          <AuraMark size={120} />
        </motion.div>
        <motion.h1 initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }} className="text-4xl font-semibold tracking-tight md:text-6xl">
          Your AI Powerhouse
        </motion.h1>
        <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }} className="mx-auto mt-4 max-w-2xl text-lg text-muted">
          Conversations, research, documents and data in one calm, private workspace.
        </motion.p>
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.45 }} className="mt-8 flex justify-center gap-3">
          <Button asChild size="lg"><Link to={me ? '/app' : '/signup'}>{me ? 'Open workspace' : 'Get started free'}</Link></Button>
        </motion.div>
        <p className="mt-3 text-xs text-muted">Public beta. Free usage limits apply; no payment details are ever requested.</p>
      </section>
      <section className="mx-auto grid max-w-6xl gap-4 px-4 pb-20 sm:grid-cols-2 lg:grid-cols-3">
        {FEATURES.map((f, i) => (
          <motion.div
            key={f.title}
            initial={{ opacity: 0, y: 14 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: i * 0.06 }}
            className="rounded-xl border border-border bg-surface/70 p-5"
          >
            <f.icon className="mb-3 h-5 w-5 text-accent" aria-hidden />
            <p className="font-medium">{f.title}</p>
            <p className="mt-1 text-sm text-muted">{f.body}</p>
          </motion.div>
        ))}
      </section>
    </main>
  )
}
