#!/usr/bin/env python3
"""R15A: exposed-interface auxiliary-variable representation escape control.

This pass intentionally starts from the already-exposed exact R13-W05 bridge
relation. It asks only whether that relation, whose same-variable CNF width is
6, has a compact width<=3 existential extension representation. It does NOT
validate a direct-from-frame compiler and has no SAT-algorithm authority.

For execution efficiency, the 228 already-proven width<=4 prime clauses are
reconstructed by the frozen R12B compiler and checked against its immutable
basis hash; the 14 already-exposed R14 missing primes are then appended. This is
exactly the 242-prime W05 interface already exposed by R14, not a new discovery.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import janus_trump_r10_exact_semantic_bridge_interface as r10
import janus_trump_r12b_forbidden_pattern_quotient_compiler as r12b
import janus_trump_r13_unseen_interface_generalization as r13

WORLD_ID = "R13-W05"
EXPECTED_FRAME_SHA = "84fa0fbdd127b1c73f3c8ef6820a0d0cdf154093750ed9c600289fce4b6aae88"
EXPECTED_TRUTH_SHA = "acf8828272994c0ad05a44590aa4335e1828d5b7d3e3d4f438b0d497cfcad92f"
EXPECTED_ALLOWED = 287
EXPECTED_PRIMES = 242
EXPECTED_K4_PRIMES = 228
EXPECTED_K4_BASIS_SHA = "82e161d4d01c3c03fd078d8a4be0f6d854246eb62f00c6efda9ff53ad4fcafeb"
EXPECTED_SAME_VARIABLE_WIDTH = 6
MISSING_PRIMES = (
    (-4,-5,10,12,16),
    (-2,-5,10,12,14),
    (-2,-5,10,12,16),
    (-2,3,-5,-13,-14),
    (-2,3,-5,10,-14),
    (-2,3,-5,10,12),
    (-2,3,-5,11,12),
    (-2,3,-5,12,-13),
    (2,-10,-12,-14,-16),
    (3,-10,-12,-14,-16),
    (-2,3,-10,-13,-14,-15),
    (-2,3,-10,-11,-13,-14),
    (-2,3,-9,-10,-13,-14),
    (-2,3,7,-10,-13,-14),
)


def neg(lit: int) -> int:
    return -int(lit)


def encode_or_equiv(out_var: int, left_lit: int, right_lit: int):
    return [
        (-out_var, left_lit, right_lit),
        (out_var, neg(left_lit)),
        (out_var, neg(right_lit)),
    ]


def encode_clause_width3(clause, next_aux: int):
    c = tuple(int(x) for x in clause)
    if len(c) <= 3:
        return [c], [], next_aux
    out_clauses = []
    defs = []
    a = next_aux; next_aux += 1
    out_clauses.extend(encode_or_equiv(a, c[0], c[1]))
    defs.append((a, c[0], c[1]))
    cursor = a
    for lit in c[2:-2]:
        a = next_aux; next_aux += 1
        out_clauses.extend(encode_or_equiv(a, cursor, lit))
        defs.append((a, cursor, lit))
        cursor = a
    out_clauses.append((cursor, c[-2], c[-1]))
    return out_clauses, defs, next_aux


def build_extended_interface(primes, bridge_size: int):
    next_aux = bridge_size + 1
    clauses, definitions = [], []
    for prime in primes:
        enc, defs, next_aux = encode_clause_width3(prime, next_aux)
        clauses.extend(enc); definitions.extend(defs)
    return {
        "clauses": tuple(tuple(c) for c in clauses),
        "definitions": tuple(tuple(d) for d in definitions),
        "auxiliary_variable_count": next_aux - (bridge_size + 1),
        "max_variable": next_aux - 1,
    }


def eval_lit(lit: int, assignment: dict[int, bool]) -> bool:
    value = bool(assignment[abs(lit)])
    return value if lit > 0 else not value


def bridge_assignment(k: int, mask: int):
    return {i + 1: bool((mask >> i) & 1) for i in range(k)}


def extend_assignment(mask: int, k: int, definitions):
    assignment = bridge_assignment(k, mask)
    for out_var, left, right in definitions:
        assignment[out_var] = eval_lit(left, assignment) or eval_lit(right, assignment)
    return assignment


def satisfies_cnf(clauses, assignment) -> bool:
    return all(any(eval_lit(lit, assignment) for lit in clause) for clause in clauses)


def allowed_masks_cnf(clauses, k: int):
    out=[]
    for mask in range(1 << k):
        a=bridge_assignment(k,mask)
        if satisfies_cnf(clauses,a): out.append(mask)
    return out


def allowed_masks_extended(encoded, k: int):
    allowed=[]
    for mask in range(1 << k):
        a=extend_assignment(mask,k,encoded["definitions"])
        if satisfies_cnf(encoded["clauses"],a): allowed.append(mask)
    return allowed


def digest_masks(masks):
    return hashlib.sha256(json.dumps(list(masks), separators=(",", ":")).encode()).hexdigest()


def clause_hash(clauses):
    ordered=sorted((tuple(c) for c in clauses), key=lambda c:(len(c),c))
    return hashlib.sha256(json.dumps([list(c) for c in ordered],separators=(",", ":")).encode()).hexdigest()


def structural_controls():
    enc, defs, nxt=encode_clause_width3((1,-2,3,-4),5)
    if len(defs)!=1 or nxt!=6 or max(map(len,enc))>3: return False
    for m in range(16):
        original=any(eval_lit(l,bridge_assignment(4,m)) for l in (1,-2,3,-4))
        assignment=extend_assignment(m,4,defs)
        if satisfies_cnf(enc,assignment)!=original: return False
    return True


def reconstruct_exposed_primes(frame, bridge):
    q=r12b.saturate_forbidden_pattern_basis(frame, 600, "R15A_W05_K4_RECONSTRUCTION")
    if q["status"]!="FIXED_POINT": raise AssertionError("frozen R12B reconstruction did not reach fixed point")
    basis=r12b.bridge_only_basis(q["active"],bridge)
    local=tuple(sorted({r12b.localize_clause(c,bridge) for c in basis},key=lambda c:(len(c),c)))
    if len(local)!=EXPECTED_K4_PRIMES or clause_hash(local)!=EXPECTED_K4_BASIS_SHA:
        raise AssertionError("R12B k4 prime basis drift")
    primes=tuple(sorted(set(local)|set(MISSING_PRIMES),key=lambda c:(len(c),c)))
    if len(primes)!=EXPECTED_PRIMES: raise AssertionError("242-prime reconstruction drift")
    return primes,q["stats"]


def run():
    freeze=r13.load_freeze(); spec=next(w for w in freeze["worlds"] if w["id"]==WORLD_ID)
    world=r13.generate_world(spec)
    if world["source"]["frame_sha256"]!=EXPECTED_FRAME_SHA: raise AssertionError("W05 frame drift")
    bridge=tuple(world["bridge"])
    if len(bridge)!=16: raise AssertionError("W05 bridge-size drift")

    primes,k4_stats=reconstruct_exposed_primes(world["frame"],bridge)
    original_allowed=allowed_masks_cnf(primes,len(bridge))
    original_sha=digest_masks(original_allowed)
    # Width-5 hull stays inexact, width-6 complete, reconstructing R14 without the slow geometry pass.
    width5=[c for c in primes if len(c)<=5]
    w5_allowed=allowed_masks_cnf(width5,len(bridge))
    exact_width_reconstructed=(original_sha==EXPECTED_TRUTH_SHA and len(original_allowed)==EXPECTED_ALLOWED and len(w5_allowed)!=EXPECTED_ALLOWED)

    encoded=build_extended_interface(primes,len(bridge))
    ext_allowed=allowed_masks_extended(encoded,len(bridge))
    exact=set(original_allowed); ext=set(ext_allowed)
    fp=sorted(ext-exact); fn=sorted(exact-ext)
    truth_sha=digest_masks(ext_allowed); max_width=max(map(len,encoded["clauses"]),default=0)
    gates={
        "G1_EXPOSED_W05_FRAME_FROZEN": world["source"]["frame_sha256"]==EXPECTED_FRAME_SHA,
        "G2_EXPOSED_242_PRIME_INTERFACE_RECONSTRUCTED": len(primes)==EXPECTED_PRIMES and original_sha==EXPECTED_TRUTH_SHA,
        "G3_R14_WIDTH6_ENDPOINT_RECONSTRUCTED": exact_width_reconstructed,
        "G4_STRUCTURAL_ENCODING_CONTROL": structural_controls(),
        "G5_MAX_EXTENDED_WIDTH_LE3": max_width<=3,
        "G6_ALLOWED_SET_MATCH": not fp and not fn and len(ext_allowed)==EXPECTED_ALLOWED,
        "G7_TRUTH_HASH_MATCH": truth_sha==EXPECTED_TRUTH_SHA,
        "G8_NO_DIRECT_FROM_FRAME_COMPILER_CLAIM": True,
        "G9_NO_GLOBAL_COMPLEXITY_INFLATION": True,
    }
    verdict="AUXILIARY_WIDTH3_REPRESENTATION_ESCAPE_CONFIRMED" if all(gates.values()) else "AUXILIARY_ENCODING_CONTROL_FAIL"
    width_dist={}
    for c in encoded["clauses"]: width_dist[str(len(c))]=width_dist.get(str(len(c)),0)+1
    return {
        "schema":"JANUS/TRUMP/R15A/AUXILIARY_REPRESENTATION_ESCAPE_CONTROL/RESULT/v1.0",
        "created_date":"2026-09-02","verdict":verdict,
        "target":{"world_id":WORLD_ID,"bridge_size":len(bridge),"same_variable_minimum_cnf_width":6,"exact_prime_count":len(primes),"exact_allowed_count":EXPECTED_ALLOWED,"truth_table_sha256":EXPECTED_TRUTH_SHA},
        "k4_reconstruction_stats":{"seen_content_states":k4_stats["seen_content_states"],"active_basis_size":k4_stats["active_basis_size"],"pair_pivots_attempted":k4_stats["pair_pivots_attempted"]},
        "extended_representation":{"representation":"acyclic definitional OR-chain CNF with fresh existential auxiliaries","auxiliary_variable_count":encoded["auxiliary_variable_count"],"extended_clause_count":len(encoded["clauses"]),"maximum_clause_width":max_width,"clause_width_distribution":width_dist,"allowed_count":len(ext_allowed),"truth_table_sha256":truth_sha,"false_positive_count":len(fp),"false_negative_count":len(fn)},
        "gates":gates,
        "scientific_interpretation":{"positive":"R14's width-6 lower bound is specific to same-variable CNF. The already-known exact W05 interface has an exact existential extension representation of width<=3 with linear definitional overhead.","hard_wall":"The wide semantic constraints were already exposed by R14. R15A does not show that a direct-from-frame algorithm can discover or compile the needed extension atoms without the exact answer.","next_question":"Freeze a direct-from-frame extension-variable compiler before new unseen worlds; exact shadow may only score after candidate completion."},
        "seal":"THE_NEW_LANGUAGE_CAN_CARRY_THE_MEANING__NOW_PROVE_THE_FRAME_CAN_COMPILE_IT_WITHOUT_BEING_TOLD_THE_ANSWER","P_VS_NP":"OPEN"
    }


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--output",required=True); args=ap.parse_args()
    d=run(); Path(args.output).write_text(json.dumps(d,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"verdict":d["verdict"],"extended_representation":d["extended_representation"],"gates":d["gates"],"P_VS_NP":"OPEN"},indent=2,sort_keys=True))
    return 0 if all(d["gates"].values()) else 2

if __name__=="__main__": raise SystemExit(main())
