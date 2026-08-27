#!/usr/bin/env python3
"""Exhaustive frozen-v3 forward census for normalized legitimate roots N=17.

Finite exact size layer only. Reuses the complete order-preserving canonical
root enumerator from the N13-N14 census. P_VS_NP remains OPEN.
"""
from __future__ import annotations

import json

from experiments.direct import janus_v3_exhaustive_legitimate_root_layers_13_14 as prior

TARGET_N = 17
P_VS_NP = "OPEN"


def main() -> int:
    layer = prior.census(TARGET_N)
    report = {
        "schema": "JANUS/C025/V3-EXHAUSTIVE-LEGITIMATE-ROOT-LAYER-17/v1",
        "layer": layer,
        "scientific_boundary": {
            "exhaustive_only_for_N17": True,
            "order_preserving_variable_renaming_only": True,
            "finite_totality_does_not_imply_asymptotic_totality": True,
            "no_open_does_not_prove_universal_availability": True,
            "heuristic_or_predictive_layer_has_theorem_authority": False,
            "P_VS_NP": P_VS_NP,
        },
    }
    if layer["first_open"] is not None:
        report["status"] = "REACHABLE_OPEN_N17_FOUND"
    elif layer["first_extension"] is not None:
        report["status"] = "FIRST_EXTENSION_N17_FOUND"
    else:
        report["status"] = "FINITE_TOTALITY_N17_NO_EXTENSION"
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
