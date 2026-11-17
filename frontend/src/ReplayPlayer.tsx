import { useEffect, useState } from 'react'
import type { CodeFiles, Language } from './Editor'

export type ReplayEvent = {
  t_ms: number
  kind: string
  payload: { language?: Language; changes?: { rangeOffset: number; rangeLength: number; text: string }[] }
}

export function replayAt(initial: CodeFiles, events: ReplayEvent[], time: number): CodeFiles {
  const result = { ...initial }
  for (const event of events) {
    if (event.t_ms > time) break
    if (event.kind !== 'edit' || !event.payload.language || !event.payload.changes) continue
    const language = event.payload.language
    for (const change of event.payload.changes) {
      const value = result[language]
      result[language] = value.slice(0, change.rangeOffset) + change.text + value.slice(change.rangeOffset + change.rangeLength)
    }
  }
  return result
}

type Props = { initial: CodeFiles; events: ReplayEvent[]; languages: Language[] }

export function ReplayPlayer({ initial, events, languages }: Props) {
  const duration = events.reduce((maximum, event) => Math.max(maximum, event.t_ms), 0)
  const [time, setTime] = useState(0)
  const [playing, setPlaying] = useState(false)
  const [speed, setSpeed] = useState(1)
  const [language, setLanguage] = useState<Language>(languages[0] ?? 'html')

  useEffect(() => {
    if (!playing) return
    let previous = performance.now()
    const timer = window.setInterval(() => {
      const now = performance.now()
      const elapsed = now - previous
      previous = now
      setTime((current) => {
        const next = Math.min(duration, current + elapsed * speed)
        if (next >= duration) setPlaying(false)
        return next
      })
    }, 100)
    return () => window.clearInterval(timer)
  }, [playing, speed, duration])

  const code = replayAt(initial, events, time)
  return <section aria-label="Çalışma kaydı">
    <h3>Çalışma kaydı</h3>
    <button type="button" onClick={() => { if (!playing && time >= duration) setTime(0); setPlaying(!playing) }} disabled={duration === 0}>{playing ? 'Duraklat' : 'Oynat'}</button>
    <label>Hız <select value={speed} onChange={(event) => setSpeed(Number(event.target.value))}>
      <option value={0.5}>0,5×</option><option value={1}>1×</option><option value={2}>2×</option><option value={4}>4×</option>
    </select></label>
    <label>Konum <input type="range" min={0} max={duration} value={Math.min(time, duration)} onChange={(event) => setTime(Number(event.target.value))} /></label>
    <output>{(time / 1000).toFixed(1)} / {(duration / 1000).toFixed(1)} sn</output>
    <div>{languages.map((item) => <button type="button" key={item} aria-pressed={item === language} onClick={() => setLanguage(item)}>{item.toUpperCase()}</button>)}</div>
    <pre aria-label="Kayıttaki kod">{code[language]}</pre>
  </section>
}
