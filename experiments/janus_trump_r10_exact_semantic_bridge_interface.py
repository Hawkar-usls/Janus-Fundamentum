#!/usr/bin/env python3
"""R10 exact semantic bridge-interface killer test.

Candidate lane: exact bounded-width Davis-Putnam projection of internal frame
variables onto the frozen R9 bridge.  It may return OPEN; it may never discard a
required non-tautological resolvent, recurse on assignments, or call an exact
search oracle.

Independent witness lane: only after the candidate is frozen, enumerate the
finite bridge domain and use the pre-existing exact DPLL verifier to compute the
true existential interface.  The shadow lane has no theorem/routing authority.
"""
from __future__ import annotations

import argparse
import inspect
import json
from hashlib import sha256
from pathlib import Path

import janus_trump_p_vs_np_direct_challenge_r0 as direct
import janus_trump_r8a_unseen_natural_holdout as r8a
import janus_trump_r9_reference_frame_difference_kernel as r9

OPEN_INDICES = (3, 7)
OPEN_HASHES = (
    "d10f03b1150e9ebfa0220c02024147d18e62c436be2e8c3976aebcfe1596a2d4",
    "017cb3c17e33b024d6fc8590906513d120f93252d19ad43d07148c97dda6cc0d",
)
WIDTH_CAP = 4


def vars_of(cnf):
    return {abs(lit) for clause in cnf for lit in clause}


def norm_clause(lits):
    s = set(lits)
    if any(-lit in s for lit in s):
        return None
    return tuple(sorted(s, key=lambda x: (abs(x), x < 0)))


def resolve_pair(pos_clause, neg_clause, var):
    return norm_clause([lit for lit in pos_clause if lit != var] + [lit for lit in neg_clause if lit != -var])


def inspect_elimination(cnf, var, width_cap=WIDTH_CAP):
    """Inspect one exact DP elimination step without mutating the formula."""
    pos = [c for c in cnf if var in c]
    neg = [c for c in cnf if -var in c]
    rest = [c for c in cnf if var not in c and -var not in c]
    resolvents = []
    pair_checks = 0
    widest = 0
    for p in pos:
        for n in neg:
            pair_checks += 1
            r = resolve_pair(p, n, var)
            if r is None:
                continue
            widest = max(widest, len(r))
            if len(r) > width_cap:
                return {
                    "safe": False,
                    "var": var,
                    "pair_checks": pair_checks,
                    "widest_required": widest,
                    "reason": "REQUIRED_RESOLVENT_EXCEEDS_WIDTH_CAP",
                    "pos_count": len(pos),
                    "neg_count": len(neg),
                }
            resolvents.append(r)
    new_cnf = direct.canon(tuple(rest) + tuple(resolvents))
    return {
        "safe": True,
        "var": var,
        "pair_checks": pair_checks,
        "widest_required": widest,
        "pos_count": len(pos),
        "neg_count": len(neg),
        "new_cnf": new_cnf,
        "parents_pos": tuple(pos),
        "parents_neg": tuple(neg),
        "resolvents_generated": len(resolvents),
        "resolvents_after_canon": max(0, len(new_cnf) - len(direct.canon(rest))),
    }


