import { Link } from 'react-router'
import { AuraMark } from '@/components/brand/AuraMark'

// Draft texts for the beta. The owner should have them reviewed before public launch.
function Legal({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <main className="aura-backdrop min-h-full px-4 py-10">
      <article className="mx-auto max-w-3xl space-y-4 rounded-2xl border border-border bg-surface/90 p-8 text-sm leading-relaxed">
        <Link to="/" className="flex items-center gap-2 font-semibold"><AuraMark size={28} /> AURA</Link>
        <h1 className="text-2xl font-semibold">{title}</h1>
        <p className="text-xs text-muted">Beta version · last updated 20 November 2026</p>
        {children}
      </article>
    </main>
  )
}

const H = ({ children }: { children: React.ReactNode }) => <h2 className="pt-2 text-base font-semibold">{children}</h2>

export function PrivacyPage() {
  return (
    <Legal title="Privacy Policy">
      <H>What AURA stores</H>
      <p>Your account (email, name, hashed password), your chats, memories, continuation summaries, projects, uploaded document text, datasets, workflows and usage counts. Original uploaded files are not kept: only the extracted text is stored.</p>
      <H>Who can see it</H>
      <p>Only you. Every record is tied to your account and never shown to other users. Administrators can see account details (email, status) to run the service and stop abuse, but not your chats or documents through the app.</p>
      <H>External AI providers</H>
      <p>The offline demo model sends nothing anywhere. If you consent and choose an external free-tier provider (for example Google Gemini, Groq, OpenRouter, Mistral, Cloudflare, Cerebras or Hugging Face), the content of that request is sent to that provider. Some free tiers allow the provider to use or review submitted content, so do not send sensitive personal information. You can withdraw consent at any time in Settings.</p>
      <H>Images and audio</H>
      <p>Images are re-encoded before processing, which removes hidden metadata such as GPS location.</p>
      <H>Your controls</H>
      <p>You can view, edit, disable and delete memories and summaries, download all your data, and permanently delete your account in the Security Center. Deletion removes your data from the live database immediately; database backups are kept for up to 30 days and then overwritten.</p>
      <H>Cookies</H>
      <p>AURA uses only necessary cookies: a session cookie and a security (CSRF) cookie. There is no advertising or third-party tracking.</p>
      <H>Contact</H>
      <p>Questions or deletion requests: contact the AURA administrator through the project's GitHub page.</p>
    </Legal>
  )
}

export function TermsPage() {
  return (
    <Legal title="Terms of Use">
      <p>AURA is a free beta for testing. It may change, have errors or be unavailable, and is provided "as is" without warranty.</p>
      <H>Acceptable use</H>
      <p>Do not use AURA to break the law, harm others, attempt to access other users' data, overload the service, or bypass usage limits. Accounts that do this may be suspended.</p>
      <H>AI output</H>
      <p>AI answers can be wrong. Check important information, especially medical, legal or financial content. Research and fact-check results show their sources so you can verify them.</p>
      <H>Usage limits</H>
      <p>Free model allowances are shared by all testers, so daily limits apply. AURA never switches you to a paid service and never asks for payment details.</p>
      <H>Your content</H>
      <p>You keep ownership of what you upload and create. You give AURA permission to store and process it only to provide the service to you.</p>
      <H>Third-party providers</H>
      <p>When you choose an external AI provider, that provider's own terms also apply to the request.</p>
    </Legal>
  )
}
