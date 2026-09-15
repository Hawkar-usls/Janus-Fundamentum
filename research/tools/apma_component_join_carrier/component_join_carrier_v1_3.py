from __future__ import annotations

import json

from research.tools.apma_component_join_carrier import component_join_carrier as v1
from research.tools.apma_component_join_carrier import component_join_carrier_v1_2 as v12

ARTIFACT_ID = "JANUS-TRUMP-BICAMERAL-COMPONENT-BOUNDARY-JOIN-CARRIER-CANDIDATE-2026-09-15-v1.3"
AUTHORITY = "CANDIDATE_CONTROL_REPAIR_WRAPPER__NO_SCIENTIFIC_PROMOTION"
FROZEN_V1_CANDIDATE_BLOB = "89f5d591d4d553bb26489908a79f2c739f62b756"
FROZEN_V12_WRAPPER_BLOB = "85d8a6c826ba308f5e84dc246bdd152e2704f001"


def _embedded_or(n: int) -> list[list[int]]:
    return [list((a, b) + (a,) * (n - 2)) for a, b in [(0,1), (1,0), (1,1)]]


def _embedded_xor(n: int) -> list[list[int]]:
    return [list((a, b, c) + (a,) * (n - 3)) for a, b, c in [(0,0,0), (0,1,1), (1,0,1), (1,1,0)]]


def alpha_cycle_control_v1_3() -> dict:
    B = list(range(20))
    y12 = list(range(20,40))
    y23 = list(range(40,60))
    y31 = list(range(60,80))
    z = 80
    s1 = B + y12 + y31
    s2 = B + y12 + y23
    s3 = B + y23 + y31
    sr = B + [z]
    return {
        "variables": list(range(81)),
        "constraints": [
            {"id": "cycle_or_12_31", "scope": s1, "allowed": _embedded_or(len(s1))},
            {"id": "cycle_xor_12_23", "scope": s2, "allowed": _embedded_xor(len(s2))},
            {"id": "cycle_or_23_31", "scope": s3, "allowed": _embedded_or(len(s3))},
            {"id": "cycle_right", "scope": sr, "allowed": _embedded_or(len(sr))},
        ],
    }


def explain_overwidth_component_join(raw: dict) -> dict:
    v12.install_repair()
    return v1.explain_overwidth_component_join(raw)


def main() -> None:
    v12.install_repair()
    print(json.dumps({
        "artifact_id": ARTIFACT_ID,
        "authority": AUTHORITY,
        "repair": "ALPHA_CYCLE_RAW_CONTROL_SCOPE_ONLY",
        "frozen_v1_candidate_blob": FROZEN_V1_CANDIDATE_BLOB,
        "frozen_v1_2_wrapper_blob": FROZEN_V12_WRAPPER_BLOB,
        "positive": v1.explain_overwidth_component_join(v1.positive_multi_relation_k20()),
        "negative_empty": v1.explain_overwidth_component_join(v1.empty_conditional_join_control()),
        "negative_cycle": v1.explain_overwidth_component_join(alpha_cycle_control_v1_3()),
        "negative_no_anchor_unit": v1.no_anchor_unit_control(),
        "negative_hint": v1.explain_overwidth_component_join(v1.injected_hint_control()),
        "negative_tamper": v1.tampered_control(),
        "scientific_firewall": v1.firewall(),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
