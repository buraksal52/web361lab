# Test Strategy

- **Unit tests:** Applying replay events (the same events produce the same code), signal counters, role/enrollment checks, settings (IntelliSense/paste/live diagnostics) being carried correctly from assignment to editor, **check rule → result** mapping, **suggested score calculation**, CSV output.
- **Checker test set:** For each example assignment at least three example solutions: a complete solution (everything must pass), an incomplete solution (the expected criteria must fail), and an empty-tag solution (the "must not be empty" rule must catch it).
- **Linter test set:** Known faulty code examples → expected warnings. Clean code → no warnings. Mapping tests for the Turkish message table.
- **API tests:** Creating an assignment, saving a draft, submitting and locking, saving the rubric, rejecting unauthorized access.
- **End to end (few, core flow):** The instructor creates an assignment → the student writes and submits → the instructor sees the check result and replay, grades, and gets the CSV.
- **Manual checklist (at the end of every sprint):** With paste off, do pasting from outside and drag-and-drop not work? Does copy-paste inside the editor work? Can the preview not reach any outside page? Does the replay play correctly from start to end? With the checker off, is no result shown? With "show to student" off, does the student not see results?
- **Short usability trial with the instructor:** The instructor creates an assignment, turns on the checker and grades one submission. Where they get stuck is noted.
- **In Phase 3:** For the interpreter, an example PHP + expected output set per topic.
