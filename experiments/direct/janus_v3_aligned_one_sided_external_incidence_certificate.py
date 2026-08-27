#!/usr/bin/env python3
"""Executable certificate for the audited C025 v3 aligned one-sided corridor.

This checks a proved sufficient corridor only.  It does NOT modify the frozen
solver, does NOT claim universal v3 availability, and does NOT prove P=NP.

The structural condition for a selected sign-aware pair (a,b) is:
  * every clause containing both selected literals is a replaceable pair clause;
  * outside those pair clauses, variable |a| may occur only as literal a;
  * outside those pair clauses, variable |b| may occur only as literal b.

For a cap-admissible canonical B2 macro M, the contract checks that exact raw-
capped elimination of |a| then |b| succeeds with

    raw_A <= state_units(M)
    raw_B <= state_units(after_A) <= state_units(M)

before optional subsumption compression.  The old stronger -7/-10 bookkeeping
is deliberately NOT required because canonical macro subsumption can remove
some definitional clauses (e.g. when (a OR b) becomes unit (-e)).
"""
from __future__ import annotations

from dataclasses import dataclass

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct import janus_unified_macro_restore_v2 as v2

P_VS_NP = "OPEN"


@dataclass(frozen=True)
class CorridorCertificate:
    pair: tuple[int, int]
    extension: int
    macro_units: int
    after_a_units: int
    after_b_units: int
    raw_a_units: int
    raw_b_units: int
    before_live: int
    after_live: int


def pair_clauses(cnf: base.CNF, a: int, b: int) -> tuple[base.Clause, ...]:
    return tuple(c for c in cnf if a in c and b in c)


def is_aligned_one_sided(cnf: base.CNF, a: int, b: int) -> bool:
    A, B = abs(a), abs(b)
    if A == B or not pair_clauses(cnf, a, b):
        return False

    for c in cnf:
        if a in c and b in c:
            continue
        vars_c = {abs(l) for l in c}
        if A in vars_c and a not in c:
            return False
        if B in vars_c and b not in c:
            return False
    return True


def certify(
    cnf: base.CNF,
    a: int,
    b: int,
    *,
    cap: int,
) -> CorridorCertificate:
    if not is_aligned_one_sided(cnf, a, b):
        raise ValueError("PAIR_NOT_IN_ALIGNED_ONE_SIDED_CORRIDOR")

    before_live_set = set(base.vars_of(cnf))
    A, B = abs(a), abs(b)
    if A not in before_live_set or B not in before_live_set:
        raise ValueError("PAIR_VARIABLE_NOT_LIVE")

    e = max(before_live_set, default=0) + 1
    macro, macro_cert = v2.apply_or_pair_v2(cnf, a, b, e)
    if not v2.verify_or_pair_v2(cnf, macro, macro_cert):
        raise AssertionError("B2_MACRO_REPLAY_FAILED")

    macro_units = base.state_units(macro)
    if macro_units > cap:
        raise ValueError("MACRO_NOT_CAP_ADMISSIBLE")

    after_a, stats_a = base.eliminate_var_capped(macro, A, cap)
    if after_a is None:
        raise AssertionError("ALIGNED_CORRIDOR_FIRST_ELIMINATION_OVERFLOW")
    if not base.verify_elimination_transition(macro, A, after_a, cap):
        raise AssertionError("FIRST_ELIMINATION_REPLAY_FAILED")
    raw_a = int(stats_a["raw_units"])
    if raw_a > macro_units:
        raise AssertionError("FIRST_RAW_MONOTONICITY_CONTRACT_FAILED")

    after_a_units = base.state_units(after_a)
    if after_a_units > macro_units:
        raise AssertionError("FIRST_CANONICAL_SIZE_CONTRACT_FAILED")

    after_b, stats_b = base.eliminate_var_capped(after_a, B, cap)
    if after_b is None:
        raise AssertionError("ALIGNED_CORRIDOR_SECOND_ELIMINATION_OVERFLOW")
    if not base.verify_elimination_transition(after_a, B, after_b, cap):
        raise AssertionError("SECOND_ELIMINATION_REPLAY_FAILED")
    raw_b = int(stats_b["raw_units"])
    if raw_b > after_a_units:
        raise AssertionError("SECOND_RAW_MONOTONICITY_CONTRACT_FAILED")

    after_b_units = base.state_units(after_b)
    if after_b_units > after_a_units:
        raise AssertionError("SECOND_CANONICAL_SIZE_CONTRACT_FAILED")

    after_live_set = set(base.vars_of(after_b))
    if A in after_live_set or B in after_live_set:
        raise AssertionError("OLD_PIVOT_SURVIVED")
    if not after_live_set <= ((before_live_set - {A, B}) | {e}):
        raise AssertionError("UNEXPECTED_NEW_LIVE_VARIABLE")
    if len(after_live_set) > len(before_live_set) - 1:
        raise AssertionError("ROOT_FREE_PROGRESS_NOT_STRICT")

    return CorridorCertificate(
        pair=(a, b),
        extension=e,
        macro_units=macro_units,
        after_a_units=after_a_units,
        after_b_units=after_b_units,
        raw_a_units=raw_a,
        raw_b_units=raw_b,
        before_live=len(before_live_set),
        after_live=len(after_live_set),
    )


