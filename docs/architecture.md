# Architecture

## 1. Overview

```
Browser (Teams tab or direct)
┌──────────────────────────────────────────────────┐
│ Frontend (React + TypeScript + Vite)             │
│  ├─ Editor (Monaco) ── settings: IntelliSense,   │
│  │                     paste, live diagnostics   │
│  ├─ Preview (sandboxed iframe, srcdoc)           │
│  ├─ Side panel (Markdown)                        │
│  ├─ Replay recorder / player                     │
│  ├─ Writing checks (static analysis)            │
│  ├─ Instructor screens: assignment creation,     │
│  │   rubric, reports                             │
│  └─ Identity interface (IdentityProvider)        │
└───────────────┬──────────────────────────────────┘
                │ HTTPS + token (Bearer)
┌───────────────▼──────────────────────────────────┐
│ Backend (FastAPI)                                │
│  ├─ Auth: IdentityProvider (MVP: demo mode)      │
│  ├─ Assignment / submission / draft / rubric API │
│  ├─ Replay event intake and queries              │
│  ├─ Checker (bounded static HTML analysis)       │
│  ├─ CSV export                                   │
│  └─ Database (PostgreSQL)                         │
└──────────────────────────────────────────────────┘
```

Code is never executed on the server. HTML/CSS/JS runs in the sandboxed iframe in the browser. The checker and linter do **not run** code, they only parse it. The server stores assignment, draft, submission, replay and evaluation data.

## 2. Components

| Component | Responsibility |
|---|---|
| Editor | Monaco with separate HTML, CSS and JavaScript tabs, enabled per assignment. IntelliSense and live diagnostics are turned off per setting; pasting from outside and drag-and-drop text are blocked |
| Preview | `<iframe sandbox="allow-scripts" srcdoc=...>`. `allow-same-origin` is never granted |
| Side panel | Renders Markdown. Raw HTML is not allowed (safe rendering) |
| Replay recorder | Collects editor changes with timestamps, batches and sends them |
| Replay player | Rebuilds the code by applying events from the start; offers speed and seeking |
| Signal collector | Blocked pastes, tab loss, largest single insertion |
| Checker | Parses submitted HTML on the server without executing it, with size and time limits; counts elements against the instructor's rules |
| Writing checker | Scans HTML/CSS/JS with linter tools, produces a report and Turkish messages |
| Rubric service | Criteria, automatic results, suggested score, instructor score, feedback, CSV |
| IdentityProvider | `getCurrentUser()` and `isEnrolled(course)` interface. Demo in the MVP, Entra later |
| Assignment/submission service | CRUD, locking, lists |

## 3. Data model (summary)

| Entity | Key fields |
|---|---|
| User | id, name, email, role (teacher/student) |
| Course | id, name |
| Enrollment | user_id, course_id, role |
| Assignment | id, course_id, title, description_md, side_panel_md, starter_code, intellisense_enabled, paste_enabled, diagnostics_enabled, checker_enabled, check_rules (JSON), lint_rules (JSON), show_results_to_student, show_criteria_to_student, due_at |
| Draft | id, assignment_id, student_id, code, updated_at |
| Submission | id, assignment_id, student_id, final_code, submitted_at, locked, check_result (JSON), lint_report (JSON) |
| ReplayEvent | id, draft_id, t_ms, kind, payload |
| SignalSummary | draft_id, paste_blocked_count, blur_count, max_insert_chars |
| Criterion | id, assignment_id, kind (auto/manual), label, max_points, check_rule_ref |
| Evaluation | submission_id, suggested_points, final_points, feedback, graded_at |
| CriterionResult | submission_id, criterion_id, auto_result (pass/fail/null), teacher_override, points |

To make later mapping to Teams easier, entities are kept close to Teams' class/assignment/submission/grade logic.

## 4. Replay event format (kept simple)

Each event has: time (ms, relative to the session), kind (`edit`, `paste_blocked`, `blur`, `focus`, `submit`) and data. An `edit` event carries Monaco's change information (range + inserted text). The player starts from the starter code and applies events in order.

Starter code, drafts and submissions contain separate code for each language. Edit events identify the language they modify; preview and analysis use the enabled tabs.

For editor changes, `payload` contains `language` and `changes`, each with Monaco's UTF-16 `rangeOffset`, `rangeLength`, and inserted `text`. Drafts keep their original starter code so replay remains stable if the assignment is edited. Draft code and event batches are saved atomically; a batch ID makes retries idempotent. The server requires student consent and course enrollment before creating or recording a draft. The student and the course instructor may read replay data.

Submission first waits for pending draft batches, then locks the current draft and stores its final code with a `submit` replay event. The server rejects subsequent new edits while locked. An enrolled course instructor can reopen the submission; a later submission replaces the saved final-code snapshot.

## 5. Checker and rubric

Check rules are defined with fields (the instructor never writes selectors) and stored in this form:

```
{ tag: "input", attrs: { type: "email" }, min_count: 1, non_empty: false, inside: "form" }
```

- The checker parses the submitted HTML and counts the elements that satisfy the rule. Result: pass/fail and the count found.
- An automatic criterion either passes or fails (no partial credit, to keep it simple).
- **Suggested score** = sum of the maximum points of passed automatic criteria + the manual points the instructor enters. The instructor can change any criterion. The **final score** is what the instructor saves.
- A check means "used", not "works correctly". The UI and the pitch to the instructor are written accordingly.
- The "must not be empty" option greatly reduces tricking the checker with empty tags (`<h1></h1>`).
- When the checker is off, no check result is produced or shown.
- Checker rules are omitted from student responses when visibility is disabled; results are disclosed only to the course instructor or the submitting student when the assignment permits it. Results contain a snapshot of the rules used at submission.
- The standard-library HTML parser runs in a separate process, with a 256 KiB HTML limit and a five-second deadline. It does not execute code. Its handling of malformed HTML is simpler than a browser's HTML parser.

## 6. Writing checks (linter)

The rule set consists of groups the instructor can turn on or off per assignment. Rules are shown as "warning"; only syntax errors count as "error".

| Area | MVP rules |
|---|---|
| HTML | Unclosed or wrongly nested tags, duplicate `id`, `alt` on `img`, `doctype`, warning for presentational tags (`<i>`, `<b>`, `<center>`, `<font>`) |
| CSS | Syntax errors, unknown property, invalid value |
| JS | Syntax errors, `===` instead of `==`, unused variable, undefined variable |
| Format | Consistent indentation |

- Selected in S6: HTMLHint, CSSTree, ESLint and Prettier. At submission, a local Node subprocess performs static analysis with a 256 KiB total input limit and an eight-second deadline; it never executes student code or sends it externally. The report is visible only to the course instructor. Inline directives cannot change the instructor's chosen rules. HTML, CSS and JavaScript tabs are checked; embedded style and script blocks are checked as HTML locations.
- Monaco's built-in live diagnostics are independently configured per assignment and are not the submission linter. Formatting checks use Prettier for HTML/CSS indentation where lines can be compared and ESLint for JavaScript indentation; they are observations rather than automatic code changes.
- Messages: the 20-30 most common errors get a plain Turkish explanation. A message not in the table is shown raw.
- `<em>` / `<i>` example: the linter flags `<i>` usage. Deciding "is emphasis meant here, or is it only italics" is not rule-based; it belongs to the instructor (and to the comment layer in Phase 2).
