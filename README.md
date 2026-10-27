# Codex agent configuration

Private, portable configuration for the Codex desktop app and CLI. It installs:

- 24 custom-agent profiles: GPT-6 Luna, GPT-6.1 Terra, GPT-6.1 Sol, and GPT-6 Astra across six effort levels;
- the `route-subagents` personal skill with task-fit, cost-performance, quota, escalation, and fallback rules;
- an optional OpenCode/Qwen worker that can run either through local OpenCode + Ollama or through persistent remote LlamaCode/OpenCode sessions over SSH;
- a managed routing block in the user's global `AGENTS.md`.

The installer never copies `auth.json`, sessions, databases, logs, or MCP secrets. Supplying a worker host writes `~/.codex/opencode-worker.json` and registers the local stdio MCP server in `config.toml`; it does not expose OpenCode on the network or change the user's OpenCode configuration. An existing `config.toml` is backed up before registration.

For installation in Codex, Claude Code/Desktop, OpenCode, Cursor, or another stdio MCP client, see [OpenCode worker MCP setup](docs/opencode-worker-mcp-setup.md).

## Windows quick install

Prerequisites: Git and access to this GitHub repository.

```powershell
gh repo clone Brazzo978/codex-agent-config
Set-Location codex-agent-config
.\install.ps1
.\install.ps1 -OpenCodeHost 127.0.0.1
.\install.ps1 -LlamaCodeHost 10.10.10.115 -OpenCodeBackend llamacode -LlamaCodeProfile qwen38-remote-q4-216k -LlamaCodeSshKey "$HOME\.codex\llamacode-worker-key"
.\install.ps1 -Check
```

If GitHub CLI is unavailable, clone the repository with Git and run the same installer.

## macOS or Linux quick install

```sh
gh repo clone Brazzo978/codex-agent-config
cd codex-agent-config
sh ./install.sh
sh ./install.sh --opencode-host 10.10.10.115
sh ./install.sh --check
```

## Free OpenCode/Qwen worker

The worker supports two execution backends:

```text
ollama:    Codex -> local OpenCode -> Ollama endpoint
llamacode: Codex -> local MCP bridge -> SSH -> named tmux job -> private OpenCode API/tools/Qwen
```

Codex can give the worker a task, workspace path, explicit file paths, and an effort (`low`, `medium`, or `xhigh`). Effort defaults to `medium`; `xhigh` is reserved for exceptional hard or high-risk work. Default `agent` mode loads the relevant local or remote OpenCode configuration and may inspect or edit the workspace, run commands and tests, and use configured OpenCode/MCP tools. Optional `bounded` mode remains isolated and tool-free with its original eight-file/48 KiB cap. The primary Codex agent remains responsible for scope, verification, and synthesis.

The local worker is explicit opt-in only: Codex must use it only when the user's current request names local Qwen, local OpenCode, or the local worker. Generic subagent requests and automatic cost/task-fit routing stay on native Codex profiles.

For the `ollama` backend, the host may be an IP or a full URL and the model comes from `/api/tags`. For `llamacode`, the host is an SSH hostname/IP, the profile comes from `llamacode --list`, and the bridge requires non-interactive SSH authentication. MCP tasks are restricted to `qwen38-remote-*` profiles; the interactive launcher uses `qwen38-agent-*`. Use `-LlamaCodeProfile` / `--llamacode-profile` to pin the remote profile.

LlamaCode has two modes. Running `llamacode` interactively shows the currently loaded router profile, asks for agent model/effort and new/resume, then creates or attaches to a named tmux TUI session. `llamacode remote ...` is the machine-facing contract used by MCP: create/run/continue/status/messages/cancel persistent OpenCode sessions. Both modes use full agent permissions; bounded MCP mode denies tools.

Every remote session owns `/srv/llamacode/sessions/<name>/` with `workspace`, `inbox`, `outbox`, and `logs`. With no project option, `workspace` is isolated. Supplying an existing remote project makes `workspace` a link to it while inbox/outbox/logs remain isolated. Local context files are uploaded and staged into the session inbox. Use the returned `session_id` in a later `start_task` to continue the same OpenCode history, and use `fetch_file` to download a result from the managed session directory.

The matching VPS components are versioned as `scripts/llamacode` and `scripts/llamacode_remote.py` inside the installed skill. Deploy them as `/usr/local/bin/llamacode` and `/usr/local/lib/llamacode/remote.py` after backing up an existing launcher. They expect OpenCode at `/root/.opencode/bin/opencode`, an authenticated `opencode.service` on private localhost port 4096, tmux, and the Qwen profile router on 11434. The local installer intentionally does not overwrite a remote launcher automatically.

Health check without inference:

```powershell
python "$HOME\.codex\skills\route-subagents\scripts\opencode_worker.py" --healthcheck
```

