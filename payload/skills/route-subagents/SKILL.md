---
name: route-subagents
description: Dynamically choose and spawn the best available Codex custom-agent model and reasoning profile. Use for every explicit agent, subagent, parallel-work, model, or effort request, and whenever delegation would materially improve speed, quality, context isolation, independent verification, or long-task reliability.
---

# Route Subagents

Honor an explicit profile exactly. If unavailable, stop.

## Local OpenCode worker

This lane is explicit opt-in only. Enter this section only when the user's current request explicitly asks for local Qwen, local OpenCode, or the local worker by name. Do not infer permission from a generic request for a subagent, task simplicity, free/unlimited usage, native quota pressure, or apparent task fit. Otherwise do not read the local-worker reference or call its MCP tools; route only among native Codex profiles.

When explicitly requested, read [references/local-worker.md](references/local-worker.md), then call `local_opencode_worker.start_task`. Pass the relevant workspace, explicit file paths, and an effort. Use `low` for deterministic execution with a settled design, `medium` for a single bounded implementation or debugging tranche that needs judgment, and `xhigh` only for exceptional hard or high-risk work; task size alone never justifies `xhigh`. Split broad multi-artifact goals into independently verifiable tranches instead of raising effort. Agent mode is the default and may inspect or modify the workspace, run commands, and use the user's configured OpenCode tools and MCP servers. Retain its `task_id`, inspect it with `get_task`, and use bounded `wait_task` calls until completion. Leave `timeout` omitted for the default run-until-terminal behavior; pass a positive timeout only when the user or task genuinely requires a hard wall-clock limit. Use `cancel_task` when its work is no longer needed. Invoke the bundled script only when MCP is unavailable.

This lane is a tool-backed pseudo-subagent, not a native `spawn_agent` profile. With the `llamacode` backend, the bridge creates or continues a persistent OpenCode session over SSH and runs each prompt in a named remote tmux job; OpenCode, its tools, files, and history live on the remote machine. Retain the returned `session_id` when continuation is useful, inspect compact remote messages through `get_task`/`wait_task`, and retrieve artifacts with `fetch_file`. The legacy `ollama` backend still launches OpenCode locally and sends only inference to Ollama. Give either backend a bounded outcome, the correct project/workspace, explicit files, and only the summarized context that changes execution; do not paste broad history or assume it knows the primary conversation. State known facts and completed checks so it does not rediscover them. Keep final synthesis, verification, acceptance, and escalation in the primary agent.

## Simple routing examples

Match these first to establish workload, baseline profile, and minimum intelligence. Then apply the catalog's cost optimization even when an example fits.

- One command, syntax answer, tiny obvious fix, or narrow lookup with all required context already small and local -> `spark_medium`.
- Purely mechanical extraction, classification, formatting, or identical repetition with no judgment -> `luna_low`.
- Clear repeatable transformation or structured summary requiring a few checks -> `luna_medium`.
- A simple ten-page description, summary, translation, or rewrite with clear instructions -> `luna_medium`. Length alone does not require Terra or Sol.
- A bounded deterministic task with important but familiar edge cases -> `luna_high`.
- An unusually hard but still bounded deterministic task -> `luna_xhigh`.
- A Luna-shaped task not positively classified as simple -> `luna_max`.
- Normal multi-file repository work, implementation, tests, review, or debugging with a settled objective -> `terra_high`.
- Subtle or high-risk execution with a settled design -> `terra_xhigh`.
- Complex implementation or investigation with settled architecture -> `terra_max`.
- Architecture, strategy, unresolved ambiguity, consequential judgment, or polished synthesis -> `sol_medium`.
- Difficult Sol-shaped work with multiple tradeoffs -> `sol_high`.
- Exceptional cross-system or high-risk Sol-shaped work -> `sol_xhigh`.
- Ultra-complex indivisible Sol work -> ask before `sol_max`. Use `sol_ultra` only when explicitly requested.
- A hardest end-to-end workflow whose capability need reaches roughly `sol_max`, especially across systems, tools, or disciplines -> `astra_low` only when Sol is insufficient or Astra's fit matters.
- Escalate Astra to `medium` only when Low lacks depth. `astra_high`, `astra_xhigh`, `astra_max`, and `astra_ultra` require an explicit user request.

If no example fits, choose the family by the dominant need: clear/repeatable -> Luna; repository/tools -> Terra; ambiguity/judgment -> Sol; hardest end-to-end work near Sol Max capability -> Astra Low. Then load `references/model-catalog.md` and use its route table. For every scored implicit profile, treat the baseline Intelligence Index as a floor: exclude incompatible, under-floor, or gated profiles; retain the highest workload-fit tier; then choose its lowest published task cost, using intelligence only as a tie-breaker. If the best-fit baseline cost is unpublished, preserve it instead of estimating. Never trade away natural task fit merely to reduce benchmark cost. Spark, Ultra, and explicitly named profiles bypass numeric optimization and remain exact.

Spark has a hard context-fit gate: reject it for multi-file context, long documents, broad conversation history, many tool traces, or cross-source synthesis. If the task or required context grows, escalate once to Luna, Terra, or Sol; do not retry the unsuitable Spark lane.

For every native Codex spawn:

- Apply Max/Ultra gates from the catalog.
- Set `task_name=<scope>_<model_code>_<effort_code>`; codes: models `sp/l/t/s/a`, efforts `l/m/h/xh/mx/u`.
- Spawn the minimum bounded lanes; avoid overlapping ownership and redundant retries.
- Keep synthesis, verification, acceptance, and escalation in the primary agent.