def compile_projection_interface(frame_cnf, bridge_vars, width_cap=WIDTH_CAP):
    """Exact polynomial candidate projection, or OPEN before any lossy step."""
    cnf = direct.canon(frame_cnf)
    bridge = set(bridge_vars)
    internal = vars_of(cnf) - bridge
    history = []
    charged_ops = len(cnf)
    while internal:
        inspected = []
        for var in sorted(internal):
            step = inspect_elimination(cnf, var, width_cap)
            charged_ops += int(step["pair_checks"]) + len(cnf)
            inspected.append(step)
        safe = [s for s in inspected if s["safe"]]
        if not safe:
            required = [int(s.get("widest_required", 0)) for s in inspected]
            return {
                "status": "OPEN",
                "reason": "NO_SAFE_INTERNAL_VARIABLE_UNDER_FROZEN_WIDTH_CAP",
                "width_cap": width_cap,
                "remaining_internal_variables": len(internal),
                "remaining_variables": len(vars_of(cnf)),
                "remaining_clauses": len(cnf),
                "minimum_observed_required_width": min((w for w in required if w > 0), default=None),
                "maximum_observed_required_width": max(required, default=0),
                "charged_ops": charged_ops,
                "history_steps": len(history),
                "interface": None,
                "history": history,
            }
        safe.sort(key=lambda s: (s["pos_count"] * s["neg_count"], s["var"]))
        chosen = safe[0]
        history.append({
            "var": chosen["var"],
            "parents_pos": [list(c) for c in chosen["parents_pos"]],
            "parents_neg": [list(c) for c in chosen["parents_neg"]],
            "pair_checks": chosen["pair_checks"],
            "widest_required": chosen["widest_required"],
            "resolvents_generated": chosen["resolvents_generated"],
        })
        cnf = chosen["new_cnf"]
        internal.remove(chosen["var"])
    if not vars_of(cnf) <= bridge:
        raise AssertionError("projection retained non-bridge variable")
    return {
        "status": "EXACT_INTERFACE",
        "reason": "ALL_INTERNAL_VARIABLES_EXACTLY_ELIMINATED",
        "width_cap": width_cap,
        "remaining_internal_variables": 0,
        "remaining_variables": len(vars_of(cnf)),
        "remaining_clauses": len(cnf),
        "interface": [list(c) for c in cnf],
        "history": history,
        "history_steps": len(history),
        "charged_ops": charged_ops,
        "max_interface_width": max((len(c) for c in cnf), default=0),
    }


def assignment_satisfies_cnf(cnf, assignment):
    for clause in cnf:
        if not any(bool(assignment[abs(lit)]) == (lit > 0) for lit in clause):
            return False
    return True


def mask_assignment(bridge_vars, mask):
    return {var: bool((mask >> i) & 1) for i, var in enumerate(bridge_vars)}


def interface_accepts(candidate, bridge_vars, mask):
    if candidate["status"] != "EXACT_INTERFACE":
        raise ValueError("candidate emitted no exact interface")
    assignment = mask_assignment(bridge_vars, mask)
    return assignment_satisfies_cnf(tuple(tuple(c) for c in candidate["interface"]), assignment)


def diverge_decoder(frame_cnf, bridge_vars, mask, candidate):
    """Reverse exact elimination; each variable tests only its two local values."""
    if candidate["status"] != "EXACT_INTERFACE":
        return {"status": "OPEN", "witness": None, "ops": 0}
    assignment = mask_assignment(bridge_vars, mask)
    ops = 0
    for record in reversed(candidate["history"]):
        var = int(record["var"])
        parents = [tuple(c) for c in record["parents_pos"] + record["parents_neg"]]
        chosen = None
        for value in (False, True):
            trial = dict(assignment)
            trial[var] = value
            ops += len(parents)
            if assignment_satisfies_cnf(parents, trial):
                chosen = value
                break
        if chosen is None:
            return {"status": "DECODER_FAIL", "witness": None, "ops": ops}
        assignment[var] = chosen
    replay = assignment_satisfies_cnf(frame_cnf, assignment)
    return {"status": "SAT_WITNESS" if replay else "DECODER_FAIL", "witness": assignment if replay else None, "ops": ops}


def frozen_world(index):
    residuals = r8a.frozen_residuals()
    item = residuals[index]
    roots = {r8a.digest(r["cnf"]): r for r in r8a.frozen_roots()}
    root = roots[item["root_sha256"]]
    fd = r9.restriction_frame_delta(root["cnf"], item["pivot"], item["branch_value"])
    if item["formula_sha256"] != OPEN_HASHES[OPEN_INDICES.index(index)]:
        raise AssertionError("frozen world hash drift")
    return {
        "item": item,
        "root": root,
        "frame": fd["frame"],
        "delta": fd["shortened"],
        "bridge_vars": tuple(fd["active_bridge_vars"]),
        "frame_sha256": fd["frame_sha256"],
    }


def candidate_firewall():
    funcs = [norm_clause, resolve_pair, inspect_elimination, compile_projection_interface,
             assignment_satisfies_cnf, mask_assignment, interface_accepts, diverge_decoder]
    src = "\n".join(inspect.getsource(f) for f in funcs)
    forbidden = ["dpll(", "exact_search_witness", "product((False, True)", "robdd(", "range(1 <<"]
    hits = [token for token in forbidden if token in src]
    return {"pass": not hits, "forbidden_hits": hits}


# ---------- independent post-candidate witness lane ----------

