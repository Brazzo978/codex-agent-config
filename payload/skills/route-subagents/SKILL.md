---
name: route-subagents
description: Choose GPT-6 Luna, GPT-6.1 Terra, or GPT-6.1 Sol for subagent work by task fit and cost. Astra Low/Medium cover exceptional workflows or optional brief advice; higher Astra and Ultra require an explicit request.
---

# Route Subagents

Honor an explicitly named exposed model/profile and effort exactly. Stop if unavailable; do not substitute. Otherwise compare the supplied nonzero costs: Luna is very inexpensive but not free; Terra's nominal same-usage tariff is half Sol's. Keep capability and task fit above cost.

## Choose an implicit route

Read [references/model-catalog.md](references/model-catalog.md) for the current fit and [references/routing-data.json](references/routing-data.json) for the numeric source. Classify the task by its actual scope:

- **Bounded:** clear, repeatable work, narrow lookups, summaries, known-file edits, and deterministic checks -> Luna. Use Low for mechanical work, Medium for simple transformations, High for checked work, XHigh for hard bounded work, and Max for demanding bounded work.
- **Execution:** repository work with exploration, coupled files, implementation, tests, debugging, or moderate investigation -> Terra. Use Low for a narrow execution task, Medium for routine work, High normally, and XHigh for subtle or risky execution.
- **Heavy specialized workflow:** exceptionally difficult work across systems or disciplines where Astra's task fit matters -> Astra Low; Medium only when Low lacks depth. This is a distinct fit, not a generic expensive fallback.
- **Judgment:** unresolved architecture, competing causes, consequential decisions, or synthesis requiring more capability -> choose the minimum sufficient capability. Moderate judgment can use Terra High; ordinary consequential judgment starts at Sol Medium, difficult work at High, and exceptional work at XHigh. Sol Max requires a demonstrated indivisible extreme need.

The example or route-table profile establishes a minimum capability in the current **v5.0 index dated 2026-10-28**. Preserve that floor during optimization and treat Terra/Sol as equally suitable when either can perform the task. Luna has no automatic zero-cost priority.

After fit and the v5.0 capability floor, rank nominal same-usage tariffs first: Luna 0.1, Terra 1, Sol 2. If Terra and Sol both satisfy the task, choose Terra for its half tariff. The supplied **v4.3.2 task costs dated 2026-10-27** are separately labeled historical data and may rank efforts only within equal tariffs; they must not reverse that cross-family preference. If the historical proxy is disabled, use the lowest sufficient effort. New scores remove the old equivalence: Terra Max is 51 and Sol Medium is 46. At a requirement of 51, choose Terra Max; a requirement of 52 needs Sol XHigh. Luna Max remains the cheap bounded choice at floor 28 even though Terra Low's dated benchmark task cost is lower.

Use the bundled resolver when availability, cross-family choices, or gates matter:

```text
python <skill-dir>/scripts/select_profile.py --workload execution --difficulty normal
```

The resolver reads the JSON catalog, preserves the floor, excludes unavailable/gated profiles, and reports the selection reason. `--available` accepts the exposed profile names. `--minimum-index` may raise the floor; it never lowers the baseline. An explicit model request restricts candidates to that model's family; a named profile is exact. Use `--allow-sol-max` only for a demonstrated indivisible extreme need. Do not silently replace a missing exact request.

Astra Low and Medium can be selected implicitly for a justified heavy workflow or a difficult advisor question. Astra High/XHigh/Max and all Luna/Terra/Sol/Astra Ultra profiles require an explicit request. Ultra has no inferred benchmark score or cost. An Ultra request does not by itself authorize extra delegation. Task length and repetitive volume change batching, not family or effort.

For a native spawn, use `task_name=<scope>_<model_code>_<effort_code>`: models `l/t/s/a`, efforts `l/m/h/xh/mx/u`. Use bounded ownership and keep verification and synthesis in the primary agent.

## Advisor after a real stall

The executor normally works and verifies independently. It may consult Sol or Astra when concrete attempts are failing to converge: a persistent bug, unexplained behavior after focused checks, or a difficult GUI/design problem that remains unresolved. A direct user request for a second opinion also permits consultation.

Do not ask for advice at every thought, uncertainty, planning step, GUI task, or phase. Read [references/advisor-mode.md](references/advisor-mode.md) when a real blocker warrants it. Sol Medium is the usual advisor; use Low for a narrow modest blocker. Astra Low/Medium are available when an exceptionally difficult specialized blocker justifies their fit.

Send what failed, what has been tried, relevant evidence/constraints, and one precise question. Request a short opinion; the advisor does not implement, edit files, or delegate. Keep execution, the decision, and verification with the primary.

Use `--mode advisor --stalled-on "attempts and observed failure" --consult-reason "one question"`. The resolver rejects automatic advice without stall evidence. Use `--advisor-fit heavy` for Astra's specialized lane. Only an explicit user request permits `--advisor-requested` without a prior stall. Begin with one consultation and follow up only for a material new fact or unresolved contradiction.

## Local OpenCode worker

This lane is explicit opt-in only. Enter it only when the current user request names local Qwen, local OpenCode, or the local worker. Generic delegation, free usage, and native quota pressure do not authorize it.

When explicitly requested, read [references/local-worker.md](references/local-worker.md). Pass the authorized workspace, explicit files, and bounded outcome to `local_opencode_worker.start_task`; use Low for deterministic execution, Medium for bounded work needing judgment, and XHigh only for exceptional difficulty or risk. Preserve task/session IDs, inspect progress with bounded waits, and verify the result. Leave timeout omitted unless a hard limit is required. Use the bundled script only when MCP is unavailable.
