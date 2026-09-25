# Dynamic subagent routing

Use `route-subagents` for explicit agent/model/effort requests or material delegation benefit. The native catalog contains GPT-6 Luna, Sol, and Astra only.

Implicit route: choose Luna for clear and repeatable work, Sol for repository work or consequential judgment, and Astra for the hardest end-to-end work when Sol is insufficient or Astra's fit is essential. Match the skill's examples first, then the catalog route table. The baseline profile sets the minimum Intelligence Index. Exclude unavailable, incompatible, under-floor, and gated profiles; retain the highest task-fit tier, then choose the lowest published benchmark task cost, with intelligence as the tie-breaker. Never trade away natural task fit for a cheaper benchmark result.

Defaults: Luna=`max` unless positively simple, with `xhigh` for hard bounded deterministic work. Sol=`medium`, escalating through `high` and `xhigh`; use `max` only for demonstrably indivisible extreme work. Astra starts at `low`; use `medium` only if Low is insufficient. Astra `high`/`xhigh`/`max` and all Luna/Sol/Astra `ultra` profiles require an explicit user request. Ultra has no separate benchmark score or cost. Difficulty depends on reasoning, ambiguity, risk, context coupling, and verification; length and repetitive volume do not raise effort.

Benchmark data is the user-supplied Artificial Analysis v4.3.2 chart dated 2026-09-25. Its USD values are costs for a fixed benchmark workload, not Codex quota or credit consumption. Do not equate effort names across families: Luna XHigh and Sol Low both score 34; Sol XHigh scores 44.

Explicit exposed profile wins. If it is unavailable, stop; do not substitute. Bound scope, avoid overlapping ownership and redundant retries, and keep verification and synthesis with the primary agent.

The local OpenCode/Qwen worker is explicit opt-in only. Use or consult it only when the user's current request explicitly asks for local Qwen, local OpenCode, or the local worker by name. A general request for a subagent, a simple task, free/unlimited usage, native quota pressure, or apparent task fit is not authorization. Otherwise route only among native Codex profiles. Its default agent mode may use OpenCode tools and modify the supplied workspace; give it only user-authorized scope and always verify its work.

For every spawn set `task_name=<scope>_<model>_<effort>` using model codes `l/s/a` and effort codes `l/m/h/xh/mx/u`; lowercase and underscores only. Example: `audit_cross_system_a_xh`.
