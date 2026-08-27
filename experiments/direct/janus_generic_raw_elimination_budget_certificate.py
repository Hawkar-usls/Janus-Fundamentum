#!/usr/bin/env python3
"""Executable regression for C025 generic pre-subsumption raw budget lemma.

The mathematical lemma is combinatorial.  This executable checks that the
closed-form bound matches the frozen `eliminate_var_capped` accounting and then
runs a finite exhaustive small-CNF regression.  Finite enumeration is NOT a
universal theorem and is never promoted to one.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base

P_VS_NP = "OPEN"


@dataclass(frozen=True)
class RawBudget:
    var: int
    p: int
    q: int
    U_plus: int
    U_minus: int
    retained_units: int
    state_units: int
    bound: int
    whole_state_bound: int


def raw_budget(cnf: base.CNF, var: int) -> RawBudget:
    if var <= 0:
        raise ValueError("var must be positive")
    pos = [c for c in cnf if var in c]
    neg = [c for c in cnf if -var in c]
    retained = [c for c in cnf if var not in c and -var not in c]

    p = len(pos)
    q = len(neg)
    U_plus = sum(len(c) - 1 for c in pos)
    U_minus = sum(len(c) - 1 for c in neg)
    R = base.state_units(tuple(retained))
    s = base.state_units(cnf)

    B = R + p * q + q * U_plus + p * U_minus
    B2 = s + p * q - 2 * p - 2 * q + (q - 1) * U_plus + (p - 1) * U_minus
    if B != B2:
        raise AssertionError(("WHOLE_STATE_IDENTITY_MISMATCH", B, B2))

    expected_R = s - 2 * p - 2 * q - U_plus - U_minus
    if R != expected_R:
        raise AssertionError(("RETAINED_IDENTITY_MISMATCH", R, expected_R))

    return RawBudget(var, p, q, U_plus, U_minus, R, s, B, B2)


def verify_against_actual(cnf: base.CNF, var: int) -> RawBudget:
    budget = raw_budget(cnf, var)
    # Use the mathematical bound itself as the cap.  The lemma says the frozen
    # monotone accumulator can never cross it.
    out, stats = base.eliminate_var_capped(cnf, var, budget.bound)
    if out is None:
        raise AssertionError(("BOUND_FAILED_TO_PREVENT_ABORT", cnf, var, budget, stats))
    actual_raw = int(stats["raw_units"])
    if actual_raw > budget.bound:
        raise AssertionError(("ACTUAL_RAW_EXCEEDS_BOUND", actual_raw, budget.bound))
    if not base.verify_elimination_transition(cnf, var, out, budget.bound):
        raise AssertionError("ELIMINATION_REPLAY_FAILED")
    return budget


def all_non_tautological_clauses_3vars() -> tuple[base.Clause, ...]:
    clauses = set()
    # Each variable is absent, positive, or negative: 3^3-1 nonempty choices.
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
        if not lits:
            continue
        c = base.canon_clause(lits)
        if c is not None:
            clauses.add(c)
    return tuple(sorted(clauses, key=lambda c: (len(c), c)))


def exhaustive_small_regression() -> tuple[int, int]:
    universe = all_non_tautological_clauses_3vars()
    seen: set[base.CNF] = set()
    checked_pivots = 0

    # Exhaust all raw clause sets of cardinality 1..3. Canonicalization may
    # collapse/subsume them; deduplicate canonical states before testing.
    for k in (1, 2, 3):
        for raw_rows in combinations(universe, k):
            cnf = base.canon_cnf(raw_rows)
            if not cnf or cnf in seen:
                continue
            seen.add(cnf)
            for var in base.vars_of(cnf):
                verify_against_actual(cnf, var)
                checked_pivots += 1
    return len(seen), checked_pivots


def selftest() -> None:
    fixtures = (
        base.canon_cnf(((1, 2, 3), (-1, 4, 5), (1, -4, 6), (-1, -5, 7))),
        base.canon_cnf(((1, 2), (1, 3, 4), (-1, 5, 6), (-1, 7, 8))),
        base.canon_cnf(((1, 2, 3), (1, 4, 5), (2, 6, 7))),  # pure/one-sided pivot cases
    )
    for cnf in fixtures:
        for var in base.vars_of(cnf):
            verify_against_actual(cnf, var)

    states, pivots = exhaustive_small_regression()
    assert states > 0 and pivots > 0

    print(f"GENERIC_RAW_BUDGET_SMALL_CANONICAL_STATES={states}")
    print(f"GENERIC_RAW_BUDGET_SMALL_PIVOTS={pivots}")
    print("GENERIC_PRE_SUBSUMPTION_RAW_BOUND=PASS")
    print("FINITE_EXHAUSTION_IS_NOT_UNIVERSAL_PROOF=PASS")
    print("P_VS_NP=OPEN")


if __name__ == "__main__":
    selftest()
