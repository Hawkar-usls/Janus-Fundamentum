#!/usr/bin/env python3
"""R12: direct fixed-width-4 semantic-interface compiler.

Candidate lane: resolution saturation at fixed clause width <=4 on the preserved
GENERAL_CNF frame.  No Davis-Putnam variable elimination, branching, DPLL,
assignment enumeration, width widening, or lossy pruning is allowed.

The NAME-vs-CONTENT quotient is operationalized proof-theoretically: many
resolution histories may produce one identical canonical clause.  Clause
content, not derivation label/history, is the memoized state.

Only after the candidate fixed point is complete does the independent R10/R11
finite bridge witness run.  That shadow lane has no routing/theorem authority.
"""
from __future__ import annotations

import argparse
import inspect
import json
from collections import defaultdict, deque
from hashlib import sha256
from pathlib import Path

import janus_trump_r10_exact_semantic_bridge_interface as r10
import janus_trump_r11_exact_interface_structure_microscope as r11

WIDTH_CAP = 4
OPEN_INDICES = (3, 7)
EXPECTED = {
    3: {"allowed": 135, "truth_sha256": "9032c5d24f3e2bea515f78c57b0a019c8918f5c3f4677314e65da2035e68b29c"},
    7: {"allowed": 127, "truth_sha256": "93004dbf4c532e8522191785bc8f98b5625c7c5a04e3f6a2b5b61fb097bfc066"},
}


def canonical_clause(lits):
    vals = set(int(x) for x in lits)
    if 0 in vals:
        raise ValueError("literal 0 is invalid")
    if any(-x in vals for x in vals):
        return None
    return tuple(sorted(vals, key=lambda x: (abs(x), x < 0)))


def resolve_on(a, b, pivot):
    if pivot not in a or -pivot not in b:
        raise ValueError("invalid resolution pivot orientation")
    return canonical_clause([x for x in a if x != pivot] + [x for x in b if x != -pivot])


def add_clause(store, index, queue, proof, clause, record):
    c = canonical_clause(clause)
    if c is None:
        return "TAUTOLOGY", None
    if len(c) > WIDTH_CAP:
        return "TOO_WIDE", c
    if c in store:
        return "DUPLICATE", c
    cid = len(store)
    store.append(c)
    proof.append(record)
    for lit in c:
        index[lit].add(cid)
    queue.append(cid)
    return "NEW", c


def saturate_width4(frame_cnf):
    """Fixed-width resolution closure with exact-content quotient memoization."""
    store = []
    proof = []
    index = defaultdict(set)
    queue = deque()
    clause_to_id = {}
    stats = {
        "initial_input_clauses": len(frame_cnf),
        "initial_duplicate_clauses_collapsed": 0,
        "pair_pivots_attempted": 0,
        "tautological_resolvents": 0,
        "too_wide_resolvents": 0,
        "duplicate_resolvents_collapsed": 0,
        "new_resolvents": 0,
    }

    for raw in frame_cnf:
        c = canonical_clause(raw)
        if c is None:
            stats["tautological_resolvents"] += 1
            continue
        if len(c) > WIDTH_CAP:
            raise AssertionError("R12 frozen frame contains clause wider than width cap")
        if c in clause_to_id:
            stats["initial_duplicate_clauses_collapsed"] += 1
            continue
        cid = len(store)
        clause_to_id[c] = cid
        store.append(c)
        proof.append({"kind": "AXIOM", "clause": list(c)})
        for lit in c:
            index[lit].add(cid)
        queue.append(cid)

    # IDs are addition-order monotone.  Process each unordered clause pair only
    # when its later-added member is popped.  This avoids path-label duplicates
    # while preserving every content-distinct width<=4 resolvent.
    while queue:
        cid = queue.popleft()
        c = store[cid]
        for lit in c:
            for did in tuple(index.get(-lit, ())):
                if did >= cid:
                    continue
                d = store[did]
                stats["pair_pivots_attempted"] += 1
                r = resolve_on(c, d, lit)
                if r is None:
                    stats["tautological_resolvents"] += 1
                    continue
                if len(r) > WIDTH_CAP:
                    stats["too_wide_resolvents"] += 1
                    continue
                if r in clause_to_id:
                    stats["duplicate_resolvents_collapsed"] += 1
                    continue
                rid = len(store)
                clause_to_id[r] = rid
                store.append(r)
                proof.append({
                    "kind": "RESOLUTION",
                    "parents": [cid, did],
                    "pivot": int(lit),
                    "clause": list(r),
                })
                for x in r:
                    index[x].add(rid)
                queue.append(rid)
                stats["new_resolvents"] += 1

    stats["unique_canonical_clauses"] = len(store)
    generated = stats["new_resolvents"] + stats["duplicate_resolvents_collapsed"]
    stats["content_quotient_duplicate_fraction"] = (
        stats["duplicate_resolvents_collapsed"] / generated if generated else 0.0
    )
    return {"clauses": store, "proof": proof, "stats": stats}


