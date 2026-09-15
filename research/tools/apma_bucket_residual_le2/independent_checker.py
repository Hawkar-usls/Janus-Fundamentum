from __future__ import annotations

import hashlib
import json
from pathlib import Path

from research.tools.apma_unseen_basis.raw_relation_basis import canonicalize_raw
from research.tools.apma_bucket_common_core import common_core_semijoin_prefilter as cc_v1
from research.tools.apma_bucket_common_core import common_core_semijoin_prefilter_v1_1 as cc_v11
from research.tools.apma_bucket_conditioned_factorized_payload import conditioned_factorized_payload as v35
from research.tools.apma_bucket_residual_le2 import residual_le2_factorized_payload as cand
from research.tools.apma_guarded_elimination import guarded_bounded_output_elimination as guarded
from research.tools.apma_cut_support_carrier import cut_support_carrier as parent_support

ARTIFACT_ID = "JANUS-TRUMP-BICAMERAL-BUCKET-UNIQUE-CORE-RESIDUAL-COMPONENT-LE2-FACTORIZED-PAYLOAD-INDEPENDENT-CHECK-2026-09-15-v1.0"
VERDICT = "PASS_SCOPED_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_COMPONENT_LE2_FACTORIZED_PAYLOAD_V1"
CANDIDATE = Path("research/tools/apma_bucket_residual_le2/residual_le2_factorized_payload.py")
CANDIDATE_BLOB = "8c0c2802ccf8bf9b67b80cedb5b26797cd78d1c8"


def root() -> Path:
    return Path(__file__).resolve().parents[3]


def blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def _projection(factor: dict, variables: list[int], row: tuple[int, ...]) -> tuple[int, ...]:
    pos = {int(v): i for i, v in enumerate(factor["scope"])}
    return tuple(int(row[pos[int(v)]]) for v in variables)


def _residual_scope(factor: dict, core: list[int]) -> list[int]:
    c = set(int(v) for v in core)
    return [int(v) for v in factor["scope"] if int(v) not in c]


def prepare_independent(raw: dict) -> dict:
    predecessor = cc_v11.explain(raw)
    if predecessor.get("status") != "OPEN_COMMON_CORE_FILTERED_BUCKET_STILL_OVER_L2":
        return {"status": "OUT_OF_SCOPE_PREDECESSOR_NOT_STICKY_OPEN", "predecessor_status": predecessor.get("status")}
    ready = cc_v11.first_failed_original_bucket_v11(raw)
    if ready.get("status") != "READY":
        return {"status": ready.get("status", "OUT_OF_SCOPE_READY_FAILURE")}
    core = [int(v) for v in ready["common_core"]]
    supports = []
    for f in ready["bucket"]:
        supports.append({_projection(f, core, tuple(row)) for row in f["rows"]})
    common = set.intersection(*supports) if supports else set()
    if len(common) != 1:
        return {"status": "OPEN_NONUNIQUE_COMMON_CORE_SUPPORT", "common_support_size": len(common)}
    bucket_ids = [str(f["id"]) for f in ready["bucket"]]
    target_ids = [f"orig:{int(gi)}" for gi in ready["component"]]
    if bucket_ids != target_ids:
        return {"status": "OPEN_INCOMPLETE_TARGET_COMPONENT_COVERAGE"}
    state = tuple(next(iter(common)))
    conditioned = []
    for f in ready["bucket"]:
        rows = [tuple(int(x) for x in row) for row in f["rows"] if _projection(f, core, tuple(row)) == state]
        if not rows:
            return {"status": "EXACT_UNSAT_BY_EMPTY_CONDITIONED_FACTOR", "factor_id": f["id"]}
        conditioned.append({**f, "rows": rows})

    scopes = [set(_residual_scope(f, core)) for f in conditioned]
    adj = {i: set() for i in range(len(conditioned))}
    for i in range(len(conditioned)):
        for j in range(i + 1, len(conditioned)):
            if scopes[i] & scopes[j]:
                adj[i].add(j)
                adj[j].add(i)
    seen = set()
    components = []
    for start in range(len(conditioned)):
        if start in seen:
            continue
        stack = [start]
        comp = []
        while stack:
            x = stack.pop()
            if x in seen:
                continue
            seen.add(x)
            comp.append(x)
            stack.extend(sorted(adj[x] - seen, reverse=True))
        components.append(sorted(comp))
    components = sorted(components, key=lambda xs: (xs[0], len(xs), xs))
    if any(len(c) > 2 for c in components):
        return {"status": "OPEN_RESIDUAL_COMPONENT_GT2", "residual_components": components, "pair_join_count": 0, "global_residual_cartesian_products_materialized": 0}
    return {
        "status": "READY",
        "predecessor": predecessor,
        "ready": ready,
        "canonical": ready["canonical"],
        "core": core,
        "state": state,
        "conditioned": conditioned,
        "components": components,
    }


