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
PREREG_BLOB = "70bf83eeb5b603832cdda5770c5683efcac8e4d3"
PARENT_STATE = Path("registry/TRUMP_CURRENT_STATE_2026-09-15_v3.7.json")
PARENT_STATE_BLOB = "78dbb314746cbf9f7d24d0906ccb4061d947028c"
V36 = Path("research/tools/apma_bucket_residual_le2/residual_le2_factorized_payload.py")
V36_BLOB = "8c0c2802ccf8bf9b67b80cedb5b26797cd78d1c8"
OLD_SINGLE = Path("research/tools/apma_bicameral_explanation/bicameral_explainer.py")
OLD_SINGLE_BLOB = "bc3a9e0040b255cd4c976512a619f90644434d45"


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
        "prereg_gate": p.get("frozen_gate") == "TRUMP_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_SINGLE_VARIABLE_SEPARATOR_FACTORIZED_PAYLOAD_FALSIFIER_GATE",
        "parent_state_blob": git_blob_sha1(r / PARENT_STATE) == PARENT_STATE_BLOB,
        "v36_blob": git_blob_sha1(r / V36) == V36_BLOB,
        "old_single_blob": git_blob_sha1(r / OLD_SINGLE) == OLD_SINGLE_BLOB,
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
        "SCOPE": "UNIQUE_COMMON_CORE_WITH_RAW_DERIVED_SINGLE_BOOLEAN_RESIDUAL_SEPARATOR_WHOSE_TWO_BRANCHES_REDUCE_TO_COMPONENT_SIZE_AT_MOST_TWO",
    }


def _prepare(raw: dict) -> dict:
    predecessor = cc_v11.explain(raw)
    if predecessor.get("status") != "OPEN_COMMON_CORE_FILTERED_BUCKET_STILL_OVER_L2":
        return {"status": "OUT_OF_SCOPE_PREDECESSOR_NOT_STICKY_OPEN", "predecessor_status": predecessor.get("status")}
    ready = cc_v11.first_failed_original_bucket_v11(raw)
    if ready.get("status") != "READY":
        return {"status": ready.get("status", "OUT_OF_SCOPE_READY_FAILURE")}
    canonical = ready["canonical"]
    core = [int(v) for v in ready["common_core"]]
    sf = cc_v1.support_and_filter(canonical, ready["bucket"], core)
    common = sorted(sf["common"])
    if len(common) != 1:
        return {"status": "OPEN_NONUNIQUE_COMMON_CORE_SUPPORT", "common_support_size": len(common), "separator_branches_enumerated": 0}
    bucket_ids = [str(f["id"]) for f in ready["bucket"]]
    target_ids = [f"orig:{int(gi)}" for gi in ready["component"]]
    if bucket_ids != target_ids:
        return {"status": "OPEN_INCOMPLETE_TARGET_COMPONENT_COVERAGE", "separator_branches_enumerated": 0}
    state = tuple(int(x) for x in common[0])
    conditioned = []
    for f in ready["bucket"]:
        rows = [tuple(int(x) for x in row) for row in f["rows"] if cc_v1._projection(f, core, row) == state]
        if not rows:
            return {"status": "EXACT_UNSAT_BY_EMPTY_CONDITIONED_FACTOR", "factor_id": f["id"]}
        conditioned.append({**f, "rows": rows})
    components = v36.residual_components(conditioned, core)
    if not any(len(c) >= 3 for c in components):
        return {"status": "OUT_OF_SCOPE_NO_RESIDUAL_COMPONENT_GT2", "residual_components": components}
    return {
        "status": "READY",
        "predecessor": predecessor,
        "ready": ready,
        "canonical": canonical,
        "core": core,
        "state": state,
        "conditioned": conditioned,
        "residual_components": components,
    }


def _residual_scope(f: dict, core: list[int]) -> list[int]:
    C = set(core)
    return [int(v) for v in f["scope"] if int(v) not in C]


def _components_from_scopes(scopes: list[set[int]]) -> list[list[int]]:
    n = len(scopes)
    parent = list(range(n))
    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            if ra > rb:
                ra, rb = rb, ra
            parent[rb] = ra
    for i in range(n):
        for j in range(i + 1, n):
            if scopes[i] & scopes[j]:
                union(i, j)
    groups: dict[int, list[int]] = {}
    for i in range(n):
        groups.setdefault(find(i), []).append(i)
    return sorted((sorted(xs) for xs in groups.values()), key=lambda xs: (xs[0], len(xs), xs))


