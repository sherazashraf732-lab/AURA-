import { afterEach, describe, expect, it, vi } from 'vitest'
import { streamMessage, type StreamEvent } from '@/lib/chat'
import { ApiError } from '@/lib/api'

function sseResponse(chunks: string[]) {
  const body = new ReadableStream<Uint8Array>({
    start(c) {
      const enc = new TextEncoder()
      for (const ch of chunks) c.enqueue(enc.encode(ch))
      c.close()
    },
  })
  return new Response(body, { status: 200, headers: { 'content-type': 'text/event-stream' } })
}

afterEach(() => vi.unstubAllGlobals())

describe('streamMessage', () => {
  it('parses events split across network chunks', async () => {
    vi.stubGlobal('fetch', vi.fn(async () =>
      sseResponse([
        'event: meta\ndata: {"conversation_id":"c1","language":"ur-Latn","provider":"mock","model":"m"}\n\nevent: del',
        'ta\ndata: {"text":"Sal"}\n\nevent: delta\ndata: {"text":"am"}\n\n',
        'event: done\ndata: {"tokens_in":1,"tokens_out":2,"latency_ms":3}\n\n',
      ]),
    ))
    const events: StreamEvent[] = []
    await streamMessage('c1', 'hi', (e) => events.push(e), new AbortController().signal)
    expect(events.map((e) => e.event)).toEqual(['meta', 'delta', 'delta', 'done'])
    expect(events.filter((e) => e.event === 'delta').map((e) => (e.data as { text: string }).text).join('')).toBe('Salam')
  })

  it('surfaces API errors before the stream starts', async () => {
    vi.stubGlobal('fetch', vi.fn(async () =>
      new Response(JSON.stringify({ error: { code: 'daily_limit', message: 'Limit reached' } }), { status: 429 }),
    ))
    await expect(streamMessage('c1', 'hi', () => {}, new AbortController().signal)).rejects.toMatchObject({
      constructor: ApiError,
      code: 'daily_limit',
      status: 429,
    })
  })
})
