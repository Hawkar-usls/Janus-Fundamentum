from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from research.tools.apma_unseen_basis.raw_relation_basis import canonicalize_raw, RawBasisInputError
from research.tools.apma_bucket_common_core import common_core_semijoin_prefilter as cc_v1
from research.tools.apma_bucket_common_core import common_core_semijoin_prefilter_v1_1 as cc_v11
from research.tools.apma_bucket_residual_le2 import residual_le2_factorized_payload as v36
from research.tools.apma_guarded_elimination import guarded_bounded_output_elimination as guarded
from research.tools.apma_cut_support_carrier import cut_support_carrier as parent_support

ARTIFACT_ID = "JANUS-TRUMP-BICAMERAL-BUCKET-UNIQUE-CORE-RESIDUAL-SINGLE-VARIABLE-SEPARATOR-FACTORIZED-PAYLOAD-CANDIDATE-2026-09-15-v1.0"
AUTHORITY = "CANDIDATE_IMPLEMENTATION__NO_SCIENTIFIC_PROMOTION"
PREREG = Path("research/TRUMP_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_SINGLE_VARIABLE_SEPARATOR_FACTORIZED_PAYLOAD_PREREGISTRATION_2026-09-15.json")
PREREG_BLOB = "e1746da233ad931b1d240ee73290d292a7b6a5a5"
PARENT_STATE = Path("registry/TRUMP_CURRENT_STATE_2026-09-15_v3.7.json")
PARENT_STATE_BLOB = "78dbb314746cbf9f7d24d0906ccb4061d947028c"
V36 = Path("research/tools/apma_bucket_residual_le2/residual_le2_factorized_payload.py")
V36_BLOB = "8c0c2802ccf8bf9b67b80cedb5b26797cd78d1c8"


def root() -> Path:
    return Path(__file__).resolve().parents[3]


def blob(path: Path) -> str:
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
        "prereg_blob": blob(r / PREREG) == PREREG_BLOB,
        "prereg_frozen": p.get("status") == "FROZEN_BEFORE_CANDIDATE_IMPLEMENTATION",
        "gate_name": p.get("frozen_gate") == "TRUMP_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_SINGLE_VARIABLE_SEPARATOR_FACTORIZED_PAYLOAD_FALSIFIER_GATE",
        "parent_state_blob": blob(r / PARENT_STATE) == PARENT_STATE_BLOB,
        "v36_candidate_blob": blob(r / V36) == V36_BLOB,
    }
    return {"ok": all(checks.values()), "checks": checks}


def firewall() -> dict:
    return {
        "P_VS_NP": "OPEN",
        "GENERAL_SAT_IN_P": "NOT_PROVED",
        "CONNECTED_MIXED_CORE_SOLVED": "NO",
        "GENERAL_PARTIAL_OVERLAP_FACTORIZATION": "NOT_PROVED",
        "GENERAL_RESIDUAL_SEPARATOR_TRACTABILITY": "NOT_PROVED",
        "GENERAL_BUCKET_ELIMINATION_POLYNOMIAL": "NOT_PROVED",
        "GLOBAL_APMA_FRONTIER_ADVANCE": "NONE_PENDING_HQ_REVIEW",
        "SCOPE": "UNIQUE_COMMON_CORE__EXACTLY_ONE_RESIDUAL_GT2_COMPONENT__RAW_DERIVED_SINGLE_BOOLEAN_VARIABLE_SEPARATOR__BOTH_BRANCHES_REDUCE_TO_SEALED_LE2_CARRIERS",
    }


def _projection(factor: dict, variables: list[int], row: tuple[int, ...]) -> tuple[int, ...]:
    pos = {int(v): i for i, v in enumerate(factor["scope"])}
    return tuple(int(row[pos[int(v)]]) for v in variables)


