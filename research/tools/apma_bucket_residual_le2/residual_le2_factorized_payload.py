from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from research.tools.apma_unseen_basis.raw_relation_basis import canonicalize_raw, RawBasisInputError
from research.tools.apma_bucket_common_core import common_core_semijoin_prefilter as cc_v1
from research.tools.apma_bucket_common_core import common_core_semijoin_prefilter_v1_1 as cc_v11
from research.tools.apma_bucket_conditioned_factorized_payload import conditioned_factorized_payload as v35
from research.tools.apma_guarded_elimination import guarded_bounded_output_elimination as guarded
from research.tools.apma_cut_support_carrier import cut_support_carrier as parent_support

ARTIFACT_ID = "JANUS-TRUMP-BICAMERAL-BUCKET-UNIQUE-CORE-RESIDUAL-COMPONENT-LE2-FACTORIZED-PAYLOAD-CANDIDATE-2026-09-15-v1.0"
AUTHORITY = "CANDIDATE_IMPLEMENTATION__NO_SCIENTIFIC_PROMOTION"
PREREG = Path("research/TRUMP_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_COMPONENT_LE2_FACTORIZED_PAYLOAD_PREREGISTRATION_2026-09-15.json")
PREREG_BLOB = "9c84c058a713f206b73a22a75103693b1bf9f79a"
PARENT_STATE = Path("registry/TRUMP_CURRENT_STATE_2026-09-15_v3.5.json")
PARENT_STATE_BLOB = "4b52dc0529593bc3eb0437101545ed5112c98482"
V35 = Path("research/tools/apma_bucket_conditioned_factorized_payload/conditioned_factorized_payload.py")
V35_BLOB = "c07cc8c12fa6f7a9b8f2560095caa4bdcc235480"
TWO_REL_PREREG = Path("research/TRUMP_BICAMERAL_DERIVED_TWO_RELATION_BOUNDARY_FACTOR_PREREGISTRATION_2026-09-15.json")
TWO_REL_PREREG_BLOB = "4c3af40842188d2489df8df7ed66c0e3dc8e711e"
FACTORIZED = Path("research/tools/apma_factorized_feedback/factorized_portfolio.py")
FACTORIZED_BLOB = "ab3cd177eb1e554f5119238c8556f05feb988bb3"


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
        "prereg_gate": p.get("frozen_gate") == "TRUMP_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_COMPONENT_LE2_FACTORIZED_PAYLOAD_FALSIFIER_GATE",
        "parent_state_blob": git_blob_sha1(r / PARENT_STATE) == PARENT_STATE_BLOB,
        "v35_candidate_blob": git_blob_sha1(r / V35) == V35_BLOB,
        "two_relation_prereg_blob": git_blob_sha1(r / TWO_REL_PREREG) == TWO_REL_PREREG_BLOB,
        "factorized_feedback_blob": git_blob_sha1(r / FACTORIZED) == FACTORIZED_BLOB,
    }
    return {"ok": all(checks.values()), "checks": checks}


def firewall() -> dict:
    return {
        "P_VS_NP": "OPEN",
        "GENERAL_SAT_IN_P": "NOT_PROVED",
        "CONNECTED_MIXED_CORE_SOLVED": "NO",
        "GENERAL_CONDITIONED_FACTORIZATION": "NOT_PROVED",
        "GENERAL_PARTIAL_OVERLAP_FACTORIZATION": "NOT_PROVED",
        "GENERAL_BUCKET_ELIMINATION_POLYNOMIAL": "NOT_PROVED",
        "GLOBAL_APMA_FRONTIER_ADVANCE": "NONE_PENDING_HQ_REVIEW",
        "SCOPE": "UNIQUE_COMMON_CORE_COMPLETE_COVERAGE_WITH_RESIDUAL_RELATION_COMPONENT_SIZE_AT_MOST_TWO",
    }


def _conditioned_rows(factor: dict, core: list[int], state: tuple[int, ...]) -> list[tuple[int, ...]]:
    return [tuple(int(x) for x in row) for row in factor["rows"] if cc_v1._projection(factor, core, row) == state]


def _residual_scope(factor: dict, core: list[int]) -> list[int]:
    c = set(core)
    return [int(v) for v in factor["scope"] if int(v) not in c]


