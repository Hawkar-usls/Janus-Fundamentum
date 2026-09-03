#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path

EVIDENCE_PATH = Path(__file__).with_name(
    "JANUS_TRUMP_R44X_SIGNED_PAIR_INTERACTION_COUNTEREXAMPLE_2026-09-03.json"
)


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


def witness_satisfies(cnf, witness):
    return all(
        any(bool(witness[str(abs(lit))]) == (lit > 0) for lit in clause)
        for clause in cnf
    )


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


def encode_signature(sig):
    return [[[a, b], count] for (a, b), count in sig]


def main():
    raw = EVIDENCE_PATH.read_bytes()
    evidence = json.loads(raw)

    assert evidence["id"] == "JANUS_TRUMP_R44X_SIGNED_PAIR_INTERACTION_COUNTEREXAMPLE_2026-09-03"
    assert evidence["status"] == "EXPLICIT_FINITE_COUNTEREXAMPLE_DISCOVERED_EXPLORATORILY"
    assert evidence["discovery_protocol"]["preregistered_before_discovery"] is False
    assert evidence["discovery_protocol"]["authority"] == "EXACT_COUNTEREXAMPLE_ONLY"

    sat_formula = evidence["sat_formula"]
    unsat_formula = evidence["unsat_formula"]

    assert sat_formula != unsat_formula
    assert len(sat_formula) == len(unsat_formula) == evidence["shared_m"] == 10
    assert variables(sat_formula) == variables(unsat_formula) == [1, 2, 3, 4]
    assert evidence["shared_n"] == 4
    assert all(
        len(c) == 3 and len({abs(x) for x in c}) == 3
        for c in sat_formula + unsat_formula
    )

    sat_deg = polarity_degrees(sat_formula)
    unsat_deg = polarity_degrees(unsat_formula)
    claimed_deg = tuple(tuple(x) for x in evidence["shared_polarity_degrees"])
    assert sat_deg == unsat_deg == claimed_deg

    sat_pairs = signed_pair_signature(sat_formula)
    unsat_pairs = signed_pair_signature(unsat_formula)
    assert sat_pairs == unsat_pairs
    assert encode_signature(sat_pairs) == evidence["shared_signed_pair_signature"]

    sat_connected = connected_incidence(sat_formula)
    unsat_connected = connected_incidence(unsat_formula)
    sat_bipolar = is_bipolar_2core(sat_formula)
    unsat_bipolar = is_bipolar_2core(unsat_formula)
    assert sat_connected and unsat_connected
    assert sat_bipolar and unsat_bipolar

    structural = evidence["verified_structural_properties"]
    assert structural["both_connected_incidence_graphs"] is True
    assert structural["both_bipolar"] is True
    assert structural["every_variable_degree_at_least_2"] is True
    assert structural["no_unit_clause"] is True
    assert structural["all_clauses_width_3"] is True

    sat_status, first_sat_witness, sat_rejected = exact_decision(sat_formula)
    unsat_status, unsat_witness, unsat_rejected = exact_decision(unsat_formula)
    assert sat_status == "SAT"
    assert first_sat_witness is not None
    assert witness_satisfies(sat_formula, evidence["sat_witness"])
    assert unsat_status == "UNSAT"
    assert unsat_witness is None
    assert unsat_rejected == evidence["unsat_assignments_rejected"] == 16

    assert evidence["formal_conclusion"] == (
        "UNARY_AND_SIGNED_PAIRWISE_MARGINALS_ARE_NOT_AN_EXACT_UNIVERSAL_3CNF_DECISION_SIGNATURE"
    )
    assert evidence["P_EQUALS_NP"] == "NOT_PROVED"
    assert evidence["P_NE_NP"] == "NOT_PROVED"
    assert evidence["P_VS_NP"] == "OPEN"

    out = {
        "gate_id": "R44X_SIGNED_PAIR_INTERACTION_COUNTEREXAMPLE",
        "status": "EXPLICIT_SIGNED_PAIR_COLLISION_VERIFIED",
        "canonical_evidence_sha256": hashlib.sha256(raw).hexdigest(),
        "shared_n": evidence["shared_n"],
        "shared_m": evidence["shared_m"],
        "shared_polarity_degrees": [list(x) for x in sat_deg],
        "shared_signed_pair_signature": encode_signature(sat_pairs),
        "connected_incidence_both": sat_connected and unsat_connected,
        "bipolar_2core_both": sat_bipolar and unsat_bipolar,
        "sat_status": sat_status,
        "sat_witness": evidence["sat_witness"],
        "sat_assignments_rejected_before_first_witness": sat_rejected,
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