def _articulation_variables(factors: list[dict], core: list[int]) -> list[int]:
    scopes = [set(_residual_scope(f, core)) for f in factors]
    base = _components_from_scopes(scopes)
    base_count = len(base)
    vars_ = sorted(set().union(*scopes) if scopes else set())
    out = []
    for v in vars_:
        reduced = [set(s) - {v} for s in scopes]
        if len(_components_from_scopes(reduced)) > base_count:
            out.append(v)
    return out


def _restrict_factor(f: dict, variable: int, value: int) -> tuple[dict | None, dict]:
    scope = [int(v) for v in f["scope"]]
    rows = [tuple(int(x) for x in row) for row in f["rows"]]
    if variable not in scope:
        origin = {row: row for row in rows}
        return {**f, "scope": scope, "rows": rows, "_origin_scope": scope, "_origin_witness": origin}, {"factor_id": f["id"], "touched": False, "surviving_rows": len(rows)}
    pos = scope.index(variable)
    new_scope = scope[:pos] + scope[pos + 1:]
    witness: dict[tuple[int, ...], tuple[int, ...]] = {}
    for row in rows:
        if int(row[pos]) != int(value):
            continue
        reduced = row[:pos] + row[pos + 1:]
        witness.setdefault(reduced, row)
    new_rows = sorted(witness)
    if not new_rows:
        return None, {"factor_id": f["id"], "touched": True, "surviving_rows": 0}
    return {
        **f,
        "scope": new_scope,
        "rows": new_rows,
        "_origin_scope": scope,
        "_origin_witness": witness,
        "_separator_variable": variable,
        "_separator_value": value,
    }, {"factor_id": f["id"], "touched": True, "surviving_rows": len(new_rows)}


def _branch_structure(prep: dict, variable: int, value: int) -> dict:
    factors = []
    restrictions = []
    for f in prep["conditioned"]:
        rf, rec = _restrict_factor(f, variable, value)
        restrictions.append(rec)
        if rf is None:
            return {
                "status": "EXACT_UNSAT_BY_EMPTY_SEPARATOR_RESTRICTION",
                "value": value,
                "factors": None,
                "residual_components": [],
                "restriction_receipt": restrictions,
            }
        factors.append(rf)
    components = v36.residual_components(factors, prep["core"])
    if any(len(c) > 2 for c in components):
        return {
            "status": "OPEN_BRANCH_RESIDUAL_COMPONENT_GT2",
            "value": value,
            "factors": factors,
            "residual_components": components,
            "restriction_receipt": restrictions,
        }
    return {
        "status": "READY_BRANCH_LE2",
        "value": value,
        "factors": factors,
        "residual_components": components,
        "restriction_receipt": restrictions,
    }


def separator_candidates(prep: dict) -> list[dict]:
    out = []
    for v in _articulation_variables(prep["conditioned"], prep["core"]):
        branches = [_branch_structure(prep, v, b) for b in (0, 1)]
        structural_ok = all(x["status"] in {"READY_BRANCH_LE2", "EXACT_UNSAT_BY_EMPTY_SEPARATOR_RESTRICTION"} for x in branches)
        out.append({
            "variable": int(v),
            "branch_statuses": [x["status"] for x in branches],
            "structural_ok": structural_ok,
        })
    return out


def proposal_record(prep: dict, separator: int, candidates: list[dict]) -> dict:
    body = {
        "kind": "UNIQUE_CORE_RESIDUAL_SINGLE_VARIABLE_SEPARATOR_TO_LE2_BRANCH_PORTFOLIOS",
        "raw_object_sha256": sha256_obj(prep["canonical"]),
        "failed_variable": int(prep["ready"]["failed_variable"]),
        "common_core": list(prep["core"]),
        "unique_common_state": list(prep["state"]),
        "separator_variable": int(separator),
        "branch_values": [0, 1],
        "candidate_separator_variables": [int(x["variable"]) for x in candidates],
        "truth_authority": False,
        "proof_authority": False,
        "automatic_promotion": False,
    }
    body["proposal_sha256"] = sha256_obj(body)
    return body


def verify_proposal(prep: dict, separator: int, candidates: list[dict], proposal: dict) -> bool:
    expected = proposal_record(prep, separator, candidates)
    body = dict(proposal)
    claimed = body.pop("proposal_sha256", None)
    return isinstance(claimed, str) and sha256_obj(body) == claimed and proposal == expected


