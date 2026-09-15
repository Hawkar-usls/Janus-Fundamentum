from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path
from typing import Any

from research.tools.apma_unseen_basis.raw_relation_basis import canonicalize_raw, RawBasisInputError
from research.tools.apma_unseen_basis.compositional_basis import induce_compositional_basis
from research.tools.apma_bicameral_mincut import mincut_logwidth_explainer as parent_mincut
from research.tools.apma_cut_support_carrier import cut_support_carrier as parent_support
from research.tools.apma_component_join_carrier import component_join_carrier_v1_3 as join_tree_gate
from research.tools.apma_derived_boundary_factor import derived_two_relation_factor as pair_v1
from research.tools.apma_derived_boundary_factor import derived_two_relation_factor_v1_1 as pair_gate

ARTIFACT_ID = "JANUS-TRUMP-BICAMERAL-GUARDED-BOUNDED-OUTPUT-ELIMINATION-CANDIDATE-2026-09-15-v1.0"
AUTHORITY = "CANDIDATE_IMPLEMENTATION__NO_SCIENTIFIC_PROMOTION"
PREREG = Path("research/TRUMP_BICAMERAL_GUARDED_BOUNDED_OUTPUT_ELIMINATION_PREREGISTRATION_2026-09-15.json")
PREREG_BLOB = "a2426b4600c6135e28d3b6fd8a981442a28093e0"
PARENT_STATE = Path("registry/TRUMP_CURRENT_STATE_2026-09-15_v3.1.json")
PARENT_STATE_BLOB = "2bea05bc87b0e1f29a241e22dab0fd2ab29f4088"
PAIR_GATE = Path("research/tools/apma_derived_boundary_factor/derived_two_relation_factor_v1_1.py")
PAIR_GATE_BLOB = "2332b09a897cbc85e1f5d2e562bc93e170ff5b1c"
R27_RESULT_COMMIT = "55c18e317d7a8081dc5ce6c20ee11e7d59f71cb8"
R29_RESULT_COMMIT = "1f1ca71c4a7a23dcca463fde5e3787772bbeac8e"
BUDGET_EXPONENT = 2


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
    p = json.loads((r / PREREG).read_text(encoding="utf-8"))
    checks = {
        "prereg_blob": git_blob_sha1(r / PREREG) == PREREG_BLOB,
        "prereg_frozen": p.get("status") == "FROZEN_BEFORE_CANDIDATE_IMPLEMENTATION",
        "prereg_gate": p.get("frozen_gate") == "TRUMP_BICAMERAL_COMPONENT_GUARDED_BOUNDED_OUTPUT_ELIMINATION_FALSIFIER_GATE",
        "parent_state_blob": git_blob_sha1(r / PARENT_STATE) == PARENT_STATE_BLOB,
        "pair_gate_blob": git_blob_sha1(r / PAIR_GATE) == PAIR_GATE_BLOB,
        "R27_bound": p.get("anti_loop", {}).get("historical_R27", {}).get("result_commit") == R27_RESULT_COMMIT,
        "R29_bound": p.get("anti_loop", {}).get("historical_R29", {}).get("result_commit") == R29_RESULT_COMMIT,
        "budget_exponent_two": p.get("fixed_budget", {}).get("bucket_combination_budget") == "L^2",
    }
    return {"ok": all(checks.values()), "checks": checks}


def firewall() -> dict:
    return {
        "P_VS_NP": "OPEN",
        "GENERAL_SAT_IN_P": "NOT_PROVED",
        "CONNECTED_MIXED_CORE_SOLVED": "NO",
        "GENERAL_BUCKET_ELIMINATION_POLYNOMIAL": "NOT_PROVED",
        "GENERAL_MULTI_RELATION_BOUNDARY_COMPRESSION": "NOT_PROVED",
        "OVERBUDGET_BUCKETS": "OPEN_NOT_NEGATIVE_EVIDENCE",
        "GLOBAL_APMA_FRONTIER_ADVANCE": "NONE_PENDING_HQ_REVIEW",
        "SCOPE": "PREDECESSOR_OPEN_MIXED_3PLUS_COMPONENTS_WITH_EVERY_FROZEN_ORDER_BUCKET_PRECHECKED_AT_PRODUCT_LE_L2",
    }


