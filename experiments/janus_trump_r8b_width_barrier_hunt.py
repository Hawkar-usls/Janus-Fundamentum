#!/usr/bin/env python3
"""R8B: hostile finite hunt for a width>4 barrier to the frozen R7D tooth."""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

import janus_trump_p_vs_np_direct_challenge_r0 as direct
import janus_trump_r7d_dense_3sat_polynomial_proof_attack as r7d
import janus_trump_r7d_dense_3sat_polynomial_proof_attack_fastpath as fast


def load_tear_audit():
    path = Path(__file__).resolve().parent / "direct" / "janus_tear_resolution_width_audit.py"
    spec = importlib.util.spec_from_file_location("janus_tear_width_control_r8b", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load preexisting width control")
    mod = importlib.util.module_from_spec(spec); sys.modules[spec.name] = mod; spec.loader.exec_module(mod)
    return mod


def to_cnf(clauses):
    return direct.canon(tuple(tuple(c) for c in clauses))


def sweep(cnf, widths=(3, 4, 5)):
    out = {}
    for k in widths:
        rr = fast.subsuming_fixed_width_resolution(cnf, k)
        replay = rr.status != "UNSAT" or (rr.proof is not None and r7d.replay_resolution_proof(cnf, rr.proof, k))
        out[str(k)] = {
            "status": rr.status, "derived": rr.derived, "blocked_wide": rr.blocked_wide,
            "ops": rr.ops, "universe_bound": rr.universe_bound, "proof_replay": replay,
            "proof_steps": 0 if rr.proof is None else len(rr.proof),
        }
    return out


def run():
    tear = load_tear_audit()
    control = to_cnf(tear.tseitin_cnf())
    control_sweep = sweep(control, (3, 4))
    control_pass = (control_sweep["3"]["status"] == "SATURATION_COMPLETE_NO_REFUTATION" and
                    control_sweep["4"]["status"] == "UNSAT" and control_sweep["4"]["proof_replay"])

    php = direct.f_php(4)
    php_sweep = sweep(php, (3, 4, 5))
    elim4 = r7d.width_bounded_eliminate(php, 4)
    oracle = direct.dpll(php)
    # Run the entire frozen stack as a boundary check: R7C is allowed to solve
    # PHP structurally, so a width barrier is not automatically a full-stack barrier.
    full = r7d.r7d_candidate(php)

    barrier = (php_sweep["4"]["status"] == "SATURATION_COMPLETE_NO_REFUTATION" and
               php_sweep["5"]["status"] == "UNSAT" and php_sweep["5"]["proof_replay"])
    consistency = not (barrier and elim4.status == "UNSAT")
    gates = {
        "G1_CONTROL_MIN_WIDTH4_REPRODUCED": control_pass,
        "G2_PHP4_MAX_INPUT_WIDTH4": max(len(c) for c in php) == 4,
        "G3_PHP4_SHADOW_UNSAT": oracle["status"] == "EXACT" and oracle["sat"] is False,
        "G4_WIDTH5_PROOF_REPLAYS_IF_CLAIMED": php_sweep["5"]["status"] != "UNSAT" or php_sweep["5"]["proof_replay"],
        "G5_ELIMINATION_CONSISTENCY": consistency,
        "G6_NO_THEOREM_INFLATION": True,
    }
    integrity = all(gates.values())
    if not integrity:
        verdict = "R8B_INTEGRITY_FAIL__P_VS_NP_OPEN"
    elif barrier:
        verdict = "R8B_FIXED_WIDTH4_STANDALONE_ROUTE_KILLED__FINITE_WIDTH5_WITNESS__P_VS_NP_OPEN"
    else:
        verdict = "R8B_NO_WIDTH4_BARRIER_FOUND_IN_FROZEN_PHP4_TEST__P_VS_NP_OPEN"
    return {
        "schema": "JANUS/TRUMP/R8B/WIDTH_BARRIER_HUNT/RESULT/v1.0",
        "status": "FROZEN_RESULT", "verdict": verdict,
        "control": {"family": "K4_TSEITIN_EXISTING_AUDIT", "width_sweep": control_sweep},
        "target": {"family": "PIGEONHOLE_PHP", "h": 4, "variables": len(direct.variables(php)),
                   "clauses": len(php), "max_input_width": max(len(c) for c in php),
                   "width_sweep": php_sweep,
                   "width4_elimination": {"status": elim4.status, "safe_steps": len(elim4.records),
                                           "blocked_pivot_witnesses": elim4.blocked_pivots[:32], "ops": elim4.ops},
                   "shadow_dpll": oracle,
                   "full_frozen_stack": full.as_dict()},
        "barrier_found": barrier,
        "gates": gates,
        "scientific_reading": {
            "if_barrier": "A replayable width-5 refutation together with complete width-4 non-refutation is a finite counterexample to fixed k=4 resolution as a universal standalone proof route. It does not refute the full TRUMP stack because structural polynomial rules may solve the same formula.",
            "claim_ceiling": "No result here proves P=NP or P!=NP. A finite barrier only falsifies universal fixed-width-4 standalone totality."
        },
        "P_VS_NP": "OPEN"
    }


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--output", required=True); args = ap.parse_args()
    result = run(); Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"verdict": result["verdict"], "barrier_found": result["barrier_found"], "gates": result["gates"], "target": result["target"], "P_VS_NP": result["P_VS_NP"]}, indent=2))
    return 0 if all(result["gates"].values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
