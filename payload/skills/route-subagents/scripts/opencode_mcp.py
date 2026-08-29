#!/usr/bin/env python3
"""Async stdio MCP bridge for local or persistent remote OpenCode workers."""

from __future__ import annotations

import json
import os
import posixpath
import sys
import threading
import time
import uuid
from concurrent.futures import Future, ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from opencode_worker import (
    DEFAULT_CONFIG,
    DEFAULT_EFFORT,
    DEFAULT_MAX_CONTEXT_BYTES,
    DEFAULT_TIMEOUT,
    MAX_TIMEOUT,
    EFFORTS,
    WorkerError,
    delegate,
    download_remote_file,
    load_config,
    normalize_effort,
    normalize_timeout,
    resolve_backend,
    resolve_limits,
    run_remote,
)

TERMINAL = {"completed", "failed", "cancelled"}
MAX_EVENT_STRING_CHARS = 2_000


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def process_alive(pid: Any) -> bool:
    try:
        value = int(pid)
    except (TypeError, ValueError):
        return False
    if value <= 0:
        return False
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        kernel32.OpenProcess.restype = wintypes.HANDLE
        kernel32.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        kernel32.WaitForSingleObject.restype = wintypes.DWORD
        kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
        kernel32.CloseHandle.restype = wintypes.BOOL
        handle = kernel32.OpenProcess(0x00100000, False, value)  # SYNCHRONIZE
        if not handle:
            return ctypes.get_last_error() == 5  # ERROR_ACCESS_DENIED means it exists.
        try:
            return kernel32.WaitForSingleObject(handle, 0) == 0x00000102  # WAIT_TIMEOUT
        finally:
            kernel32.CloseHandle(handle)
    try:
        os.kill(value, 0)
        return True
    except PermissionError:
        return True
    except (OSError, TypeError, ValueError):
        return False


