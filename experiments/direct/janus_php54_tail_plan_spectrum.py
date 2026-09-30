#!/usr/bin/env python3
from __future__ import annotations

from collections import Counter
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
    residual = state.residual
    live = tuple(base.vars_of(residual))
    fresh = max([*live, *state.root_vars], default=0) + 1

    macro_count = 0
    macro_under_cap = 0
    first_attempts = first_fits = 0
    second_attempts = second_fits = 0
    first_fit_units = []
    second_fit_units = []
    first_fit_pairs = Counter()
    second_fit_pairs = Counter()
    best_first = []
    best_second = []

    for a, b in v2.all_or_pair_candidates(residual):
        macro_count += 1
        macro, cert = v2.apply_or_pair_v2(residual, a, b, fresh)
        if base.state_units(macro) > state.state_cap:
            continue
        assert v2.verify_or_pair_v2(residual, macro, cert)
        macro_under_cap += 1
        for p1 in live:
            first_attempts += 1
            out1, s1 = base.eliminate_var_capped(macro, p1, state.state_cap)
            if out1 is None:
                continue
            first_fits += 1
            u1 = base.state_units(out1)
            first_fit_units.append(u1)
            first_fit_pairs[(a, b)] += 1
            best_first.append((u1, a, b, p1, int(s1.get("pairs", 0))))
            live1 = set(base.vars_of(out1))
            for p2 in live:
                if p2 == p1 or p2 not in live1:
                    continue
                second_attempts += 1
                out2, s2 = base.eliminate_var_capped(out1, p2, state.state_cap)
                if out2 is None:
                    continue
                second_fits += 1
                u2 = base.state_units(out2)
                second_fit_units.append(u2)
                second_fit_pairs[(a, b)] += 1
                best_second.append((u2, a, b, p1, p2, int(s1.get("pairs", 0)), int(s2.get("pairs", 0))))

    best_first.sort()
    best_second.sort()
    report = {
        "schema": "JANUS/C025/PHP54-TAIL-PLAN-SPECTRUM/v1",
        "P_VS_NP": "OPEN",
        "fingerprint": base.fingerprint(residual),
        "state_cap": state.state_cap,
        "state_units": base.state_units(residual),
        "progress_phi": state.progress_phi(),
        "live_extensions": list(live),
        "macro_candidates": macro_count,
        "macro_under_cap": macro_under_cap,
        "first_elimination": {
            "attempts": first_attempts,
            "fits": first_fits,
            "min_units": min(first_fit_units) if first_fit_units else None,
            "max_units": max(first_fit_units) if first_fit_units else None,
            "macro_pairs_with_a_fit": len(first_fit_pairs),
            "best": [list(x) for x in best_first[:12]],
        },
        "second_elimination": {
            "attempts_after_first_fit": second_attempts,
            "fits": second_fits,
            "min_units": min(second_fit_units) if second_fit_units else None,
            "max_units": max(second_fit_units) if second_fit_units else None,
            "macro_pairs_with_a_fit": len(second_fit_pairs),
            "best": [list(x) for x in best_second[:12]],
        },
        "interpretation_gate": {
            "if_first_fits_zero": "PAIR_MACRO_CANNOT_EVEN_RESTORE_ONE_CAPPED_EXTENSION_ELIMINATION; DEPTH_IS_NOT_THE_CURRENT_BLOCKER",
            "if_first_positive_second_zero": "PAIR_MACRO_RESTORES_ONE_EXTENSION_ELIMINATION_BUT_NOT_TWO; FIXED_DEPTH_OR_MACRO_GRAMMAR_REMAINS_OPEN",
            "if_second_positive": "A_TWO_STEP_PLAN_EXISTS_AND_V3_IMPLEMENTATION_MUST_BE_REAUDITED",
        },
        "scientific_boundary": {
            "diagnostic_only": True,
            "heuristic_promotion": False,
            "P_VS_NP": "OPEN",
        },
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
