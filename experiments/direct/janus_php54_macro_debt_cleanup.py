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


def exact_elim(cnf: base.CNF, pivot: int, cap: int):
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
    start = state.residual
    old_vars = tuple(base.vars_of(start))
    cap = state.state_cap
    start_phi = state.progress_phi()
    fresh1 = max([*old_vars, *state.root_vars], default=0) + 1

    stage2_states = 0
    cleanup_attempts = 0
    cleanup_fits = 0
    strict_drop = []
    cleanup_by_target = {"fresh1": 0, "fresh2": 0}

    for a1, b1 in v2.all_or_pair_candidates(start):
        m1, c1 = v2.apply_or_pair_v2(start, a1, b1, fresh1)
        if base.state_units(m1) > cap:
            continue
        assert v2.verify_or_pair_v2(start, m1, c1)

        for p1 in old_vars:
            s1, st1 = exact_elim(m1, p1, cap)
            if s1 is None:
                continue
            fresh2 = max([*base.vars_of(s1), *state.root_vars], default=0) + 1

            for a2, b2 in v2.all_or_pair_candidates(s1):
                m2, c2 = v2.apply_or_pair_v2(s1, a2, b2, fresh2)
                if base.state_units(m2) > cap:
                    continue
                assert v2.verify_or_pair_v2(s1, m2, c2)

                for p2 in old_vars:
                    if p2 == p1 or p2 not in set(base.vars_of(m2)):
                        continue
                    s2, st2 = exact_elim(m2, p2, cap)
                    if s2 is None:
                        continue
                    stage2_states += 1

                    # Debt-retirement gate: try to existentially eliminate one of
                    # the two fresh B2 variables created by this atomic staircase.
                    for label, debt in (("fresh1", fresh1), ("fresh2", fresh2)):
                        if debt not in set(base.vars_of(s2)):
                            # Already syntactically dead: canonicalization itself
                            # retired the debt, which is even stronger than elim.
                            phi = state.progress_phi(s2, state.ledger.extension_count + 2)
                            if phi < start_phi:
                                strict_drop.append({
                                    "mode": "SYNTACTIC_DEAD",
                                    "target": label,
                                    "debt_var": debt,
                                    "phi": phi,
                                    "units": base.state_units(s2),
                                    "plan": [a1,b1,p1,a2,b2,p2],
                                })
                            continue

                        cleanup_attempts += 1
                        cleaned, stc = exact_elim(s2, debt, cap)
                        if cleaned is None:
                            continue
                        cleanup_fits += 1
                        cleanup_by_target[label] += 1
                        phi = state.progress_phi(cleaned, state.ledger.extension_count + 2)
                        if phi < start_phi:
                            strict_drop.append({
                                "mode": "EXACT_EXISTENTIAL_CLEANUP",
                                "target": label,
                                "debt_var": debt,
                                "phi": phi,
                                "units": base.state_units(cleaned),
                                "cleanup_pairs": int(stc.get("pairs", 0)),
                                "plan": [a1,b1,p1,a2,b2,p2],
                            })

    strict_drop.sort(key=lambda x: (x["phi"], x["units"], x["cleanup_pairs"] if "cleanup_pairs" in x else -1, x["plan"]))
    report = {
        "schema": "JANUS/C025/PHP54-MACRO-DEBT-CLEANUP/v1",
        "P_VS_NP": "OPEN",
        "fingerprint": base.fingerprint(start),
        "state_cap": cap,
        "start_phi": start_phi,
        "stage2_states": stage2_states,
        "cleanup_attempts": cleanup_attempts,
        "cleanup_fits": cleanup_fits,
        "cleanup_by_target": cleanup_by_target,
        "strict_phi_drop_plans": len(strict_drop),
        "best_strict_drop": strict_drop[:16],
        "interpretation_gate": {
            "if_strict_drop_positive": "PAIR-MACRO STAIRCASE HAS RETIRABLE EXTENSION DEBT; IMPLEMENT FIXED PROOF-CARRYING CLEANUP BLOCK",
            "if_cleanup_positive_no_drop": "CLEANUP FITS BUT DOES NOT RETIRE NET LIVE STATE; REAUDIT POTENTIAL/DEFINITION CLOSURE",
            "if_cleanup_zero": "PAIR-MACRO STAIRCASE ACCUMULATES NON-RETIRABLE EXTENSION DEBT UNDER C=1; STRUCTURED MULTI-LITERAL MACRO IS THE LOCAL WALL",
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
