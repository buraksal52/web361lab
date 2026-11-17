# Backlog

Work items per sprint, traced to requirements (`FR-`/`NFR-`) and decisions (`ADR-`). Sprint order is the priority order. Every item starts as `todo`. The agent only works on items of the current sprint, and only after the owner approves the sprint (see `AGENTS.md`).

Status values: `todo`, `in progress`, `done`, `blocked`.

## S0: Setup

| ID | Item | Refs | Status |
|---|---|---|---|
| S0-01 | Create the repository structure (`frontend/`, `backend/`, `docs/`) and put the project documents in place | ADR-10 | done |
| S0-02 | Confirm the tech stack with the owner | ADR-10, A6 | done |
| S0-03 | Frontend skeleton (React + TypeScript + Vite) starts | ADR-10 | done |
| S0-04 | Backend skeleton (FastAPI) with a "hello" endpoint | ADR-10 | done |
| S0-05 | Test runners for both sides, one passing sample test each | NFR-05 | done |
| S0-06 | Confirm folder and module names with the owner (top-level folders confirmed; feature modules to be agreed in their respective sprints) | `AGENTS.md` | in progress |

## S1: Editor + preview

| ID | Item | Refs | Status |
|---|---|---|---|
| S1-01 | Decide the editor file model with the owner: separate HTML/CSS/JS tabs, enabled per assignment | Q8, ADR-16 | done |
| S1-02 | Monaco editor component with configurable language tabs | FR-04, FR-27, ADR-01, ADR-16 | in progress |
| S1-03 | Live preview in a sandboxed iframe (`srcdoc`, no `allow-same-origin`); browser isolation verification pending | FR-04, NFR-01, ADR-02 | in progress |
| S1-04 | IntelliSense on/off setting wired to the editor; browser behavior verification pending | FR-02 | in progress |
| S1-05 | Tests: setting really turns suggestions off; manual check that the preview is isolated | FR-02, NFR-01 | in progress |

## S2: Assignment, side panel, roles

| ID | Item | Refs | Status |
|---|---|---|---|
| S2-01 | Data model and migrations: User, Course, Enrollment, Assignment | FR-01, FR-13 | todo |
| S2-02 | `IdentityProvider` interface and demo implementation (seed users, role selection) | FR-14, NFR-06, ADR-07 | todo |
| S2-03 | Token-based session | NFR-03, ADR-06 | todo |
| S2-04 | Role and enrollment authorization checks | FR-13, UC-06 | todo |
| S2-05 | Instructor: create/edit assignment (title, Markdown text, side panel content, starter code, due date) | FR-01, UC-01 | todo |
| S2-06 | Assignment settings: IntelliSense, paste, enabled HTML/CSS/JS tabs | FR-02, FR-03, FR-27 | todo |
| S2-07 | Student assignment page: editor + preview + side panel with safe Markdown | FR-04, FR-05, UC-02 | todo |
| S2-08 | Paste blocking: outside paste and drag-and-drop text blocked, internal copy-paste allowed, short notice | FR-03, UC-03, ADR-03 | todo |
| S2-09 | Tests for the above, including rejection of unauthorized access | FR-13, FR-03 | todo |

## S3: Draft + replay recording

| ID | Item | Refs | Status |
|---|---|---|---|
| S3-01 | First-login notice and consent screen (recording must not start before consent) | FR-12, NFR-02 | todo |
| S3-02 | Automatic draft saving and restoring | FR-06 | todo |
| S3-03 | Replay event recorder (`edit`, `paste_blocked`, `blur`, `focus`), batched sending | FR-07, NFR-04, ADR-04 | todo |
| S3-04 | Replay event storage API | FR-07 | todo |
| S3-05 | Signal counters (blocked pastes, blur count, largest insertion) | FR-11 | todo |
| S3-06 | Tests: events rebuild the same code; no recording without consent; draft survives a refresh | FR-06, FR-07, FR-12 | todo |

## S4: Submission + instructor screen

