# route-index

```yaml
version: 2026-09-07
external_lookup: false

input:
  W: [spark, luna, terra, sol, astra]
  D: family_specific_route_key
  R: integer_optional_fallback
  R_basis: [reasoning_complexity, ambiguity, risk, context_coupling, verification]
  R_not_increased_by: [text_length, item_count, repetitive_volume]

route_table:
  spark: {micro: spark_medium, default: spark_medium}
  luna: {mechanical: luna_low, simple: luna_medium, checked: luna_high, hard_bounded: luna_xhigh, default: luna_max}
  terra: {lookup: terra_low, routine: terra_medium, normal: terra_high, subtle_high_risk: terra_xhigh, complex: terra_max, default: terra_high}
  sol: {small_judgment: sol_low, normal: sol_medium, difficult: sol_high, exceptional: sol_xhigh, ultra_complex_indivisible: sol_max, default: sol_medium}
  astra: {entry: astra_low, hardest_end_to_end: astra_low, exceptional_depth: astra_medium, default: astra_low}

primary_select:
  profile: route_table[W][D]
  unknown_D: route_table[W][default]
  R_effective: R_if_supplied_else_I(profile)
  sol_max: apply_gate
  astra_max: apply_gate
  optimization_bypass: [spark_medium, explicit_profile, ultra_profiles]

astra_policy:
  capability_anchor: {astra_low: 49, sol_max: 51, relation: near_not_equal}
  entry: astra_low
  implicit_ceiling: astra_medium
  explicit_only: [astra_high, astra_xhigh, astra_max, astra_ultra]
  selection: cheapest_eligible_profile

spark_context_gate:
  published_token_limit: unknown
  require: [tiny_self_contained_context, few_local_inputs, short_output]
  reject: [multi_file_context, long_documents, broad_history, many_tool_traces, cross_source_synthesis]
  overflow: escalate_once_without_spark_retry

fit: # 2=natural, 1=fallback, 0=invalid
  spark: {spark: 2, luna: 1, terra: 0, sol: 0, astra: 0}
  luna:  {spark: 0, luna: 2, terra: 1, sol: 1, astra: 0}
  terra: {spark: 0, luna: 0, terra: 2, sol: 1, astra: 0}
  sol:   {spark: 0, luna: 0, terra: 0, sol: 2, astra: 1}
  astra: {spark: 0, luna: 0, terra: 0, sol: 1, astra: 2}

profiles: # I=AA Intelligence Index v4.2; C=weighted average USD per Index task
  luna_low:     {family: luna,  I: 26, C: null, I_estimate: true}
  luna_medium:  {family: luna,  I: 30, C: null, I_estimate: true}
  luna_high:    {family: luna,  I: 37, C: null, I_estimate: true}
  luna_xhigh:   {family: luna,  I: 42, C: 0.06}
  luna_max:     {family: luna,  I: 43, C: 0.10}
  terra_low:    {family: terra, I: 32, C: null, I_estimate: true}
  terra_medium: {family: terra, I: 37, C: null, I_estimate: true}
  terra_high:   {family: terra, I: 41, C: 0.30}
  terra_xhigh:  {family: terra, I: 44, C: 0.50}
  terra_max:    {family: terra, I: 47, C: 0.81}
  sol_low:      {family: sol,   I: 41, C: 0.23}
  sol_medium:   {family: sol,   I: 46, C: 0.37}
  sol_high:     {family: sol,   I: 48, C: 0.61}
  sol_xhigh:    {family: sol,   I: 50, C: 0.89}
  sol_max:      {family: sol,   I: 51, C: 1.25}
  astra_low:    {family: astra, I: 49, C: 0.63}
  astra_medium: {family: astra, I: 52, C: 1.16}
  astra_high:   {family: astra, I: 53, C: 1.41}
  astra_xhigh:  {family: astra, I: 54, C: 1.85}
  astra_max:    {family: astra, I: 55, C: 2.57}

data_quality:
  source_date: 2026-09-07
  I_estimates: [luna_low, luna_medium, luna_high, terra_low, terra_medium]
  C_unavailable: [luna_low, luna_medium, luna_high, terra_low, terra_medium]
  null_C_rule: preserve_primary_route_and_do_not_estimate

allowance_weight_same_tokens: {luna: 1, terra: 10, sol: 25, astra: unknown_high, spark: separate}

gate:
  default: 1
  sol_max: user_explicit OR user_confirmed_ultra_complex_indivisible
  astra_high: user_explicit
  astra_xhigh: user_explicit
  astra_max: user_explicit

ultra: # max reasoning + automatic delegation; no I/C
  luna: {implicit: true, require: [lanes>=2, independent, homogeneous]}
  terra: {implicit: limited, require: [lanes>=2, lanes<=3, independent, disjoint_ownership, material_speedup]}
  sol: {explicit_user_request_only: true}
  astra: {explicit_user_request_only: true}

fitness:
  scope: scored_implicit_profiles_only
  eligible(p): gate(p) AND I(p)>=R_effective AND fit(W,family(p))>0
  F_max: max(fit(W,family(p)) WHERE eligible(p))
  candidates: profiles_where(eligible=true AND fit=F_max AND C!=null)
  select: argmin_lex([C(p), -I(p)])
  baseline_C_null: preserve_primary_profile
  priority: [capability_floor, compatibility, gate, natural_fit, cost, intelligence]
  forbidden: [raw_I_div_C, silent_R_reduction, api_USD_as_chatgpt_credits]
  use: always_after_example_or_route_table
  bypass_rule: preserve_exact_profile

gui_task_name:
  format: scope_model_effort
  model_code: {spark: sp, luna: l, terra: t, sol: s, astra: a}
  effort_code: {low: l, medium: m, high: h, xhigh: xh, max: mx, ultra: u}
  constraints: [lowercase, digits, underscores]
  example: scansione_rete_l_xh

explicit_profile:
  priority: highest
  unavailable: stop
  substitution: forbidden
```

## Standard examples

- "Give me the exact command to rename this Git branch." -> `spark_medium`.
- "Extract names and dates from 500 identical records." -> `luna_low`.
- "Write a simple ten-page product description from this fixed outline." -> `luna_medium`.
- "Check every edge case in this bounded deterministic transformation." -> `luna_xhigh`.
- "Implement this settled feature across several files and run its tests." -> `terra_high`.
- "Investigate and fix this complex regression; the architecture is already decided." -> `terra_max`.
- "Choose between these architectures and explain the tradeoffs." -> `sol_medium`.
- "Audit a high-risk cross-system design with subtle assumptions." -> `sol_xhigh`.
- "Complete this exceptionally difficult workflow across code, browser, research, and documents; Sol is insufficient." -> `astra_low`.
- "This exceeds Astra Low and needs more depth, but I did not request a higher tier." -> `astra_medium`.
- "Use Astra XHigh to resolve this exceptional high-risk cross-system problem." -> `astra_xhigh`.

Task size changes time and batching, not family by itself. Spark additionally requires the complete relevant context to stay tiny and local.
