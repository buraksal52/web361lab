import { useEffect, useState } from 'react'
import { request, type Criterion } from './api'

type Row = Criterion & { auto_result: boolean | null; teacher_override: boolean | null; points: string | null }
type View = {
  criteria: Row[]
  suggested_points: string | null
  final_points: string | null
  feedback: string
  locked: boolean
  submitted_at: string
  rubric_fingerprint: string
  uses_current_assignment_criteria: boolean
  previous_evaluation: { final_points: string; feedback: string; graded_at: string } | null
}

function cents(value: string): number | null {
  if (!/^\d+(?:\.\d{1,2})?$/.test(value)) return null
  const [whole, fraction = ''] = value.split('.')
  const result = Number(whole) * 100 + Number(fraction.padEnd(2, '0'))
  return Number.isSafeInteger(result) ? result : null
}

function suggested(rows: Row[]): string | null {
  let total = 0
  for (const row of rows) {
    const effective = row.teacher_override ?? row.auto_result
    const value = row.kind === 'auto' ? (effective === null ? null : effective ? row.max_points : '0') : row.points
    const amount = value === null ? null : cents(value)
    const maximum = cents(row.max_points)
    if (amount === null || maximum === null || amount > maximum) return null
    total += amount
  }
  return (total / 100).toFixed(2)
}

export function EvaluationPanel({ submissionId, token }: { submissionId: number; token: string }) {
  const [view, setView] = useState<View | null>(null)
  const [rows, setRows] = useState<Row[]>([])
  const [finalPoints, setFinalPoints] = useState('')
  const [feedback, setFeedback] = useState('')
  const [message, setMessage] = useState('')
  const [saving, setSaving] = useState(false)

  async function load() {
    try {
      const data = await request<View>(`/submissions/${submissionId}/evaluation`, token)
      setView(data)
      setRows(data.criteria)
      setFinalPoints(data.final_points ?? '')
      setFeedback(data.feedback)
    } catch { setMessage('Değerlendirme bilgileri alınamadı.') }
  }

  useEffect(() => { void load() }, [submissionId, token])

  function update(index: number, row: Row) {
    setRows((current) => current.map((item, position) => position === index ? row : item))
  }

  async function save() {
    if (!view) return
    setSaving(true)
    try {
      await request(`/submissions/${submissionId}/evaluation`, token, { method: 'PUT', body: JSON.stringify({
        submitted_at: view.submitted_at, rubric_fingerprint: view.rubric_fingerprint, final_points: finalPoints, feedback,
        criteria: rows.map((row) => ({ criterion_id: row.id, manual_points: row.kind === 'manual' ? row.points : null, teacher_override: row.kind === 'auto' ? row.teacher_override : null })),
      }) })
      setMessage('Değerlendirme kaydedildi.')
      await load()
    } catch { setMessage('Değerlendirme kaydedilemedi. Teslim veya kriterler değişmiş olabilir; sayfayı yenileyin.') }
    finally { setSaving(false) }
  }

  const total = suggested(rows)
  return <section><h3>Değerlendirme</h3>
    {message && <p role="status">{message}</p>}
    {view && <>
      {!view.locked && <p>Ödev düzenlemeye açık. Değerlendirme için öğrencinin yeniden teslim etmesi gerekiyor.</p>}
      {view.previous_evaluation && <p>Önceki teslime ait son puan: {view.previous_evaluation.final_points}. Önceki geri bildirim: {view.previous_evaluation.feedback || '—'}</p>}
      {view.uses_current_assignment_criteria && <p>Bu eski teslim için ödevin mevcut kriterleri kullanılıyor.</p>}
      <form onSubmit={(event) => { event.preventDefault(); void save() }}>
        {rows.map((row, index) => <fieldset key={row.id}><legend>{row.label} — azami {row.max_points} puan</legend>
          {row.kind === 'auto' ? <>
            <p>Kontrol: {row.auto_result === null ? 'Sonuç yok' : row.auto_result ? 'Kullanılmış' : 'Kullanılmamış'}</p>
            <label>Öğretim elemanı seçimi <select value={row.teacher_override === null ? 'auto' : row.teacher_override ? 'used' : 'unused'} onChange={(event) => update(index, { ...row, teacher_override: event.target.value === 'auto' ? null : event.target.value === 'used' })}>
              <option value="auto">Kontrol sonucunu kullan</option><option value="used">Kullanılmış</option><option value="unused">Kullanılmamış</option>
            </select></label>
          </> : <label>Manuel puan <input type="number" min="0" max={row.max_points} step="0.01" required value={row.points ?? ''} onChange={(event) => update(index, { ...row, points: event.target.value || null })} /></label>}
        </fieldset>)}
        <p>Önerilen puan: {total ?? 'Tüm kriterler tamamlandığında hesaplanır.'}</p>
        <label>Son puan <input type="number" min="0" max="9999999999.99" step="0.01" required value={finalPoints} onChange={(event) => setFinalPoints(event.target.value)} /></label>
        <label>Geri bildirim <textarea maxLength={5000} value={feedback} onChange={(event) => setFeedback(event.target.value)} /></label>
        <button type="submit" disabled={!view.locked || total === null || saving}>Değerlendirmeyi kaydet</button>
      </form>
    </>}
  </section>
}
