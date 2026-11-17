import { useState } from 'react'
import { Editor, type CodeFiles, type Language } from './Editor'

export function App() {
  const [files, setFiles] = useState<CodeFiles>({ html: '', css: '', javascript: '' })

  function updateFile(language: Language, value: string) {
    setFiles((current) => ({ ...current, [language]: value }))
  }

  return <main><h1>web361lab</h1><Editor enabledLanguages={['html', 'css', 'javascript']} files={files} onChange={updateFile} /></main>
}
