from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r47f_small_reachable_fixpoint_full_macro_falsifier as r47f
import janus_trump_r47x_cap_projection_coverage_one_swap_falsifier as r47x
import janus_trump_r48a_fixed_polynomial_envelope_pressure_frontier as r48a

GATE = "JANUS_TRUMP_R48A1_BSTAR_FULL_FRONTIER_KILLER"
MANDATORY_HASH = "ed330049538dc3fb487019c71bb49bde65494dc88453e50bed73b49d4ee17ca6"
MANDATORY_CLV = (75, 199, 22)
MANDATORY_BSTAR = 97


def canon(formula):
    return r33.canonical_formula(formula)


def clv(formula):
    return r33.measure(canon(formula))


def h(formula):
    return r47f.formula_hash(canon(formula))


def compact_chain(row):
    return {
        "covered": bool(row["covered"]),
        "B": int(row["B"]),
        "delta": int(row["delta"]),
        "selected_pivots": [int(s["var"]) for s in row["selected_steps"]],
        "selected_step_count": len(row["selected_steps"]),
        "candidate_probe_count": int(row["candidate_probe_count"]),
        "rejected_probe_count": int(row["rejected_probe_count"]),
        "maximum_persisted_clause_debt_over_C0": int(row["maximum_persisted_clause_debt_over_C0"]),
        "maximum_forced_clause_count": int(row["maximum_forced_clause_count"]),
        "terminal": row.get("terminal"),
        "obstruction": row.get("obstruction"),
    }


def enumerate_unique_roots():
    center_original, _, center_fixpoint = r47x.load_center_original()
    roots = [{
        "kind": "CENTER_CONTROL",
        "frontier_ordinal": 0,
        "phase": "CENTER_CONTROL",
        "source_clause": None,
        "replacement_clause": None,
        "mutated_original_hash": None,
        "formula": canon(center_fixpoint),
    }]
    seen = {h(center_fixpoint)}
    metrics = {
        "frontier_positions": 0,
        "mutants_generated": 0,
        "duplicate_mutations_skipped": 0,
        "semantic_or_nonfixpoint": 0,
        "reachable_fixpoints": 0,
        "duplicate_fixpoints": 0,
    }
    for ordinal, (phase, source, replacement, mutated) in enumerate(r47x.frontier(center_original), 1):
        metrics["frontier_positions"] += 1
        if mutated is None:
            metrics["duplicate_mutations_skipped"] += 1
            continue
        metrics["mutants_generated"] += 1
        reached = r47f.reachable_fixpoint(mutated)
        if reached is None:
            metrics["semantic_or_nonfixpoint"] += 1
            continue
        metrics["reachable_fixpoints"] += 1
        root = canon(reached["formula"])
        rh = h(root)
        if rh in seen:
            metrics["duplicate_fixpoints"] += 1
            continue
        seen.add(rh)
        roots.append({
            "kind": "ONE_SWAP_REACHABLE_FIXPOINT",
            "frontier_ordinal": int(ordinal),
            "phase": phase,
            "source_clause": list(source),
            "replacement_clause": list(replacement),
            "mutated_original_hash": h(mutated),
            "formula": root,
        })
    return roots, metrics


