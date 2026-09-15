from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from research.tools.apma_unseen_basis.raw_relation_basis import canonicalize_raw, RawBasisInputError
from research.tools.apma_bicameral_mincut import mincut_logwidth_explainer as parent_mincut
from research.tools.apma_cut_support_carrier import cut_support_carrier as parent_support
from research.tools.apma_component_join_carrier import component_join_carrier_v1_3 as old_join

ARTIFACT_ID = "JANUS-TRUMP-BICAMERAL-DERIVED-TWO-RELATION-BOUNDARY-FACTOR-CANDIDATE-2026-09-15-v1.0"
AUTHORITY = "CANDIDATE_IMPLEMENTATION__NO_SCIENTIFIC_PROMOTION"
PREREG = Path("research/TRUMP_BICAMERAL_DERIVED_TWO_RELATION_BOUNDARY_FACTOR_PREREGISTRATION_2026-09-15.json")
PREREG_BLOB = "4c3af40842188d2489df8df7ed66c0e3dc8e711e"
PARENT_STATE = Path("registry/TRUMP_CURRENT_STATE_2026-09-15_v2.9.json")
PARENT_STATE_BLOB = "80bf1fb61ee3a773733f85f4305356d815dd3532"
OLD_JOIN = Path("research/tools/apma_component_join_carrier/component_join_carrier_v1_3.py")
OLD_JOIN_BLOB = "acfa7d0f82f4a0b70074661a6f558831b73c9362"


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
        "prereg_gate": prereg.get("frozen_gate") == "TRUMP_BICAMERAL_COMPONENT_DERIVED_TWO_RELATION_BOUNDARY_FACTOR_FALSIFIER_GATE",
        "parent_state_blob": git_blob_sha1(r / PARENT_STATE) == PARENT_STATE_BLOB,
        "old_join_blob": git_blob_sha1(r / OLD_JOIN) == OLD_JOIN_BLOB,
    }
    return {"ok": all(checks.values()), "checks": checks}


def firewall() -> dict:
    return {
        "P_VS_NP": "OPEN",
        "GENERAL_SAT_IN_P": "NOT_PROVED",
        "CONNECTED_MIXED_CORE_SOLVED": "NO",
        "ARBITRARY_UNSEEN_INVARIANT_DISCOVERY": "NOT_PROVED",
        "GENERAL_MULTI_RELATION_BOUNDARY_COMPRESSION": "NOT_PROVED",
        "GENERAL_BOUNDED_OUTPUT_ELIMINATION": "NOT_PROVED",
        "GLOBAL_APMA_FRONTIER_ADVANCE": "NONE_PENDING_HQ_REVIEW",
        "SCOPE": "OVERWIDTH_CANONICAL_CUT_WITH_SINGLETON_OR_EXACTLY_TWO_RELATIONS_PER_COMPONENT_AND_NO_JOIN_CHAIN",
    }