def _portfolio_prep(prep: dict, branch: dict) -> dict:
    return {
        "ready": prep["ready"],
        "canonical": prep["canonical"],
        "core": prep["core"],
        "state": prep["state"],
        "conditioned": branch["factors"],
        "residual_components": branch["residual_components"],
    }


def _original_row(factor: dict, restricted_row: tuple[int, ...]) -> tuple[int, ...]:
    witness = factor.get("_origin_witness", {})
    return tuple(int(x) for x in witness.get(tuple(restricted_row), tuple(restricted_row)))


def _reconstruct_original(prep: dict, branch: dict, portfolio: dict, separator: int, value: int, transformed_assignment: dict[int, int]) -> dict:
    assignment = {int(k): int(v) for k, v in transformed_assignment.items()}
    cut = set(int(v) for v in prep["ready"]["cut"])
    target_internal = {
        int(v)
        for gi in prep["ready"]["component"]
        for v in prep["canonical"]["constraints"][gi]["scope"]
        if int(v) not in cut
    }
    for v in target_internal:
        assignment.pop(v, None)
    for v, bit in zip(prep["core"], prep["state"]):
        assignment[int(v)] = int(bit)
    assignment[int(separator)] = int(value)

    chosen_rows = []
    for carrier in portfolio["carriers"]:
        boundary = carrier["boundary_scope"]
        key = tuple(int(assignment[v]) for v in boundary)
        witness = carrier["witness"].get(key)
        if witness is None:
            return {"ok": False, "reason": "BOUNDARY_TUPLE_MISSING_FROM_BRANCH_PORTFOLIO", "boundary": boundary, "key": list(key)}
        restricted_rows = [witness] if len(carrier["factors"]) == 1 else list(witness)
        for factor, rrow in zip(carrier["factors"], restricted_rows):
            orow = _original_row(factor, tuple(rrow))
            oscope = [int(v) for v in factor.get("_origin_scope", factor["scope"])]
            for v, bit in zip(oscope, orow):
                v, bit = int(v), int(bit)
                if v in assignment and assignment[v] != bit:
                    return {"ok": False, "reason": "ORIGINAL_ROW_RECONSTRUCTION_CONFLICT", "factor_id": factor["id"], "variable": v}
                assignment[v] = bit
            chosen_rows.append({"factor_id": factor["id"], "original_sorted_row": list(orow)})
    verified = guarded.verify_original_assignment(prep["canonical"], assignment)
    return {"ok": verified, "reason": "ORIGINAL_RELATION_REPLAY" if verified else "ORIGINAL_RELATION_REPLAY_FAILED", "assignment": assignment, "chosen_rows": chosen_rows}


