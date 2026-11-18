import { useEffect, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { AssignmentForm } from './AssignmentForm'
import { Editor, type CodeFiles, type Language } from './Editor'
import { Preview } from './Preview'
import { request, type Assignment, type Course, type User } from './api'
import { StudentWorkspace } from './StudentWorkspace'
import { SubmissionReview } from './SubmissionReview'
import { StudentRoster } from './StudentRoster'
import { copyAssignment } from './copyAssignment'
import { Layout } from './Layout'
import { Login } from './Login'
import './style.css'
import './design.css'

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
    setEditing({ id: 0, course_id: course.id, title: '', description_md: '', side_panel_md: '', starter_code: { html: '', css: '', javascript: '' }, enabled_languages: ['html'], intellisense_enabled: true, paste_enabled: true, diagnostics_enabled: false, lint_rules: [], checker_enabled: false, check_rules: [], show_results_to_student: false, show_criteria_to_student: false, criteria: [], due_at: null })
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
    try { setUsers(await request<User[]>('/demo/users')) } catch { setError('Kullanıcı listesi alınamadı.') }
  }

  function showCourses() {
    sessionStorage.removeItem('web361lab.course')
    sessionStorage.removeItem('web361lab.assignment')
    setCourse(null); setSelected(null); setEditing(null)
  }

  function showAssignments() {
    sessionStorage.removeItem('web361lab.assignment')
    setSelected(null); setEditing(null)
  }

  return <Layout signedIn={!!token} courseOpen={!!course} teacher={course?.role === 'teacher'} onCourses={showCourses} onAssignments={showAssignments} onCreate={newAssignment} onLogout={logout}>
    {error && <p role="alert">{error}</p>}
    {!token ? <Login users={users} onLogin={login} /> : <main className="page-container">
      {!identity ? <p>Oturum yükleniyor…</p> : identity.role === 'student' && !identity.recording_consent ? <section className="card consent-card">
        <h2>Çalışma kaydı hakkında</h2>
        <p>Bu uygulamada ödev üzerinde yaptığınız editör değişiklikleri ve bazı etkileşimler kaydedilir. Kayıtlar size ve dersin öğretim elemanına gösterilir.</p>
        <button className="button-primary" onClick={async () => {
          try { await request('/me/recording-consent', token, { method: 'POST' }); setIdentity({ ...identity, recording_consent: true }) }
          catch { setError('Onay kaydedilemedi.') }
        }}>Bilgilendirmeyi okudum ve onaylıyorum</button>
      </section> : !course ? <section className="course-page"><div className="course-hero"><span className="eyebrow">CENG 361 · WEB PROGRAMLAMA</span><h1>Derslerine hoş geldin.</h1><p>Ders içeriği ve ödevlerine buradan ulaşabilirsin.</p></div><div className="page-heading"><div><h2>Dersler</h2><p>Kayıtlı olduğun dersi seç.</p></div></div>{courses.length === 0 && <p className="card empty-state">Kayıtlı dersiniz bulunmuyor.</p>}<div className="course-grid">{courses.map((item) => <article className="card course-card" key={item.id}><span className="eyebrow dark">DERS</span><h3>{item.name}</h3><p>Ödevleri ve ders içeriğini görüntüle.</p><button className="button-primary" onClick={() => openCourse(item)}>Derse git →</button></article>)}</div></section> : <>
        {!selected && !editing && <div className="page-heading"><div><span className="breadcrumb">Dersler / {course.name}</span><h1>Ödevler</h1><p>Her ödevin kuralları ve son teslim tarihi burada.</p></div>{course.role === 'teacher' && <button className="button-primary" onClick={newAssignment}>+ Yeni ödev</button>}</div>}
        {editing ? <AssignmentForm assignment={editing} onChange={setEditing} onSave={saveAssignment} onCancel={() => setEditing(null)} /> : selected ? <section>
          <div className="assignment-heading"><div><button className="text-button" onClick={showAssignments}>Ödevler</button><span className="breadcrumb"> / Kod yazma</span><h1>{selected.title}</h1></div><div className="rule-chips">{!selected.intellisense_enabled && <span className="chip warning">IntelliSense kapalı</span>}{!selected.paste_enabled && <span className="chip warning">Yapıştırma kapalı</span>}{selected.due_at && <span className="due-date">Son teslim: {new Date(selected.due_at).toLocaleString('tr-TR')}</span>}</div></div>
          {selected.description_md && <div className="assignment-description"><ReactMarkdown>{selected.description_md}</ReactMarkdown></div>}
          {course.role === 'student' && selected.show_criteria_to_student && selected.criteria && <section>
            <h4>Değerlendirme kriterleri</h4>
            {selected.criteria.length === 0 ? <p>Henüz kriter tanımlanmamış.</p> : <ul>{selected.criteria.map((criterion) => <li key={criterion.id}>{criterion.label} — azami {criterion.max_points} puan</li>)}</ul>}
          </section>}
          {course.role === 'student' ? <StudentWorkspace key={`${identity.id}-${selected.id}`} assignment={selected} token={token} userId={identity.id} /> : <div className="workspace">
            <Editor enabledLanguages={selected.enabled_languages} files={files} onChange={(language: Language, value: string) => setFiles((current) => ({ ...current, [language]: value }))} intellisenseEnabled={selected.intellisense_enabled} diagnosticsEnabled={selected.diagnostics_enabled} pasteEnabled={selected.paste_enabled} modelNamespace={`teacher-assignment-${selected.id}`} />
            <div className="workspace-side"><section className="preview-card"><div className="panel-bar">Canlı önizleme <span>Güncel</span></div><Preview files={files} enabledLanguages={selected.enabled_languages} /></section><aside className="content-card"><h3>Ders içeriği</h3><ReactMarkdown>{selected.side_panel_md}</ReactMarkdown></aside></div>
          </div>}
          {course.role === 'teacher' && <SubmissionReview key={selected.id} assignment={selected} token={token} />}
        </section> : <><section className="assignment-list card"><div className="assignment-list-head"><span>ÖDEV</span><span>TÜR</span><span>KURALLAR</span><span>SON TESLİM</span><span /></div>{assignments.length === 0 && <p className="empty-state">Bu derste henüz ödev yok.</p>}{assignments.map((assignment) => <article className="assignment-row" key={assignment.id}><div><strong>{assignment.title}</strong><small>{course.name}</small></div><span>Kod yazma</span><div className="rule-chips">{!assignment.intellisense_enabled && <span className="chip warning">IntelliSense kapalı</span>}{!assignment.paste_enabled && <span className="chip warning">Yapıştırma kapalı</span>}{assignment.intellisense_enabled && assignment.paste_enabled && <span className="chip">Serbest araçlar</span>}</div><span>{assignment.due_at ? new Date(assignment.due_at).toLocaleDateString('tr-TR') : 'Belirtilmedi'}</span><div className="row-actions"><button className="button-primary" onClick={() => openAssignment(assignment)}>{course.role === 'teacher' ? 'İncele' : 'Başla'}</button>{course.role === 'teacher' && <><button className="button-quiet" aria-label={`${assignment.title} ödevini düzenle`} onClick={() => setEditing(assignment)}>Düzenle</button><button className="button-quiet" aria-label={`${assignment.title} ödevini kopyala`} onClick={() => setEditing(copyAssignment(assignment))}>Kopyala</button></>}</div></article>)}</section>{course.role === 'teacher' && <div className="roster-card card"><StudentRoster courseId={course.id} token={token} /></div>}</>}
      </>}
    </main>}
  </Layout>
}
