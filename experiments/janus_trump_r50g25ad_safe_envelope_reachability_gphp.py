from __future__ import annotations

import argparse
import json
import random
from collections import Counter
from fractions import Fraction
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r50g25g_micro_rup_restart_replay_source_lift_family as r50g25g
import janus_trump_r50g25ab_analytic_ub_pivot_selector_amortized_potential as r50g25ab

GATE = "JANUS_TRUMP_R50G25AD_RESIDUAL_SAFE_ENVELOPE_INVARIANT_OR_BOUNDED_DEGREE_GPHP_COUNTEREXAMPLE"
AD_PREREG_COMMIT = "d5e620ec7339d24181685471e6e7d1bf0006da6b"
AC_RECEIPT_COMMIT = "841a2e9ea4f1d470ef7be1c66a96c9cdd34a3ed2"
HOLE_SIZES = (6, 8, 10, 12, 16, 20)
MODES = ("CYCLIC_MIX", "SEEDED_BALANCED")


def G_fraction(C: int, L: int, V: int) -> Fraction:
    C, L, V = int(C), int(L), int(V)
    if V <= 0:
        raise AssertionError(("AD_G_NONPOSITIVE_V", C, L, V))
    S = C + L
    return Fraction(S, 1) + Fraction((2 * V - 1) * S * S, 4 * V * V)


def choose_neighbors_cyclic(p: int, h: int):
    raw = [p % h, (p + 1) % h, (2 * p + 3) % h, (3 * p + 1) % h, (p + 3) % h]
    out = []
    for x in raw:
        if x not in out:
            out.append(x)
        if len(out) == 3:
            return tuple(out)
    for x in range(h):
        if x not in out:
            out.append(x)
        if len(out) == 3:
            return tuple(out)
    raise AssertionError(("AD_CYCLIC_NEIGHBOR_FAILURE", p, h, out))


def choose_neighbors_balanced(pigeons: int, h: int, seed: int):
    rng = random.Random(seed)
    loads = [0] * h
    result = []
    for p in range(pigeons):
        ties = list(range(h))
        rng.shuffle(ties)
        rank = {hole: i for i, hole in enumerate(ties)}
        chosen = sorted(range(h), key=lambda hole: (loads[hole], rank[hole], hole))[:3]
        chosen = tuple(sorted(chosen))
        for hole in chosen:
            loads[hole] += 1
        result.append(chosen)
    return result, loads


def graph_php(h: int, mode: str):
    if h < 3:
        raise AssertionError(("AD_H_TOO_SMALL", h))
    pigeons = h + 1
    if mode == "CYCLIC_MIX":
        neighborhoods = [choose_neighbors_cyclic(p, h) for p in range(pigeons)]
    elif mode == "SEEDED_BALANCED":
        neighborhoods, _ = choose_neighbors_balanced(pigeons, h, 86000000 + h)
    else:
        raise AssertionError(("AD_UNKNOWN_MODE", mode))

    edge_var = {}
    next_var = 1
    for p, ns in enumerate(neighborhoods):
        if len(set(ns)) != 3:
            raise AssertionError(("AD_LEFT_DEGREE_DRIFT", p, ns))
        for hole in ns:
            edge_var[(p, hole)] = next_var
            next_var += 1

    clauses = []
    for p, ns in enumerate(neighborhoods):
        clauses.append(tuple(edge_var[(p, hole)] for hole in ns))

    incident = {hole: [] for hole in range(h)}
    for (p, hole), var in edge_var.items():
        incident[hole].append((p, var))
    for hole in range(h):
        inc = sorted(incident[hole])
        for i in range(len(inc)):
            for j in range(i + 1, len(inc)):
                p1, v1 = inc[i]
                p2, v2 = inc[j]
                if p1 == p2:
                    continue
                clauses.append((-v1, -v2))

    formula = r33.canonical_formula(clauses)
    right_degrees = [len(incident[hole]) for hole in range(h)]
    widths = Counter(len(c) for c in formula)
    meta = {
        "holes": h,
        "pigeons": pigeons,
        "left_degree": 3,
        "mode": mode,
        "variable_count_expected": 3 * pigeons,
        "right_degree_min": min(right_degrees),
        "right_degree_max": max(right_degrees),
        "right_degree_sum": sum(right_degrees),
        "clause_width_histogram": {str(k): v for k, v in sorted(widths.items())},
        "UNSAT_reason": "Any satisfying assignment would allow choosing one true allowed edge per pigeon; binary collision clauses force the chosen holes to be distinct, yielding an injection from h+1 pigeons into h holes.",
    }
    if r33.measure(formula)[2] != 3 * pigeons:
        raise AssertionError(("AD_VARIABLE_COUNT_DRIFT", h, mode, r33.measure(formula), meta))
    if any(len(c) not in (2, 3) for c in formula):
        raise AssertionError(("AD_WIDTH_DRIFT", h, mode))
    return formula, meta


