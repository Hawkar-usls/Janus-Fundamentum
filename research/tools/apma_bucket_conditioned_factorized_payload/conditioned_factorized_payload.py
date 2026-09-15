from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from research.tools.apma_unseen_basis.raw_relation_basis import canonicalize_raw, RawBasisInputError
from research.tools.apma_bucket_common_core import common_core_semijoin_prefilter as cc_v1
from research.tools.apma_bucket_common_core import common_core_semijoin_prefilter_v1_1 as cc_v11
from research.tools.apma_guarded_elimination import guarded_bounded_output_elimination as guarded
from research.tools.apma_cut_support_carrier import cut_support_carrier as parent_support
from research.tools.apma_derived_boundary_factor import derived_two_relation_factor as pair_v1

ARTIFACT_ID = "JANUS-TRUMP-BICAMERAL-BUCKET-UNIQUE-CORE-CONDITIONED-FACTORIZED-PAYLOAD-CANDIDATE-2026-09-15-v1.0"
AUTHORITY = "CANDIDATE_IMPLEMENTATION__NO_SCIENTIFIC_PROMOTION"
PREREG = Path("research/TRUMP_BICAMERAL_BUCKET_UNIQUE_CORE_CONDITIONED_FACTORIZED_PAYLOAD_PREREGISTRATION_2026-09-15.json")
PREREG_BLOB = "b8d1d74ac6dd32efb1da10bde988e3b89b3276b3"
PARENT_STATE = Path("registry/TRUMP_CURRENT_STATE_2026-09-15_v3.4.json")
PARENT_STATE_BLOB = "f654b77a14d3d5650b2a6af77769bbcbc7bad3a0"
COMMON_V11 = Path("research/tools/apma_bucket_common_core/common_core_semijoin_prefilter_v1_1.py")
COMMON_V11_BLOB = "c29229bbaebf2935ab03c77c7d444e2a33422f17"
FACTORIZED = Path("research/tools/apma_factorized_feedback/factorized_portfolio.py")
FACTORIZED_BLOB = "ab3cd177eb1e554f5119238c8556f05feb988bb3"
GUARDED = Path("research/tools/apma_guarded_elimination/guarded_bounded_output_elimination.py")
GUARDED_BLOB = "314034bac990e524d1db7743aef0aebd3b4565c1"


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
        "prereg_gate": p.get("frozen_gate") == "TRUMP_BICAMERAL_BUCKET_UNIQUE_CORE_CONDITIONED_FACTORIZED_PAYLOAD_FALSIFIER_GATE",
        "parent_state_blob": git_blob_sha1(r / PARENT_STATE) == PARENT_STATE_BLOB,
        "common_v11_blob": git_blob_sha1(r / COMMON_V11) == COMMON_V11_BLOB,
        "factorized_feedback_blob": git_blob_sha1(r / FACTORIZED) == FACTORIZED_BLOB,
        "guarded_blob": git_blob_sha1(r / GUARDED) == GUARDED_BLOB,
    }
    return {"ok": all(checks.values()), "checks": checks}


def firewall() -> dict:
    return {
        "P_VS_NP": "OPEN",
        "GENERAL_SAT_IN_P": "NOT_PROVED",
        "CONNECTED_MIXED_CORE_SOLVED": "NO",
        "GENERAL_EFFECTIVE_BUCKET_COMPRESSION": "NOT_PROVED",
        "GENERAL_BUCKET_ELIMINATION_POLYNOMIAL": "NOT_PROVED",
        "GENERAL_CONDITIONED_FACTORIZATION": "NOT_PROVED",
        "GLOBAL_APMA_FRONTIER_ADVANCE": "NONE_PENDING_HQ_REVIEW",
        "SCOPE": "UNIQUE_COMMON_CORE_STATE_WITH_COMPLETE_TARGET_BUCKET_COVERAGE_AND_PAIRWISE_DISJOINT_RESIDUAL_SCOPES_ONLY",
    }


