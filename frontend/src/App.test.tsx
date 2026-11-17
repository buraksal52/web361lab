import { renderToStaticMarkup } from 'react-dom/server'
import { expect, test, vi } from 'vitest'
import { App } from './App'
import { Editor } from './Editor'
import { Preview, previewDocument } from './Preview'

vi.mock('monaco-editor', () => ({}))
vi.mock('monaco-editor/editor/editor.worker.js?worker', () => ({ default: class {} }))
vi.mock('monaco-editor/language/html/html.worker.js?worker', () => ({ default: class {} }))
vi.mock('monaco-editor/language/css/css.worker.js?worker', () => ({ default: class {} }))
vi.mock('monaco-editor/language/typescript/ts.worker.js?worker', () => ({ default: class {} }))
vi.mock('@monaco-editor/react', () => ({
  default: ({ options }: { options: { quickSuggestions: boolean; suggestOnTriggerCharacters: boolean } }) => (
    <div data-quick-suggestions={String(options.quickSuggestions)} data-trigger-suggestions={String(options.suggestOnTriggerCharacters)} />
  ),
  loader: { config: () => {} },
}))

test('shows the application name', () => {
  expect(renderToStaticMarkup(<App />)).toContain('web361lab')
})

test('shows only enabled language tabs', () => {
  const markup = renderToStaticMarkup(
    <Editor enabledLanguages={['html']} files={{ html: '', css: '', javascript: '' }} onChange={() => {}} intellisenseEnabled={false} />,
  )
  expect(markup).toContain('HTML')
  expect(markup).not.toContain('CSS')
  expect(markup).not.toContain('JavaScript')
  expect(markup).toContain('data-quick-suggestions="false"')
  expect(markup).toContain('data-trigger-suggestions="false"')
})

test('preview isolates the frame and excludes disabled language code', () => {
  const files = { html: '<h1>Merhaba</h1>', css: 'body { color: red }', javascript: 'alert(1)' }
  const markup = renderToStaticMarkup(<Preview files={files} enabledLanguages={['html']} />)
  expect(markup).toContain('sandbox="allow-scripts"')
  expect(markup).not.toContain('allow-same-origin')
  const document = previewDocument(files, ['html'])
  expect(document).toContain('<h1>Merhaba</h1>')
  expect(document).not.toContain(files.css)
  expect(document).not.toContain(files.javascript)
})