def is_unsat_terminal(out):
    label = str(out.get("terminal_label") or out.get("terminal_kind") or "")
    return "UNSAT" in label or "EMPTY_CLAUSE" in label


def audit_case(formula, meta, chain):
    initial = r33.canonical_formula(formula)
    initial_clv = list(r33.measure(initial))
    try:
        out = r50g25ab.analytic_run(initial, chain)
    except AssertionError as exc:
        return {
            "meta": meta,
            "initial_CLV": initial_clv,
            "status": "IMPLEMENTATION_FAILURE",
            "error": repr(exc),
            "safe_envelope_counterexample": None,
        }

    events = []
    first_safe_failure = None
    first_selector_gap = None
    max_ratio = None
    min_slack = None
    for event in out.get("residual_events", []):
        C, L, V = map(int, event["residual_CLV"])
        B = int(event["budget"])
        g = G_fraction(C, L, V)
        ratio = float(g / B) if B else float("inf")
        slack = Fraction(B, 1) - g
        row = {
            "outer_round": int(event["outer_round"]),
            "residual_hash": event["residual_hash"],
            "CLV": [C, L, V],
            "S": C + L,
            "B": B,
            "G_num": g.numerator,
            "G_den": g.denominator,
            "G_float": float(g),
            "G_over_B": ratio,
            "B_minus_G_float": float(slack),
            "chosen_var": int(event["chosen_var"]),
            "min_UB_S": int(event["chosen_UB_S"]),
            "safe_envelope_pass": bool(g <= B),
            "selector_within_B": bool(int(event["chosen_UB_S"]) <= B),
        }
        events.append(row)
        if not row["safe_envelope_pass"] and first_safe_failure is None:
            first_safe_failure = row
        if not row["selector_within_B"] and first_selector_gap is None:
            first_selector_gap = row
        if max_ratio is None or (ratio, row["residual_hash"], row["outer_round"]) > (max_ratio[0], max_ratio[1]["residual_hash"], max_ratio[1]["outer_round"]):
            max_ratio = (ratio, row)
        if min_slack is None or float(slack) < min_slack[0]:
            min_slack = (float(slack), row)

    semantic_mismatch = False
    if out.get("status") == "TERMINAL":
        semantic_mismatch = not is_unsat_terminal(out)

    return {
        "meta": meta,
        "initial_CLV": initial_clv,
        "status": out.get("status"),
        "terminal_kind": out.get("terminal_kind"),
        "terminal_label": out.get("terminal_label"),
        "fallback_DP_count": int(out.get("fallback_DP_count", 0)),
        "budget": int(out.get("budget", 0)),
        "max_controlled_state_size": out.get("max_controlled_state_size"),
        "selector_bound_checks": int(out.get("selector_bound_checks", 0)),
        "exact_materializations": int(out.get("exact_materializations", 0)),
        "residual_event_count": len(events),
        "residual_events": events,
        "safe_envelope_counterexample": first_safe_failure,
        "selector_gap_event": first_selector_gap,
        "max_G_over_B": None if max_ratio is None else max_ratio[0],
        "max_G_over_B_event": None if max_ratio is None else max_ratio[1],
        "minimum_B_minus_G": None if min_slack is None else min_slack[0],
        "minimum_B_minus_G_event": None if min_slack is None else min_slack[1],
        "semantic_mismatch_on_known_GPHP_UNSAT": semantic_mismatch,
        "implementation_class": out.get("class") if out.get("status") == "IMPLEMENTATION_FAILURE" else None,
        "raw_status_class": out.get("class"),
    }