def _singleton(f: dict, core: list[int], cut: set[int]) -> dict:
    residual = _residual_scope(f, core)
    boundary = [v for v in residual if v in cut]
    pos = {int(v): i for i, v in enumerate(f["scope"])}
    witness = {}
    for row in f["rows"]:
        key = tuple(int(row[pos[v]]) for v in boundary)
        witness.setdefault(key, row)
    return {"status": "ADMIT", "factors": [f], "boundary": boundary, "rows": sorted(witness), "witness": witness, "pair_join_count": 0, "pair_rows_examined": 0}


def _pair_hash(left: dict, right: dict, core: list[int], cut: set[int]) -> dict:
    lres = set(_residual_scope(left, core))
    rres = set(_residual_scope(right, core))
    shared = sorted(lres & rres)
    boundary = sorted((lres | rres) & cut)
    lpos = {int(v): i for i, v in enumerate(left["scope"])}
    rpos = {int(v): i for i, v in enumerate(right["scope"])}
    index = {}
    for row in right["rows"]:
        sig = tuple(int(row[rpos[v]]) for v in shared)
        index.setdefault(sig, []).append(row)
    witness = {}
    matched_pairs = 0
    for lrow in left["rows"]:
        sig = tuple(int(lrow[lpos[v]]) for v in shared)
        for rrow in index.get(sig, []):
            matched_pairs += 1
            merged = {int(v): int(bit) for v, bit in zip(left["scope"], lrow)}
            ok = True
            for v, bit in zip(right["scope"], rrow):
                v, bit = int(v), int(bit)
                if v in merged and merged[v] != bit:
                    ok = False
                    break
                merged[v] = bit
            if not ok:
                continue
            key = tuple(int(merged[v]) for v in boundary)
            witness.setdefault(key, (lrow, rrow))
    if not witness:
        return {"status": "EXACT_UNSAT_BY_EMPTY_RESIDUAL_PAIR_JOIN", "shared": shared, "pair_join_count": 1, "hash_matched_pairs": matched_pairs, "global_residual_cartesian_products_materialized": 0}
    return {"status": "ADMIT", "factors": [left, right], "boundary": boundary, "rows": sorted(witness), "witness": witness, "pair_join_count": 1, "hash_matched_pairs": matched_pairs}


