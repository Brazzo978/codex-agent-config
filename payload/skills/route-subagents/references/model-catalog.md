# Route catalog — 27 October 2026

The authoritative numeric data and route baselines are in [routing-data.json](routing-data.json). Model IDs are GPT-6 Luna, GPT-6.1 Terra, and GPT-6.1 Sol. Astra Low/Medium cover exceptionally difficult specialized workflows and optional heavy advisory questions.

The user reports Luna as free and Terra's same-usage tariff as half Sol's. Use free Luna when it meets both scope and capability. For paid profiles, use benchmark task costs as a comparison proxy for total work: tariff alone does not account for token volume. Do not present these USD values as Codex credits or a measured account bill.

| Effort | Luna I / benchmark USD | Terra I / benchmark USD | Sol I / benchmark USD |
|---|---:|---:|---:|
| Low | 22 / 0.0045 | 36 / 0.05 | 42 / 0.13 |
| Medium | 30 / 0.02 | 41 / 0.10 | 48 / 0.21 |
| High | 33 / 0.03 | 44 / 0.13 | 50 / 0.32 |
| XHigh | 35 / 0.04 | 45 / 0.19 | 51 / 0.39 |
| Max | 38 / 0.07 | 48 / 0.40 | 52 / 0.72 |

I = Artificial Analysis Intelligence Index v4.3.2, transcribed from the user's charts dated 2026-10-27. Rounded plotted values do not establish model-specific strengths on every task. Non-reasoning Luna is outside this profile bundle. Ultra has no separate measured value.

## Fit and selection

1. Honor an explicit profile exactly; stop if it is not exposed. An explicit model/family restricts optimization to that family.
2. Classify scope as bounded, execution, judgment, or a justified heavy specialized workflow. Bounded means a clear outcome and limited context, not merely a short prompt. A small known-file code edit can be bounded; a small-looking bug requiring repository exploration is execution.
3. Pick the route-table baseline for that workload/difficulty and keep its Intelligence Index as a floor. An optional higher requirement raises that floor.
4. Exclude unavailable, incompatible, under-floor, and gated candidates. Astra Low/Medium are implicit only in the heavy specialized or heavy advisor fit; Astra High/XHigh/Max and all Ultra profiles are explicit-only. Sol Max needs evidence of an indivisible extreme task or an explicit request.
5. Keep the highest eligible fit tier. Luna fits bounded work. Terra and Sol are both natural fits for execution and judgment when their capability suffices. In a justified heavy specialized workflow, Astra has the natural-fit tier and Sol is a fallback. This prevents the aggregate cost/index frontier from erasing a useful specialized Astra fit.
6. Prefer free candidates, using the lowest sufficient effort. For paid candidates choose the lowest published benchmark task cost, then the lower same-usage tariff, then higher intelligence. Never use a raw intelligence/cost ratio or lower the floor to save cost.
7. If no profile qualifies, report that no compatible exposed profile meets the requirement; do not silently drop the floor or switch to a specialized Astra fit without a task-specific reason.

The resolver [select_profile.py](../scripts/select_profile.py) implements these rules without network calls. Its default catalog is this skill's JSON file.

## Resulting routes

| Typical request | Baseline floor | Selected profile |
|---|---:|---|
| Extract fields from fixed records | 22 | `luna_low` |
| Summarize or rewrite a clear document | 30 | `luna_medium` |
| Check familiar bounded edge cases | 33 | `luna_high` |
| Hard deterministic transformation | 35 | `luna_xhigh` |
| Demanding bounded task / known-file fix | 38 | `luna_max` |
| Narrow execution requiring repository/tool context | 36 | `terra_low` |
| Routine implementation | 41 | `terra_medium` |
| Normal feature, tests, review, or investigation | 44 | `terra_high` |
| Subtle or risky execution | 45 | `terra_xhigh` |
| Complex coupled execution | 48 (Terra Max baseline) | `sol_medium` |
| Consequential architecture or judgment | 48 | `sol_medium` |
| Difficult tradeoffs or investigation | 50 | `sol_high` |
| Exceptional ambiguity or high risk | 51 | `sol_xhigh` |
| Demonstrated indivisible extreme need | 52 | `sol_max` |
| Exceptionally difficult specialized workflow | 46 | `astra_low` |
| Same specialized workflow requiring depth beyond Low | 50 | `astra_medium` |

Terra Max remains available: use it when explicitly requested or when cheaper compatible Sol profiles are unavailable and the floor is 48. Sol Low is also available explicitly; Terra High normally provides more capability at the same measured task cost. Do not ban profiles merely because they are not on the default frontier.

Raise effort because of reasoning, ambiguity, risk, coupled context, or verification needs. More text or repeated records alone do not justify escalation.

## Optional advisory selection

Execution remains the default. Read [advisor-mode.md](advisor-mode.md) when focused attempts have failed to resolve a concrete blocker or the user directly requests a second opinion. Ordinary uncertainty, a GUI task, and initial planning do not trigger advice. Automatic advisor mode requires both observed-stall context and one precise question, and returns a read-only, non-delegating brief. General advice uses Sol Low/Medium, rising only for a concrete need; heavy specialized advice uses Astra Low/Medium. This does not promote the whole task to Astra.