def canonical_input_L(canonical: dict) -> int:
    return max(2, len(canonical_bytes(canonical)))


def _factor_from_relation(rel: dict, global_index: int) -> dict:
    original_scope = list(rel["scope"])
    scope = sorted(original_scope)
    pos = {v: i for i, v in enumerate(original_scope)}
    rows = sorted({tuple(int(raw[pos[v]]) for v in scope) for raw in rel["allowed"]})
    return {"id": f"orig:{global_index}", "scope": scope, "rows": rows, "origin_relation_indices": [global_index]}


def _factor_public(f: dict) -> dict:
    return {"id": f["id"], "scope": list(f["scope"]), "row_count": len(f["rows"]), "rows": [list(r) for r in f["rows"]]}


def _guarded_product(counts: list[int], budget: int) -> dict:
    product = 1
    for count in counts:
        count = int(count)
        if count == 0:
            return {"over": False, "product": 0, "capped_product": 0}
        if product > budget // count:
            return {"over": True, "product": None, "capped_product": budget + 1}
        product *= count
    return {"over": product > budget, "product": product, "capped_product": min(product, budget + 1)}


def _merge_combo(bucket: list[dict], combo: tuple[tuple[int, ...], ...]) -> dict[int, int] | None:
    merged: dict[int, int] = {}
    for factor, row in zip(bucket, combo):
        for v, bit in zip(factor["scope"], row):
            bit = int(bit)
            if v in merged and merged[v] != bit:
                return None
            merged[v] = bit
    return merged


def _public_record(rec: dict) -> dict:
    out = {k: v for k, v in rec.items() if k not in {"_witness_by_row"}}
    if "_witness_by_row" in rec:
        out["witness_entries"] = [
            {"output_tuple": list(key), "eliminated_value": int(value)}
            for key, value in sorted(rec["_witness_by_row"].items())
        ]
    return out


def eliminate_one_variable(factors: list[dict], var: int, budget: int, step: int, phase: str) -> dict:
    bucket = [f for f in factors if var in f["scope"]]
    if not bucket:
        return {"status": "NOOP", "factors": factors, "record": None}
    rest = [f for f in factors if var not in f["scope"]]
    counts = [len(f["rows"]) for f in bucket]
    product = _guarded_product(counts, budget)
    base_record = {
        "step": step,
        "phase": phase,
        "variable": int(var),
        "bucket_factor_ids": [f["id"] for f in bucket],
        "bucket_factor_count": len(bucket),
        "bucket_row_counts": counts,
        "budget": budget,
        "pre_expansion_product": product["product"],
        "pre_expansion_capped_product": product["capped_product"],
        "pre_expansion_guard_over": product["over"],
    }
    if product["over"]:
        rec = {
            **base_record,
            "status": "OPEN_BUCKET_PRODUCT_BUDGET",
            "combinations_enumerated": 0,
            "compatible_combinations": 0,
            "output_rows": 0,
            "guard_ran_before_enumeration": True,
        }
        return {"status": "OPEN_BUCKET_PRODUCT_BUDGET", "factors": factors, "record": rec}

    union_scope = sorted({v for f in bucket for v in f["scope"]})
    output_scope = [v for v in union_scope if v != var]
    output_rows: dict[tuple[int, ...], int] = {}
    combinations = 0
    compatible = 0
    for combo in itertools.product(*(f["rows"] for f in bucket)):
        combinations += 1
        merged = _merge_combo(bucket, combo)
        if merged is None:
            continue
        compatible += 1
        outrow = tuple(int(merged[v]) for v in output_scope)
        output_rows.setdefault(outrow, int(merged[var]))
    rows = sorted(output_rows)
    new_factor = {
        "id": f"elim:{step}:v{var}",
        "scope": output_scope,
        "rows": rows,
        "origin_relation_indices": sorted({gi for f in bucket for gi in f.get("origin_relation_indices", [])}),
    }
    rec = {
        **base_record,
        "status": "ADMIT_BUCKET_ELIMINATION" if rows else "EXACT_EMPTY_BUCKET_PROJECTION",
        "output_factor_id": new_factor["id"],
        "output_scope": output_scope,
        "combinations_enumerated": combinations,
        "compatible_combinations": compatible,
        "output_rows": len(rows),
        "guard_ran_before_enumeration": True,
        "_witness_by_row": output_rows,
    }
    return {"status": rec["status"], "factors": rest + [new_factor], "record": rec}


