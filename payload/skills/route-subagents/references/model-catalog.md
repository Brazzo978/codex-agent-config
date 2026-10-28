# Route catalog — 28 October 2026

The authoritative data is [routing-data.json](routing-data.json). Intelligence now uses the user's **Artificial Analysis Intelligence Index v5.0** chart dated **2026-10-28**, with nine evaluations. The old v4.3.2 scores are superseded, not interchangeable with v5.0 values.

## Current intelligence

| Effort | GPT-6 Luna | GPT-6.1 Terra | GPT-6.1 Sol | GPT-6 Astra |
|---|---:|---:|---:|---:|
| Low | 10 | 29 | 35 | 43 |
| Medium | 18 | 38 | 46 | 51 |
| High | 21 | 42 | 50 | 55 |
| XHigh | 23 | 45 | 52 | 55 |
| Max | 28 | 51 | 55 | 57 |

Non-reasoning variants remain outside this bundle. Ultra has no measured score or cost in the supplied charts. Astra Low/Medium are available for justified specialized workflows or advice after a real stall; higher Astra efforts are explicit-only.

## Costs and provenance

Luna is inexpensive, **not free**. The user's cost rule is tariff-first after task fit and required capability: when Terra and Sol both qualify, prefer Terra because its nominal same-usage tariff is half Sol's. Retain Luna's supplied nonzero costs.

The supplied cost-per-task data is from **2026-10-27, benchmark v4.3.2**. Retain it as a dated historical routing proxy while v5.0 task costs are unavailable:

| Effort | Luna historical USD/task | Terra historical USD/task | Sol historical USD/task |
|---|---:|---:|---:|
| Low | 0.0045 | 0.05 | 0.13 |
| Medium | 0.02 | 0.10 | 0.21 |
| High | 0.03 | 0.13 | 0.32 |
| XHigh | 0.04 | 0.19 | 0.39 |
| Max | 0.07 | 0.40 | 0.72 |

These are not measured costs for the v5.0 evaluation mix or a Codex quota forecast. The JSON and resolver output carry separate intelligence and task-cost benchmarks/dates. Historical task costs may rank efforts only within equal nominal tariffs when `cost_policy.allow_historical_task_cost_proxy` is enabled. They cannot reverse Terra's priority over an equally suitable qualifying Sol. If disabled, use the nominal tariff and lowest sufficient effort.

The supplied nominal input/output prices imply approximately Luna:Terra:Sol = 0.1:1:2 for the same uncached usage. Cache mix and token volume can change the task total. This ratio is the primary cross-family cost preference after fit/capability, not a conversion to Codex credits.

## Fit and selection

1. Honor an explicit profile exactly; stop if unavailable. An explicit model restricts optimization to that family.
2. Classify the task as bounded, execution, judgment, or a genuinely heavy specialized workflow. Known-file edits may be bounded; a short bug report needing broad repository investigation is execution.
3. Take the workload/difficulty baseline's **current v5.0** score as the capability floor. Additional requirements may raise it, never lower it.
4. Exclude unavailable, incompatible, under-floor, and gated profiles. Astra High/XHigh/Max and all Ultra profiles require explicit requests. Sol Max requires a demonstrated indivisible extreme need or an explicit request.
5. Keep the highest eligible task-fit tier. Terra and Sol can be equally suitable. Astra has a distinct natural fit only for justified exceptionally difficult specialized workflows or heavy advisory blockers.
6. Choose the lowest nominal same-usage tariff within that fit: Luna 0.1, Terra 1, Sol 2. When Terra and Sol both meet the task requirement, Terra wins. Task costs are secondary only within equal tariffs; use current data or an enabled labeled historical proxy, then sufficient effort. Never divide intelligence by cost.
7. If none qualifies, report the unmet requirement rather than lowering the floor or activating a specialized Astra fit without a reason.

The resolver [select_profile.py](../scripts/select_profile.py) makes no network or model calls.

## Routes with the user's tariff priority and v5.0 floors

| Typical request | v5.0 baseline floor | Selected profile |
|---|---:|---|
| Mechanical extraction | 10 | `luna_low` |
| Simple summary or transformation | 18 | `luna_medium` |
| Familiar bounded checks | 21 | `luna_high` |
| Hard deterministic bounded work | 23 | `luna_xhigh` |
| Demanding bounded work (Luna Max baseline) | 28 | `luna_max` |
| Narrow execution requiring repository context | 29 | `terra_low` |
| Routine implementation | 38 | `terra_medium` |
| Normal execution | 42 | `terra_high` |
| Subtle execution | 45 | `terra_xhigh` |
| Complex execution (Terra Max baseline) | 51 | `terra_max` |
| Consequential judgment with equal Terra/Sol fit | 46 | `terra_max` (51) |
| Difficult judgment with equal Terra/Sol fit | 50 | `terra_max` (51) |
| Exceptional ambiguity | 52 | `sol_xhigh` |
| Demonstrated indivisible extreme need | 55 | `sol_max` |
| Heavy specialized workflow | 43 | `astra_low` |
| Heavy workflow needing depth beyond Low | 51 | `astra_medium` |

Terra Max (51) and Sol Medium (46) are not equivalent scores. Terra Max can nevertheless meet a task whose minimum is 46 or 50; if both families have equal fit, Terra's lower tariff gives it priority. Sol XHigh (52) is needed when the task requires more than Terra Max can provide, or when the suitable Terra profile is unavailable. Dated task costs such as $0.39 for Sol XHigh versus $0.40 for Terra Max do not override the user's tariff rule. Explicit requests remain exact.

## Optional advisor after a real stall

Read [advisor-mode.md](advisor-mode.md) only when focused attempts fail to resolve a concrete blocker or the user directly requests a second opinion. Ordinary uncertainty, a GUI mention, and initial planning do not trigger advice. Automatic advisor mode requires observed-stall context and one precise question, and returns a brief read-only, non-delegating contract. General advice uses Sol Low/Medium, rising only when needed; justified heavy specialized advice uses Astra Low/Medium. Execution and verification stay with the primary.
