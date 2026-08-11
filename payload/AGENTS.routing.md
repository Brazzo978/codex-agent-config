# Dynamic subagent routing

Use the `route-subagents` skill for every explicit agent/model/effort request and whenever delegation materially improves speed, quality, context isolation, independent verification, or long-task reliability.

Canonical capability hierarchy: `Sol > Terra > Luna > Spark`. Expected speed and cost efficiency generally run in the inverse order: `Spark > Luna > Terra > Sol`. Choose the lowest family in that hierarchy whose capability and task fit are sufficient, then use the lowest sufficient effort:

- Sol: ambiguous, open-ended, high-value work requiring architecture, difficult judgment, cross-system reasoning, polish, or critical independent review.
- Terra: default everyday lane for repository exploration, implementation, tests, debugging, review, and evidence gathering when the objective is mostly settled.
- Luna: clear, repeatable, high-volume work with explicit inputs, output format, and acceptance criteria.
- `spark_medium`: preferred for eligible near-instant microtasks with little context—one-line commands, syntax lookup, tiny obvious fixes, or short code explanations—because Spark uses a separate allowance from GPT-5.6.

Use `low` for direct low-risk work, `medium` as the balanced default, `high` for multi-step work with meaningful edge cases, and `xhigh` for subtle broad-context or higher-risk reasoning. Use `max` for one exceptionally hard indivisible problem. Use `ultra` only for genuinely independent subproblems that benefit from parallel agents; Ultra is not simply a stronger Max.

Treat usage as finite. Every subagent consumes its own model and tool work, and higher reasoning, larger context, retries, and parallel lanes use the allowance faster. Prefer `medium`, require concrete reasons for `high` or `xhigh`, and never auto-spawn `max` or `ultra` unless the user explicitly requested it. If Max or Ultra appears necessary, explain why and obtain confirmation first. For Ultra, use only the minimum useful independent lanes—normally two or three—and never create redundant agents merely to collect extra opinions.

Compare cost and capability across families, not effort labels alone. Higher effort improves a selected family but does not promote it into the family above. A higher-effort Luna may be good value only when the task is already Luna-shaped; it cannot replace Terra when Terra-level breadth or tool execution is required. Terra cannot replace Sol when ambiguity and judgment are the core problem. Exclude profiles below the required family tier before optimizing cost.

Use the dated Artificial Analysis Intelligence Index versus cost snapshot in the `route-subagents` catalog only as a secondary efficiency signal after the capability hierarchy and task-fit gate. Cross-effort overlap in that benchmark does not reverse the family order or justify down-tiering. Benchmark API cost does not override the Max/Ultra allowance gate.

Prefer Spark whenever it is exposed and the task is genuinely self-contained and tiny, including suitable microtasks inside a larger workflow. Do not fragment work merely to use Spark, and do not retry unsuitable work there. If Spark was selected implicitly but is unavailable or its separate limit is exhausted, choose the next suitable GPT-5.6 profile and disclose the fallback; if Spark was explicitly requested, stop instead.

Honor an explicitly named profile exactly. If it is not exposed by the runtime, report that and stop; never silently substitute. Keep delegated assignments bounded, avoid overlapping file ownership, preserve concurrent edits, verify material claims in the primary session, and summarize evidence rather than raw subagent output.