The installer registers `opencode_mcp.py` as `local_opencode_worker`. Its lifecycle mirrors a subagent: `start_task` returns immediately, `get_task`/`wait_task` show compact live OpenCode messages and the final result, `list_tasks` recovers task IDs, `cancel_task` aborts the remote OpenCode session and tmux job, and `fetch_file` downloads a session artifact. Timeout `0` is the default, so the remote task runs until OpenCode completes or is cancelled; pass a positive number of seconds only for an explicit hard limit. Each LlamaCode job keeps a persistent `status.json` with `queued`, `working`, `ready`, `failed`, or `cancelled`, and `get_task` exposes it as `remote_job`. Completed local metadata and raw bridge transcripts persist under `~/.codex/opencode-worker-tasks/`; the full OpenCode history remains in the persistent remote session. MCP cannot call Codex unsolicited, so the orchestrator loops through bounded `wait_task` calls while Qwen continues independently.

The legacy Ollama backend uses a 110,592-token logical context and a 32,768-token output ceiling by default. The LlamaCode installer profile uses a 16,384-token bridge output ceiling while the chosen remote launcher profile owns the real context window. Low, medium, and xhigh select reasoning effort rather than disabling reasoning. Override `context_limit` or `output_limits` in `~/.codex/opencode-worker.json` when a deployment genuinely needs different bounds.

The Ollama backend uses an in-memory OpenCode session database and isolated volatile state. The LlamaCode backend talks through the authenticated OpenCode server already running on the VPS; its credential never enters the repository or local worker config. Agent mode loads the corresponding OpenCode configuration and configured MCP tools.

In agent mode, the worker may install the smallest operating-system package that provides a Bash command required by its assigned task. It checks that the command is actually missing, uses noninteractive package installation, avoids speculative dependencies or disruptive replacements, and reports every installed package. Bounded mode remains tool-free and never installs packages.

When the Ollama backend's local models catalog cache exists, the worker pins startup to that file instead of refreshing `models.dev` for every task.

The OpenCode child receives a closed stdin so it cannot consume or wait on the parent MCP server's JSON-RPC input stream.

Task metadata records its owning MCP process. Opening another Codex task no longer marks work owned by an already-running MCP instance as failed.

## Update an existing computer

```powershell
git pull --ff-only
.\install.ps1
```

```sh
git pull --ff-only
sh ./install.sh
```

Restart the Codex desktop app and start a new task after installation or update. Custom-agent types are discovered when a task is created.

## Safety behavior

- Missing managed files are installed.
- Identical files are left untouched.
- Differing managed files are backed up beneath `~/.codex/backups/codex-agent-config/<timestamp>/` before replacement.
- Obsolete files previously managed by this bundle are backed up before removal.
- Other custom agents and skills are not removed.
- Existing global `AGENTS.md` content is preserved outside the managed routing markers.
- `-Check` or `--check` is read-only and exits nonzero if the installed bundle is missing or differs.

If an explicitly requested model or effort is unavailable to the current account or runtime, the router stops instead of silently selecting another profile.

The router uses the user's Artificial Analysis v4.3.2 charts dated 27 October 2026, with current scores and task costs for GPT-6 Luna, GPT-6.1 Terra, and GPT-6.1 Sol. The account preference is free Luna and a Terra tariff equal to half Sol's for the same usage. Luna covers bounded work, Terra covers normal repository execution, and Sol handles higher capability requirements. The numeric catalog is stored in one JSON file; the bundled resolver preserves capability floors and applies task fit, availability, and explicit-only gates before cost selection.

For paid candidates the router compares full benchmark task costs as a proxy, because more tokens can offset a lower tariff. For example, Terra Max and Sol Medium both score 48, but the supplied costs are $0.40 and $0.21 per benchmark task, so Sol Medium wins when both fit. Terra High scores 44 at $0.13, ahead of Sol Low's 42 at the same measured cost. These figures are not a Codex quota forecast. Astra Low/Medium are available for exceptionally difficult specialized workflows and brief advisor questions. Higher Astra profiles and all Ultra profiles require an explicit request. Sol Max needs a demonstrated indivisible extreme need.

Advisor mode is optional and independent of the executor's model. Use it when focused attempts are failing to resolve a concrete bug, unexplained behavior, or difficult GUI/design blocker, or when the user directly requests a second opinion. It is not a routine response to every uncertainty or planning step. Sol is the usual advisor; Astra Low/Medium are available when the question justifies their specialized fit. The advisor provides a short opinion without implementing, editing files, or spawning more agents; the primary owns the decision.

The installer replaces older Luna/Sol/Terra profiles under the same managed filenames with backups, removes the obsolete managed Spark file, and preserves unrelated agents and AGENTS.md content outside the managed block.

Check routing decisions without making model calls:

```sh
python payload/skills/route-subagents/scripts/select_profile.py --workload execution --difficulty normal
python payload/skills/route-subagents/scripts/select_profile.py --workload execution --difficulty complex
python payload/skills/route-subagents/scripts/select_profile.py --mode advisor --stalled-on "Both attempted navigation layouts still fail the usability constraint" --consult-reason "Which constraint should I reconsider?"
python -m unittest discover -s payload/skills/route-subagents/tests -p test_route_catalog.py
```

## Ask Codex to install it

On a computer already authenticated to GitHub, give Codex the repository URL and say:

```text
Clone this private repository, inspect its README and installer, run the installer for this operating system, verify it in check mode, then tell me whether I must restart the app.
```