def send(payload: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")
    sys.stdout.flush()


def rpc_result(request_id: Any, value: Any) -> None:
    send({"jsonrpc": "2.0", "id": request_id, "result": value})


def rpc_error(request_id: Any, code: int, message: str) -> None:
    send({"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}})


def text_result(value: Any, is_error: bool = False) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "content": [{"type": "text", "text": json.dumps(value, ensure_ascii=False)}]
    }
    if is_error:
        payload["isError"] = True
    return payload


def compact_event(value: Any, maximum: int = MAX_EVENT_STRING_CHARS) -> Any:
    """Keep MCP progress useful without replaying huge tool outputs into Codex context."""
    if isinstance(value, str):
        if len(value) <= maximum:
            return value
        omitted = len(value) - maximum
        return value[:maximum] + f"\n...[truncated {omitted} chars; see transcript_path]"
    if isinstance(value, list):
        return [compact_event(item, maximum) for item in value]
    if isinstance(value, dict):
        return {key: compact_event(item, maximum) for key, item in value.items()}
    return value


class TaskRegistry:
    def __init__(self) -> None:
        config_path = Path(os.getenv("OPENCODE_WORKER_CONFIG", DEFAULT_CONFIG))
        self.config = load_config(config_path)
        configured_root = os.getenv("OPENCODE_WORKER_TASKS_DIR") or self.config.get("tasks_dir")
        self.root = Path(configured_root or (Path.home() / ".codex" / "opencode-worker-tasks"))
        self.root.mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()
        self.changed = threading.Condition(self.lock)
        self.tasks: dict[str, dict[str, Any]] = {}
        self.cancel_events: dict[str, threading.Event] = {}
        self.futures: dict[str, Future[Any]] = {}
        # Match the common OLLAMA_NUM_PARALLEL=1 configuration and queue extra jobs.
        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="opencode-worker")
        self._load_history()

    def _task_dir(self, task_id: str) -> Path:
        return self.root / task_id

    def _meta_path(self, task_id: str) -> Path:
        return self._task_dir(task_id) / "meta.json"

    def _save(self, task_id: str) -> None:
        path = self._meta_path(task_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(".tmp")
        temporary.write_text(
            json.dumps(self.tasks[task_id], ensure_ascii=False, indent=2), encoding="utf-8"
        )
        temporary.replace(path)

    def _load_history(self) -> None:
        for path in self.root.glob("*/meta.json"):
            try:
                meta = json.loads(path.read_text(encoding="utf-8"))
                task_id = str(meta["task_id"])
                self.tasks[task_id] = meta
                if meta.get("status") in {"queued", "running"}:
                    owner_pid = meta.get("owner_pid")
                    if not owner_pid or not process_alive(owner_pid):
                        meta.update(
                            status="failed",
                            finished_at=utc_now(),
                            error="MCP server stopped before this task finished",
                        )
                        self._save(task_id)
            except (OSError, ValueError, KeyError, TypeError):
                continue

    def start(self, arguments: dict[str, Any]) -> dict[str, Any]:
        task = str(arguments.get("task", "")).strip()
        if not task:
            raise WorkerError("task must not be empty")
        context_files = arguments.get("context_files", [])
        if not isinstance(context_files, list) or not all(isinstance(item, str) for item in context_files):
            raise WorkerError("context_files must be an array of paths")
        mode = str(arguments.get("mode", "agent"))
        if mode not in {"agent", "bounded"}:
            raise WorkerError("mode must be agent or bounded")
        workspace = arguments.get("workspace")
        if workspace is not None and not isinstance(workspace, str):
            raise WorkerError("workspace must be a directory path")
        session_id = arguments.get("session_id")
        if session_id is not None and not isinstance(session_id, str):
            raise WorkerError("session_id must be a string")
        timeout = normalize_timeout(arguments.get("timeout", self.config.get("timeout", DEFAULT_TIMEOUT)))
        effort = normalize_effort(arguments.get("effort", self.config.get("effort", DEFAULT_EFFORT)))
        context_limit, output_limit = resolve_limits(self.config, effort)

        task_id = f"ocw_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        meta = {
            "task_id": task_id,
            "status": "queued",
            "task": task,
            "context_files": context_files,
            "mode": mode,
            "workspace": workspace,
            "session_id": session_id,
            "inbox": None,
            "outbox": None,
            "job_name": None,
            "status_file": None,
            "timeout_seconds": timeout,
            "effort": effort,
            "backend": str(os.getenv("OPENCODE_WORKER_BACKEND") or self.config.get("backend", "auto")),
            "context_limit": context_limit,
            "output_limit": output_limit,
            "owner_pid": os.getpid(),
            "created_at": utc_now(),
            "started_at": None,
            "finished_at": None,
        }
        cancel_event = threading.Event()
        with self.changed:
            self.tasks[task_id] = meta
            self.cancel_events[task_id] = cancel_event
            self._save(task_id)
            self.futures[task_id] = self.executor.submit(self._run, task_id, cancel_event)
            self.changed.notify_all()
        return self.snapshot(task_id, tail_events=0)

    def _run(self, task_id: str, cancel_event: threading.Event) -> None:
        with self.changed:
            meta = self.tasks[task_id]
            if cancel_event.is_set():
                meta.update(status="cancelled", finished_at=utc_now(), error="cancelled before start")
                self._save(task_id)
                self.changed.notify_all()
                return
            meta.update(status="running", started_at=utc_now())
            self._save(task_id)
            self.changed.notify_all()

        task_dir = self._task_dir(task_id)
        try:
            host = os.getenv("OPENCODE_WORKER_HOST") or self.config.get("host")
            if not host:
                raise WorkerError("OpenCode worker host is not configured")
            def record_remote_session(info: dict[str, Any]) -> None:
                with self.changed:
                    meta.update(
                        session_id=info.get("session_id"),
                        workspace=info.get("workspace", meta.get("workspace")),
                        inbox=info.get("inbox"),
                        outbox=info.get("outbox"),
                        job_name=info.get("job_name", meta.get("job_name")),
                        status_file=info.get("status_file", meta.get("status_file")),
                    )
                    self._save(task_id)
                    self.changed.notify_all()

            value = delegate(
                task=meta["task"],
                context_files=list(meta["context_files"]),
                host=str(host),
                model=self.config.get("model"),
                timeout=int(meta["timeout_seconds"]),
                max_context_bytes=int(self.config.get("max_context_bytes", DEFAULT_MAX_CONTEXT_BYTES)),
                opencode_command=str(self.config.get("opencode_command", "opencode")),
                effort=str(meta["effort"]),
                context_limit=int(meta["context_limit"]),
                output_limit=int(meta["output_limit"]),
                mode=str(meta["mode"]),
                workspace=meta.get("workspace"),
                event_log=task_dir / "events.ndjson",
                stderr_log=task_dir / "stderr.log",
                cancel_event=cancel_event,
                backend=str(meta["backend"]),
                ssh_user=self.config.get("ssh_user"),
                ssh_key=self.config.get("ssh_key"),
                launcher_command=str(self.config.get("launcher_command", "llamacode")),
                remote_workspace=self.config.get("remote_workspace"),
                session_id=meta.get("session_id"),
                session_callback=record_remote_session,
            )
            (task_dir / "result.json").write_text(
                json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            with self.changed:
                meta.update(status="completed", finished_at=utc_now(), result=value)
        except Exception as exc:
            status = "cancelled" if cancel_event.is_set() else "failed"
            with self.changed:
                meta.update(status=status, finished_at=utc_now(), error=str(exc))
        finally:
            with self.changed:
                self._save(task_id)
                self.changed.notify_all()

    def _events(self, task_id: str, limit: int) -> list[Any]:
        if limit <= 0:
            return []
        path = self._task_dir(task_id) / "events.ndjson"
        if not path.exists():
            return []
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()[-limit:]
        events: list[Any] = []
        for line in lines:
            try:
                events.append(compact_event(json.loads(line)))
            except json.JSONDecodeError:
                events.append({"raw": line})
        return events

    def snapshot(self, task_id: str, tail_events: int = 20) -> dict[str, Any]:
        with self.lock:
            if task_id not in self.tasks:
                raise WorkerError(f"unknown task_id: {task_id}")
            path = self._meta_path(task_id)
            try:
                disk_meta = json.loads(path.read_text(encoding="utf-8"))
                if disk_meta.get("owner_pid") != os.getpid():
                    self.tasks[task_id] = disk_meta
            except (OSError, ValueError, TypeError):
                pass
            meta = dict(self.tasks[task_id])
        meta["events"] = self._events(task_id, max(0, min(int(tail_events), 200)))
        if tail_events > 0 and meta.get("session_id"):
            try:
                backend = resolve_backend(str(meta.get("backend", "auto")))
                host = os.getenv("OPENCODE_WORKER_HOST") or self.config.get("host")
                if backend == "llamacode" and host:
                    raw = run_remote(
                        str(host),
                        self.config.get("ssh_user"),
                        self.config.get("ssh_key"),
                        [
                            str(self.config.get("launcher_command", "llamacode")),
                            "remote",
                            "messages",
                            "--session",
                            str(meta["session_id"]),
                            "--limit",
                            str(max(1, min(int(tail_events), 100))),
                        ],
                        timeout=15,
                    )
                    messages = json.loads(raw)
                    if isinstance(messages, list):
                        meta["remote_messages"] = compact_event(messages[-tail_events:])
            except (WorkerError, OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
                meta["remote_messages_error"] = str(exc)
        if meta.get("job_name"):
            try:
                backend = resolve_backend(str(meta.get("backend", "auto")))
                host = os.getenv("OPENCODE_WORKER_HOST") or self.config.get("host")
                if backend == "llamacode" and host:
                    raw = run_remote(
                        str(host),
                        self.config.get("ssh_user"),
                        self.config.get("ssh_key"),
                        [
                            str(self.config.get("launcher_command", "llamacode")),
                            "remote",
                            "status",
                            "--job",
                            str(meta["job_name"]),
                        ],
                        timeout=15,
                    )
                    meta["remote_job"] = compact_event(json.loads(raw))
            except (WorkerError, OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
                meta["remote_job_error"] = str(exc)
        meta["transcript_path"] = str((self._task_dir(task_id) / "events.ndjson").resolve())
        return meta

    def wait(self, task_id: str, seconds: float, tail_events: int) -> dict[str, Any]:
        deadline = time.monotonic() + max(0.0, min(float(seconds), 55.0))
        with self.changed:
            if task_id not in self.tasks:
                raise WorkerError(f"unknown task_id: {task_id}")
            while self.tasks[task_id]["status"] not in TERMINAL:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    break
                self.changed.wait(remaining)
        return self.snapshot(task_id, tail_events)

    def cancel(self, task_id: str) -> dict[str, Any]:
        with self.changed:
            if task_id not in self.tasks:
                raise WorkerError(f"unknown task_id: {task_id}")
            if self.tasks[task_id]["status"] in TERMINAL:
                return self.snapshot(task_id, 0)
            cancel_event = self.cancel_events.get(task_id)
            if cancel_event is None:
                raise WorkerError("task belongs to another active MCP server; cancel it from its originating Codex task")
            cancel_event.set()
            future = self.futures.get(task_id)
            if future and future.cancel():
                self.tasks[task_id].update(
                    status="cancelled", finished_at=utc_now(), error="cancelled before start"
                )
                self._save(task_id)
                self.changed.notify_all()
        return self.snapshot(task_id, 0)

    def fetch_file(self, task_id: str, remote_path: str, local_path: str | None) -> dict[str, Any]:
        with self.lock:
            if task_id not in self.tasks:
                raise WorkerError(f"unknown task_id: {task_id}")
            meta = dict(self.tasks[task_id])
        outbox = str(meta.get("outbox") or "")
        if not outbox.startswith("/srv/llamacode/sessions/"):
            raise WorkerError("task has no managed remote session outbox")
        session_root = posixpath.dirname(outbox)
        source = remote_path if remote_path.startswith("/") else posixpath.join(outbox, remote_path)
        source = posixpath.normpath(source)
        if source != session_root and not source.startswith(session_root + "/"):
            raise WorkerError("remote_path must stay inside this task's managed session directory")
        host = os.getenv("OPENCODE_WORKER_HOST") or self.config.get("host")
        if not host:
            raise WorkerError("OpenCode worker host is not configured")
        if local_path:
            destination = Path(local_path)
        else:
            name = posixpath.basename(source)
            if not name:
                raise WorkerError("remote_path must identify a file")
            destination = self._task_dir(task_id) / "downloads" / name
        downloaded = download_remote_file(
            str(host),
            self.config.get("ssh_user"),
            self.config.get("ssh_key"),
            source,
            destination,
        )
        return {"ok": True, "task_id": task_id, "remote_path": source, "local_path": str(downloaded)}

    def list(self, limit: int) -> list[dict[str, Any]]:
        with self.lock:
            for task_id in list(self.tasks):
                try:
                    disk_meta = json.loads(self._meta_path(task_id).read_text(encoding="utf-8"))
                    if disk_meta.get("owner_pid") != os.getpid():
                        self.tasks[task_id] = disk_meta
                except (OSError, ValueError, TypeError):
                    continue
            ordered = sorted(
                self.tasks.values(), key=lambda item: item.get("created_at", ""), reverse=True
            )
            return [
                {
                    key: item.get(key)
                    for key in (
                        "task_id", "status", "task", "backend", "session_id", "effort", "created_at", "started_at", "finished_at"
                    )
                }
                for item in ordered[: max(1, min(int(limit), 100))]
            ]


TOOLS = [
    {
        "name": "start_task",
        "description": "Start a tightly scoped OpenCode worker locally through Ollama or remotely through the LlamaCode one-shot launcher and return a task_id immediately. Effort defaults to medium; reserve xhigh for exceptional hard or high-risk work. Agent mode may read, edit, run commands, and use configured MCP tools on its selected machine.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task": {"type": "string", "minLength": 1},
                "workspace": {"type": "string", "description": "Directory OpenCode may inspect and modify. For the LlamaCode backend this must be an absolute path on the remote VPS."},
                "context_files": {"type": "array", "items": {"type": "string"}},
                "session_id": {"type": "string", "description": "Continue a managed remote OpenCode session returned by an earlier task. Omit to create a fresh session."},
                "mode": {"type": "string", "enum": ["agent", "bounded"], "default": "agent"},
                "effort": {
                    "type": "string",
                    "enum": list(EFFORTS),
                    "default": DEFAULT_EFFORT,
                    "description": "Use low for tiny deterministic work, medium for normal execution, and xhigh only for exceptional hard or high-risk tasks.",
                },
                "timeout": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": MAX_TIMEOUT,
                    "default": 0,
                    "description": "0 waits until OpenCode reaches a terminal state; a positive value is a hard wall-clock limit in seconds.",
                },
            },
            "required": ["task"],
            "additionalProperties": False,
        },
    },
    {
        "name": "get_task",
        "description": "Inspect status, final result, and recent compact OpenCode session events; use transcript_path for full raw output.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "string"},
                "tail_events": {"type": "integer", "minimum": 0, "maximum": 200},
            },
            "required": ["task_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "wait_task",
        "description": "Wait up to 55 seconds, then return the task's latest status and compact events.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "string"},
                "wait_seconds": {"type": "number", "minimum": 0, "maximum": 55},
                "tail_events": {"type": "integer", "minimum": 0, "maximum": 200},
            },
            "required": ["task_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "list_tasks",
        "description": "List recent OpenCode worker task summaries.",
        "inputSchema": {
            "type": "object",
            "properties": {"limit": {"type": "integer", "minimum": 1, "maximum": 100}},
            "additionalProperties": False,
        },
    },
    {
        "name": "cancel_task",
        "description": "Cancel a queued or running task, including its remote OpenCode session request and tmux job.",
        "inputSchema": {
            "type": "object",
            "properties": {"task_id": {"type": "string"}},
            "required": ["task_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "fetch_file",
        "description": "Download one file from a task's managed remote session workspace/inbox/outbox to the local machine through SCP.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "string"},
                "remote_path": {"type": "string", "description": "Absolute path inside the managed session directory, or a path relative to its outbox."},
                "local_path": {"type": "string", "description": "Optional local destination. Defaults to the MCP task downloads directory."},
            },
            "required": ["task_id", "remote_path"],
            "additionalProperties": False,
        },
    },
]

REGISTRY: TaskRegistry | None = None


def registry() -> TaskRegistry:
    global REGISTRY
    if REGISTRY is None:
        REGISTRY = TaskRegistry()
    return REGISTRY


def call_tool(name: str, arguments: dict[str, Any]) -> Any:
    store = registry()
    if name == "start_task":
        return store.start(arguments)
    if name == "get_task":
        return store.snapshot(str(arguments.get("task_id", "")), int(arguments.get("tail_events", 20)))
    if name == "wait_task":
        return store.wait(
            str(arguments.get("task_id", "")),
            float(arguments.get("wait_seconds", 30)),
            int(arguments.get("tail_events", 20)),
        )
    if name == "list_tasks":
        return store.list(int(arguments.get("limit", 20)))
    if name == "cancel_task":
        return store.cancel(str(arguments.get("task_id", "")))
    if name == "fetch_file":
        local_path = arguments.get("local_path")
        if local_path is not None and not isinstance(local_path, str):
            raise WorkerError("local_path must be a string")
        return store.fetch_file(
            str(arguments.get("task_id", "")),
            str(arguments.get("remote_path", "")),
            local_path,
        )
    raise WorkerError(f"unknown tool: {name}")


def handle(message: dict[str, Any]) -> None:
    method = message.get("method")
    request_id = message.get("id")
    if method == "initialize":
        requested = message.get("params", {}).get("protocolVersion", "2024-11-05")
        rpc_result(
            request_id,
            {
                "protocolVersion": requested,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "local-opencode-worker", "version": "0.7.0"},
            },
        )
    elif method == "ping":
        rpc_result(request_id, {})
    elif method == "tools/list":
        rpc_result(request_id, {"tools": TOOLS})
    elif method == "tools/call":
        params = message.get("params", {})
        try:
            value = call_tool(str(params.get("name", "")), params.get("arguments", {}))
            rpc_result(request_id, text_result(value))
        except (WorkerError, OSError, ValueError, TypeError) as exc:
            rpc_result(request_id, text_result({"error": str(exc)}, is_error=True))
    elif request_id is not None:
        rpc_error(request_id, -32601, f"method not found: {method}")


def main() -> int:
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8", errors="strict")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="strict")
    for line in sys.stdin:
        try:
            message = json.loads(line)
            if isinstance(message, dict):
                handle(message)
        except json.JSONDecodeError:
            continue
    return 0


if __name__ == "__main__":
    sys.exit(main())