def _run_fixture(rows, pair) -> CorridorCertificate:
    cnf = base.canon_cnf(rows)
    # The theorem is conditional on macro cap admission.  Use an original-state
    # anchored but generous polynomial cap to test the structural implication.
    N = max(base.input_size_units(cnf), 16)
    cap = N * N
    cert = certify(cnf, pair[0], pair[1], cap=cap)
    assert cert.macro_units <= cap
    assert cert.raw_a_units <= cert.macro_units
    assert cert.raw_b_units <= cert.after_a_units <= cert.macro_units
    assert cert.after_live <= cert.before_live - 1
    return cert


def selftest() -> None:
    # Aligned positive external incidence on both selected variables.
    c1 = _run_fixture(
        (
            (1, 2, 3),
            (1, 2, 4),
            (1, 5, 6),
            (1, 7, 8),
            (2, 9, 10),
            (2, 11, 12),
            (-3, 6, 9),
        ),
        (1, 2),
    )

    # Sign-aware corridor: selected a is negative and its external occurrences
    # must use that same negative sign.
    c2 = _run_fixture(
        (
            (-1, 2, 3),
            (-1, 2, 4),
            (-1, 5, 6),
            (-1, 7, 8),
            (2, 9, 10),
            (2, 11, 12),
            (-3, 6, 9),
        ),
        (-1, 2),
    )

    # Audit regression: exact pair clause becomes (-e), which can subsume D_A
    # and D_B.  The corrected <=macro raw bounds must still hold; -7/-10 are
    # intentionally not asserted.
    c3 = _run_fixture(
        (
            (1, 2),
            (1, 3, 4),
            (1, 5, 6),
            (2, 7, 8),
            (2, 9, 10),
            (-3, 7, 11),
        ),
        (1, 2),
    )

    # Negative control: opposite-sign external A incidence leaves the corridor.
    mixed = base.canon_cnf(
        (
            (1, 2, 3),
            (-1, 4, 5),
            (2, 6, 7),
            (-3, 5, 7),
        )
    )
    assert not is_aligned_one_sided(mixed, 1, 2)

    for c in (c1, c2, c3):
        assert c.raw_a_units <= c.macro_units
        assert c.raw_b_units <= c.after_a_units

    print("C025_V3_ALIGNED_ONE_SIDED_CORRIDOR=PASS")
    print("RAW_PRE_SUBSUMPTION_CAP_CONTRACT=PASS")
    print("EXACT_PAIR_SUBSUMPTION_REGRESSION=PASS")
    print("MIXED_SIGN_NEGATIVE_CONTROL=PASS")
    print("V3_UNIVERSAL_AVAILABILITY=OPEN")
    print("P_VS_NP=OPEN")


if __name__ == "__main__":
    selftest()