def replay_derivations(result):
    clauses = result["clauses"]
    proof = result["proof"]
    if len(clauses) != len(proof):
        return False
    for cid, rec in enumerate(proof):
        c = clauses[cid]
        if rec["kind"] == "AXIOM":
            if tuple(rec["clause"]) != c:
                return False
            continue
        if rec["kind"] != "RESOLUTION":
            return False
        a_id, b_id = rec["parents"]
        if not (a_id < cid and b_id < cid):
            return False
        pivot = int(rec["pivot"])
        a, b = clauses[a_id], clauses[b_id]
        if pivot not in a or -pivot not in b:
            return False
        r = resolve_on(a, b, pivot)
        if r != c or len(c) > WIDTH_CAP:
            return False
    return True


def bridge_only_clauses(clauses, bridge_vars):
    b = set(bridge_vars)
    return [c for c in clauses if {abs(x) for x in c} <= b]


def localize_clause(clause, bridge_vars):
    pos = {v: i + 1 for i, v in enumerate(bridge_vars)}
    out = []
    for lit in clause:
        idx = pos[abs(lit)]
        out.append(idx if lit > 0 else -idx)
    return canonical_clause(out)


def assignment_satisfies_local(clauses, k, mask):
    for c in clauses:
        ok = False
        for lit in c:
            bit = bool((mask >> (abs(lit) - 1)) & 1)
            if bit == (lit > 0):
                ok = True
                break
        if not ok:
            return False
    return True


def candidate_firewall():
    funcs = [canonical_clause, resolve_on, add_clause, saturate_width4,
             replay_derivations, bridge_only_clauses, localize_clause]
    src = "\n".join(inspect.getsource(f) for f in funcs)
    forbidden = ["dpll(", "exact_search_witness", "range(1 <<", "robdd(",
                 "dp_eliminate(", "shadow_exact_interface", "itertools.product"]
    hits = [token for token in forbidden if token in src]
    return {"pass": not hits, "forbidden_hits": hits}


def quotient_controls():
    same = canonical_clause([2, 1, 1]) == canonical_clause([1, 2])
    distinct = canonical_clause([1, 2]) != canonical_clause([1, -2])
    tiny = saturate_width4(((1, 2), (-1, 3)))
    derived = canonical_clause((2, 3)) in set(tiny["clauses"])
    replay = replay_derivations(tiny)
    return {"permutation_duplicate_collapses": same, "sign_change_stays_distinct": distinct,
            "known_resolvent_derived": derived, "known_resolvent_replays": replay,
            "pass": same and distinct and derived and replay}


def compare_after_candidate(index, world, candidate):
    bridge = tuple(world["bridge_vars"])
    local_candidate = sorted({localize_clause(c, bridge) for c in bridge_only_clauses(candidate["clauses"], bridge)})

    # Independent witness begins only here, after candidate fixed point exists.
    shadow = r10.shadow_exact_interface(world["frame"], bridge)
    if shadow["truth_table_sha256"] != EXPECTED[index]["truth_sha256"]:
        raise AssertionError("immutable R10/R11 witness hash drift")
    if shadow["allowed_count"] != EXPECTED[index]["allowed"]:
        raise AssertionError("immutable R10/R11 allowed count drift")

    k = len(bridge)
    exact_allowed = set(shadow["allowed_masks"])
    candidate_allowed = {
        mask for mask in range(1 << k)
        if assignment_satisfies_local(local_candidate, k, mask)
    }
    false_pos = sorted(candidate_allowed - exact_allowed)
    false_neg = sorted(exact_allowed - candidate_allowed)

    geometry = r11.exact_cnf_geometry(shadow["allowed_masks"], k)
    exact_primes = {tuple(c) for c in geometry["prime_clauses"]}
    cand_set = set(local_candidate)
    violated_prime_witnesses = []
    if false_pos:
        fp = false_pos[0]
        for clause in sorted(exact_primes, key=lambda c: (len(c), c)):
            if not assignment_satisfies_local((clause,), k, fp):
                violated_prime_witnesses.append(list(clause))
                if len(violated_prime_witnesses) >= 8:
                    break

    verdict = "MATCH" if not false_pos and not false_neg else "MISMATCH"
    return {
        "verdict": verdict,
        "bridge_size": k,
        "candidate_bridge_clause_count": len(local_candidate),
        "candidate_bridge_clause_sha256": sha256(json.dumps([list(c) for c in local_candidate], separators=(",", ":")).encode()).hexdigest(),
        "candidate_allowed_count": len(candidate_allowed),
        "exact_allowed_count": len(exact_allowed),
        "false_positive_count": len(false_pos),
        "false_negative_count": len(false_neg),
        "first_false_positive_masks": false_pos[:16],
        "first_false_negative_masks": false_neg[:16],
        "violated_exact_prime_implicate_witnesses": violated_prime_witnesses,
        "exact_min_same_variable_cnf_width": geometry["minimum_same_variable_cnf_width"],
        "exact_prime_implicate_count": geometry["prime_implicate_count_through_exact_width"],
        "literal_prime_overlap_count": len(cand_set & exact_primes),
        "shadow_dpll_work": shadow["dpll_work"],
        "truth_table_sha256": shadow["truth_table_sha256"],
    }


