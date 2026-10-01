# Route catalog

```yaml
version: 2026-09-25
benchmark: Artificial Analysis Intelligence Index v4.3.2
external_lookup: false
models: [gpt-6-luna, gpt-6.1-sol, gpt-6-astra]
families: [luna, sol, astra]

# I = Intelligence Index. C = weighted-average USD per Intelligence Index task.
# These are benchmark API costs, not Codex subscription/allowance charges.
profiles:
  luna_low:     {model: gpt-6-luna,  effort: low,    I: 21, C: 0.0045}
  luna_medium:  {model: gpt-6-luna,  effort: medium, I: 29, C: 0.02}
  luna_high:    {model: gpt-6-luna,  effort: high,   I: 32, C: 0.03}
  luna_xhigh:   {model: gpt-6-luna,  effort: xhigh,  I: 34, C: 0.04}
  luna_max:     {model: gpt-6-luna,  effort: max,    I: 37, C: 0.07}
  sol_low:      {model: gpt-6.1-sol, effort: low,    I: 34, C: 0.13}
  sol_medium:   {model: gpt-6.1-sol, effort: medium, I: 40, C: 0.25}
  sol_high:     {model: gpt-6.1-sol, effort: high,   I: 43, C: 0.37}
  sol_xhigh:    {model: gpt-6.1-sol, effort: xhigh,  I: 44, C: 0.53}
  sol_max:      {model: gpt-6.1-sol, effort: max,    I: 48, C: 1.06}
  astra_low:    {model: gpt-6-astra, effort: low,    I: 46, C: 0.82}
  astra_medium: {model: gpt-6-astra, effort: medium, I: 50, C: 1.54}
  astra_high:   {model: gpt-6-astra, effort: high,   I: 51, C: 1.73}
  astra_xhigh:  {model: gpt-6-astra, effort: xhigh,  I: 52, C: 2.31}
  astra_max:    {model: gpt-6-astra, effort: max,    I: 53, C: 3.26}

# Ultra has no separate benchmark score or cost. It is never an implicit route.
ultra: {luna: explicit_only, sol: explicit_only, astra: explicit_only}

route_table:
  luna: {mechanical: luna_low, simple: luna_medium, checked: luna_high, hard_bounded: luna_xhigh, demanding_bounded: luna_max, default: luna_max}
  sol: {small_judgment: sol_low, normal: sol_medium, difficult: sol_high, exceptional: sol_xhigh, indivisible_extreme: sol_max, default: sol_medium}
  astra: {entry: astra_low, exceptional_depth: astra_medium, default: astra_low}

# 2 = natural task fit; 1 = fallback only when natural family cannot meet the
# capability need and the substitute is compatible; 0 = incompatible.
fit:
  luna:  {luna: 2, sol: 1, astra: 0}
  sol:   {luna: 0, sol: 2, astra: 1}
  astra: {luna: 0, sol: 1, astra: 2}

gates:
  luna_ultra: explicit_only
  sol_max: demonstrated_indivisible_extreme
  sol_ultra: explicit_only
  astra_high: explicit_only
  astra_xhigh: explicit_only
  astra_max: explicit_only
  astra_ultra: explicit_only

routine_ceilings: {luna: max, sol: xhigh, astra: medium}
astra_entry: low
astra_escalation: medium_only_when_low_is_insufficient

selection:
  baseline: route_table[dominant_family][difficulty]
  floor: I(baseline)
  eligible: available AND compatible AND not_gated AND I>=floor
  rank: [highest_fit_tier, lowest_C, highest_I]
  constraints:
    - Keep a natural family when it meets the required capability.
    - Do not select a higher effort only because the task is long or repetitive.
    - Do not equate benchmark USD with Codex quota or credits.
    - Do not infer an Ultra score or price from Max.
    - Explicit model/profile requests are exact; stop if unavailable.
  cost_data_source: user_supplied_Artificial_Analysis_charts_2026-09-25

task_name:
  format: scope_model_effort
  model_codes: {luna: l, sol: s, astra: a}
  effort_codes: {low: l, medium: m, high: h, xhigh: xh, max: mx, ultra: u}
```

## Standard examples

- "Extract names and dates from 500 identical records." -> `luna_low`.
- "Summarize this fixed outline with a few checks." -> `luna_medium`.
- "Verify a bounded transformation with familiar edge cases." -> `luna_high`.
- "Solve a hard but deterministic task within a small, clear scope." -> `luna_xhigh`.
- "Handle a demanding but still bounded deterministic task." -> `luna_max`.
- "Implement a feature across files and run focused tests." -> `sol_medium`.
- "Investigate a difficult regression with several plausible causes." -> `sol_high`.
- "Review a high-risk design with subtle cross-system assumptions." -> `sol_xhigh`.
- "Carry out an exceptional end-to-end workflow requiring capabilities beyond normal Sol routing." -> `astra_low`.
- "Astra Low is insufficient for this exceptional workflow." -> `astra_medium`.

The benchmark measures a fixed evaluation workload. Use its scores as a capability floor and its costs to compare compatible routes, not as a prediction of the cost of the user's task. Task volume changes batching and elapsed time; complexity, ambiguity, risk, context coupling, and verification needs determine the family and effort.