def _target_factor_ids(ready: dict) -> list[str]:
    return [f"orig:{int(gi)}" for gi in ready["component"]]


def _residual_scopes(bucket: list[dict], core: list[int]) -> list[list[int]]:
    c = set(core)
    return [[v for v in f["scope"] if v not in c] for f in bucket]


def _cross_couplings(residual_scopes: list[list[int]]) -> list[dict]:
    out = []
    for i in range(len(residual_scopes)):
        a = set(residual_scopes[i])
        for j in range(i + 1, len(residual_scopes)):
            shared = sorted(a & set(residual_scopes[j]))
            if shared:
                out.append({"i": i, "j": j, "shared": shared})
    return out


def proposal_record(canonical: dict, ready: dict, unique_state: tuple[int, ...], residual_scopes: list[list[int]]) -> dict:
    body = {
        "kind": "UNIQUE_COMMON_CORE_CONDITIONED_FACTORIZED_PAYLOAD_PORTFOLIO",
        "raw_object_sha256": sha256_obj(canonical),
        "failed_variable": int(ready["failed_variable"]),
        "target_component": list(ready["component"]),
        "bucket_factor_ids": [f["id"] for f in ready["bucket"]],
        "common_core": list(ready["common_core"]),
        "unique_common_state": list(unique_state),
        "residual_scopes": [list(x) for x in residual_scopes],
        "truth_authority": False,
        "proof_authority": False,
        "automatic_promotion": False,
    }
    body["proposal_sha256"] = sha256_obj(body)
    return body


def verify_proposal(canonical: dict, ready: dict, unique_state: tuple[int, ...], residual_scopes: list[list[int]], proposal: dict) -> bool:
    body = dict(proposal)
    claimed = body.pop("proposal_sha256", None)
    expected = proposal_record(canonical, ready, unique_state, residual_scopes)
    return (
        isinstance(claimed, str)
        and sha256_obj(body) == claimed
        and proposal == expected
    )


def _conditioned_rows(factor: dict, core: list[int], state: tuple[int, ...]) -> list[tuple[int, ...]]:
    return [row for row in factor["rows"] if cc_v1._projection(factor, core, row) == state]


def _build_portfolio(ready: dict, state: tuple[int, ...]) -> dict:
    canonical = ready["canonical"]
    cut = set(ready["cut"])
    core = list(ready["common_core"])
    portfolio_public = []
    internal = []
    boundary_constraints = []
    total_conditioned_rows = 0
    total_boundary_rows = 0

    for ordinal, factor in enumerate(ready["bucket"]):
        rows = _conditioned_rows(factor, core, state)
        if not rows:
            return {"status": "EXACT_UNSAT_BY_EMPTY_CONDITIONED_FACTOR", "factor_id": factor["id"]}
        total_conditioned_rows += len(rows)
        residual_scope = [v for v in factor["scope"] if v not in set(core)]
        boundary_scope = [v for v in residual_scope if v in cut]
        pos = {v: i for i, v in enumerate(factor["scope"])}
        witness_by_boundary: dict[tuple[int, ...], tuple[int, ...]] = {}
        for row in rows:
            key = tuple(int(row[pos[v]]) for v in boundary_scope)
            witness_by_boundary.setdefault(key, row)
        boundary_rows = sorted(witness_by_boundary)
        total_boundary_rows += len(boundary_rows)
        public = {
            "factor_id": factor["id"],
            "origin_relation_index": int(factor["gi"]),
            "residual_scope": residual_scope,
            "boundary_scope": boundary_scope,
            "conditioned_row_count": len(rows),
            "boundary_row_count": len(boundary_rows),
            "boundary_rows": [list(x) for x in boundary_rows],
            "witness_entries": [
                {"boundary_tuple": list(k), "original_sorted_row": list(witness_by_boundary[k])}
                for k in boundary_rows
            ],
        }
        public["factor_receipt_sha256"] = sha256_obj(public)
        portfolio_public.append(public)
        internal.append({"factor": factor, "boundary_scope": boundary_scope, "witness_by_boundary": witness_by_boundary})
        if boundary_scope:
            boundary_constraints.append({
                "id": f"conditioned_boundary_{ordinal}_{factor['id'].replace(':', '_')}",
                "scope": boundary_scope,
                "allowed": [list(x) for x in boundary_rows],
            })

    return {
        "status": "ADMIT_FACTORIZED_TARGET_BOUNDARY_PORTFOLIO",
        "portfolio": portfolio_public,
        "boundary_constraints": boundary_constraints,
        "internal": internal,
        "metrics": {
            "portfolio_records": len(portfolio_public),
            "total_conditioned_rows_scanned": total_conditioned_rows,
            "total_boundary_rows_stored": total_boundary_rows,
            "cartesian_products_materialized": 0,
            "bucket_combinations_enumerated": 0,
        },
    }