def residual_components(factors: list[dict], core: list[int]) -> list[list[int]]:
    n = len(factors)
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

    scopes = [set(_residual_scope(f, core)) for f in factors]
    for i in range(n):
        for j in range(i + 1, n):
            if scopes[i] & scopes[j]:
                union(i, j)
    groups: dict[int, list[int]] = {}
    for i in range(n):
        groups.setdefault(find(i), []).append(i)
    return sorted((sorted(xs) for xs in groups.values()), key=lambda xs: (xs[0], len(xs), xs))


def prepare(raw: dict) -> dict:
    predecessor = cc_v11.explain(raw)
    if predecessor.get("status") != "OPEN_COMMON_CORE_FILTERED_BUCKET_STILL_OVER_L2":
        return {"status": "OUT_OF_SCOPE_PREDECESSOR_NOT_STICKY_OPEN", "predecessor_status": predecessor.get("status")}
    ready = cc_v11.first_failed_original_bucket_v11(raw)
    if ready.get("status") != "READY":
        return {"status": ready.get("status", "OUT_OF_SCOPE_READY_FAILURE")}
    canonical = ready["canonical"]
    core = list(ready["common_core"])
    sf = cc_v1.support_and_filter(canonical, ready["bucket"], core)
    common = sorted(sf["common"])
    if len(common) != 1:
        return {"status": "OPEN_NONUNIQUE_COMMON_CORE_SUPPORT", "common_support_size": len(common), "bucket_cartesian_combinations_enumerated": 0}
    bucket_ids = [str(f["id"]) for f in ready["bucket"]]
    target_ids = [f"orig:{int(gi)}" for gi in ready["component"]]
    if bucket_ids != target_ids:
        return {"status": "OPEN_INCOMPLETE_TARGET_COMPONENT_COVERAGE", "bucket_factor_ids": bucket_ids, "target_factor_ids": target_ids, "bucket_cartesian_combinations_enumerated": 0}
    state = tuple(int(x) for x in common[0])
    conditioned = []
    for f in ready["bucket"]:
        rows = _conditioned_rows(f, core, state)
        if not rows:
            return {"status": "EXACT_UNSAT_BY_EMPTY_CONDITIONED_FACTOR", "factor_id": f["id"]}
        conditioned.append({**f, "rows": rows})
    components = residual_components(conditioned, core)
    if any(len(comp) > 2 for comp in components):
        return {
            "status": "OPEN_RESIDUAL_COMPONENT_GT2",
            "residual_components": components,
            "residual_component_sizes": [len(c) for c in components],
            "pair_joins_materialized": 0,
            "global_residual_cartesian_products_materialized": 0,
        }
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


def proposal_record(prep: dict) -> dict:
    body = {
        "kind": "UNIQUE_CORE_RESIDUAL_COMPONENT_LE2_FACTORIZED_PAYLOAD_PORTFOLIO",
        "raw_object_sha256": sha256_obj(prep["canonical"]),
        "failed_variable": int(prep["ready"]["failed_variable"]),
        "target_component": list(prep["ready"]["component"]),
        "common_core": list(prep["core"]),
        "unique_common_state": list(prep["state"]),
        "residual_components": [list(c) for c in prep["residual_components"]],
        "max_residual_component_size": 2,
        "truth_authority": False,
        "proof_authority": False,
        "automatic_promotion": False,
    }
    body["proposal_sha256"] = sha256_obj(body)
    return body


def verify_proposal(prep: dict, proposal: dict) -> bool:
    body = dict(proposal)
    claimed = body.pop("proposal_sha256", None)
    return isinstance(claimed, str) and sha256_obj(body) == claimed and proposal == proposal_record(prep)


def _row_assignment(factor: dict, row: tuple[int, ...]) -> dict[int, int]:
    return {int(v): int(bit) for v, bit in zip(factor["scope"], row)}


