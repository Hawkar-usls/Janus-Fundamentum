from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r47f_small_reachable_fixpoint_full_macro_falsifier as r47f
import janus_trump_r47x_cap_projection_coverage_one_swap_falsifier as r47x
import janus_trump_r47z_r47x_minimum_additive_envelope_slack_rescue as r47z

GATE = "JANUS_TRUMP_R47AA_FRONTIER_MINIMUM_ADDITIVE_ENVELOPE_SLACK_PROFILE"
MAX_ORDINAL = 64
R47Z_TARGET_HASH = "ed330049538dc3fb487019c71bb49bde65494dc88453e50bed73b49d4ee17ca6"
R47Z_EXPECTED_DELTA = 4


def canon(formula):
    return r33.canonical_formula(formula)


def clv(formula):
    return r33.measure(canon(formula))


def formula_hash(formula):
    return r47f.formula_hash(canon(formula))


def run_general_envelope(root, delta):
    root = canon(root)
    C0, _, V0 = clv(root)
    B = C0 + int(delta)
    old_c0, old_v0 = r47z.C0, r47z.V0
    try:
        r47z.C0 = int(C0)
        r47z.V0 = int(V0)
        result = r47z.run_envelope_chain(root, B)
    finally:
        r47z.C0 = old_c0
        r47z.V0 = old_v0
    if result["B"] != B or result["delta"] != int(delta):
        raise AssertionError(("R47AA_GENERAL_ENVELOPE_PARAMETER_DRIFT", result["B"], result["delta"], B, delta))
    return result


def compact_attempt(result):
    row = {
        "delta": int(result["delta"]),
        "B": int(result["B"]),
        "covered": bool(result["covered"]),
        "selected_pivots": [int(s["var"]) for s in result["selected_steps"]],
        "selected_step_count": len(result["selected_steps"]),
        "candidate_probe_count": int(result["candidate_probe_count"]),
        "rejected_probe_count": int(result["rejected_probe_count"]),
    }
    if result["covered"]:
        row["terminal"] = result["terminal"]
        if result["terminal"]["semantic_sat"] is True:
            if not result["SAT_root_reconstruction"]["pass"]:
                raise AssertionError("R47AA_SAT_RECONSTRUCTION_FAIL")
            row["SAT_root_reconstruction_pass"] = True
    else:
        obstruction = result["obstruction"]
        best = obstruction.get("best_rejected")
        row["obstruction"] = {
            "state_hash": obstruction["state_hash"],
            "state_CLV": obstruction["state_CLV"],
            "candidate_count": int(obstruction["candidate_count"]),
            "best_rejected": None if best is None else {
                "var": int(best["var"]),
                "final_CLV": best["final_CLV"],
                "final_clause_overflow": int(best["final_clause_overflow"]),
            },
        }
    return row


def profile_root(root, provenance):
    root = canon(root)
    root_clv = clv(root)
    C0, _, V0 = root_clv
    if V0 <= 0:
        raise AssertionError(("R47AA_ZERO_VARIABLE_ROOT", provenance, root_clv))
    ladder = []
    full_terminal = None
    minimum_delta = None
    total_probes = 0
    total_selected = 0
    final_obstruction = None

    for delta in range(V0 + 1):
        result = run_general_envelope(root, delta)
        total_probes += int(result["candidate_probe_count"])
        total_selected += len(result["selected_steps"])
        ladder.append(compact_attempt(result))
        if result["covered"]:
            minimum_delta = int(delta)
            full_terminal = result["terminal"]
            break
        final_obstruction = result["obstruction"]

    return {
        "provenance": provenance,
        "root_hash": formula_hash(root),
        "root_CLV": list(root_clv),
        "C0": int(C0),
        "V0": int(V0),
        "minimum_delta": minimum_delta,
        "minimum_B": None if minimum_delta is None else int(C0 + minimum_delta),
        "rescued_within_delta_le_V0": minimum_delta is not None,
        "attempt_count": len(ladder),
        "total_candidate_probes_across_delta_ladder": int(total_probes),
        "total_selected_steps_across_delta_ladder": int(total_selected),
        "delta_ladder": ladder,
        "terminal_at_minimum": full_terminal,
        "last_obstruction_if_unrescued": None if minimum_delta is not None or final_obstruction is None else {
            "state_hash": final_obstruction["state_hash"],
            "state_CLV": final_obstruction["state_CLV"],
            "candidate_count": int(final_obstruction["candidate_count"]),
        },
    }