def _execute_branch(prep: dict, separator: int, value: int) -> dict:
    branch = _branch_structure(prep, separator, value)
    if branch["status"] == "EXACT_UNSAT_BY_EMPTY_SEPARATOR_RESTRICTION":
        return {
            "value": value,
            "status": branch["status"],
            "exact_unsat": True,
            "exact_sat": False,
            "residual_components": [],
            "resource_receipt": {"three_plus_join_chains_materialized": 0, "global_residual_cartesian_products_materialized": 0},
        }
    if branch["status"] != "READY_BRANCH_LE2":
        return {
            "value": value,
            "status": branch["status"],
            "exact_unsat": False,
            "exact_sat": False,
            "residual_components": branch.get("residual_components", []),
            "resource_receipt": {"three_plus_join_chains_materialized": 0, "global_residual_cartesian_products_materialized": 0},
        }
    bprep = _portfolio_prep(prep, branch)
    portfolio = v36.build_portfolio(bprep)
    if portfolio.get("status") == "EXACT_UNSAT_BY_EMPTY_RESIDUAL_PAIR_JOIN":
        return {
            "value": value,
            "status": "EXACT_UNSAT_BY_EMPTY_RESIDUAL_PAIR_JOIN",
            "exact_unsat": True,
            "exact_sat": False,
            "residual_components": branch["residual_components"],
            "resource_receipt": {"three_plus_join_chains_materialized": 0, "global_residual_cartesian_products_materialized": 0},
        }
    if portfolio.get("status") != "ADMIT_RESIDUAL_LE2_PORTFOLIO":
        return {"value": value, "status": portfolio.get("status", "OPEN_BRANCH_PORTFOLIO_FAILURE"), "exact_unsat": False, "exact_sat": False, "residual_components": branch["residual_components"]}

    transformed = canonicalize_raw(v36._transformed_raw(bprep, portfolio))
    transformed_components = parent_support.constraint_components_after_cut(transformed, list(prep["ready"]["cut"]))
    handoff = guarded.run_guarded_elimination(transformed, list(prep["ready"]["cut"]), transformed_components)
    receipt = {
        "value": value,
        "residual_component_sizes": [len(c) for c in branch["residual_components"]],
        "portfolio_records": portfolio["metrics"]["residual_component_count"],
        "pair_join_count": portfolio["metrics"]["pair_join_count"],
        "pair_row_comparisons": portfolio["metrics"]["pair_row_comparisons"],
        "global_residual_cartesian_products_materialized": 0,
        "three_plus_join_chains_materialized": 0,
        "handoff_terminal": handoff.get("status"),
    }
    if handoff.get("status") == "EXACT_UNSAT_BY_COMPLETE_GUARDED_ELIMINATION":
        return {"value": value, "status": "EXACT_UNSAT_BY_SEPARATOR_BRANCH_HANDOFF", "exact_unsat": True, "exact_sat": False, "residual_components": branch["residual_components"], "receipt": receipt}
    if handoff.get("status") != "ADMIT_EXACT_GUARDED_BOUNDED_OUTPUT_ELIMINATION":
        return {"value": value, "status": "OPEN_SEPARATOR_BRANCH_HANDOFF", "exact_unsat": False, "exact_sat": False, "residual_components": branch["residual_components"], "receipt": receipt}
    transformed_assignment = {int(k): int(v) for k, v in handoff["witness"]["assignment"].items()}
    reconstruction = _reconstruct_original(prep, branch, portfolio, separator, value, transformed_assignment)
    receipt["original_witness_verified"] = bool(reconstruction["ok"])
    if not reconstruction["ok"]:
        return {"value": value, "status": "OPEN_ORIGINAL_WITNESS_REPLAY_FAILURE", "exact_unsat": False, "exact_sat": False, "residual_components": branch["residual_components"], "receipt": receipt, "reconstruction": reconstruction}
    return {
        "value": value,
        "status": "ADMIT_EXACT_SEPARATOR_BRANCH_SAT",
        "exact_unsat": False,
        "exact_sat": True,
        "residual_components": branch["residual_components"],
        "receipt": receipt,
        "witness": {str(v): int(reconstruction["assignment"][v]) for v in sorted(reconstruction["assignment"])},
        "witness_verified": True,
        "reconstruction_rows": reconstruction["chosen_rows"],
    }


def build(raw: dict, proposal_override: dict | None = None) -> dict:
    prep = _prepare(raw)
    if prep.get("status") != "READY":
        return prep
    candidates = separator_candidates(prep)
    admissible = [x for x in candidates if x["structural_ok"]]
    if not admissible:
        return {
            "status": "OPEN_NO_ADMISSIBLE_RESIDUAL_SINGLE_VARIABLE_SEPARATOR",
            "separator_candidates": candidates,
            "separator_branches_enumerated": 0,
            "three_plus_join_chains_materialized": 0,
            "global_residual_cartesian_products_materialized": 0,
        }
    separator = int(admissible[0]["variable"])
    proposal = proposal_override or proposal_record(prep, separator, candidates)
    if not verify_proposal(prep, separator, candidates, proposal):
        return {"status": "REJECT_TAMPERED_PROVENANCE"}
    branches = [_execute_branch(prep, separator, b) for b in (0, 1)]
    sat = next((b for b in branches if b.get("exact_sat") and b.get("witness_verified")), None)
    all_unsat = all(bool(b.get("exact_unsat")) for b in branches)
    any_open = any(not b.get("exact_sat") and not b.get("exact_unsat") for b in branches)
    receipt = {
        "separator_variable": separator,
        "branch_values": [0, 1],
        "branch_statuses": [b["status"] for b in branches],
        "separator_candidate_count": len(candidates),
        "selected_separator_is_min_admissible": separator == min(x["variable"] for x in admissible),
        "three_plus_join_chains_materialized": 0,
        "global_residual_cartesian_products_materialized": 0,
        "budget_raised": False,
        "alternative_order_search": 0,
        "generic_transfer_calls": 0,
        "external_solver_calls": 0,
    }
    if sat is not None:
        return {"status": "ADMIT_EXACT_UNIQUE_CORE_RESIDUAL_SINGLE_VARIABLE_SEPARATOR_FACTORIZED_PAYLOAD", "proposal": proposal, "branches": branches, "receipt": receipt, "witness": sat["witness"], "witness_verified": True}
    if all_unsat:
        return {"status": "EXACT_UNSAT_BY_BOTH_SEPARATOR_BRANCHES", "proposal": proposal, "branches": branches, "receipt": receipt, "witness": None, "witness_verified": True}
    return {"status": "OPEN_SEPARATOR_BRANCH_NOT_FULLY_ADMITTED" if any_open else "OPEN_SEPARATOR_UNRESOLVED", "proposal": proposal, "branches": branches, "receipt": receipt}


