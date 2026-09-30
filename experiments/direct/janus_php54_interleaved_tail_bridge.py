#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct import janus_unified_macro_restore_v2 as v2
from experiments.direct.janus_php54_macro_restore_attack import pigeonhole

CAPTURED: base.EngineState | None = None
ORIGINAL = v2.discover_macro_restore_v2


def capture(state: base.EngineState):
    global CAPTURED
    out = ORIGINAL(state)
    if out is None and not any(v in set(state.root_vars) for v in base.vars_of(state.residual)):
        CAPTURED = state
    return out


def elim(cnf: base.CNF, pivot: int, cap: int):
    out, stats = base.eliminate_var_capped(cnf, pivot, cap)
    if out is None:
        return None, stats
    assert base.verify_elimination_transition(cnf, pivot, out, cap)
    return out, stats


def main() -> None:
    global CAPTURED
    old = v2.discover_macro_restore_v2
    v2.discover_macro_restore_v2 = capture
    try:
        r = v2.solve_fail_closed_v2(pigeonhole(5, 4), cap_exponent=1, extension_exponent=1)
    finally:
        v2.discover_macro_restore_v2 = old
    assert r["status"] == "OPEN" and CAPTURED is not None

    state = CAPTURED
    root_tail = state.residual
    old_vars = tuple(base.vars_of(root_tail))
    old_set = set(old_vars)
    cap = state.state_cap
    start_phi = state.progress_phi()

    stage1_macro = stage1_fit = 0
    stage2_macro = stage2_fit = 0
    stage3_fit = 0
    stage2_best = []
    complete = []

    fresh1 = max([*old_vars, *state.root_vars], default=0) + 1

    for a1, b1 in v2.all_or_pair_candidates(root_tail):
        m1, c1 = v2.apply_or_pair_v2(root_tail, a1, b1, fresh1)
        if base.state_units(m1) > cap:
            continue
        assert v2.verify_or_pair_v2(root_tail, m1, c1)
        stage1_macro += 1

        for p1 in old_vars:
            s1, st1 = elim(m1, p1, cap)
            if s1 is None:
                continue
            stage1_fit += 1

            live1 = tuple(base.vars_of(s1))
            fresh2 = max([*live1, *state.root_vars], default=0) + 1
            # The second macro is again canonical/exhaustive over the CURRENT state.
            for a2, b2 in v2.all_or_pair_candidates(s1):
                m2, c2 = v2.apply_or_pair_v2(s1, a2, b2, fresh2)
                if base.state_units(m2) > cap:
                    continue
                assert v2.verify_or_pair_v2(s1, m2, c2)
                stage2_macro += 1

                # Only eliminate variables that belonged to the frozen extension tail;
                # neither fresh macro variable is used as a descent pivot.
                for p2 in old_vars:
                    if p2 == p1 or p2 not in set(base.vars_of(m2)):
                        continue
                    s2, st2 = elim(m2, p2, cap)
                    if s2 is None:
                        continue
                    stage2_fit += 1
                    stage2_best.append((base.state_units(s2), a1, b1, p1, a2, b2, p2, int(st1.get("pairs",0)), int(st2.get("pairs",0))))

                    # Net live-variable count is still a plateau after M1,E1,M2,E2.
                    # Test one ordinary old-extension elimination.  If it fits, the
                    # fixed atomic pattern M-E-M-E-E has net -1 live variable and
                    # therefore strictly decreases Phi when r=0.
                    for p3 in old_vars:
                        if p3 in (p1, p2) or p3 not in set(base.vars_of(s2)):
                            continue
                        s3, st3 = elim(s2, p3, cap)
                        if s3 is None:
                            continue
                        stage3_fit += 1
                        final_phi = state.progress_phi(s3, state.ledger.extension_count + 2)
                        row = (
                            final_phi,
                            base.state_units(s3),
                            a1,b1,p1,a2,b2,p2,p3,
                            int(st1.get("pairs",0)),int(st2.get("pairs",0)),int(st3.get("pairs",0)),
                        )
                        if final_phi < start_phi:
                            complete.append(row)

    stage2_best.sort()
    complete.sort()
    report = {
        "schema": "JANUS/C025/PHP54-INTERLEAVED-TAIL-BRIDGE/v1",
        "P_VS_NP": "OPEN",
        "fingerprint": base.fingerprint(root_tail),
        "state_cap": cap,
        "state_units": base.state_units(root_tail),
        "start_phi": start_phi,
        "pattern": "M1 -> E1 -> M2 -> E2 -> E3",
        "fixed_macro_count": 2,
        "fixed_elimination_count": 3,
        "stage1": {
            "macros_under_cap": stage1_macro,
            "elimination_fits": stage1_fit,
        },
        "stage2": {
            "macros_under_cap_after_first_fit": stage2_macro,
            "second_elimination_fits": stage2_fit,
            "best": [list(x) for x in stage2_best[:12]],
        },
        "stage3": {
            "third_elimination_fits": stage3_fit,
            "strict_phi_drop_plans": len(complete),
            "best_complete": [list(x) for x in complete[:12]],
        },
        "interpretation_gate": {
            "if_stage2_fit_zero": "A_SECOND_PAIR_MACRO_STILL_CANNOT_BRIDGE_THE_SECOND_EXTENSION_ELIMINATION; PAIR_MACRO_GRAMMAR_IS_THE_LOCAL WALL",
            "if_stage2_positive_stage3_zero": "INTERLEAVING_OPENS_TWO_STEPS_BUT_NOT_A_NET-PROGRESS_ATOMIC_BLOCK; COMPOSITION_DEPTH_OR_GRAMMAR_REMAINS_OPEN",
            "if_complete_positive": "A_FIXED_PROOF_CARRYING_TWO-MACRO_THREE-ELIM_PROGRESS_PLAN_EXISTS; IMPLEMENT_V4_AND_RUN FULL REGRESSION",
        },
        "scientific_boundary": {
            "diagnostic_only": True,
            "heuristic_promotion": False,
            "unbounded_backtracking": False,
            "general_sat_oracle": False,
            "finite_attack_only": True,
            "P_VS_NP": "OPEN",
        },
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
