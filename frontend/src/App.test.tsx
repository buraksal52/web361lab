import { renderToStaticMarkup } from 'react-dom/server'
import { expect, test, vi } from 'vitest'
import { App } from './App'
import { Editor } from './Editor'

vi.mock('monaco-editor', () => ({}))
vi.mock('@monaco-editor/react', () => ({
  default: () => null,
  loader: { config: () => {} },
}))

test('shows the application name', () => {
  expect(renderToStaticMarkup(<App />)).toContain('web361lab')
})

test('shows only enabled language tabs', () => {
  const markup = renderToStaticMarkup(
    <Editor enabledLanguages={['html']} files={{ html: '', css: '', javascript: '' }} onChange={() => {}} />,
  )
  expect(markup).toContain('HTML')
  expect(markup).not.toContain('CSS')
  expect(markup).not.toContain('JavaScript')
})
