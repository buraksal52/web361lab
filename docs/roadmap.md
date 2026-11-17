# Roadmap

Sprint length is set by the course tempo (suggestion: about 1 week). **At the start and end of every sprint the agent asks for the owner's approval.** Work items for each sprint are in [backlog.md](backlog.md).

## Phase 0: MVP

| Sprint | Output | Definition of done (DoD) |
|---|---|---|
| **S0: Setup** | Repo, folder structure, tech stack confirmation, skeleton app, `AGENTS.md`/`CLAUDE.md` in place | Frontend and backend start, a "hello" endpoint works, the tech stack is confirmed |
| **S1: Editor + preview** | Monaco editor with configurable HTML/CSS/JS tabs, live preview (sandboxed iframe), IntelliSense on/off | When the setting changes IntelliSense really turns off, the preview is sandboxed, basic tests pass |
| **S2: Assignment, side panel, roles** | Instructor creates/edits assignments (natural-language text) and selects enabled editor tabs, student assignment page (editor + Markdown side panel), paste on/off, role model and demo login (seed users, role selection) | The instructor can create an assignment and see it on the student screen, paste blocking works, unauthorized access is rejected |
| **S3: Draft + replay recording** | First-login notice and consent (before recording), automatic draft, replay event recording, signal counters | Recording does not start without consent, the code comes back after a page refresh, events are recorded, signals are counted |
| **S4: Submission + instructor screen** | Submit and lock, instructor submission list, code view, replay player, signal display | The core flow (UC-01 → UC-06) works from start to end. **Core demo ready** |
| **S5: Checker** | "Enable checker" and required-element fields in assignment creation, static check, result on the instructor's submission screen, show-to-student setting | For the example form assignment, the rules give the expected result on three example solutions (complete, incomplete, empty-tag); with the setting off the student does not see results |
| **S6: Writing checks** | Tool feasibility check (put to the owner for approval), linter report, instructor rule selection, Turkish message table (first 20), live diagnostics setting | Example faulty code gives the expected warnings, the report is on the instructor's screen, the live diagnostics setting works |
| **S7: Rubric** | Criteria definition (automatic + manual), suggested score, instructor score and feedback, CSV export, show criteria to students | Score calculation tests pass, the instructor can grade one submission from start to end and get a CSV |
| **S8: Polish + demo** | Student list upload from CSV, error messages, accessibility, demo data and scenario, copy assignment (Could) | A full demo that can be shown to the instructor is ready, the manual checklist is clean |

**Decision points:**
- **A (end of S4):** Core demo. If wanted, early feedback is taken from the instructor.
- **B (end of S8):** Full MVP presentation and demo. If approved, Phase 1.

**Cut order if time runs short (cut first at the top):** FR-23 (copy assignment), FR-21 (show criteria to students), FR-18 (live diagnostics), FR-17 (writing checks, i.e. most of S6), FR-20 (CSV). FR-15/16 (checker) and FR-19 (rubric) are cut last, because they are the core that lowers the instructor's reading burden.

## Phase 1: Approval and Teams integration

1. Meeting with the instructor and the IT department, KVKK/disclosure text.
2. Teams tab app (Teams JS SDK) and iframe compatibility verification.
3. Entra ID SSO, plugged in behind `IdentityProvider`.
4. Course list from Teams team membership (Microsoft Graph, admin consent may be needed). CSV fallback if not possible.
5. Transfer of grades to Teams (if permissions allow).
6. Pilot: one instructor, one section.

## Phase 2: Comment layer + checker extensions

- LLM comment layer (ADR-15): comment provider interface; instructor-triggered, criteria-limited, instructor-only comments. The provider (cloud model or local small model) is chosen according to the KVKK decision, and cost is calculated with current prices at that time.
- Checker extensions: CSS property checks (such as `display: flex`), converting JS code to a tree to check loops, conditions and function definitions.

## Phase 3: Interpreter + blocks

Detailing the PHP subset specification ([php-subset-spec.md](php-subset-spec.md)), tokenizer, parser, evaluator, step-by-step tracing. Then block assignments over the shared AST (a ready-made Blockly-like library, not written from scratch).

## Phase 4: SQL and beyond

SQL assignments with `sql.js` and automatic checking (query result comparison). Later PHP + database, JS/DOM tests, a mock endpoint for AJAX.

> The order of Phase 2 and Phase 3 can be changed according to course needs (see Q7 in [assumptions-and-open-questions.md](assumptions-and-open-questions.md)).
