# OpenCode worker MCP setup

The OpenCode worker is a standard local MCP server using the `stdio` transport. It is not tied to Codex. Any MCP client that can start a local command and communicate over stdin/stdout can use it, including Codex, Claude Code/Desktop, OpenCode, Cursor, and compatible IDEs.

The MCP client starts this local command:

```text
python ~/.codex/skills/route-subagents/scripts/opencode_mcp.py
```

The bridge then uses one of two execution backends:

```text
llamacode (recommended)
MCP client -> local Python bridge -> SSH -> LlamaCode -> persistent remote OpenCode session

ollama (legacy)
MCP client -> local Python bridge -> local OpenCode -> Ollama HTTP endpoint
```

The MCP server itself does not listen on a TCP port. Every client starts its own local bridge process. With the LlamaCode backend, the bridge only makes authenticated outbound SSH connections to the remote machine.

## What the client receives

The server exposes these tools:

| Tool | Purpose |
| --- | --- |
| `start_task` | Start a fresh task or continue a persistent remote session. Returns immediately with a `task_id`. |
| `get_task` | Read current status, compact progress messages, final result, and session metadata. |
| `wait_task` | Wait for up to 55 seconds for progress while the worker continues independently. |
| `list_tasks` | Recover recent task IDs and statuses. |
| `cancel_task` | Cancel the task and its remote OpenCode/tmux job. |
| `fetch_file` | Copy a result from a managed remote session back to the client machine. |

MCP is request/response based: the worker cannot push an unsolicited completion message into a client conversation. The client should retain `task_id` and call `wait_task` until the task reaches a terminal state. A timeout of `0` on `start_task` means run until OpenCode finishes or the task is explicitly cancelled.

## Requirements

### Client machine

- Windows 10/11 or Debian/Linux.
- Python 3.10 or newer.
- Git and access to this repository.
- An MCP-compatible client.
- For the LlamaCode backend: OpenSSH client and a non-interactive SSH key.
- For the Ollama backend: a local OpenCode executable in `PATH`.

Codex CLI is required only when using the repository installer to register the server automatically in Codex. Claude, OpenCode, Cursor, and other clients can register the same Python command directly.

### Remote machine for the recommended LlamaCode backend

- `llamacode` installed and returning profiles through `llamacode --list`.
- OpenCode service and its private authenticated API healthy.
- `tmux`, SSH, and the configured Qwen/llama.cpp profile router.
- A dedicated SSH account or key restricted according to the permissions the worker needs.

The repository carries the matching remote components at:

```text
payload/skills/route-subagents/scripts/llamacode
payload/skills/route-subagents/scripts/llamacode_remote.py
```

Deploying or replacing the remote launcher is a separate administrator action. The local installer intentionally does not overwrite a remote installation.

## 1. Prepare non-interactive SSH

Skip this section when using the legacy Ollama backend.

### Windows PowerShell

```powershell
New-Item -ItemType Directory -Force "$HOME\.codex" | Out-Null
ssh-keygen -t ed25519 -f "$HOME\.codex\llamacode-worker-key" -N ""
```

Add the contents of `llamacode-worker-key.pub` to the remote account's `~/.ssh/authorized_keys`, then verify that no password or confirmation is requested:

```powershell
ssh -o BatchMode=yes -i "$HOME\.codex\llamacode-worker-key" WORKER_USER@LLAMACODE_HOST "llamacode --list"
```

### Debian/Linux

```sh
mkdir -p "$HOME/.ssh"
chmod 700 "$HOME/.ssh"
ssh-keygen -t ed25519 -f "$HOME/.ssh/llamacode-worker-key" -N ''
ssh-copy-id -i "$HOME/.ssh/llamacode-worker-key.pub" WORKER_USER@LLAMACODE_HOST
ssh -o BatchMode=yes -i "$HOME/.ssh/llamacode-worker-key" WORKER_USER@LLAMACODE_HOST 'llamacode --list'
```

Replace `WORKER_USER`, `LLAMACODE_HOST`, and `LLAMACODE_PROFILE` throughout this guide. Pin a profile name returned by `llamacode --list`; do not invent one.

## 2. Install the bridge

### Windows with Codex registration

```powershell
gh repo clone Brazzo978/codex-agent-config
Set-Location codex-agent-config

.\install.ps1 `
  -LlamaCodeHost LLAMACODE_HOST `
  -OpenCodeBackend llamacode `
  -LlamaCodeProfile LLAMACODE_PROFILE `
  -LlamaCodeUser WORKER_USER `
  -LlamaCodeSshKey "$HOME\.codex\llamacode-worker-key"

