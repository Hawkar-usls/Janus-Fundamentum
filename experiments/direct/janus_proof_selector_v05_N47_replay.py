#!/usr/bin/env python3
"""Executable regression for JANUS C025 v0.5 proof-selector through N=47.

Checks the finite partition, r<=8 exact ledger, a degree-3 r=9 fixture,
and the r=10,m=6,L=30 transition into the proved m<=5 invariant.
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


def verify_N47_partition() -> None:
    N = 47
    assert (N - 6) // 4 == 10
    r9 = []
    r10 = []
    for m in range(5, N):
        L9 = N - 1 - 9 - m
        if L9 >= 27 and L9 >= 2 * m:
            r9.append((m, L9))
        L10 = N - 1 - 10 - m
        if L10 >= 30 and L10 >= 2 * m:
            r10.append((m, L10))
    assert r9 == [(5,32),(6,31),(7,30),(8,29),(9,28),(10,27)], r9
    assert r10 == [(5,31),(6,30)], r10
    print("V05_N47_PARTITION=PASS")


def verify_N47_r_le_8_recurrence() -> None:
    cap = 47 * 47
    maximum = Fraction(0)
    where = None
    for r in range(1, 9):
        for n, s, raw, _ in recurrence_raw_bounds_root(47, r):
            if raw > maximum:
                maximum = raw
                where = (r, n, s)
            assert raw <= cap
    assert maximum == Fraction(130429, 108), maximum
    assert where == (8, 7, Fraction(364, 3)), where
    print("V05_N47_R_LE_8_RECURRENCE=PASS")
    print(f"V05_N47_R_LE_8_MAX_RAW={maximum}")


def build_N47_r9_m10_L27_fixture() -> core.CNF:
    raw = [
        (-1, 2, 3),
        (1, 2, 4),
        (1, 2, 5),
        (3, 4, 5),
        (3, 4, 6),
        (5, 7, 8),
        (6, 7, 8),
        (6, 9),
        (7, 9),
        (8, 9),
    ]
    cnf = core.canon_cnf(raw)
    assert len(cnf) == 10, cnf
    assert sum(len(c) for c in cnf) == 27
    assert len(core.vars_of(cnf)) == 9
    assert core.state_units(cnf) == 38
    assert core.input_size_units(cnf) == 47
    degrees = [v05.incidence_degree(cnf, v) for v in range(1, 10)]
    assert degrees == [3] * 9, degrees
    return cnf


def verify_N47_r9_fixture_and_tail() -> None:
    class Stub:
        pass

    cnf = build_N47_r9_m10_L27_fixture()
    st = Stub()
    st.residual = cnf
    st.root_vars = tuple(range(1, 10))
    pivot = v05.proof_pivot_order(st)[0]
    assert pivot == 1
    assert v05.incidence_degree(cnf, pivot) == 3
    out, stats = core.eliminate_var_capped(cnf, pivot, 47 * 47)
    assert out is not None
    assert stats["raw_units"] <= 42, stats
    assert len(core.vars_of(out)) <= 8

    cap = 47 * 47
    got = [raw for _, _, raw, _ in recurrence_raw_bounds_from(Fraction(42), 8)]
    expected = [
        Fraction(1693, 12),
        Fraction(2827489, 1728),
        Fraction(1053),
        Fraction(297),
        Fraction(81),
        Fraction(21),
    ]
    assert got == expected, got
    assert max(got) == Fraction(2827489, 1728)
    assert all(x <= cap for x in got)
    print("V05_N47_R9_FIXTURE_AND_TAIL=PASS")


def build_N47_r10_m6_L30_fixture() -> core.CNF:
    raw = [
        (-1, 2, 3, 4, 5),
        (1, 2, 3, 4, 6),
        (1, 2, 3, 4, 7),
        (5, 6, 8, 9, 10),
        (5, 7, 8, 9, 10),
        (6, 7, 8, 9, 10),
    ]
    cnf = core.canon_cnf(raw)
    assert len(cnf) == 6, cnf
    assert sum(len(c) for c in cnf) == 30
    assert len(core.vars_of(cnf)) == 10
    assert core.state_units(cnf) == 37
    assert core.input_size_units(cnf) == 47
    degrees = [v05.incidence_degree(cnf, v) for v in range(1, 11)]
    assert degrees == [3] * 10, degrees
    return cnf


def verify_N47_r10_to_m_le_5() -> None:
    class Stub:
        pass

    cnf = build_N47_r10_m6_L30_fixture()
    st = Stub()
    st.residual = cnf
    st.root_vars = tuple(range(1, 11))
    pivot = v05.proof_pivot_order(st)[0]
    assert pivot == 1
    assert v05.incidence_degree(cnf, pivot) == 3
    out, stats = core.eliminate_var_capped(cnf, pivot, 47 * 47)
    assert out is not None, stats
    assert {stats["positive"], stats["negative"]} == {1, 2}, stats
    assert stats["retained"] == 3, stats
    assert stats["pairs"] == 2, stats
    assert stats["raw_units"] <= 42, stats
    assert len(out) <= 5, (out, stats)
    assert len(core.vars_of(out)) <= 9
    assert 1 + 5 * len(core.vars_of(out)) <= 46
    print("V05_N47_R10_M6_TO_M_LE_5=PASS")


def selftest() -> None:
    v05.selftest()
    verify_N47_partition()
    verify_N47_r_le_8_recurrence()
    verify_N47_r9_fixture_and_tail()
    verify_N47_r10_to_m_le_5()
    print("V05_SELECTOR_BRIDGE_N_LE_47_REGRESSION=PASS")
    print("THEOREM_RUNTIME_HEURISTICS=FORBIDDEN")
    print("UNBOUNDED_TOTALITY=OPEN")
    print("V3_UNIVERSAL_AVAILABILITY=OPEN")
    print("UNIVERSAL_GPEI=OPEN")
    print("P_VS_NP=OPEN")


if __name__ == "__main__":
    selftest()
