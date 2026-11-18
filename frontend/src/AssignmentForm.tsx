import type { Assignment } from './api'
import type { Language } from './Editor'
import { CheckerRules } from './CheckerRules'
import { WritingRules } from './WritingRules'
import { RubricEditor } from './RubricEditor'

type Props = {
  assignment: Assignment
  onChange: (assignment: Assignment) => void
  onSave: () => void
  onCancel: () => void
}

const languages: Language[] = ['html', 'css', 'javascript']

function localDateTime(value: string | null) {
  if (!value) return ''
  const date = new Date(value)
  return new Date(date.getTime() - date.getTimezoneOffset() * 60000).toISOString().slice(0, 16)
}

export function AssignmentForm({ assignment, onChange, onSave, onCancel }: Props) {
  const criteria = assignment.criteria ?? []
  const rules = assignment.check_rules ?? []
  const missingRule = criteria.some((criterion) => criterion.kind === 'auto' && !rules.some((rule) => rule.id === criterion.check_rule_ref))
  function update(key: keyof Assignment, value: unknown) {
    onChange({ ...assignment, [key]: value })
  }

  return <form onSubmit={(event) => { event.preventDefault(); onSave() }}>
    <h2>Ödev düzenle</h2>
    <label>Başlık <input required value={assignment.title} onChange={(event) => update('title', event.target.value)} /></label>
    <label>Ödev açıklaması <textarea value={assignment.description_md} onChange={(event) => update('description_md', event.target.value)} /></label>
    <label>Ders içeriği <textarea value={assignment.side_panel_md} onChange={(event) => update('side_panel_md', event.target.value)} /></label>
    <label>Son tarih <input type="datetime-local" value={localDateTime(assignment.due_at)} onChange={(event) => update('due_at', event.target.value ? new Date(event.target.value).toISOString() : null)} /></label>
    <fieldset><legend>Etkin sekmeler</legend>
      {languages.map((language) => <label key={language}>
        <input type="checkbox" checked={assignment.enabled_languages.includes(language)} onChange={(event) => update('enabled_languages', event.target.checked ? [...assignment.enabled_languages, language] : assignment.enabled_languages.filter((item) => item !== language))} /> {language.toUpperCase()}
      </label>)}
    </fieldset>
    {languages.filter((language) => assignment.enabled_languages.includes(language)).map((language) => <label key={language}>
      {language.toUpperCase()} başlangıç kodu
      <textarea value={assignment.starter_code[language]} onChange={(event) => update('starter_code', { ...assignment.starter_code, [language]: event.target.value })} />
    </label>)}
    <label><input type="checkbox" checked={assignment.intellisense_enabled} onChange={(event) => update('intellisense_enabled', event.target.checked)} /> IntelliSense etkin</label>
    <label><input type="checkbox" checked={assignment.paste_enabled} onChange={(event) => update('paste_enabled', event.target.checked)} /> Dışarıdan yapıştırma etkin</label>
    <label><input type="checkbox" checked={assignment.diagnostics_enabled} onChange={(event) => update('diagnostics_enabled', event.target.checked)} /> Editörde canlı hata gösterimi etkin</label>
    <WritingRules rules={assignment.lint_rules ?? []} onChange={(rules) => update('lint_rules', rules)} />
    <label><input type="checkbox" checked={assignment.checker_enabled} onChange={(event) => update('checker_enabled', event.target.checked)} /> Öğe kullanım kontrolü etkin</label>
    {assignment.checker_enabled && <>
      <CheckerRules rules={assignment.check_rules ?? []} onChange={(rules) => update('check_rules', rules)} />
      <label><input type="checkbox" checked={assignment.show_results_to_student} onChange={(event) => update('show_results_to_student', event.target.checked)} /> Kontrol kurallarını ve sonuçlarını öğrenciye göster</label>
    </>}
    <RubricEditor criteria={criteria} rules={rules} checkerEnabled={assignment.checker_enabled} onChange={(value) => update('criteria', value)} />
    {missingRule && <p role="alert">Otomatik kriterler için bir kontrol kuralı seçin veya ilgili kriteri kaldırın.</p>}
    <button type="submit" disabled={assignment.enabled_languages.length === 0 || missingRule}>Kaydet</button>
    <button type="button" onClick={onCancel}>İptal</button>
  </form>
}
