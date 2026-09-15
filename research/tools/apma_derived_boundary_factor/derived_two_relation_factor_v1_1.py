from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research.tools.apma_derived_boundary_factor import derived_two_relation_factor as v1

ARTIFACT_ID = "JANUS-TRUMP-BICAMERAL-DERIVED-TWO-RELATION-BOUNDARY-FACTOR-CANDIDATE-2026-09-15-v1.1"
AUTHORITY = "CANDIDATE_SERIALIZATION_REPAIR_WRAPPER__NO_SCIENTIFIC_PROMOTION"
FROZEN_V1_CANDIDATE_BLOB = "1047351df47ed5f326eef2650da0c9f5ee0f2fda"
V11_PREREG = Path("research/TRUMP_BICAMERAL_DERIVED_TWO_RELATION_BOUNDARY_FACTOR_V1_1_PREREGISTRATION_2026-09-15.json")
V11_PREREG_BLOB = "b0a784b2fa1dd9380ccee7eec676bb24bf35772a"
ORIGINAL_CANONICAL_BYTES = v1.canonical_bytes


def _json_safe_keys(obj: Any) -> Any:
    if isinstance(obj, dict):
        out = {}
        for key, value in obj.items():
            if isinstance(key, tuple):
                safe_key = "__tuple_key__:" + ",".join(str(int(x)) for x in key)
            else:
                safe_key = key
            out[safe_key] = _json_safe_keys(value)
        return out
    if isinstance(obj, list):
        return [_json_safe_keys(x) for x in obj]
    if isinstance(obj, tuple):
        return [_json_safe_keys(x) for x in obj]
    return obj


def canonical_bytes_v1_1(obj: Any) -> bytes:
    return json.dumps(_json_safe_keys(obj), ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def install_repair() -> None:
    v1.canonical_bytes = canonical_bytes_v1_1


def repair_guard() -> dict:
    root = v1.root()
    prereg = root / V11_PREREG
    p = json.loads(prereg.read_text(encoding="utf-8"))
    checks = {
        "v11_prereg_blob": v1.git_blob_sha1(prereg) == V11_PREREG_BLOB,
        "v11_prereg_frozen": p.get("status") == "FROZEN_BEFORE_V1_1_REPAIR",
        "repair_class": p.get("repair_class") == "JSON_SAFE_PROVENANCE_SERIALIZATION_ONLY",
        "frozen_v1_candidate_declared": p.get("frozen_v1_candidate", {}).get("blob_sha") == FROZEN_V1_CANDIDATE_BLOB,
    }
    return {"ok": all(checks.values()), "checks": checks}


def explain(raw: dict) -> dict:
    guard = repair_guard()
    if not guard["ok"]:
        return {"artifact_id": ARTIFACT_ID, "authority": AUTHORITY, "status": "HALT_V1_1_REPAIR_GUARD", "repair_guard": guard, "scientific_firewall": v1.firewall()}
    install_repair()
    out = v1.explain(raw)
    out["v1_1_repair"] = {
        "class": "JSON_SAFE_PROVENANCE_SERIALIZATION_ONLY",
        "frozen_v1_candidate_blob": FROZEN_V1_CANDIDATE_BLOB,
        "mathematical_support_keys_unchanged_in_memory": True,
    }
    out["repair_guard"] = guard
    return out


def tampered_control() -> dict:
    install_repair()
    return v1.tampered_control()


def main() -> None:
    install_repair()
    unit_can, unit_comp, unit_cut = v1.incomplete_cover_unit_control()
    result = {
        "artifact_id": ARTIFACT_ID,
        "authority": AUTHORITY,
        "repair_guard": repair_guard(),
        "repair": "JSON_SAFE_PROVENANCE_SERIALIZATION_ONLY",
        "frozen_v1_candidate_blob": FROZEN_V1_CANDIDATE_BLOB,
        "positive": explain(v1.positive_no_anchor_k20()),
        "negative_empty": explain(v1.empty_pair_support_control()),
        "negative_three": explain(v1.three_relation_no_anchor_control()),
        "negative_incomplete_cover_unit": v1.component_support(unit_can, unit_comp, unit_cut),
        "negative_hint": explain(v1.injected_hint_control()),
        "negative_tamper": tampered_control(),
        "scientific_firewall": v1.firewall(),
    }
    print(json.dumps(_json_safe_keys(result), sort_keys=True))


if __name__ == "__main__":
    main()