def base_prepare(raw: dict) -> dict:
    predecessor = cc_v11.explain(raw)
    if predecessor.get("status") != "OPEN_COMMON_CORE_FILTERED_BUCKET_STILL_OVER_L2":
        return {"status": "OUT_OF_SCOPE_PREDECESSOR_NOT_STICKY_OPEN", "predecessor_status": predecessor.get("status")}
    ready = cc_v11.first_failed_original_bucket_v11(raw)
    if ready.get("status") != "READY":
        return {"status": ready.get("status", "OUT_OF_SCOPE_READY_FAILURE")}
    canonical = ready["canonical"]
    core = [int(v) for v in ready["common_core"]]
    supports = [{_projection(f, core, tuple(row)) for row in f["rows"]} for f in ready["bucket"]]
    common = set.intersection(*supports) if supports else set()
    if len(common) != 1:
        return {"status": "OPEN_NONUNIQUE_COMMON_CORE_SUPPORT", "common_support_size": len(common), "global_residual_cartesian_products_materialized": 0}
    bucket_ids = [str(f["id"]) for f in ready["bucket"]]
    target_ids = [f"orig:{int(gi)}" for gi in ready["component"]]
    if bucket_ids != target_ids:
        return {"status": "OPEN_INCOMPLETE_TARGET_COMPONENT_COVERAGE", "bucket_factor_ids": bucket_ids, "target_factor_ids": target_ids}
    state = tuple(int(x) for x in sorted(common)[0])
    conditioned = []
    for f in ready["bucket"]:
        rows = [tuple(int(x) for x in row) for row in f["rows"] if _projection(f, core, tuple(row)) == state]
        if not rows:
            return {"status": "EXACT_UNSAT_BY_EMPTY_CONDITIONED_FACTOR", "factor_id": f["id"]}
        conditioned.append({**f, "rows": rows})
    components = v36.residual_components(conditioned, core)
    gt2 = [c for c in components if len(c) > 2]
    if len(gt2) == 0:
        return {"status": "OUT_OF_SCOPE_RESIDUAL_LE2_ALREADY_SOLVED", "residual_components": components}
    if len(gt2) != 1 or any(len(c) > 2 for c in components if c is not gt2[0]):
        return {"status": "OPEN_MULTIPLE_RESIDUAL_GT2_COMPONENTS", "residual_components": components, "global_residual_cartesian_products_materialized": 0}
    return {
        "status": "READY",
        "predecessor": predecessor,
        "ready": ready,
        "canonical": canonical,
        "core": core,
        "state": state,
        "conditioned": conditioned,
        "residual_components": components,
        "target_gt2": list(gt2[0]),
    }


def _residual_scope(factor: dict, core: list[int]) -> set[int]:
    C = set(int(v) for v in core)
    return {int(v) for v in factor["scope"] if int(v) not in C}


def discover_separator(prep: dict) -> dict:
    target = [prep["conditioned"][i] for i in prep["target_gt2"]]
    variables = sorted(set().union(*(_residual_scope(f, prep["core"]) for f in target)))
    candidates = []
    for v in variables:
        comps = v36.residual_components(target, list(prep["core"]) + [int(v)])
        if comps and max(len(c) for c in comps) <= 2 and len(comps) >= 2:
            candidates.append({"variable": int(v), "post_removal_components": [list(c) for c in comps]})
    if not candidates:
        return {"status": "OPEN_NO_RESIDUAL_SINGLE_VARIABLE_SEPARATOR", "candidate_variables_examined": len(variables), "three_plus_join_chains_materialized": 0, "global_residual_cartesian_products_materialized": 0}
    return {"status": "ADMIT_SEPARATOR_PROPOSAL", "separator": candidates[0]["variable"], "post_removal_components": candidates[0]["post_removal_components"], "all_valid_separators": [x["variable"] for x in candidates], "candidate_variables_examined": len(variables)}


def proposal_record(prep: dict, discovery: dict) -> dict:
    body = {
        "kind": "RAW_DERIVED_RESIDUAL_SINGLE_BOOLEAN_VARIABLE_SEPARATOR_TO_SEALED_LE2_BRANCH_PORTFOLIOS",
        "raw_object_sha256": sha256_obj(prep["canonical"]),
        "failed_variable": int(prep["ready"]["failed_variable"]),
        "target_component": list(prep["ready"]["component"]),
        "common_core": list(prep["core"]),
        "unique_common_state": list(prep["state"]),
        "gt2_component": list(prep["target_gt2"]),
        "separator_variable": int(discovery["separator"]),
        "branch_values": [0, 1],
        "post_removal_components": [list(c) for c in discovery["post_removal_components"]],
        "truth_authority": False,
        "proof_authority": False,
        "automatic_promotion": False,
    }
    body["proposal_sha256"] = sha256_obj(body)
    return body


