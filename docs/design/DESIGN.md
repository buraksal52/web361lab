# CENG 361 Lab — Tasarım Rehberi

Bu klasördeki `*.dc.html` dosyaları arayüzün **görsel referansıdır**. Birebir kopyalanmaz,
`.dc.html` formatı ve `support.js` projeye taşınmaz. Mevcut stack ile yeniden yazılır.
İş mantığına (auth, API, veri modeli) dokunulmaz, sadece görünüm katmanı değişir.

Kaynak tasarım dili: Ankara Bilim Üniversitesi sitesinden esinlenildi, ama bu **resmî site değil**.
Gerçek üniversite logosu kullanılmaz. Logo yer tutucudur ("ABÜ" kutusu).
Footer'daki "resmî web sitesi değildir" notu kalır.

## Genel
- Sadece açık tema. Dil: Türkçe. Ürün adı: **CENG 361 Lab**.
- Her sayfada sırayla: üst bilgi barı, header, içerik, footer. Bunlar ortak bir layout bileşeni olmalı.

## Tipografi
- Ana font: **Nunito Sans** (400, 600, 700, 800)
- Kod: **JetBrains Mono** (400, 500)

## Renkler
| Rol | Değer |
|---|---|
| Lacivert (ana) | `#112e6e` |
| Mavi (link, vurgu) | `#1e51cb` |
| Hero bandı mavi | `#1c46ad` |
| Koyu kart | `#1e273a` |
| Metin | `#22252f`, ikincil `#344350`, soluk `#526179` |
| Açık zemin | `#f3f6f9`, `#f6f6f6` (üst bar) |
| Kenarlık | `#e6ebef` (üst bar altı `#eeeeee`) |
| Hero içi açık mavi metin | `#b9ccf5`, `#dbe6ff` |

## Şekil
- Buton: 10px radius, yükseklik 44–52px
- Kart: 14px radius, `1px solid #e6ebef`, gölge `0 6px 24px rgba(17,46,110,0.06)`
- Hero kartı: 20px radius, koyu zemin
- Kod bloğu: beyaz zemin, 10px radius, JetBrains Mono

## Layout
- Üst bilgi barı: 38px, `#f6f6f6`, 12.6px/500. Solda okul linki, sağda "CENG 361 · pilot sürüm".
- Header: logo (sol), öğrenci menüsü (Ders, Konular, Ödevler), sağda öğretim üyesi menüsü (Ödev oluştur, Teslimler). Aktif link altında 3px çizgi.
- İçerik: en çok ~1200px, kenar boşluğu 40px.
- Footer: açık zemin, 4 sütun (marka, Ders, Öğretim üyesi, Okul) + alt telif satırı.

## Ekranlar
| Dosya | Ekran | Not |
|---|---|---|
| Main | Giriş | "Teams ile giriş yap" (mock). Rol hesaptan anlaşılır: öğrenci / ders hocası |
| Ders | Ders ana sayfası | Hero, sıradaki ödev, haftalık konular, duyurular |
| Konular | Konu anlatımı | Sol konu ağacı, makale, "bu sayfada" yan paneli |
| Simulasyon | Blok simülasyonu | Ayrı sayfa. Sürükle-bırak, canlı önizleme, bloklar kümülatif |
| Odevler | Ödev listesi | Kural çipleri (Intellisense / yapıştırma kapalı) |
| Editor | Kod editörü ödevi | Editör + canlı önizleme + görev paneli |
| Bloklar | Mantık blokları ödevi | Palet, çalışma alanı, adım adım |
| Sonuc | Teslim sonucu | Puan, kural denetimi, çıktı |
| OdevOlustur | Ödev oluştur (hoca) | Form, kural anahtarları |
| Teslimler | Teslimler (hoca) | Tablo + detay paneli, puan ve yorum |

## Simülasyon kuralları
- Her simülasyon, kendinden önceki konuların bloklarına da sahiptir (palet gruplara ayrılır, "Bu konu" etiketi yeni olanları gösterir).
- Sürükle-bırak çalışmalı, tıkla-ekle yedeği de olmalı.
- Sağda canlı önizleme: oluşan HTML ve stil gösterilir.

## Kod kuralları
- Basit ve orantılı kod. Gereksiz soyutlama yok.
- Renk, font, radius değerleri tasarım token'ı olarak tek yerde tanımlanır.
- Ekranlar sırayla taşınır, her aşama sonunda onay alınır.