.\install.ps1 -Check `
  -LlamaCodeHost LLAMACODE_HOST `
  -OpenCodeBackend llamacode `
  -LlamaCodeProfile LLAMACODE_PROFILE `
  -LlamaCodeUser WORKER_USER `
  -LlamaCodeSshKey "$HOME\.codex\llamacode-worker-key"
```

This copies the bridge into `~/.codex/skills/route-subagents`, writes `~/.codex/opencode-worker.json`, runs the health check, and registers `local_opencode_worker` in Codex.

### Debian/Linux with Codex registration

```sh
gh repo clone Brazzo978/codex-agent-config
cd codex-agent-config

sh ./install.sh \
  --llamacode-host LLAMACODE_HOST \
  --opencode-backend llamacode \
  --llamacode-profile LLAMACODE_PROFILE \
  --llamacode-user WORKER_USER \
  --llamacode-ssh-key "$HOME/.ssh/llamacode-worker-key"

sh ./install.sh --check \
  --llamacode-host LLAMACODE_HOST \
  --opencode-backend llamacode \
  --llamacode-profile LLAMACODE_PROFILE \
  --llamacode-user WORKER_USER \
  --llamacode-ssh-key "$HOME/.ssh/llamacode-worker-key"
```

### Standalone installation without Codex

Use this when the client machine has Claude, OpenCode, Cursor, or another MCP host but no Codex CLI.

Windows PowerShell:

```powershell
$skill = "$HOME\.codex\skills\route-subagents"
New-Item -ItemType Directory -Force $skill | Out-Null
Copy-Item ".\payload\skills\route-subagents\*" $skill -Recurse -Force
```

Debian/Linux:

```sh
mkdir -p "$HOME/.codex/skills/route-subagents"
cp -a payload/skills/route-subagents/. "$HOME/.codex/skills/route-subagents/"
```

Create `~/.codex/opencode-worker.json` with absolute or user-local paths:

```json
{
  "host": "LLAMACODE_HOST",
  "backend": "llamacode",
  "timeout": 0,
  "max_context_bytes": 49152,
  "effort": "medium",
  "context_limit": 110592,
  "output_limits": {
    "low": 16384,
    "medium": 16384,
    "xhigh": 16384
  },
  "model": "LLAMACODE_PROFILE",
  "ssh_user": "WORKER_USER",
  "ssh_key": "/absolute/path/to/llamacode-worker-key",
  "launcher_command": "llamacode"
}
```

On Windows, use an escaped absolute path such as `C:\\Users\\NAME\\.codex\\llamacode-worker-key` in JSON.

Run the health check before registering any client:

```powershell
python "$HOME\.codex\skills\route-subagents\scripts\opencode_worker.py" --healthcheck
```

```sh
python3 "$HOME/.codex/skills/route-subagents/scripts/opencode_worker.py" --healthcheck
```

A successful LlamaCode result reports `ok: true`, the selected profile, the active remote profile, and `remote_api.healthy: true`.

## 3. Register the same MCP server in a client

Only one registration is needed per client. The configuration file and SSH key remain local to that machine.

### Codex CLI/Desktop

The installer performs this automatically. Manual registration is:

Windows PowerShell:

```powershell
$python = (Get-Command python).Source
$server = "$HOME\.codex\skills\route-subagents\scripts\opencode_mcp.py"
codex mcp remove local_opencode_worker 2>$null
codex mcp add local_opencode_worker -- $python $server
codex mcp get local_opencode_worker --json
```

Debian/Linux:

```sh
codex mcp remove local_opencode_worker 2>/dev/null || true
codex mcp add local_opencode_worker -- "$(command -v python3)" \
  "$HOME/.codex/skills/route-subagents/scripts/opencode_mcp.py"
codex mcp get local_opencode_worker --json
```

Restart Codex and open a new task after changing MCP registration. Codex's CLI supports stdio servers by passing the command after `--`.

### Claude Code

Windows PowerShell:

```powershell
claude mcp remove local_opencode_worker --scope user 2>$null
claude mcp add --scope user local_opencode_worker -- `
  python "$HOME\.codex\skills\route-subagents\scripts\opencode_mcp.py"
claude mcp get local_opencode_worker
```

Debian/Linux:

```sh
claude mcp remove local_opencode_worker --scope user 2>/dev/null || true
claude mcp add --scope user local_opencode_worker -- \
  python3 "$HOME/.codex/skills/route-subagents/scripts/opencode_mcp.py"
