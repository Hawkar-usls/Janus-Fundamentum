#!/usr/bin/env python3
"""Provider finite replay for the Akinator RSPC semantic-survival barrier.

Finite mechanics only. This does not prove NP-completeness or any asymptotic
lower bound.
"""

from itertools import product


def assignments(n):
    yield from product((False, True), repeat=n)


def nonconstant(vals):
    return set(vals) == {False, True}


def check_reduction():
    total = 0
    for n in range(4):
        xs = list(assignments(n))
        m = len(xs)
        for mask in range(1 << m):
            table = {x: bool((mask >> i) & 1) for i, x in enumerate(xs)}
            sat = any(table.values())
            vals = [z and table[x] for z in (False, True) for x in xs]
            assert nonconstant(vals) == sat
            total += 1
    assert total == 278


def check_witness_conflict():
    def a(x, y):
        return x or y

    def b(x, y):
        return x or (not y)

    wa = (False, True)
    wb = (False, False)
    assert a(*wa)
    assert b(*wb)
    assert wa != wb
    vals = [a(x, y) and b(x, y) for x, y in assignments(2)]
    assert nonconstant(vals)
    assert any(a(x, y) and b(x, y) for x, y in assignments(2))


def check_pair_count():
    for v in range(2, 80):
        assert sum(1 for i in range(v) for j in range(v) if i != j) == v * (v - 1)


if __name__ == "__main__":
    check_reduction()
    check_witness_conflict()
    check_pair_count()
    print("C025_AKINATOR_RSPC_SAT_TO_NONCONSTANCY_FINITE_REPLAY = PASS")
    print("C025_AKINATOR_RSPC_SINGLE_WITNESS_COUNTEREXAMPLE = PASS")
    print("C025_AKINATOR_RSPC_POLY_PAIR_ENUMERATION = PASS")
    print("C025_AKINATOR_RSPC_NP_COMPLETENESS = ANALYTIC_REDUCTION_NOT_CI")
    print("C025_AKINATOR_RSPC_WITNESS_FRONTIER_LOWER_BOUND = OPEN")
    print("C025_AKINATOR_RSPC_SOURCE_MATCHED_RESTRICTION = OPEN")
    print("C025_AKINATOR_RSPC_CLAIM_CEILING = FINITE_MECHANICS_ONLY")
    print("P_VS_NP = OPEN")