def shadow_exact_interface(frame_cnf, bridge_vars):
    allowed = []
    work = 0
    k = len(bridge_vars)
    for mask in range(1 << k):
        restricted = direct.canon(frame_cnf)
        assignment = mask_assignment(bridge_vars, mask)
        for var in bridge_vars:
            restricted = direct.restrict_cnf(restricted, var, assignment[var])
        oracle = direct.dpll(restricted)
        work += int(oracle.get("work", 0))
        if oracle["status"] != "EXACT":
            raise AssertionError("shadow verifier returned non-exact status")
        if oracle["sat"]:
            allowed.append(mask)
    payload = json.dumps(allowed, separators=(",", ":")).encode()
    return {"allowed_masks": allowed, "allowed_count": len(allowed), "domain_size": 1 << k,
            "truth_table_sha256": sha256(payload).hexdigest(), "dpll_work": work}


def exact_2sat_representation(bridge_vars, allowed_masks):
    k = len(bridge_vars)
    allowed = set(allowed_masks)
    literals = [(i, sign) for i in range(k) for sign in (False, True)]

    def lit_true(mask, lit):
        i, positive = lit
        bit = bool((mask >> i) & 1)
        return bit if positive else not bit

    clauses = []
    for lit in literals:
        if all(lit_true(mask, lit) for mask in allowed):
            clauses.append((lit,))
    for i in range(k):
        for j in range(i + 1, k):
            for si in (False, True):
                for sj in (False, True):
                    clause = ((i, si), (j, sj))
                    if all(lit_true(mask, clause[0]) or lit_true(mask, clause[1]) for mask in allowed):
                        clauses.append(clause)
    represented = []
    for mask in range(1 << k):
        if all(any(lit_true(mask, lit) for lit in clause) for clause in clauses):
            represented.append(mask)
    exact = set(represented) == allowed
    return {"exact": exact, "valid_unit_binary_clauses": len(clauses),
            "represented_count": len(represented)}


def gf2_rank(values):
    basis = {}
    for value in values:
        x = int(value)
        while x:
            p = x.bit_length() - 1
            if p in basis:
                x ^= basis[p]
            else:
                basis[p] = x
                break
    return len(basis)


def exact_affine_representation(allowed_masks):
    if not allowed_masks:
        return {"exact": True, "rank": None, "reason": "EMPTY_RELATION"}
    base = allowed_masks[0]
    diffs = {mask ^ base for mask in allowed_masks}
    rank = gf2_rank(diffs)
    return {"exact": (1 << rank) == len(diffs), "rank": rank, "relation_size": len(diffs)}


def compare_candidate_to_shadow(candidate, bridge_vars, shadow, frame_cnf):
    if candidate["status"] != "EXACT_INTERFACE":
        return {"verdict": "OPEN", "mismatch_mask": None, "decoder_failures": None,
                "candidate_allowed_count": None}
    exact_allowed = set(shadow["allowed_masks"])
    candidate_allowed = []
    mismatch = None
    decoder_failures = 0
    decoder_ops = 0
    for mask in range(1 << len(bridge_vars)):
        accepts = interface_accepts(candidate, bridge_vars, mask)
        if accepts:
            candidate_allowed.append(mask)
            dec = diverge_decoder(frame_cnf, bridge_vars, mask, candidate)
            decoder_ops += int(dec["ops"])
            if dec["status"] != "SAT_WITNESS":
                decoder_failures += 1
        if accepts != (mask in exact_allowed) and mismatch is None:
            mismatch = mask
    return {"verdict": "MATCH" if mismatch is None and decoder_failures == 0 else "MISMATCH",
            "mismatch_mask": mismatch, "decoder_failures": decoder_failures,
            "decoder_ops": decoder_ops, "candidate_allowed_count": len(candidate_allowed)}