def run():
    chain = r50g25g._chain()
    cases = []
    for h in HOLE_SIZES:
        for mode in MODES:
            f, meta = graph_php(h, mode)
            cases.append((f, meta))

    rows = [audit_case(f, meta, chain) for f, meta in cases]
    safe_counterexamples = [r for r in rows if r.get("safe_envelope_counterexample") is not None]
    selector_gaps = [r for r in rows if r.get("selector_gap_event") is not None or r.get("status") == "SELECTOR_GAP"]
    semantic_mismatches = [r for r in rows if r.get("semantic_mismatch_on_known_GPHP_UNSAT")]
    implementation_failures = [r for r in rows if r.get("status") == "IMPLEMENTATION_FAILURE"]
    residual_limits = [r for r in rows if r.get("status") == "RESIDUAL_LIMIT"]

    if safe_counterexamples:
        verdict = "SAFE_ENVELOPE_REACHABILITY_COUNTEREXAMPLE_FOUND"
    elif selector_gaps:
        verdict = "ANALYTIC_SELECTOR_BUDGET_GAP_WITHOUT_G_COUNTEREXAMPLE"
    elif semantic_mismatches:
        verdict = "SEMANTIC_MISMATCH_ON_GPHP_UNSAT"
    elif implementation_failures:
        verdict = "REPLAY_OR_BOUND_SOUNDNESS_FAILURE"
    elif residual_limits:
        verdict = "RESIDUAL_AFTER_AT_MOST_V0_FALLBACKS"
    else:
        verdict = "NO_SAFE_ENVELOPE_COUNTEREXAMPLE_IN_PREREGISTERED_DEGREE3_GPHP_FAMILY"

    event_rows = [(r["max_G_over_B"], r) for r in rows if r.get("max_G_over_B") is not None]
    max_case = max(event_rows, key=lambda x: (x[0], x[1]["meta"]["holes"], x[1]["meta"]["mode"]))[1] if event_rows else None
    total_events = sum(r.get("residual_event_count", 0) for r in rows)
    status_hist = Counter(str(r.get("status")) for r in rows)
    terminal_hist = Counter(str(r.get("terminal_label")) for r in rows if r.get("status") == "TERMINAL")

    return {
        "gate": GATE,
        "AD_preregistration_commit": AD_PREREG_COMMIT,
        "parent_AC_receipt_commit": AC_RECEIPT_COMMIT,
        "verdict": verdict,
        "domain": {
            "case_count": len(rows),
            "hole_sizes": list(HOLE_SIZES),
            "modes": list(MODES),
            "all_left_degree": 3,
            "all_clause_widths_subset_2_3": True,
            "truth_used_for_generation_or_pivot_selection": False,
            "semantic_UNSAT_known_by_pigeonhole_counting": True,
        },
        "status_partition": dict(sorted(status_hist.items())),
        "terminal_partition": dict(sorted(terminal_hist.items())),
        "total_root_reachable_residual_event_count": total_events,
        "safe_envelope_counterexample_count": len(safe_counterexamples),
        "selector_gap_case_count": len(selector_gaps),
        "semantic_mismatch_count": len(semantic_mismatches),
        "implementation_failure_count": len(implementation_failures),
        "residual_limit_count": len(residual_limits),
        "max_G_over_B_case": max_case,
        "rows": rows,
        "next_gate": "R50G25AE_MINIMIZE_SAFE_ENVELOPE_REACHABILITY_COUNTEREXAMPLE" if safe_counterexamples else "R50G25AE_SCALE_BOUNDED_DEGREE_GPHP_AND_DERIVE_REACHABILITY_INVARIANT_CANDIDATE",
        "firewall": {
            "P_VS_NP": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "TRUMP_finished": False,
            "finite_no_counterexample_is_not_universal_proof": True,
            "these_exact_graphs_are_empirical_adversaries_not_claimed_published_hard_instances": True,
            "resolution_lower_bounds_do_not_automatically_transfer_to_hybrid_scheduler": True,
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    result = run()
    p = Path(args.out)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "gate": result["gate"],
        "verdict": result["verdict"],
        "domain": result["domain"],
        "status_partition": result["status_partition"],
        "terminal_partition": result["terminal_partition"],
        "residual_events": result["total_root_reachable_residual_event_count"],
        "safe_counterexamples": result["safe_envelope_counterexample_count"],
        "selector_gap_cases": result["selector_gap_case_count"],
        "semantic_mismatches": result["semantic_mismatch_count"],
        "next_gate": result["next_gate"],
    }, indent=2, sort_keys=True))
    if result["max_G_over_B_case"] is not None:
        m = result["max_G_over_B_case"]
        print("MAX_G_OVER_B", json.dumps({
            "meta": m["meta"],
            "initial_CLV": m["initial_CLV"],
            "max_G_over_B": m["max_G_over_B"],
            "event": m["max_G_over_B_event"],
            "fallback_DP_count": m["fallback_DP_count"],
            "terminal_label": m["terminal_label"],
        }, sort_keys=True))


if __name__ == "__main__":
    main()
