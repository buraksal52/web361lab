import { useState } from 'react'
import MonacoEditor, { loader } from '@monaco-editor/react'
import * as monaco from 'monaco-editor'
import EditorWorker from 'monaco-editor/editor/editor.worker.js?worker'
import HtmlWorker from 'monaco-editor/language/html/html.worker.js?worker'
import CssWorker from 'monaco-editor/language/css/css.worker.js?worker'
import TsWorker from 'monaco-editor/language/typescript/ts.worker.js?worker'

if (typeof self !== 'undefined') self.MonacoEnvironment = {
  getWorker(_workerId, label) {
    if (label === 'html' || label === 'handlebars' || label === 'razor') return new HtmlWorker()
    if (label === 'css' || label === 'scss' || label === 'less') return new CssWorker()
    if (label === 'typescript' || label === 'javascript') return new TsWorker()
    return new EditorWorker()
  },
}

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
  intellisenseEnabled: boolean
}

export function Editor({ enabledLanguages, files, onChange, intellisenseEnabled }: EditorProps) {
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
        options={{
          quickSuggestions: intellisenseEnabled,
          suggestOnTriggerCharacters: intellisenseEnabled,
          wordBasedSuggestions: intellisenseEnabled ? 'matchingDocuments' : 'off',
          parameterHints: { enabled: intellisenseEnabled },
          inlineSuggest: { enabled: intellisenseEnabled },
          tabCompletion: intellisenseEnabled ? 'on' : 'off',
        }}
        beforeMount={(instance) => {
          instance.languages.typescript.javascriptDefaults.setEagerModelSync(true)
        }}
        onMount={(editor, instance) => {
          editor.addCommand(instance.KeyMod.CtrlCmd | instance.KeyCode.Space, () => {
            if (editor.getRawOptions().quickSuggestions !== false) {
              editor.trigger('keyboard', 'editor.action.triggerSuggest', {})
            }
          })
        }}
      />
    </section>
  )
}