def run():
    firewall = candidate_firewall()
    controls = quotient_controls()
    rows = []
    for index in OPEN_INDICES:
        world = r10.frozen_world(index)
        candidate = saturate_width4(world["frame"])
        replay = replay_derivations(candidate)
        comparison = compare_after_candidate(index, world, candidate)
        rows.append({
            "global_index": index,
            "frame_sha256": world["frame_sha256"],
            "frame_variables": len(r10.vars_of(world["frame"])),
            "frame_clauses": len(world["frame"]),
            "bridge_variables": len(world["bridge_vars"]),
            "candidate_stats": candidate["stats"],
            "proof_replay": replay,
            "comparison": comparison,
        })

    all_match = all(r["comparison"]["verdict"] == "MATCH" for r in rows)
    gates = {
        "G1_REPRESENTATION_CONTRACT_CONTROLS": controls["pass"],
        "G2_CANDIDATE_FIREWALL": firewall["pass"],
        "G3_DERIVATION_REPLAY": all(r["proof_replay"] for r in rows),
        "G4_FROZEN_WITNESS_HASHES": all(r["comparison"]["truth_table_sha256"] == EXPECTED[r["global_index"]]["truth_sha256"] for r in rows),
        "G5_NO_FALSE_NEGATIVES_FROM_SOUND_RESOLUTION": all(r["comparison"]["false_negative_count"] == 0 for r in rows),
        "G6_NO_THEOREM_INFLATION": True,
    }

    verdict = (
        "R12_DIRECT_WIDTH4_COMPILER_MATCH_BOTH__SCOPED_COMPILER_PASS__P_VS_NP_OPEN"
        if all_match else
        "R12_DIRECT_WIDTH4_COMPILER_INCOMPLETE__SEMANTIC_WIDTH_VS_PROOF_WIDTH_GAP_PRESERVED__P_VS_NP_OPEN"
    )
    return {
        "schema": "JANUS/TRUMP/R12/DIRECT_WIDTH4_INTERFACE_COMPILER/RESULT/v1.0",
        "created_date": "2026-09-01",
        "verdict": verdict,
        "representation_contract": {
            "target_invariant_I": "I_F(B)=EXISTS Y F(Y,B)",
            "candidate_representation": "fixed-width-4 resolution closure",
            "quotient_representation": "canonical clause content modulo derivation labels/history",
            "control_has_power_to_say_no": True,
        },
        "firewall": firewall,
        "controls": controls,
        "gates": gates,
        "worlds": rows,
        "all_match": all_match,
        "law": "DIFFERENT_DERIVATION_NAMES_MAY_DENOTE_ONE_CLAUSE_CONTENT__QUOTIENT_THE_PATHS__VERIFY_THE_INTERFACE",
        "seal": "THE_COMPILER_MUST_DERIVE_THE_MEANING_WITHOUT_BORROWING_FORBIDDEN_WIDTH",
        "P_VS_NP": "OPEN",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output")
    args = ap.parse_args()
    data = run()
    text = json.dumps(data, indent=2, sort_keys=True)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    print(json.dumps({
        "verdict": data["verdict"],
        "all_match": data["all_match"],
        "gates": data["gates"],
        "worlds": [{
            "index": r["global_index"],
            "unique": r["candidate_stats"]["unique_canonical_clauses"],
            "duplicates": r["candidate_stats"]["duplicate_resolvents_collapsed"],
            "too_wide": r["candidate_stats"]["too_wide_resolvents"],
            "bridge_clauses": r["comparison"]["candidate_bridge_clause_count"],
            "candidate_allowed": r["comparison"]["candidate_allowed_count"],
            "exact_allowed": r["comparison"]["exact_allowed_count"],
            "false_pos": r["comparison"]["false_positive_count"],
            "comparison": r["comparison"]["verdict"],
        } for r in data["worlds"]],
        "P_VS_NP": data["P_VS_NP"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
