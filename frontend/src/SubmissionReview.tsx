import { useEffect, useState } from 'react'
import { Preview } from './Preview'
import { ReplayPlayer, type ReplayEvent } from './ReplayPlayer'
import { request, type Assignment, type CheckResult } from './api'
import { CheckResults } from './CheckResults'
import type { CodeFiles } from './Editor'

type Submission = { id: number; student_id: number; student_name: string; submitted_at: string; locked: boolean; final_code: CodeFiles; check_result?: CheckResult[] }
type Replay = { initial_code: CodeFiles; events: ReplayEvent[]; signals: { paste_blocked_count: number; blur_count: number; max_insert_chars: number } }

export function SubmissionReview({ assignment, token }: { assignment: Assignment; token: string }) {
  const [submissions, setSubmissions] = useState<Submission[]>([])
  const [selected, setSelected] = useState<Submission | null>(null)
  const [replay, setReplay] = useState<Replay | null>(null)
  const [error, setError] = useState('')

  async function loadList() {
    try { setSubmissions(await request<Submission[]>(`/assignments/${assignment.id}/submissions`, token)) }
    catch { setError('Teslimler alınamadı.') }
  }

  useEffect(() => { void loadList() }, [assignment.id, token])

  async function open(submission: Submission) {
    try {
      const [detail, history] = await Promise.all([
        request<Submission>(`/submissions/${submission.id}`, token),
        request<Replay>(`/assignments/${assignment.id}/students/${submission.student_id}/replay`, token),
      ])
      setSelected(detail)
      setReplay(history)
      setError('')
    } catch { setError('Teslim bilgisi alınamadı.') }
  }

  async function unlock() {
    if (!selected || !window.confirm('Öğrencinin ödevi yeniden düzenlemesine izin verilsin mi?')) return
    try {
      await request(`/submissions/${selected.id}/unlock`, token, { method: 'POST' })
      setSelected({ ...selected, locked: false })
      await loadList()
    } catch { setError('Düzenleme izni verilemedi.') }
  }

  return <section>
    <h3>Teslimler</h3>
    {error && <p role="alert">{error}</p>}
    {submissions.length === 0 && <p>Henüz teslim yok.</p>}
    {submissions.map((submission) => <div key={submission.id}>
      <button type="button" onClick={() => open(submission)}>{submission.student_name}</button>
      <span>{new Date(submission.submitted_at).toLocaleString('tr-TR')} — {submission.locked ? 'Teslim edildi' : 'Düzenlemeye açık'}</span>
    </div>)}
    {selected && replay && <section>
      <h3>{selected.student_name}</h3>
      {selected.locked && <button type="button" onClick={unlock}>Yeniden düzenlemeye izin ver</button>}
      <h4>Teslim edilen kod</h4>
      {assignment.enabled_languages.map((language) => <section key={language}><h5>{language.toUpperCase()}</h5><pre>{selected.final_code[language]}</pre></section>)}
      <Preview files={selected.final_code} enabledLanguages={assignment.enabled_languages} />
      {assignment.checker_enabled && selected.check_result !== undefined && <CheckResults results={selected.check_result} />}
      <h4>Gözlemler</h4>
      <p>Engellenen yapıştırma: {replay.signals.paste_blocked_count}</p>
      <p>Sekme veya pencere odağı kaybı: {replay.signals.blur_count}</p>
      <p>En büyük tek ekleme: {replay.signals.max_insert_chars} karakter</p>
      <ReplayPlayer key={selected.id} initial={replay.initial_code} events={replay.events} languages={assignment.enabled_languages} />
    </section>}
  </section>
}
