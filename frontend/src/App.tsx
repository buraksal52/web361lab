import { useState } from 'react'
import { Editor, type CodeFiles, type Language } from './Editor'
import { Preview } from './Preview'

const enabledLanguages: Language[] = ['html', 'css', 'javascript']

export function App() {
  const [files, setFiles] = useState<CodeFiles>({ html: '', css: '', javascript: '' })
  const [intellisenseEnabled, setIntellisenseEnabled] = useState(true)

  function updateFile(language: Language, value: string) {
    setFiles((current) => ({ ...current, [language]: value }))
  }

  return (
    <main>
      <h1>web361lab</h1>
      <label>
        <input type="checkbox" checked={intellisenseEnabled} onChange={(event) => setIntellisenseEnabled(event.target.checked)} />
        IntelliSense etkin
      </label>
      <Editor enabledLanguages={enabledLanguages} files={files} onChange={updateFile} intellisenseEnabled={intellisenseEnabled} />
      <Preview files={files} enabledLanguages={enabledLanguages} />
    </main>
  )
}
