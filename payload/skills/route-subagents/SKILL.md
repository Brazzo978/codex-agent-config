---
name: route-subagents
description: Dynamically choose and spawn the best available Codex custom-agent model and reasoning profile. Use for every explicit agent, subagent, parallel-work, model, or effort request, and whenever delegation would materially improve speed, quality, context isolation, independent verification, or long-task reliability.
---

# Route Subagents

1. Load `references/model-catalog.md`; do not refresh externally.
2. Explicit profile: use exactly; unavailable => stop.
3. Implicit profile: derive `W` and `D`; use `route_table[W][D]`. Use fitness formula only for cross-family fallback/audit.
4. Spark-eligible microtask => `spark_medium`.
5. Apply Max/Ultra gates from catalog.
6. Set `task_name=<scope>_<model_code>_<effort_code>` from catalog; keep scope short.
7. Spawn minimum bounded lanes; no overlapping ownership or redundant retries.
8. Primary agent owns synthesis, verification, acceptance, and evidence-based escalation.

Constraints:

- Fit gate precedes cost.
- Set `R` from cognitive difficulty/risk, not length or repetitive volume.
- `I>=R`; never optimize raw `I/C`.
- Luna default `max`; lower only after positive simple classification.
- Terra default `high`; `max` for complex settled execution.
- Sol default `medium`; normal ceiling `xhigh`; `max` gated; `ultra` explicit-only.
- Ultra = max reasoning + automatic delegation; requires independent lanes.