def verify_proposal(prep: dict, discovery: dict, proposal: dict) -> bool:
    body = dict(proposal)
    claimed = body.pop("proposal_sha256", None)
    return isinstance(claimed, str) and sha256_obj(body) == claimed and proposal == proposal_record(prep, discovery)


def _restrict_rows(factor: dict, separator: int, bit: int) -> list[tuple[int, ...]]:
    if separator not in [int(v) for v in factor["scope"]]:
        return [tuple(int(x) for x in row) for row in factor["rows"]]
    pos = {int(v): i for i, v in enumerate(factor["scope"])}[int(separator)]
    return [tuple(int(x) for x in row) for row in factor["rows"] if int(row[pos]) == int(bit)]


def branch_prepare(prep: dict, separator: int, bit: int) -> dict:
    conditioned = []
    for f in prep["conditioned"]:
        rows = _restrict_rows(f, separator, bit)
        if not rows:
            return {"status": "BRANCH_EXACT_UNSAT_EMPTY_FACTOR", "bit": int(bit), "factor_id": f["id"], "residual_components": [], "three_plus_join_chains_materialized": 0}
        conditioned.append({**f, "rows": rows})
    core2 = list(prep["core"]) + [int(separator)]
    state2 = tuple(prep["state"]) + (int(bit),)
    components = v36.residual_components(conditioned, core2)
    if any(len(c) > 2 for c in components):
        return {"status": "BRANCH_OPEN_RESIDUAL_COMPONENT_GT2", "bit": int(bit), "residual_components": components, "three_plus_join_chains_materialized": 0, "global_residual_cartesian_products_materialized": 0}
    return {
        "status": "READY",
        "predecessor": prep["predecessor"],
        "ready": prep["ready"],
        "canonical": prep["canonical"],
        "core": core2,
        "state": state2,
        "conditioned": conditioned,
        "residual_components": components,
        "separator": int(separator),
        "separator_bit": int(bit),
    }


def solve_branch(prep: dict, separator: int, bit: int) -> dict:
    bp = branch_prepare(prep, separator, bit)
    if bp.get("status") == "BRANCH_EXACT_UNSAT_EMPTY_FACTOR":
        return {**bp, "terminal_class": "EXACT_UNSAT", "pair_join_count": 0, "global_residual_cartesian_products_materialized": 0}
    if bp.get("status") != "READY":
        return {**bp, "terminal_class": "OPEN"}
    portfolio = v36.build_portfolio(bp)
    if portfolio.get("status") == "EXACT_UNSAT_BY_EMPTY_RESIDUAL_PAIR_JOIN":
        return {"status": "BRANCH_EXACT_UNSAT_EMPTY_PAIR_JOIN", "terminal_class": "EXACT_UNSAT", "bit": int(bit), "residual_components": bp["residual_components"], "pair_join_count": int(portfolio.get("pair_join_count", 1)), "global_residual_cartesian_products_materialized": 0}
    if portfolio.get("status") != "ADMIT_RESIDUAL_LE2_PORTFOLIO":
        return {"status": "BRANCH_OPEN_PORTFOLIO", "terminal_class": "OPEN", "bit": int(bit), "portfolio_status": portfolio.get("status"), "residual_components": bp["residual_components"]}
    transformed = canonicalize_raw(v36._transformed_raw(bp, portfolio))
    transformed_components = parent_support.constraint_components_after_cut(transformed, list(bp["ready"]["cut"]))
    handoff = guarded.run_guarded_elimination(transformed, list(bp["ready"]["cut"]), transformed_components)
    metrics = {
        "bit": int(bit),
        "residual_components": [list(c) for c in bp["residual_components"]],
        "residual_component_sizes": [len(c) for c in bp["residual_components"]],
        "pair_join_count": int(portfolio["metrics"]["pair_join_count"]),
        "pair_row_comparisons": int(portfolio["metrics"]["pair_row_comparisons"]),
        "portfolio_records": int(portfolio["metrics"]["residual_component_count"]),
        "portfolio_boundary_rows": int(portfolio["metrics"]["total_boundary_rows_stored"]),
        "three_plus_join_chains_materialized": 0,
        "global_residual_cartesian_products_materialized": 0,
        "handoff_terminal": handoff.get("status"),
    }
    if handoff.get("status") == "EXACT_UNSAT_BY_COMPLETE_GUARDED_ELIMINATION":
        return {"status": "BRANCH_EXACT_UNSAT_BY_HANDOFF", "terminal_class": "EXACT_UNSAT", **metrics}
    if handoff.get("status") != "ADMIT_EXACT_GUARDED_BOUNDED_OUTPUT_ELIMINATION":
        return {"status": "BRANCH_OPEN_HANDOFF", "terminal_class": "OPEN", **metrics}
    transformed_assignment = {int(k): int(v) for k, v in handoff["witness"]["assignment"].items()}
    reconstruction = v36._reconstruct(bp, portfolio, transformed_assignment)
    if not reconstruction.get("ok"):
        return {"status": "BRANCH_OPEN_ORIGINAL_WITNESS_REPLAY_FAILURE", "terminal_class": "OPEN", "reconstruction_reason": reconstruction.get("reason"), **metrics}
    return {
        "status": "BRANCH_EXACT_SAT",
        "terminal_class": "EXACT_SAT",
        "witness": {str(v): int(reconstruction["assignment"][v]) for v in sorted(reconstruction["assignment"])},
        "witness_verified": True,
        "reconstruction_rows": reconstruction["chosen_rows"],
        **metrics,
    }


