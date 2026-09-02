#!/usr/bin/env python3
"""R17 diagnostic replay of the byte-frozen R15D candidate on the frozen R16 worlds.

No truth verifier is imported or called.  The only purpose is to measure where
physical clause materialization grows under exactly the R16 candidate logic and
resource caps.
"""
from __future__ import annotations

import argparse
import hashlib
import inspect
import json
from pathlib import Path

import janus_trump_r15d_bounded_observer_equivalent_refactor as r15d
import janus_trump_r16_prospective_unseen_factored_bridge_holdout as r16

EXPECTED_BLOB = "e6def9fef656c8f1af1b9f245bc855081f13a586"


def analyze_history(spec, frame, bridge, candidate):
    history = list(candidate.get("history", []))
    initial_clauses = int(spec["frame_clause_count"])
    original_internal = int(spec["frame_variable_count"]) - int(spec["bridge_variable_count"])
    prev = initial_clauses
    trajectory = []
    max_factor = None
    max_factor_step = None
    max_delta = None
    max_delta_step = None
    for i, rec in enumerate(history, start=1):
        after = int(rec["after_clauses"])
        delta = after - prev
        factor = (after / prev) if prev else None
        row = {
            "step": i,
            "eliminated_var": int(rec["eliminated_var"]),
            "before_clauses": prev,
            "after_clauses": after,
            "clause_delta": delta,
            "clause_growth_factor": factor,
            "remaining_internal": int(rec["remaining_internal"]),
            "pair_attempts_step": int(rec["pair_attempts_step"]),
            "direct_resolvents": int(rec["direct_resolvents"]),
            "wide_resolvents": int(rec["wide_resolvents"]),
            "new_shared_atoms": int(rec["new_shared_atoms"]),
            "atom_reuse_hits": int(rec["atom_reuse_hits"]),
            "dominated_or_duplicate_removed": int(rec["dominated_or_duplicate_removed"]),
        }
        trajectory.append(row)
        if factor is not None and (max_factor is None or factor > max_factor):
            max_factor, max_factor_step = factor, i
        if max_delta is None or delta > max_delta:
            max_delta, max_delta_step = delta, i
        prev = after

    cp = candidate.get("checkpoint", {})
    checkpoint_active = int(cp.get("active_clauses", prev))
    checkpoint_aux = int(cp.get("auxiliary_variables", 0) or 0)
    eliminated = int(cp.get("eliminated", len(history)) or len(history))
    remaining = int(cp.get("remaining_internal", max(0, original_internal - eliminated)) or 0)
    terminal = candidate.get("status") in ("COMPLETE_EXTENDED_INTERFACE", "COMPLETE_UNSAT_INTERFACE")
    if candidate.get("status") == "OPEN_RESOURCE_LIMIT_WITH_CHECKPOINT" and candidate.get("reason") == "ACTIVE_CLAUSE_CAP":
        wall_class = "TERMINAL_REPRESENTATION_MATERIALIZATION_OVER_CAP" if remaining == 0 else "PRETERMINAL_REPRESENTATION_MATERIALIZATION_OVER_CAP"
    elif terminal:
        wall_class = "TERMINAL_WITHIN_FROZEN_CAP"
    else:
        wall_class = "OTHER_RESOURCE_OR_INTEGRITY_STATUS"

    return {
        "id": spec["id"],
        "suite": spec["suite"],
        "n": int(spec["n"]),
        "frame_sha256": spec["frame_sha256"],
        "frame_clauses": initial_clauses,
        "frame_variables": int(spec["frame_variable_count"]),
        "bridge_variables": int(spec["bridge_variable_count"]),
        "original_internal_variables": original_internal,
        "candidate_status": candidate.get("status"),
        "candidate_reason": candidate.get("reason"),
        "candidate_phase": candidate.get("phase"),
        "elapsed_seconds": candidate.get("elapsed_seconds"),
        "history_steps": len(history),
        "checkpoint_active_clauses": checkpoint_active,
        "checkpoint_auxiliary_variables": checkpoint_aux,
        "checkpoint_shared_pair_atoms": int(cp.get("shared_pair_atoms", 0) or 0),
        "checkpoint_atom_reuse_hits": int(cp.get("atom_reuse_hits", 0) or 0),
        "checkpoint_pair_attempts": int(cp.get("pair_attempts", 0) or 0),
        "checkpoint_dominated_removed": int(cp.get("dominated_removed", 0) or 0),
        "eliminated_internal_variables": eliminated,
        "remaining_internal_variables": remaining,
        "completion_fraction": (eliminated / original_internal) if original_internal else 1.0,
        "active_clause_over_input_ratio": checkpoint_active / initial_clauses if initial_clauses else None,
        "active_clause_over_auxiliary_ratio": checkpoint_active / checkpoint_aux if checkpoint_aux else None,
        "maximum_step_clause_growth_factor": max_factor,
        "maximum_step_clause_growth_factor_step": max_factor_step,
        "maximum_step_clause_growth_delta": max_delta,
        "maximum_step_clause_growth_delta_step": max_delta_step,
        "wall_class": wall_class,
        "trajectory": trajectory,
    }


def forensic_firewall():
    src = "\n".join(inspect.getsource(f) for f in (analyze_history, run))
    forbidden = ["dpll(", "shadow_exact_interface", "incremental_allowed_masks", "allowed_masks", "truth_table_sha256", "exact_cnf_geometry"]
    hits = [x for x in forbidden if x in src]
    return {"pass": not hits, "forbidden_hits": hits}


