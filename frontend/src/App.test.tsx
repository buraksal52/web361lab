import { renderToStaticMarkup } from 'react-dom/server'
import { expect, test } from 'vitest'
import { App } from './App'

test('shows the application name', () => {
  expect(renderToStaticMarkup(<App />)).toContain('web361lab')
})
