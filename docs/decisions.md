# Architecture Decision Records

All decisions are draft v0.3 except where explicitly confirmed. ADR-08 and ADR-09 apply to later phases. When a decision changes, update this file first.

**ADR-01: Monaco Editor.**
*Decision:* Use Monaco as the editor. *Why:* IntelliSense, paste, live diagnostics and other behaviors can be controlled through settings and events; it is ready-made and widely used. *Consequence:* Large package size, acceptable.

**ADR-02: Run code in the browser.**
*Decision:* HTML/CSS/JS runs in a sandboxed iframe. *Why:* Running student code on the server is a security and cost risk. *Consequence:* The server only stores data.

**ADR-03: Paste blocking at editor level, supported by replay.**
*Decision:* Pasting from outside and drag-and-drop text are cancelled. Text copied inside the editor is allowed (the app tracks its own internal clipboard). *Why:* An absolute block is impossible (a student can ask an AI on a phone and type the answer by hand). *Consequence:* The goal is to make it harder and noticeable. It is presented to the instructor this way.

**ADR-04: Replay is event-based, not keystroke logging.**
*Decision:* Editor change events are recorded instead of keystrokes. *Why:* Less data, less privacy risk, easy to play back. *Consequence:* It shows how the code came to be; it does not record what else the student typed.

**ADR-05: The system does not judge and does not grade.**
*Decision:* Signals and check results never say "suspicious", "correct" or "wrong"; they show counts and observations. Scores are labeled "suggested". *Why:* False positives (a fast typist, a student who drafts elsewhere, a student with a different but valid solution) can lead to unfair outcomes. *Consequence:* The decision belongs to the instructor.

**ADR-06: Token-based session, iframe-compatible.**
*Decision:* Bearer token instead of cookies. *Why:* Third-party cookies can be a problem in a Teams tab iframe. *Consequence:* No rewrite needed later.

**ADR-07: Identity provider abstraction, demo mode in the MVP.**
*Decision:* One interface; demo behind it in the MVP, Entra SSO later. *Why:* SSO cannot be set up before approval, but switching later must be easy. *Consequence:* Only the provider changes at switch time.

**ADR-08 (later phase): Shared AST for blocks and code.**
*Decision:* Blocks and typed PHP are converted to the same tree structure, and a single interpreter runs them. *Why:* Avoid writing two separate systems and allow step-by-step tracing. *Consequence:* The interpreter is written in Phase 3.

**ADR-09 (later phase): `sql.js` for SQL.**
*Decision:* SQL assignments run in the browser with SQLite. *Why:* Ready-made, small, suited to automatic checking. *Consequence:* Small syntax differences from MySQL are clarified with the instructor. Done in Phase 4.

**ADR-10: Confirmed tech stack.**
*Decision:* Frontend React + TypeScript + Vite, backend FastAPI, database PostgreSQL. The owner confirmed the stack in S0. *Why:* The stack favors simplicity and fast development. *Consequence:* Do not change it without approval.

**ADR-11: Natural-language assignment, checker as an optional separate layer.**
*Decision:* The assignment text is free Markdown and the system does not interpret it. The checker is separate and optional, and checks the rules the instructor selected. *Why:* The instructor's habit of writing assignments is not disturbed, which helps adoption. Converting natural language into rules needs an LLM, which carries reliability and privacy risks. *Consequence:* The instructor picks rules from cards/fields and never writes selectors.

**ADR-12: Static analysis, usage check.**
*Decision:* The checker and linter parse code without running it. *Why:* Safe, fast, explainable and repeatable. *Consequence:* They only answer "is it used" and "is the writing fine", not "does it work correctly". This limit is stated clearly in the UI and in the pitch to the instructor.

**ADR-13: Writing checks with ready-made linters.**
*Decision:* Instead of writing our own rule engine, use ready-made tools and add a Turkish message table on top. *Why:* Ready-made, easy to maintain, widely used rules. *Consequence:* Whether the tools work in the browser is verified in S6; one that does not runs as static analysis on the server.

**ADR-14: Rubric and suggested score.**
*Decision:* Criteria are automatic or manual; the system calculates a suggested score and the instructor enters the final score. *Why:* It lowers the instructor's burden of reading submissions one by one while keeping control with them. *Consequence:* An automatic criterion either passes or fails. Grades are exported as CSV; direct transfer to Teams is a later phase.

**ADR-15: No LLM in the MVP, comment provider interface in Phase 2.**
*Decision:* No LLM/AI service is called in the MVP. In Phase 2 the LLM comment layer is added behind a single "comment provider" interface, like the identity provider. *Why:* Grading needs consistency and explainability. Sending student code to an external service requires the school's IT/KVKK approval. *Consequence:* The LLM only produces **comments**. It runs when the instructor presses a button, is limited to criteria the instructor selects (semantic tags, naming, indentation and so on), outputs short items with line numbers, and goes to the instructor only. Student name/number is not sent. Student code is treated as "data", so instructions inside it (prompt injection) are ignored. The provider (cloud or local small model) is chosen after the KVKK decision.

**ADR-16: Assignment-specific editor tabs.**
*Decision:* Use separate HTML, CSS and JavaScript tabs. The instructor selects which tabs are enabled for each assignment. *Consequence:* Code, starter content, replay changes and analysis must identify the corresponding language. The assignment settings are implemented in S2.

**ADR-17: Server-side static checker.**
*Decision:* Run the optional HTML checker on the server at submission, using a bounded static parser; never execute student code. Enforce input-size and execution-time limits. *Why:* Rules and results must remain hidden from students unless the instructor enables visibility; browser-side checking would disclose the rules to the student's browser. *Consequence:* The server stores results with their rule snapshot and applies authorization on every response. This replaces the S5 browser `DOMParser` choice.