def _singleton_carrier(factor: dict, core: list[int], cut: set[int], ordinal: int) -> dict:
    residual = _residual_scope(factor, core)
    boundary = [v for v in residual if v in cut]
    pos = {v: i for i, v in enumerate(factor["scope"])}
    witness: dict[tuple[int, ...], tuple[int, ...]] = {}
    for row in factor["rows"]:
        key = tuple(int(row[pos[v]]) for v in boundary)
        witness.setdefault(key, row)
    rows = sorted(witness)
    public = {
        "kind": "SINGLETON_RESIDUAL_COMPONENT",
        "component_ordinal": ordinal,
        "factor_ids": [factor["id"]],
        "boundary_scope": boundary,
        "boundary_rows": [list(x) for x in rows],
        "boundary_row_count": len(rows),
        "conditioned_rows_scanned": len(factor["rows"]),
        "pair_row_comparisons": 0,
        "pair_join_count": 0,
    }
    public["carrier_sha256"] = sha256_obj(public)
    return {"status": "ADMIT_COMPONENT", "public": public, "boundary_scope": boundary, "boundary_rows": rows, "witness": witness, "factors": [factor]}


def _pair_carrier(left: dict, right: dict, core: list[int], cut: set[int], ordinal: int) -> dict:
    left_res = set(_residual_scope(left, core))
    right_res = set(_residual_scope(right, core))
    shared = sorted(left_res & right_res)
    boundary = sorted((left_res | right_res) & cut)
    witness: dict[tuple[int, ...], tuple[tuple[int, ...], tuple[int, ...]]] = {}
    comparisons = 0
    compatible = 0
    for lrow in left["rows"]:
        la = _row_assignment(left, lrow)
        for rrow in right["rows"]:
            comparisons += 1
            ra = _row_assignment(right, rrow)
            if any(la[v] != ra[v] for v in shared):
                continue
            compatible += 1
            merged = dict(la)
            conflict = False
            for v, bit in ra.items():
                if v in merged and merged[v] != bit:
                    conflict = True
                    break
                merged[v] = bit
            if conflict:
                continue
            key = tuple(int(merged[v]) for v in boundary)
            witness.setdefault(key, (lrow, rrow))
    if not witness:
        return {
            "status": "EXACT_UNSAT_BY_EMPTY_RESIDUAL_PAIR_JOIN",
            "factor_ids": [left["id"], right["id"]],
            "shared_residual_variables": shared,
            "pair_row_comparisons": comparisons,
            "compatible_pairs": compatible,
            "pair_join_count": 1,
            "global_residual_cartesian_products_materialized": 0,
        }
    rows = sorted(witness)
    public = {
        "kind": "PAIR_RESIDUAL_COMPONENT",
        "component_ordinal": ordinal,
        "factor_ids": [left["id"], right["id"]],
        "shared_residual_variables": shared,
        "boundary_scope": boundary,
        "boundary_rows": [list(x) for x in rows],
        "boundary_row_count": len(rows),
        "left_conditioned_rows": len(left["rows"]),
        "right_conditioned_rows": len(right["rows"]),
        "pair_row_comparisons": comparisons,
        "compatible_pairs": compatible,
        "pair_join_count": 1,
    }
    public["carrier_sha256"] = sha256_obj(public)
    return {"status": "ADMIT_COMPONENT", "public": public, "boundary_scope": boundary, "boundary_rows": rows, "witness": witness, "factors": [left, right]}


def build_portfolio(prep: dict) -> dict:
    cut = set(int(v) for v in prep["ready"]["cut"])
    carriers = []
    boundary_constraints = []
    pair_joins = 0
    pair_comparisons = 0
    total_boundary_rows = 0
    for ordinal, comp in enumerate(prep["residual_components"]):
        if len(comp) == 1:
            carrier = _singleton_carrier(prep["conditioned"][comp[0]], prep["core"], cut, ordinal)
        elif len(comp) == 2:
            carrier = _pair_carrier(prep["conditioned"][comp[0]], prep["conditioned"][comp[1]], prep["core"], cut, ordinal)
        else:
            return {"status": "OPEN_RESIDUAL_COMPONENT_GT2", "component": comp}
        if carrier["status"] != "ADMIT_COMPONENT":
            return carrier
        carriers.append(carrier)
        pair_joins += int(carrier["public"].get("pair_join_count", 0))
        pair_comparisons += int(carrier["public"].get("pair_row_comparisons", 0))
        total_boundary_rows += len(carrier["boundary_rows"])
        if carrier["boundary_scope"]:
            boundary_constraints.append({
                "id": f"residual_component_{ordinal}",
                "scope": list(carrier["boundary_scope"]),
                "allowed": [list(row) for row in carrier["boundary_rows"]],
            })
    return {
        "status": "ADMIT_RESIDUAL_LE2_PORTFOLIO",
        "carriers": carriers,
        "portfolio_public": [c["public"] for c in carriers],
        "boundary_constraints": boundary_constraints,
        "metrics": {
            "residual_component_count": len(carriers),
            "pair_component_count": sum(1 for c in carriers if c["public"]["kind"] == "PAIR_RESIDUAL_COMPONENT"),
            "pair_join_count": pair_joins,
            "pair_row_comparisons": pair_comparisons,
            "total_boundary_rows_stored": total_boundary_rows,
            "global_residual_cartesian_products_materialized": 0,
            "join_chains_materialized": 0,
        },
    }


