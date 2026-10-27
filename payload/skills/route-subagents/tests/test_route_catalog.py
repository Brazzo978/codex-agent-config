"""Behavioral regressions for the static fit and installed profile contract."""
import importlib.util
import json
from pathlib import Path
import tomllib
import unittest

SKILL = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("select_profile", SKILL / "scripts" / "select_profile.py")
router = importlib.util.module_from_spec(spec)
spec.loader.exec_module(router)
DATA = json.loads((SKILL / "references" / "routing-data.json").read_text(encoding="utf-8"))


class RouteTests(unittest.TestCase):
    def choose(self, **kwargs):
        return router.resolve(DATA, **kwargs)["selected_profile"]

    def test_bounded_tasks_stay_on_free_luna(self):
        expected = {"mechanical": "luna_low", "simple": "luna_medium", "checked": "luna_high",
                    "hard": "luna_xhigh", "demanding": "luna_max"}
        for difficulty, name in expected.items():
            with self.subTest(difficulty=difficulty):
                self.assertEqual(self.choose(workload="bounded", difficulty=difficulty), name)

    def test_paid_frontier_uses_task_cost_and_capability(self):
        cases = {"narrow": "terra_low", "routine": "terra_medium", "normal": "terra_high",
                 "subtle": "terra_xhigh", "complex": "sol_medium"}
        for difficulty, name in cases.items():
            with self.subTest(difficulty=difficulty):
                self.assertEqual(self.choose(workload="execution", difficulty=difficulty), name)
        self.assertEqual(self.choose(workload="execution", minimum_index=42), "terra_high")
        self.assertEqual(self.choose(workload="judgment", difficulty="difficult"), "sol_high")
        self.assertEqual(self.choose(workload="judgment", difficulty="exceptional"), "sol_xhigh")

    def test_free_does_not_lower_floor_or_override_scope(self):
        self.assertEqual(self.choose(workload="bounded", minimum_index=41), "terra_medium")
        self.assertEqual(self.choose(workload="execution", difficulty="narrow"), "terra_low")
        # A caller cannot lower the execution default floor of 44.
        chosen = router.resolve(DATA, workload="execution", minimum_index=22)
        self.assertEqual(chosen["minimum_index"], 44)
        self.assertEqual(chosen["selected_profile"], "terra_high")

    def test_terra_max_remains_a_valid_availability_fallback(self):
        available = {name for name in DATA["profiles"] if not name.startswith("sol_")}
        self.assertEqual(self.choose(workload="execution", difficulty="complex", available=available), "terra_max")

    def test_sol_high_is_cheaper_than_terra_max_when_medium_is_missing(self):
        available = set(DATA["profiles"]) - {"sol_medium"}
        self.assertEqual(self.choose(workload="execution", difficulty="complex", available=available), "sol_high")

    def test_no_silent_underfloor_or_astra_fallback(self):
        with self.assertRaises(ValueError):
            self.choose(workload="execution", minimum_index=53)
        with self.assertRaises(ValueError):
            self.choose(available={"luna_max", "astra_low", "astra_medium"})

    def test_max_and_ultra_gates(self):
        with self.assertRaises(ValueError):
            self.choose(workload="judgment", difficulty="extreme")
        self.assertEqual(self.choose(workload="judgment", difficulty="extreme", allow_sol_max=True), "sol_max")
        for family in ["luna", "terra", "sol", "astra"]:
            self.assertEqual(self.choose(explicit=family + "_ultra"), family + "_ultra")

    def test_explicit_requests_remain_exact(self):
        self.assertEqual(self.choose(explicit="terra_max"), "terra_max")
        self.assertEqual(self.choose(explicit="sol_low"), "sol_low")
        self.assertEqual(self.choose(explicit="astra_low"), "astra_low")
        with self.assertRaises(ValueError):
            self.choose(explicit="terra_max", available={"sol_medium"})
        self.assertEqual(self.choose(workload="execution", difficulty="complex", requested_model="gpt-6.1-terra"), "terra_max")
        self.assertEqual(self.choose(requested_model="gpt-6-astra"), "astra_low")
        with self.assertRaises(ValueError):
            self.choose(requested_model="gpt-5.6-terra")

    def test_payload_matches_numeric_catalog(self):
        agents = SKILL.parents[1] / "agents"
        files = list(agents.glob("*.toml"))
        self.assertEqual(len(files), DATA["expected_agent_count"])
        seen = set()
        for path in files:
            parsed = tomllib.loads(path.read_text(encoding="utf-8"))
            name = parsed["name"]
            self.assertNotIn(name, seen)
            seen.add(name)
            expected = DATA["profiles"][name]
            self.assertEqual(parsed["model"], expected["model"])
            self.assertEqual(parsed["model_reasoning_effort"], expected["effort"])
            self.assertTrue(parsed["description"])
            self.assertTrue(parsed["developer_instructions"])
        self.assertEqual(seen, set(DATA["profiles"]))


if __name__ == "__main__":
    unittest.main()
