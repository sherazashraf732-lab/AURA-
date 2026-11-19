import { ApiError } from '@/lib/api'

export interface Conversation {
  id: string
  title: string
  provider: string
  model: string
  project_id: string | null
  archived: boolean
  continued_from_id: string | null
  continuation_summary_id: string | null
  language_override: string | null
  created_at: string
  updated_at: string
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  language: string | null
  provider: string | null
  model: string | null
  status: 'complete' | 'error' | 'stopped'
  error_code: string | null
  created_at: string
}

export interface ProviderInfo {
  id: string
  name: string
  paid: boolean
  available: boolean
  requires_consent: boolean
  free_tier_note: string
  data_policy: string
  models: { id: string; label: string; context_window: number }[]
}

export type StreamEvent =
  | { event: 'meta'; data: { conversation_id: string; language: string; provider: string; model: string } }
  | { event: 'delta'; data: { text: string } }
  | { event: 'done'; data: { tokens_in: number; tokens_out: number; latency_ms: number } }
  | { event: 'error'; data: { code: string; message: string } }
  | { event: 'continued'; data: { conversation_id: string } }
  | { event: 'notice'; data: { code: string; message: string } }

function csrf(): string {
  const raw = document.cookie.split('; ').find((c) => c.startsWith('aura_csrf='))?.split('=')[1]
  return raw ? decodeURIComponent(raw) : ''
}

/** POST a message and parse the Server-Sent Events stream incrementally. */
export async function streamMessage(
  conversationId: string,
  content: string,
  onEvent: (e: StreamEvent) => void,
  signal: AbortSignal,
): Promise<void> {
  const res = await fetch(`/api/v1/conversations/${conversationId}/messages`, {
    method: 'POST',
    credentials: 'same-origin',
    headers: { 'content-type': 'application/json', 'x-csrf-token': csrf() },
    body: JSON.stringify({ content }),
    signal,
  })
  if (!res.ok || !res.body) {
    const body = (await res.json().catch(() => null)) as { error?: { code: string; message: string } } | null
    throw new ApiError(res.status, body?.error?.code ?? 'stream_failed', body?.error?.message ?? 'Request failed')
  }
  const reader = res.body.pipeThrough(new TextDecoderStream()).getReader()
  let buffer = ''
  for (;;) {
    const { value, done } = await reader.read()
    if (done) break
    buffer += value
    let idx: number
    while ((idx = buffer.indexOf('\n\n')) !== -1) {
      const block = buffer.slice(0, idx)
      buffer = buffer.slice(idx + 2)
      let event = 'message'
      let data = ''
      for (const line of block.split('\n')) {
        if (line.startsWith('event: ')) event = line.slice(7)
        else if (line.startsWith('data: ')) data += line.slice(6)
      }
      if (data) onEvent({ event, data: JSON.parse(data) } as StreamEvent)
    }
  }
}
