# web361lab Documentation

> **Status:** Draft v0.3 (17 November 2026)
> **Project name:** web361lab (working title for the web course assignment platform)

This folder is the single source of truth for the project. If `AGENTS.md` and a file here conflict, the file here wins.

## Index

| File | Purpose |
|---|---|
| [instructor-brief.md](instructor-brief.md) | Half-page summary for presenting the idea to the course instructor |
| [vision-and-scope.md](vision-and-scope.md) | Goal, stakeholders, what is in and out of scope |
| [requirements.md](requirements.md) | Functional and non-functional requirements (MoSCoW) |
| [use-cases.md](use-cases.md) | Main user flows |
| [architecture.md](architecture.md) | Components, data model, replay events, checker, rubric, linter |
| [decisions.md](decisions.md) | Architecture decision records (ADR-01 to ADR-15) |
| [risks.md](risks.md) | Risk register with mitigations |
| [test-strategy.md](test-strategy.md) | What is tested and how |
| [roadmap.md](roadmap.md) | Phases, sprints, definitions of done, decision points |
| [backlog.md](backlog.md) | Work items per sprint, traced to requirements |
| [php-subset-spec.md](php-subset-spec.md) | Draft PHP subset for the later interpreter (Phase 3) |
| [assumptions-and-open-questions.md](assumptions-and-open-questions.md) | Assumptions to confirm and questions still open |

## Suggested reading order

1. vision-and-scope → requirements → use-cases
2. architecture → decisions
3. roadmap → backlog (to see what is being built now)

## Conventions

- Documents, code identifiers and code comments are in English.
- User-facing UI text is in Turkish (see assumption A9).
- IDs are stable and used across files: `FR-` (functional requirement), `NFR-` (non-functional), `UC-` (use case), `ADR-` (decision), `R` (risk), `S` (sprint), `A` (assumption), `Q` (open question).
- When a decision changes, update `decisions.md` first, then the files that depend on it.

## Change log

| Version | Date | Change |
|---|---|---|
| v0.3 | 17 Nov 2026 | Project named web361lab. Documents translated to English. Single plan split into separate files under `docs/`. Backlog added |
| v0.2 | 17 Nov 2026 | Natural-language assignments, optional checker, lint, rubric, LLM comment layer moved to Phase 2, sprints S0-S8 |
| v0.1 | 17 Nov 2026 | First plan draft |
