---
name: route-subagents
description: Dynamically choose and spawn the best available Codex custom-agent model and reasoning profile. Use for every explicit agent, subagent, parallel-work, model, or effort request, and whenever delegation would materially improve speed, quality, context isolation, independent verification, or long-task reliability.
---

# Route Subagents

Honor an explicit profile exactly. If unavailable, stop.

## Simple routing examples

Match these before reading the catalog. Do not calculate fitness when an example fits.

- One command, syntax answer, tiny obvious fix, or narrow lookup -> `spark_medium`.
- Purely mechanical extraction, classification, formatting, or identical repetition with no judgment -> `luna_low`.
- Clear repeatable transformation or structured summary requiring a few checks -> `luna_medium`.
- A simple ten-page description, summary, translation, or rewrite with clear instructions -> `luna_medium`. Length alone does not require Terra or Sol.
- A bounded deterministic task with important but familiar edge cases -> `luna_high`.
- An unusually hard but still bounded deterministic task -> `luna_xhigh`.
- A Luna-shaped task not positively classified as simple -> `luna_max`.
- Normal multi-file repository work, implementation, tests, review, or debugging with a settled objective -> `terra_high`.
- Subtle or high-risk execution with a settled design -> `terra_xhigh`.
- Complex implementation or investigation with settled architecture -> `terra_max`.
- Architecture, strategy, unresolved ambiguity, consequential judgment, or polished synthesis -> `sol_medium`.
- Difficult Sol-shaped work with multiple tradeoffs -> `sol_high`.
- Exceptional cross-system or high-risk Sol-shaped work -> `sol_xhigh`.
- Ultra-complex indivisible Sol work -> ask before `sol_max`. Use `sol_ultra` only when explicitly requested.

If no example fits, choose the family by the dominant need: clear/repeatable -> Luna; repository/tools -> Terra; ambiguity/judgment -> Sol. Then load `references/model-catalog.md` and use its route table. Use fitness math only for cross-family fallback or audit.

For every spawn:

- Apply Max/Ultra gates from the catalog.
- Set `task_name=<scope>_<model_code>_<effort_code>`; codes: models `sp/l/t/s`, efforts `l/m/h/xh/mx/u`.
- Spawn the minimum bounded lanes; avoid overlapping ownership and redundant retries.
- Keep synthesis, verification, acceptance, and escalation in the primary agent.
