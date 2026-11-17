# Assumptions and Open Questions

## Assumptions (change the ones that are wrong)

- **A1:** It is presented as a course project / pilot; broad classroom use is not targeted in the first version.
- **A2:** In the MVP the grade comes from the instructor. Automatic results are only usage and writing checks; there is no claim of "correctness".
- **A3:** The server stores assignment, draft, submission, replay and evaluation data. Code execution happens in the browser.
- **A4:** Being enrolled in the course = being a member of the Teams team (to be confirmed with the instructor).
- **A5:** Login with the school account is possible (Entra). IT approval is obtained in the after-approval phase.
- **A6:** The owner confirmed React, TypeScript, Vite, FastAPI, and PostgreSQL in S0.
- **A7:** Grades are given as points (to be confirmed with Q6). The score field was designed accordingly.
- **A8:** Whether the linter tools work in the browser is verified at the start of S6.
- **A9:** Documents, code identifiers and code comments are in English. User-facing UI text is in Turkish.

## Open questions

- **Q1:** How sensitive is the instructor about AI use? The emphasis of the presentation is adjusted accordingly.
- **Q2:** How is PHP run in the course today (XAMPP etc.)? Important for Phase 3.
- **Q3:** Is MySQL used for SQL? The difference from `sql.js` (SQLite) is raised with the instructor.
- **Q4:** Can the instructor connect with the IT department for the Teams integration?
- **Q5:** How long should replay records be kept after the course?
- **Q6:** Are assignments graded in the course with points, or as pass/fail?
- **Q7:** In Phase 2, first the LLM comment layer, or the PHP interpreter and blocks?
- **Q8:** Editor file model: does the student write a single HTML file (with inline CSS/JS), or three tabs (HTML, CSS, JS)? This affects the checker, the replay events and the linter. To be decided in S1.
