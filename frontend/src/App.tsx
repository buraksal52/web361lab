import { useEffect, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { AssignmentForm } from './AssignmentForm'
import { Editor, type CodeFiles, type Language } from './Editor'
import { Preview } from './Preview'
import { request, type Assignment, type Course, type User } from './api'
import './style.css'

export function App() {
  const [users, setUsers] = useState<User[]>([])
  const [token, setToken] = useState('')
  const [courses, setCourses] = useState<Course[]>([])
  const [course, setCourse] = useState<Course | null>(null)
  const [assignments, setAssignments] = useState<Assignment[]>([])
  const [selected, setSelected] = useState<Assignment | null>(null)
  const [editing, setEditing] = useState<Assignment | null>(null)
  const [files, setFiles] = useState<CodeFiles>({ html: '', css: '', javascript: '' })
  const [error, setError] = useState('')

  useEffect(() => { request<User[]>('/demo/users').then(setUsers).catch(() => setError('Kullanıcı listesi alınamadı.')) }, [])

  async function login(userId: number) {
    try {
      const result = await request<{ token: string }>(`/demo/login/${userId}`, undefined, { method: 'POST' })
      setToken(result.token)
      setCourses(await request<Course[]>('/courses', result.token))
      setError('')
    } catch { setError('Giriş yapılamadı.') }
  }

  async function openCourse(nextCourse: Course, currentToken = token) {
    try {
      setAssignments(await request<Assignment[]>(`/courses/${nextCourse.id}/assignments`, currentToken))
      setCourse(nextCourse)
      setSelected(null)
      setEditing(null)
      setError('')
    } catch { setError('Ödevler alınamadı.') }
  }

  function openAssignment(assignment: Assignment) {
    setFiles({ ...assignment.starter_code })
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
      {!course ? <section><h2>Dersler</h2>{courses.length === 0 && <p>Kayıtlı dersiniz bulunmuyor.</p>}{courses.map((item) => <button key={item.id} onClick={() => openCourse(item)}>{item.name}</button>)}</section> : <>
        <button onClick={() => { setCourse(null); setSelected(null); setEditing(null) }}>Dersler</button>
        <h2>{course.name}</h2>
        {editing ? <AssignmentForm assignment={editing} onChange={setEditing} onSave={saveAssignment} onCancel={() => setEditing(null)} /> : selected ? <section>
          <button onClick={() => setSelected(null)}>Ödevler</button>
          <h3>{selected.title}</h3>
          <ReactMarkdown>{selected.description_md}</ReactMarkdown>
          {selected.due_at && <p>Son tarih: {new Date(selected.due_at).toLocaleString('tr-TR')}</p>}
          <div className="workspace">
            <Editor enabledLanguages={selected.enabled_languages} files={files} onChange={(language: Language, value: string) => setFiles((current) => ({ ...current, [language]: value }))} intellisenseEnabled={selected.intellisense_enabled} pasteEnabled={selected.paste_enabled} />
            <Preview files={files} enabledLanguages={selected.enabled_languages} />
            <aside><h3>Ders içeriği</h3><ReactMarkdown>{selected.side_panel_md}</ReactMarkdown></aside>
          </div>
        </section> : <section><h3>Ödevler</h3>{course.role === 'teacher' && <button onClick={newAssignment}>Yeni ödev</button>}{assignments.map((assignment) => <div key={assignment.id}><button onClick={() => openAssignment(assignment)}>{assignment.title}</button>{course.role === 'teacher' && <button onClick={() => setEditing(assignment)}>Düzenle</button>}</div>)}</section>}
      </>}
    </>}
  </main>
}
