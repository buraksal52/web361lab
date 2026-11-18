# S6 Linter Feasibility

Date: 18 November 2026. Tests used fictional snippets and temporary packages outside the repository. No linter was added to the project.

| Candidate | Tested version | Result |
|---|---:|---|
| HTMLHint | 1.9.2 | Bundled for a browser and ran locally in Chrome. The sample detected missing doctype, missing `alt` and duplicate `id`. `tag-no-obsolete` flagged `center` and `font` but not `i` or `b`; those need another rule or a small custom extension. HTML comments can disable rules, so instructor-controlled rules need protection against inline directives. |
| CSSTree | 3.2.1 | Bundled and ran locally in Chrome; detected an unknown property and an invalid value. Its parser recovers from some errors, so syntax errors must be collected with `onParseError`. |
| ESLint | 10.15.0 | A direct browser bundle failed on Node built-ins; this does not establish that every browser integration is impossible. A local Node test reported `no-undef`, `no-unused-vars` and `eqeqeq`. Inline configuration can be disabled. |
| Stylelint | 17.16.0 | A direct browser bundle failed on Node built-ins. A local Node test reported an unknown property and an invalid property value. |
| Prettier | 3.10.1 | The standalone browser build and HTML plugin bundled and ran; `check` identified formatting differences. It compares overall formatting, not indentation alone. |

Bundle sizes from the local unminified smoke test were approximately 100 KiB (HTMLHint), 376 KiB (CSSTree), and 321 KiB (Prettier with the HTML plugin); these are not production bundle measurements.

## Decision needed

Recommend HTMLHint, CSSTree, ESLint and optionally Prettier, subject to owner approval. The exact handling of HTML inline directives and `i`/`b` must be verified before implementation is considered complete. ESLint and Stylelint require a different integration from a straightforward browser bundle; a bounded local Node subprocess is an option permitted by ADR-13, but its deployment/runtime consequences need approval. No source code should be executed and no student data sent to external services.

Sources: [HTMLHint rules](https://www.htmlhint.com/rules/), [HTMLHint inline configuration](https://htmlhint.com/configuration/), [CSSTree](https://github.com/csstree/csstree), [ESLint Node API](https://eslint.org/docs/latest/integrate/nodejs-api), [Prettier browser documentation](https://prettier.io/docs/browser/).
