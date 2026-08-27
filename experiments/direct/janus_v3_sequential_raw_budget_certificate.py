#!/usr/bin/env python3
"""Executable certificate for C025 v3 sequential raw-budget rescue corridor.

This composes the generic pre-subsumption raw upper bound with the frozen v3
B2-macro/two-old-pivot transition.  It is a sufficient corridor checker, not a
replacement solver and not a totality proof.
"""
from __future__ import annotations

from dataclasses import dataclass

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct import janus_unified_macro_restore_v2 as v2
from experiments.direct import janus_unified_macro_restore_v3 as v3
from experiments.direct import janus_generic_raw_elimination_budget_certificate as rawcert
from experiments.direct import janus_v3_aligned_one_sided_external_incidence_certificate as aligned

P_VS_NP = "OPEN"


@dataclass(frozen=True)
class SequentialCertificate:
    pair: tuple[int, int]
    pivots: tuple[int, int]
    extension: int
    before_units: int
    macro_units: int
    first_bound: int
    first_actual_raw: int
    after_first_units: int
    second_bound: int
    second_actual_raw: int
    after_second_units: int
    before_live: int
    after_live: int


def certify_pair_order(
    cnf: base.CNF,
    pair: tuple[int, int],
    pivots: tuple[int, int],
    *,
    cap: int,
) -> SequentialCertificate:
    a, b = pair
    x, y = pivots
    V0 = set(base.vars_of(cnf))
    if abs(a) == abs(b) or not any(a in c and b in c for c in cnf):
        raise ValueError("PAIR_NOT_A_FROZEN_V3_MACRO_CANDIDATE")
    if x == y or x not in V0 or y not in V0:
        raise ValueError("PIVOTS_MUST_BE_DISTINCT_PRE_MACRO_LIVE_VARIABLES")

    e = max(V0, default=0) + 1
    macro, macro_cert = v2.apply_or_pair_v2(cnf, a, b, e)
    if not v2.verify_or_pair_v2(cnf, macro, macro_cert):
        raise AssertionError("B2_MACRO_REPLAY_FAILED")
    macro_units = base.state_units(macro)
    if macro_units > cap:
        raise ValueError("MACRO_EXCEEDS_CAP")

    B1 = rawcert.raw_budget(macro, x)
    if B1.bound > cap:
        raise ValueError("FIRST_GENERIC_RAW_BUDGET_NOT_CERTIFIED")
    after1, stats1 = base.eliminate_var_capped(macro, x, cap)
    if after1 is None:
        raise AssertionError("FIRST_ELIMINATION_ABORTED_DESPITE_CERTIFICATE")
    if int(stats1["raw_units"]) > B1.bound:
        raise AssertionError("FIRST_ACTUAL_RAW_EXCEEDS_GENERIC_BOUND")
    if not base.verify_elimination_transition(macro, x, after1, cap):
        raise AssertionError("FIRST_ELIMINATION_REPLAY_FAILED")

    if y not in set(base.vars_of(after1)):
        raise ValueError("SECOND_OLD_PIVOT_NOT_LIVE_AFTER_FIRST_ELIMINATION")

    B2 = rawcert.raw_budget(after1, y)
    if B2.bound > cap:
        raise ValueError("SECOND_GENERIC_RAW_BUDGET_NOT_CERTIFIED")
    after2, stats2 = base.eliminate_var_capped(after1, y, cap)
    if after2 is None:
        raise AssertionError("SECOND_ELIMINATION_ABORTED_DESPITE_CERTIFICATE")
    if int(stats2["raw_units"]) > B2.bound:
        raise AssertionError("SECOND_ACTUAL_RAW_EXCEEDS_GENERIC_BOUND")
    if not base.verify_elimination_transition(after1, y, after2, cap):
        raise AssertionError("SECOND_ELIMINATION_REPLAY_FAILED")

    V2 = set(base.vars_of(after2))
    if x in V2 or y in V2:
        raise AssertionError("ELIMINATED_OLD_PIVOT_SURVIVED")
    if not V2 <= ((V0 - {x, y}) | {e}):
        raise AssertionError("UNEXPECTED_NEW_SEMANTIC_VARIABLE")
    if len(V2) > len(V0) - 1:
        raise AssertionError("ROOT_FREE_PROGRESS_NOT_STRICT")

    return SequentialCertificate(
        pair=pair,
        pivots=pivots,
        extension=e,
        before_units=base.state_units(cnf),
        macro_units=macro_units,
        first_bound=B1.bound,
        first_actual_raw=int(stats1["raw_units"]),
        after_first_units=base.state_units(after1),
        second_bound=B2.bound,
        second_actual_raw=int(stats2["raw_units"]),
        after_second_units=base.state_units(after2),
        before_live=len(V0),
        after_live=len(V2),
    )


