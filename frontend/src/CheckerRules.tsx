import type { CheckRule } from './api'

const tags = ['a', 'article', 'button', 'div', 'footer', 'form', 'h1', 'h2', 'h3', 'header', 'img', 'input', 'label', 'li', 'main', 'nav', 'ol', 'option', 'p', 'section', 'select', 'span', 'table', 'tbody', 'td', 'textarea', 'th', 'thead', 'tr', 'ul']
const attributes = ['type', 'name', 'required', 'placeholder']

export function CheckerRules({ rules, onChange }: { rules: CheckRule[]; onChange: (rules: CheckRule[]) => void }) {
  function update(index: number, rule: CheckRule) {
    onChange(rules.map((item, current) => current === index ? rule : item))
  }

  return <fieldset>
    <legend>Gerekli öğeler</legend>
    {rules.map((rule, index) => <fieldset key={rule.id}>
      <legend>Kural {index + 1}</legend>
      <label>Etiket <select value={rule.tag} onChange={(event) => update(index, { ...rule, tag: event.target.value, label_linked: event.target.value === 'input' && rule.label_linked })}>{tags.map((tag) => <option key={tag}>{tag}</option>)}</select></label>
      <label>En az kaç tane <input type="number" min={1} max={100} required value={rule.min_count} onChange={(event) => update(index, { ...rule, min_count: Number(event.target.value) })} /></label>
      <label>Şu öğenin içinde <select value={rule.inside ?? ''} onChange={(event) => update(index, { ...rule, inside: event.target.value || null })}><option value="">Fark etmez</option>{tags.map((tag) => <option key={tag}>{tag}</option>)}</select></label>
      <label><input type="checkbox" checked={rule.non_empty} onChange={(event) => update(index, { ...rule, non_empty: event.target.checked })} /> Metin içeriği boş olmasın</label>
      {rule.tag === 'input' && <label><input type="checkbox" checked={rule.label_linked} onChange={(event) => update(index, { ...rule, label_linked: event.target.checked })} /> Etiket (label) ile ilişkili olsun</label>}
      <fieldset><legend>Özellikler</legend>
        {attributes.map((attribute) => <div key={attribute}>
          <label><input type="checkbox" checked={attribute in rule.attrs} onChange={(event) => {
            const attrs = { ...rule.attrs }
            if (event.target.checked) attrs[attribute] = ''
            else delete attrs[attribute]
            update(index, { ...rule, attrs })
          }} /> {attribute} kullanılsın</label>
          {attribute in rule.attrs && attribute !== 'required' && <label>{attribute} değeri (isteğe bağlı) <input maxLength={200} value={rule.attrs[attribute]} onChange={(event) => update(index, { ...rule, attrs: { ...rule.attrs, [attribute]: event.target.value } })} /></label>}
        </div>)}
      </fieldset>
      <button type="button" onClick={() => onChange(rules.filter((_, current) => current !== index))}>Kuralı kaldır</button>
    </fieldset>)}
    <button type="button" disabled={rules.length >= 100} onClick={() => onChange([...rules, { id: crypto.randomUUID(), tag: 'form', attrs: {}, min_count: 1, non_empty: false, inside: null, label_linked: false }])}>Kural ekle</button>
  </fieldset>
}
