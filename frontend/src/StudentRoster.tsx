import { useState } from 'react'
import { request } from './api'

export function StudentRoster({ courseId, token }: { courseId: number; token: string }) {
  const [file, setFile] = useState<File | null>(null)
  const [message, setMessage] = useState('')
  const [busy, setBusy] = useState(false)

  async function upload() {
    if (!file) return
    if (file.size > 262144) { setMessage('Dosya 256 KB boyutunu aşmamalı.'); return }
    setBusy(true)
    try {
      const result = await request<{ created: number; enrolled: number }>(`/courses/${courseId}/students/import`, token, {
        method: 'POST', body: JSON.stringify({ csv_text: await file.text() }),
      })
      setMessage(`${result.created} yeni öğrenci oluşturuldu; ${result.enrolled} öğrenci derse eklendi.`)
    } catch { setMessage('Liste yüklenemedi. CSV sütunlarını, numaraları ve mevcut kayıtlarla uyuşmazlıkları kontrol edin.') }
    finally { setBusy(false) }
  }

  return <section aria-labelledby="roster-heading">
    <h3 id="roster-heading">Öğrenci listesi yükle</h3>
    <p>CSV sütunları: student_number, name, email. Öğrenci numarası 9 haneli olmalı.</p>
    <label htmlFor="roster-file">CSV dosyası</label>{' '}
    <input id="roster-file" type="file" accept=".csv,text/csv" onChange={(event) => { setFile(event.target.files?.[0] ?? null); setMessage('') }} />
    <button type="button" disabled={!file || busy} onClick={() => { void upload() }}>Listeyi yükle</button>
    {message && <p role="status">{message}</p>}
  </section>
}
