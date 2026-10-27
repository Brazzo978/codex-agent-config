---
name: route-subagents
description: Choose GPT-6 Luna, GPT-6.1 Terra, or GPT-6.1 Sol for subagent work by task fit and cost. Astra and Ultra require an explicit request.
---

# Route Subagents

Honor an explicitly named exposed model/profile and effort exactly. Stop if unavailable; do not substitute. Otherwise route with the user's pricing preference: Luna is free, Terra has half Sol's tariff for the same usage. Keep capability and task fit above cost.

## Choose an implicit route

Read [references/model-catalog.md](references/model-catalog.md) for the current fit and [references/routing-data.json](references/routing-data.json) for the numeric source. Classify the task by its actual scope:

- **Bounded:** clear, repeatable work, narrow lookups, summaries, known-file edits, and deterministic checks -> Luna. Use Low for mechanical work, Medium for simple transformations, High for checked work, XHigh for hard bounded work, and Max for demanding bounded work.
- **Execution:** repository work with exploration, coupled files, implementation, tests, debugging, or moderate investigation -> Terra. Use Low for a narrow execution task, Medium for routine work, High normally, and XHigh for subtle or risky execution.
- **Judgment:** unresolved architecture, competing causes, consequential decisions, or synthesis requiring more capability -> choose the minimum sufficient capability. Moderate judgment can use Terra High; ordinary consequential judgment starts at Sol Medium, difficult work at High, and exceptional work at XHigh. Sol Max requires a demonstrated indivisible extreme need.

The example or route-table profile establishes a capability floor; retain it during cost optimization. Treat Terra and Sol as equally suitable when either can perform the task. Prefer free Luna whenever its scope and capability suffice. For paid candidates, compare the supplied per-task benchmark costs because a lower tariff can be offset by more tokens. Terra Max and Sol Medium both score 48, but the benchmark task costs are $0.40 and $0.21: choose Sol Medium when both fit. Terra High scores 44 at $0.13 and usually supersedes Sol Low (42 at $0.13). These benchmark USD values are comparison signals, not Codex quota forecasts.

Use the bundled resolver when availability, cross-family choices, or gates matter:

```text
python <skill-dir>/scripts/select_profile.py --workload execution --difficulty normal
```

The resolver reads the JSON catalog, preserves the floor, excludes unavailable/gated profiles, and reports the selection reason. `--available` accepts the exposed profile names. `--minimum-index` may raise the floor; it never lowers the baseline. An explicit model request restricts candidates to that model's family; a named profile is exact. Use `--allow-sol-max` only for a demonstrated indivisible extreme need. Do not silently replace a missing exact request.

Astra stays installed for explicit requests only. All Luna/Terra/Sol/Astra Ultra profiles require an explicit request and have no inferred benchmark score or cost. An Ultra request does not by itself authorize extra delegation. Task length and repetitive volume change batching, not family or effort.

For a native spawn, use `task_name=<scope>_<model_code>_<effort_code>`: models `l/t/s/a`, efforts `l/m/h/xh/mx/u`. Use bounded ownership and keep verification and synthesis in the primary agent.

## Local OpenCode worker

This lane is explicit opt-in only. Enter it only when the current user request names local Qwen, local OpenCode, or the local worker. Generic delegation, free usage, and native quota pressure do not authorize it.

When explicitly requested, read [references/local-worker.md](references/local-worker.md). Pass the authorized workspace, explicit files, and bounded outcome to `local_opencode_worker.start_task`; use Low for deterministic execution, Medium for bounded work needing judgment, and XHigh only for exceptional difficulty or risk. Preserve task/session IDs, inspect progress with bounded waits, and verify the result. Leave timeout omitted unless a hard limit is required. Use the bundled script only when MCP is unavailable.