def make_root_free_state(cnf: base.CNF, N: int) -> base.EngineState:
    return base.EngineState(
        root=cnf,
        residual=cnf,
        fixed_assignment={},
        root_vars=(),
        extension_defs=[],
        elimination_history=[],
        seen=set(),
        N=N,
        cap_exponent=2,
        extension_exponent=1,
        ledger=base.Ledger(),
    )


def assert_frozen_v3_discovers_some_plan(cnf: base.CNF, N: int) -> None:
    state = make_root_free_state(cnf, N)
    plan = v3.discover_extension_tail_plan_v3(state)
    if plan is None:
        raise AssertionError("FROZEN_V3_FAILED_TO_DISCOVER_EXISTING_CERTIFIED_CORRIDOR_PLAN")

    replay_cert = dict(plan.macro_cert)
    replay_cert["kind"] = "B2_OR_PAIR_MACRO_EXHAUSTIVE_V2"
    replay_plan = v3.MacroPlan(
        plan.macro_cnf,
        replay_cert,
        plan.pivots,
        plan.before_each_elim,
        plan.after_each_elim,
        plan.elim_stats,
        plan.kind,
    )
    if not v3.verify_plan(cnf, replay_plan, state.state_cap):
        raise AssertionError("FROZEN_V3_DISCOVERED_PLAN_REPLAY_FAILED")


def find_certified_order(cnf: base.CNF, pair: tuple[int, int], cap: int) -> SequentialCertificate:
    V0 = base.vars_of(cnf)
    last = None
    for x in V0:
        for y in V0:
            if x == y:
                continue
            try:
                return certify_pair_order(cnf, pair, (x, y), cap=cap)
            except ValueError as exc:
                last = exc
                continue
    raise ValueError(f"NO_SEQUENTIAL_CERTIFIED_ORDER: {last}")


def selftest() -> None:
    # Explicitly mixed-sign external incidence around both selected variables.
    # This is outside the aligned-one-sided theorem but inside the new generic
    # sequential budget corridor under a generous original-N anchored N^2 cap.
    mixed = base.canon_cnf(
        (
            (1, 2, 3),
            (1, 2, 4),
            (-1, 5, 6),
            (1, 7, 8),
            (-2, 9, 10),
            (2, 11, 12),
            (-3, 5, 9),
            (4, -6, 11),
        )
    )
    assert not aligned.is_aligned_one_sided(mixed, 1, 2)
    N = max(base.input_size_units(mixed), 16)
    cap = N * N
    cert = find_certified_order(mixed, (1, 2), cap)
    assert cert.first_bound <= cap
    assert cert.second_bound <= cap
    assert cert.first_actual_raw <= cert.first_bound
    assert cert.second_actual_raw <= cert.second_bound
    assert cert.after_live <= cert.before_live - 1
    assert_frozen_v3_discovers_some_plan(mixed, N)

    # Sign-aware mixed external incidence with a negative selected literal.
    mixed_signaware = base.canon_cnf(
        (
            (-1, 2, 3),
            (-1, 2, 4),
            (1, 5, 6),       # opposite to selected -1: deliberately mixed
            (-1, 7, 8),
            (-2, 9, 10),     # opposite to selected +2: deliberately mixed
            (2, 11, 12),
            (-3, 5, 9),
        )
    )
    assert not aligned.is_aligned_one_sided(mixed_signaware, -1, 2)
    N2 = max(base.input_size_units(mixed_signaware), 16)
    cert2 = find_certified_order(mixed_signaware, (-1, 2), N2 * N2)
    assert cert2.after_live <= cert2.before_live - 1
    assert_frozen_v3_discovers_some_plan(mixed_signaware, N2)

    print("V3_SEQUENTIAL_GENERIC_RAW_BUDGET_CORRIDOR=PASS")
    print("MIXED_SIGN_INSTANCE_OUTSIDE_ALIGNED_CORRIDOR=PASS")
    print("FROZEN_V3_DISCOVERY_REPLAY=PASS")
    print("ALL_CANDIDATE_SEQUENTIAL_BUDGET_FAILURE=OPEN")
    print("V3_UNIVERSAL_AVAILABILITY=OPEN")
    print("P_VS_NP=OPEN")


if __name__ == "__main__":
    selftest()
