#!/usr/bin/env python3
"""Executable regression for JANUS C025 v0.5 proof-selector through N=43.

Finite fixtures and arithmetic regression are implementation evidence only.
The universal/finite mathematical statements live in the theorem JSON.
P vs NP remains OPEN.
"""

from fractions import Fraction
from math import comb

from experiments.direct import janus_unified_proof_carrying_akinator_jec as core
from experiments.direct import janus_proof_selector_v05_candidate as v05

P_VS_NP = "OPEN"


def T(s: Fraction) -> Fraction:
    s = Fraction(s)
    return max(s, Fraction(1) + (s - 1) ** 2 / 12)


def Uraw(n: int) -> int:
    return 3 ** (n - 2) * (2 * n + 1)


def Smax(n: int) -> int:
    if n <= 0:
        return 1
    return 1 + max((k + 1) * comb(n, k) * (2 ** k) for k in range(1, n + 1))


def recurrence_raw_bounds_from(s0: Fraction, n0: int):
    s = Fraction(s0)
    n = n0
    out = []
    while n > 2:
        raw = min(T(s), Fraction(Uraw(n)))
        next_s = min(T(s), Fraction(Smax(n - 1)))
        out.append((n, s, raw, next_s))
        s = next_s
        n -= 1
    return out


def verify_N43_partition() -> None:
    N = 43
    hard_r_max = (N - 6) // 4
    assert hard_r_max == 9
    cells = []
    r = 9
    for m in range(5, N):
        L = N - 1 - r - m
        if L >= 3 * r and L >= 2 * m and L >= r:
            cells.append((m, L))
    assert cells == [(5, 28), (6, 27)], cells
    print("V05_N43_HARD_R_MAX=9")
    print("V05_N43_R9_CELLS=M5L28,M6L27")


def base_N42_raw_clauses():
    # Same five-clause incidence skeleton used by the N42 replay.
    # Each variable occurs exactly three times; total literal incidence is 27.
    return [
        (-4, -5, -6, -7, -8, -9),
        (-1, -2, -3, 7, 8, 9),
        (2, 3, 5, 6, 9),
        (1, 3, 4, 6, 8),
        (1, 2, 4, 5, 7),
    ]


def build_N43_m5_L28_fixture() -> core.CNF:
    raw = base_N42_raw_clauses()
    # Add a fourth occurrence of variable 1 to clause 1. Degrees become
    # d1=4 and d2..d9=3, total incidence 28, while keeping five clauses.
    raw[0] = (1, *raw[0])
    cnf = core.canon_cnf(raw)
    assert len(cnf) == 5, cnf
    assert sum(len(c) for c in cnf) == 28
    assert len(core.vars_of(cnf)) == 9
    assert core.state_units(cnf) == 34
    assert core.input_size_units(cnf) == 43
    degrees = [v05.incidence_degree(cnf, v) for v in range(1, 10)]
    assert sorted(degrees) == [3] * 8 + [4], degrees
    return cnf


def build_N43_m6_L27_fixture() -> core.CNF:
    raw = base_N42_raw_clauses()
    # Split the all-negative six-literal clause into two disjoint triples.
    # Clause count increases 5->6 while literal incidence and every variable
    # incidence degree remain unchanged.
    raw = [(-4, -5, -6), (-7, -8, -9), *raw[1:]]
    cnf = core.canon_cnf(raw)
    assert len(cnf) == 6, cnf
    assert sum(len(c) for c in cnf) == 27
    assert len(core.vars_of(cnf)) == 9
    assert core.state_units(cnf) == 34
    assert core.input_size_units(cnf) == 43
    degrees = [v05.incidence_degree(cnf, v) for v in range(1, 10)]
    assert degrees == [3] * 9, degrees
    return cnf


def verify_fixture(cnf: core.CNF, label: str) -> None:
    class Stub:
        pass

    st = Stub()
    st.residual = cnf
    st.root_vars = tuple(range(1, 10))
    order = v05.proof_pivot_order(st)
    pivot = order[0]
    d = v05.incidence_degree(cnf, pivot)
    assert d == 3, (label, order, d)

    out, stats = core.eliminate_var_capped(cnf, pivot, 43 * 43)
    assert out is not None, (label, stats)
    assert stats["raw_units"] <= 38, (label, stats)
    assert len(core.vars_of(out)) <= 8
    print(f"{label}_SELECTED_PIVOT={pivot}")
    print(f"{label}_SELECTED_DEGREE={d}")
    print(f"{label}_ACTUAL_RAW_UNITS={stats['raw_units']}")
    print(f"{label}=PASS")


def verify_N43_tail_ledger() -> None:
    cap = 43 * 43
    rows = recurrence_raw_bounds_from(Fraction(38), 8)
    got = [raw for _, _, raw, _ in rows]
    expected = [
        Fraction(1381, 12),
        Fraction(1875889, 1728),
        Fraction(1053),
        Fraction(297),
        Fraction(81),
        Fraction(21),
    ]
    assert got == expected, got
    assert all(raw <= cap for raw in got)
    assert max(got) == Fraction(1875889, 1728)
    print("V05_N43_TAIL_LEDGER=PASS")
    print(f"V05_N43_TAIL_MAX_RAW={max(got)}")
    print(f"V05_N43_CAP={cap}")


def selftest() -> None:
    verify_N43_partition()
    verify_fixture(build_N43_m5_L28_fixture(), "V05_N43_M5_L28_FIXTURE")
    verify_fixture(build_N43_m6_L27_fixture(), "V05_N43_M6_L27_FIXTURE")
    verify_N43_tail_ledger()
    print("V05_SELECTOR_BRIDGE_N_LE_43_REGRESSION=PASS")
    print("THEOREM_RUNTIME_HEURISTICS=FORBIDDEN")
    print("UNBOUNDED_TOTALITY=OPEN")
    print("V3_UNIVERSAL_AVAILABILITY=OPEN")
    print("P_VS_NP=OPEN")


if __name__ == "__main__":
    selftest()
