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

LAST_BARRIER: dict | None = None


def phi_for(state: base.EngineState, cnf: base.CNF, ext_count_delta: int = 0) -> int:
    # ext_count is not used by the current frozen potential implementation, but
    # keep the parameter explicit so a future potential change cannot be hidden.
    return state.progress_phi(cnf, state.ledger.extension_count + ext_count_delta)


def diagnose(state: base.EngineState) -> dict:
    residual = state.residual
    live = set(base.vars_of(residual))
    roots = [v for v in state.root_vars if v in live]
    exts = [v for v in sorted(live) if v not in set(state.root_vars)]

    width_hist = Counter(len(c) for c in residual)
    literal_occ = Counter(l for c in residual for l in c)
    var_degree = {
        str(v): {
            "positive": literal_occ[v],
            "negative": literal_occ[-v],
            "total": literal_occ[v] + literal_occ[-v],
        }
        for v in sorted(live)
    }

    elimination = []
    for var in roots:
        out, stats = base.eliminate_var_capped(residual, var, state.state_cap)
        elimination.append({
            "var": var,
            "fits": out is not None,
            **stats,
            "canonical_units_if_fit": base.state_units(out) if out is not None else None,
        })

    pair_candidates = v2.all_or_pair_candidates(residual)
    pair_freq = Counter()
    for c in residual:
        for i in range(len(c)):
            for j in range(i + 1, len(c)):
                a, b = c[i], c[j]
                if abs(a) == abs(b):
                    continue
                pair = tuple(sorted((a, b), key=lambda z: (abs(z), z < 0)))
                pair_freq[pair] += 1

    fresh = max([*live, *state.root_vars], default=0) + 1
    under_cap = 0
    replay_ok = 0
    restores_any_root = 0
    restores_with_phi_drop = 0
    best_restores = []
    before_phi = state.progress_phi()

    for a, b in pair_candidates:
        macro, cert = v2.apply_or_pair_v2(residual, a, b, fresh)
        units = base.state_units(macro)
        if units > state.state_cap:
            continue
        under_cap += 1
        if not v2.verify_or_pair_v2(residual, macro, cert):
            continue
        replay_ok += 1
        local_restores = []
        for var in roots:
            out, stats = base.eliminate_var_capped(macro, var, state.state_cap)
            if out is None:
                continue
            after_phi = phi_for(state, out, 1)
            local_restores.append({
                "pivot": var,
                "after_phi": after_phi,
                "after_units": base.state_units(out),
                "pairs": stats.get("pairs", 0),
            })
        if local_restores:
            restores_any_root += 1
            best = min(local_restores, key=lambda row: (row["after_phi"], row["after_units"], row["pivot"]))
            best_restores.append({
                "pair": [a, b],
                "pair_frequency": pair_freq[(a, b)],
                "macro_units": units,
                **best,
            })
            if any(row["after_phi"] < before_phi for row in local_restores):
                restores_with_phi_drop += 1

    best_restores.sort(key=lambda row: (row["after_phi"], row["after_units"], row["pivot"], row["pair"]))

    return {
        "schema": "JANUS/C025/PHP54-OPEN-BARRIER/v1",
        "fingerprint": base.fingerprint(residual),
        "state_cap": state.state_cap,
        "state_units": base.state_units(residual),
        "progress_phi": before_phi,
        "clause_count": len(residual),
        "live_variable_count": len(live),
        "live_root_variables": roots,
        "live_extension_variables": exts,
        "width_histogram": {str(k): width_hist[k] for k in sorted(width_hist)},
        "variable_degree": var_degree,
        "root_elimination_attempts": elimination,
        "or_pair_search": {
            "candidate_count": len(pair_candidates),
            "frequency_histogram": dict(sorted(Counter(pair_freq.values()).items())),
            "under_cap": under_cap,
            "replay_ok": replay_ok,
            "restores_any_root": restores_any_root,
            "restores_with_phi_drop": restores_with_phi_drop,
            "best_nonprogress_restores": best_restores[:12],
        },
        "residual_cnf": [list(c) for c in residual],
        "scientific_boundary": {
            "diagnostic_only": True,
            "no_semantic_oracle": True,
            "P_VS_NP": "OPEN",
        },
    }


def capture_discovery(state: base.EngineState):
    global LAST_BARRIER
    result = ORIGINAL_DISCOVERY(state)
    if result is None:
        LAST_BARRIER = diagnose(state)
    return result


ORIGINAL_DISCOVERY = v2.discover_macro_restore_v2


def main() -> None:
    global LAST_BARRIER
    old_v2 = v2.discover_macro_restore_v2
    v2.discover_macro_restore_v2 = capture_discovery
    try:
        result = v2.solve_fail_closed_v2(pigeonhole(5, 4), cap_exponent=1, extension_exponent=1)
    finally:
        v2.discover_macro_restore_v2 = old_v2

    assert result["status"] == "OPEN"
    assert result["reason"] == "NO_CAPPED_CERTIFIED_MOVE"
    assert LAST_BARRIER is not None
    report = {
        "engine_status": result["status"],
        "engine_reason": result["reason"],
        "N": result["N"],
        "barrier": LAST_BARRIER,
        "P_VS_NP": "OPEN",
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
