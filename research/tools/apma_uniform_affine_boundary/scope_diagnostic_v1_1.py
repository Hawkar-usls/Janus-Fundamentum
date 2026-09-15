from __future__ import annotations

import hashlib
import json
from pathlib import Path

from research.tools.apma_unseen_basis.raw_relation_basis import canonicalize_raw
from research.tools.apma_unseen_basis.compositional_basis import induce_compositional_basis
from research.tools.apma_bicameral_mincut import mincut_logwidth_explainer as parent_mincut
from research.tools.apma_derived_boundary_factor import derived_two_relation_factor_v1_1 as pair_gate
from research.tools.apma_uniform_affine_boundary import uniform_affine_boundary as frozen_v1

ARTIFACT_ID = "JANUS-TRUMP-BICAMERAL-UNIFORM-RAW-DERIVED-AFFINE-BOUNDARY-SCOPE-DIAGNOSTIC-2026-09-15-v1.1"
AUTHORITY = "DIAGNOSTIC_ONLY__NO_THEOREM_PROMOTION"
PREREG = Path("research/TRUMP_BICAMERAL_UNIFORM_RAW_DERIVED_AFFINE_BOUNDARY_DIAGNOSTIC_V1_1_PREREGISTRATION_2026-09-15.json")
FROZEN_CANDIDATE = Path("research/tools/apma_uniform_affine_boundary/uniform_affine_boundary.py")
FROZEN_CANDIDATE_BLOB = "336c58c059fecba49c7fbfba9018a95761f8fc24"
FIRST_FAILURE = Path("research/TRUMP_BICAMERAL_UNIFORM_RAW_DERIVED_AFFINE_BOUNDARY_FACTOR_FIRST_RUN_FAILURE_2026-09-15.json")


def root() -> Path:
    return Path(__file__).resolve().parents[3]


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def main() -> None:
    r = root()
    prereg = json.loads((r / PREREG).read_text(encoding="utf-8"))
    failure = json.loads((r / FIRST_FAILURE).read_text(encoding="utf-8"))
    source_checks = {
        "diagnostic_prereg_frozen": prereg.get("status") == "FROZEN_DIAGNOSTIC_ONLY_BEFORE_RUN",
        "frozen_candidate_blob_unchanged": git_blob_sha1(r / FROZEN_CANDIDATE) == FROZEN_CANDIDATE_BLOB,
        "first_failure_preserved": failure.get("actions_run") == 34920916569 and failure.get("candidate_blob") == FROZEN_CANDIDATE_BLOB,
    }

    raw = frozen_v1.positive_affine_k20()
    canonical = canonicalize_raw(raw)
    global_basis = induce_compositional_basis(canonical)
    parent = parent_mincut.explain_with_mincut(raw)
    predecessor = pair_gate.explain(raw)
    affine_certs = [frozen_v1.relation_affine_certificate(rel) for rel in canonical["constraints"]]

    parent_status = parent.get("status")
    global_status = global_basis.get("status")
    has_cut = isinstance(parent.get("cut"), dict) and bool(parent.get("cut", {}).get("cut_variables"))
    all_affine = all(c.get("affine") is True for c in affine_certs)

    if global_status == "ADMIT_COMPOSITIONAL_BASIS_PORTFOLIO" and parent_status == "OUT_OF_SCOPE_GLOBAL_OR_DISCONNECTED_BASIS_ALREADY_EXISTS" and not has_cut:
        classification = "SUPERSEDED_ROUTE__ALL_AFFINE_3PLUS_CASE_ALREADY_CLOSED_BY_EARLIER_RAW_BASIS_LAYER__DO_NOT_REPAIR_UNIFORM_AFFINE_GATE"
    elif parent_status == "OPEN_MINCUT_BRANCH_BUDGET" and has_cut:
        classification = "CONTROL_BUG_ONLY__A_SEPARATE_REPAIR_PREREG_MAY_BE_OPENED"
    else:
        classification = "DIAGNOSTIC_INCONCLUSIVE__REMAIN_OPEN"

    checks = {
        **source_checks,
        "positive_all_raw_relations_affine": all_affine,
        "global_basis_status_observed": isinstance(global_status, str),
        "parent_status_observed": isinstance(parent_status, str),
        "predecessor_status_observed": isinstance(predecessor.get("status"), str),
        "classification_matches_frozen_rule": classification in set(prereg.get("classification_rule", {}).values()),
        "firewall_p_vs_np_open": frozen_v1.firewall().get("P_VS_NP") == "OPEN",
        "firewall_general_sat_not_proved": frozen_v1.firewall().get("GENERAL_SAT_IN_P") == "NOT_PROVED",
    }
    out = {
        "artifact_id": ARTIFACT_ID,
        "authority": AUTHORITY,
        "checks": checks,
        "positive": {
            "all_raw_relations_affine": all_affine,
            "relation_affine_reasons": [c.get("reason") for c in affine_certs],
            "global_basis_status": global_status,
            "global_basis_component_count": len(global_basis.get("components", [])) if isinstance(global_basis, dict) else None,
            "parent_mincut_status": parent_status,
            "parent_has_cut_receipt": has_cut,
            "parent_pair_status": parent.get("parent_pair_status"),
            "predecessor_two_relation_status": predecessor.get("status"),
        },
        "classification": classification,
        "scientific_firewall": {
            "P_VS_NP": "OPEN",
            "GENERAL_SAT_IN_P": "NOT_PROVED",
            "GLOBAL_APMA_FRONTIER_ADVANCE": "NONE",
        },
    }
    print(json.dumps(out, sort_keys=True))
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