def reconstruct_assignment(records: list[dict], variables: list[int]) -> dict:
    assignment: dict[int, int] = {}
    for rec in reversed(records):
        if rec.get("status") not in {"ADMIT_BUCKET_ELIMINATION"}:
            continue
        scope = list(rec["output_scope"])
        if any(v not in assignment for v in scope):
            return {"ok": False, "reason": "MISSING_LATER_VARIABLE_FOR_RECONSTRUCTION", "assignment": assignment, "failed_step": rec["step"]}
        key = tuple(int(assignment[v]) for v in scope)
        witness = rec.get("_witness_by_row", {})
        if key not in witness:
            return {"ok": False, "reason": "OUTPUT_TUPLE_NOT_IN_WITNESS_MAP", "assignment": assignment, "failed_step": rec["step"], "key": list(key)}
        value = int(witness[key])
        var = int(rec["variable"])
        if var in assignment and assignment[var] != value:
            return {"ok": False, "reason": "RECONSTRUCTION_CONFLICT", "assignment": assignment, "failed_step": rec["step"]}
        assignment[var] = value
    for v in variables:
        assignment.setdefault(int(v), 0)
    return {"ok": True, "reason": "REVERSE_BUCKET_WITNESS_REPLAY", "assignment": assignment}


def verify_original_assignment(canonical: dict, assignment: dict[int, int]) -> bool:
    for rel in canonical["constraints"]:
        scope = list(rel["scope"])
        if any(v not in assignment for v in scope):
            return False
        target = tuple(int(assignment[v]) for v in scope)
        allowed = {tuple(int(x) for x in row) for row in rel["allowed"]}
        if target not in allowed:
            return False
    return True


