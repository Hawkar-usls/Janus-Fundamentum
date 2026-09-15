from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

from research.tools.apma_trinity_sovereign.trinity import akinator_propose, run_trinity
from research.tools.apma_ss_provenance.apma_ss_controller import (
    encode_c023,
    reverse_c023,
    classify_source,
    run_apma_ss,
)
from research.tools.apma_interface_quotient.exact_quotient import make_affine_control
from research.tools.apma_factorized_feedback.factorized_portfolio import (
    canonical_components,
    component_obligations,
    solve_instance as solve_factorized_instance,
)
from research.tools.apma_log_alien_transfer.log_alien_transfer import (
    RELATIONS,
    connected_or2_xor_sat,
    solve_instance as solve_alien_instance,
)

ARTIFACT_ID = "JANUS-TRUMP-INVERTED-PYRAMID-ADMISSION-V2-CANDIDATE-2026-09-15-v1.0"
AUTHORITY = "ARCHITECTURAL_DIAGNOSTIC_CANDIDATE__NO_SCIENTIFIC_PROMOTION"
PREREG_REL = Path("research/TRUMP_INVERTED_PYRAMID_ADMISSION_V2_PREREGISTRATION_2026-09-15.json")
PREREG_COMMIT = "2ce2b4d62c7cb0b701197776fe1c050f5d2c8c41"
PREREG_GIT_BLOB_SHA1 = "6f25ed436f19fac2b9d77adb45e48392f41362a8"

SOURCE_GUARDS = {
    "research/tools/apma_trinity_sovereign/trinity.py": "40bfffa1d2705158b7f8b73b73bcaf3ebc616bb4",
    "research/tools/apma_ss_provenance/apma_ss_controller.py": "49b0f43c706b58939ce9df53305ce9036cb22340",
    "research/tools/apma_interface_quotient/exact_quotient.py": "cc331245bd71b6c83ab6c43b86f961fe53ed31c8",
    "research/tools/apma_factorized_feedback/factorized_portfolio.py": "ab3cd177eb1e554f5119238c8556f05feb988bb3",
    "research/tools/apma_log_alien_transfer/log_alien_transfer.py": "d20cd94fa2e0324e301f55211152c2d410099425",
}

LEGACY = "LEGACY_TRINITY_KNOWN_DOORS"
PROVENANCE = "PROVENANCE_PRESERVING_TRACTABLE_ESCAPE"
AFFINE = "AFFINE_SYNDROME_EXACT_QUOTIENT"
FACTORIZED = "FACTORIZED_FEEDBACK_PORTFOLIO"
ALIEN = "LOG_ALIEN_CONSTRAINT_EXACT_TRANSFER"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def source_guard() -> dict:
    root = repo_root()
    checks = {"prereg": git_blob_sha1(root / PREREG_REL) == PREREG_GIT_BLOB_SHA1}
    for rel, want in SOURCE_GUARDS.items():
        checks[rel] = git_blob_sha1(root / rel) == want
    prereg = json.loads((root / PREREG_REL).read_text(encoding="utf-8"))
    checks["prereg_status"] = prereg.get("status") == "FROZEN_BEFORE_CANDIDATE_IMPLEMENTATION"
    checks["prereg_artifact"] = prereg.get("artifact_id") == "JANUS-TRUMP-INVERTED-PYRAMID-ADMISSION-V2-PREREGISTRATION-2026-09-15-v1.0"
    return {"ok": all(checks.values()), "checks": checks}


def _admit_legacy(payload: dict) -> dict:
    source = tuple(tuple(int(x) for x in c) for c in payload["source"])
    n = int(payload["n"])
    proposal = akinator_propose(source, n)
    if proposal.get("door") is None:
        return {"admitted": False, "reason": "NO_LEGACY_TRINITY_DOOR", "evidence": proposal.get("evidence", {})}
    return {"admitted": True, "door": LEGACY, "proposal": proposal}


def _admit_provenance(payload: dict) -> dict:
    image = payload["image"]
    rev = reverse_c023(image)
    if rev.get("status") != "MORPH_PASS":
        return {"admitted": False, "reason": "REVERSE_MORPH_FAIL", "evidence": rev}
    kind = classify_source(rev["source"])
    if kind == "GENERAL_3CNF":
        return {"admitted": False, "reason": "REVERSED_SOURCE_NOT_TRACTABLE", "source_class": kind}
    return {"admitted": True, "door": PROVENANCE, "source_class": kind, "source_hash": rev["certificate"]["source_hash"]}