def _transformed_raw(prep: dict, portfolio: dict) -> dict:
    target = set(int(x) for x in prep["ready"]["component"])
    constraints = [json.loads(json.dumps(rel)) for gi, rel in enumerate(prep["canonical"]["constraints"]) if gi not in target]
    constraints.extend(json.loads(json.dumps(rel)) for rel in portfolio["boundary_constraints"])
    return {"variables": list(prep["canonical"]["variables"]), "constraints": constraints}


def _reconstruct(prep: dict, portfolio: dict, transformed_assignment: dict[int, int]) -> dict:
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

    chosen = []
    for carrier in portfolio["carriers"]:
        boundary = carrier["boundary_scope"]
        key = tuple(int(assignment[v]) for v in boundary)
        witness = carrier["witness"].get(key)
        if witness is None:
            return {"ok": False, "reason": "BOUNDARY_TUPLE_MISSING_FROM_RESIDUAL_COMPONENT", "boundary": boundary, "key": list(key)}
        rows = [witness] if len(carrier["factors"]) == 1 else list(witness)
        for factor, row in zip(carrier["factors"], rows):
            for v, bit in zip(factor["scope"], row):
                v, bit = int(v), int(bit)
                if v in assignment and assignment[v] != bit:
                    return {"ok": False, "reason": "RESIDUAL_COMPONENT_RECONSTRUCTION_CONFLICT", "factor_id": factor["id"], "variable": v}
                assignment[v] = bit
            chosen.append({"factor_id": factor["id"], "sorted_row": list(row)})
    verified = guarded.verify_original_assignment(prep["canonical"], assignment)
    return {"ok": verified, "reason": "ORIGINAL_RELATION_REPLAY" if verified else "ORIGINAL_RELATION_REPLAY_FAILED", "assignment": assignment, "chosen_rows": chosen}


