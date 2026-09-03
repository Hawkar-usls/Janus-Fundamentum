#!/usr/bin/env python3
"""Exact finite verifier for R44BN.

The verifier is not a heuristic search and does not claim a global SAT theorem.
It exhaustively proves the finite clause-complexity statement for the fixed
R44AS critical sibling projection.
"""
from itertools import combinations, product

PARENT = [
    (2, 3, -4),
    (-1, 2, 4),
    (-2, -5, -6),
    (1, -3, -4),
    (1, -5, 6),
    (-3, 5, -6),
    (-2, 3, 6),
    (-1, 4, 5),
]
PIVOT = 2
REMAINING = (1, 3, 4, 5, 6)
EXPECTED_PRIMES = {
    frozenset(c)
    for c in [
        (3, -5, 6),
        (3, -4, 6),
        (3, -4, -5),
        (-3, 5, -6),
        (1, -5, 6),
        (1, -4, 6),
        (1, -4, -5),
        (1, -3, -4),
        (-1, 4, -6),
        (-1, 4, 5),
        (-1, 3, 6),
        (-1, 3, -5),
        (-1, 3, 4),
    ]
}
EXACT_EIGHT_COVER = [
    (3, -5, 6),
    (3, -4, 6),
    (3, -4, -5),
    (-3, 5, -6),
    (1, -5, 6),
    (1, -3, -4),
    (-1, 4, -6),
    (-1, 4, 5),
]


def clause_sat(clause, assignment):
    return any(
        assignment[abs(lit)] if lit > 0 else not assignment[abs(lit)]
        for lit in clause
    )


def formula_sat(formula, assignment):
    return all(clause_sat(c, assignment) for c in formula)


def simplify(formula, var, value):
    out = []
    for clause in formula:
        new_clause = []
        satisfied = False
        for lit in clause:
            if abs(lit) != var:
                new_clause.append(lit)
                continue
            lit_true = value if lit > 0 else not value
            if lit_true:
                satisfied = True
                break
        if not satisfied:
            out.append(tuple(new_clause))
    return out


def delta_star(formula):
    best = 0
    m = len(formula)
    for mask in range(1, 1 << m):
        selected = [formula[i] for i in range(m) if mask & (1 << i)]
        variables = {abs(lit) for clause in selected for lit in clause}
        best = max(best, len(selected) - len(variables))
    return best


def projection_truth_table():
    models = []
    nonmodels = []
    for bits in product((False, True), repeat=len(REMAINING)):
        partial = dict(zip(REMAINING, bits))
        projected_true = False
        for pivot_value in (False, True):
            assignment = dict(partial)
            assignment[PIVOT] = pivot_value
            if formula_sat(PARENT, assignment):
                projected_true = True
                break
        (models if projected_true else nonmodels).append(bits)
    return models, nonmodels


def assignment_dict(bits):
    return dict(zip(REMAINING, bits))


def enumerate_implicates(models):
    implicates = []
    for state in product((0, 1, -1), repeat=len(REMAINING)):
        if all(s == 0 for s in state):
            continue
        clause = tuple(v * s for v, s in zip(REMAINING, state) if s != 0)
        if all(clause_sat(clause, assignment_dict(bits)) for bits in models):
            implicates.append(clause)
    return implicates


def is_implicate(clause, models):
    return all(clause_sat(clause, assignment_dict(bits)) for bits in models)


def prime_implicates(implicates, models):
    primes = []
    for clause in implicates:
        prime = True
        for i in range(len(clause)):
            reduced = clause[:i] + clause[i + 1 :]
            if reduced and is_implicate(reduced, models):
                prime = False
                break
        if prime:
            primes.append(clause)
    return primes


def falsified_by(clause, bits):
    return not clause_sat(clause, assignment_dict(bits))


def covers_all_nonmodels(selected, nonmodels):
    return all(any(falsified_by(clause, bits) for clause in selected) for bits in nonmodels)


def main():
    # Recheck the R44AS fixed-parent rank facts used by this finite theorem.
    assert delta_star(PARENT) == 2
    full_delta = len(PARENT) - len({abs(l) for c in PARENT for l in c})
    assert full_delta == 2
    for mask in range(1, (1 << len(PARENT)) - 1):
        selected = [PARENT[i] for i in range(len(PARENT)) if mask & (1 << i)]
        variables = {abs(lit) for clause in selected for lit in clause}
        assert len(selected) - len(variables) < 2
    assert delta_star(simplify(PARENT, PIVOT, False)) == 1
    assert delta_star(simplify(PARENT, PIVOT, True)) == 1

    models, nonmodels = projection_truth_table()
    assert len(models) == 11
    assert len(nonmodels) == 21

    implicates = enumerate_implicates(models)
    primes = prime_implicates(implicates, models)
    prime_sets = {frozenset(c) for c in primes}
    assert prime_sets == EXPECTED_PRIMES
    assert len(primes) == 13

    # Exact lower bound: no <=7 prime implicates cover all nonmodels.
    for r in range(0, 8):
        for chosen in combinations(primes, r):
            assert not covers_all_nonmodels(chosen, nonmodels)

    # Exact upper bound: eight prime implicates suffice.
    assert all(frozenset(c) in EXPECTED_PRIMES for c in EXACT_EIGHT_COVER)
    assert covers_all_nonmodels(EXACT_EIGHT_COVER, nonmodels)

    # The exhibited minimum-size CNF has delta*=3.
    assert delta_star(EXACT_EIGHT_COVER) == 3

    print("R44BN finite certificate: PASS")
    print("parent delta*=2; both cofactors delta*=1")
    print("projection models=11 nonmodels=21")
    print("prime implicates=13")
    print("minimum auxiliary-free projection-faithful CNF clauses=8")
    print("therefore every such CNF has ordinary deficiency >=8-5=3 and delta*>=3")
    print("TRUMP_finished=false SAT_IN_P=NOT_PROVED P_VS_NP=OPEN")


if __name__ == "__main__":
    main()
