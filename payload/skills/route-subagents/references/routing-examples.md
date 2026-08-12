# route-examples

```yaml
microtask: spark_medium
luna_simple: minimum_R_match
long_simple_text: {W: luna, R: simple, select: minimum_cost_eligible_luna}
luna_default: luna_max
terra_normal: terra_high
terra_subtle: terra_xhigh
terra_complex: terra_max
sol_normal: sol_medium
sol_difficult: sol_high
sol_exceptional: sol_xhigh
short_complex_architecture: {W: sol, R: difficult_or_higher}
sol_ultra_complex_indivisible: sol_max_with_gate
parallel: {luna: implicit_if_eligible, terra: limited, sol: explicit_only}
```
