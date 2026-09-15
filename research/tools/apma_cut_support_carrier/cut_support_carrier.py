from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path
from typing import Any

from research.tools.apma_unseen_basis.raw_relation_basis import canonicalize_raw, RawBasisInputError
from research.tools.apma_bicameral_mincut import mincut_logwidth_explainer as parent_mincut

ARTIFACT_ID = "JANUS-TRUMP-BICAMERAL-CUT-SUPPORT-CARRIER-CANDIDATE-2026-09-15-v1.0"
AUTHORITY = "CANDIDATE_IMPLEMENTATION__NO_SCIENTIFIC_PROMOTION"
PREREG = Path("research/TRUMP_BICAMERAL_CUT_SUPPORT_CARRIER_PREREGISTRATION_2026-09-15.json")
PREREG_BLOB = "b4eaaf90fe45b2c45867114928e93726132ebaf5"
PARENT_STATE = Path("registry/TRUMP_CURRENT_STATE_2026-09-15_v2.7.json")
PARENT_STATE_BLOB = "deb9b4b1d32b7dba24b945d80ef933f10044de2a"
PARENT_MINCUT = Path("research/tools/apma_bicameral_mincut/mincut_logwidth_explainer.py")
PARENT_MINCUT_BLOB = "c0c612676e39241b95026c15823e7af6b3da8f0d"
OLD_QUOTIENT = Path("research/tools/apma_interface_quotient/exact_quotient.py")
OLD_QUOTIENT_BLOB = "cc331245bd71b6c83ab6c43b86f961fe53ed31c8"
OLD_QUOTIENT_CHECKER = Path("research/tools/apma_interface_quotient/independent_checker.py")
OLD_QUOTIENT_CHECKER_BLOB = "fb5fe1773bbc5cc91a78e13eb1129449b84d3820"


def root() -> Path:
    return Path(__file__).resolve().parents[3]


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def canonical_bytes(obj: Any) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_obj(obj: Any) -> str:
    return hashlib.sha256(canonical_bytes(obj)).hexdigest()


def source_guard() -> dict:
    r = root()
    prereg = json.loads((r / PREREG).read_text(encoding="utf-8"))
    checks = {
        "prereg_blob": git_blob_sha1(r / PREREG) == PREREG_BLOB,
        "prereg_frozen": prereg.get("status") == "FROZEN_BEFORE_CANDIDATE_IMPLEMENTATION",
        "prereg_gate": prereg.get("frozen_gate") == "TRUMP_BICAMERAL_MINCUT_EFFECTIVE_QUOTIENT_RANK_EXPLANATION_FALSIFIER_GATE__CUT_SUPPORT_INTERSECTION_FIRST",
        "parent_state_blob": git_blob_sha1(r / PARENT_STATE) == PARENT_STATE_BLOB,
        "parent_mincut_blob": git_blob_sha1(r / PARENT_MINCUT) == PARENT_MINCUT_BLOB,
        "old_quotient_blob": git_blob_sha1(r / OLD_QUOTIENT) == OLD_QUOTIENT_BLOB,
        "old_quotient_checker_blob": git_blob_sha1(r / OLD_QUOTIENT_CHECKER) == OLD_QUOTIENT_CHECKER_BLOB,
    }
    return {"ok": all(checks.values()), "checks": checks}


def firewall() -> dict:
    return {
        "P_VS_NP": "OPEN",
        "GENERAL_SAT_IN_P": "NOT_PROVED",
        "CONNECTED_MIXED_CORE_SOLVED": "NO",
        "ARBITRARY_UNSEEN_INVARIANT_DISCOVERY": "NOT_PROVED",
        "GENERAL_OVERWIDTH_CUT_COMPRESSION": "NOT_PROVED",
        "AFFINE_SYNDROME_UNIVERSALITY": "NOT_CLAIMED",
        "SCOPE": "OVERWIDTH_CANONICAL_CUT_WITH_ONE_FULL_CUT_EXPLICIT_RELATION_PER_COMPONENT",
        "GLOBAL_APMA_FRONTIER_ADVANCE": "NONE_PENDING_HQ_REVIEW",
    }


def _incidence(canonical: dict) -> dict[str, set[str]]:
    g: dict[str, set[str]] = {f"v:{v}": set() for v in canonical["variables"]}
    for i, row in enumerate(canonical["constraints"]):
        c = f"c:{i}"
        g[c] = set()
        for v in row["scope"]:
            n = f"v:{v}"
            g[c].add(n)
            g[n].add(c)
    return g


