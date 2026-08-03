---
name: route-subagents
description: Dynamically select and spawn the best available Codex custom-agent model and reasoning profile for delegated work. Use whenever the user requests an agent, subagent, parallel work, model routing, a specific model or effort, or when delegation would materially improve speed, quality, context isolation, or independent verification.
---

# Route Subagents

Choose the model and effort before spawning. A running agent cannot switch its own model. Prefer the lowest-cost and fastest profile that can reliably complete the bounded assignment.

## Route

1. Read [references/model-catalog.md](references/model-catalog.md).
2. Inspect the native spawn tool's currently exposed agent types and model/effort overrides. Treat runtime exposure as authoritative.
3. If the user names a model, effort, or custom profile, use that exact route. If unavailable, report it; do not silently substitute.
4. Otherwise classify the task by required context, ambiguity, reasoning depth, risk, latency, and whether independent verification matters.
5. Select one installed `<model>_<effort>` profile using the catalog. Use the lowest sufficient effort.
6. Give the spawned agent one bounded objective, owned files or scope, constraints, verification, and required return evidence.
7. Inspect the result and verify material claims in the primary session. Escalate with a fresh, stronger profile only when evidence shows the first route was insufficient.

## Guardrails

- Use `spark_medium` only for near-instant, very small tasks with little context and limited reasoning needs.
- Do not use Luna or Spark for architecture, broad debugging, high-risk changes, or large-context synthesis.
- Use Max for exceptionally difficult single-agent reasoning. Use Ultra only when supported and useful for meaningfully parallel work.
- Keep the primary session responsible for requirements, routing, synthesis, verification, and acceptance.
- Never hide an unavailable profile, model mismatch, effort mismatch, failed lane, or fallback.
- Avoid parallel agents that edit the same files. Preserve user and concurrent edits.

## Invocation examples

```text
Use $route-subagents to delegate this task with the best available profile.
```

```text
Use $route-subagents with spark_medium for this tiny lookup.
```

```text
Use $route-subagents to split the independent work, then verify and consolidate every result.
```