def run_guarded_elimination(canonical: dict, cut: list[int], components: list[list[int]]) -> dict:
    L = canonical_input_L(canonical)
    budget = L * L
    records: list[dict] = []
    public_buckets: list[dict] = []
    boundary_factors: list[dict] = []
    step = 0
    total_combinations = 0
    max_output_rows = 0

    B = set(cut)
    for ci, comp in enumerate(components):
        factors = [_factor_from_relation(canonical["constraints"][gi], gi) for gi in comp]
        internal = sorted({v for f in factors for v in f["scope"] if v not in B})
        for v in internal:
            step += 1
            result = eliminate_one_variable(factors, v, budget, step, f"COMPONENT_{ci}_PRIVATE")
            rec = result["record"]
            if rec is not None:
                public_buckets.append(_public_record(rec))
                if rec["status"] == "OPEN_BUCKET_PRODUCT_BUDGET":
                    return {
                        "status": "OPEN_BUCKET_PRODUCT_BUDGET",
                        "L": L,
                        "budget": budget,
                        "cut": cut,
                        "components": components,
                        "failed_bucket": _public_record(rec),
                        "bucket_records": public_buckets,
                        "records_internal": records,
                        "resource_receipt": {
                            "raw_cut_assignments_enumerated": 0,
                            "failed_bucket_combinations_enumerated": 0,
                            "total_combinations_enumerated_before_open": total_combinations,
                            "alternative_order_retries": 0,
                            "generic_transfer_calls": 0,
                            "external_solver_calls": 0,
                        },
                    }
                total_combinations += int(rec["combinations_enumerated"])
                max_output_rows = max(max_output_rows, int(rec["output_rows"]))
                records.append(rec)
            factors = result["factors"]
            if any(len(f["rows"]) == 0 for f in factors):
                return {
                    "status": "EXACT_UNSAT_BY_COMPLETE_GUARDED_ELIMINATION",
                    "L": L,
                    "budget": budget,
                    "cut": cut,
                    "components": components,
                    "bucket_records": public_buckets,
                    "records_internal": records,
                    "resource_receipt": {
                        "raw_cut_assignments_enumerated": 0,
                        "total_combinations_enumerated": total_combinations,
                        "max_output_rows": max_output_rows,
                        "alternative_order_retries": 0,
                        "generic_transfer_calls": 0,
                        "external_solver_calls": 0,
                    },
                }
        if any(any(v not in B for v in f["scope"]) for f in factors):
            return {"status": "OPEN_INTERNAL_ELIMINATION_GAP", "resource_receipt": {"raw_cut_assignments_enumerated": 0}}
        boundary_factors.extend(factors)

    boundary_factor_snapshot = [_factor_public(f) for f in boundary_factors]
    factors = boundary_factors
    for v in sorted(cut):
        step += 1
        result = eliminate_one_variable(factors, v, budget, step, "GLOBAL_BOUNDARY")
        rec = result["record"]
        if rec is not None:
            public_buckets.append(_public_record(rec))
            if rec["status"] == "OPEN_BUCKET_PRODUCT_BUDGET":
                return {
                    "status": "OPEN_BUCKET_PRODUCT_BUDGET",
                    "L": L,
                    "budget": budget,
                    "cut": cut,
                    "components": components,
                    "boundary_factor_snapshot": boundary_factor_snapshot,
                    "failed_bucket": _public_record(rec),
                    "bucket_records": public_buckets,
                    "records_internal": records,
                    "resource_receipt": {
                        "raw_cut_assignments_enumerated": 0,
                        "failed_bucket_combinations_enumerated": 0,
                        "total_combinations_enumerated_before_open": total_combinations,
                        "alternative_order_retries": 0,
                        "generic_transfer_calls": 0,
                        "external_solver_calls": 0,
                    },
                }
            total_combinations += int(rec["combinations_enumerated"])
            max_output_rows = max(max_output_rows, int(rec["output_rows"]))
            records.append(rec)
        factors = result["factors"]
        if any(len(f["rows"]) == 0 for f in factors):
            return {
                "status": "EXACT_UNSAT_BY_COMPLETE_GUARDED_ELIMINATION",
                "L": L,
                "budget": budget,
                "cut": cut,
                "components": components,
                "boundary_factor_snapshot": boundary_factor_snapshot,
                "bucket_records": public_buckets,
                "records_internal": records,
                "resource_receipt": {
                    "raw_cut_assignments_enumerated": 0,
                    "total_combinations_enumerated": total_combinations,
                    "max_output_rows": max_output_rows,
                    "alternative_order_retries": 0,
                    "generic_transfer_calls": 0,
                    "external_solver_calls": 0,
                },
            }
    if any(f["scope"] for f in factors):
        return {"status": "OPEN_BOUNDARY_ELIMINATION_GAP", "resource_receipt": {"raw_cut_assignments_enumerated": 0}}
    if any(len(f["rows"]) == 0 for f in factors):
        return {"status": "EXACT_UNSAT_BY_COMPLETE_GUARDED_ELIMINATION", "records_internal": records, "bucket_records": public_buckets, "resource_receipt": {"raw_cut_assignments_enumerated": 0, "total_combinations_enumerated": total_combinations}}

    reconstructed = reconstruct_assignment(records, list(canonical["variables"]))
    verified = bool(reconstructed["ok"] and verify_original_assignment(canonical, reconstructed["assignment"]))
    return {
        "status": "ADMIT_EXACT_GUARDED_BOUNDED_OUTPUT_ELIMINATION" if verified else "OPEN_WITNESS_RECONSTRUCTION_FAILURE",
        "L": L,
        "budget": budget,
        "cut": cut,
        "components": components,
        "boundary_factor_snapshot": boundary_factor_snapshot,
        "bucket_records": public_buckets,
        "records_internal": records,
        "witness": {"assignment": {str(v): int(reconstructed["assignment"][v]) for v in sorted(reconstructed["assignment"])} if reconstructed["ok"] else None, "reconstruction_reason": reconstructed["reason"]},
        "witness_verified": verified,
        "resource_receipt": {
            "raw_cut_assignments_enumerated": 0,
            "total_combinations_enumerated": total_combinations,
            "failed_bucket_combinations_enumerated": None,
            "max_output_rows": max_output_rows,
            "successful_bucket_count": len(records),
            "certificate_witness_entries": sum(len(rec.get("_witness_by_row", {})) for rec in records),
            "alternative_order_retries": 0,
            "generic_transfer_calls": 0,
            "external_solver_calls": 0,
            "materialized_global_cut_cube": False,
        },
    }


