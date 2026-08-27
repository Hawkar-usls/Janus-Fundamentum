#!/usr/bin/env python3
"""Executable regression for JANUS C025 v0.5 proof-selector through N=52.

Protects the finite N52 partition, the r=10 bounded bridge, and a real
r=11,m=7,L=33 degree-3 fixture. P vs NP remains OPEN.
"""

from fractions import Fraction
from math import comb

from experiments.direct import janus_unified_proof_carrying_akinator_jec as core
from experiments.direct import janus_proof_selector_v05_candidate as v05

P_VS_NP = "OPEN"
CAP = 52 * 52


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
    rows = []
    for n in range(n0, 2, -1):
        raw = min(T(s), Fraction(Uraw(n)))
        next_s = min(T(s), Fraction(Smax(n - 1)))
        rows.append((n, s, raw, next_s))
        s = next_s
    return rows


def verify_partition() -> None:
    N = 52
    r9 = []
    for m in range(7, N):
        L = N - 1 - 9 - m
        if L >= 27 and L >= 2 * m:
            r9.append((m, L))
    assert r9 == [(7,35),(8,34),(9,33),(10,32),(11,31),(12,30),(13,29),(14,28)], r9

    r10 = []
    for m in range(7, N):
        L = N - 1 - 10 - m
        if L >= 30 and L >= 2 * m:
            r10.append((m, L))
    assert r10 == [(7,34),(8,33),(9,32),(10,31),(11,30)], r10

    r11 = []
    for m in range(7, N):
        L = N - 1 - 11 - m
        if L >= 33 and L >= 2 * m:
            r11.append((m, L))
    assert r11 == [(7,33)], r11
    print('V05_N52_PARTITION=PASS')


def verify_r_le_8_recurrence() -> None:
    maximum = Fraction(0)
    for r in range(1, 9):
        for _, _, raw, _ in recurrence_raw_bounds_from(Fraction(52-r), r):
            maximum = max(maximum, raw)
            assert raw <= CAP, (r, raw, CAP)
    assert maximum == Fraction(3420529, 1728), maximum
    print(f'V05_N52_R_LE_8_RECURRENCE_MAX={maximum}')
    print('V05_N52_R_LE_8_RECURRENCE=PASS')


def verify_r9_tail() -> None:
    got = [raw for _, _, raw, _ in recurrence_raw_bounds_from(Fraction(47), 8)]
    expected = [Fraction(532,3), Fraction(279949,108), Fraction(1053), Fraction(297), Fraction(81), Fraction(21)]
    assert got == expected, got
    assert max(got) == Fraction(279949,108)
    assert all(x <= CAP for x in got)
    print('V05_N52_R9_TAIL=PASS')


def verify_r10_bridge_arithmetic() -> None:
    assert T(Fraction(47)) == Fraction(532,3)
    assert T(Fraction(91)) == Fraction(676)
    assert T(Fraction(169)) == Fraction(2353)
    assert Uraw(6) == 1053
    assert Fraction(532,3) < CAP
    assert Fraction(676) < CAP
    assert Fraction(2353) < CAP
    assert 1053 < CAP

    for m1 in range(7, 11):
        L1 = 47 - 1 - m1
        assert L1 // 9 <= 4
        for d in range(1, 5):
            assert m1 - d + (d*d)//4 <= 10

    assert 1 + 10 * (1 + 8) == 91
    coarse_non_dense = max(10 - d + (d*d)//4 for d in range(1, 10))
    assert coarse_non_dense == 21
    assert 1 + 21 * (1 + 7) == 169
    print('V05_N52_R10_BRIDGE_ARITHMETIC=PASS')


def build_r11_m7_L33_fixture() -> core.CNF:
    # Eleven variables, each of degree 3 across seven clauses; clause widths
    # are 5,4,5,5,4,5,5. Pivot 1 has split 1+2.
    raw = [
        (1, 2, 6, 7, 11),
        (4, 6, 9, 10),
        (-1, 5, 6, 8, 9),
        (2, 3, 5, 10, 11),
        (2, 5, 7, 8),
        (-1, 3, 4, 8, 11),
        (3, 4, 7, 9, 10),
    ]
    cnf = core.canon_cnf(raw)
    assert len(cnf) == 7, cnf
    assert sum(len(c) for c in cnf) == 33
    assert len(core.vars_of(cnf)) == 11
    assert core.state_units(cnf) == 41
    assert core.input_size_units(cnf) == 52
    assert [v05.incidence_degree(cnf, v) for v in range(1, 12)] == [3] * 11
    return cnf


def verify_r11_fixture() -> None:
    class Stub: pass
    roots = tuple(range(1, 12))
    st = Stub(); st.root_vars = roots
    current = build_r11_m7_L33_fixture()
    st.residual = current
    pivot = v05.proof_pivot_order(st)[0]
    assert pivot == 1
    assert v05.incidence_degree(current, pivot) == 3

    current, stats = core.eliminate_var_capped(current, pivot, CAP)
    assert current is not None, stats
    assert {stats['positive'], stats['negative']} == {1, 2}, stats
    assert len(current) <= 6, (current, stats)
    assert stats['raw_units'] <= CAP
    print(f'V05_N52_R11_POST_CLAUSES={len(current)}')
    print('V05_N52_R11_M7_L33_FIXTURE=PASS')


def selftest() -> None:
    v05.selftest()
    verify_partition()
    verify_r_le_8_recurrence()
    verify_r9_tail()
    verify_r10_bridge_arithmetic()
    verify_r11_fixture()
    print('V05_SELECTOR_BRIDGE_N_LE_52_REGRESSION=PASS')
    print('THEOREM_RUNTIME_HEURISTICS=FORBIDDEN')
    print('UNBOUNDED_TOTALITY=OPEN')
    print('V3_UNIVERSAL_AVAILABILITY=OPEN')
    print('UNIVERSAL_GPEI=OPEN')
    print('P_VS_NP=OPEN')


if __name__ == '__main__':
    selftest()