def constraint_components_after_cut(canonical: dict, cut_vars: list[int]) -> list[list[int]]:
    g = _incidence(canonical)
    removed = {f"v:{v}" for v in cut_vars}
    seen: set[str] = set()
    out: list[list[int]] = []
    for cidx in range(len(canonical["constraints"])):
        start = f"c:{cidx}"
        if start in seen:
            continue
        stack = [start]
        comp_constraints: list[int] = []
        while stack:
            node = stack.pop()
            if node in seen or node in removed:
                continue
            seen.add(node)
            if node.startswith("c:"):
                comp_constraints.append(int(node.split(":", 1)[1]))
            stack.extend(n for n in g[node] if n not in seen and n not in removed)
        if comp_constraints:
            out.append(sorted(comp_constraints))
    return sorted(out)


def project_relation_support(row: dict, cut_vars: list[int]) -> dict:
    scope = list(row["scope"])
    if not set(cut_vars).issubset(scope):
        raise ValueError("RELATION_DOES_NOT_EXPOSE_FULL_CUT")
    positions = [scope.index(v) for v in cut_vars]
    support: dict[tuple[int, ...], list[int]] = {}
    for raw_tuple in row["allowed"]:
        t = tuple(int(x) for x in raw_tuple)
        key = tuple(t[p] for p in positions)
        support.setdefault(key, list(t))
    body = {
        "relation_id": row["id"],
        "cut_variables": list(cut_vars),
        "support_size": len(support),
        "support_keys": [list(k) for k in sorted(support)],
        "input_rows_scanned": len(row["allowed"]),
    }
    body["support_sha256"] = sha256_obj(body)
    return {"receipt": body, "support": support}


def verify_original_assignment(canonical: dict, assignment: dict[int, int]) -> bool:
    for row in canonical["constraints"]:
        scope = list(row["scope"])
        t = tuple(int(assignment[v]) for v in scope)
        if list(t) not in [list(x) for x in row["allowed"]]:
            return False
    return True


def carrier_proposal(canonical: dict, parent: dict) -> dict:
    cut = list(parent["cut"]["cut_variables"])
    comps = constraint_components_after_cut(canonical, cut)
    body = {
        "role": "INAIHR_CANDIDATE_ONLY_EXACT_CUT_SUPPORT_CARRIER",
        "kind": "FULL_CUT_PROJECTED_SUPPORT_INTERSECTION",
        "raw_object_sha256": sha256_obj(canonical),
        "parent_cut_receipt_sha256": parent["cut"]["cut_receipt_sha256"],
        "cut_variables": cut,
        "constraint_components": comps,
        "truth_authority": False,
        "proof_authority": False,
        "automatic_promotion": False,
    }
    body["proposal_sha256"] = sha256_obj(body)
    return body


def verify_proposal(canonical: dict, parent: dict, proposal: dict) -> bool:
    body = dict(proposal)
    claimed = body.pop("proposal_sha256", None)
    return (
        isinstance(claimed, str)
        and sha256_obj(body) == claimed
        and proposal.get("kind") == "FULL_CUT_PROJECTED_SUPPORT_INTERSECTION"
        and proposal.get("raw_object_sha256") == sha256_obj(canonical)
        and proposal.get("parent_cut_receipt_sha256") == parent["cut"]["cut_receipt_sha256"]
        and proposal.get("cut_variables") == parent["cut"]["cut_variables"]
        and proposal.get("constraint_components") == constraint_components_after_cut(canonical, parent["cut"]["cut_variables"])
    )


