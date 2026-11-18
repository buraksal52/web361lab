import { renderToStaticMarkup } from 'react-dom/server'
import { expect, test } from 'vitest'
import { CheckResults } from './CheckResults'

test('explains each rule using neutral usage wording and counts', () => {
  const rule = { id: 'rule', tag: 'input', attrs: { type: 'email' }, min_count: 2, non_empty: false, inside: 'form', label_linked: true }
  const html = renderToStaticMarkup(<CheckResults results={[{ rule, count: 1, used: false }]} />)
  expect(html).toContain('Kullanılmamış')
  expect(html).toContain('1 bulundu; en az 2')
  expect(html).toContain('email')
  expect(html).toContain('form')
})