def run():
    center_original, center_reached, center_fixpoint = r47x.load_center_original()
    records = []
    seen = set()
    metrics = {
        "frontier_positions_seen": 0,
        "mutants_generated": 0,
        "duplicate_mutations_skipped": 0,
        "semantic_or_nonfixpoint": 0,
        "reachable_fixpoints": 0,
        "unique_reachable_fixpoints_profiled": 0,
        "total_candidate_probes_all_delta_ladders": 0,
        "total_selected_steps_all_delta_ladders": 0,
    }

    center_record = profile_root(center_fixpoint, {
        "kind": "CENTER_CONTROL",
        "frontier_ordinal": 0,
        "phase": "CENTER",
        "source_clause": None,
        "replacement_clause": None,
    })
    records.append(center_record)
    seen.add(center_record["root_hash"])

    target_regression = None

    for ordinal, (phase, source, replacement, mutated) in enumerate(r47x.frontier(center_original), 1):
        if ordinal > MAX_ORDINAL:
            break
        metrics["frontier_positions_seen"] += 1
        if mutated is None:
            metrics["duplicate_mutations_skipped"] += 1
            continue
        r47x.validate_exact_3cnf(mutated)
        metrics["mutants_generated"] += 1
        reached = r47f.reachable_fixpoint(mutated)
        if reached is None:
            metrics["semantic_or_nonfixpoint"] += 1
            continue
        metrics["reachable_fixpoints"] += 1
        root = canon(reached["formula"])
        fh = formula_hash(root)
        if fh in seen:
            continue
        seen.add(fh)

        record = profile_root(root, {
            "kind": "ONE_SWAP_REACHABLE_FIXPOINT",
            "frontier_ordinal": int(ordinal),
            "phase": phase,
            "source_clause": list(source),
            "replacement_clause": list(replacement),
            "mutated_original_hash": formula_hash(mutated),
        })
        records.append(record)

        if fh == R47Z_TARGET_HASH:
            target_regression = record
            if record["minimum_delta"] != R47Z_EXPECTED_DELTA:
                raise AssertionError(("R47AA_R47Z_TARGET_DELTA_DRIFT", record["minimum_delta"]))

    metrics["unique_reachable_fixpoints_profiled"] = len(records)
    metrics["total_candidate_probes_all_delta_ladders"] = sum(
        int(r["total_candidate_probes_across_delta_ladder"]) for r in records
    )
    metrics["total_selected_steps_all_delta_ladders"] = sum(
        int(r["total_selected_steps_across_delta_ladder"]) for r in records
    )

    if target_regression is None:
        raise AssertionError("R47AA_R47Z_TARGET_NOT_REACHED_INSIDE_FROZEN_WINDOW")

    rescued = [r for r in records if r["minimum_delta"] is not None]
    unrescued = [r for r in records if r["minimum_delta"] is None]
    histogram = Counter(str(int(r["minimum_delta"])) for r in rescued)
    hardest = None
    if rescued:
        hardest = max(
            rescued,
            key=lambda r: (
                int(r["minimum_delta"]),
                int(r["total_candidate_probes_across_delta_ladder"]),
                tuple(r["root_CLV"]),
                r["root_hash"],
            ),
        )

    verdict = (
        "EXPLICIT_ROOT_WITH_NO_RESCUE_FOR_DELTA_LE_V0_FOUND"
        if unrescued
        else "FRONTIER_MAXIMUM_MINIMUM_SLACK_MEASURED__FINITE_ONLY"
    )
    return {
        "gate": GATE,
        "verdict": verdict,
        "frozen_frontier": {
            "center_original_hash": r47x.CENTER_ORIGINAL_HASH,
            "ordinal_window": [1, MAX_ORDINAL],
            "center_control_included": True,
            "deduplicate_by_reachable_fixpoint_hash": True,
        },
        "R47Z_regression": {
            "target_hash": R47Z_TARGET_HASH,
            "minimum_delta": target_regression["minimum_delta"],
            "pass": target_regression["minimum_delta"] == R47Z_EXPECTED_DELTA,
        },
        "metrics": metrics,
        "profile_summary": {
            "rescued_root_count": len(rescued),
            "unrescued_root_count": len(unrescued),
            "minimum_delta_histogram": dict(sorted(histogram.items(), key=lambda kv: int(kv[0]))),
            "maximum_observed_minimum_delta": None if hardest is None else int(hardest["minimum_delta"]),
            "maximum_observed_minimum_delta_exceeds_R47Z_4": False if hardest is None else int(hardest["minimum_delta"]) > 4,
        },
        "hardest_rescued_root": None if hardest is None else hardest,
        "first_unrescued_root": None if not unrescued else unrescued[0],
        "roots": records,
        "interpretation": {
            "finite_frontier_only": True,
            "finite_maximum_delta_is_not_asymptotic_bound": True,
            "bounded_frontier_does_not_prove_universal_polynomial_envelope": True,
            "no_sequence_enumeration": True,
            "next_if_no_unrescued_root": "R47AB_INPUT_SIZE_LADDER_FOR_MINIMUM_ADDITIVE_ENVELOPE_SLACK_GROWTH_OR_SYMBOLIC_BOUND",
            "next_if_unrescued_root": "FORENSICS_ON_FIRST_DELTA_GT_V0_LOWER_BOUND_WITNESS_OR_STRONGER_CERTIFIED_RESET",
        },
        "firewall": {
            "UNIVERSAL_POLYNOMIAL_ENVELOPE_COVERAGE": "OPEN",
            "O4_UNIVERSAL_COVERAGE": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "P_EQ_NP": "NOT_PROVED",
            "P_NE_NP": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "TRUMP_finished": False,
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    args = parser.parse_args()
    result = run()
    if args.output:
        p = Path(args.output)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "gate": result["gate"],
        "verdict": result["verdict"],
        "R47Z_regression": result["R47Z_regression"],
        "metrics": result["metrics"],
        "profile_summary": result["profile_summary"],
        "hardest_rescued_root": None if result["hardest_rescued_root"] is None else {
            "root_hash": result["hardest_rescued_root"]["root_hash"],
            "root_CLV": result["hardest_rescued_root"]["root_CLV"],
            "minimum_delta": result["hardest_rescued_root"]["minimum_delta"],
            "minimum_B": result["hardest_rescued_root"]["minimum_B"],
            "provenance": result["hardest_rescued_root"]["provenance"],
        },
        "first_unrescued_root": None if result["first_unrescued_root"] is None else {
            "root_hash": result["first_unrescued_root"]["root_hash"],
            "root_CLV": result["first_unrescued_root"]["root_CLV"],
            "provenance": result["first_unrescued_root"]["provenance"],
        },
        "firewall": result["firewall"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