def solve_independent(raw: dict) -> dict:
    prep = prepare_independent(raw)
    if prep.get("status") != "READY":
        return prep
    cut = set(int(v) for v in prep["ready"]["cut"])
    carriers = []
    boundary_constraints = []
    pair_joins = 0
    total_rows = 0
    for ordinal, comp in enumerate(prep["components"]):
        if len(comp) == 1:
            car = _singleton(prep["conditioned"][comp[0]], prep["core"], cut)
        elif len(comp) == 2:
            car = _pair_hash(prep["conditioned"][comp[0]], prep["conditioned"][comp[1]], prep["core"], cut)
        else:
            return {"status": "OPEN_RESIDUAL_COMPONENT_GT2", "residual_components": prep["components"]}
        if car["status"] != "ADMIT":
            return car
        carriers.append(car)
        pair_joins += int(car.get("pair_join_count", 0))
        total_rows += len(car["rows"])
        if car["boundary"]:
            boundary_constraints.append({"id": f"independent_residual_component_{ordinal}", "scope": list(car["boundary"]), "allowed": [list(x) for x in car["rows"]]})

    target = set(int(x) for x in prep["ready"]["component"])
    constraints = [json.loads(json.dumps(rel)) for gi, rel in enumerate(prep["canonical"]["constraints"]) if gi not in target]
    constraints.extend(boundary_constraints)
    transformed = canonicalize_raw({"variables": list(prep["canonical"]["variables"]), "constraints": constraints})
    transformed_components = parent_support.constraint_components_after_cut(transformed, list(prep["ready"]["cut"]))
    handoff = guarded.run_guarded_elimination(transformed, list(prep["ready"]["cut"]), transformed_components)
    if handoff.get("status") == "EXACT_UNSAT_BY_COMPLETE_GUARDED_ELIMINATION":
        return {"status": "EXACT_UNSAT_BY_RESIDUAL_LE2_FACTORIZED_BOUNDARY_HANDOFF", "components": prep["components"], "pair_join_count": pair_joins, "total_boundary_rows": total_rows, "global_residual_cartesian_products_materialized": 0}
    if handoff.get("status") != "ADMIT_EXACT_GUARDED_BOUNDED_OUTPUT_ELIMINATION":
        return {"status": "OPEN_RESIDUAL_LE2_TRANSFORMED_HANDOFF", "handoff": handoff.get("status"), "components": prep["components"]}

    assignment = {int(k): int(v) for k, v in handoff["witness"]["assignment"].items()}
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
    for car in carriers:
        key = tuple(int(assignment[v]) for v in car["boundary"])
        rows = car["witness"].get(key)
        if rows is None:
            return {"status": "OPEN_ORIGINAL_WITNESS_REPLAY_FAILURE", "reason": "BOUNDARY_WITNESS_MISSING"}
        row_list = [rows] if len(car["factors"]) == 1 else list(rows)
        for f, row in zip(car["factors"], row_list):
            for v, bit in zip(f["scope"], row):
                v, bit = int(v), int(bit)
                if v in assignment and assignment[v] != bit:
                    return {"status": "OPEN_ORIGINAL_WITNESS_REPLAY_FAILURE", "reason": "RECONSTRUCTION_CONFLICT", "factor_id": f["id"], "variable": v}
                assignment[v] = bit
    verified = guarded.verify_original_assignment(prep["canonical"], assignment)
    return {
        "status": "ADMIT_EXACT_UNIQUE_CORE_RESIDUAL_LE2_FACTORIZED_PAYLOAD_PORTFOLIO" if verified else "OPEN_ORIGINAL_WITNESS_REPLAY_FAILURE",
        "components": prep["components"],
        "component_sizes": [len(c) for c in prep["components"]],
        "pair_join_count": pair_joins,
        "total_boundary_rows": total_rows,
        "global_residual_cartesian_products_materialized": 0,
        "witness_verified": verified,
    }


