import { expect, test } from 'vitest'
import { replayAt, type ReplayEvent } from './ReplayPlayer'

test('rebuilds code at different replay positions, including UTF-16 offsets', () => {
  const initial = { html: '😀', css: '', javascript: '' }
  const events: ReplayEvent[] = [
    { t_ms: 100, kind: 'edit', payload: { language: 'html', changes: [{ rangeOffset: 2, rangeLength: 0, text: 'a' }] } },
    { t_ms: 200, kind: 'edit', payload: { language: 'html', changes: [{ rangeOffset: 2, rangeLength: 1, text: 'bc' }] } },
    { t_ms: 300, kind: 'submit', payload: {} },
  ]
  expect(replayAt(initial, events, 0).html).toBe('😀')
  expect(replayAt(initial, events, 100).html).toBe('😀a')
  expect(replayAt(initial, events, 300).html).toBe('😀bc')
  expect(initial.html).toBe('😀')
})