def build(raw: dict, proposal_override: dict | None = None) -> dict:
    prep = base_prepare(raw)
    if prep.get("status") != "READY":
        return prep
    discovery = discover_separator(prep)
    if discovery.get("status") != "ADMIT_SEPARATOR_PROPOSAL":
        return discovery
    proposal = proposal_override or proposal_record(prep, discovery)
    if not verify_proposal(prep, discovery, proposal):
        return {"status": "REJECT_TAMPERED_PROVENANCE"}
    separator = int(discovery["separator"])
    branches = [solve_branch(prep, separator, bit) for bit in (0, 1)]
    sat = [b for b in branches if b.get("terminal_class") == "EXACT_SAT"]
    exact_unsat = [b for b in branches if b.get("terminal_class") == "EXACT_UNSAT"]
    receipt = {
        "separator_variable": separator,
        "candidate_variables_examined": int(discovery["candidate_variables_examined"]),
        "all_valid_separators": list(discovery["all_valid_separators"]),
        "branch_count": 2,
        "branch_terminals": [b.get("status") for b in branches],
        "branch_classes": [b.get("terminal_class") for b in branches],
        "three_plus_join_chains_materialized": sum(int(b.get("three_plus_join_chains_materialized", 0)) for b in branches),
        "global_residual_cartesian_products_materialized": sum(int(b.get("global_residual_cartesian_products_materialized", 0)) for b in branches),
        "pair_join_count": sum(int(b.get("pair_join_count", 0)) for b in branches),
        "budget_raised": False,
        "alternative_orders": 0,
        "external_solver_calls": 0,
        "generic_transfer_calls": 0,
    }
    if sat:
        chosen = sorted(sat, key=lambda b: int(b["bit"]))[0]
        receipt["selected_satisfying_branch"] = int(chosen["bit"])
        return {"status": "ADMIT_EXACT_UNIQUE_CORE_RESIDUAL_SINGLE_VARIABLE_SEPARATOR_FACTORIZED_PAYLOAD", "proposal": proposal, "discovery": discovery, "branches": branches, "receipt": receipt, "witness": chosen["witness"], "witness_verified": True}
    if len(exact_unsat) == 2:
        return {"status": "EXACT_UNSAT_BY_RESIDUAL_SINGLE_VARIABLE_SEPARATOR_BRANCHES", "proposal": proposal, "discovery": discovery, "branches": branches, "receipt": receipt, "witness": None, "witness_verified": True}
    return {"status": "OPEN_RESIDUAL_SEPARATOR_BRANCH_UNRESOLVED", "proposal": proposal, "discovery": discovery, "branches": branches, "receipt": receipt}