def _admit_affine(payload: dict) -> dict:
    c = payload["control"]
    conditions = {
        "wide": bool(c.get("is_wide_relative_to_prior_door")),
        "complete_queries_factor": bool(c.get("all_queries_in_rowspace")),
        "quotient_polynomial": bool(c.get("polynomial_size_control")),
        "witness_reconstructs": bool(c.get("witness_ok")),
        "omitted_observable_rejected": bool(c.get("negative_adequacy_rejected")),
        "no_raw_discovery": int(c.get("raw_assignments_enumerated_for_discovery", -1)) == 0,
    }
    if not all(conditions.values()):
        return {"admitted": False, "reason": "AFFINE_CONTRACT_INCOMPLETE", "conditions": conditions}
    return {"admitted": True, "door": AFFINE, "conditions": conditions, "rank": int(c["rank"]), "classes": int(c["syndrome_image_size"])}


def _admit_factorized(payload: dict) -> dict:
    instance = payload["instance"]
    L = int(instance["L"])
    B = sorted(set(int(v) for v in instance["B"]))
    obligations = list(instance["obligations"])
    components = canonical_components(B, obligations)
    log_budget = int(math.floor(math.log2(max(2, L))))
    carrier_plan = []
    for comp in components:
        obs = component_obligations(comp, obligations)
        kinds = {ob.get("kind") for ob in obs}
        if not obs:
            carrier = "EMPTY_COMPONENT"
        elif kinds == {"affine_eq"}:
            carrier = "SEALED_AFFINE_SYNDROME_QUOTIENT"
        elif kinds == {"raw_table"} and len(comp) <= log_budget:
            carrier = "SEALED_RAW_LOG_WIDTH_CONDITIONING"
        else:
            return {
                "admitted": False,
                "reason": "NO_COMPLETE_SEALED_CARRIER_FOR_COMPONENT",
                "component": comp,
                "kinds": sorted(str(x) for x in kinds),
                "components": components,
            }
        carrier_plan.append({"component": comp, "carrier": carrier})
    return {"admitted": True, "door": FACTORIZED, "components": components, "carrier_plan": carrier_plan}


def _admit_alien(payload: dict) -> dict:
    instance = payload["instance"]
    base_kind = str(instance["base_kind"])
    alien_kind = str(instance["alien_kind"])
    if (base_kind, alien_kind) not in {("OR2", "EVEN_XOR3"), ("EVEN_XOR3", "OR2")}:
        return {"admitted": False, "reason": "UNSUPPORTED_ALIEN_ORIENTATION"}
    if any(str(r["kind"]) != base_kind for r in instance["base_constraints"]):
        return {"admitted": False, "reason": "BASE_KIND_MISMATCH"}
    if any(str(r["kind"]) != alien_kind for r in instance["alien_constraints"]):
        return {"admitted": False, "reason": "ALIEN_KIND_MISMATCH"}
    q = len(RELATIONS[alien_kind])
    k = len(instance["alien_constraints"])
    budget = q ** k
    L = int(instance["L"])
    if budget > L:
        return {"admitted": False, "reason": "ALIEN_TUPLE_BUDGET", "q": q, "k": k, "q_pow_k": budget, "L": L}
    return {"admitted": True, "door": ALIEN, "q": q, "k": k, "q_pow_k": budget, "L": L}


def admit(case: dict) -> dict:
    surface = str(case["surface"])
    payload = case["payload"]
    if surface == "CNF_ROOT":
        return _admit_legacy(payload)
    if surface == "PROVENANCE_IMAGE":
        return _admit_provenance(payload)
    if surface == "AFFINE_CONTRACT":
        return _admit_affine(payload)
    if surface == "FEEDBACK_INTERFACE":
        return _admit_factorized(payload)
    if surface == "ALIEN_CONSTRAINT_INSTANCE":
        return _admit_alien(payload)
    return {"admitted": False, "reason": "UNKNOWN_SURFACE"}


def execute(case: dict, admission: dict) -> dict:
    if not admission.get("admitted"):
        raise AssertionError("EXECUTION_BEFORE_ADMISSION_FORBIDDEN")
    payload = case["payload"]
    door = admission["door"]
    if door == LEGACY:
        return run_trinity(tuple(tuple(int(x) for x in c) for c in payload["source"]), int(payload["n"]))
    if door == PROVENANCE:
        return run_apma_ss(payload["image"])
    if door == AFFINE:
        # The sealed affine quotient artifact is an exact carrier/adequacy object rather than a root SAT solver.
        return {"status": "ADMITTED_EXACT_AFFINE_CARRIER", "control": payload["control"]}
    if door == FACTORIZED:
        return solve_factorized_instance(payload["instance"])
    if door == ALIEN:
        return solve_alien_instance(payload["instance"])
    raise AssertionError("UNAUTHORIZED_DOOR")


