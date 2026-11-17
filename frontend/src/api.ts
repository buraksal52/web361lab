import type { CodeFiles, Language } from './Editor'

export type User = { id: number; name: string; role: string }
export type Course = { id: number; name: string; role: string }
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
