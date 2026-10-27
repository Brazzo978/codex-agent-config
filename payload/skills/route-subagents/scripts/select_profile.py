#!/usr/bin/env python3
"""Resolve the user's static subagent fit; no network or model calls."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


DEFAULT_CATALOG = Path(__file__).resolve().parents[1] / "references" / "routing-data.json"


def resolve(
    data, workload="execution", difficulty="default", minimum_index=None,
    explicit=None, requested_model=None, available=None, allow_sol_max=False,
):
    profiles = data["profiles"]
    exposed = set(profiles) if available is None else set(available)
    if explicit is not None:
        if explicit not in profiles or explicit not in exposed:
            raise ValueError(f"Explicit profile is unavailable: {explicit}")
        p = profiles[explicit]
        if requested_model is not None and requested_model != p["model"]:
            raise ValueError("Explicit profile and requested model conflict.")
        return result(explicit, p, data, None, None, "Exact explicit profile; optimization bypassed.")

    if workload not in data["routes"]:
        raise ValueError(f"Unknown workload: {workload}")
    routes = data["routes"][workload]
    baseline = routes.get(difficulty, routes["default"])
    floor = profiles[baseline]["intelligence_index"]
    if minimum_index is not None:
        if isinstance(minimum_index, bool) or not isinstance(minimum_index, int) or minimum_index < 0:
            raise ValueError("Minimum index must be a nonnegative integer.")
        floor = max(floor, minimum_index)
    known_models = {p["model"] for p in profiles.values()}
    if requested_model is not None and requested_model not in known_models:
        raise ValueError(f"Explicit model is unavailable: {requested_model}")

    eligible = []
    for name, p in profiles.items():
        if name not in exposed or p["intelligence_index"] is None:
            continue
        if requested_model is not None and p["model"] != requested_model:
            continue
        explicit_astra_model = requested_model == p["model"] and p["family"] == "astra"
        if p["explicit_only"] and not explicit_astra_model:
            continue
        if p["requires_indivisible_extreme"] and not allow_sol_max:
            continue
        fit = data["fit"][workload].get(p["family"], 0)
        if explicit_astra_model:
            fit = 2
        if fit <= 0 or p["intelligence_index"] < floor:
            continue
        eligible.append((name, p, fit))
    if not eligible:
        raise ValueError(f"No compatible exposed profile meets floor {floor} and the request/gates.")

    best_fit = max(item[2] for item in eligible)
    eligible = [item for item in eligible if item[2] == best_fit]
    weights = data["account_pricing"]["same_usage_relative_tariff"]
    effort_order = data["effort_order"]

    def key(item):
        name, p, _ = item
        weight = weights[p["family"]]
        if weight == 0:
            return (0, effort_order.index(p["effort"]), 0, -p["intelligence_index"])
        cost = p["benchmark_cost_usd"]
        if cost is None:
            return (2, float("inf"), weight if weight is not None else float("inf"), -p["intelligence_index"])
        return (1, cost, weight if weight is not None else float("inf"), -p["intelligence_index"])

    name, p, _ = min(eligible, key=key)
    reason = (
        "Free Luna meets scope and capability; choose the lowest sufficient effort."
        if weights[p["family"]] == 0
        else "Lowest published paid benchmark task cost among equally suitable profiles at or above the floor."
    )
    return result(name, p, data, baseline, floor, reason)


def result(name, profile, data, baseline, floor, reason):
    return {
        "selected_profile": name,
        "model": profile["model"],
        "effort": profile["effort"],
        "baseline_profile": baseline,
        "minimum_index": floor,
        "intelligence_index": profile["intelligence_index"],
        "benchmark_cost_usd": profile["benchmark_cost_usd"],
        "same_usage_relative_tariff": data["account_pricing"]["same_usage_relative_tariff"][profile["family"]],
        "selection_reason": reason,
        "cost_caveat": "Benchmark USD is a comparison proxy, not a Codex quota forecast.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--workload", choices=["bounded", "execution", "judgment"], default="execution")
    parser.add_argument("--difficulty", default="default")
    parser.add_argument("--minimum-index", type=int)
    parser.add_argument("--explicit", help="Exact exposed profile; bypass optimization.")
    parser.add_argument("--model", dest="requested_model", help="Restrict selection to this exact model ID.")
    parser.add_argument("--available", nargs="+", help="Exposed profile names. Omit to use all installed catalog profiles.")
    parser.add_argument("--allow-sol-max", action="store_true", help="Use only when an indivisible extreme need is demonstrated.")
    args = parser.parse_args()
    data = json.loads(args.catalog.read_text(encoding="utf-8"))
    try:
        selected = resolve(
            data, args.workload, args.difficulty, args.minimum_index,
            args.explicit, args.requested_model, args.available, args.allow_sol_max,
        )
    except ValueError as exc:
        parser.exit(2, f"Routing failed: {exc}\n")
    print(json.dumps(selected, indent=2))


if __name__ == "__main__":
    main()
