#!/usr/bin/env python3
"""Current frozen-v3 N^2 selector-product tower scout.

Reuses only the pure CNF generator from the historical selector-product hostile
probe.  Unlike that historical experiment, every generated legitimate root is
sent directly to `janus_unified_macro_restore_v3.solve_fail_closed_v3` with its
current default cap_exponent=2 and original root-anchored N.

This is a deterministic finite scout, not a totality proof.  Its purpose is to
find an honest upper bound on the first legitimate current-v3 extension use or
reachable OPEN.  Absence of either through the executed depths proves nothing
beyond those specimens. P_VS_NP remains OPEN.
"""
from __future__ import annotations

import json

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct import janus_unified_macro_restore_v3 as v3
from experiments.direct import janus_selector_product_tower_hostile_probe as tower

P_VS_NP = "OPEN"
MAX_DEPTH = 3


def count_kind(events: list[dict], kind: str) -> int:
    return sum(1 for event in events if event.get("kind") == kind)


def row_for_depth(depth: int) -> dict:
    root = tower.build_tree(depth)
    N = base.input_size_units(root)
    result = v3.solve_fail_closed_v3(root)
    events = result.get("events", [])
    ext = int(result["ledger"].get("extension_count", 0))
    return {
        "depth": depth,
        "leaf_count": 1 << depth,
        "root_fingerprint": base.fingerprint(root),
        "root_variables": len(base.vars_of(root)),
        "root_clauses": len(root),
        "root_state_units": base.state_units(root),
        "N": int(result["N"]),
        "expected_N": N,
        "state_cap": int(result["state_cap"]),
        "cap_exponent": 2,
        "status": result["status"],
        "reason": result["reason"],
        "residual_fingerprint": result["residual_fingerprint"],
        "residual_units": int(result["residual_units"]),
        "max_state_units": int(result["ledger"]["max_state_units"]),
        "ordinary_elimination_events": count_kind(events, "AKINATOR_EXACT_ELIMINATION"),
        "v2_macro_rescue_events": count_kind(events, "JEC_MACRO_RESTORE_CAP"),
        "v3_tail_rescue_events": count_kind(events, "JEC_EXTENSION_TAIL_DESCENT_V3"),
        "extension_count": ext,
        "missing_bridge": result.get("missing_bridge"),
        "first_extension_event": next(
            (e for e in events if e.get("kind") in {"JEC_MACRO_RESTORE_CAP", "JEC_EXTENSION_TAIL_DESCENT_V3"}),
            None,
        ),
        "scientific_note": "Known K5-leaf UNSAT structure is generator metadata only; frozen v3 receives only the CNF.",
    }


def main() -> int:
    rows = []
    first_extension = None
    first_open = None
    for depth in range(1, MAX_DEPTH + 1):
        row = row_for_depth(depth)
        if row["N"] != row["expected_N"]:
            raise AssertionError("ROOT_N_REBASE_OR_DRIFT")
        if row["state_cap"] != row["N"] ** 2:
            raise AssertionError("CURRENT_N2_CAP_CONTRACT_FAILED")
        rows.append(row)
        if row["extension_count"] > 0 and first_extension is None:
            first_extension = dict(row)
        if row["status"] == "OPEN":
            first_open = dict(row)
        if first_extension is not None or first_open is not None:
            break

    report = {
        "schema": "JANUS/C025/CURRENT-V3-N2-SELECTOR-TOWER-SCOUT/v1",
        "solver": "janus_unified_macro_restore_v3.solve_fail_closed_v3",
        "rows": rows,
        "first_extension": first_extension,
        "first_open": first_open,
        "status": (
            "REACHABLE_OPEN_FOUND" if first_open is not None
            else "CURRENT_V3_EXTENSION_FOUND" if first_extension is not None
            else "NO_EXTENSION_OR_OPEN_THROUGH_EXECUTED_DEPTHS"
        ),
        "scientific_boundary": {
            "legitimate_root_N_recomputed_from_root": True,
            "root_anchored_N_not_rebased": True,
            "current_default_cap_exponent": 2,
            "historical_v0_4_decision_core_not_used": True,
            "finite_structured_scout_only": True,
            "no_extension_is_not_universal_proof": True,
            "found_extension_is_only_an_upper_bound_on_first_extension_size": True,
            "found_open_refutes_only_current_frozen_v3_totality": True,
            "P_VS_NP": P_VS_NP,
        },
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
