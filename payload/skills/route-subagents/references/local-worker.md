# Local OpenCode worker

Use this lane only when the user's current request explicitly asks for local Qwen, local OpenCode, or the local worker by name. Do not select it automatically for a generic subagent request, a simple task, free/unlimited usage, native quota pressure, or apparent fitness. Once explicitly selected, it can handle repository inspection, edits, commands, tests, extraction, formatting, and independent investigation from the task, workspace, files, and summarized context supplied by the orchestrator. The primary agent remains responsible for choosing the scope and verifying completion.

The worker has two backends. `llamacode` is the recommended remote-agent backend: the local MCP bridge opens non-interactive SSH connections to persistent OpenCode sessions and runs each task in a named tmux job, so OpenCode, its tools, plugins, MCP servers, model router, history, and workspace all remain on the remote machine. `ollama` is the legacy backend: OpenCode runs on the current computer and only inference goes to the configured Ollama endpoint. The default `agent` mode grants full OpenCode permissions and therefore may read, edit, execute commands, start OpenCode subagents, access configured MCP tools, or affect files in the supplied workspace. Use `bounded` mode when a tool-free isolated response is desired.

Prefer the asynchronous MCP lifecycle when it is registered:

```text
local_opencode_worker.start_task -> task_id
local_opencode_worker.get_task / wait_task -> progress, events, result
local_opencode_worker.cancel_task
local_opencode_worker.list_tasks
local_opencode_worker.fetch_file
```

`start_task` accepts `task`, optional remote `workspace`/project, optional local `context_files`, optional remote `session_id`, `mode`, `effort`, and `timeout`, then returns immediately. Timeout `0` is the default and lets OpenCode work until it reaches a terminal state; pass a positive number of seconds only when a hard wall-clock limit is required. Omit `session_id` for a fresh persistent session; pass one returned by an earlier task to continue its history. OpenCode runs in a background queue, with one active
inference at a time. `get_task` exposes recent compact OpenCode events and the absolute transcript
path; `wait_task` provides the subagent-like "return when done" loop. MCP cannot initiate an
unsolicited call into Codex, so the orchestrator calls `wait_task` until the task reaches a
terminal state. Do not add an arbitrary timeout merely to make `wait_task` bounded; each individual wait is already bounded while the remote task continues. `fetch_file` copies one artifact from the managed remote session directory back to the local computer. LlamaCode writes each remote job's persistent `status.json` under its session log directory and exposes `queued`, `working`, `ready`, `failed`, or `cancelled` through `get_task` as `remote_job`.

Effort is deliberately narrow:

- `low`: deterministic execution with a settled design, including a small implementation tranche, extraction, or one-pass checks. It maps directly to Ollama `reasoning_effort: low`; it is not a no-thinking or instant profile.
- `medium`: a single bounded repository implementation or debugging tranche that genuinely needs judgment.
- `xhigh`: exceptional hard or high-risk work only. Do not select it because a task is long, multi-file, or merely important.

Do not encode a broad milestone as one worker request. Split it into independently verifiable tranches with a concrete artifact and stopping condition, and keep the same or lower effort. If a run exhausts its output budget in reasoning without acting, treat it as a failed tranche: narrow the brief and lower effort rather than immediately increasing the token cap.

The legacy Ollama backend advertises a 110,592-token logical context and allows up to 32,768 output tokens per turn by default. The LlamaCode installer profile uses a more conservative 16,384-token output ceiling and lets the selected remote profile own its actual context window. `low`, `medium`, and `xhigh` change reasoning effort, not whether reasoning is enabled. These local bridge limits can be overridden in `~/.codex/opencode-worker.json` with `context_limit` and `output_limits`.

Otherwise invoke the bundled client:

```powershell
python scripts/opencode_worker.py --mode agent --effort medium --workspace "<repo>" --task "<task>" --context-file "<path>"
```

For the remote persistent-session backend, configure a non-interactive SSH key and remote LlamaCode host/profile. The optional workspace parameter links an existing remote project into the otherwise isolated session workspace:

```powershell
.\install.ps1 -LlamaCodeHost 10.10.10.115 -OpenCodeBackend llamacode `
  -LlamaCodeProfile qwen38-remote-q4-216k `
  -LlamaCodeSshKey "$HOME\.codex\llamacode-worker-key"
```

```sh
sh ./install.sh --llamacode-host 10.10.10.115 --opencode-backend llamacode \
  --llamacode-profile qwen38-remote-q4-216k \
  --llamacode-ssh-key "$HOME/.ssh/llamacode-worker-key"
```

For `llamacode`, the profile is selected from `llamacode --list`; for `ollama`, the model is selected from `/api/tags`. Pass the installer profile/model option when selection must be fixed. Run `python scripts/opencode_worker.py --healthcheck` to verify SSH or Ollama reachability and selection without starting inference.

Operating guidance:

- Write a bounded execution brief: desired artifact, owned files/workspace, known facts, checks already completed, verification expected, and a clear stopping condition. Do not paste broad conversation history.
- Tell the worker to act after one targeted reconnaissance pass and within three tool calls. Do not ask it to "investigate everything", redesign unrelated architecture, pre-plan later tranches, or keep going without a stopping condition.
- Avoid attaching raw decompiler dumps, full API responses, large logs, or whole files when a filtered excerpt or path lets the worker inspect only what it needs.
- Agent mode has no artificial file-count or byte cap. With `llamacode`, each session owns `/srv/llamacode/sessions/<name>/{workspace,inbox,outbox,logs}`. An optional `workspace` argument is an absolute existing project path on the remote machine and is linked as the session workspace. Explicit local context files are uploaded and staged into the inbox; ask the worker to put return artifacts in `../outbox`.
- Agent mode is powerful: its OpenCode permission is `allow`, including shell, edits, external directories, and configured MCP tools. Delegate only actions already authorized by the user.
- In agent mode, a missing Bash command needed for the assigned task is not by itself a blocker. The worker confirms the command is absent, installs only the smallest providing OS package noninteractively, refreshes package metadata only if needed, and reports what it installed. It must not install speculative packages or proceed through package removals, unknown repositories, or missing credentials; those conditions return `needs_context`. Bounded mode never installs anything.
- Treat output and workspace changes as work requiring primary-agent review. Verify facts, calculations, diffs, tests, and completion claims.
- Use `bounded` mode for untrusted content or when tools and side effects are unnecessary; bounded mode retains the eight-file/48 KiB limits.
- If the worker fails, asks for missing context, or returns an invalid result, retry once only when the correction is obvious; otherwise use a native Codex profile.
- Do not use this lane when wall-clock latency matters more than native-model usage.

To expose the same client as a Codex MCP server, register `scripts/opencode_mcp.py` as a local stdio MCP command. Task state and full event transcripts are retained under `~/.codex/opencode-worker-tasks/`; the server opens outbound SSH or HTTP connections but does not expose OpenCode, LlamaCode, or Ollama to the network.

The Ollama backend uses an in-memory OpenCode session database and task-local volatile state. The LlamaCode backend uses the authenticated private OpenCode API on the VPS and never copies its server password locally. Agent mode reads the corresponding local or remote OpenCode configuration, tools, plugins, and MCP definitions. Progress returned through MCP includes compact remote OpenCode messages; complete remote history remains attached to the returned `session_id`.

If OpenCode's cached `models.json` catalog exists, the worker uses it through `OPENCODE_MODELS_PATH` so task startup does not wait on a fresh `models.dev` request.
