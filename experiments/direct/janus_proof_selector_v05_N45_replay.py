#!/usr/bin/env python3
"""Executable regression for JANUS C025 v0.5 proof-selector through N=45.

Finite fixtures and arithmetic replay are regression evidence only.
The finite theorem statement lives in the corresponding JSON artifact.
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
    rows = []
    while n > 2:
        raw = min(T(s), Fraction(Uraw(n)))
        next_s = min(T(s), Fraction(Smax(n - 1)))
        rows.append((n, s, raw, next_s))
        s = next_s
        n -= 1
    return rows


def recurrence_raw_bounds_root(N: int, r0: int):
    return recurrence_raw_bounds_from(Fraction(N - r0), r0)


def verify_N45_partition() -> None:
    N = 45
    hard_r_max = (N - 6) // 4
    assert hard_r_max == 9
    cells = []
    r = 9
    for m in range(5, N):
        L = N - 1 - r - m
        if L >= 3 * r and L >= 2 * m and L >= r:
            cells.append((m, L))
    assert cells == [(5, 30), (6, 29), (7, 28), (8, 27)], cells
    print("V05_N45_HARD_R_MAX=9")
    print("V05_N45_R9_CELLS=M5L30,M6L29,M7L28,M8L27")


def verify_N45_r_le_8_recurrence() -> None:
    cap = 45 * 45
    maximum = Fraction(0)
    for r in range(1, 9):
        for _, _, raw, _ in recurrence_raw_bounds_root(45, r):
            maximum = max(maximum, raw)
            assert raw <= cap, (r, raw, cap)
    assert maximum == 1053, maximum
    print("V05_N45_R_LE_8_RECURRENCE=PASS")
    print(f"V05_N45_R_LE_8_MAX_RAW={maximum}")


def base_N42_raw_clauses():
    return [
        (-4, -5, -6, -7, -8, -9),
        (-1, -2, -3, 7, 8, 9),
        (2, 3, 5, 6, 9),
        (1, 3, 4, 6, 8),
        (1, 2, 4, 5, 7),
    ]


def build_N45_m5_L30_fixture() -> core.CNF:
    raw = base_N42_raw_clauses()
    raw[0] = (1, 2, 3, *raw[0])
    cnf = core.canon_cnf(raw)
    assert len(cnf) == 5, cnf
    assert sum(len(c) for c in cnf) == 30
    assert len(core.vars_of(cnf)) == 9
    assert core.state_units(cnf) == 36
    assert core.input_size_units(cnf) == 45
    degrees = [v05.incidence_degree(cnf, v) for v in range(1, 10)]
    assert sorted(degrees) == [3] * 6 + [4, 4, 4], degrees
    return cnf


def build_N45_m6_L29_fixture() -> core.CNF:
    raw = base_N42_raw_clauses()
    raw = [(-4, -5, -6), (-7, -8, -9), *raw[1:]]
    raw[0] = (1, 2, *raw[0])
    cnf = core.canon_cnf(raw)
    assert len(cnf) == 6, cnf
    assert sum(len(c) for c in cnf) == 29
    assert len(core.vars_of(cnf)) == 9
    assert core.state_units(cnf) == 36
    assert core.input_size_units(cnf) == 45
    degrees = [v05.incidence_degree(cnf, v) for v in range(1, 10)]
    assert sorted(degrees) == [3] * 7 + [4, 4], degrees
    return cnf


def build_N45_m7_L28_fixture() -> core.CNF:
    raw = base_N42_raw_clauses()
    raw = [(1, -4, -5), (-6, -7), (-8, -9), *raw[1:]]
    cnf = core.canon_cnf(raw)
    assert len(cnf) == 7, cnf
    assert sum(len(c) for c in cnf) == 28
    assert len(core.vars_of(cnf)) == 9
    assert core.state_units(cnf) == 36
    assert core.input_size_units(cnf) == 45
    degrees = [v05.incidence_degree(cnf, v) for v in range(1, 10)]
    assert sorted(degrees) == [3] * 8 + [4], degrees
    return cnf


def build_N45_m8_L27_fixture() -> core.CNF:
    raw = [
        (-1, 2, 3, 4),
        (1, 2, 3, 5),
        (1, 2, 3, 6),
        (4, 5, 6),
        (4, 7, 8),
        (5, 7, 9),
        (6, 8, 9),
        (7, 8, 9),
    ]
    cnf = core.canon_cnf(raw)
    assert len(cnf) == 8, cnf
    assert sum(len(c) for c in cnf) == 27
    assert len(core.vars_of(cnf)) == 9
    assert core.state_units(cnf) == 36
    assert core.input_size_units(cnf) == 45
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

    out, stats = core.eliminate_var_capped(cnf, pivot, 45 * 45)
    assert out is not None, (label, stats)
    assert stats["raw_units"] <= 40, (label, stats)
    assert len(core.vars_of(out)) <= 8
    print(f"{label}_SELECTED_PIVOT={pivot}")
    print(f"{label}_SELECTED_DEGREE={d}")
    print(f"{label}_ACTUAL_RAW_UNITS={stats['raw_units']}")
    print(f"{label}=PASS")


def verify_N45_tail_ledger() -> None:
    cap = 45 * 45
    rows = recurrence_raw_bounds_from(Fraction(40), 8)
    got = [raw for _, _, raw, _ in rows]
    expected = [
        Fraction(511, 4),
        Fraction(85747, 64),
        Fraction(1053),
        Fraction(297),
        Fraction(81),
        Fraction(21),
    ]
    assert got == expected, got
    assert all(raw <= cap for raw in got)
    assert max(got) == Fraction(85747, 64)
    print("V05_N45_TAIL_LEDGER=PASS")
    print(f"V05_N45_TAIL_MAX_RAW={max(got)}")
    print(f"V05_N45_CAP={cap}")


def selftest() -> None:
    v05.selftest()
    verify_N45_partition()
    verify_N45_r_le_8_recurrence()
    verify_fixture(build_N45_m5_L30_fixture(), "V05_N45_M5_L30_FIXTURE")
    verify_fixture(build_N45_m6_L29_fixture(), "V05_N45_M6_L29_FIXTURE")
    verify_fixture(build_N45_m7_L28_fixture(), "V05_N45_M7_L28_FIXTURE")
    verify_fixture(build_N45_m8_L27_fixture(), "V05_N45_M8_L27_FIXTURE")
    verify_N45_tail_ledger()
    print("V05_SELECTOR_BRIDGE_N_LE_45_REGRESSION=PASS")
    print("THEOREM_RUNTIME_HEURISTICS=FORBIDDEN")
    print("UNBOUNDED_TOTALITY=OPEN")
    print("V3_UNIVERSAL_AVAILABILITY=OPEN")
    print("UNIVERSAL_GPEI=OPEN")
    print("P_VS_NP=OPEN")


if __name__ == "__main__":
    selftest()