| ID | Item | Refs | Status |
|---|---|---|---|
| S4-01 | Submit with a confirmation box and lock the submission | FR-08, UC-04 | todo |
| S4-02 | Instructor submission list | FR-09, UC-05 | todo |
| S4-03 | Submission view: final code and preview | FR-09 | todo |
| S4-04 | Replay player (play/pause, speed, seek) | FR-10 | todo |
| S4-05 | Signals display as counts and observations, with no judging words | FR-11, NFR-08, ADR-05 | todo |
| S4-06 | End-to-end test of UC-01 → UC-06 and the manual checklist. **Core demo ready** | FR-01 to FR-14 | todo |

## S5: Checker

| ID | Item | Refs | Status |
|---|---|---|---|
| S5-01 | Assignment form: "Enable checker" toggle and required-element fields (tag, attribute, minimum count, must not be empty, inside element, label linked to input) | FR-15, ADR-11 | todo |
| S5-02 | Static checker with `DOMParser`: pass/fail and the count found | FR-15, ADR-12 | todo |
| S5-03 | Run the checker at submission and store the result | FR-15, UC-04 | todo |
| S5-04 | Instructor submission view: "used / not used" per rule | FR-16, NFR-08 | todo |
| S5-05 | Per-assignment setting to show results to the student (default off) | FR-16 | todo |
| S5-06 | Example solution set (complete, incomplete, empty-tag) and tests | FR-15, R12 | todo |

## S6: Writing checks

| ID | Item | Refs | Status |
|---|---|---|---|
| S6-01 | Feasibility check of the linter tools in the browser; present the result to the owner for approval | FR-17, ADR-13, R13 | todo |
| S6-02 | Run the linter at submission and store the report | FR-17 | todo |
| S6-03 | Instructor rule selection per assignment | FR-17 | todo |
| S6-04 | Turkish message table (first 20 common errors), raw message for the rest | FR-17, R14 | todo |
| S6-05 | Instructor view of the lint report | FR-17, UC-05 | todo |
| S6-06 | Live diagnostics setting, independent of IntelliSense | FR-18 | todo |
| S6-07 | Faulty and clean code example set and tests | FR-17 | todo |

## S7: Rubric

| ID | Item | Refs | Status |
|---|---|---|---|
| S7-01 | Criteria model and UI: automatic criteria from checker rules, manual criteria added by the instructor, maximum points | FR-19, ADR-14 | todo |
| S7-02 | Suggested score calculation | FR-19, NFR-09 | todo |
| S7-03 | Instructor evaluation panel: change automatic results, score manual criteria, enter final score and feedback | FR-19, UC-07 | todo |
| S7-04 | CSV export of grades | FR-20 | todo |
| S7-05 | Show criteria to students (instructor's choice) | FR-21, UC-08 | todo |
| S7-06 | Tests for score calculation and CSV | FR-19, FR-20 | todo |

## S8: Polish + demo

| ID | Item | Refs | Status |
|---|---|---|---|
| S8-01 | Student list upload from CSV for demo login | FR-14 | todo |
| S8-02 | Error messages and empty states | NFR-07 | todo |
| S8-03 | Accessibility pass (keyboard use, contrast) | NFR-07 | todo |
| S8-04 | Demo data and demo scenario | R10 | todo |
| S8-05 | Copy an assignment with its settings and criteria (Could) | FR-23, R16 | todo |
| S8-06 | Final manual checklist. **Full MVP demo ready** | [test-strategy.md](test-strategy.md) | todo |

## Icebox (not scheduled; see [roadmap.md](roadmap.md))

| Phase | Items |
|---|---|
| Phase 1 | Meeting with the instructor and IT, KVKK text; Teams tab app; Entra SSO behind `IdentityProvider`; course list from Teams membership; grade transfer to Teams; pilot |
| Phase 2 | LLM comment layer behind a comment provider interface (FR-26, ADR-15); checker extensions for CSS properties and JS loop/condition/function checks |
| Phase 3 | PHP subset interpreter; block assignments over the shared AST (ADR-08) |
| Phase 4 | SQL assignments with `sql.js` (ADR-09); PHP + database; mock endpoint for AJAX |
| Could (unscheduled) | "Explain your code" step (FR-22) |
| Won't | Per-student parameter variation (FR-24); the system giving the final grade (FR-25) |