def build(raw: dict, proposal_override: dict | None = None) -> dict:
    prep = prepare(raw)
    if prep.get("status") != "READY":
        return prep
    proposal = proposal_override or proposal_record(prep)
    if not verify_proposal(prep, proposal):
        return {"status": "REJECT_TAMPERED_PROVENANCE"}
    portfolio = build_portfolio(prep)
    if portfolio.get("status") != "ADMIT_RESIDUAL_LE2_PORTFOLIO":
        return portfolio
    transformed = canonicalize_raw(_transformed_raw(prep, portfolio))
    transformed_components = parent_support.constraint_components_after_cut(transformed, list(prep["ready"]["cut"]))
    handoff = guarded.run_guarded_elimination(transformed, list(prep["ready"]["cut"]), transformed_components)
    receipt = {
        "failed_variable": int(prep["ready"]["failed_variable"]),
        "common_core": list(prep["core"]),
        "unique_common_state": list(prep["state"]),
        "residual_components": [list(c) for c in prep["residual_components"]],
        "residual_component_sizes": [len(c) for c in prep["residual_components"]],
        "pair_component_count": portfolio["metrics"]["pair_component_count"],
        "pair_join_count": portfolio["metrics"]["pair_join_count"],
        "pair_row_comparisons": portfolio["metrics"]["pair_row_comparisons"],
        "portfolio_records": portfolio["metrics"]["residual_component_count"],
        "portfolio_boundary_rows": portfolio["metrics"]["total_boundary_rows_stored"],
        "global_residual_cartesian_products_materialized": 0,
        "join_chains_materialized": 0,
        "budget_raised": False,
        "alternative_orders": 0,
        "generic_transfer_calls": 0,
        "external_solver_calls": 0,
        "transformed_handoff_terminal": handoff.get("status"),
    }
    if handoff.get("status") == "EXACT_UNSAT_BY_COMPLETE_GUARDED_ELIMINATION":
        return {"status": "EXACT_UNSAT_BY_RESIDUAL_LE2_FACTORIZED_BOUNDARY_HANDOFF", "proposal": proposal, "portfolio": portfolio["portfolio_public"], "receipt": receipt, "witness": None, "witness_verified": True}
    if handoff.get("status") != "ADMIT_EXACT_GUARDED_BOUNDED_OUTPUT_ELIMINATION":
        return {"status": "OPEN_RESIDUAL_LE2_TRANSFORMED_HANDOFF", "proposal": proposal, "portfolio": portfolio["portfolio_public"], "receipt": receipt, "handoff": {k: v for k, v in handoff.items() if k != "records_internal"}}
    transformed_assignment = {int(k): int(v) for k, v in handoff["witness"]["assignment"].items()}
    reconstruction = _reconstruct(prep, portfolio, transformed_assignment)
    receipt["original_witness_verified"] = bool(reconstruction["ok"])
    if not reconstruction["ok"]:
        return {"status": "OPEN_ORIGINAL_WITNESS_REPLAY_FAILURE", "proposal": proposal, "portfolio": portfolio["portfolio_public"], "receipt": receipt, "reconstruction": reconstruction}
    return {
        "status": "ADMIT_EXACT_UNIQUE_CORE_RESIDUAL_LE2_FACTORIZED_PAYLOAD_PORTFOLIO",
        "proposal": proposal,
        "portfolio": portfolio["portfolio_public"],
        "receipt": receipt,
        "witness": {str(v): int(reconstruction["assignment"][v]) for v in sorted(reconstruction["assignment"])},
        "witness_verified": True,
        "reconstruction_rows": reconstruction["chosen_rows"],
    }


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


def positive_pair_control() -> dict:
    return v35.residual_cross_coupling_control()


def pair_unsat_control() -> dict:
    raw = positive_pair_control()
    s0 = next(r for r in raw["constraints"] if r["id"] == "sticky_0")
    s1 = next(r for r in raw["constraints"] if r["id"] == "sticky_1")
    # In the positive control sticky_1's first payload coordinate was renamed to sticky_0's,
    # so row[-2] is the shared residual variable in both explicit tables.
    s0["allowed"] = [row for row in s0["allowed"] if int(row[-2]) == 0]
    s1["allowed"] = [row for row in s1["allowed"] if int(row[-2]) == 1]
    return raw


def residual_component_gt2_control() -> dict:
    raw = cc_v1.filtered_still_overbudget_control()
    s0 = next(r for r in raw["constraints"] if r["id"] == "sticky_0")
    shared = int(s0["scope"][-2])
    for name in ["sticky_1", "sticky_2"]:
        rel = next(r for r in raw["constraints"] if r["id"] == name)
        rel["scope"][-2] = shared
    return raw


def multiple_common_core_states_control() -> dict:
    return v35.multiple_common_core_states_control()


def injected_hint_control() -> dict:
    raw = positive_pair_control()
    raw["residual_component_partition"] = "TRUSTED"
    return raw


def tampered_control() -> dict:
    raw = positive_pair_control()
    prep = prepare(raw)
    if prep.get("status") != "READY":
        return prep
    proposal = proposal_record(prep)
    proposal["residual_components"] = list(reversed(proposal["residual_components"]))
    return build(raw, proposal)


def main() -> None:
    out = {
        "artifact_id": ARTIFACT_ID,
        "authority": AUTHORITY,
        "positive_pair": explain(positive_pair_control()),
        "pair_unsat": explain(pair_unsat_control()),
        "residual_gt2": explain(residual_component_gt2_control()),
        "multiple_core": explain(multiple_common_core_states_control()),
        "hint": explain(injected_hint_control()),
        "tamper": tampered_control(),
        "scientific_firewall": firewall(),
    }
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
