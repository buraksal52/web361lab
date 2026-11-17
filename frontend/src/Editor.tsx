import { useState } from 'react'
import MonacoEditor, { loader } from '@monaco-editor/react'
import * as monaco from 'monaco-editor'

loader.config({ monaco })

export type Language = 'html' | 'css' | 'javascript'
export type CodeFiles = Record<Language, string>

const labels: Record<Language, string> = {
  html: 'HTML',
  css: 'CSS',
  javascript: 'JavaScript',
}

type EditorProps = {
  enabledLanguages: Language[]
  files: CodeFiles
  onChange: (language: Language, value: string) => void
}

export function Editor({ enabledLanguages, files, onChange }: EditorProps) {
  const [selected, setSelected] = useState<Language | undefined>(enabledLanguages[0])
  const active = selected && enabledLanguages.includes(selected) ? selected : enabledLanguages[0]

  if (!active) return <p>Bu ödevde etkin bir kod sekmesi yok.</p>

  return (
    <section aria-label="Kod editörü">
      <div aria-label="Kod dilleri">
        {enabledLanguages.map((language) => (
          <button key={language} type="button" aria-pressed={language === active} onClick={() => setSelected(language)}>
            {labels[language]}
          </button>
        ))}
      </div>
      <MonacoEditor
        height="60vh"
        path={`assignment.${active === 'javascript' ? 'js' : active}`}
        language={active}
        value={files[active]}
        onChange={(value) => onChange(active, value ?? '')}
      />
    </section>
  )
}
