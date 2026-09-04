#!/usr/bin/env python3
from __future__ import annotations

from collections import defaultdict
from itertools import combinations, product
import json

Formula = tuple[tuple[int, ...], ...]


def canonical_formula(clauses) -> Formula:
    canon = []
    for clause in clauses:
        lits = set(int(x) for x in clause)
        if any(-x in lits for x in lits):
            continue
        normalized = tuple(sorted(lits, key=lambda z: (abs(z), z < 0)))
        if normalized:
            canon.append(normalized)
    return tuple(sorted(set(canon)))


def variables(F: Formula) -> tuple[int, ...]:
    return tuple(sorted({abs(l) for c in F for l in c}))


def exact_sat(F: Formula) -> bool:
    vs = variables(F)
    if not F:
        return True
    for bits in product((False, True), repeat=len(vs)):
        assignment = dict(zip(vs, bits))
        if all(any(assignment[abs(l)] if l > 0 else not assignment[abs(l)] for l in c) for c in F):
            return True
    return False


def exact_representation(F: Formula):
    # Positive control: injective on canonical Formula objects.
    return F


def clv_representation(F: Formula):
    # Resource profile only. This gate tests that it is never promoted to semantic authority.
    return (len(F), sum(len(c) for c in F), len(variables(F)))


def finite_formula_domain(max_vars: int = 2, max_clauses: int = 3):
    clause_universe = []
    for width in (1, 2):
        for varset in combinations(range(1, max_vars + 1), width):
            for signs in product((-1, 1), repeat=width):
                clause_universe.append(tuple(s * v for s, v in zip(signs, varset)))
    seen = set()
    for k in range(0, max_clauses + 1):
        for subset in combinations(clause_universe, k):
            F = canonical_formula(subset)
            if F not in seen:
                seen.add(F)
                yield F


def find_fiber_collision(formulas, encoder):
    fibers = defaultdict(dict)
    checked = 0
    for F in formulas:
        checked += 1
        key = encoder(F)
        truth = exact_sat(F)
        opposite = not truth
        if opposite in fibers[key]:
            G = fibers[key][opposite]
            return {
                "found": True,
                "checked_before_collision": checked,
                "representation": key,
                "formula_a": G,
                "sat_a": opposite,
                "formula_b": F,
                "sat_b": truth,
            }
        fibers[key].setdefault(truth, F)
    return {"found": False, "checked": checked, "fiber_count": len(fibers)}


def formula_json(F: Formula):
    return [list(c) for c in F]


def audit():
    domain = list(finite_formula_domain())

    positive = find_fiber_collision(domain, exact_representation)
    assert positive["found"] is False

    negative = find_fiber_collision(domain, clv_representation)
    assert negative["found"] is True
    assert negative["sat_a"] != negative["sat_b"]
    assert clv_representation(negative["formula_a"]) == clv_representation(negative["formula_b"])

    # Independent exact replay of the discovered witness.
    replay_a = exact_sat(negative["formula_a"])
    replay_b = exact_sat(negative["formula_b"])
    assert replay_a == negative["sat_a"]
    assert replay_b == negative["sat_b"]
    assert replay_a != replay_b

    result = {
        "gate": "R47AF_REPRESENTATION_AUTHORITY_FIBER_GATE",
        "domain_formula_count": len(domain),
        "target_predicate": "SAT",
        "positive_control": {
            "representation": "EXACT_CANONICAL_CNF_IDENTITY",
            "finite_collision_found": False,
            "universal_semantic_authority_basis": "INJECTIVITY_BY_CONSTRUCTION",
            "SEMANTIC_AUTHORITY": "GRANTED_FOR_IDENTITY_CONTROL",
            "ALGORITHMIC_AUTHORITY": "NOT_GRANTED_NO_POLYNOMIAL_SAT_DECIDER_PROVIDED",
            "finite_audit_is_not_the_universal_proof": True,
        },
        "negative_control": {
            "representation": "CLV_RESOURCE_PROFILE",
            "fiber_signature": list(negative["representation"]),
            "formula_a": formula_json(negative["formula_a"]),
            "sat_a": negative["sat_a"],
            "formula_b": formula_json(negative["formula_b"]),
            "sat_b": negative["sat_b"],
            "independent_exact_replay_pass": True,
            "SEMANTIC_AUTHORITY": "DENIED",
            "ALGORITHMIC_AUTHORITY": "DENIED",
            "verdict": "QUARANTINED_INSUFFICIENT_REPRESENTATION",
        },
        "laws": {
            "formula_identity_ne_representation_identity_ne_semantic_identity": True,
            "polynomial_size_does_not_imply_predicate_sufficiency": True,
            "polynomial_decoder_or_verifier_does_not_imply_polynomial_decider": True,
            "semantic_authority_requires_monochromatic_predicate_fibers": True,
            "algorithmic_authority_requires_polynomial_representation_decider": True,
        },
        "UNIVERSAL_POLYNOMIAL_ENVELOPE_COVERAGE": "OPEN",
        "O4_UNIVERSAL_COVERAGE": "OPEN",
        "SAT_IN_P": "NOT_PROVED",
        "P_EQ_NP": "NOT_PROVED",
        "P_NE_NP": "NOT_PROVED",
        "P_VS_NP": "OPEN",
        "TRUMP_finished": False,
    }
    return result


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2, sort_keys=True))
