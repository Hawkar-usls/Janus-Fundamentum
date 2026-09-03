#!/usr/bin/env python3
from __future__ import annotations

import itertools
import json
from collections import Counter

SAT_FORMULA = [
    [-1,-3,4],[-1,-2,-3],[-1,2,3],[-1,2,4],[-1,3,-4],
    [1,-3,-4],[1,-2,3],[1,2,-3],[1,3,4],[2,3,4],
]
UNSAT_FORMULA = [
    [-1,-3,-4],[-1,-3,4],[-1,-2,3],[-1,2,3],[-1,2,4],
    [1,-2,-3],[1,2,-3],[1,3,-4],[1,3,4],[2,3,4],
]
EXPECTED_DEGREES = ((4,5),(4,2),(5,4),(4,2))
EXPECTED_SAT_WITNESS = (False, False, False, True)


def variables(cnf):
    return sorted({abs(lit) for clause in cnf for lit in clause})


def polarity_degrees(cnf):
    vs = variables(cnf)
    return tuple((sum(v in c for c in cnf), sum(-v in c for c in cnf)) for v in vs)


def literal_order(lit):
    return (abs(lit), lit < 0)


def signed_pair_signature(cnf):
    counts = Counter()
    for clause in cnf:
        for a, b in itertools.combinations(clause, 2):
            key = tuple(sorted((a, b), key=literal_order))
            counts[key] += 1
    return tuple(sorted(counts.items()))


def exact_decision(cnf):
    vs = variables(cnf)
    rejected = 0
    for bits in itertools.product((False, True), repeat=len(vs)):
        assignment = dict(zip(vs, bits))
        if all(any(assignment[abs(lit)] == (lit > 0) for lit in clause) for clause in cnf):
            return "SAT", bits, rejected
        rejected += 1
    return "UNSAT", None, rejected


def connected_incidence(cnf):
    vs = variables(cnf)
    graph = {("v", v): set() for v in vs}
    for i, clause in enumerate(cnf):
        cnode = ("c", i)
        graph[cnode] = set()
        for lit in clause:
            vnode = ("v", abs(lit))
            graph[vnode].add(cnode)
            graph[cnode].add(vnode)
    start = next(iter(graph))
    seen = {start}
    stack = [start]
    while stack:
        node = stack.pop()
        for nxt in graph[node]:
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    return len(seen) == len(graph)


def is_bipolar_2core(cnf):
    for v in variables(cnf):
        p = sum(v in c for c in cnf)
        n = sum(-v in c for c in cnf)
        if p < 1 or n < 1 or p + n < 2:
            return False
    return True


def main():
    assert SAT_FORMULA != UNSAT_FORMULA
    assert len(SAT_FORMULA) == len(UNSAT_FORMULA) == 10
    assert variables(SAT_FORMULA) == variables(UNSAT_FORMULA) == [1,2,3,4]
    assert all(len(c) == 3 and len({abs(x) for x in c}) == 3 for c in SAT_FORMULA + UNSAT_FORMULA)

    sat_deg = polarity_degrees(SAT_FORMULA)
    unsat_deg = polarity_degrees(UNSAT_FORMULA)
    assert sat_deg == unsat_deg == EXPECTED_DEGREES

    sat_pairs = signed_pair_signature(SAT_FORMULA)
    unsat_pairs = signed_pair_signature(UNSAT_FORMULA)
    assert sat_pairs == unsat_pairs

    assert connected_incidence(SAT_FORMULA)
    assert connected_incidence(UNSAT_FORMULA)
    assert is_bipolar_2core(SAT_FORMULA)
    assert is_bipolar_2core(UNSAT_FORMULA)

    sat_status, sat_witness, sat_rejected = exact_decision(SAT_FORMULA)
    unsat_status, unsat_witness, unsat_rejected = exact_decision(UNSAT_FORMULA)
    assert sat_status == "SAT"
    assert sat_witness == EXPECTED_SAT_WITNESS
    assert sat_rejected == 1
    assert unsat_status == "UNSAT"
    assert unsat_witness is None
    assert unsat_rejected == 16

    out = {
        "gate_id": "R44X_SIGNED_PAIR_INTERACTION_COUNTEREXAMPLE",
        "status": "EXPLICIT_SIGNED_PAIR_COLLISION_VERIFIED",
        "shared_n": 4,
        "shared_m": 10,
        "shared_polarity_degrees": [list(x) for x in sat_deg],
        "shared_signed_pair_signature": [[[a,b], count] for (a,b), count in sat_pairs],
        "connected_incidence_both": True,
        "bipolar_2core_both": True,
        "sat_status": sat_status,
        "sat_witness": {str(i+1): bit for i, bit in enumerate(sat_witness)},
        "unsat_status": unsat_status,
        "unsat_assignments_rejected": unsat_rejected,
        "order_le_2_local_marginals_sufficient": False,
        "global_polynomial_compression_ruled_out": False,
        "proof_authority_delta": 0,
        "TRUMP_finished": False,
        "SAT_IN_P": "NOT_PROVED",
        "P_EQUALS_NP": "NOT_PROVED",
        "P_NE_NP": "NOT_PROVED",
        "P_VS_NP": "OPEN",
        "next_theorem_target": "TRUMP_UNIVERSAL_PROOF_CARRYING_DECOMPOSITION_LEMMA",
    }
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
