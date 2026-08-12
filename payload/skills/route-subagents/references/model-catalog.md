# route-index

```yaml
version: 2026-08-11
external_lookup: false

input:
  W: [spark, luna, terra, sol]
  D: family_specific_route_key
  R: integer_optional_fallback
  R_basis: [reasoning_complexity, ambiguity, risk, context_coupling, verification]
  R_not_increased_by: [text_length, item_count, repetitive_volume]

route_table:
  spark: {micro: spark_medium, default: spark_medium}
  luna: {mechanical: luna_low, simple: luna_medium, checked: luna_high, hard_bounded: luna_xhigh, default: luna_max}
  terra: {lookup: terra_low, routine: terra_medium, normal: terra_high, subtle_high_risk: terra_xhigh, complex: terra_max, default: terra_high}
  sol: {small_judgment: sol_low, normal: sol_medium, difficult: sol_high, exceptional: sol_xhigh, ultra_complex_indivisible: sol_max, default: sol_medium}

primary_select:
  profile: route_table[W][D]
  unknown_D: route_table[W][default]
  sol_max: apply_gate

fit: # 2=natural, 1=fallback, 0=invalid
  spark: {spark: 2, luna: 1, terra: 0, sol: 0}
  luna:  {spark: 0, luna: 2, terra: 1, sol: 1}
  terra: {spark: 0, luna: 0, terra: 2, sol: 1}
  sol:   {spark: 0, luna: 0, terra: 0, sol: 2}

profiles: # I=Intelligence Index; C=USD full evaluation suite
  luna_low:     {family: luna,  I: 34, C: 14}
  luna_medium:  {family: luna,  I: 39, C: 21}
  luna_high:    {family: luna,  I: 47, C: 55}
  luna_xhigh:   {family: luna,  I: 50, C: 95}
  luna_max:     {family: luna,  I: 52, C: 172}
  terra_low:    {family: terra, I: 41, C: 130}
  terra_medium: {family: terra, I: 47, C: 192}
  terra_high:   {family: terra, I: 50, C: 395}
  terra_xhigh:  {family: terra, I: 53, C: 590}
  terra_max:    {family: terra, I: 57, C: 1390}
  sol_low:      {family: sol,   I: 51, C: 344}
  sol_medium:   {family: sol,   I: 56, C: 580}
  sol_high:     {family: sol,   I: 57, C: 955}
  sol_xhigh:    {family: sol,   I: 59, C: 1525}
  sol_max:      {family: sol,   I: 61, C: 2823}

allowance_weight_same_tokens: {luna: 1, terra: 10, sol: 25, spark: separate}

gate:
  default: 1
  sol_max: user_explicit OR user_confirmed_ultra_complex_indivisible

ultra: # max reasoning + automatic delegation; no I/C
  luna: {implicit: true, require: [lanes>=2, independent, homogeneous]}
  terra: {implicit: limited, require: [lanes>=2, lanes<=3, independent, disjoint_ownership, material_speedup]}
  sol: {explicit_user_request_only: true}

fitness:
  A(p): gate(p) * indicator(I(p)>=R) * indicator(fit(W,family(p))>0)
  V(p): [A(p), fit(W,family(p)), -C(p)]
  select: argmax_lex(V)
  require: [A=1]
  priority: [eligibility, workload_fit, cost]
  forbidden: [raw_I_div_C, silent_R_reduction, api_USD_as_chatgpt_credits]
  use: cross_family_fallback_or_audit_only

gui_task_name:
  format: scope_model_effort
  model_code: {spark: sp, luna: l, terra: t, sol: s}
  effort_code: {low: l, medium: m, high: h, xhigh: xh, max: mx, ultra: u}
  constraints: [lowercase, digits, underscores]
  example: scansione_rete_l_xh

explicit_profile:
  priority: highest
  unavailable: stop
  substitution: forbidden
```