def build_exact_carrier(canonical: dict, parent: dict, proposal: dict) -> dict:
    if not verify_proposal(canonical, parent, proposal):
        return {"status": "REJECT_TAMPERED_PROVENANCE", "resource_receipt": {"raw_cut_assignments_enumerated": 0}}

    cut = list(parent["cut"]["cut_variables"])
    comps = constraint_components_after_cut(canonical, cut)
    if len(comps) < 2 or any(len(c) != 1 for c in comps):
        return {"status": "OPEN_UNSUPPORTED_CUT_SUPPORT_CARRIER", "reason": "COMPONENT_RELATION_COUNT", "constraint_components": comps, "resource_receipt": {"raw_cut_assignments_enumerated": 0}}

    relations = [canonical["constraints"][c[0]] for c in comps]
    if any(not set(cut).issubset(set(r["scope"])) for r in relations):
        return {"status": "OPEN_UNSUPPORTED_CUT_SUPPORT_CARRIER", "reason": "PARTIAL_CUT_VISIBILITY", "constraint_components": comps, "resource_receipt": {"raw_cut_assignments_enumerated": 0}}

    private_sets = [set(r["scope"]) - set(cut) for r in relations]
    for i in range(len(private_sets)):
        for j in range(i + 1, len(private_sets)):
            if private_sets[i] & private_sets[j]:
                return {"status": "OPEN_UNSUPPORTED_CUT_SUPPORT_CARRIER", "reason": "PRIVATE_VARIABLE_OVERLAP", "resource_receipt": {"raw_cut_assignments_enumerated": 0}}

    projected = [project_relation_support(r, cut) for r in relations]
    key_sets = [set(p["support"]) for p in projected]
    common = set.intersection(*key_sets) if key_sets else set()
    sorted_common = sorted(common)
    min_support = min((len(s) for s in key_sets), default=0)
    total_rows = sum(len(r["allowed"]) for r in relations)

    base = {
        "proposal_sha256": proposal["proposal_sha256"],
        "cut_variables": cut,
        "cut_size": len(cut),
        "parent_L": parent["canonical_input_bytes_L"],
        "parent_raw_branch_budget": parent["redteam"]["branch_budget"],
        "component_support_receipts": [p["receipt"] for p in projected],
        "effective_support_size": len(sorted_common),
        "effective_support": [list(k) for k in sorted_common],
        "support_size_bound": min_support,
        "total_input_rows_scanned": total_rows,
    }

    resource = {
        "raw_cut_assignments_enumerated": 0,
        "component_input_rows_scanned": total_rows,
        "cartesian_products_materialized": 0,
        "generic_transfer_calls": 0,
        "solver_invocations": 0,
        "effective_states_materialized": len(sorted_common),
    }

    if not sorted_common:
        out = {**base, "status": "EXACT_UNSAT_BY_EMPTY_CUT_SUPPORT_INTERSECTION", "witness": None, "witness_verified": True, "resource_receipt": resource}
        out["carrier_sha256"] = sha256_obj(out)
        return out

    sigma = sorted_common[0]
    assignment: dict[int, int] = {v: int(bit) for v, bit in zip(cut, sigma)}
    relation_witness_rows = []
    for relation, proj in zip(relations, projected):
        row_tuple = proj["support"][sigma]
        relation_witness_rows.append({"relation_id": relation["id"], "tuple": list(row_tuple)})
        for v, bit in zip(relation["scope"], row_tuple):
            if v in assignment and assignment[v] != int(bit):
                raise AssertionError("INCONSISTENT_RECONSTRUCTION")
            assignment[v] = int(bit)
    for v in canonical["variables"]:
        assignment.setdefault(v, 0)
    verified = verify_original_assignment(canonical, assignment)
    out = {
        **base,
        "status": "ADMIT_EXACT_CUT_SUPPORT_INTERSECTION_CARRIER" if verified else "OPEN_UNSUPPORTED_CUT_SUPPORT_CARRIER",
        "witness": {"assignment": {str(v): assignment[v] for v in sorted(assignment)}, "relation_rows": relation_witness_rows},
        "witness_verified": verified,
        "resource_receipt": resource,
    }
    out["carrier_sha256"] = sha256_obj(out)
    return out


