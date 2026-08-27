#!/usr/bin/env python3
"""Executable regression for C025 bounded-width integer degree strengthening v1.2.

The theorem uses integrality: min incidence degree <= floor(L/n).  This script
verifies the frozen width-3 ladder arithmetic and cross-checks the low-degree
bound against the audited generic raw-budget implementation on representative
states.  Finite checks are not theorem authority.
"""
from __future__ import annotations

import math

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct import janus_bounded_width_degree_corridor_certificate as v11
from experiments.direct import janus_generic_raw_elimination_budget_certificate as rawcert

P_VS_NP = "OPEN"


def integer_forced(n: int, L: int, w: int, s: int, cap: int) -> tuple[bool, int, float]:
    d_floor = L // n
    D = v11.threshold(w, cap - s)
    return d_floor <= D, d_floor, D


def verify_rungs() -> None:
    rungs = (
        (4, 8, 8),
        (4, 10, 9),
        (5, 10, 9),
        (5, 12, 10),
    )
    for n, m, N in rungs:
        w = 3
        s = 1 + (w + 1) * m
        L = w * m
        forced, d_floor, D = integer_forced(n, L, w, s, N * N)
        if not forced:
            raise AssertionError(("INTEGER_STRENGTHENING_FAILED_FROZEN_RUNG", n, m, N, d_floor, D))

    # The formerly borderline rung is the key regression.
    forced, d_floor, D = integer_forced(4, 30, 3, 41, 81)
    assert forced and d_floor == 7 and 7 < D < 8
    assert round(D, 6) == 7.478775


def verify_representative_low_degree_pivot() -> None:
    # Width-3 state with 4 variables and 10 clauses. By integer averaging some
    # pivot has d<=7. Check the generic bound implication on a deterministic
    # representative; this is implementation regression, not the universal proof.
    cnf = base.canon_cnf((
        (1, 2, 3), (1, 2, -3), (1, -2, 4), (-1, 2, 4),
        (-1, -2, 3), (1, 3, -4), (-1, 3, 4), (2, 3, -4),
        (-2, 3, 4), (1, -2, -4),
    ))
    assert len(cnf) == 10 and max(map(len, cnf)) == 3
    L = sum(map(len, cnf))
    assert L == 30
    degrees = {}
    for x in base.vars_of(cnf):
        p = sum(x in c for c in cnf)
        q = sum(-x in c for c in cnf)
        degrees[x] = p + q
    x = min(degrees, key=lambda z: (degrees[z], z))
    assert degrees[x] <= 30 // 4

    generic = rawcert.raw_budget(cnf, x)
    d = degrees[x]
    degree_upper = v11.degree_bound(base.state_units(cnf), 3, d)
    assert generic.bound <= degree_upper + 1e-12
    assert degree_upper <= 81
    out, stats = base.eliminate_var_capped(cnf, x, 81)
    assert out is not None and int(stats["raw_units"]) <= 81


def selftest() -> None:
    verify_rungs()
    verify_representative_low_degree_pivot()
    print("INTEGER_AVERAGE_DEGREE_STRENGTHENING=PASS")
    print("FORMER_BORDERLINE_RUNG_4V_10C_N9=ORDINARY_SAFE_PIVOT_FORCED")
    print("FROZEN_WIDTH3_LADDER_THEOREM_CLOSED=PASS")
    print("V3_ROOT_FREE_TAIL_AVAILABILITY=OPEN")
    print("P_VS_NP=OPEN")


if __name__ == "__main__":
    selftest()