def explain(raw: dict) -> dict:
    g = source_guard()
    if not g["ok"]:
        return {"artifact_id": ARTIFACT_ID, "status": "HALT_SOURCE_GUARD", "source_guard": g, "scientific_firewall": firewall()}
    try:
        canonicalize_raw(raw)
    except RawBasisInputError as exc:
        return {"artifact_id": ARTIFACT_ID, "authority": AUTHORITY, "status": "REJECT_RAW_INPUT", "reason": str(exc), "source_guard": g, "scientific_firewall": firewall()}
    carrier = build(raw)
    return {"artifact_id": ARTIFACT_ID, "authority": AUTHORITY, "status": carrier["status"], "source_guard": g, "carrier": carrier, "scientific_firewall": firewall()}


def positive_separator_control() -> dict:
    return v36.residual_component_gt2_control()


def one_branch_unsat_one_sat_control() -> dict:
    raw = positive_separator_control()
    s0 = next(r for r in raw["constraints"] if r["id"] == "sticky_0")
    sep = int(s0["scope"][-2])
    pos = s0["scope"].index(sep)
    s0["allowed"] = [row for row in s0["allowed"] if int(row[pos]) == 1]
    return raw


def both_branches_unsat_control() -> dict:
    raw = positive_separator_control()
    s0 = next(r for r in raw["constraints"] if r["id"] == "sticky_0")
    s1 = next(r for r in raw["constraints"] if r["id"] == "sticky_1")
    sep = int(s0["scope"][-2])
    for rel, keep in [(s0, 0), (s1, 1)]:
        pos = rel["scope"].index(sep)
        rel["allowed"] = [row for row in rel["allowed"] if int(row[pos]) == keep]
    return raw


def no_single_variable_articulation_control() -> dict:
    raw = cc_v1.filtered_still_overbudget_control()
    s0 = next(r for r in raw["constraints"] if r["id"] == "sticky_0")
    s1 = next(r for r in raw["constraints"] if r["id"] == "sticky_1")
    s2 = next(r for r in raw["constraints"] if r["id"] == "sticky_2")
    a, b = int(s0["scope"][-2]), int(s0["scope"][-1])
    c = int(s1["scope"][-1])
    s0["scope"][-2:] = [a, b]
    s1["scope"][-2:] = [a, c]
    s2["scope"][-2:] = [b, c]
    return raw


def branch_still_gt2_control() -> dict:
    raw = no_single_variable_articulation_control()
    s0 = next(r for r in raw["constraints"] if r["id"] == "sticky_0")
    s3 = next(r for r in raw["constraints"] if r["id"] == "sticky_3")
    bridge = int(s3["scope"][-2])
    if bridge not in s0["scope"]:
        s0["scope"].append(bridge)
        expanded = []
        for row in s0["allowed"]:
            expanded.append(list(row) + [0])
            expanded.append(list(row) + [1])
        s0["allowed"] = expanded
    return raw


def injected_hint_control() -> dict:
    raw = positive_separator_control()
    raw["residual_separator"] = 47
    return raw


def tampered_control() -> dict:
    raw = positive_separator_control()
    prep = _prepare(raw)
    if prep.get("status") != "READY":
        return prep
    candidates = separator_candidates(prep)
    admissible = [x for x in candidates if x["structural_ok"]]
    if not admissible:
        return {"status": "HALT_NO_SEPARATOR_FOR_TAMPER_CONTROL"}
    separator = int(admissible[0]["variable"])
    proposal = proposal_record(prep, separator, candidates)
    proposal["branch_values"] = [1, 0]
    return build(raw, proposal)


def main() -> None:
    out = {
        "artifact_id": ARTIFACT_ID,
        "authority": AUTHORITY,
        "positive": explain(positive_separator_control()),
        "one_branch_unsat_one_sat": explain(one_branch_unsat_one_sat_control()),
        "both_branches_unsat": explain(both_branches_unsat_control()),
        "no_articulation": explain(no_single_variable_articulation_control()),
        "branch_still_gt2": explain(branch_still_gt2_control()),
        "hint": explain(injected_hint_control()),
        "tamper": tampered_control(),
        "scientific_firewall": firewall(),
    }
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
