import { useRef, useState } from 'react'
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
  onChange: (language: Language, value: string, event: monaco.editor.IModelContentChangedEvent) => void
  intellisenseEnabled: boolean
  pasteEnabled?: boolean
  onPasteBlocked?: () => void
  modelNamespace?: string
}

export function Editor({ enabledLanguages, files, onChange, intellisenseEnabled, pasteEnabled = true, onPasteBlocked, modelNamespace = 'assignment' }: EditorProps) {
  const [selected, setSelected] = useState<Language | undefined>(enabledLanguages[0])
  const [notice, setNotice] = useState('')
  const editorRef = useRef<monaco.editor.IStandaloneCodeEditor | null>(null)
  const internalClipboard = useRef<string | null>(null)
  const active = selected && enabledLanguages.includes(selected) ? selected : enabledLanguages[0]

  if (!active) return <p>Bu ödevde etkin bir kod sekmesi yok.</p>

  return (
    <section aria-label="Kod editörü" onCopyCapture={() => {
      const editor = editorRef.current
      const selection = editor?.getSelection()
      internalClipboard.current = selection ? editor?.getModel()?.getValueInRange(selection) ?? null : null
    }} onPasteCapture={(event) => {
      if (!pasteEnabled && (internalClipboard.current === null || event.clipboardData.getData('text/plain') !== internalClipboard.current)) {
        event.preventDefault()
        event.stopPropagation()
        setNotice('Dışarıdan yapıştırma bu ödevde kapalı.')
        onPasteBlocked?.()
      }
    }} onDropCapture={(event) => {
      if (!pasteEnabled) {
        event.preventDefault()
        event.stopPropagation()
        setNotice('Sürükleyerek metin bırakma bu ödevde kapalı.')
        onPasteBlocked?.()
      }
    }} onDragOverCapture={(event) => { if (!pasteEnabled) event.preventDefault() }} onKeyDownCapture={(event) => {
      if (!intellisenseEnabled && (event.ctrlKey || event.metaKey) && event.code === 'Space') {
        event.preventDefault()
        event.stopPropagation()
      }
    }}>
      <div aria-label="Kod dilleri">
        {enabledLanguages.map((language) => (
          <button key={language} type="button" aria-pressed={language === active} onClick={() => setSelected(language)}>
            {labels[language]}
          </button>
        ))}
      </div>
      {notice && <p role="status">{notice}</p>}
      <MonacoEditor
        height="60vh"
        path={`${modelNamespace}.${active === 'javascript' ? 'js' : active}`}
        language={active}
        value={files[active]}
        onChange={(value, event) => onChange(active, value ?? '', event)}
        onMount={(editor) => { editorRef.current = editor }}
        options={{
          quickSuggestions: intellisenseEnabled,
          suggestOnTriggerCharacters: intellisenseEnabled,
          wordBasedSuggestions: intellisenseEnabled ? 'matchingDocuments' : 'off',
          parameterHints: { enabled: intellisenseEnabled },
          inlineSuggest: { enabled: intellisenseEnabled },
          tabCompletion: intellisenseEnabled ? 'on' : 'off',
        }}
      />
    </section>
  )
}
