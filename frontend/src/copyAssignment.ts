import type { Assignment } from './api'

export function copyAssignment(source: Assignment): Assignment {
  const ruleIds = new Map((source.check_rules ?? []).map((rule) => [rule.id, crypto.randomUUID()]))
  return { ...source, id: 0, title: `${source.title.slice(0, 190)} (kopya)`,
    check_rules: (source.check_rules ?? []).map((rule) => ({ ...rule, id: ruleIds.get(rule.id)! })),
    criteria: (source.criteria ?? []).map((criterion) => ({ ...criterion, id: crypto.randomUUID(), check_rule_ref: criterion.check_rule_ref ? ruleIds.get(criterion.check_rule_ref) ?? null : null })),
  }
}