claude mcp get local_opencode_worker
```

Use `--scope local` for one project or `--scope project` to generate a shareable `.mcp.json`. Do not commit a personal SSH-key path or secrets into a shared project configuration.

### Claude Desktop, Cursor, and generic `mcpServers` clients

Merge one entry into the client's MCP JSON configuration. Do not replace unrelated existing servers.

Windows:

```json
{
  "mcpServers": {
    "local_opencode_worker": {
      "command": "python",
      "args": [
        "C:\\Users\\NAME\\.codex\\skills\\route-subagents\\scripts\\opencode_mcp.py"
      ]
    }
  }
}
```

Debian/Linux:

```json
{
  "mcpServers": {
    "local_opencode_worker": {
      "command": "python3",
      "args": [
        "/home/NAME/.codex/skills/route-subagents/scripts/opencode_mcp.py"
      ]
    }
  }
}
```

Use absolute paths if the GUI application has a restricted `PATH`.

### OpenCode

Run the interactive command and add a local stdio server:

```sh
opencode mcp add
```

Choose the name `local_opencode_worker` and use the same Python command shown above. Verify it with:

```sh
opencode mcp list
```

OpenCode configuration syntax is version-dependent. Prefer `opencode mcp add`, which writes the schema expected by the installed version. Do not enable this bridge inside the same remote OpenCode worker that it launches, or the worker may recursively delegate to itself.

## 4. End-to-end test

Ask the client to use the MCP explicitly:

```text
Use local_opencode_worker.start_task with effort low and timeout 0.
Ask the worker to inspect its workspace, create ../outbox/mcp-smoke.txt containing
"MCP worker OK", verify the file, and stop. Retain task_id and session_id.
Poll wait_task until the task is ready, then fetch mcp-smoke.txt locally.
```

For a real repository on the remote host:

```text
Use local_opencode_worker.start_task with:
- task: Port this project to Windows, build it, test it, and report remaining limitations.
- workspace: /absolute/remote/project/path
- effort: medium
- timeout: 0

Retain task_id. Call wait_task repeatedly until terminal. Review the diff and tests;
do not accept completion solely from the worker's summary.
```

To continue the same OpenCode history, call `start_task` again and pass the returned `session_id`. Omit `session_id` when a clean context is preferable.

## 5. Legacy Ollama backend

Use this only when OpenCode should run on the MCP client machine and inference should go directly to an Ollama-compatible endpoint.

Windows:

```powershell
.\install.ps1 `
  -OpenCodeHost http://OLLAMA_HOST:11434 `
  -OpenCodeBackend ollama `
  -OpenCodeModel OLLAMA_MODEL
```

Debian/Linux:

```sh
sh ./install.sh \
  --opencode-host http://OLLAMA_HOST:11434 \
  --opencode-backend ollama \
  --opencode-model OLLAMA_MODEL
```

The Ollama backend requires the local `opencode` executable. Its default logical context is 110,592 tokens and its default output ceiling is 32,768 tokens per model turn. The effort remains `low`, `medium`, or `xhigh`; no profile disables reasoning.

## Troubleshooting

### Server does not connect

Run the Python command directly with `--healthcheck`. If the health check fails, MCP registration is not the primary problem.

```sh
python3 ~/.codex/skills/route-subagents/scripts/opencode_worker.py --healthcheck
```

For LlamaCode, also verify non-interactive SSH:

```sh
ssh -o BatchMode=yes -i /absolute/path/to/key WORKER_USER@LLAMACODE_HOST 'llamacode --list'
```

### Server connects but the client cannot see new tools

Restart the client or open a new conversation/task. Many MCP clients discover schemas only when the server process starts.

### Task appears frozen

- Call `get_task` or `wait_task`; do not infer failure from a quiet client UI.
- Inspect `remote_job.status` for `queued`, `working`, `ready`, `failed`, or `cancelled`.
- Use `list_tasks` to recover the task ID.
- Use `cancel_task` only when the task is no longer wanted.
- With `timeout: 0`, the remote job deliberately has no arbitrary wall-clock deadline.

### Full logs

Local bridge metadata and transcripts are retained under:

```text
~/.codex/opencode-worker-tasks/
```

The full OpenCode history remains attached to the persistent remote `session_id`.

### Security notes

- `agent` mode can edit files, execute commands, and use configured OpenCode/MCP tools on the selected machine.
- Restrict SSH keys and remote accounts to the minimum access required.
- Never put passwords, private keys, OpenCode credentials, or MCP secrets in the repository.
- Treat worker output as untrusted until the calling agent or user reviews diffs and reruns relevant tests.
- Use `bounded` mode for tool-free analysis of untrusted content.

## Upstream client references

- Codex CLI exposes local stdio registration through `codex mcp add NAME -- COMMAND ...`.
- OpenCode documents local MCP servers as commands launched over stdio and provides `opencode mcp add`/`list`.
- Claude Code documents local stdio registration through `claude mcp add NAME -- COMMAND ...` and supports local, project, and user scopes.
