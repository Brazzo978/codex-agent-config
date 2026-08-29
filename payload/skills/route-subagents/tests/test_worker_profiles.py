from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import opencode_mcp  # noqa: E402
import opencode_worker  # noqa: E402


class WorkerProfileTests(unittest.TestCase):
    def test_effort_is_restricted_and_defaults_to_medium(self) -> None:
        self.assertEqual(opencode_worker.normalize_effort(None), "medium")
        self.assertEqual(opencode_worker.normalize_effort("LOW"), "low")
        self.assertEqual(opencode_worker.normalize_effort("xhigh"), "xhigh")
        with self.assertRaises(opencode_worker.WorkerError):
            opencode_worker.normalize_effort("high")
        with self.assertRaises(opencode_worker.WorkerError):
            opencode_worker.normalize_effort("max")

    def test_backend_is_explicit_and_auto_preserves_ollama(self) -> None:
        self.assertEqual(opencode_worker.resolve_backend(None), "ollama")
        self.assertEqual(opencode_worker.resolve_backend("auto"), "ollama")
        self.assertEqual(opencode_worker.resolve_backend("llamacode"), "llamacode")
        with self.assertRaises(opencode_worker.WorkerError):
            opencode_worker.resolve_backend("ssh")

    def test_timeout_zero_waits_until_completion_and_positive_limits_are_validated(self) -> None:
        self.assertEqual(opencode_worker.normalize_timeout(0), 0)
        self.assertEqual(opencode_worker.normalize_timeout("3600"), 3600)
        with self.assertRaises(opencode_worker.WorkerError):
            opencode_worker.normalize_timeout(9)
        with self.assertRaises(opencode_worker.WorkerError):
            opencode_worker.normalize_timeout(opencode_worker.MAX_TIMEOUT + 1)

    def test_llamacode_prefers_remote_profile(self) -> None:
        available = ["qwen38-remote-q4-216k", "qwen38-agent-q4-216k"]
        selected = opencode_worker.choose_model(available, None, "llamacode")
        self.assertEqual(selected, "qwen38-remote-q4-216k")
        with self.assertRaises(opencode_worker.WorkerError):
            opencode_worker.choose_model(["qwen38-agent-q4-216k"], None, "llamacode")

    def test_remote_command_quotes_one_liner_arguments(self) -> None:
        command = opencode_worker.remote_command(
            "10.10.10.115",
            "root",
            None,
            ["llamacode", "run", "--dir", "/root/a folder", "do one thing"],
        )
        self.assertEqual(command[-2], "root@10.10.10.115")
        self.assertEqual(
            command[-1],
            "llamacode run --dir '/root/a folder' 'do one thing'",
        )

    def test_managed_remote_command_wraps_worker_process_group(self) -> None:
        command = opencode_worker.managed_remote_command(
            "10.10.10.115", "root", None, ["llamacode", "run", "task"]
        )
        self.assertIn("setsid", command[-1])
        self.assertIn("kill -TERM", command[-1])
        self.assertIn("llamacode run task", command[-1])

    def test_limits_are_effort_specific_and_configurable(self) -> None:
        self.assertEqual(opencode_worker.resolve_limits({}, "medium"), (110_592, 32_768))
        config = {"context_limit": 98_304, "output_limits": {"low": 2_048}}
        self.assertEqual(opencode_worker.resolve_limits(config, "low"), (98_304, 2_048))

    def test_inline_config_carries_variant_limits_and_guardrails(self) -> None:
        payload = json.loads(
            opencode_worker.make_inline_config(
                "http://127.0.0.1:11434",
                "qwen-test",
                "agent",
                "medium",
                110_592,
                32_768,
            )
        )
        model = payload["provider"]["local-worker"]["models"]["qwen-test"]
        agent = payload["agent"]["local-worker"]
        self.assertEqual(model["limit"], {"context": 110_592, "output": 32_768})
        self.assertEqual(model["variants"]["low"]["reasoningEffort"], "low")
        self.assertEqual(model["variants"]["xhigh"]["reasoningEffort"], "high")
        self.assertEqual(agent["variant"], "medium")
        self.assertIn("at most one concise reconnaissance pass", agent["prompt"])
        self.assertIn("never dump complete large files", agent["prompt"])
        self.assertIn("smallest operating-system package", agent["prompt"])
        self.assertIn("Report every package installed", agent["prompt"])

    def test_task_contract_installs_only_required_missing_bash_packages(self) -> None:
        request = opencode_worker.build_request("do the task")
        self.assertIn("if a command required for the assigned task is unavailable", request)
        self.assertIn("install only that package noninteractively", request)
        self.assertIn("Do not install optional or speculative packages", request)
        self.assertIn("stop with needs_context", request)

    def test_mcp_schema_exposes_only_supported_efforts(self) -> None:
        start = next(tool for tool in opencode_mcp.TOOLS if tool["name"] == "start_task")
        effort = start["inputSchema"]["properties"]["effort"]
        self.assertEqual(effort["enum"], ["low", "medium", "xhigh"])
        self.assertEqual(effort["default"], "medium")
        timeout = start["inputSchema"]["properties"]["timeout"]
        self.assertEqual(timeout["minimum"], 0)
        self.assertEqual(timeout["default"], 0)
        self.assertIn("session_id", start["inputSchema"]["properties"])
        fetch = next(tool for tool in opencode_mcp.TOOLS if tool["name"] == "fetch_file")
        self.assertEqual(fetch["inputSchema"]["required"], ["task_id", "remote_path"])

    def test_progress_events_truncate_large_strings(self) -> None:
        compact = opencode_mcp.compact_event({"output": "x" * 5_000}, maximum=100)
        self.assertLess(len(compact["output"]), 200)
        self.assertIn("truncated 4900 chars", compact["output"])
        self.assertIn("transcript_path", compact["output"])


if __name__ == "__main__":
    unittest.main()