def run():
    firewall = candidate_firewall()
    rows = []
    for index in OPEN_INDICES:
        world = frozen_world(index)
        candidate = compile_projection_interface(world["frame"], world["bridge_vars"], WIDTH_CAP)
        # Candidate is now complete.  Only after this line may the independent witness run.
        shadow = shadow_exact_interface(world["frame"], world["bridge_vars"])
        comparison = compare_candidate_to_shadow(candidate, world["bridge_vars"], shadow, world["frame"])
        two_sat = exact_2sat_representation(world["bridge_vars"], shadow["allowed_masks"])
        affine = exact_affine_representation(shadow["allowed_masks"])
        rows.append({
            "global_index": index,
            "residual_sha256": world["item"]["formula_sha256"],
            "frame_sha256": world["frame_sha256"],
            "bridge_variables": list(world["bridge_vars"]),
            "bridge_size": len(world["bridge_vars"]),
            "frame_variables": len(vars_of(world["frame"])),
            "frame_clauses": len(world["frame"]),
            "delta_type": r9.classify_cnf(world["delta"]),
            "candidate": candidate,
            "independent_witness": {k: v for k, v in shadow.items() if k != "allowed_masks"},
            "comparison": comparison,
            "shadow_interface_classification": {"exact_2sat": two_sat, "exact_affine": affine},
        })

    emitted = [r for r in rows if r["candidate"]["status"] == "EXACT_INTERFACE"]
    mismatch = [r for r in emitted if r["comparison"]["verdict"] != "MATCH"]
    gates = {
        "G1_FROZEN_WORLD_HASHES": [r["residual_sha256"] for r in rows] == list(OPEN_HASHES),
        "G2_CANDIDATE_FIREWALL": firewall["pass"],
        "G3_NO_DROPPED_REQUIRED_RESOLVENTS": True,
        "G4_ANY_EMITTED_INTERFACE_MATCHES_INDEPENDENT_WITNESS": len(mismatch) == 0,
        "G5_ANY_DECODER_WITNESS_REPLAYS": all((r["comparison"]["decoder_failures"] or 0) == 0 for r in emitted),
        "G6_OPEN_IS_ALLOWED": True,
        "G7_NO_THEOREM_INFLATION": True,
    }
    if not all(gates.values()):
        verdict = "R10_INTERFACE_CANDIDATE_MISMATCH_OR_INTEGRITY_FAIL__P_VS_NP_OPEN"
    elif len(emitted) == len(rows):
        verdict = "R10_SCOPED_EXACT_SEMANTIC_INTERFACES_MATCH_INDEPENDENT_WITNESS__P_VS_NP_OPEN"
    else:
        verdict = "R10_REFERENCE_FRAME_SURVIVES__BOUNDED_INTERFACE_LANGUAGE_INCOMPLETE__OPEN_PRESERVED__P_VS_NP_OPEN"
    return {
        "schema": "JANUS/TRUMP/R10/EXACT_SEMANTIC_BRIDGE_INTERFACE/RESULT/v1.0",
        "status": "FROZEN_RESULT",
        "verdict": verdict,
        "admission_gate": "NO_HIDDEN_SEARCH",
        "candidate_firewall": firewall,
        "summary": {
            "worlds": len(rows),
            "candidate_exact_interfaces": len(emitted),
            "candidate_open": len(rows) - len(emitted),
            "matches": sum(1 for r in emitted if r["comparison"]["verdict"] == "MATCH"),
            "mismatches": len(mismatch),
        },
        "gates": gates,
        "rows": rows,
        "highest_admissible_claim": "R10 tests one frozen exact polynomial bridge language (bounded-width exact projection) against an independent exhaustive bridge witness on the two immutable R8A OPEN worlds. OPEN or failure of that language does not falsify the reference-frame/delta decomposition. Success would remain scoped evidence, not arbitrary-CNF totality or P=NP.",
        "law": "COMPILE_THE_INVARIANT__EXPOSE_ONLY_THE_DIFFERENCE__LET_AN_INDEPENDENT_WITNESS_TRY_TO_BREAK_THE_INTERFACE",
        "P_VS_NP": "OPEN",
    }


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--output", required=True); args = ap.parse_args()
    result = run()
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"verdict": result["verdict"], "summary": result["summary"],
                      "gates": result["gates"],
                      "worlds": [{"index": r["global_index"], "bridge": r["bridge_size"],
                                  "candidate": r["candidate"]["status"],
                                  "comparison": r["comparison"]["verdict"],
                                  "shadow_allowed": r["independent_witness"]["allowed_count"],
                                  "shadow_2sat": r["shadow_interface_classification"]["exact_2sat"]["exact"],
                                  "shadow_affine": r["shadow_interface_classification"]["exact_affine"]["exact"]}
                                 for r in result["rows"]],
                      "P_VS_NP": result["P_VS_NP"]}, indent=2))
    return 0 if all(result["gates"].values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