def _transformed_raw(ready: dict, portfolio: dict) -> dict:
    canonical = ready["canonical"]
    target = set(int(x) for x in ready["component"])
    constraints = [
        json.loads(json.dumps(rel))
        for gi, rel in enumerate(canonical["constraints"])
        if gi not in target
    ]
    constraints.extend(json.loads(json.dumps(x)) for x in portfolio["boundary_constraints"])
    return {"variables": list(canonical["variables"]), "constraints": constraints}


def _reconstruct_original(ready: dict, portfolio: dict, state: tuple[int, ...], transformed_assignment: dict[int, int]) -> dict:
    assignment = {int(k): int(v) for k, v in transformed_assignment.items()}
    cut = set(ready["cut"])
    target_internal = {
        v
        for gi in ready["component"]
        for v in ready["canonical"]["constraints"][gi]["scope"]
        if v not in cut
    }
    for v in target_internal:
        assignment.pop(int(v), None)
    for v, bit in zip(ready["common_core"], state):
        assignment[int(v)] = int(bit)

    chosen_rows = []
    for rec in portfolio["internal"]:
        factor = rec["factor"]
        bscope = rec["boundary_scope"]
        key = tuple(int(assignment[v]) for v in bscope)
        row = rec["witness_by_boundary"].get(key)
        if row is None:
            return {"ok": False, "reason": "BOUNDARY_TUPLE_MISSING_FROM_TARGET_PORTFOLIO", "factor_id": factor["id"], "key": list(key)}
        for v, bit in zip(factor["scope"], row):
            bit = int(bit)
            if v in assignment and assignment[v] != bit:
                return {"ok": False, "reason": "TARGET_PORTFOLIO_RECONSTRUCTION_CONFLICT", "factor_id": factor["id"], "variable": int(v)}
            assignment[int(v)] = bit
        chosen_rows.append({"factor_id": factor["id"], "sorted_row": list(row)})

    verified = guarded.verify_original_assignment(ready["canonical"], assignment)
    return {"ok": verified, "reason": "ORIGINAL_RELATION_REPLAY" if verified else "ORIGINAL_RELATION_REPLAY_FAILED", "assignment": assignment, "chosen_rows": chosen_rows}


