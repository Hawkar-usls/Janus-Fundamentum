#!/usr/bin/env python3
"""Finite provider replay for the C025-C2G v1.3 selector-lift barrier.

Checks finite semantics and an explicit plain-Resolution proof translation.
The coNP-completeness and asymptotic implications are analytical theorems, not
claims made by this finite replay.
"""
from __future__ import annotations

from itertools import combinations, product

Clause = tuple[int, ...]
CNF = tuple[Clause, ...]


def eval_clause(clause: Clause, assignment: dict[int, int]) -> bool:
    return any(assignment[abs(l)] if l > 0 else 1 - assignment[abs(l)] for l in clause)


def sat(cnf: CNF) -> bool:
    vars_ = sorted({abs(l) for c in cnf for l in c})
    for bits in product((0, 1), repeat=len(vars_)):
        a = dict(zip(vars_, bits))
        if all(eval_clause(c, a) for c in cnf):
            return True
    return False


def selector_lift(cnf: CNF, selector: int) -> CNF:
    assert selector not in {abs(l) for c in cnf for l in c}
    return tuple(tuple([selector, *c]) for c in cnf)


def entails_unit(cnf: CNF, unit: int) -> bool:
    vars_ = sorted({abs(l) for c in cnf for l in c} | {abs(unit)})
    for bits in product((0, 1), repeat=len(vars_)):
        a = dict(zip(vars_, bits))
        if all(eval_clause(c, a) for c in cnf) and not eval_clause((unit,), a):
            return False
    return True


def all_nonempty_clauses(n: int) -> list[Clause]:
    out: list[Clause] = []
    for pattern in product((-1, 0, 1), repeat=n):
        if all(x == 0 for x in pattern):
            continue
        clause: list[int] = []
        for var, sign in enumerate(pattern, start=2):  # reserve selector id 1
            if sign > 0:
                clause.append(var)
            elif sign < 0:
                clause.append(-var)
        out.append(tuple(clause))
    return sorted(set(out), key=lambda c: (len(c), c))


def resolve(left: Clause, right: Clause, pivot: int) -> Clause:
    assert pivot in left and -pivot in right
    literals = (set(left) - {pivot}) | (set(right) - {-pivot})
    assert not any(-l in literals for l in literals)
    return tuple(sorted(literals, key=lambda l: (abs(l), l < 0)))


def explicit_resolution_translation() -> None:
    # H is the 2-variable contradiction containing every parity/equality row.
    # Variables are 2,3; selector is 1.
    h1 = (2, 3)
    h2 = (2, -3)
    h3 = (-2, 3)
    h4 = (-2, -3)
    H = (h1, h2, h3, h4)
    assert not sat(H)

    # Plain Resolution refutation H: derive 2, derive -2, then empty.
    p = resolve(h1, h2, 3)
    n = resolve(h3, h4, 3)
    empty = resolve(p, n, 2)
    assert p == (2,) and n == (-2,) and empty == ()

    S = selector_lift(H, 1)
    lifted = [tuple([1, *c]) for c in H]
    lp = resolve(lifted[0], lifted[1], 3)
    ln = resolve(lifted[2], lifted[3], 3)
    unit_s = resolve(lp, ln, 2)
    assert lp == (1, 2)
    assert ln == (1, -2)
    assert unit_s == (1,)
    assert entails_unit(S, 1)

    # Restricting s=0 removes literal s and exactly recovers the original proof.
    def restrict_s0(clause: Clause) -> Clause:
        return tuple(l for l in clause if l != 1)

    assert tuple(restrict_s0(c) for c in lifted) == H
    assert restrict_s0(lp) == p
    assert restrict_s0(ln) == n
    assert restrict_s0(unit_s) == empty


def exhaustive_semantic_reduction() -> int:
    clauses = all_nonempty_clauses(2)
    checked = 0
    # All CNFs with up to 4 distinct nonempty clauses on two non-selector roots.
    for count in range(5):
        for chosen in combinations(clauses, count):
            H = tuple(chosen)
            S = selector_lift(H, 1)
            assert entails_unit(S, 1) == (not sat(H))
            checked += 1
    return checked


def sat_counterexample() -> None:
    H = ((2,),)
    assert sat(H)
    S = selector_lift(H, 1)
    assert not entails_unit(S, 1)
    # Explicit witness s=0,x=1.
    a = {1: 0, 2: 1}
    assert all(eval_clause(c, a) for c in S)
    assert not eval_clause((1,), a)


def main() -> None:
    checked = exhaustive_semantic_reduction()
    explicit_resolution_translation()
    sat_counterexample()
    print("C025_C2G_V1_3_SELECTOR_SEMANTIC_EQUIVALENCE = PASS")
    print(f"C025_C2G_V1_3_SELECTOR_CNFS_CHECKED = {checked}")
    print("C025_C2G_V1_3_PLAIN_RES_LIFT_AND_RESTRICT = PASS")
    print("C025_C2G_V1_3_SAT_NONIMPLICATION_WITNESS = PASS")
    print("C025_C2G_V1_3_CO_NP_COMPLETENESS = ANALYTICAL_NOT_CI")
    print("C025_C2G_V1_3_POLY_DISCOVERY_IMPLIES_PNP = ANALYTICAL_IMPLICATION_ONLY")
    print("C025_C2G_V1_3_UNIVERSAL_DISCOVERY = OPEN")
    print("P_VS_NP = OPEN")


if __name__ == "__main__":
    main()
