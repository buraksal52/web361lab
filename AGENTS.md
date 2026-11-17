# AGENTS.md

These rules are binding for every coding agent working on web361lab. The source documents are in `docs/` (start with `docs/README.md`). If this file and the documents conflict, the documents win.

## 1. Working rhythm (the most important rule)

- **Ask the user for approval before every sprint and every step.** Do not move to the next sprint, phase or step without approval. Never advance on your own.
- Before starting a step, write briefly what you will do (which files, what result) and ask "Shall I start?".
- When a step is done, summarize what you did in 2-3 sentences and suggest the next step. Then stop and wait for approval.
- If something is unclear, do not guess, ask.

## 2. Fidelity to the documents

- Before starting, read the relevant files in `docs/`: `requirements.md`, `architecture.md`, `decisions.md`, and the current sprint in `roadmap.md` and `backlog.md`.
- Work only on backlog items of the current, approved sprint.
- **Do not add features that are not in the documents.** Even if you think it would be useful, do not add it; only suggest it and ask the user.
- Do not touch anything outside the MVP or in later phases: Teams, SSO, transferring grades to Teams, **LLM/AI calls and the comment layer**, the PHP interpreter, blocks, SQL.
- Do not change the tech stack (ADR-10 in `docs/decisions.md`) or add a big new dependency without the user's approval.
- If the documents are missing something or wrong, suggest how to update them before changing code.

## 3. Coding principles

- **Write simple and proportionate code.** If the problem is small, the solution is small. No unnecessary abstraction, premature generalization, "clever" shortcuts or dense one-liners.
- Readability comes before cleverness. A student should be able to read the code and understand it.
- Short functions, clear names. Code identifiers, code comments and documents are in English. User-facing UI text is in Turkish.
- Comments only for "why". Do not write comments that repeat what the code does.
- Before adding a new library, check whether the standard or existing solution is enough. If it is, do not add it.
- Do not rewrite a file from scratch, edit the relevant place. Do not do refactors nobody asked for.

## 4. Efficiency (token saving)

- Do not read files again and again without need. Read the part you need.
- Do not produce long explanations or output. Summarize briefly and clearly.
- Do not repeat yourself or retell a step that is already done.

## 5. Security and privacy rules (not negotiable)

- Student code runs **only** in an iframe with `sandbox="allow-scripts"`. Do not add `allow-same-origin`. Do not run student code on the server.
- The checker and writing checks **do not run** student code, they only parse it (static analysis). If analysis runs on the server, set size and time limits.
- **No LLM/AI service is called in the MVP.** Student code or data is not sent to any external service.
- Side panel Markdown is rendered safely. Do not allow raw HTML.
- The session is token-based; do not use cookies (iframe/Teams compatibility).
- Replay is **event-based** (editor changes). Do not add keystroke logging.
- Replay recording does not start until the student confirms the first-login notice.
- Typing history, check results and reports are visible only to the student concerned and the course instructor. Apply this authorization check on every relevant endpoint.
- Secrets, keys and real student data never enter the repo. Example data is fake.
- Identity operations go through the `IdentityProvider` interface. Do not write code that depends directly on the demo user.

## 6. Evaluation rules (behavior and wording)

- **The system does not give the final grade.** Score fields are labeled "Suggested score". Only the instructor enters the final score and feedback.
- **UI wording is non-judgmental:** "used / not used" (Turkish UI: "kullanılmış / kullanılmamış") and "warning". Do not write judging words such as "correct", "wrong", "cheated", "suspicious". Signals are shown only as counts and observations.
- The checker checks only the rules the instructor defined. If the checker is off, produce and show no result.
- Check rules are defined with selection fields (tag, attribute, count, non-empty, container). Do not make the instructor write CSS selectors.
- An automatic criterion either passes or fails; do not add partial credit.
- Check results and criteria are shown to the student only if the assignment setting allows it (default off).
- Present the choice of linter tools (S6) to the user with the feasibility result, and do not add them without approval. Error messages come from the Turkish table; a message not in the table is shown raw.

## 7. Testing

- Write tests for new behavior (see `docs/test-strategy.md`). Do not say "done" until the items in the sprint's DoD (`docs/roadmap.md`) pass.
- For the checker and linter, write example solution sets: complete, incomplete and empty-tag solutions.
- Run the tests and report the result. If you could not run them, say so clearly; do not assume they passed.
- If a test fails, explain why; do not make it pass by deleting or loosening the test.

## 8. Folder structure (confirmed in S0)

```
web361lab/
  AGENTS.md
  CLAUDE.md
  docs/         Project documents (start with docs/README.md)
  frontend/     React + TypeScript + Vite
  backend/      FastAPI
```

Frontend module names (such as editor, preview, replay, checker, lint, rubric) are settled together with the user in S0.

## 9. Git

- Small, meaningful commits. Messages are short and clear, in English.
- Do not push without the user asking, and do not rewrite history (rebase, force push).

## 10. Stop and ask

Stop the work and ask the user if any of these happens:
- Something is needed that does not match the documents.
- A new big dependency or a tech stack change is needed.
- A solution seems to need a compromise on the security/privacy rules (section 5) or the evaluation rules (section 6).
- An action that is hard to undo (deleting, data migration, rewriting history).
- The sprint's DoD cannot be met.
