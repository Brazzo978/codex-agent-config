---
name: route-subagents
description: Choose a GPT-6 Luna, Sol, or Astra custom-agent profile for explicit agent/model/effort requests or useful delegation.
---

# Route Subagents

Route only when the user explicitly requests an agent or delegation would materially improve speed, quality, context isolation, independent verification, or reliability. Honor an explicitly named exposed profile exactly. If it is unavailable, stop rather than substituting another model or effort.

## Local OpenCode worker

This lane is explicit opt-in only. Enter this section only when the user's current request explicitly asks for local Qwen, local OpenCode, or the local worker by name. Do not infer permission from a generic request for a subagent, task simplicity, free/unlimited usage, native quota pressure, or apparent task fit. Otherwise do not read the local-worker reference or call its MCP tools; route only among native Codex profiles.

When explicitly requested, read [references/local-worker.md](references/local-worker.md), then call `local_opencode_worker.start_task`. Pass the relevant workspace, explicit file paths, and an effort. Use `low` for deterministic execution with a settled design, `medium` for a single bounded implementation or debugging tranche that needs judgment, and `xhigh` only for exceptional hard or high-risk work; task size alone never justifies `xhigh`. Split broad multi-artifact goals into independently verifiable tranches instead of raising effort. Agent mode is the default and may inspect or modify the workspace, run commands, and use the user's configured OpenCode tools and MCP servers. Retain its `task_id`, inspect it with `get_task`, and use bounded `wait_task` calls until completion. Leave `timeout` omitted for the default run-until-terminal behavior; pass a positive timeout only when the user or task genuinely requires a hard wall-clock limit. Use `cancel_task` when its work is no longer needed. Invoke the bundled script only when MCP is unavailable.

This lane is a tool-backed pseudo-subagent, not a native `spawn_agent` profile. With the `llamacode` backend, the bridge creates or continues a persistent OpenCode session over SSH and runs each prompt in a named remote tmux job; OpenCode, its tools, files, and history live on the remote machine. Retain the returned `session_id` when continuation is useful, inspect compact remote messages through `get_task`/`wait_task`, and retrieve artifacts with `fetch_file`. The legacy `ollama` backend still launches OpenCode locally and sends only inference to Ollama. Give either backend a bounded outcome, the correct project/workspace, explicit files, and only the summarized context that changes execution; do not paste broad history or assume it knows the primary conversation. State known facts and completed checks so it does not rediscover them. Keep final synthesis, verification, acceptance, and escalation in the primary agent.

## Native route

Match the examples first. They set the workload family and the minimum capability. Then use [references/model-catalog.md](references/model-catalog.md) to select the lowest benchmark cost among compatible, available, ungated profiles that meet the capability floor and have the highest task-fit tier. Prefer the model family that naturally fits the task. The published USD costs are benchmark API costs, not Codex quota or credit values. Do not raise effort for document length, item count, or repetitive volume alone.

- Mechanical extraction, formatting, or identical repetition without judgment -> `luna_low`.
- Clear repeatable transformation, summary, translation, or rewrite -> `luna_medium`.
- Bounded deterministic work with familiar edge cases -> `luna_high`.
- Hard bounded deterministic work -> `luna_xhigh`.
- Demanding Luna-shaped work or uncertain but bounded edge cases -> `luna_max`.
- Small repository lookup or modest code judgment -> `sol_low`.
- Normal multi-file implementation, tests, review, debugging, architecture, or synthesis -> `sol_medium`.
- Difficult Sol-shaped work with multiple tradeoffs or plausible causes -> `sol_high`.
- Exceptional high-risk or cross-system Sol-shaped work -> `sol_xhigh`.
- Indivisible extreme Sol work that demonstrably needs more capability -> `sol_max`.
- A hardest end-to-end workflow where normal Sol routing is insufficient or Astra's cross-system fit is essential -> `astra_low`.
- Escalate Astra to `medium` only if Low is insufficient for the task.

Luna, Sol, and Astra Ultra require an explicit user request. Astra High, XHigh, and Max also require an explicit request. Keep Luna Max available for bounded tasks that need it. Start Astra at Low; do not select a more expensive Astra effort without a concrete capability reason. Luna XHigh scores 34 in the supplied benchmark, equal to Sol Low; Sol XHigh scores 44. Do not treat same effort labels across model families as equivalent capability.

If no example fits, choose Luna for clear and repeatable tasks, Sol for repository work or consequential judgment, and Astra for the hardest end-to-end workflows. Use the route table in the catalog. Explicit model and effort requests bypass cost optimization.

For every native Codex spawn:

- Set `task_name=<scope>_<model_code>_<effort_code>`; model codes `l/s/a`, effort codes `l/m/h/xh/mx/u`.
- Spawn the minimum number of bounded lanes; avoid overlapping ownership and redundant retries.
- Keep synthesis, verification, acceptance, and escalation in the primary agent.
