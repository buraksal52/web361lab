import { useState } from 'react'
import type { User } from './api'

export function Login({ users, onLogin }: { users: User[]; onLogin: (id: number) => void }) {
  const [selected, setSelected] = useState('')
  return <main className="login-page">
    <section className="login-band"><div className="login-inner">
      <div className="login-hero"><span className="eyebrow">CENG 361 · WEB PROGRAMLAMA</span><h1><span>Web'i yaz, dene,</span><br />kavra.</h1><p>Ders içeriği, ödevler ve canlı önizleme tek yerde.</p></div>
      <div className="login-panel" id="giris"><h2>Şimdi derse giriş zamanı!</h2><p>Demo kullanıcını seçerek derslerine ve ödevlerine ulaşabilirsin.</p>
        <label htmlFor="demo-user">Demo kullanıcısı</label><select id="demo-user" value={selected} onChange={(event) => setSelected(event.target.value)}><option value="">Kullanıcı seçin</option>{users.map((user) => <option key={user.id} value={user.id}>{user.name}{user.student_number ? ` — ${user.student_number}` : ''} ({user.role === 'teacher' ? 'Öğretim elemanı' : 'Öğrenci'})</option>)}</select>
        <button type="button" className="login-button" disabled={!selected} onClick={() => onLogin(Number(selected))}>Derse giriş yap <span aria-hidden="true">→</span></button>
        {users.length === 0 && <p>Kullanıcı listesi yükleniyor veya bulunamadı.</p>}
      </div>
    </div></section>
    <section className="feature-grid" id="platform" aria-label="Platform özellikleri"><article><div className="feature-visual feature-preview" aria-hidden="true" /><div className="feature-copy"><h2>Canlı önizleme</h2><p>Yazdıkça sonucu yanında gör.</p></div></article><article><div className="feature-visual feature-content" aria-hidden="true" /><div className="feature-copy"><h2>Ders içeriği</h2><p>Görevini yaparken ders notlarına ulaş.</p></div></article><article><div className="feature-visual feature-rules" aria-hidden="true" /><div className="feature-copy"><h2>Açık ödev kuralları</h2><p>Her ödevin kurallarını baştan gör.</p></div></article><article><div className="feature-visual feature-replay" aria-hidden="true" /><div className="feature-copy"><h2>Çalışma kaydı</h2><p>Çalışmanı daha sonra incele.</p></div></article></section>
  </main>
}
