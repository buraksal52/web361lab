import { useEffect, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { AssignmentForm } from './AssignmentForm'
import { Editor, type CodeFiles, type Language } from './Editor'
import { Preview } from './Preview'
import { request, type Assignment, type Course, type User } from './api'
import { StudentWorkspace } from './StudentWorkspace'
import { SubmissionReview } from './SubmissionReview'
import './style.css'

export function App() {
  const [users, setUsers] = useState<User[]>([])
  const [token, setToken] = useState(() => typeof window === 'undefined' ? '' : sessionStorage.getItem('web361lab.token') ?? '')
  const [identity, setIdentity] = useState<{ id: number; role: string; recording_consent: boolean } | null>(null)
  const [courses, setCourses] = useState<Course[]>([])
  const [course, setCourse] = useState<Course | null>(null)
  const [assignments, setAssignments] = useState<Assignment[]>([])
  const [selected, setSelected] = useState<Assignment | null>(null)
  const [editing, setEditing] = useState<Assignment | null>(null)
  const [files, setFiles] = useState<CodeFiles>({ html: '', css: '', javascript: '' })
  const [error, setError] = useState('')

  useEffect(() => { request<User[]>('/demo/users').then(setUsers).catch(() => setError('Kullanıcı listesi alınamadı.')) }, [])

  useEffect(() => {
    if (!token) return
    async function restore() {
      try {
        const [me, courseList] = await Promise.all([
          request<{ id: number; role: string; recording_consent: boolean }>('/me', token),
          request<Course[]>('/courses', token),
        ])
        setIdentity(me)
        setCourses(courseList)
        const savedCourse = courseList.find((item) => item.id === Number(sessionStorage.getItem('web361lab.course')))
        if (savedCourse) {
          const list = await request<Assignment[]>(`/courses/${savedCourse.id}/assignments`, token)
          setCourse(savedCourse)
          setAssignments(list)
          const savedAssignment = list.find((item) => item.id === Number(sessionStorage.getItem('web361lab.assignment')))
          if (savedAssignment) {
            setSelected(savedAssignment)
            setFiles({ ...savedAssignment.starter_code })
          }
        }
      } catch {
        sessionStorage.removeItem('web361lab.token')
        setToken('')
        setIdentity(null)
        setError('Oturum yeniden açılamadı. Lütfen tekrar giriş yapın.')
      }
    }
    void restore()
  }, [token])

  async function login(userId: number) {
    try {
      const result = await request<{ token: string }>(`/demo/login/${userId}`, undefined, { method: 'POST' })
      sessionStorage.setItem('web361lab.token', result.token)
      setToken(result.token)
      setError('')
    } catch { setError('Giriş yapılamadı.') }
  }

  async function openCourse(nextCourse: Course, currentToken = token) {
    try {
      setAssignments(await request<Assignment[]>(`/courses/${nextCourse.id}/assignments`, currentToken))
      setCourse(nextCourse)
      sessionStorage.setItem('web361lab.course', String(nextCourse.id))
      sessionStorage.removeItem('web361lab.assignment')
      setSelected(null)
      setEditing(null)
      setError('')
    } catch { setError('Ödevler alınamadı.') }
  }

  function openAssignment(assignment: Assignment) {
    setFiles({ ...assignment.starter_code })
    sessionStorage.setItem('web361lab.assignment', String(assignment.id))
    setSelected(assignment)
  }

  async function saveAssignment() {
    if (!editing || !course) return
    try {
      await request<Assignment>(editing.id ? `/assignments/${editing.id}` : '/assignments', token, {
        method: editing.id ? 'PUT' : 'POST', body: JSON.stringify(editing),
      })
      await openCourse(course)
    } catch { setError('Ödev kaydedilemedi.') }
  }

  function newAssignment() {
    if (!course) return
    setEditing({ id: 0, course_id: course.id, title: '', description_md: '', side_panel_md: '', starter_code: { html: '', css: '', javascript: '' }, enabled_languages: ['html'], intellisense_enabled: true, paste_enabled: true, due_at: null })
  }

  async function logout() {
    try { await request('/demo/logout', token, { method: 'POST' }) } catch { setError('Oturum sunucuda kapatılamadı.') }
    setToken('')
    sessionStorage.removeItem('web361lab.token')
    sessionStorage.removeItem('web361lab.course')
    sessionStorage.removeItem('web361lab.assignment')
    setIdentity(null)
    setCourses([])
    setCourse(null)
    setSelected(null)
    setEditing(null)
  }

  return <main>
    <h1>web361lab</h1>
    {error && <p role="alert">{error}</p>}
    {!token ? <section><h2>Demo girişi</h2><p>Bir kullanıcı seçin.</p>{users.map((user) => <button key={user.id} onClick={() => login(user.id)}>{user.name} ({user.role === 'teacher' ? 'Öğretim elemanı' : 'Öğrenci'})</button>)}</section> : <>
      <button onClick={logout}>Çıkış</button>
      {!identity ? <p>Oturum yükleniyor…</p> : identity.role === 'student' && !identity.recording_consent ? <section>
        <h2>Çalışma kaydı hakkında</h2>
        <p>Bu uygulamada ödev üzerinde yaptığınız editör değişiklikleri ve bazı etkileşimler kaydedilir. Kayıtlar size ve dersin öğretim elemanına gösterilir.</p>
        <button onClick={async () => {
          try { await request('/me/recording-consent', token, { method: 'POST' }); setIdentity({ ...identity, recording_consent: true }) }
          catch { setError('Onay kaydedilemedi.') }
        }}>Bilgilendirmeyi okudum ve onaylıyorum</button>
      </section> : !course ? <section><h2>Dersler</h2>{courses.length === 0 && <p>Kayıtlı dersiniz bulunmuyor.</p>}{courses.map((item) => <button key={item.id} onClick={() => openCourse(item)}>{item.name}</button>)}</section> : <>
        <button onClick={() => { sessionStorage.removeItem('web361lab.course'); sessionStorage.removeItem('web361lab.assignment'); setCourse(null); setSelected(null); setEditing(null) }}>Dersler</button>
        <h2>{course.name}</h2>
        {editing ? <AssignmentForm assignment={editing} onChange={setEditing} onSave={saveAssignment} onCancel={() => setEditing(null)} /> : selected ? <section>
          <button onClick={() => { sessionStorage.removeItem('web361lab.assignment'); setSelected(null) }}>Ödevler</button>
          <h3>{selected.title}</h3>
          <ReactMarkdown>{selected.description_md}</ReactMarkdown>
          {selected.due_at && <p>Son tarih: {new Date(selected.due_at).toLocaleString('tr-TR')}</p>}
          {course.role === 'student' ? <StudentWorkspace key={`${identity.id}-${selected.id}`} assignment={selected} token={token} userId={identity.id} /> : <div className="workspace">
            <Editor enabledLanguages={selected.enabled_languages} files={files} onChange={(language: Language, value: string) => setFiles((current) => ({ ...current, [language]: value }))} intellisenseEnabled={selected.intellisense_enabled} pasteEnabled={selected.paste_enabled} modelNamespace={`teacher-assignment-${selected.id}`} />
            <Preview files={files} enabledLanguages={selected.enabled_languages} />
            <aside><h3>Ders içeriği</h3><ReactMarkdown>{selected.side_panel_md}</ReactMarkdown></aside>
          </div>}
          {course.role === 'teacher' && <SubmissionReview key={selected.id} assignment={selected} token={token} />}
        </section> : <section><h3>Ödevler</h3>{course.role === 'teacher' && <button onClick={newAssignment}>Yeni ödev</button>}{assignments.map((assignment) => <div key={assignment.id}><button onClick={() => openAssignment(assignment)}>{assignment.title}</button>{course.role === 'teacher' && <button onClick={() => setEditing(assignment)}>Düzenle</button>}</div>)}</section>}
      </>}
    </>}
  </main>
}
