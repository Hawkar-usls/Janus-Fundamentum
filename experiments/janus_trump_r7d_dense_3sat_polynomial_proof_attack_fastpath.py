#!/usr/bin/env python3
"""Execution-order and subsumption optimization for frozen R7D.

The preregistered proof rules and frozen width k=4 are unchanged. We first try
exact width-bounded elimination directly; only an OPEN width barrier proceeds to
fixed-width resolution saturation. Saturation uses standard subsumption deletion
so only currently minimal clauses participate. This changes execution cost, not
logical/theorem authority.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict, deque
from pathlib import Path

import janus_trump_r7d_dense_3sat_polynomial_proof_attack as base


def subsuming_fixed_width_resolution(cnf, k=base.WIDTH_K):
    f = base.canon(cnf)
    ub = base.clause_universe_bound(len(base.variables(f)), k)
    if any(len(c) > k for c in f):
        return base.ResolutionResult("OPEN_INPUT_WIDTH", f, 0, 0, 0, None, ub)
    if () in f:
        proof = [{"clause": [], "kind": "AXIOM"}]
        return base.ResolutionResult("UNSAT", f, 1, 0, 0, proof, ub)

    all_known = set(f)
    active = set(f)
    parents = {c: None for c in f}
    index = defaultdict(set)
    agenda = deque(sorted(f, key=base.clause_key))
    ops = 0
    derived = 0
    blocked = 0

    while agenda:
        c = agenda.popleft()
        if c not in active:
            continue
        for lit in c:
            for d in list(index.get(-lit, ())):
                if d not in active:
                    continue
                ops += len(c) + len(d) + 1
                rr = base.resolve_pair(c, d, lit)
                if rr is None:
                    continue
                if len(rr) > k:
                    blocked += 1
                    continue
                if rr in all_known:
                    continue
                sr = set(rr)
                # If an active stronger clause already exists, rr is redundant.
                if any(set(e).issubset(sr) for e in active):
                    continue
                all_known.add(rr)
                parents[rr] = (c, d, lit)
                derived += 1
                if rr == ():
                    proof = base.proof_ancestors(rr, parents)
                    if not base.replay_resolution_proof(f, proof, k):
                        return base.ResolutionResult("INTERNAL_PROOF_REPLAY_FAILURE", base.canon(tuple(active | {rr})), ops, derived, blocked, proof, ub)
                    return base.ResolutionResult("UNSAT", base.canon(tuple(active | {rr})), ops, derived, blocked, proof, ub)

                # Standard subsumption deletion: the new stronger clause replaces
                # active supersets. Parent records remain immutable for proof DAGs.
                supersets = [e for e in active if sr.issubset(set(e)) and e != rr]
                for e in supersets:
                    active.discard(e)
                active.add(rr)
                agenda.append(rr)
                if len(all_known) > ub:
                    return base.ResolutionResult("INTERNAL_UNIVERSE_BOUND_FAILURE", base.canon(tuple(active)), ops, derived, blocked, None, ub)
        for lit in c:
            index[lit].add(c)

    return base.ResolutionResult("SATURATION_COMPLETE_NO_REFUTATION", base.canon(tuple(active)), ops, derived, blocked, None, ub)


# Same frozen logical rule, optimized implementation.
base.fixed_width_resolution = subsuming_fixed_width_resolution


def fast_attack_component(part):
    f = base.canon(part)

    first = base.width_bounded_eliminate(f, base.WIDTH_K)
    ops = first.ops
    if first.status == "UNSAT":
        return {
            "status": "UNSAT",
            "class": "WIDTH4_EXACT_ELIMINATION",
            "assignment": None,
            "ops": ops,
            "certificate": {"type": "WIDTH4_EXACT_ELIMINATION_REFUTATION", "phase": "PRE_SATURATION", "width": base.WIDTH_K, "records": first.records, "final_cnf": [list(c) for c in first.final_cnf]},
        }
    if first.status == "SAT":
        if first.witness is not None and base.r7b.verify_sat(f, first.witness):
            return {
                "status": "SAT",
                "class": "WIDTH4_EXACT_ELIMINATION",
                "assignment": first.witness,
                "ops": ops,
                "certificate": {"type": "WIDTH4_EXACT_ELIMINATION_MODEL", "phase": "PRE_SATURATION", "width": base.WIDTH_K, "records": first.records},
            }
        return {"status": "OPEN", "class": "WIDTH4_RECONSTRUCTION_FAILURE", "assignment": None, "ops": ops, "certificate": {"type": "PRE_SATURATION_MODEL_REPLAY_FAILED"}}

    rr = base.fixed_width_resolution(f, base.WIDTH_K)
    ops += rr.ops
    if rr.status == "UNSAT":
        return {
            "status": "UNSAT",
            "class": "WIDTH4_RESOLUTION_REFUTATION",
            "assignment": None,
            "ops": ops,
            "certificate": {"type": "WIDTH4_RESOLUTION_REFUTATION", "width": base.WIDTH_K, "proof": rr.proof, "derived_clauses": rr.derived, "blocked_wide_resolvents": rr.blocked_wide, "clause_universe_bound": rr.universe_bound},
        }
    if rr.status != "SATURATION_COMPLETE_NO_REFUTATION":
        return {"status": "OPEN", "class": "WIDTH4_UNSUPPORTED", "assignment": None, "ops": ops, "certificate": {"type": rr.status}}

    second = base.width_bounded_eliminate(rr.saturated, base.WIDTH_K)
    ops += second.ops
    if second.status == "UNSAT":
        return {
            "status": "UNSAT",
            "class": "WIDTH4_EXACT_ELIMINATION",
            "assignment": None,
            "ops": ops,
            "certificate": {"type": "WIDTH4_EXACT_ELIMINATION_REFUTATION", "phase": "POST_SATURATION", "width": base.WIDTH_K, "records": second.records, "final_cnf": [list(c) for c in second.final_cnf]},
        }
    if second.status == "SAT":
        if second.witness is not None and base.r7b.verify_sat(f, second.witness):
            return {
                "status": "SAT",
                "class": "WIDTH4_EXACT_ELIMINATION",
                "assignment": second.witness,
                "ops": ops,
                "certificate": {"type": "WIDTH4_EXACT_ELIMINATION_MODEL", "phase": "POST_SATURATION", "width": base.WIDTH_K, "records": second.records, "saturation_derived_clauses": rr.derived},
            }
        return {"status": "OPEN", "class": "WIDTH4_RECONSTRUCTION_FAILURE", "assignment": None, "ops": ops, "certificate": {"type": "POST_SATURATION_MODEL_REPLAY_FAILED"}}

    return {
        "status": "OPEN",
        "class": "WIDTH4_BARRIER",
        "assignment": None,
        "ops": ops,
        "certificate": {"type": second.status, "width": base.WIDTH_K, "pre_saturation_safe_steps": len(first.records), "post_saturation_safe_steps": len(second.records), "remaining_variables": len(base.variables(second.final_cnf)), "remaining_clauses": len(second.final_cnf), "blocked_pivot_witnesses": second.blocked_pivots[:32], "saturation_derived_clauses": rr.derived, "blocked_wide_resolvents": rr.blocked_wide},
    }


base.attack_component = fast_attack_component


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    result = base.run()
    result["execution_order"] = "WIDTH4_EXACT_ELIMINATION -> IF_OPEN SUBSUMPTION_WIDTH4_RESOLUTION_SATURATION -> WIDTH4_EXACT_ELIMINATION"
    result["optimization"] = "STANDARD_SUBSUMPTION_DELETION_ONLY__FROZEN_LOGICAL_RULES_UNCHANGED"
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"verdict": result["verdict"], "summary": result["summary"], "gates": result["gates"], "candidate_source_firewall": result["candidate_source_firewall"], "P_VS_NP": result["P_VS_NP"]}, indent=2))
    return 0 if all(result["gates"].values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
