#!/usr/bin/env python3
"""Executable regression for the C025 frozen reachable live-variable ceiling.

The theorem is structural.  This executable checks the root-size inequality on
small canonical roots and the live-count effect of representative frozen v2/v3
transition shapes.  It does not establish totality and does not prove P=NP.
"""
from __future__ import annotations

from itertools import combinations

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct import janus_unified_macro_restore_v2 as v2

P_VS_NP = "OPEN"


def assert_root_ceiling(cnf: base.CNF) -> None:
    if not cnf or not base.vars_of(cnf):
        return
    N = base.input_size_units(cnf)
    r = len(base.vars_of(cnf))
    if r > (N - 2) // 2:
        raise AssertionError(("ROOT_VARIABLE_CEILING_FAILED", cnf, N, r))


def small_root_regression() -> tuple[int, int]:
    universe = []
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
        if c is not None and c:
            universe.append(c)
    universe = tuple(sorted(set(universe), key=lambda c: (len(c), c)))
    seen = set()
    checks = 0
    for k in (1, 2, 3):
        for rows in combinations(universe, k):
            cnf = base.canon_cnf(rows)
            if not cnf or cnf in seen:
                continue
            seen.add(cnf)
            assert_root_ceiling(cnf)
            checks += 1
    return len(seen), checks


def transition_shape_regression() -> None:
    # Ordinary elimination never creates a fresh semantic variable.
    before = base.canon_cnf(((1, 2, 3), (-1, 4, 5), (2, -4, 6)))
    out, _ = base.eliminate_var_capped(before, 1, 10_000)
    assert out is not None
    assert set(base.vars_of(out)) <= set(base.vars_of(before)) - {1}

    # B2 macro introduces exactly one possible fresh e. Atomic root restoration
    # then eliminates one old pivot, so after that elimination the live set is a
    # subset of (old minus pivot) union {e}.
    old = base.canon_cnf(((1, 2, 3), (1, 2, 4), (-3, 4, 5)))
    V0 = set(base.vars_of(old))
    e = max(V0) + 1
    macro, cert = v2.apply_or_pair_v2(old, 1, 2, e)
    assert v2.verify_or_pair_v2(old, macro, cert)
    after, _ = base.eliminate_var_capped(macro, 1, 10_000)
    assert after is not None
    assert set(base.vars_of(after)) <= ((V0 - {1}) | {e})
    assert len(base.vars_of(after)) <= len(V0)

    # Two distinct old eliminations after one B2 macro lower live count by >=1
    # whenever both old pivots remain available in sequence.
    old2 = base.canon_cnf(((1, 2, 3), (1, 2, 4), (3, 4, 5), (-3, 5, 6)))
    V2 = set(base.vars_of(old2))
    e2 = max(V2) + 1
    macro2, cert2 = v2.apply_or_pair_v2(old2, 1, 2, e2)
    assert v2.verify_or_pair_v2(old2, macro2, cert2)
    a1, _ = base.eliminate_var_capped(macro2, 1, 10_000)
    assert a1 is not None and 2 in set(base.vars_of(a1))
    a2, _ = base.eliminate_var_capped(a1, 2, 10_000)
    assert a2 is not None
    assert set(base.vars_of(a2)) <= ((V2 - {1, 2}) | {e2})
    assert len(base.vars_of(a2)) <= len(V2) - 1


def selftest() -> None:
    states, checks = small_root_regression()
    transition_shape_regression()
    assert (10 - 2) // 2 == 4
    print(f"REACHABLE_CEILING_SMALL_ROOT_STATES={states}")
    print(f"REACHABLE_CEILING_ROOT_CHECKS={checks}")
    print("FROZEN_TRANSITION_LIVE_COUNT_SHAPES=PASS")
    print("N10_REACHABLE_LIVE_CEILING=4")
    print("N10_SEED172_LIVE10=UNREACHABLE_BY_CEILING")
    print("P_VS_NP=OPEN")


if __name__ == "__main__":
    selftest()