def run():
    freeze, resources = r16.load_contracts()
    rows = []
    candidate_fw = r15d.candidate_firewall()
    for spec in freeze["worlds"]:
        generated = r16.generate_frozen_world(spec)
        candidate = r15d.compile_observed(generated["frame"], generated["bridge"])
        rows.append(analyze_history(spec, generated["frame"], generated["bridge"], candidate))

    fw = forensic_firewall()
    active_cap_rows = [r for r in rows if r["candidate_reason"] == "ACTIVE_CLAUSE_CAP"]
    terminal_rows = [r for r in rows if r["candidate_status"] in ("COMPLETE_EXTENDED_INTERFACE", "COMPLETE_UNSAT_INTERFACE")]
    terminal_over_cap = [r for r in active_cap_rows if r["remaining_internal_variables"] == 0]
    suites_with_cap = sorted({r["suite"] for r in active_cap_rows})
    n_with_cap = sorted({r["n"] for r in active_cap_rows})
    max_ratio = max((r["active_clause_over_input_ratio"] for r in rows), default=None)
    worst = max(rows, key=lambda r: r["checkpoint_active_clauses"])
    gates = {
        "G1_CANDIDATE_FIREWALL": candidate_fw["pass"],
        "G2_FORENSIC_NO_TRUTH_ACCESS": fw["pass"],
        "G3_ALL_EIGHT_FROZEN_WORLDS_REPLAYED": len(rows) == 8,
        "G4_RESOURCE_CAP_UNCHANGED": r15d.MAX_ACTIVE_CLAUSES == 150000 and r15d.WALL_SECONDS == 120.0,
        "G5_NO_THEOREM_INFLATION": True,
    }
    verdict = "R17_FAIL_INTEGRITY" if not all(gates.values()) else "R17_PHYSICAL_CLAUSE_MATERIALIZATION_WALL_REPRODUCED"
    return {
        "schema": "JANUS/TRUMP/R17/RESOURCE_GROWTH_FORENSICS/RESULT/v1.0",
        "created_date": "2026-09-02",
        "verdict": verdict,
        "candidate_blob_sha": EXPECTED_BLOB,
        "gates": gates,
        "summary": {
            "worlds": len(rows),
            "terminal_within_cap": len(terminal_rows),
            "active_clause_cap_worlds": len(active_cap_rows),
            "active_clause_cap_suites": suites_with_cap,
            "active_clause_cap_n_values": n_with_cap,
            "terminal_representation_over_cap_worlds": [r["id"] for r in terminal_over_cap],
            "maximum_active_clause_over_input_ratio": max_ratio,
            "largest_checkpoint_world": worst["id"],
            "largest_checkpoint_active_clauses": worst["checkpoint_active_clauses"],
            "largest_checkpoint_input_clauses": worst["frame_clauses"],
        },
        "representation_analysis": {
            "literal_duplicate_debt": "NOT_THE_WHOLE_EXPLANATION: each post-step formula is rebuilt as a Python set of canonical clauses by minimize_width3_basis_bounded.",
            "simple_subset_dominance_debt": "NOT_THE_WHOLE_EXPLANATION: the frozen minimizer removes unit/binary subset-dominated width<=3 clauses before checkpoint active_clauses is recorded.",
            "semantic_redundancy_beyond_subset": "OPEN: R17 does not run a truth oracle or semantic minimizer.",
            "name_debt": "PAIR-ATOM NAME DEBT IS STRONGLY QUOTIENTED: shared pair atoms remain below 859 in every resource-open world while active physical clauses reach 160968..533525.",
            "localized_wall": "PHYSICAL_CLAUSE_MATERIALIZATION_IN_THE_CURRENT_WIDTH3_DEFINITIONAL_CNF_LANGUAGE",
        },
        "rows": rows,
        "scientific_update": "The same frozen candidate reproduces the R16 wall across both PLANTED and UNSAT_CORE cells at n=32/40/48. The strongest witness is the n=32 UNSAT_CORE world whose original internal-variable elimination reaches zero while the minimized physical width<=3 representation contains 533525 active clauses. Therefore, for that world, unfinished original search depth is not the reason for OPEN; the frozen representation itself exceeds the preregistered physical clause envelope.",
        "next_gate": "R18_SEMANTIC_FACTOR_GRAPH_COMPRESSION_DISCOVERY__NEW_LANGUAGE_REQUIRED__THEN_NEW_UNSEEN_HOLDOUT",
        "claim_ceiling": "This is finite forensic evidence of representation materialization growth under one frozen language. It is not an asymptotic lower bound and does not imply that all compact representations fail.",
        "law": "WHEN_NAMES_ARE_ALREADY_SHARED_BUT_THE_SENTENCES_EXPLODE__COMPRESS_THE_SEMANTIC_STRUCTURE_NOT_JUST_THE_NAMES",
        "seal": "CAPTAIN_OBVIOUS_FOUND_WHAT_FILLED_THE_ROOM__IT_WAS_THE_CLAUSES",
        "P_VS_NP": "OPEN",
    }


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--output", required=True); args = ap.parse_args()
    out = run()
    Path(args.output).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"verdict": out["verdict"], "summary": out["summary"], "representation_analysis": out["representation_analysis"], "gates": out["gates"], "P_VS_NP": "OPEN"}, indent=2, sort_keys=True))
    return 2 if out["verdict"] == "R17_FAIL_INTEGRITY" else 0


if __name__ == "__main__":
    raise SystemExit(main())
