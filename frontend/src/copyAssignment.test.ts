import { describe, expect, it } from 'vitest'
import { copyAssignment } from './copyAssignment'
import type { Assignment } from './api'

describe('copyAssignment', () => {
  it('copies settings and reconnects new automatic criteria to new rules', () => {
    const source = { id: 12, title: 'Form', checker_enabled: true, paste_enabled: false,
      check_rules: [{ id: 'original-rule', tag: 'form', attrs: {}, min_count: 1, non_empty: false, inside: null, label_linked: false }],
      criteria: [{ id: 'original-criterion', kind: 'auto', label: 'Form', max_points: '10', check_rule_ref: 'original-rule' }],
    } as Assignment
    const result = copyAssignment(source)
    expect(result.id).toBe(0)
    expect(result.paste_enabled).toBe(false)
    expect(result.check_rules![0].id).not.toBe('original-rule')
    expect(result.criteria![0].id).not.toBe('original-criterion')
    expect(result.criteria![0].check_rule_ref).toBe(result.check_rules![0].id)
    expect(source.criteria![0].check_rule_ref).toBe('original-rule')
  })
})
