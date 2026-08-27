#!/usr/bin/env python3
"""Executable contract checks for the proved C025 v3 root-free tail progress lemma.

This is not a SAT totality test.  It only checks properties of any plan that
`discover_extension_tail_plan_v3` actually admits: root-free precondition,
two distinct pre-macro pivots, one fresh extension maximum, exact replay, and
strict live-variable descent.

P_VS_NP remains OPEN.
"""
from __future__ import annotations

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct import janus_unified_macro_restore_v3 as v3

P_VS_NP = "OPEN"


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


def verify_admitted_plan_descent(state: base.EngineState, plan: v3.MacroPlan) -> None:
    before_live = set(base.vars_of(state.residual))
    assert not (before_live & set(state.root_vars))
    assert len(plan.pivots) == 2
    assert plan.pivots[0] != plan.pivots[1]
    assert set(plan.pivots) <= before_live

    e = int(plan.macro_cert["extension"])
    assert e not in before_live
    assert e not in plan.pivots

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
    assert v3.verify_plan(state.residual, replay_plan, state.state_cap)

    after_live = set(base.vars_of(plan.after))
    assert not (set(plan.pivots) & after_live)
    assert after_live <= ((before_live - set(plan.pivots)) | {e})
    assert len(after_live) <= len(before_live) - 1
    assert state.progress_phi(plan.after, state.ledger.extension_count + 1) < state.progress_phi()


def selftest() -> None:
    fixtures = (
        ((1, 2, 3), (-1, -2, 3), (-1, 2, -3), (1, -2, -3)),
        ((1, 2, 3), (1, -2, 4), (-1, 3, 4), (-1, -3, -4), (2, -3, 4)),
    )
    admitted = 0
    for rows in fixtures:
        cnf = base.canon_cnf(rows)
        # Deliberately give the contract a generous but original-N anchored cap.
        N = max(base.input_size_units(cnf), 16)
        state = make_root_free_state(cnf, N)
        assert base.state_units(cnf) <= state.state_cap
        plan = v3.discover_extension_tail_plan_v3(state)
        if plan is None:
            continue
        admitted += 1
        verify_admitted_plan_descent(state, plan)

    assert admitted >= 1, "SELFTEST_NEEDS_AT_LEAST_ONE_ADMITTED_V3_PLAN"
    print("V3_ROOT_FREE_ADMITTED_PLAN_PROGRESS_CONTRACT=PASS")
    print("V3_SUCCESSFUL_PLAN_LIVE_DESCENT_AT_LEAST_ONE=PASS")
    print("V3_AVAILABILITY=OPEN")
    print("P_VS_NP=OPEN")


if __name__ == "__main__":
    selftest()
