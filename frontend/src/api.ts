import type { CodeFiles, Language } from './Editor'

export type User = { id: number; name: string; role: string }
export type Course = { id: number; name: string; role: string }
export type CheckRule = { id: string; tag: string; attrs: Record<string, string>; min_count: number; non_empty: boolean; inside: string | null; label_linked: boolean }
export type CheckResult = { rule: CheckRule; count: number; used: boolean }
export type LintIssue = { language: string; rule: string; message: string; raw_message: string; line: number; column: number; severity: 'error' | 'warning' }
export type Assignment = {
  id: number
  course_id: number
  title: string
  description_md: string
  side_panel_md: string
  starter_code: CodeFiles
  enabled_languages: Language[]
  intellisense_enabled: boolean
  paste_enabled: boolean
  checker_enabled: boolean
  check_rules?: CheckRule[]
  show_results_to_student: boolean
  diagnostics_enabled: boolean
  lint_rules?: string[]
  due_at: string | null
}

export async function request<T>(path: string, token?: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`/api${path}`, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}), ...options.headers },
  })
  if (!response.ok) throw new Error('İşlem tamamlanamadı. Lütfen tekrar deneyin.')
  return response.json() as Promise<T>
}
