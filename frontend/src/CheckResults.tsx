import type { CheckResult } from './api'

export function CheckResults({ results }: { results: CheckResult[] }) {
  return <section>
    <h4>Öğe kullanım kontrolü</h4>
    <p>Bu kontrol öğelerin kullanımını inceler; çalışıp çalışmadığını değerlendirmez.</p>
    {results.length === 0 && <p>Kontrol kuralı tanımlanmamış.</p>}
    {results.map(({ rule, count, used }) => <div key={rule.id}>
      <p>{rule.tag} — {used ? 'Kullanılmış' : 'Kullanılmamış'} ({count} bulundu; en az {rule.min_count})</p>
      {Object.entries(rule.attrs).map(([name, value]) => <p key={name}>Özellik: {name}{value ? ` = ${value}` : ' (bulunmalı)'}</p>)}
      {rule.inside && <p>İçinde: {rule.inside}</p>}
      {rule.non_empty && <p>Metin içeriği boş olmamalı</p>}
      {rule.label_linked && <p>Etiket (label) ile ilişkili olmalı</p>}
    </div>)}
  </section>
}