def build(raw: dict, proposal_override: dict | None = None) -> dict:
    predecessor = cc_v11.explain(raw)
    if predecessor.get("status") != "OPEN_COMMON_CORE_FILTERED_BUCKET_STILL_OVER_L2":
        return {"status": "OUT_OF_SCOPE_PREDECESSOR_NOT_STICKY_OPEN", "predecessor_status": predecessor.get("status")}

    ready = cc_v11.first_failed_original_bucket_v11(raw)
    if ready.get("status") != "READY":
        return {"status": ready.get("status", "OUT_OF_SCOPE_PREPARE_FAILURE")}
    canonical = ready["canonical"]
    core = list(ready["common_core"])
    sf = cc_v1.support_and_filter(canonical, ready["bucket"], core)
    common = sorted(sf["common"])
    if len(common) != 1:
        return {
            "status": "OPEN_NONUNIQUE_COMMON_CORE_SUPPORT",
            "common_support_size": len(common),
            "bucket_cartesian_combinations_enumerated": 0,
        }
    state = tuple(int(x) for x in common[0])

    bucket_ids = [f["id"] for f in ready["bucket"]]
    target_ids = _target_factor_ids(ready)
    if bucket_ids != target_ids:
        return {
            "status": "OPEN_INCOMPLETE_TARGET_COMPONENT_COVERAGE",
            "bucket_factor_ids": bucket_ids,
            "target_factor_ids": target_ids,
            "bucket_cartesian_combinations_enumerated": 0,
        }

    residual_scopes = _residual_scopes(ready["bucket"], core)
    couplings = _cross_couplings(residual_scopes)
    if couplings:
        return {
            "status": "OPEN_RESIDUAL_CROSS_COUPLING",
            "residual_scopes": residual_scopes,
            "cross_couplings": couplings,
            "bucket_cartesian_combinations_enumerated": 0,
        }

    proposal = proposal_override or proposal_record(canonical, ready, state, residual_scopes)
    if not verify_proposal(canonical, ready, state, residual_scopes, proposal):
        return {"status": "REJECT_TAMPERED_PROVENANCE"}

    portfolio = _build_portfolio(ready, state)
    if portfolio["status"] != "ADMIT_FACTORIZED_TARGET_BOUNDARY_PORTFOLIO":
        return portfolio

    transformed_raw = _transformed_raw(ready, portfolio)
    transformed = canonicalize_raw(transformed_raw)
    transformed_components = parent_support.constraint_components_after_cut(transformed, list(ready["cut"]))
    handoff = guarded.run_guarded_elimination(transformed, list(ready["cut"]), transformed_components)

    receipt = {
        "failed_variable": int(ready["failed_variable"]),
        "common_core": core,
        "unique_common_state": list(state),
        "common_support_size": 1,
        "predecessor_filtered_product": predecessor.get("carrier", {}).get("receipt", {}).get("filtered_bucket_product"),
        "target_factor_count": len(ready["bucket"]),
        "residual_scopes": residual_scopes,
        "residual_cross_couplings": 0,
        "portfolio_records": portfolio["metrics"]["portfolio_records"],
        "portfolio_boundary_rows": portfolio["metrics"]["total_boundary_rows_stored"],
        "target_cartesian_products_materialized": 0,
        "target_bucket_combinations_enumerated": 0,
        "budget_raised": False,
        "alternative_orders": 0,
        "generic_transfer_calls": 0,
        "external_solver_calls": 0,
        "transformed_constraint_count": len(transformed["constraints"]),
        "transformed_handoff_terminal": handoff.get("status"),
    }

    if handoff.get("status") == "EXACT_UNSAT_BY_COMPLETE_GUARDED_ELIMINATION":
        return {
            "status": "EXACT_UNSAT_BY_UNIQUE_CORE_CONDITIONED_FACTORIZED_BOUNDARY_HANDOFF",
            "proposal": proposal,
            "portfolio": portfolio["portfolio"],
            "receipt": receipt,
            "witness": None,
            "witness_verified": True,
        }
    if handoff.get("status") != "ADMIT_EXACT_GUARDED_BOUNDED_OUTPUT_ELIMINATION":
        return {
            "status": "OPEN_TRANSFORMED_FACTORIZED_HANDOFF",
            "proposal": proposal,
            "portfolio": portfolio["portfolio"],
            "receipt": receipt,
            "handoff": {k: v for k, v in handoff.items() if k != "records_internal"},
        }

    transformed_assignment = {int(k): int(v) for k, v in handoff["witness"]["assignment"].items()}
    reconstruction = _reconstruct_original(ready, portfolio, state, transformed_assignment)
    receipt["original_witness_verified"] = bool(reconstruction["ok"])
    if not reconstruction["ok"]:
        return {
            "status": "OPEN_ORIGINAL_WITNESS_REPLAY_FAILURE",
            "proposal": proposal,
            "portfolio": portfolio["portfolio"],
            "receipt": receipt,
            "reconstruction": reconstruction,
        }
    return {
        "status": "ADMIT_EXACT_UNIQUE_CORE_CONDITIONED_FACTORIZED_PAYLOAD_PORTFOLIO",
        "proposal": proposal,
        "portfolio": portfolio["portfolio"],
        "receipt": receipt,
        "witness": {str(v): int(reconstruction["assignment"][v]) for v in sorted(reconstruction["assignment"])},
        "witness_verified": True,
        "reconstruction_rows": reconstruction["chosen_rows"],
    }


