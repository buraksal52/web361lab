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
type Draft = { code: CodeFiles; started_at: string }

type Props = { assignment: Assignment; token: string; userId: number }

export function StudentWorkspace({ assignment, token, userId }: Props) {
  const [files, setFiles] = useState<CodeFiles | null>(null)
  const [status, setStatus] = useState('Taslak yükleniyor…')
  const pending = useRef<Pending | null>(null)
  const busy = useRef(false)
  const started = useRef(0)
  const alive = useRef(true)
  const key = `web361lab.pending.${userId}.${assignment.id}`
  const url = `/assignments/${assignment.id}/draft`

  function persist() {
    if (!pending.current) return
    if (pending.current.batches.length) sessionStorage.setItem(key, JSON.stringify(pending.current))
    else sessionStorage.removeItem(key)
  }

  async function flush() {
    if (busy.current || !pending.current?.batches.length) return
    busy.current = true
    try {
      while (pending.current?.batches.length) {
        const batch = pending.current.batches[0]
        await request(`${url}/batches`, token, { method: 'POST', body: JSON.stringify(batch) })
        pending.current.batches.shift()
        persist()
      }
      if (alive.current) setStatus('Taslak kaydedildi.')
    } catch {
      if (alive.current) setStatus('Kaydedilemedi; yeniden denenecek.')
    } finally { busy.current = false }
  }

  function record(kind: Event['kind'], payload: Event['payload'], nextCode?: CodeFiles) {
    if (!pending.current) return
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
        const saved = sessionStorage.getItem(key)
        pending.current = saved ? JSON.parse(saved) as Pending : { batches: [], code: draft.code }
        started.current = Date.parse(draft.started_at.endsWith('Z') || draft.started_at.includes('+') ? draft.started_at : `${draft.started_at}Z`)
        await flush()
        if (alive.current) {
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

  return <>
    <p role="status">{status}</p>
    {files && <div className="workspace">
      <Editor enabledLanguages={assignment.enabled_languages} files={files} onChange={change}
        intellisenseEnabled={assignment.intellisense_enabled} pasteEnabled={assignment.paste_enabled}
        modelNamespace={`student-${userId}-assignment-${assignment.id}`}
        onPasteBlocked={() => record('paste_blocked', {})} />
      <Preview files={files} enabledLanguages={assignment.enabled_languages} />
      <aside><h3>Ders içeriği</h3><ReactMarkdown>{assignment.side_panel_md}</ReactMarkdown></aside>
    </div>}
  </>
}
