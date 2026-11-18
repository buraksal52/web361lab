import type { LintIssue } from './api'

export function WritingReport({ issues }: { issues: LintIssue[] }) {
  return <section><h4>Yazım kontrolü</h4>
    {issues.length === 0 && <p>Seçilen kurallarda bir uyarı bulunmadı.</p>}
    {issues.map((issue, index) => <p key={`${issue.rule}-${issue.line}-${issue.column}-${index}`}>
      {issue.severity === 'error' ? 'Hata' : 'Uyarı'} · {issue.language.toUpperCase()} · {issue.line}:{issue.column} · {issue.message}
    </p>)}
  </section>
}
