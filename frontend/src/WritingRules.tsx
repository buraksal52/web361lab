const groups = [
  { title: 'HTML', rules: [
    ['html_tag_pair', 'Etiket açılışı ve kapanışı'], ['html_id_unique', 'Tekrarlanan id'],
    ['html_alt', 'Görsellerde alt'], ['html_doctype', 'Doctype bildirimi'],
    ['html_presentational', 'Sunum amaçlı etiketler'],
  ] },
  { title: 'CSS', rules: [
    ['css_syntax', 'Yazım hataları'], ['css_unknown_property', 'Bilinmeyen özellik'],
    ['css_invalid_value', 'Geçersiz değer'],
  ] },
  { title: 'JavaScript', rules: [
    ['js_syntax', 'Yazım hataları'], ['js_eqeqeq', 'Karşılaştırma operatörü'],
    ['js_unused', 'Kullanılmayan değişken'], ['js_undef', 'Tanımlanmamış ad'],
  ] },
  { title: 'Biçim', rules: [['indentation', 'Tutarlı girinti']] },
]

export function WritingRules({ rules, onChange }: { rules: string[]; onChange: (rules: string[]) => void }) {
  return <fieldset><legend>Yazım kontrolleri</legend>
    {groups.map((group) => <fieldset key={group.title}><legend>{group.title}</legend>
      {group.rules.map(([id, label]) => <label key={id}><input type="checkbox" checked={rules.includes(id)} onChange={(event) => onChange(event.target.checked ? [...rules, id] : rules.filter((rule) => rule !== id))} /> {label}</label>)}
    </fieldset>)}
  </fieldset>
}
