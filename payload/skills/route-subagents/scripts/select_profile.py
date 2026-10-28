#!/usr/bin/env python3
"""Resolve execution or an optional bounded advisor; no model calls."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


DEFAULT_CATALOG = Path(__file__).resolve().parents[1] / "references" / "routing-data.json"


def task_cost_basis(data):
    """Keep cost provenance separate from the current intelligence benchmark."""
    snapshot = data.get("task_cost_snapshot", {})
    if snapshot.get("benchmark") == data["benchmark"]:
        return "current_benchmark"
    if snapshot and data.get("cost_policy", {}).get("allow_historical_task_cost_proxy", False):
        return "historical_proxy"
    return "unavailable"


def resolve(
    data, workload="execution", difficulty="default", minimum_index=None,
    explicit=None, requested_model=None, available=None, allow_sol_max=False,
    mode="execute", consult_reason=None, advisor_fit="general",
    stalled_on=None, advisor_requested=False,
):
    if mode not in {"execute", "advisor"}:
        raise ValueError(f"Unknown mode: {mode}")
    if mode == "advisor":
        if not isinstance(consult_reason, str) or not consult_reason.strip():
            raise ValueError("Advisor mode needs a concrete consultation reason; skip unnecessary consultations.")
        if not advisor_requested and (not isinstance(stalled_on, str) or not stalled_on.strip()):
            raise ValueError("Automatic advice requires an observed stall with attempted work/evidence; ordinary uncertainty is insufficient.")
        if advisor_fit not in {"general", "heavy"}:
            raise ValueError(f"Unknown advisor fit: {advisor_fit}")
        workload = "advisor_heavy" if advisor_fit == "heavy" else "advisor"

    profiles = data["profiles"]
    exposed = set(profiles) if available is None else set(available)
    if explicit is not None:
        if explicit not in profiles or explicit not in exposed:
            raise ValueError(f"Explicit profile is unavailable: {explicit}")
        p = profiles[explicit]
        if requested_model is not None and requested_model != p["model"]:
            raise ValueError("Explicit profile and requested model conflict.")
        return result(explicit, p, data, None, None, "Exact explicit profile; optimization bypassed.",
                      mode, consult_reason, stalled_on, advisor_requested)

    if workload not in data["routes"]:
        raise ValueError(f"Unknown workload: {workload}")
    if mode == "execute" and workload.startswith("advisor"):
        raise ValueError("Advisor workloads require advisor mode and a concrete consultation reason.")
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
        # Naming Astra's model permits its Low/Medium lane. Higher efforts
        # remain explicit-profile-only, just like Ultra in every family.
        if p["explicit_only"]:
            continue
        if p["requires_indivisible_extreme"] and not allow_sol_max:
            continue
        fit = data["fit"][workload].get(p["family"], 0)
        if requested_model == p["model"] and p["family"] == "astra":
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

    basis = task_cost_basis(data)

    def key(item):
        name, p, _ = item
        weight = weights[p["family"]]
        tariff = weight if weight is not None else float("inf")
        cost = p["benchmark_cost_usd"] if basis != "unavailable" else None
        # The user's tariff preference is decisive across equally suitable
        # qualifying families. Task-cost proxies only rank equal tariffs.
        task_cost = cost if cost is not None else float("inf")
        return (tariff, task_cost, effort_order.index(p["effort"]), -p["intelligence_index"])

    name, p, _ = min(eligible, key=key)
    reason = "Lowest nominal same-usage tariff among the highest-fit profiles meeting the capability floor; task costs are secondary within equal tariffs."
    return result(name, p, data, baseline, floor, reason, mode, consult_reason, stalled_on, advisor_requested)


def result(name, profile, data, baseline, floor, reason, mode, consult_reason, stalled_on, advisor_requested):
    selected = {
        "mode": mode,
        "selected_profile": name,
        "model": profile["model"],
        "effort": profile["effort"],
        "baseline_profile": baseline,
        "minimum_index": floor,
        "intelligence_index": profile["intelligence_index"],
        "intelligence_benchmark": data["benchmark"],
        "intelligence_date": data["intelligence_snapshot"]["date"],
        "benchmark_cost_usd": profile["benchmark_cost_usd"],
        "task_cost_snapshot": data.get("task_cost_snapshot"),
        "task_cost_basis": task_cost_basis(data),
        "task_cost_role": "secondary_within_equal_tariff" if baseline is not None else "reference_only",
        "selection_cost_priority": "nominal same-usage tariff before benchmark task-cost proxies",
        "task_cost_used_for_selection": baseline is not None and task_cost_basis(data) != "unavailable" and profile["benchmark_cost_usd"] is not None,
        "same_usage_relative_tariff": data["account_pricing"]["same_usage_relative_tariff"][profile["family"]],
        "selection_reason": reason,
        "cost_caveat": "Task-cost USD keeps its own benchmark/date. Historical values are routing proxies, not measured v5.0 costs or Codex quota forecasts.",
    }
    if mode == "advisor":
        selected["consult_reason"] = consult_reason.strip()
        selected["stalled_on"] = stalled_on.strip() if isinstance(stalled_on, str) else None
        selected["explicit_user_requested_advice"] = bool(advisor_requested)
        selected["advisor_contract"] = data["advisor"]["contract"]
    return selected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--mode", choices=["execute", "advisor"], default="execute")
    parser.add_argument("--workload", choices=["bounded", "execution", "judgment", "heavy"], default="execution")
    parser.add_argument("--difficulty", default="default")
    parser.add_argument("--minimum-index", type=int)
    parser.add_argument("--explicit", help="Exact exposed profile; bypass optimization.")
    parser.add_argument("--model", dest="requested_model", help="Restrict selection to this exact model ID.")
    parser.add_argument("--available", nargs="+", help="Exposed profile names. Omit to use all installed catalog profiles.")
    parser.add_argument("--allow-sol-max", action="store_true", help="Use only when an indivisible extreme need is demonstrated.")
    parser.add_argument("--consult-reason", help="The concrete decision or uncertainty a short second opinion can resolve.")
    parser.add_argument("--stalled-on", help="Observed non-convergence: what failed, what was tried, and relevant evidence.")
    parser.add_argument("--advisor-requested", action="store_true", help="Only when the user explicitly requests a second opinion; permits advice without a prior stall.")
    parser.add_argument("--advisor-fit", choices=["general", "heavy"], default="general",
                        help="Heavy requires a real need for Astra's specialized end-to-end/design fit.")
    args = parser.parse_args()
    data = json.loads(args.catalog.read_text(encoding="utf-8"))
    try:
        selected = resolve(
            data, args.workload, args.difficulty, args.minimum_index,
            args.explicit, args.requested_model, args.available, args.allow_sol_max,
            args.mode, args.consult_reason, args.advisor_fit,
            args.stalled_on, args.advisor_requested,
        )
    except ValueError as exc:
        parser.exit(2, f"Routing failed: {exc}\n")
    print(json.dumps(selected, indent=2))


if __name__ == "__main__":
    main()