def proposal_record(canonical: dict, parent: dict, components: list[list[int]]) -> dict:
    body = {
        "role": "INAIHR_CANDIDATE_ONLY_GUARDED_BOUNDED_OUTPUT_ELIMINATION",
        "kind": "CANONICAL_ORDER_EXACT_BUCKET_ELIMINATION_WITH_L2_PRE_EXPANSION_GUARD",
        "raw_object_sha256": sha256_obj(canonical),
        "parent_cut_receipt_sha256": parent["cut"]["cut_receipt_sha256"],
        "cut_variables": list(parent["cut"]["cut_variables"]),
        "components": components,
        "budget_exponent": BUDGET_EXPONENT,
        "variable_order": "INCREASING_PRIVATE_PER_COMPONENT_THEN_INCREASING_CUT",
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
        and proposal.get("kind") == "CANONICAL_ORDER_EXACT_BUCKET_ELIMINATION_WITH_L2_PRE_EXPANSION_GUARD"
        and proposal.get("raw_object_sha256") == sha256_obj(canonical)
        and proposal.get("parent_cut_receipt_sha256") == parent["cut"]["cut_receipt_sha256"]
        and proposal.get("cut_variables") == parent["cut"]["cut_variables"]
        and proposal.get("components") == components
        and proposal.get("budget_exponent") == BUDGET_EXPONENT
        and proposal.get("variable_order") == "INCREASING_PRIVATE_PER_COMPONENT_THEN_INCREASING_CUT"
    )


def build_carrier(canonical: dict, parent: dict, components: list[list[int]], proposal: dict) -> dict:
    if not verify_proposal(canonical, parent, components, proposal):
        return {"status": "REJECT_TAMPERED_PROVENANCE", "resource_receipt": {"raw_cut_assignments_enumerated": 0, "failed_bucket_combinations_enumerated": 0}}
    result = run_guarded_elimination(canonical, list(parent["cut"]["cut_variables"]), components)
    public = {k: v for k, v in result.items() if k != "records_internal"}
    public["carrier_sha256"] = sha256_obj(public)
    return public


def explain(raw: dict) -> dict:
    guard = source_guard()
    if not guard["ok"]:
        return {"artifact_id": ARTIFACT_ID, "status": "HALT_SOURCE_GUARD", "source_guard": guard, "scientific_firewall": firewall()}
    try:
        canonical = canonicalize_raw(raw)
    except RawBasisInputError as exc:
        return {"artifact_id": ARTIFACT_ID, "authority": AUTHORITY, "status": "REJECT_RAW_INPUT", "reason": str(exc), "source_guard": guard, "scientific_firewall": firewall()}

    global_basis = induce_compositional_basis(canonical)
    if global_basis.get("status") == "ADMIT_COMPOSITIONAL_BASIS_PORTFOLIO":
        return {"artifact_id": ARTIFACT_ID, "authority": AUTHORITY, "status": "OUT_OF_SCOPE_RAW_BASIS_ALREADY_ADMITS", "global_basis_status": global_basis.get("status"), "source_guard": guard, "scientific_firewall": firewall()}

    parent = parent_mincut.explain_with_mincut(raw)
    if parent.get("status") != "OPEN_MINCUT_BRANCH_BUDGET":
        return {"artifact_id": ARTIFACT_ID, "authority": AUTHORITY, "status": "OUT_OF_SCOPE_PARENT_NOT_OVERWIDTH", "parent_status": parent.get("status"), "global_basis_status": global_basis.get("status"), "source_guard": guard, "scientific_firewall": firewall()}
    if parent.get("redteam", {}).get("resource_receipt", {}).get("branch_enumerations") != 0:
        return {"artifact_id": ARTIFACT_ID, "authority": AUTHORITY, "status": "HALT_PARENT_RESOURCE_GUARD", "source_guard": guard, "scientific_firewall": firewall()}

    cut = list(parent["cut"]["cut_variables"])
    components = parent_support.constraint_components_after_cut(canonical, cut)
    if not any(len(c) >= 3 for c in components):
        return {"artifact_id": ARTIFACT_ID, "authority": AUTHORITY, "status": "OUT_OF_SCOPE_NO_THREE_RELATION_COMPONENT", "components": components, "source_guard": guard, "scientific_firewall": firewall()}

    predecessor = pair_gate.explain(raw)
    if predecessor.get("status") != "OPEN_COMPONENT_RELATION_COUNT_GT_2":
        return {"artifact_id": ARTIFACT_ID, "authority": AUTHORITY, "status": "OUT_OF_SCOPE_PREDECESSOR_TERMINAL", "predecessor_status": predecessor.get("status"), "components": components, "source_guard": guard, "scientific_firewall": firewall()}

    old_join = join_tree_gate.explain_overwidth_component_join(raw)
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
        "global_basis_status": global_basis.get("status"),
        "parent_status": parent["status"],
        "parent_cut": parent["cut"],
        "parent_resource_receipt": parent["redteam"]["resource_receipt"],
        "components": components,
        "predecessor_two_relation_status": predecessor.get("status"),
        "predecessor_join_tree_status": old_join.get("status"),
        "proposal": proposal,
        "carrier": carrier,
        "provenance_receipt": receipt,
        "complexity": {
            "claim": "FIXED_ORIGINAL_L_POLYNOMIAL_ENVELOPE_FOR_FROZEN_GUARDED_BUCKET_SCOPE",
            "bucket_budget": "L^2 combinations checked before enumeration",
            "successful_bucket_output": "<= L^2 rows",
            "number_of_eliminated_variables": "<= O(L)",
            "conservative_total_lifecycle": "O(L^6)",
            "polynomial_degree_depends_on_relation_count": False,
            "raw_2_to_k_enumeration": 0,
            "alternative_order_search": 0,
        },
        "scientific_firewall": firewall(),
    }


