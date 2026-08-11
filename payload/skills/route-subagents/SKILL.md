---
name: route-subagents
description: Dynamically choose and spawn the best available Codex custom-agent model and reasoning profile. Use for every explicit agent, subagent, parallel-work, model, or effort request, and whenever delegation would materially improve speed, quality, context isolation, independent verification, or long-task reliability.
---

# Route Subagents

Choose the model and effort before spawning; a running agent cannot change its own model. Match the model family to the shape of the work, then select the lowest sufficient effort.

## Route

1. Read [references/model-catalog.md](references/model-catalog.md).
2. Inspect the native spawn tool's currently exposed custom-agent types. Runtime exposure and account/workspace policy are authoritative.
3. Honor an explicit user-selected profile exactly. If unavailable, stop and report it; never silently substitute.
4. Otherwise choose the family first, using the fit matrix, the dated Artificial Analysis intelligence/cost snapshot, and the current relative cost index in the catalog. Task fit is a hard gate; the benchmark is a cost-performance prior only among profiles that can actually perform the work:
   - Spark first for eligible near-instant microtasks with little context, preserving the main GPT-5.6 allowance through its separate usage limit.
   - Luna for clear, repeatable, tightly specified work.
   - Terra for everyday implementation, tool use, exploration, and debugging.
   - Sol for ambiguity, architecture, high-value judgment, polish, or critical review.
5. Choose effort second. Start at the lowest level that covers the steps, edge cases, risk, and verification burden. Prefer a Pareto-efficient candidate when fit is comparable. A higher-effort cheaper family can beat a lower-effort expensive family only when its task-fit score remains strong. Do not treat effort names as equivalent capability across families.
6. Apply the usage-budget gate from the catalog. Every spawned agent consumes its own model and tool usage. If Max or Ultra was not explicitly requested, explain the concrete benefit and obtain user confirmation before spawning it.
7. If the task remains hard to classify, read [references/routing-examples.md](references/routing-examples.md). Do not load it for an obvious route.
8. Spawn the minimum number of bounded assignments needed, each with objective, owned scope, interfaces, constraints, verification, and required evidence.
9. Keep the primary session responsible for synthesis and acceptance. Verify material claims, and escalate with a fresh stronger profile only when evidence shows the selected lane was insufficient.

## Guardrails

- Do not use Spark or Luna for broad-context synthesis, architecture, open-ended debugging, or high-risk decisions.
- Prefer Spark over GPT-5.6 when Spark scores `5` for the task and is exposed; if an implicit Spark route is unavailable, select the next suitable profile and report the change.
- Do not route to Sol merely because a task is large; use Terra when the architecture and acceptance criteria are already settled.
- Do not route to Terra by habit. The Artificial Analysis snapshot places Luna and Sol ahead of Terra on generic intelligence per dollar, so Terra must earn its place through repository execution, tool use, latency, or another task-specific advantage.
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
