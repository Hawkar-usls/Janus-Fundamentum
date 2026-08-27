#!/usr/bin/env python3
"""Executable regression for JANUS C025 v0.5 proof-selector through N=48.

Checks the exact finite partition, the r=9 degree-3 tail, and the unique
r=10,m=7,L=30 transition into the proved m<=6 invariant.
Regression evidence is not an unbounded proof. P vs NP remains OPEN.
"""

from fractions import Fraction
from math import comb

from experiments.direct import janus_unified_proof_carrying_akinator_jec as core
from experiments.direct import janus_proof_selector_v05_candidate as v05

P_VS_NP = "OPEN"
CAP = 48 * 48


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
    out = []
    for n in range(n0, 2, -1):
        raw = min(T(s), Fraction(Uraw(n)))
        next_s = min(T(s), Fraction(Smax(n - 1)))
        out.append((n, s, raw, next_s))
        s = next_s
    return out


def verify_partition() -> None:
    N = 48
    assert (N - 8) // 4 == 10

    r9 = []
    for m in range(7, N):
        L = N - 1 - 9 - m
        if L >= 27 and L >= 2 * m:
            r9.append((m, L))
    assert r9 == [(7, 31), (8, 30), (9, 29), (10, 28), (11, 27)], r9

    r10 = []
    for m in range(7, N):
        L = N - 1 - 10 - m
        if L >= 30 and L >= 2 * m:
            r10.append((m, L))
    assert r10 == [(7, 30)], r10
    print("V05_N48_PARTITION=PASS")


def verify_r_le_8_recurrence() -> None:
    maximum = Fraction(0)
    for r in range(1, 9):
        s0 = Fraction(48 - r)
        for _, _, raw, _ in recurrence_raw_bounds_from(s0, r):
            maximum = max(maximum, raw)
            assert raw <= CAP, (r, raw, CAP)
    print(f"V05_N48_R_LE_8_RECURRENCE_MAX={maximum}")
    print("V05_N48_R_LE_8_RECURRENCE=PASS")


def build_r9_m11_L27_fixture() -> core.CNF:
    raw = [
        (-1, 2),
        (3, 4),
        (1, 2),
        (3, 5),
        (1, 3),
        (2, 6),
        (4, 5, 6),
        (4, 7, 8),
        (5, 7, 9),
        (6, 8, 9),
        (7, 8, 9),
    ]
    cnf = core.canon_cnf(raw)
    assert len(cnf) == 11, cnf
    assert sum(len(c) for c in cnf) == 27
    assert len(core.vars_of(cnf)) == 9
    assert core.state_units(cnf) == 39
    assert core.input_size_units(cnf) == 48
    assert [v05.incidence_degree(cnf, v) for v in range(1, 10)] == [3] * 9
    return cnf


def verify_r9_fixture_and_tail() -> None:
    class Stub:
        pass

    cnf = build_r9_m11_L27_fixture()
    st = Stub(); st.residual = cnf; st.root_vars = tuple(range(1, 10))
    pivot = v05.proof_pivot_order(st)[0]
    assert v05.incidence_degree(cnf, pivot) == 3
    out, stats = core.eliminate_var_capped(cnf, pivot, CAP)
    assert out is not None, stats
    assert stats["raw_units"] <= 43, stats
    assert len(core.vars_of(out)) <= 8

    got = [raw for _, _, raw, _ in recurrence_raw_bounds_from(Fraction(43), 8)]
    expected = [
        Fraction(148),
        Fraction(7207, 4),
        Fraction(1053),
        Fraction(297),
        Fraction(81),
        Fraction(21),
    ]
    assert got == expected, got
    assert max(got) == Fraction(7207, 4)
    assert all(x <= CAP for x in got)
    print(f"V05_N48_R9_SELECTED_PIVOT={pivot}")
    print(f"V05_N48_R9_ACTUAL_RAW_UNITS={stats['raw_units']}")
    print("V05_N48_R9_TAIL=PASS")


def build_r10_m7_L30_fixture() -> core.CNF:
    raw = [
        (1, 2, 3, 4, 5),
        (1, 6, 7, 8, 9),
        (-1, 2, 6, 10),
        (3, 4, 7, 10),
        (5, 8, 9, 10),
        (2, 3, 6, 7),
        (4, 5, 8, 9),
    ]
    cnf = core.canon_cnf(raw)
    assert len(cnf) == 7, cnf
    assert sum(len(c) for c in cnf) == 30
    assert len(core.vars_of(cnf)) == 10
    assert core.state_units(cnf) == 38
    assert core.input_size_units(cnf) == 48
    assert [v05.incidence_degree(cnf, v) for v in range(1, 11)] == [3] * 10
    return cnf


def verify_r10_enters_six_clause_invariant() -> None:
    class Stub:
        pass

    cnf = build_r10_m7_L30_fixture()
    roots = tuple(range(1, 11))
    st = Stub(); st.residual = cnf; st.root_vars = roots
    pivot = v05.proof_pivot_order(st)[0]
    assert pivot == 1
    assert v05.incidence_degree(cnf, pivot) == 3
    out, stats = core.eliminate_var_capped(cnf, pivot, CAP)
    assert out is not None, stats
    assert {stats["positive"], stats["negative"]} == {1, 2}, stats
    assert len(out) <= 6, (out, stats)
    assert stats["raw_units"] <= 61, stats

    # Follow the same min-degree selector and verify that the fixture stays
    # inside m<=6 while every exact ordinary step stays below the frozen cap.
    current = out
    steps = 1
    while core.vars_of(current):
        st.residual = current
        order = v05.proof_pivot_order(st)
        if not order:
            break
        p = order[0]
        nxt, step_stats = core.eliminate_var_capped(current, p, CAP)
        assert nxt is not None, (p, step_stats)
        assert step_stats["raw_units"] <= CAP, (p, step_stats)
        assert len(nxt) <= 6, (p, nxt, step_stats)
        current = nxt
        steps += 1

    print(f"V05_N48_R10_SELECTED_PIVOT={pivot}")
    print(f"V05_N48_R10_POST_CLAUSES={len(out)}")
    print(f"V05_N48_R10_REPLAY_STEPS={steps}")
    print("V05_N48_R10_TO_M_LE_6_INVARIANT=PASS")


def selftest() -> None:
    v05.selftest()
    verify_partition()
    verify_r_le_8_recurrence()
    verify_r9_fixture_and_tail()
    verify_r10_enters_six_clause_invariant()
    print("V05_SELECTOR_BRIDGE_N_LE_48_REGRESSION=PASS")
    print("THEOREM_RUNTIME_HEURISTICS=FORBIDDEN")
    print("UNBOUNDED_TOTALITY=OPEN")
    print("V3_UNIVERSAL_AVAILABILITY=OPEN")
    print("UNIVERSAL_GPEI=OPEN")
    print("P_VS_NP=OPEN")


if __name__ == "__main__":
    selftest()