def run() -> dict:
    positive_raw = cand.positive_pair_control()
    pair_unsat_raw = cand.pair_unsat_control()
    gt2_raw = cand.residual_component_gt2_control()
    multiple_raw = cand.multiple_common_core_states_control()

    old_positive = v35.explain(positive_raw)
    cpos = cand.explain(positive_raw)
    ipos = solve_independent(positive_raw)
    cunsat = cand.explain(pair_unsat_raw)
    iunsat = solve_independent(pair_unsat_raw)
    cgt2 = cand.explain(gt2_raw)
    igt2 = solve_independent(gt2_raw)
    cmulti = cand.explain(multiple_raw)
    imulti = solve_independent(multiple_raw)
    hint = cand.explain(cand.injected_hint_control())
    tamper = cand.tampered_control()

    cpos_car = cpos.get("carrier", {})
    receipt = cpos_car.get("receipt", {})
    components = receipt.get("residual_components", [])
    sizes = receipt.get("residual_component_sizes", [])

    checks = {
        "G1_candidate_blob": blob(root() / CANDIDATE) == CANDIDATE_BLOB,
        "G1_candidate_source_guard": cand.source_guard()["ok"] is True,
        "G2_predecessor_sticky": cand.prepare(positive_raw).get("predecessor", {}).get("status") == "OPEN_COMMON_CORE_FILTERED_BUCKET_STILL_OVER_L2",
        "G2_unique_core": cand.prepare(positive_raw).get("status") == "READY" and len(cand.prepare(positive_raw).get("state", ())) == len(cand.prepare(positive_raw).get("core", [])),
        "G3_components_match": components == ipos.get("components"),
        "G4_v35_old_cross_open": old_positive.get("status") == "OPEN_RESIDUAL_CROSS_COUPLING",
        "G4_has_pair_component": 2 in sizes and all(int(x) <= 2 for x in sizes),
        "G5_candidate_positive": cpos.get("status") == "ADMIT_EXACT_UNIQUE_CORE_RESIDUAL_LE2_FACTORIZED_PAYLOAD_PORTFOLIO",
        "G5_candidate_witness": cpos_car.get("witness_verified") is True,
        "G5_independent_positive": ipos.get("status") == "ADMIT_EXACT_UNIQUE_CORE_RESIDUAL_LE2_FACTORIZED_PAYLOAD_PORTFOLIO" and ipos.get("witness_verified") is True,
        "G6_candidate_one_join_per_pair": int(receipt.get("pair_join_count", -1)) == int(receipt.get("pair_component_count", -2)) and int(receipt.get("join_chains_materialized", -1)) == 0,
        "G6_independent_one_join_per_pair": int(ipos.get("pair_join_count", -1)) == sum(1 for x in ipos.get("component_sizes", []) if int(x) == 2),
        "G7_candidate_zero_global_product": int(receipt.get("global_residual_cartesian_products_materialized", -1)) == 0,
        "G7_independent_zero_global_product": int(ipos.get("global_residual_cartesian_products_materialized", -1)) == 0,
        "G8_candidate_pair_unsat": cunsat.get("status") == "EXACT_UNSAT_BY_EMPTY_RESIDUAL_PAIR_JOIN",
        "G8_independent_pair_unsat": iunsat.get("status") == "EXACT_UNSAT_BY_EMPTY_RESIDUAL_PAIR_JOIN",
        "G9_candidate_gt2_open": cgt2.get("status") == "OPEN_RESIDUAL_COMPONENT_GT2" and int(cgt2.get("carrier", {}).get("pair_joins_materialized", 0)) == 0,
        "G9_independent_gt2_open": igt2.get("status") == "OPEN_RESIDUAL_COMPONENT_GT2" and int(igt2.get("pair_join_count", 0)) == 0,
        "G10_candidate_multiple_open": cmulti.get("status") == "OPEN_NONUNIQUE_COMMON_CORE_SUPPORT",
        "G10_independent_multiple_open": imulti.get("status") == "OPEN_NONUNIQUE_COMMON_CORE_SUPPORT",
        "G11_hint_rejected": hint.get("status") == "REJECT_RAW_INPUT",
        "G11_tamper_rejected": tamper.get("status") == "REJECT_TAMPERED_PROVENANCE",
        "G12_no_budget_raise": receipt.get("budget_raised") is False,
        "G12_no_alt_orders": int(receipt.get("alternative_orders", -1)) == 0,
        "G12_no_generic_transfer": int(receipt.get("generic_transfer_calls", -1)) == 0,
        "G12_no_external_solver": int(receipt.get("external_solver_calls", -1)) == 0,
        "FW_p_vs_np": cand.firewall()["P_VS_NP"] == "OPEN",
        "FW_general_sat": cand.firewall()["GENERAL_SAT_IN_P"] == "NOT_PROVED",
        "FW_general_partial_overlap": cand.firewall()["GENERAL_PARTIAL_OVERLAP_FACTORIZATION"] == "NOT_PROVED",
    }
    verdict = VERDICT if all(checks.values()) else "FAIL_OR_OPEN_UNIQUE_CORE_RESIDUAL_COMPONENT_LE2_FACTORIZED_PAYLOAD_V1"
    return {
        "artifact_id": ARTIFACT_ID,
        "authority": "INDEPENDENT_CHECKER__SCOPED_ONLY",
        "checks": checks,
        "controls": {
            "old_v35_positive": old_positive.get("status"),
            "positive_candidate": cpos.get("status"),
            "positive_independent": ipos.get("status"),
            "positive_component_sizes": sizes,
            "positive_pair_component_count": receipt.get("pair_component_count"),
            "positive_pair_join_count": receipt.get("pair_join_count"),
            "positive_pair_row_comparisons": receipt.get("pair_row_comparisons"),
            "positive_portfolio_records": receipt.get("portfolio_records"),
            "positive_boundary_rows": receipt.get("portfolio_boundary_rows"),
            "pair_unsat_candidate": cunsat.get("status"),
            "pair_unsat_independent": iunsat.get("status"),
            "gt2_candidate": cgt2.get("status"),
            "gt2_independent": igt2.get("status"),
            "multiple_candidate": cmulti.get("status"),
            "multiple_independent": imulti.get("status"),
            "hint": hint.get("status"),
            "tamper": tamper.get("status"),
        },
        "independent_methods": {
            "residual_components": "SEPARATE_BFS_ON_PAIRWISE_SCOPE_OVERLAP_GRAPH",
            "pair_join": "HASH_INDEX_ON_SHARED_RESIDUAL_SIGNATURE",
            "candidate_pair_join": "NESTED_EXPLICIT_PAIR_LOOP",
            "candidate_componentization": "UNION_FIND",
            "candidate_helpers_used_for_components_or_pair_join": False,
            "global_residual_cartesian_products_materialized": 0,
        },
        "scientific_firewall": cand.firewall(),
        "verdict": verdict,
    }


def main() -> None:
    print(json.dumps(run(), sort_keys=True))


if __name__ == "__main__":
    main()
