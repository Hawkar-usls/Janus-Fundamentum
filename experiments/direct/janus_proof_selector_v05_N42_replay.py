#!/usr/bin/env python3
"""Executable regression for the C025 v0.5 proof-selector bridge.

Authority split:
- universal selector and arithmetic statements are proved in the JSON theorem;
- this executable checks implementation agreement and exact rational ledgers;
- finite fixtures are regression evidence only, never a P=NP proof.
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


def recurrence_raw_bounds(N: int, r0: int):
    s = Fraction(N - r0)
    n = r0
    out = []
    while n > 2:
        raw = min(T(s), Fraction(Uraw(n)))
        next_s = min(T(s), Fraction(Smax(n - 1)))
        out.append((n, s, raw, next_s))
        s = next_s
        n -= 1
    return out


def verify_N26_selector_base() -> None:
    N = 26
    for r in (9, 10):
        mmax = N - 2 * r - 1
        assert mmax >= 1
        for m in range(1, mmax + 1):
            L = N - 1 - r - m
            if L < r or L < 2 * m:
                continue
            assert L < 2 * r
            assert L // r <= 1
    print("V05_N26_MIN_DEGREE1_REROOT_BASE=PASS")


def verify_N27_to_N41_hard_recurrence() -> None:
    for N in range(27, 42):
        cap = N * N
        hard_r_max = (N - 6) // 4
        maximum = Fraction(0)
        for r in range(1, hard_r_max + 1):
            for _, _, raw, _ in recurrence_raw_bounds(N, r):
                maximum = max(maximum, raw)
                assert raw <= cap, ("HARD_RECURRENCE_CAP_FAILURE", N, r, raw, cap)
        print(f"V05_N{N}_HARD_RECURRENCE_MAX={maximum}")
    print("V05_N27_TO_N41_HARD_RECURRENCE=PASS")


def build_N42_degree3_fixture() -> core.CNF:
    # Nine variables, five clauses, 27 incidences.  Each variable is absent
    # from exactly two of five clauses with absence-counts 3,3,4,4,4.
    absence_pairs = {
        1: (1, 3),
        2: (1, 4),
        3: (1, 5),
        4: (2, 3),
        5: (2, 4),
        6: (2, 5),
        7: (3, 4),
        8: (3, 5),
        9: (4, 5),
    }
    occurrences = {v: [] for v in range(1, 10)}
    raw = []
    for ci in range(1, 6):
        clause = []
        for v in range(1, 10):
            if ci in absence_pairs[v]:
                continue
            occurrences[v].append(ci)
            # First occurrence negative, later occurrences positive: split 1+2.
            lit = -v if len(occurrences[v]) == 1 else v
            clause.append(lit)
        raw.append(tuple(clause))
    cnf = core.canon_cnf(raw)
    assert len(cnf) == 5
    assert sum(len(c) for c in cnf) == 27
    assert core.state_units(cnf) == 33
    assert core.input_size_units(cnf) == 42
    for v in range(1, 10):
        assert v05.incidence_degree(cnf, v) == 3
    return cnf


def verify_N42_executed_selector() -> None:
    class Stub:
        pass

    cnf = build_N42_degree3_fixture()
    st = Stub()
    st.residual = cnf
    st.root_vars = tuple(range(1, 10))
    order = v05.proof_pivot_order(st)
    pivot = order[0]
    assert v05.incidence_degree(cnf, pivot) == 3

    out, stats = core.eliminate_var_capped(cnf, pivot, 42 * 42)
    assert out is not None
    assert stats["raw_units"] <= 37, stats
    assert len(core.vars_of(out)) <= 8
    print(f"V05_N42_SELECTED_PIVOT={pivot}")
    print(f"V05_N42_ACTUAL_RAW_UNITS={stats['raw_units']}")
    print("V05_N42_DEGREE3_FIXTURE=PASS")


def verify_N42_tail_ledger() -> None:
    cap = 42 * 42
    s = Fraction(37)
    expected = [109, 973, 1053, 297, 81, 21]
    got = []
    for n in range(8, 2, -1):
        raw = min(T(s), Fraction(Uraw(n)))
        got.append(int(raw) if raw.denominator == 1 else raw)
        assert raw <= cap
        s = min(T(s), Fraction(Smax(n - 1)))
    assert got == expected, got
    print("V05_N42_TAIL_LEDGER=PASS")


def verify_selector_implementation() -> None:
    v05.selftest()
    old = core.canonical_pivot_order
    try:
        v05.activate_on_imported_core()
        assert core.canonical_pivot_order is v05.proof_pivot_order
    finally:
        core.canonical_pivot_order = old
    print("V05_PROCESS_LOCAL_ACTIVATION=PASS")


def selftest() -> None:
    verify_selector_implementation()
    verify_N26_selector_base()
    verify_N27_to_N41_hard_recurrence()
    verify_N42_executed_selector()
    verify_N42_tail_ledger()
    print("V05_SELECTOR_BRIDGE_N_LE_42_REGRESSION=PASS")
    print("THEOREM_RUNTIME_HEURISTICS=FORBIDDEN")
    print("UNBOUNDED_TOTALITY=OPEN")
    print("V3_UNIVERSAL_AVAILABILITY=OPEN")
    print("P_VS_NP=OPEN")


if __name__ == "__main__":
    selftest()