def _bits(seed: int, n: int) -> list[int]:
    return [((seed >> (i % 8)) ^ (i // 3)) & 1 for i in range(n)]


def positive_no_anchor_k20() -> dict:
    B0 = list(range(10))
    B1 = list(range(10, 20))
    Y = list(range(20, 40))
    z = 40
    A, C, D = _bits(5, 20), _bits(11, 20), _bits(23, 20)
    X, Y1, Y2 = _bits(7, 20), _bits(19, 20), _bits(29, 20)
    return {
        "variables": list(range(41)),
        "constraints": [
            {"id": "left_half_0", "scope": B0 + Y, "allowed": [A[:10] + X, C[:10] + Y1, D[:10] + Y2]},
            {"id": "left_half_1", "scope": B1 + Y, "allowed": [A[10:] + X, C[10:] + Y2, D[10:] + Y1]},
            {"id": "right_full", "scope": list(range(20)) + [z], "allowed": [A + [0], D + [1]]},
        ],
    }


def empty_pair_support_control() -> dict:
    raw = positive_no_anchor_k20()
    impossible = _bits(31, 20)
    raw["constraints"][1]["allowed"] = [raw["constraints"][1]["allowed"][0][:-20] + impossible]
    return raw


def three_relation_no_anchor_control() -> dict:
    raw = positive_no_anchor_k20()
    Y = list(range(20, 40))
    p = 41
    X = _bits(7, 20)
    raw["variables"] = list(range(42))
    raw["constraints"].insert(2, {"id": "left_third", "scope": Y + [p], "allowed": [X + [1]]})
    return raw


def incomplete_cover_unit_control() -> tuple[dict, list[int], list[int]]:
    B = list(range(20))
    canonical = canonicalize_raw({
        "variables": list(range(40)),
        "constraints": [
            {"id": "u0", "scope": list(range(10)) + list(range(20, 30)), "allowed": [[0] * 20]},
            {"id": "u1", "scope": list(range(10, 19)) + list(range(20, 30)), "allowed": [[0] * 19]},
        ],
    })
    return canonical, [0, 1], B


def injected_hint_control() -> dict:
    raw = positive_no_anchor_k20()
    raw["boundary_carrier"] = "TRUSTED_DERIVED_FACTOR"
    return raw


def _projection(scope: list[int], row: tuple[int, ...], cut: list[int]) -> tuple[int, ...]:
    pos = {v: i for i, v in enumerate(scope)}
    return tuple(int(row[pos[v]]) for v in cut)


def _compatible(scope_a: list[int], row_a: tuple[int, ...], scope_b: list[int], row_b: tuple[int, ...]) -> bool:
    pos_b = {v: i for i, v in enumerate(scope_b)}
    for i, v in enumerate(scope_a):
        j = pos_b.get(v)
        if j is not None and int(row_a[i]) != int(row_b[j]):
            return False
    return True


def _merge_rows(scope_a: list[int], row_a: tuple[int, ...], scope_b: list[int], row_b: tuple[int, ...]) -> dict[int, int]:
    merged = {v: int(bit) for v, bit in zip(scope_a, row_a)}
    for v, bit in zip(scope_b, row_b):
        bit = int(bit)
        if v in merged and merged[v] != bit:
            raise AssertionError("INCOMPATIBLE_ROWS_REACHED_MERGE")
        merged[v] = bit
    return merged


def component_support(canonical: dict, component: list[int], cut: list[int]) -> dict:
    B = set(cut)
    if len(component) == 1:
        gi = component[0]
        relation = canonical["constraints"][gi]
        scope = list(relation["scope"])
        if not B.issubset(set(scope)):
            return {"status": "OPEN_SINGLETON_WITHOUT_FULL_CUT_VISIBILITY", "component": component, "support": {}, "resource": {"row_pair_comparisons": 0}}
        support: dict[tuple[int, ...], dict] = {}
        for raw in relation["allowed"]:
            row = tuple(int(x) for x in raw)
            sigma = _projection(scope, row, cut)
            support.setdefault(sigma, {"rows": [{"global_relation_index": gi, "tuple": list(row)}]})
        return {
            "status": "ADMIT_DIRECT_SINGLETON_SUPPORT",
            "component": component,
            "support": support,
            "receipt": {"component": component, "kind": "SINGLETON_DIRECT_FULL_CUT_PROJECTION", "input_rows": len(relation["allowed"]), "support_size": len(support)},
            "resource": {"row_pair_comparisons": 0, "derived_pair_rows_materialized": 0},
        }
    if len(component) != 2:
        return {"status": "OPEN_COMPONENT_RELATION_COUNT_GT_2", "component": component, "support": {}, "resource": {"row_pair_comparisons": 0, "derived_pair_rows_materialized": 0}}
    g0, g1 = component
    r0, r1 = canonical["constraints"][g0], canonical["constraints"][g1]
    s0, s1 = list(r0["scope"]), list(r1["scope"])
    if not B.issubset(set(s0) | set(s1)):
        return {"status": "OPEN_INCOMPLETE_TWO_RELATION_CUT_COVER", "component": component, "support": {}, "resource": {"row_pair_comparisons": 0, "derived_pair_rows_materialized": 0}}
    support: dict[tuple[int, ...], dict] = {}
    comparisons = 0
    compatible_pairs = 0
    for raw0 in r0["allowed"]:
        row0 = tuple(int(x) for x in raw0)
        for raw1 in r1["allowed"]:
            row1 = tuple(int(x) for x in raw1)
            comparisons += 1
            if not _compatible(s0, row0, s1, row1):
                continue
            compatible_pairs += 1
            merged = _merge_rows(s0, row0, s1, row1)
            sigma = tuple(merged[v] for v in cut)
            support.setdefault(sigma, {"rows": [
                {"global_relation_index": g0, "tuple": list(row0)},
                {"global_relation_index": g1, "tuple": list(row1)},
            ]})
    product_bound = len(r0["allowed"]) * len(r1["allowed"])
    receipt = {
        "component": component,
        "kind": "DERIVED_TWO_RELATION_NATURAL_JOIN_PROJECT_B",
        "input_row_counts": [len(r0["allowed"]), len(r1["allowed"])],
        "row_pair_product_bound": product_bound,
        "row_pair_comparisons": comparisons,
        "compatible_pair_count": compatible_pairs,
        "support_size": len(support),
        "support_states": [list(x) for x in sorted(support)],
        "raw_full_cut_anchor_count": int(B.issubset(set(s0))) + int(B.issubset(set(s1))),
        "scope_union_covers_cut": True,
    }
    receipt["support_sha256"] = sha256_obj(receipt)
    return {
        "status": "ADMIT_DERIVED_TWO_RELATION_SUPPORT" if support else "EXACT_UNSAT_BY_EMPTY_DERIVED_COMPONENT_SUPPORT",
        "component": component,
        "support": support,
        "receipt": receipt,
        "resource": {
            "row_pair_comparisons": comparisons,
            "derived_pair_rows_materialized": compatible_pairs,
            "row_pair_product_bound": product_bound,
        },
    }


def proposal_record(canonical: dict, parent: dict, components: list[list[int]]) -> dict:
    body = {
        "role": "INAIHR_CANDIDATE_ONLY_DERIVED_TWO_RELATION_BOUNDARY_FACTOR",
        "kind": "BOUNDED_ONE_JOIN_PROJECT_BOUNDARY_FACTOR",
        "raw_object_sha256": sha256_obj(canonical),
        "parent_cut_receipt_sha256": parent["cut"]["cut_receipt_sha256"],
        "cut_variables": list(parent["cut"]["cut_variables"]),
        "constraint_components": components,
        "truth_authority": False,
        "proof_authority": False,
        "automatic_promotion": False,
    }
    body["proposal_sha256"] = sha256_obj(body)
    return body


def verify_proposal(canonical: dict, parent: dict, components: list[list[int]], proposal: dict) -> bool:
    body = dict(proposal)
    claimed = body.pop("proposal_sha256", None)
    return (
        isinstance(claimed, str)
        and sha256_obj(body) == claimed
        and proposal.get("kind") == "BOUNDED_ONE_JOIN_PROJECT_BOUNDARY_FACTOR"
        and proposal.get("raw_object_sha256") == sha256_obj(canonical)
        and proposal.get("parent_cut_receipt_sha256") == parent["cut"]["cut_receipt_sha256"]
        and proposal.get("cut_variables") == parent["cut"]["cut_variables"]
        and proposal.get("constraint_components") == components
    )


def verify_original_assignment(canonical: dict, assignment: dict[int, int]) -> bool:
    for relation in canonical["constraints"]:
        scope = list(relation["scope"])
        if any(v not in assignment for v in scope):
            return False
        target = tuple(int(assignment[v]) for v in scope)
        allowed = {tuple(int(x) for x in row) for row in relation["allowed"]}
        if target not in allowed:
            return False
    return True


def build_carrier(canonical: dict, parent: dict, components: list[list[int]], proposal: dict) -> dict:
    if not verify_proposal(canonical, parent, components, proposal):
        return {"status": "REJECT_TAMPERED_PROVENANCE", "resource_receipt": {"raw_cut_assignments_enumerated": 0, "unbounded_join_chains": 0}}
    cut = list(parent["cut"]["cut_variables"])
    results = []
    for comp in components:
        result = component_support(canonical, comp, cut)
        results.append(result)
        if result["status"].startswith("OPEN_"):
            return {"status": result["status"], "failed_component": comp, "component_results": results, "resource_receipt": {"raw_cut_assignments_enumerated": 0, "unbounded_join_chains": 0}}
        if result["status"] == "EXACT_UNSAT_BY_EMPTY_DERIVED_COMPONENT_SUPPORT":
            return {
                "status": "EXACT_UNSAT_BY_EMPTY_DERIVED_COMPONENT_SUPPORT",
                "failed_component": comp,
                "component_results": results,
                "witness": None,
                "witness_verified": True,
                "resource_receipt": {
                    "raw_cut_assignments_enumerated": 0,
                    "row_pair_comparisons": sum(x["resource"].get("row_pair_comparisons", 0) for x in results),
                    "unbounded_join_chains": 0,
                    "generic_transfer_calls": 0,
                    "external_solver_invocations": 0,
                },
            }
    supports = [set(x["support"]) for x in results]
    common = set.intersection(*supports) if supports else set()
    if not common:
        return {
            "status": "EXACT_UNSAT_BY_EMPTY_DERIVED_COMPONENT_SUPPORT",
            "component_results": results,
            "witness": None,
            "witness_verified": True,
            "resource_receipt": {
                "raw_cut_assignments_enumerated": 0,
                "row_pair_comparisons": sum(x["resource"].get("row_pair_comparisons", 0) for x in results),
                "unbounded_join_chains": 0,
                "generic_transfer_calls": 0,
                "external_solver_invocations": 0,
            },
        }
    sigma = sorted(common)[0]
    assignment = {v: int(bit) for v, bit in zip(cut, sigma)}
    relation_rows = []
    for result in results:
        for item in result["support"][sigma]["rows"]:
            gi = int(item["global_relation_index"])
            row = tuple(int(x) for x in item["tuple"])
            relation = canonical["constraints"][gi]
            for v, bit in zip(relation["scope"], row):
                if v in assignment and assignment[v] != bit:
                    raise AssertionError("WITNESS_MERGE_CONFLICT")
                assignment[v] = bit
            relation_rows.append({"relation_id": relation["id"], "tuple": list(row)})
    verified = verify_original_assignment(canonical, assignment)
    total_pairs = sum(x["resource"].get("row_pair_comparisons", 0) for x in results)
    max_product = max([x["resource"].get("row_pair_product_bound", 0) for x in results] or [0])
    out = {
        "status": "ADMIT_EXACT_DERIVED_TWO_RELATION_BOUNDARY_FACTOR" if verified else "OPEN_WITNESS_RECONSTRUCTION_FAILURE",
        "cut_variables": cut,
        "cut_size": len(cut),
        "component_results": results,
        "effective_support_size": len(common),
        "effective_support": [list(x) for x in sorted(common)],
        "witness": {"assignment": {str(v): assignment[v] for v in sorted(assignment)}, "relation_rows": relation_rows},
        "witness_verified": verified,
        "resource_receipt": {
            "raw_cut_assignments_enumerated": 0,
            "row_pair_comparisons": total_pairs,
            "max_component_row_pair_product_bound": max_product,
            "unbounded_join_chains": 0,
            "cartesian_products_across_components": 0,
            "generic_transfer_calls": 0,
            "external_solver_invocations": 0,
        },
    }
    out["carrier_sha256"] = sha256_obj(out)
    return out


def explain(raw: dict) -> dict:
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
    smaller = parent_support.explain_overwidth_cut(raw)
    if smaller.get("status") in {"ADMIT_EXACT_CUT_SUPPORT_INTERSECTION_CARRIER", "EXACT_UNSAT_BY_EMPTY_CUT_SUPPORT_INTERSECTION"}:
        return {"artifact_id": ARTIFACT_ID, "authority": AUTHORITY, "status": "OUT_OF_SCOPE_SINGLETON_CARRIER_ALREADY_EXISTS", "parent_support_status": smaller.get("status"), "source_guard": guard, "scientific_firewall": firewall()}
    old = old_join.explain_overwidth_component_join(raw)
    if old.get("status") == "ADMIT_EXACT_COMPONENT_JOIN_TREE_BOUNDARY_CARRIER":
        return {"artifact_id": ARTIFACT_ID, "authority": AUTHORITY, "status": "OUT_OF_SCOPE_OLD_FULL_ANCHOR_CARRIER_ALREADY_EXISTS", "old_join_status": old.get("status"), "source_guard": guard, "scientific_firewall": firewall()}
    cut = list(parent["cut"]["cut_variables"])
    components = parent_support.constraint_components_after_cut(canonical, cut)
    if len(components) < 2:
        return {"artifact_id": ARTIFACT_ID, "authority": AUTHORITY, "status": "OUT_OF_SCOPE_NO_CUT_COMPONENT_SPLIT", "components": components, "source_guard": guard, "scientific_firewall": firewall()}
    proposal = proposal_record(canonical, parent, components)
    carrier = build_carrier(canonical, parent, components, proposal)
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
        "parent_support_status": smaller.get("status"),
        "old_join_status": old.get("status"),
        "parent_cut": parent["cut"],
        "parent_resource_receipt": parent["redteam"]["resource_receipt"],
        "components": components,
        "proposal": proposal,
        "carrier": carrier,
        "provenance_receipt": receipt,
        "complexity": {
            "claim": "FIXED_POLYNOMIAL_IN_CANONICAL_EXPLICIT_INPUT_LENGTH_FOR_SINGLETON_OR_TWO_RELATION_COMPONENT_SCOPE",
            "two_relation_join": "one explicit row-pair natural join per two-relation component",
            "support_bound": "<= |R1|*|R2| <= O(L^2) per two-relation component",
            "global_conservative_bound": "O(L^3*arity) including O(L) components",
            "raw_2_to_k_enumeration": "FORBIDDEN_AND_ZERO",
            "unbounded_join_chain": "FORBIDDEN_AND_ZERO",
        },
        "scientific_firewall": firewall(),
    }


def tampered_control() -> dict:
    raw = positive_no_anchor_k20()
    canonical = canonicalize_raw(raw)
    parent = parent_mincut.explain_with_mincut(raw)
    cut = list(parent["cut"]["cut_variables"])
    components = parent_support.constraint_components_after_cut(canonical, cut)
    proposal = proposal_record(canonical, parent, components)
    proposal["constraint_components"] = list(reversed(components))
    return build_carrier(canonical, parent, components, proposal)


def main() -> None:
    unit_can, unit_comp, unit_cut = incomplete_cover_unit_control()
    print(json.dumps({
        "artifact_id": ARTIFACT_ID,
        "authority": AUTHORITY,
        "positive": explain(positive_no_anchor_k20()),
        "negative_empty": explain(empty_pair_support_control()),
        "negative_three": explain(three_relation_no_anchor_control()),
        "negative_incomplete_cover_unit": component_support(unit_can, unit_comp, unit_cut),
        "negative_hint": explain(injected_hint_control()),
        "negative_tamper": tampered_control(),
        "scientific_firewall": firewall(),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
