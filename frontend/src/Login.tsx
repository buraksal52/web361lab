import { useState } from 'react'
import type { User } from './api'

export function Login({ users, onLogin }: { users: User[]; onLogin: (id: number) => void }) {
  const [selected, setSelected] = useState('')
  return <main className="login-page">
    <section className="login-band"><div className="login-inner">
      <div className="login-hero"><span className="eyebrow">CENG 361 · WEB PROGRAMLAMA</span><h1><span>Web'i yaz, dene,</span><br />kavra.</h1><p>Ders içeriği, ödevler ve canlı önizleme tek yerde.</p><pre><code><span>&lt;div</span> class="kutu"<span>&gt;</span>{'\n'}  <span>&lt;h1&gt;</span>Merhaba Web<span>&lt;/h1&gt;</span>{'\n'}<span>&lt;/div&gt;</span></code></pre></div>
      <div className="login-panel"><h2>Şimdi derse giriş zamanı!</h2><p>Demo kullanıcını seçerek derslerine ve ödevlerine ulaşabilirsin.</p>
        <label htmlFor="demo-user">Demo kullanıcısı</label><select id="demo-user" value={selected} onChange={(event) => setSelected(event.target.value)}><option value="">Kullanıcı seçin</option>{users.map((user) => <option key={user.id} value={user.id}>{user.name}{user.student_number ? ` — ${user.student_number}` : ''} ({user.role === 'teacher' ? 'Öğretim elemanı' : 'Öğrenci'})</option>)}</select>
        <button type="button" className="login-button" disabled={!selected} onClick={() => onLogin(Number(selected))}>Derse giriş yap <span aria-hidden="true">→</span></button>
        {users.length === 0 && <p>Kullanıcı listesi yükleniyor veya bulunamadı.</p>}
      </div>
    </div></section>
    <section className="feature-grid" aria-label="Platform özellikleri"><article><span className="feature-symbol">&lt;/&gt;</span><h2>Canlı önizleme</h2><p>Yazdıkça sonucu yanında gör.</p></article><article><span className="feature-symbol">▤</span><h2>Ders içeriği</h2><p>Görevini yaparken ders notlarına ulaş.</p></article><article><span className="feature-symbol">✓</span><h2>Açık ödev kuralları</h2><p>Her ödevin kurallarını baştan gör.</p></article><article><span className="feature-symbol">◎</span><h2>Çalışma kaydı</h2><p>Çalışmanı daha sonra incele.</p></article></section>
  </main>
}
