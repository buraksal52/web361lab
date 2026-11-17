# Requirements

## Functional requirements (MoSCoW)

"Must" is the core product flow (S0-S4). "Should" and "Could" items are built in the MVP sprints (S5-S8) and are postponed in the cut order given in [roadmap.md](roadmap.md) if time runs short.

| ID | Requirement | Priority |
|---|---|---|
| FR-01 | The instructor creates and edits an assignment (title, assignment text in natural language (Markdown), side panel content, starter code, due date) | Must |
| FR-02 | The instructor turns IntelliSense on or off per assignment | Must |
| FR-03 | The instructor turns pasting from outside on or off per assignment (copy-paste inside the editor stays allowed) | Must |
| FR-04 | The student writes HTML/CSS/JS in the editor and sees a live preview | Must |
| FR-05 | Lesson content is shown in the side panel next to the editor (Markdown) | Must |
| FR-06 | The draft is saved automatically; the student continues where they left off | Must |
| FR-07 | Typing history is recorded as timestamped events | Must |
| FR-08 | The student submits (after submission there are no changes unless the instructor allows) | Must |
| FR-09 | The instructor lists submissions and sees the final code | Must |
| FR-10 | The instructor plays the replay (speed control, seeking back and forth) | Must |
| FR-11 | The instructor sees signals: number of blocked pastes, number of tab/window losses, largest single insertion in characters | Should |
| FR-12 | On first login (before recording starts) the student is told that typing history is recorded, and consent is collected | Must |
| FR-13 | Role model: instructor and student. A user not enrolled in the course cannot access it | Must |
| FR-14 | Demo login: seed users + the instructor's CSV list, person/role selection on the login screen | Must |
| FR-15 | **Checker (optional):** the instructor turns it on per assignment and selects required elements from fields: tag, attribute (`type`, `name`, `required`, `placeholder`), minimum count, "must not be empty", "must be inside this element", "label linked to input". The instructor does not write selectors (CSS selectors) | Should |
| FR-16 | The check result appears on the instructor's submission screen as "used / not used". Showing it to the student is a per-assignment setting (default off) | Should |
| FR-17 | **Writing checks:** submitted code is scanned with a linter and the report is shown on the instructor's screen. The instructor chooses which rules are on per assignment. Messages are in Turkish and plain for the most common errors | Should |
| FR-18 | Live error display (underlined errors in the editor) can be turned on or off per assignment, independent of IntelliSense | Could |
| FR-19 | **Rubric:** the instructor defines criteria for an assignment. Automatic criteria come from checker rules, manual criteria are added by the instructor. Each criterion has a maximum score. The system calculates a **suggested score**. The instructor can change automatic results, scores manual criteria, and enters the final score and short feedback | Should |
| FR-20 | Grades entered by the instructor are exported as CSV | Should |
| FR-21 | Rubric criteria can be shown to the student on the assignment page (the instructor chooses) | Could |
| FR-22 | "Explain your code" step: a short question to the student at submission | Could |
| FR-23 | Copy an assignment (with its settings and criteria) | Could |
| FR-24 | Per-student parameter variation | Won't (MVP) |
| FR-25 | The system giving the final grade by itself | Won't (deliberate decision) |
| FR-26 | **LLM comment layer:** works on the instructor's request, produces comment suggestions for the instructor only (Phase 2) | Won't (MVP) |

## Non-functional requirements

| ID | Requirement |
|---|---|
| NFR-01 | **Security:** Student code runs only in a sandboxed iframe and shares no data with the main app. The checker and linter do not run code, they only parse it |
| NFR-02 | **Privacy:** Typing history and reports are visible only to the student concerned and the course instructor. The student knows recording takes place. In the MVP, student code is not sent to any external service |
| NFR-03 | **Iframe compatibility:** Cookie-less, token-based session so the app can run as a Teams tab |
| NFR-04 | **Performance:** No noticeable lag while typing. Replay recording does not slow typing (events are batched). Checker and linter run at submission, not while typing |
| NFR-05 | **Simplicity:** Code is written simply and proportionately (see `AGENTS.md`) |
| NFR-06 | **Portability:** The identity provider sits behind an abstract interface |
| NFR-07 | **Accessibility:** Usable with a keyboard, sufficient contrast |
| NFR-08 | **Explainability:** Every automatic result shows which rule it is based on. The UI uses non-judgmental words such as "used / not used" (Turkish UI: "kullanılmış / kullanılmamış") and "warning" |
| NFR-09 | **Instructor control:** Automatic results and the suggested score can be changed by the instructor. The final grade always belongs to the instructor |
