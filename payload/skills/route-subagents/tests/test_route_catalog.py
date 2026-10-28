"""Behavioral regressions for the static fit and installed profile contract."""
from copy import deepcopy
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

    def test_bounded_tasks_compare_nonzero_costs(self):
        expected = {"mechanical": "luna_low", "simple": "luna_medium", "checked": "luna_high",
                    "hard": "luna_xhigh", "demanding": "luna_max"}
        for difficulty, name in expected.items():
            with self.subTest(difficulty=difficulty):
                self.assertEqual(self.choose(workload="bounded", difficulty=difficulty), name)

    def test_paid_frontier_uses_task_cost_and_capability(self):
        cases = {"narrow": "terra_low", "routine": "terra_medium", "normal": "terra_high",
                 "subtle": "terra_xhigh", "complex": "terra_max"}
        for difficulty, name in cases.items():
            with self.subTest(difficulty=difficulty):
                self.assertEqual(self.choose(workload="execution", difficulty=difficulty), name)
        self.assertEqual(self.choose(workload="execution", minimum_index=42), "terra_high")
        self.assertEqual(self.choose(workload="judgment", difficulty="difficult"), "terra_max")
        self.assertEqual(self.choose(workload="judgment", difficulty="exceptional"), "sol_xhigh")

    def test_cost_preference_does_not_lower_floor_or_override_scope(self):
        self.assertEqual(self.choose(workload="bounded", minimum_index=41), "terra_high")
        self.assertEqual(self.choose(workload="execution", difficulty="narrow"), "terra_low")
        # A caller cannot lower the execution default floor of 42.
        chosen = router.resolve(DATA, workload="execution", minimum_index=22)
        self.assertEqual(chosen["minimum_index"], 42)
        self.assertEqual(chosen["selected_profile"], "terra_high")

    def test_terra_max_remains_a_valid_availability_fallback(self):
        available = {name for name in DATA["profiles"] if not name.startswith("sol_")}
        self.assertEqual(self.choose(workload="execution", difficulty="complex", available=available), "terra_max")

    def test_complex_execution_never_drops_to_underfloor_sol_medium(self):
        available = set(DATA["profiles"]) - {"terra_max"}
        self.assertEqual(self.choose(workload="execution", difficulty="complex", available=available), "sol_xhigh")

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

    def test_heavy_specialized_workflows_use_astra_low_then_medium(self):
        self.assertEqual(self.choose(workload="heavy"), "astra_low")
        self.assertEqual(self.choose(workload="heavy", difficulty="deep"), "astra_medium")
        self.assertEqual(self.choose(workload="heavy", minimum_index=48), "astra_medium")
        self.assertEqual(self.choose(workload="heavy", minimum_index=52), "sol_xhigh")
        # Naming Astra alone does not unlock High/XHigh/Max.
        with self.assertRaises(ValueError):
            self.choose(requested_model="gpt-6-astra", minimum_index=52)
        self.assertEqual(self.choose(explicit="astra_high"), "astra_high")

    def test_execution_does_not_request_an_advisor(self):
        selected = router.resolve(DATA, workload="execution")
        self.assertEqual(selected["mode"], "execute")
        self.assertNotIn("advisor_contract", selected)

    def test_automatic_advice_requires_an_actual_stall(self):
        with self.assertRaises(ValueError):
            self.choose(mode="advisor", consult_reason="I am uncertain about the layout")
        with self.assertRaises(ValueError):
            self.choose(mode="advisor", consult_reason="Choose a design", stalled_on=" ")
        with self.assertRaises(ValueError):
            self.choose(mode="advisor", stalled_on="The same failure remains after focused fixes")
        with self.assertRaises(ValueError):
            self.choose(workload="advisor")

    def test_stalled_advisor_is_bounded_and_uses_sol_by_default(self):
        kwargs = dict(mode="advisor", consult_reason="What cause should I check next?",
                      stalled_on="The bug persists after both plausible fixes; logs contradict the hypothesis.")
        self.assertEqual(self.choose(**kwargs), "sol_medium")
        self.assertEqual(self.choose(**kwargs, difficulty="narrow"), "sol_low")
        selected = router.resolve(DATA, **kwargs)
        self.assertFalse(selected["advisor_contract"]["may_edit_files"])
        self.assertFalse(selected["advisor_contract"]["may_spawn_agents"])
        self.assertEqual(selected["advisor_contract"]["default_max_words"], 250)
        self.assertIn("bug persists", selected["stalled_on"])

    def test_heavy_stalled_advisor_uses_minimum_sufficient_astra(self):
        kwargs = dict(mode="advisor", advisor_fit="heavy",
                      consult_reason="How can this interaction satisfy the conflicting constraints?",
                      stalled_on="Both concrete GUI approaches failed keyboard navigation and layout constraints.")
        self.assertEqual(self.choose(**kwargs), "astra_low")
        self.assertEqual(self.choose(**kwargs, difficulty="deep"), "astra_medium")
        self.assertEqual(self.choose(**kwargs, minimum_index=52), "sol_xhigh")

    def test_direct_user_advice_request_can_precede_a_stall(self):
        self.assertEqual(self.choose(mode="advisor", advisor_requested=True,
                                     consult_reason="The user explicitly requested a second opinion"), "sol_medium")


    def test_v5_score_transcription_and_luna_nonzero_cost(self):
        expected = {"luna": [10, 18, 21, 23, 28], "terra": [29, 38, 42, 45, 51],
                    "sol": [35, 46, 50, 52, 55], "astra": [43, 51, 55, 55, 57]}
        for family, scores in expected.items():
            actual = [DATA["profiles"][family + "_" + effort]["intelligence_index"]
                      for effort in ["low", "medium", "high", "xhigh", "max"]]
            self.assertEqual(actual, scores)
        self.assertFalse(DATA["cost_policy"]["luna_is_free"])
        self.assertGreater(DATA["account_pricing"]["same_usage_relative_tariff"]["luna"], 0)
        for effort in ["low", "medium", "high", "xhigh", "max"]:
            self.assertGreater(DATA["profiles"]["luna_" + effort]["benchmark_cost_usd"], 0)

    def test_v5_floor_and_historical_task_cost_provenance_stay_separate(self):
        selected = router.resolve(DATA, workload="execution", difficulty="complex")
        self.assertEqual(selected["minimum_index"], 51)
        self.assertEqual(selected["selected_profile"], "terra_max")
        self.assertEqual(selected["intelligence_index"], 51)
        self.assertEqual(selected["intelligence_benchmark"], "Artificial Analysis Intelligence Index v5.0")
        self.assertEqual(selected["intelligence_date"], "2026-10-28")
        self.assertEqual(selected["task_cost_basis"], "historical_proxy")
        self.assertEqual(selected["task_cost_snapshot"]["date"], "2026-10-27")
        self.assertEqual(selected["task_cost_snapshot"]["benchmark"], "Artificial Analysis Intelligence Index v4.3.2")

    def test_disabling_historical_proxy_uses_tariff_and_sufficient_effort(self):
        data = deepcopy(DATA)
        data["cost_policy"]["allow_historical_task_cost_proxy"] = False
        selected = router.resolve(data, workload="execution", difficulty="complex")
        self.assertEqual(selected["selected_profile"], "terra_max")
        self.assertEqual(selected["task_cost_basis"], "unavailable")
        self.assertFalse(selected["task_cost_used_for_selection"])
        self.assertEqual(router.resolve(data, workload="bounded")["selected_profile"], "luna_max")

    def test_matching_current_costs_can_rank_efforts_within_same_tariff(self):
        data = deepcopy(DATA)
        data["cost_policy"]["allow_historical_task_cost_proxy"] = False
        data["task_cost_snapshot"].update(benchmark=data["benchmark"], date="2026-10-28", status="current")
        data["profiles"]["terra_high"]["benchmark_cost_usd"] = 0.25
        data["profiles"]["terra_xhigh"]["benchmark_cost_usd"] = 0.12
        selected = router.resolve(data, workload="execution", difficulty="normal")
        self.assertEqual(selected["selected_profile"], "terra_xhigh")
        self.assertEqual(selected["task_cost_basis"], "current_benchmark")
        self.assertTrue(selected["task_cost_used_for_selection"])

    def test_terra_wins_equal_index_even_when_sol_has_lower_task_cost_proxy(self):
        data = deepcopy(DATA)
        data["profiles"]["sol_medium"]["intelligence_index"] = 51
        selected = router.resolve(data, workload="execution", difficulty="complex",
                                  available={"terra_max", "sol_medium"})
        self.assertEqual(data["profiles"]["terra_max"]["intelligence_index"],
                         data["profiles"]["sol_medium"]["intelligence_index"])
        self.assertGreater(data["profiles"]["terra_max"]["benchmark_cost_usd"],
                           data["profiles"]["sol_medium"]["benchmark_cost_usd"])
        self.assertEqual(selected["selected_profile"], "terra_max")
        self.assertEqual(selected["same_usage_relative_tariff"], 1)

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
