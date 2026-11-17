# Risk Register

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R1 | Scope creep (wanting to rewrite Teams from scratch, the checker turning into a system that "verifies everything") | High | High | The MVP scope list is binding. New requests are written to the later-phase list |
| R2 | Paste blocking is bypassed / AI is used | Certain | Medium | Position it as "making it harder and noticeable", not "prevention". Replay and signals |
| R3 | Replay signals produce false positives | Medium | High | Signals do not judge. The instructor gets an interpretation note |
| R4 | Student privacy / KVKK | Medium | High | First-login notice and consent. Event-based, not keystroke logging. Access only for the course instructor. No external service in the MVP. School approval is obtained in the after-approval phase |
| R5 | The instructor does not adopt it (harder than Teams) | Medium | High | Assignment text is free, the checker is optional. Assignment creation flow is kept short. Early trial with the instructor. Copy assignment (FR-23) |
| R6 | Teams/IT permissions cannot be obtained | Medium | Medium | Identity abstraction + CSV fallback. The platform also works without Teams |
| R7 | The agent goes out of scope or writes overly complex code | Medium | Medium | `AGENTS.md` rules, approval before every phase/sprint |
| R8 | Student code escapes the iframe | Low | High | `sandbox` attribute, no `allow-same-origin`, no data shared with the main page |
| R9 | The interpreter (Phase 3) runs incorrectly | Medium | Medium | Test set per topic. Clear error for unsupported syntax |
| R10 | Not enough time for the presentation | Medium | Medium | A core demo can be shown at the end of S4. Cut order is in [roadmap.md](roadmap.md) |
| R11 | A "used" result is read as "correct" | Medium | High | Non-judgmental UI wording (NFR-08). The limit is explained openly in the pitch to the instructor (ADR-12) |
| R12 | The checker is tricked with empty or fake tags | Medium | Medium | "Must not be empty" option. The instructor sees the code and replay anyway |
| R13 | Linter tools do not work in the browser or are too heavy | Medium | Medium | Feasibility check at the start of S6. Static analysis fallback on the server (limited in size/time) |
| R14 | Linter warnings give false positives and mislead the student | Medium | Medium | The instructor chooses rules. Warning/error distinction. Turkish explanation table |
| R15 | The suggested score is perceived as the instructor's grade | Low | High | "Suggested" label; the final score is a separate field and comes from the instructor (ADR-14) |
| R16 | Writing criteria is too much work for the instructor | Medium | Medium | Selection from ready fields, copying assignments/criteria, example templates |
| R17 | Privacy, prompt injection and inconsistent output in the LLM comment layer (Phase 2) | Medium | High | ADR-15: instructor-only, instructor-triggered, criteria-limited, no identity data sent, code treated as data, only after KVKK approval |
