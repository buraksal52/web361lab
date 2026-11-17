# Vision and Scope

## Goal

Bring web course assignments into one environment that makes the learning process visible and that the instructor controls. Reduce the instructor's burden of reading every submission one by one, but leave the decision with the instructor. The grade is determined not only by the output but also by the student's thinking process.

## Stakeholders

| Stakeholder | Role |
|---|---|
| Instructor | Creates assignments, sets settings and criteria, reviews submissions, replay and reports, gives the grade |
| Student | Reads the assignment, writes code, submits |
| School IT department (after approval) | Teams app, SSO, data permissions and KVKK |
| Developer (owner + coding agent) | Protects the scope, approves at the end of each sprint |

## Scope lists

| List | Content |
|---|---|
| **In MVP** | Instructor creates assignments (title, assignment text in natural language, side panel content, starter code, due date). Assignment settings: IntelliSense, paste, live error display. Student editor + live preview (HTML/CSS/JS). Automatic draft saving. Typing history (replay) recording. Submission. Instructor submission list, code view, replay player, signals. **Checker (optional):** required elements (tag, attribute, count, non-empty, container). **Writing checks:** linter report, rules chosen by the instructor, Turkish messages. **Rubric:** automatic and manual criteria, suggested score, instructor's score and feedback, CSV export. Setting to show results/criteria to students. Role model (instructor/student). Demo login mode (seed users + CSV list). First-login notice |
| **Not in MVP (after approval)** | Teams tab app. School-account SSO (Microsoft Entra ID). Course list from Teams membership. Transferring grades to Teams. IT/KVKK approval. Notifications |
| **Later phases** | Phase 2: LLM comment layer (instructor-facing), checker extensions (CSS properties, JS tree checks). Phase 3: PHP subset interpreter, block assignments (shared AST). Phase 4: SQL assignments (`sql.js`), PHP + database, mock endpoint for AJAX |
| **Out of scope** | Running code on the server. Any access for people not enrolled in the course. Own account/password system. The system giving the final grade by itself. Claiming 100% prevention of AI use (impossible; the goal is to make it harder and noticeable). Claiming to prove that code "works correctly" (the MVP only checks usage and writing) |
