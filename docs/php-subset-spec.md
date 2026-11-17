# PHP Subset Specification (draft, Phase 3)

> This document is not detailed until Phase 3. It is both a rule for the agent and the "this is what it supports" list for the instructor. When the interpreter meets syntax outside the scope, it reports a clear error instead of silently running wrongly.

## To be supported (based on the course curriculum, weeks 5-7)

- `<?php ... ?>` mixed with HTML, `echo`, `print`
- Variables (`$x`), basic types: string, int, float, bool, array, null
- Operators: arithmetic, comparison, logical, string concatenation (`.`), assignment
- Variable interpolation inside double quotes (`"Hello $name"`)
- `if / elseif / else`, `switch`, `for`, `while`, `foreach`
- Function definition and calls
- Arrays (indexed and associative)
- A small number of built-in functions: `count`, `strlen`, `strtoupper`, `strtolower`, `str_replace`, `in_array`, `array_push`, `implode`, `explode`
- Simulated `$_GET` / `$_POST` (from scenarios defined by the instructor)

## Not supported at first

Classes/objects, `include/require`, file operations, sessions/cookies, database functions, type juggling (such as `"5" + 3`) and advanced built-in functions. These are added later according to course needs.

## Architecture

Tokenizer, Parser (AST), Evaluator. The evaluator is written so it can be paused and observed, in order to show step-by-step execution and a variable table.
