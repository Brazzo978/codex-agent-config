# Model and effort catalog

Runtime exposure and account/workspace availability always take precedence over this installed catalog. Start a new Codex task after changing custom-agent files.

## Selection order

1. Honor an explicit user-selected profile exactly.
2. Otherwise choose the least capable profile that is still sufficient.
3. Increase effort before changing model when the model family remains suitable.
4. Change family when the task shape requires a different context, reasoning, quality, or latency tradeoff.
5. Never silently fall back when a route is unavailable.

## Models

| Model family | Installed profiles | Route when |
|---|---|---|
| GPT-5.3 Codex Spark | `spark_medium` | Near-instant small coding answers, narrow lookups, tiny edits, mechanical tasks, little context. Research-preview availability may be restricted. |
| GPT-5.6 Luna | `luna_low`, `luna_medium`, `luna_high`, `luna_xhigh`, `luna_max`, `luna_ultra` | Clear, repeatable, high-volume extraction, classification, transformation, structured summaries, or tightly specified edits. Higher efforts are conditional on runtime support. |
| GPT-5.6 Terra | `terra_low`, `terra_medium`, `terra_high`, `terra_xhigh`, `terra_max`, `terra_ultra` | Everyday implementation, tool use, exploration, debugging, review, and supporting analysis. Increase effort with difficulty and risk. |
| GPT-5.6 Sol | `sol_low`, `sol_medium`, `sol_high`, `sol_xhigh`, `sol_max`, `sol_ultra` | Ambiguous, complex, open-ended, high-value or polished work; architecture, deep research, high-risk decisions, and independent final review. |

## Effort

| Effort | Route when |
|---|---|
| `low` | Quick, well-scoped, low-risk work. |
| `medium` | Balanced default needing some planning or checking. |
| `high` | Difficult multi-step work, several sources, meaningful tradeoffs, or non-trivial verification. |
| `xhigh` | Very difficult reasoning, broad context, subtle edge cases, or higher risk. |
| `max` | Hardest single-agent problems where depth matters more than latency or usage. |
| `ultra` | Supported tasks that divide into genuinely independent subproblems; do not use merely as a stronger Max. |

## Escalation examples

- Tiny answer or one obvious edit: `spark_medium`.
- Repetitive structured transformation: `luna_low` or `luna_medium`.
- Routine repository implementation: `terra_medium`.
- Difficult debugging or security-sensitive implementation: `terra_high` through `terra_max`.
- Architecture or ambiguous multi-system design: `sol_high` through `sol_max`.
- Fresh high-confidence final review: a fresh `sol_high` or stronger read-only profile when isolation is required and available.
