#!/usr/bin/env python3
"""Exhaustive current-v3 N=20 census for one recurrence-unresolved root-var layer.

The iterated unit-free envelope theorem already certifies raw-cap ordinary
availability at N=20 for all allowed r0 except {4,5,6}.  This script exhausts
one of those three normalized legitimate root layers under the unchanged
current v3 solver and reports any actual extension use or OPEN.

A no-extension result here combines with the theorem only for the extension/cap
question; it does not by itself close unrelated software/witness-lift OPEN paths
on omitted r0 layers. P_VS_NP remains OPEN.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct import janus_unified_macro_restore_v3 as v3
from experiments.direct import janus_v3_exhaustive_legitimate_root_layers_13_14 as enum

TARGET_N = 20
ALLOWED_R = {4, 5, 6}
P_VS_NP = "OPEN"


def census(r0: int) -> dict:
    roots = enum.roots_for_layer(TARGET_N, r0)
    statuses: Counter[str] = Counter()
    reasons: Counter[str] = Counter()
    ext_hist: Counter[int] = Counter()
    first_extension = None
    first_open = None
    roots_v2 = 0
    roots_v3 = 0

    for idx, root in enumerate(roots):
        if base.input_size_units(root) != TARGET_N:
            raise AssertionError("WRONG_N_FROM_COMPLETE_ENUMERATOR")
        if len(base.vars_of(root)) != r0:
            raise AssertionError("WRONG_R_FROM_COMPLETE_ENUMERATOR")
        result = v3.solve_fail_closed_v3(root)
        statuses[result["status"]] += 1
        reasons[result["reason"]] += 1
        ext = int(result["ledger"].get("extension_count", 0))
        ext_hist[ext] += 1
        events = result.get("events", [])
        used_v2 = any(e.get("kind") == "JEC_MACRO_RESTORE_CAP" for e in events)
        used_v3 = any(e.get("kind") == "JEC_EXTENSION_TAIL_DESCENT_V3" for e in events)
        roots_v2 += int(used_v2)
        roots_v3 += int(used_v3)

        if ext > 0 and first_extension is None:
            first_extension = {
                "index": idx,
                "root": root,
                "root_fingerprint": base.fingerprint(root),
                "status": result["status"],
                "reason": result["reason"],
                "extension_count": ext,
                "used_v2": used_v2,
                "used_v3": used_v3,
                "events": events,
            }
        if result["status"] == "OPEN" and first_open is None:
            first_open = {
                "index": idx,
                "root": root,
                "root_fingerprint": base.fingerprint(root),
                "reason": result["reason"],
                "residual_fingerprint": result["residual_fingerprint"],
                "residual_units": result["residual_units"],
                "events": events,
            }

    return {
        "schema": "JANUS/C025/V3-EXHAUSTIVE-N20-RECURRENCE-UNRESOLVED-R/v1",
        "N": TARGET_N,
        "r0": r0,
        "target_clause_units": TARGET_N - r0 - 1,
        "total_roots": len(roots),
        "status_counts": dict(sorted(statuses.items())),
        "reason_counts": dict(sorted(reasons.items())),
        "extension_count_histogram": {str(k): v for k, v in sorted(ext_hist.items())},
        "roots_using_v2_macro_restore": roots_v2,
        "roots_using_v3_tail": roots_v3,
        "first_extension": first_extension,
        "first_open": first_open,
        "extension_free_for_complete_layer": first_extension is None,
        "scientific_boundary": {
            "complete_normalized_root_layer": True,
            "current_frozen_v3": True,
            "current_cap_exponent": 2,
            "N_root_anchored": True,
            "this_layer_selected_because_N20_recurrence_unresolved": True,
            "no_extension_closes_only_this_r0_layer": True,
            "no_open_here_does_not_cover_omitted_r0_software_paths": True,
            "P_VS_NP": P_VS_NP,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--r", type=int, required=True)
    args = parser.parse_args()
    if args.r not in ALLOWED_R:
        raise SystemExit("--r must be one of 4,5,6")
    print(json.dumps(census(args.r), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