def positive_mixed_three_relation_control() -> dict:
    return pair_v1.three_relation_no_anchor_control()


def scoped_unsat_control() -> dict:
    raw = positive_mixed_three_relation_control()
    D = pair_v1._bits(23, 20)
    raw["constraints"][-1] = {"id": "right_incompatible_singleton", "scope": list(range(20)) + [40], "allowed": [D + [0]]}
    return raw


def _or_like_y_relation(rel_id: str, p: int) -> dict:
    Y = list(range(20, 40))
    rows = []
    for a, b in [(0, 1), (1, 0), (1, 1)]:
        y = [0] * 20
        y[0] = a
        rows.append(y + [b])
    return {"id": rel_id, "scope": Y + [p], "allowed": rows}


def _xor_like_y_relation(rel_id: str, p: int) -> dict:
    Y = list(range(20, 40))
    rows = []
    for a, b, c in [(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 0)]:
        y = [0] * 20
        y[0] = a
        y[1] = b
        rows.append(y + [c])
    return {"id": rel_id, "scope": Y + [p], "allowed": rows}


def overbudget_control() -> dict:
    raw = positive_mixed_three_relation_control()
    extras = []
    start = 42
    for i in range(20):
        p = start + i
        if i % 2 == 0:
            extras.append(_or_like_y_relation(f"budget_or_{i}", p))
        else:
            extras.append(_xor_like_y_relation(f"budget_xor_{i}", p))
    raw["variables"] = list(range(start + len(extras)))
    raw["constraints"] = raw["constraints"][:-1] + extras + [raw["constraints"][-1]]
    return raw


def injected_hint_control() -> dict:
    raw = positive_mixed_three_relation_control()
    raw["elimination_order"] = "TRUSTED_MAGIC_ORDER"
    return raw


def tampered_control() -> dict:
    raw = positive_mixed_three_relation_control()
    canonical = canonicalize_raw(raw)
    parent = parent_mincut.explain_with_mincut(raw)
    cut = list(parent["cut"]["cut_variables"])
    components = parent_support.constraint_components_after_cut(canonical, cut)
    proposal = proposal_record(canonical, parent, components)
    proposal["components"] = list(reversed(components))
    return build_carrier(canonical, parent, components, proposal)


def main() -> None:
    result = {
        "artifact_id": ARTIFACT_ID,
        "authority": AUTHORITY,
        "positive": explain(positive_mixed_three_relation_control()),
        "negative_unsat": explain(scoped_unsat_control()),
        "negative_overbudget": explain(overbudget_control()),
        "negative_hint": explain(injected_hint_control()),
        "negative_tamper": tampered_control(),
        "scientific_firewall": firewall(),
    }
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
