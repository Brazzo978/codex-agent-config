# Codex agent configuration

Private, portable configuration for the Codex desktop app and CLI. It installs:

- 19 custom-agent profiles: GPT-5.6 Sol, Terra, and Luna across six effort levels, plus GPT-5.3 Codex Spark / Medium;
- the `route-subagents` personal skill with task-fit, cost-performance, quota, escalation, and fallback rules;
- a managed routing block in the user's global `AGENTS.md`.

The installer never copies `auth.json`, sessions, databases, logs, MCP secrets, or the machine-specific `config.toml`.

## Windows quick install

Prerequisites: Git and access to this private GitHub repository.

```powershell
gh repo clone Brazzo978/codex-agent-config
Set-Location codex-agent-config
.\install.ps1
.\install.ps1 -Check
```

If GitHub CLI is unavailable, clone the private repository using Git Credential Manager and run the same installer.

## macOS or Linux quick install

```sh
gh repo clone Brazzo978/codex-agent-config
cd codex-agent-config
sh ./install.sh
sh ./install.sh --check
```

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
- Other custom agents and skills are not removed.
- Existing global `AGENTS.md` content is preserved outside the managed routing markers.
- `-Check` or `--check` is read-only and exits nonzero if the installed bundle is missing or differs.

If an explicitly requested model or effort is unavailable to the current account or runtime, the router stops instead of silently selecting another profile.

The router preserves the canonical capability hierarchy `Sol > Terra > Luna > Spark`, with expected speed and cost efficiency generally running in the inverse direction. It prefers Spark for eligible self-contained microtasks because Spark has a separate usage limit. The dated Artificial Analysis Intelligence Index/cost snapshot is only a secondary efficiency signal after family capability and task fit; it cannot justify down-tiering. Max and Ultra require confirmation before automatic use.

## Ask Codex to install it

On a computer already authenticated to GitHub, give Codex the repository URL and say:

```text
Clone this private repository, inspect its README and installer, run the installer for this operating system, verify it in check mode, then tell me whether I must restart the app.
```