def run():
    roots, frontier_metrics = enumerate_unique_roots()
    rows = []
    failures = []
    mandatory = None
    total_probes = 0
    total_steps = 0
    max_debt = 0
    max_forced = 0

    for meta in roots:
        root = meta["formula"]
        C0, _, V0 = clv(root)
        B_star = C0 + V0
        chain = r48a.run_chain(root, B_star)
        compact = compact_chain(chain)
        total_probes += compact["candidate_probe_count"]
        total_steps += compact["selected_step_count"]
        max_debt = max(max_debt, compact["maximum_persisted_clause_debt_over_C0"])
        max_forced = max(max_forced, compact["maximum_forced_clause_count"])
        record = {
            "kind": meta["kind"],
            "frontier_ordinal": meta["frontier_ordinal"],
            "phase": meta["phase"],
            "source_clause": meta["source_clause"],
            "replacement_clause": meta["replacement_clause"],
            "mutated_original_hash": meta["mutated_original_hash"],
            "root_hash": h(root),
            "root_CLV": list(clv(root)),
            "C0": C0,
            "V0": V0,
            "B_star": B_star,
            "chain": compact,
        }
        rows.append(record)
        if record["root_hash"] == MANDATORY_HASH:
            mandatory = record
        if not compact["covered"]:
            failure = dict(record)
            failure["root_formula"] = [list(c) for c in root]
            failures.append(failure)

    if mandatory is None:
        raise AssertionError("R48A1_MANDATORY_R47Z_ROOT_NOT_FOUND")
    if tuple(mandatory["root_CLV"]) != MANDATORY_CLV:
        raise AssertionError(("R48A1_MANDATORY_CLV_DRIFT", mandatory["root_CLV"]))
    if mandatory["B_star"] != MANDATORY_BSTAR:
        raise AssertionError(("R48A1_MANDATORY_BSTAR_DRIFT", mandatory["B_star"]))
    if not mandatory["chain"]["covered"]:
        raise AssertionError("R48A1_MANDATORY_R47Z_ROOT_NOT_COVERED_BY_BSTAR")

    hardest = max(
        rows,
        key=lambda r: (
            r["chain"]["maximum_persisted_clause_debt_over_C0"],
            r["chain"]["candidate_probe_count"],
            r["chain"]["selected_step_count"],
            r["root_hash"],
        ),
    )

    verdict = (
        "ALL_FROZEN_FRONTIER_ROOTS_COVERED_BY_B_STAR__FINITE_ONLY"
        if not failures
        else "EXPLICIT_FROZEN_FRONTIER_B_STAR_COUNTEREXAMPLE_FOUND"
    )

    return {
        "gate": GATE,
        "verdict": verdict,
        "frontier_metrics": {
            **frontier_metrics,
            "unique_roots_including_center": len(rows),
            "B_star_covered_roots": len(rows) - len(failures),
            "B_star_failed_roots": len(failures),
            "total_candidate_probes": total_probes,
            "total_selected_steps": total_steps,
            "maximum_persisted_clause_debt_over_C0": max_debt,
            "maximum_forced_clause_count": max_forced,
        },
        "mandatory_regression": {
            "root_hash": mandatory["root_hash"],
            "root_CLV": mandatory["root_CLV"],
            "B_star": mandatory["B_star"],
            "covered": mandatory["chain"]["covered"],
            "selected_pivots": mandatory["chain"]["selected_pivots"],
            "candidate_probe_count": mandatory["chain"]["candidate_probe_count"],
        },
        "hardest_B_star_root": {
            "root_hash": hardest["root_hash"],
            "root_CLV": hardest["root_CLV"],
            "frontier_ordinal": hardest["frontier_ordinal"],
            "phase": hardest["phase"],
            "source_clause": hardest["source_clause"],
            "replacement_clause": hardest["replacement_clause"],
            "B_star": hardest["B_star"],
            "chain": hardest["chain"],
        },
        "failure_summaries": [{
            "root_hash": f["root_hash"],
            "root_CLV": f["root_CLV"],
            "frontier_ordinal": f["frontier_ordinal"],
            "phase": f["phase"],
            "source_clause": f["source_clause"],
            "replacement_clause": f["replacement_clause"],
            "B_star": f["B_star"],
            "obstruction": f["chain"]["obstruction"],
        } for f in failures],
        "full_failures": failures,
        "roots": rows,
        "interpretation": {
            "finite_frontier_only": True,
            "all_covered_proves_universal_B_star": False,
            "explicit_failure_refutes_B_star_for_frozen_controller": bool(failures),
            "sequence_enumeration_used": False,
            "R48A_minimum_delta_sweep_replaced": False,
        },
        "firewall": {
            "B_C0_PLUS_V0_UNIVERSAL_COVERAGE": "OPEN",
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
    d = run()
    if args.output:
        p = Path(args.output)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(d, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "gate": d["gate"],
        "verdict": d["verdict"],
        "frontier_metrics": d["frontier_metrics"],
        "mandatory_regression": d["mandatory_regression"],
        "hardest_B_star_root": d["hardest_B_star_root"],
        "failure_summaries": d["failure_summaries"],
        "firewall": d["firewall"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
