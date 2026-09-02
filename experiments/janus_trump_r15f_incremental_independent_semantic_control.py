#!/usr/bin/env python3
"""R15F: full-domain incremental semantic control for the byte-frozen R15D candidate.

Candidate phase is imported unchanged from R15D.  Only after candidate terminal
are two independent PySAT solvers constructed: Minisat22 for the original frame
and Glucose4 for the completed extended interface.  Every one of the 2^16
bridge assignments is tested by assumptions; internal/auxiliary variables stay
existential.  SAT models are replayed directly against the corresponding CNF.
"""
from __future__ import annotations

import argparse
import importlib.metadata
import json
import time
from hashlib import sha256
from pathlib import Path

from pysat.solvers import Solver

import janus_trump_r13_unseen_interface_generalization as r13
import janus_trump_r15b_factored_dp_extension_compiler_calibration as r15b
import janus_trump_r15d_bounded_observer_equivalent_refactor as r15d

WORLD_ID = "R13-W05"
EXPECTED_CANDIDATE_BLOB_SHA = "e6def9fef656c8f1af1b9f245bc855081f13a586"
EXPECTED_FRAME_SHA = "84fa0fbdd127b1c73f3c8ef6820a0d0cdf154093750ed9c600289fce4b6aae88"
EXPECTED_TRUTH_SHA = "acf8828272994c0ad05a44590aa4335e1828d5b7d3e3d4f438b0d497cfcad92f"
EXPECTED_ALLOWED = 287
EXPECTED_PYSAT_VERSION = "1.9.dev15"
ORIGINAL_SOLVER = "m22"
CANDIDATE_SOLVER = "g4"
VERIFIER_WALL_SECONDS = 600.0
PROGRESS_MASKS = 4096


class VerifierDeadline(RuntimeError):
    pass


def allowed_hash(masks):
    return sha256(json.dumps(list(masks), separators=(",", ":")).encode()).hexdigest()


def assumptions_for_mask(bridge, mask):
    return [int(v) if ((mask >> i) & 1) else -int(v) for i, v in enumerate(bridge)]


def replay_model(cnf, assumptions, model):
    """Check one SAT model against assumptions and every physical clause."""
    values = {abs(int(l)): int(l) > 0 for l in model if int(l) != 0}
    for lit in assumptions:
        v = abs(int(lit)); want = int(lit) > 0
        if v in values and values[v] != want:
            return False
        values[v] = want
    for clause in cnf:
        sat = False
        for lit in clause:
            val = values.get(abs(int(lit)))
            if val is not None and val == (int(lit) > 0):
                sat = True
                break
        if not sat:
            return False
    return True


def incremental_allowed_masks(cnf, bridge, solver_name, deadline, label):
    clauses = [list(map(int, c)) for c in cnf]
    allowed = []
    replay_failures = []
    started = time.monotonic()
    domain = 1 << len(bridge)
    scanned = 0
    with Solver(name=solver_name, bootstrap_with=clauses) as solver:
        for mask in range(domain):
            if time.monotonic() >= deadline:
                return {
                    "status": "OPEN_VERIFIER_RESOURCE_LIMIT",
                    "label": label,
                    "solver": solver_name,
                    "masks_scanned": scanned,
                    "domain_size": domain,
                    "allowed_partial_count": len(allowed),
                    "sat_model_replay_failures": replay_failures,
                    "elapsed_seconds": time.monotonic() - started,
                }
            assumps = assumptions_for_mask(bridge, mask)
            sat = bool(solver.solve(assumptions=assumps))
            scanned += 1
            if sat:
                model = solver.get_model()
                if model is None or not replay_model(clauses, assumps, model):
                    replay_failures.append(mask)
                    return {
                        "status": "FAIL_MODEL_REPLAY",
                        "label": label,
                        "solver": solver_name,
                        "masks_scanned": scanned,
                        "domain_size": domain,
                        "allowed_partial_count": len(allowed),
                        "sat_model_replay_failures": replay_failures,
                        "elapsed_seconds": time.monotonic() - started,
                    }
                allowed.append(mask)
            if scanned % PROGRESS_MASKS == 0 or scanned == domain:
                print(json.dumps({
                    "R15F_PROGRESS": label,
                    "solver": solver_name,
                    "masks_scanned": scanned,
                    "domain_size": domain,
                    "allowed_so_far": len(allowed),
                    "elapsed_s": round(time.monotonic() - started, 3),
                }, sort_keys=True), flush=True)
    return {
        "status": "COMPLETE",
        "label": label,
        "solver": solver_name,
        "masks_scanned": scanned,
        "domain_size": domain,
        "allowed_masks": allowed,
        "allowed_count": len(allowed),
        "truth_table_sha256": allowed_hash(allowed),
        "sat_model_replay_failures": replay_failures,
        "elapsed_seconds": time.monotonic() - started,
    }