def explain(raw: dict) -> dict:
    guard = source_guard()
    if not guard["ok"]:
        return {"artifact_id": ARTIFACT_ID, "status": "HALT_SOURCE_GUARD", "source_guard": guard, "scientific_firewall": firewall()}
    try:
        canonicalize_raw(raw)
    except RawBasisInputError as exc:
        return {"artifact_id": ARTIFACT_ID, "authority": AUTHORITY, "status": "REJECT_RAW_INPUT", "reason": str(exc), "source_guard": guard, "scientific_firewall": firewall()}
    carrier = build(raw)
    return {"artifact_id": ARTIFACT_ID, "authority": AUTHORITY, "status": carrier["status"], "source_guard": guard, "carrier": carrier, "scientific_firewall": firewall()}


def residual_cross_coupling_control() -> dict:
    raw = cc_v1.filtered_still_overbudget_control()
    sticky0 = next(r for r in raw["constraints"] if r["id"] == "sticky_0")
    sticky1 = next(r for r in raw["constraints"] if r["id"] == "sticky_1")
    shared_payload = sticky0["scope"][-2]
    sticky1["scope"][-2] = shared_payload
    return raw


def multiple_common_core_states_control() -> dict:
    raw = cc_v1.filtered_still_overbudget_control()
    y1 = pair_v1._bits(19, 20)
    left_third = next(r for r in raw["constraints"] if r["id"] == "left_third")
    left_third["allowed"].append(y1 + [0])
    for rel in raw["constraints"]:
        if rel["id"].startswith("sticky_"):
            rel["allowed"].extend(y1 + [a, b] for a, b in [(0, 0), (0, 1), (1, 0), (1, 1)])
    return raw


def incomplete_target_coverage_control() -> dict:
    raw = cc_v1.filtered_still_overbudget_control()
    p = max(raw["variables"]) + 1
    raw["variables"].append(p)
    raw["constraints"].insert(-1, {"id": "nonbucket_same_component", "scope": [21, p], "allowed": [[0, 0], [1, 1]]})
    return raw


def injected_hint_control() -> dict:
    raw = cc_v1.filtered_still_overbudget_control()
    raw["factorized_payload"] = "TRUSTED"
    return raw


def tampered_control() -> dict:
    raw = cc_v1.filtered_still_overbudget_control()
    ready = cc_v11.first_failed_original_bucket_v11(raw)
    sf = cc_v1.support_and_filter(ready["canonical"], ready["bucket"], ready["common_core"])
    state = tuple(sorted(sf["common"])[0])
    residual = _residual_scopes(ready["bucket"], ready["common_core"])
    proposal = proposal_record(ready["canonical"], ready, state, residual)
    proposal["residual_scopes"] = list(reversed(proposal["residual_scopes"]))
    return build(raw, proposal)


def main() -> None:
    out = {
        "artifact_id": ARTIFACT_ID,
        "authority": AUTHORITY,
        "positive_sticky": explain(cc_v1.filtered_still_overbudget_control()),
        "negative_cross_coupling": explain(residual_cross_coupling_control()),
        "negative_multiple_core": explain(multiple_common_core_states_control()),
        "negative_incomplete_coverage": explain(incomplete_target_coverage_control()),
        "negative_hint": explain(injected_hint_control()),
        "negative_tamper": tampered_control(),
        "scientific_firewall": firewall(),
    }
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