def explain(raw: dict) -> dict:
    g = source_guard()
    if not g["ok"]:
        return {"artifact_id": ARTIFACT_ID, "status": "HALT_SOURCE_GUARD", "source_guard": g, "scientific_firewall": firewall()}
    try:
        canonicalize_raw(raw)
    except RawBasisInputError as exc:
        return {"artifact_id": ARTIFACT_ID, "authority": AUTHORITY, "status": "REJECT_RAW_INPUT", "reason": str(exc), "source_guard": g, "scientific_firewall": firewall()}
    carrier = build(raw)
    return {"artifact_id": ARTIFACT_ID, "authority": AUTHORITY, "status": carrier.get("status"), "source_guard": g, "carrier": carrier, "scientific_firewall": firewall()}


def positive_control() -> dict:
    return v36.residual_component_gt2_control()


def one_branch_unsat_one_sat_control() -> dict:
    raw = positive_control()
    s0 = next(r for r in raw["constraints"] if r["id"] == "sticky_0")
    sep = int(s0["scope"][-2])
    pos = s0["scope"].index(sep)
    s0["allowed"] = [row for row in s0["allowed"] if int(row[pos]) == 0]
    return raw


def both_branches_unsat_control() -> dict:
    raw = positive_control()
    s0 = next(r for r in raw["constraints"] if r["id"] == "sticky_0")
    s1 = next(r for r in raw["constraints"] if r["id"] == "sticky_1")
    sep = int(s0["scope"][-2])
    p0 = s0["scope"].index(sep)
    p1 = s1["scope"].index(sep)
    s0["allowed"] = [row for row in s0["allowed"] if int(row[p0]) == 0]
    s1["allowed"] = [row for row in s1["allowed"] if int(row[p1]) == 1]
    return raw


def no_single_variable_articulation_control() -> dict:
    raw = cc_v1.filtered_still_overbudget_control()
    s0 = next(r for r in raw["constraints"] if r["id"] == "sticky_0")
    s1 = next(r for r in raw["constraints"] if r["id"] == "sticky_1")
    s2 = next(r for r in raw["constraints"] if r["id"] == "sticky_2")
    a = int(s0["scope"][-2])
    b = int(s0["scope"][-1])
    c = int(s1["scope"][-1])
    s1["scope"][-2] = b
    s2["scope"][-2] = c
    s2["scope"][-1] = a
    return raw


def multiple_common_core_states_control() -> dict:
    return v36.multiple_common_core_states_control()


def injected_hint_control() -> dict:
    raw = positive_control()
    raw["residual_separator_hint"] = 47
    return raw


def tampered_control() -> dict:
    raw = positive_control()
    prep = base_prepare(raw)
    discovery = discover_separator(prep)
    proposal = proposal_record(prep, discovery)
    proposal["separator_variable"] = int(discovery["separator"]) + 1
    return build(raw, proposal)


def invalid_separator_branch_guard_control() -> dict:
    prep = base_prepare(positive_control())
    discovery = discover_separator(prep)
    sep = int(discovery["separator"])
    residual_vars = sorted(set().union(*(_residual_scope(prep["conditioned"][i], prep["core"]) for i in prep["target_gt2"])))
    invalid = next(v for v in residual_vars if v != sep)
    return solve_branch(prep, invalid, 0)


def main() -> None:
    out = {
        "artifact_id": ARTIFACT_ID,
        "authority": AUTHORITY,
        "positive": explain(positive_control()),
        "one_branch_unsat_one_sat": explain(one_branch_unsat_one_sat_control()),
        "both_branches_unsat": explain(both_branches_unsat_control()),
        "no_single_variable_articulation": explain(no_single_variable_articulation_control()),
        "multiple_common_core": explain(multiple_common_core_states_control()),
        "hint": explain(injected_hint_control()),
        "tamper": tampered_control(),
        "invalid_separator_branch_guard": invalid_separator_branch_guard_control(),
        "scientific_firewall": firewall(),
    }
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
