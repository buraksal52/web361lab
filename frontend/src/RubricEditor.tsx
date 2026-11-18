import type { CheckRule, Criterion } from './api'

type Props = {
  criteria: Criterion[]
  rules: CheckRule[]
  checkerEnabled: boolean
  onChange: (criteria: Criterion[]) => void
}

export function RubricEditor({ criteria, rules, checkerEnabled, onChange }: Props) {
  function update(index: number, criterion: Criterion) {
    onChange(criteria.map((item, current) => current === index ? criterion : item))
  }

  function add(kind: 'manual' | 'auto') {
    onChange([...criteria, { id: crypto.randomUUID(), kind, label: '', max_points: '0', check_rule_ref: kind === 'auto' ? rules[0].id : null }])
  }

  return <fieldset>
    <legend>Değerlendirme kriterleri</legend>
    <p>Otomatik kriterler seçilen kontrol kurallarına dayanır; diğer kriterleri öğretim elemanı değerlendirir.</p>
    {!checkerEnabled && criteria.some((criterion) => criterion.kind === 'auto') && <p>Öğe kullanım kontrolü kapalıyken otomatik kontrol sonucu üretilmez.</p>}
    {criteria.map((criterion, index) => <fieldset key={criterion.id}>
      <legend>{criterion.kind === 'auto' ? 'Otomatik' : 'Manuel'} kriter {index + 1}</legend>
      <label>Kriter açıklaması <input required maxLength={200} value={criterion.label} onChange={(event) => update(index, { ...criterion, label: event.target.value })} /></label>
      <label>Azami puan <input type="number" min="0" max="99999999.99" step="0.01" required value={criterion.max_points} onChange={(event) => update(index, { ...criterion, max_points: event.target.value })} /></label>
      {criterion.kind === 'auto' && <label>Kontrol kuralı <select required value={criterion.check_rule_ref ?? ''} onChange={(event) => update(index, { ...criterion, check_rule_ref: event.target.value })}>
        {!rules.some((rule) => rule.id === criterion.check_rule_ref) && <option value={criterion.check_rule_ref ?? ''}>Kontrol kuralı seçin</option>}
        {rules.map((rule, ruleIndex) => <option key={rule.id} value={rule.id}>Kural {ruleIndex + 1}: {rule.tag}</option>)}
      </select></label>}
      <button type="button" onClick={() => onChange(criteria.filter((_, current) => current !== index))}>Kriteri kaldır</button>
    </fieldset>)}
    <button type="button" disabled={criteria.length >= 100} onClick={() => add('manual')}>Manuel kriter ekle</button>
    <button type="button" disabled={rules.length === 0 || criteria.length >= 100} onClick={() => add('auto')}>Otomatik kriter ekle</button>
  </fieldset>
}