def route(case: dict) -> dict:
    guard = source_guard()
    if not guard["ok"]:
        return {"status": "HALT_SOURCE_GUARD", "source_guard": guard, "metrics": {"sealed_executions": 0, "generic_transfer_calls": 0}}
    admission = admit(case)
    if not admission.get("admitted"):
        return {
            "status": "OPEN_NO_ADMITTED_EXACT_BASIS",
            "admission": admission,
            "source_guard": guard,
            "metrics": {
                "sealed_executions": 0,
                "generic_transfer_calls": 0,
                "global_variable_cube_enumeration": 0,
                "cartesian_products_materialized": 0,
            },
        }
    execution = execute(case, admission)
    metrics = {
        "sealed_executions": 1,
        "generic_transfer_calls": 0,
        "global_variable_cube_enumeration": int(execution.get("metrics", {}).get("global_variable_assignments_enumerated", 0)),
        "cartesian_products_materialized": int(execution.get("metrics", {}).get("cartesian_products_materialized", 0)),
    }
    return {"status": "ROUTED", "admission": admission, "execution": execution, "source_guard": guard, "metrics": metrics}


def legacy_2cnf_case() -> dict:
    return {"surface": "CNF_ROOT", "payload": {"n": 2, "source": [[1, 2], [-1, 2]]}}


def provenance_2cnf_case() -> dict:
    source = ((1, 2), (-1, 2))
    return {"surface": "PROVENANCE_IMAGE", "payload": {"image": encode_c023(source, 2)}}


def affine_case() -> dict:
    return {"surface": "AFFINE_CONTRACT", "payload": {"control": make_affine_control()}}


def factorized_case() -> dict:
    return {
        "surface": "FEEDBACK_INTERFACE",
        "payload": {
            "instance": {
                "L": 64,
                "B": [0, 1, 2, 3],
                "obligations": [
                    {"id": "raw01", "kind": "raw_table", "scope": [0, 1], "allowed": ["01", "10", "11"]},
                    {"id": "aff23", "kind": "affine_eq", "scope": [2, 3], "coeff": {"2": 1, "3": 1}, "rhs": 0},
                ],
            }
        },
    }


def alien_case() -> dict:
    return {"surface": "ALIEN_CONSTRAINT_INSTANCE", "payload": {"instance": connected_or2_xor_sat()}}


def alien_over_budget_case() -> dict:
    instance = connected_or2_xor_sat()
    instance = {**instance, "L": 4}
    return {"surface": "ALIEN_CONSTRAINT_INSTANCE", "payload": {"instance": instance}}


def unsupported_connected_mixed_feedback_case() -> dict:
    return {
        "surface": "FEEDBACK_INTERFACE",
        "payload": {
            "instance": {
                "L": 64,
                "B": [0, 1, 2],
                "obligations": [
                    {"id": "raw01", "kind": "raw_table", "scope": [0, 1], "allowed": ["01", "10", "11"]},
                    {"id": "aff12", "kind": "affine_eq", "scope": [1, 2], "coeff": {"1": 1, "2": 1}, "rhs": 0},
                ],
            }
        },
    }


def run_controls() -> dict:
    named = {
        "legacy_2cnf": legacy_2cnf_case(),
        "provenance_2cnf": provenance_2cnf_case(),
        "affine_wide": affine_case(),
        "factorized_feedback": factorized_case(),
        "log_alien_connected": alien_case(),
        "alien_over_budget": alien_over_budget_case(),
        "unsupported_connected_mixed_feedback": unsupported_connected_mixed_feedback_case(),
    }
    results = {name: route(case) for name, case in named.items()}
    return {
        "artifact_id": ARTIFACT_ID,
        "authority": AUTHORITY,
        "prereg_commit": PREREG_COMMIT,
        "orientation": "EXACT_ADMISSION_THEN_SEALED_EXECUTION_THEN_REPLAY_OR_OPEN",
        "results": results,
        "scientific_firewall": {
            "GENERAL_SAT_IN_P": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "GLOBAL_APMA_FRONTIER_ADVANCE": "NONE",
            "NEW_SAT_CLASS": "NOT_CLAIMED",
        },
    }


def main() -> None:
    print(json.dumps(run_controls(), sort_keys=True))


if __name__ == "__main__":
    main()