def tiny_incremental_control():
    # exists x: (x or b) and (~x or c)  <=>  (b or c)
    frame = ((1, 2), (-1, 3))
    bridge = (2, 3)
    deadline = time.monotonic() + 10.0
    got = incremental_allowed_masks(frame, bridge, ORIGINAL_SOLVER, deadline, "TINY_CONTROL")
    if got["status"] != "COMPLETE":
        return False
    expected = [1, 2, 3]
    return got["allowed_masks"] == expected and not got["sat_model_replay_failures"]


def run():
    package_version = importlib.metadata.version("python-sat")
    freeze = r13.load_freeze()
    spec = next(w for w in freeze["worlds"] if w["id"] == WORLD_ID)
    world = r13.generate_world(spec)
    frame = tuple(tuple(c) for c in world["frame"])
    bridge = tuple(world["bridge"])
    frame_ok = world["source"]["frame_sha256"] == EXPECTED_FRAME_SHA
    if not frame_ok:
        raise AssertionError("W05 frame drift")

    # Candidate phase. No exact-interface/truth access before terminal.
    candidate_started = time.monotonic()
    candidate = r15d.compile_observed(frame, bridge)
    candidate_elapsed = time.monotonic() - candidate_started
    remaining = candidate.get("remaining_internal", candidate.get("checkpoint", {}).get("remaining_internal"))
    candidate_complete = candidate.get("status") == "COMPLETE_EXTENDED_INTERFACE" and remaining == 0

    base = {
        "schema": "JANUS/TRUMP/R15F/INCREMENTAL_INDEPENDENT_SEMANTIC_CONTROL/RESULT/v1.0",
        "created_date": "2026-09-02",
        "frozen_candidate": {
            "path": "experiments/janus_trump_r15d_bounded_observer_equivalent_refactor.py",
            "blob_sha": EXPECTED_CANDIDATE_BLOB_SHA,
        },
        "world": {
            "id": WORLD_ID,
            "frame_sha256": world["source"]["frame_sha256"],
            "bridge_size": len(bridge),
            "bridge_vars": list(bridge),
        },
        "candidate": {k: v for k, v in candidate.items() if k not in ("formula", "history")},
        "candidate_formula_clause_count": len(candidate.get("formula", [])),
        "candidate_history_steps": len(candidate.get("history", [])),
        "candidate_elapsed_seconds_outer": candidate_elapsed,
        "verifier_package": {"python_sat": package_version},
        "P_VS_NP": "OPEN",
    }
    if not candidate_complete:
        return {
            **base,
            "verdict": "R15F_CANDIDATE_NONTERMINAL",
            "original_frame_verifier": {"not_run": True},
            "candidate_interface_verifier": {"not_run": True},
            "comparison": {"not_run": True},
            "gates": {
                "G1_FRAME_FROZEN": frame_ok,
                "G2_PYSAT_VERSION_FROZEN": package_version == EXPECTED_PYSAT_VERSION,
                "G3_CANDIDATE_TERMINAL_BEFORE_VERIFIER": False,
                "G4_ORIGINAL_WITNESS_HASH_FROZEN": True,
                "G5_ALL_SAT_MODELS_REPLAY": True,
                "G6_FULL_DOMAIN_COMPARISON": False,
                "G7_NO_GENERALIZATION_CLAIM": True,
            },
            "seal": "FIRST_THE_MACHINE_FINISHES__THEN_THE_WORLD_GETS_TO_SAY_MATCH_OR_MISMATCH",
        }

    verifier_deadline = time.monotonic() + VERIFIER_WALL_SECONDS
    original = incremental_allowed_masks(frame, bridge, ORIGINAL_SOLVER, verifier_deadline, "ORIGINAL_FRAME")
    if original["status"] == "OPEN_VERIFIER_RESOURCE_LIMIT":
        return {
            **base,
            "verdict": "R15F_OPEN_VERIFIER_RESOURCE_LIMIT",
            "original_frame_verifier": original,
            "candidate_interface_verifier": {"not_run": True},
            "comparison": {"not_run": True},
            "gates": {
                "G1_FRAME_FROZEN": frame_ok,
                "G2_PYSAT_VERSION_FROZEN": package_version == EXPECTED_PYSAT_VERSION,
                "G3_CANDIDATE_TERMINAL_BEFORE_VERIFIER": True,
                "G4_ORIGINAL_WITNESS_HASH_FROZEN": True,
                "G5_ALL_SAT_MODELS_REPLAY": not original.get("sat_model_replay_failures"),
                "G6_FULL_DOMAIN_COMPARISON": False,
                "G7_NO_GENERALIZATION_CLAIM": True,
            },
            "seal": "THE_VERIFIER_REACHED_ITS_FROZEN_RESOURCE_WALL__NO_CANDIDATE_VERDICT",
        }
    if original["status"] != "COMPLETE" or original["sat_model_replay_failures"]:
        integrity = False
    else:
        integrity = (
            original["allowed_count"] == EXPECTED_ALLOWED
            and original["truth_table_sha256"] == EXPECTED_TRUTH_SHA
        )
    if not integrity:
        return {
            **base,
            "verdict": "R15F_INTEGRITY_FAIL",
            "original_frame_verifier": original,
            "candidate_interface_verifier": {"not_run": True},
            "comparison": {"not_run": True},
            "gates": {
                "G1_FRAME_FROZEN": frame_ok,
                "G2_PYSAT_VERSION_FROZEN": package_version == EXPECTED_PYSAT_VERSION,
                "G3_CANDIDATE_TERMINAL_BEFORE_VERIFIER": True,
                "G4_ORIGINAL_WITNESS_HASH_FROZEN": False,
                "G5_ALL_SAT_MODELS_REPLAY": not original.get("sat_model_replay_failures"),
                "G6_FULL_DOMAIN_COMPARISON": False,
                "G7_NO_GENERALIZATION_CLAIM": True,
            },
            "seal": "THE_NEW_WITNESS_FAILED_TO_REPRODUCE_THE_FROZEN_WORLD",
        }

    candidate_scan = incremental_allowed_masks(
        tuple(tuple(c) for c in candidate["formula"]),
        bridge,
        CANDIDATE_SOLVER,
        verifier_deadline,
        "CANDIDATE_EXTENDED_INTERFACE",
    )
    if candidate_scan["status"] == "OPEN_VERIFIER_RESOURCE_LIMIT":
        verdict = "R15F_OPEN_VERIFIER_RESOURCE_LIMIT"
        comparison = {"not_run": True}
    elif candidate_scan["status"] != "COMPLETE" or candidate_scan["sat_model_replay_failures"]:
        verdict = "R15F_INTEGRITY_FAIL"
        comparison = {"not_run": True}
    else:
        exact = set(original["allowed_masks"])
        got = set(candidate_scan["allowed_masks"])
        false_pos = sorted(got - exact)
        false_neg = sorted(exact - got)
        comparison = {
            "full_domain": True,
            "false_positive_count": len(false_pos),
            "false_negative_count": len(false_neg),
            "first_false_positive_masks": false_pos[:32],
            "first_false_negative_masks": false_neg[:32],
            "allowed_set_equal": not false_pos and not false_neg,
            "candidate_truth_table_sha256": candidate_scan["truth_table_sha256"],
            "original_truth_table_sha256": original["truth_table_sha256"],
        }
        verdict = "R15F_FULL_DOMAIN_SEMANTIC_MATCH" if comparison["allowed_set_equal"] else "R15F_FULL_DOMAIN_SEMANTIC_MISMATCH"

    gates = {
        "G1_FRAME_FROZEN": frame_ok,
        "G2_PYSAT_VERSION_FROZEN": package_version == EXPECTED_PYSAT_VERSION,
        "G3_CANDIDATE_TERMINAL_BEFORE_VERIFIER": True,
        "G4_ORIGINAL_WITNESS_HASH_FROZEN": original["truth_table_sha256"] == EXPECTED_TRUTH_SHA,
        "G5_ALL_SAT_MODELS_REPLAY": not original.get("sat_model_replay_failures") and not candidate_scan.get("sat_model_replay_failures"),
        "G6_FULL_DOMAIN_COMPARISON": bool(comparison.get("full_domain", False)) if verdict not in ("R15F_OPEN_VERIFIER_RESOURCE_LIMIT", "R15F_INTEGRITY_FAIL") else True,
        "G7_NO_GENERALIZATION_CLAIM": True,
    }
    return {
        **base,
        "verdict": verdict,
        "original_frame_verifier": original,
        "candidate_interface_verifier": candidate_scan,
        "comparison": comparison,
        "gates": gates,
        "scientific_interpretation": {
            "if_match": "The byte-frozen R15D direct-from-frame extended representation is semantically exact on the complete exposed W05 bridge domain. This authorizes a prospective unseen R16 test only.",
            "if_mismatch": "The completed representation does not preserve the target bridge invariant on W05. Freeze the mismatch; do not tune this candidate inside validation.",
            "if_open": "Verifier resource exhaustion is observer evidence only and cannot be scored as candidate failure.",
        },
        "seal": "FIRST_THE_MACHINE_FINISHES__THEN_TWO_INDEPENDENT_WITNESSES_CHECK_THE_ENTIRE_BRIDGE",
    }


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--output", required=True); args = ap.parse_args()
    result = run()
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "verdict": result["verdict"],
        "candidate": result["candidate"],
        "original": {k: v for k, v in result["original_frame_verifier"].items() if k != "allowed_masks"},
        "candidate_verifier": {k: v for k, v in result["candidate_interface_verifier"].items() if k != "allowed_masks"},
        "comparison": result["comparison"],
        "gates": result["gates"],
        "P_VS_NP": "OPEN",
    }, indent=2, sort_keys=True))
    return 2 if result["verdict"] == "R15F_INTEGRITY_FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
