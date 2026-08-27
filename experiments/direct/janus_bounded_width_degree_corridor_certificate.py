#!/usr/bin/env python3
"""Executable regression for C025 bounded-width average-degree safe-pivot theorem.

Checks the algebraic upper bound against the audited generic raw-budget formula
on finite small canonical CNFs and verifies the frozen width-3 ladder arithmetic.
Finite regression is not theorem authority; P_VS_NP remains OPEN.
"""
from __future__ import annotations

import math
from itertools import combinations

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct import janus_generic_raw_elimination_budget_certificate as rawcert

P_VS_NP = "OPEN"


def threshold(w: int, delta: int) -> float:
    if w < 2 or delta < 0:
        raise ValueError("w>=2 and delta>=0 required")
    return 2.0 * ((w + 1) + math.sqrt((w + 1) ** 2 + (2 * w - 1) * delta)) / (2 * w - 1)


def degree_bound(s: int, w: int, d: int) -> float:
    return s - (w + 1) * d + ((2 * w - 1) * d * d) / 4.0


def signed_counts(cnf: base.CNF, var: int) -> tuple[int, int]:
    return sum(var in c for c in cnf), sum(-var in c for c in cnf)


def verify_state(cnf: base.CNF) -> int:
    if not cnf:
        return 0
    w = max(len(c) for c in cnf)
    if w < 2:
        return 0
    s = base.state_units(cnf)
    checked = 0
    for x in base.vars_of(cnf):
        p, q = signed_counts(cnf, x)
        if p == 0 or q == 0:
            # Pure deletion: exact output must be strictly no larger than input.
            out, stats = base.eliminate_var_capped(cnf, x, s)
            if out is None or int(stats["raw_units"]) > s:
                raise AssertionError("PURE_PIVOT_NOT_SAFE")
            checked += 1
            continue

        d = p + q
        generic = rawcert.raw_budget(cnf, x)
        pair_sensitive = s - (w + 1) * d + (2 * w - 1) * p * q
        degree_only = degree_bound(s, w, d)
        if generic.bound > pair_sensitive + 1e-12:
            raise AssertionError(("GENERIC_BOUND_EXCEEDS_WIDTH_PAIR_BOUND", cnf, x, generic.bound, pair_sensitive))
        if pair_sensitive > degree_only + 1e-12:
            raise AssertionError(("PAIR_BOUND_EXCEEDS_DEGREE_BOUND", cnf, x, pair_sensitive, degree_only))
        checked += 1
    return checked


def small_clause_universe() -> tuple[base.Clause, ...]:
    clauses = set()
    for code in range(1, 27):
        x = code
        lits = []
        for v in (1, 2, 3):
            digit = x % 3
            x //= 3
            if digit == 1:
                lits.append(v)
            elif digit == 2:
                lits.append(-v)
        c = base.canon_clause(lits)
        if c is not None and len(c) >= 2:
            clauses.add(c)
    return tuple(sorted(clauses, key=lambda c: (len(c), c)))


def exhaustive_small_regression() -> tuple[int, int]:
    U = small_clause_universe()
    seen = set()
    pivots = 0
    for k in (1, 2, 3):
        for rows in combinations(U, k):
            cnf = base.canon_cnf(rows)
            if not cnf or cnf in seen or max(map(len, cnf)) < 2:
                continue
            seen.add(cnf)
            pivots += verify_state(cnf)
    return len(seen), pivots


def verify_frozen_ladder() -> None:
    expected = (
        (4, 8, 8, True, 6.830679),
        (4, 10, 9, False, 7.478775),
        (5, 10, 9, True, 7.478775),
        (5, 12, 10, True, 8.184831),
    )
    for n, m, N, forced, rounded in expected:
        w = 3
        s = 1 + (w + 1) * m
        cap = N * N
        delta = cap - s
        L_over_n = (w * m) / n
        D = threshold(w, delta)
        if round(D, 6) != rounded:
            raise AssertionError(("FROZEN_LADDER_THRESHOLD_MISMATCH", n, m, N, D, rounded))
        if (L_over_n <= D) is not forced:
            raise AssertionError(("FROZEN_LADDER_CLASSIFICATION_MISMATCH", n, m, N, L_over_n, D, forced))


def selftest() -> None:
    states, pivots = exhaustive_small_regression()
    verify_frozen_ladder()
    print(f"BOUNDED_WIDTH_SMALL_CANONICAL_STATES={states}")
    print(f"BOUNDED_WIDTH_SMALL_PIVOTS={pivots}")
    print("BOUNDED_WIDTH_DEGREE_UPPER_BOUND=PASS")
    print("FROZEN_WIDTH3_LADDER_ARITHMETIC=PASS")
    print("THREE_OF_FOUR_RUNGS_ORDINARY_PIVOT_FORCED=PASS")
    print("UNIVERSAL_V3_AVAILABILITY=OPEN")
    print("P_VS_NP=OPEN")


if __name__ == "__main__":
    selftest()
