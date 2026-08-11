---
name: route-subagents
description: Dynamically choose and spawn the best available Codex custom-agent model and reasoning profile. Use for every explicit agent, subagent, parallel-work, model, or effort request, and whenever delegation would materially improve speed, quality, context isolation, independent verification, or long-task reliability.
---

# Route Subagents

Choose the model and effort before spawning; a running agent cannot change its own model. Preserve the official workload roles of Sol, Terra, Luna, and Spark, then compare concrete model-plus-effort profiles with the dated intelligence ladder in the catalog. At equal effort the observed order is `Sol > Terra > Luna`; across different efforts the profiles interleave. Spark is unranked and remains the fastest microtask lane.

## Route

1. Read [references/model-catalog.md](references/model-catalog.md).
2. Inspect the native spawn tool's currently exposed custom-agent types. Runtime exposure and account/workspace policy are authoritative.
3. Honor an explicit user-selected profile exactly. If unavailable, stop and report it; never silently substitute.
4. Otherwise apply workload fit first using the official family roles:
   - Sol for ambiguity, architecture, high-value judgment, polish, or critical review.
   - Terra for everyday implementation, tool use, exploration, and debugging.
   - Luna for clear, repeatable, tightly specified work.
   - Spark for eligible near-instant microtasks with little context, preserving the main GPT-5.6 allowance through its separate usage limit.
5. Choose the concrete profile second. Start at the lowest effort that covers the steps, edge cases, risk, and verification burden, then use the dated Artificial Analysis intelligence-and-API-cost table. Set a minimum intelligence floor and select the cheapest natural-fit profile that reaches it. A higher-effort lower family may outrank a lower-effort higher family, but it keeps its original workload strengths and weaknesses.
6. Apply the usage-budget gate from the catalog. Every spawned agent consumes its own model and tool usage. If Max or Ultra was not explicitly requested, explain the concrete benefit and obtain user confirmation before spawning it.
7. If the task remains hard to classify, read [references/routing-examples.md](references/routing-examples.md). Do not load it for an obvious route.
8. Spawn the minimum number of bounded assignments needed, each with objective, owned scope, interfaces, constraints, verification, and required evidence.
9. Keep the primary session responsible for synthesis and acceptance. Verify material claims, and escalate with a fresh stronger profile only when evidence shows the selected lane was insufficient.

## Guardrails

- Do not use Spark or Luna for broad-context synthesis, architecture, open-ended debugging, or high-risk decisions.
- Prefer Spark over GPT-5.6 when Spark scores `5` for the task and is exposed; if an implicit Spark route is unavailable, select the next suitable profile and report the change.
- At equal effort preserve the observed order `Sol > Terra > Luna`; across different efforts follow the profile ladder in the catalog. Do not assign Spark an Intelligence Index score that the source does not provide.
- Do not route to Sol merely because a task is large; use Terra when the architecture and acceptance criteria are already settled.
- Permit a higher-effort lower family to win on the fit-conditioned cost frontier only when its workload fit remains sufficient. Never maximize raw intelligence divided by cost; a benchmark score never repairs a family mismatch.
- Do not use Max for a divisible workload or Ultra as a synonym for “more intelligent.”
- Do not spend Max or Ultra on first-pass exploration, ordinary implementation, or speculative duplicate attempts.
- Do not retry a failed lane unchanged. Diagnose first; escalate once only when evidence justifies the additional usage.
- Avoid parallel agents that edit the same files. Preserve user and concurrent edits.
- Report unavailable profiles, routing mismatches, failures, and fallbacks explicitly.

## Invocation examples

```text
Use $route-subagents and choose the lowest sufficient profile for this task.
```

```text
Use $route-subagents with luna_high exactly; stop if that profile is unavailable.
```

```text
Use $route-subagents to split only the independent work, then verify and consolidate the results.
```
