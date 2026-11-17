import { useEffect, useRef, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { Editor, type CodeFiles, type Language } from './Editor'
import { Preview } from './Preview'
import { request, type Assignment } from './api'
import type { editor } from 'monaco-editor'

type Change = { rangeOffset: number; rangeLength: number; text: string }
type Event = { t_ms: number; kind: 'edit' | 'paste_blocked' | 'blur' | 'focus'; payload: { language?: Language; changes?: Change[] } }
type Batch = { batch_id: string; code: CodeFiles; events: Event[] }
type Pending = { batches: Batch[]; code: CodeFiles }
type Draft = { code: CodeFiles; started_at: string; locked: boolean }

type Props = { assignment: Assignment; token: string; userId: number }

export function StudentWorkspace({ assignment, token, userId }: Props) {
  const [files, setFiles] = useState<CodeFiles | null>(null)
  const [status, setStatus] = useState('Taslak yükleniyor…')
  const [locked, setLocked] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const pending = useRef<Pending | null>(null)
  const busy = useRef(false)
  const flushTask = useRef<Promise<boolean> | null>(null)
  const recording = useRef(false)
  const started = useRef(0)
  const alive = useRef(true)
  const key = `web361lab.pending.${userId}.${assignment.id}`
  const url = `/assignments/${assignment.id}/draft`

  function persist() {
    if (!pending.current) return
    if (pending.current.batches.length) sessionStorage.setItem(key, JSON.stringify(pending.current))
    else sessionStorage.removeItem(key)
  }

  function flush(): Promise<boolean> {
    if (flushTask.current) return flushTask.current
    if (!pending.current?.batches.length) return Promise.resolve(true)
    busy.current = true
    const task = (async () => {
      try {
        while (pending.current?.batches.length) {
          const batch = pending.current.batches[0]
          await request(`${url}/batches`, token, { method: 'POST', body: JSON.stringify(batch) })
          pending.current.batches.shift()
          persist()
        }
        if (alive.current) setStatus('Taslak kaydedildi.')
        return true
      } catch {
        if (alive.current) setStatus('Kaydedilemedi; yeniden denenecek.')
        return false
      } finally { busy.current = false; flushTask.current = null }
    })()
    flushTask.current = task
    return task
  }

  function record(kind: Event['kind'], payload: Event['payload'], nextCode?: CodeFiles) {
    if (!pending.current || !recording.current) return
    const code = nextCode ?? pending.current.code
    const event: Event = { t_ms: Math.min(2147483647, Math.max(0, Date.now() - started.current)), kind, payload }
    const batches = pending.current.batches
    const last = batches[batches.length - 1]
    if (last && (!busy.current || batches.length > 1) && last.events.length < 1000) {
      last.events.push(event)
      last.code = code
    } else {
      batches.push({ batch_id: crypto.randomUUID(), code, events: [event] })
    }
    pending.current.code = code
    persist()
    setStatus('Kaydediliyor…')
  }

  useEffect(() => {
    alive.current = true
    async function load() {
      try {
        const draft = await request<Draft>(url, token, { method: 'POST' })
        if (draft.locked) {
          if (alive.current) { setLocked(true); setFiles(draft.code); setStatus('Ödev teslim edildi ve düzenlemeye kapalı.') }
          return
        }
        const saved = sessionStorage.getItem(key)
        pending.current = saved ? JSON.parse(saved) as Pending : { batches: [], code: draft.code }
        started.current = Date.parse(draft.started_at.endsWith('Z') || draft.started_at.includes('+') ? draft.started_at : `${draft.started_at}Z`)
        await flush()
        if (alive.current) {
          recording.current = true
          setFiles(pending.current.code)
          setStatus(pending.current.batches.length ? 'Kaydedilemedi; yeniden denenecek.' : 'Taslak kaydedildi.')
        }
      } catch { if (alive.current) setStatus('Taslak yüklenemedi. Lütfen yeniden deneyin.') }
    }
    void load()
    const timer = window.setInterval(() => { void flush() }, 1500)
    const onBlur = () => record('blur', {})
    const onFocus = () => record('focus', {})
    window.addEventListener('blur', onBlur)
    window.addEventListener('focus', onFocus)
    return () => {
      alive.current = false
      recording.current = false
      window.clearInterval(timer)
      window.removeEventListener('blur', onBlur)
      window.removeEventListener('focus', onFocus)
      void flush()
    }
  }, [assignment.id, token, userId])

  function change(language: Language, value: string, event: editor.IModelContentChangedEvent) {
    if (!pending.current) return
    const next = { ...pending.current.code, [language]: value }
    record('edit', { language, changes: event.changes.map(({ rangeOffset, rangeLength, text }) => ({ rangeOffset, rangeLength, text })) }, next)
    setFiles(next)
  }

  async function submit() {
    if (!pending.current || !window.confirm('Ödevi teslim etmek istiyor musunuz? Teslimden sonra düzenleme kapanır.')) return
    recording.current = false
    setSubmitting(true)
    const saved = await flush()
    if (!saved || !pending.current || pending.current.batches.length) {
      setStatus('Ödev teslim edilemedi; önce değişiklikler kaydedilmeli.')
      recording.current = true
      setSubmitting(false)
      return
    }
    try {
      await request(`/assignments/${assignment.id}/submit`, token, { method: 'POST', body: JSON.stringify(pending.current.code) })
      setLocked(true)
      setStatus('Ödev teslim edildi ve düzenlemeye kapalı.')
    } catch {
      setStatus('Ödev teslim edilemedi. Lütfen tekrar deneyin.')
      recording.current = true
    } finally { setSubmitting(false) }
  }

  return <>
    <p role="status">{status}</p>
    {files && !locked && <button type="button" onClick={submit} disabled={submitting}>Ödevi teslim et</button>}
    {files && locked && <div><h3>Teslim edilen kod</h3>{assignment.enabled_languages.map((language) => <section key={language}><h4>{language.toUpperCase()}</h4><pre>{files[language]}</pre></section>)}</div>}
    {files && !locked && !submitting && <div className="workspace">
      <Editor enabledLanguages={assignment.enabled_languages} files={files} onChange={change}
        intellisenseEnabled={assignment.intellisense_enabled} pasteEnabled={assignment.paste_enabled}
        modelNamespace={`student-${userId}-assignment-${assignment.id}`}
        onPasteBlocked={() => record('paste_blocked', {})} />
      <Preview files={files} enabledLanguages={assignment.enabled_languages} />
      <aside><h3>Ders içeriği</h3><ReactMarkdown>{assignment.side_panel_md}</ReactMarkdown></aside>
    </div>}
  </>
}