def explain_overwidth_cut(raw: dict) -> dict:
    guard = source_guard()
    if not guard["ok"]:
        return {"artifact_id": ARTIFACT_ID, "status": "HALT_SOURCE_GUARD", "source_guard": guard, "scientific_firewall": firewall()}
    try:
        canonical = canonicalize_raw(raw)
    except RawBasisInputError as exc:
        return {"artifact_id": ARTIFACT_ID, "authority": AUTHORITY, "status": "REJECT_RAW_INPUT", "reason": str(exc), "source_guard": guard, "scientific_firewall": firewall()}

    parent = parent_mincut.explain_with_mincut(raw)
    if parent.get("status") != "OPEN_MINCUT_BRANCH_BUDGET":
        return {"artifact_id": ARTIFACT_ID, "authority": AUTHORITY, "status": "OUT_OF_SCOPE_PARENT_NOT_OVERWIDTH", "parent_status": parent.get("status"), "source_guard": guard, "scientific_firewall": firewall()}
    if parent.get("redteam", {}).get("resource_receipt", {}).get("branch_enumerations") != 0:
        return {"artifact_id": ARTIFACT_ID, "authority": AUTHORITY, "status": "HALT_PARENT_RESOURCE_GUARD", "source_guard": guard, "scientific_firewall": firewall()}

    proposal = carrier_proposal(canonical, parent)
    carrier = build_exact_carrier(canonical, parent, proposal)
    receipt = {
        "raw_object_sha256": sha256_obj(canonical),
        "parent_cut_receipt_sha256": parent["cut"]["cut_receipt_sha256"],
        "proposal_sha256": proposal["proposal_sha256"],
        "carrier_sha256": carrier.get("carrier_sha256"),
        "terminal": carrier["status"],
    }
    receipt["explanation_sha256"] = sha256_obj(receipt)
    return {
        "artifact_id": ARTIFACT_ID,
        "authority": AUTHORITY,
        "status": carrier["status"],
        "source_guard": guard,
        "parent_status": parent["status"],
        "parent_cut": parent["cut"],
        "parent_resource_receipt": parent["redteam"]["resource_receipt"],
        "proposal": proposal,
        "carrier": carrier,
        "provenance_receipt": receipt,
        "execution_authorized": False,
        "complexity": {
            "claim": "POLYNOMIAL_IN_CANONICAL_EXPLICIT_INPUT_LENGTH_FOR_FROZEN_FULL_CUT_SINGLE_RELATION_COMPONENT_SCOPE",
            "construction": "project each explicit relation row to the canonical cut and intersect projected supports",
            "carrier_size": "<= minimum component projected support size <= total explicit input rows",
            "raw_2_to_k_enumeration": "FORBIDDEN_AND_ZERO",
        },
        "scientific_firewall": firewall(),
    }


def positive_overwidth() -> dict:
    return parent_mincut.negative_overwidth_cut(20)


def _embedded_xor_repeat_b(n: int) -> list[list[int]]:
    return [list((a,b,c) + (b,) * (n - 3)) for a,b,c in [(0,0,0),(0,1,1),(1,0,1),(1,1,0)]]


def empty_intersection_control(n: int = 20) -> dict:
    scope = list(range(n))
    return {
        "variables": scope,
        "constraints": [
            {"id": "opaque_embedded_or", "scope": scope, "allowed": parent_mincut._embedded_or_relation(n)},
            {"id": "opaque_affine_disjoint", "scope": scope, "allowed": _embedded_xor_repeat_b(n)},
        ],
    }


def multi_relation_component_control(n: int = 20) -> dict:
    cut = list(range(n))
    p = n
    ext_or0 = [row + [0] for row in parent_mincut._embedded_or_relation(n)]
    ext_or1 = [row + [1] for row in parent_mincut._embedded_or_relation(n)]
    return {
        "variables": cut + [p],
        "constraints": [
            {"id": "opaque_or_left", "scope": cut + [p], "allowed": ext_or0},
            {"id": "opaque_xor_right", "scope": cut, "allowed": parent_mincut._embedded_xor_relation(n)},
            {"id": "opaque_or_left_2", "scope": cut + [p], "allowed": ext_or1},
        ],
    }


def partial_cut_visibility_control() -> dict:
    base = list(range(18))
    scopes = [base + [18,19], base + [18,20], base + [19,20]]
    return {
        "variables": list(range(21)),
        "constraints": [
            {"id": "opaque_or_a", "scope": scopes[0], "allowed": parent_mincut._embedded_or_relation(20)},
            {"id": "opaque_xor_b", "scope": scopes[1], "allowed": parent_mincut._embedded_xor_relation(20)},
            {"id": "opaque_or_c", "scope": scopes[2], "allowed": parent_mincut._embedded_or_relation(20)},
        ],
    }


def injected_hint_control() -> dict:
    raw = positive_overwidth()
    raw["quotient_rank"] = 1
    return raw


def tamper_control() -> dict:
    canonical = canonicalize_raw(positive_overwidth())
    parent = parent_mincut.explain_with_mincut(positive_overwidth())
    proposal = carrier_proposal(canonical, parent)
    proposal["cut_variables"] = proposal["cut_variables"][:-1]
    return build_exact_carrier(canonical, parent, proposal)


def main() -> None:
    out = {
        "artifact_id": ARTIFACT_ID,
        "positive": explain_overwidth_cut(positive_overwidth()),
        "negative_empty": explain_overwidth_cut(empty_intersection_control()),
        "negative_multi_relation_component": explain_overwidth_cut(multi_relation_component_control()),
        "negative_partial_cut_visibility": explain_overwidth_cut(partial_cut_visibility_control()),
        "negative_hint": explain_overwidth_cut(injected_hint_control()),
        "negative_tamper": tamper_control(),
        "scientific_firewall": firewall(),
    }
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
