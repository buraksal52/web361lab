import type { ReactNode } from 'react'

type Props = { children: ReactNode; signedIn: boolean; courseOpen: boolean; teacher: boolean; onCourses: () => void; onAssignments: () => void; onCreate: () => void; onLogout: () => void }

function Brand() {
  return <span className="brand"><span className="brand-mark">ABÜ</span><span><strong>CENG 361 Lab</strong><small>Ankara Bilim Üniversitesi · Web Programlama</small></span></span>
}

export function Layout({ children, signedIn, courseOpen, teacher, onCourses, onAssignments, onCreate, onLogout }: Props) {
  return <div className="app-shell">
    <div className="topbar"><div><span className="topbar-links"><a href="https://ankarabilim.edu.tr">Ankara Bilim Üniversitesi</a><a href="https://kutuphane.ankarabilim.edu.tr">Kütüphane</a></span><span>CENG 361 · pilot sürüm</span></div></div>
    <header className="site-header"><Brand />
      {!signedIn && <><nav aria-label="Ana menü" className="site-nav landing-nav"><a href="#platform">Platform</a><a href="#giris">Derse giriş</a></nav><div className="header-spacer" /><a className="header-signin" href="#giris">Giriş yap</a></>}
      {signedIn && <><nav aria-label="Ders menüsü" className="site-nav"><button type="button" onClick={onCourses}>Dersler</button>{courseOpen && <button type="button" onClick={onAssignments}>Ödevler</button>}</nav>
        <div className="header-spacer" />
        {teacher && courseOpen && <nav aria-label="Öğretim üyesi" className="site-nav teacher-nav"><span>ÖĞRETİM ÜYESİ</span><button type="button" onClick={onCreate}>Ödev oluştur</button></nav>}
        <button type="button" className="header-logout" onClick={onLogout}>Çıkış</button></>}
    </header>
    {children}
    <footer className="site-footer"><div className="footer-content"><div className="footer-brand"><Brand /><p>Web Programlama dersi için ödev ve ders içeriği platformu. Pilot sürüm.</p></div><div><strong>Ders</strong>{signedIn && <button type="button" onClick={onCourses}>Dersler</button>}{signedIn && courseOpen && <button type="button" onClick={onAssignments}>Ödevler</button>}</div>{teacher && courseOpen && <div><strong>Öğretim üyesi</strong><button type="button" onClick={onCreate}>Ödev oluştur</button></div>}<div><strong>Okul</strong><a href="https://ankarabilim.edu.tr">Ankara Bilim Üniversitesi</a></div></div>
      <div className="footer-bottom">© 2026 CENG 361 Lab · Ders projesi. Ankara Bilim Üniversitesi'nin resmî web sitesi değildir.</div>
    </footer>
  </div>
}
