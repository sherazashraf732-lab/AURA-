import '@testing-library/jest-dom/vitest'

// jsdom lacks IntersectionObserver (used by Motion's whileInView); a no-op stub is enough for tests.
class IO {
  observe() {}
  unobserve() {}
  disconnect() {}
  takeRecords() {
    return []
  }
}
globalThis.IntersectionObserver ??= IO as unknown as typeof IntersectionObserver
