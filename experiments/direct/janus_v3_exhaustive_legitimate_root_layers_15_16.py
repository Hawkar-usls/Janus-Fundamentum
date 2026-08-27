#!/usr/bin/env python3
"""Exhaustive frozen-v3 forward census for legitimate normalized roots N=15,16.

Reuses the audited layer enumerator/census from N13-N14. Finite exact layers
only; P_VS_NP remains OPEN.
"""
from __future__ import annotations

import json

from experiments.direct import janus_v3_exhaustive_legitimate_root_layers_13_14 as prior

TARGETS = (15, 16)
P_VS_NP = "OPEN"


def main() -> int:
    layers = [prior.census(N) for N in TARGETS]
    first_extension_layer = next((x for x in layers if x["first_extension"] is not None), None)
    first_open_layer = next((x for x in layers if x["first_open"] is not None), None)
    report = {
        "schema": "JANUS/C025/V3-EXHAUSTIVE-LEGITIMATE-ROOT-LAYERS-15-16/v1",
        "layers": layers,
        "first_extension_layer": None if first_extension_layer is None else first_extension_layer["N"],
        "first_open_layer": None if first_open_layer is None else first_open_layer["N"],
        "scientific_boundary": {
            "exhaustive_only_for_listed_finite_layers": True,
            "order_preserving_variable_renaming_only": True,
            "finite_totality_does_not_imply_asymptotic_totality": True,
            "no_open_does_not_prove_universal_availability": True,
            "heuristic_or_predictive_layer_has_theorem_authority": False,
            "P_VS_NP": P_VS_NP,
        },
    }
    report["status"] = "REACHABLE_OPEN_FOUND" if first_open_layer else ("FIRST_EXTENSION_FOUND" if first_extension_layer else "FINITE_TOTALITY_15_16_NO_EXTENSION")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
