from __future__ import annotations

import json
from typing import Any

from research.tools.apma_unseen_basis.raw_relation_basis import canonicalize_raw
from research.tools.apma_bucket_common_core import common_core_semijoin_prefilter as cc_v1
from research.tools.apma_bucket_common_core import common_core_semijoin_prefilter_v1_1 as cc_v11
from research.tools.apma_guarded_elimination import guarded_bounded_output_elimination as guarded
from research.tools.apma_cut_support_carrier import cut_support_carrier as parent_support
from research.tools.apma_derived_boundary_factor import derived_two_relation_factor as pair_v1
from research.tools.apma_bucket_conditioned_factorized_payload import conditioned_factorized_payload as cand

ARTIFACT_ID = "JANUS-TRUMP-BICAMERAL-BUCKET-UNIQUE-CORE-CONDITIONED-FACTORIZED-PAYLOAD-INDEPENDENT-CHECK-2026-09-15-v1.0"
VERDICT = "PASS_SCOPED_BICAMERAL_BUCKET_UNIQUE_CORE_CONDITIONED_FACTORIZED_PAYLOAD_V1"


def _project(scope: list[int], row: tuple[int, ...], core: list[int]) -> tuple[int, ...]:
    pos = {v: i for i, v in enumerate(scope)}
    return tuple(int(row[pos[v]]) for v in core)


def _raw_factors(ready: dict) -> list[dict]:
    out = []
    for gi in ready["component"]:
        rel = ready["canonical"]["constraints"][gi]
        os = list(rel["scope"])
        scope = sorted(os)
        pos = {v: i for i, v in enumerate(os)}
        rows = sorted({tuple(int(raw[pos[v]]) for v in scope) for raw in rel["allowed"]})
        out.append({"id": f"orig:{gi}", "gi": gi, "scope": scope, "rows": rows})
    return out


def independent_solve(raw: dict) -> dict:
    predecessor = cc_v11.explain(raw)
    if predecessor.get("status") != "OPEN_COMMON_CORE_FILTERED_BUCKET_STILL_OVER_L2":
        return {"status": "OUT_OF_SCOPE_PREDECESSOR_NOT_STICKY_OPEN", "predecessor": predecessor.get("status")}
    ready = cc_v11.first_failed_original_bucket_v11(raw)
    if ready.get("status") != "READY":
        return {"status": ready.get("status")}

    canonical = ready["canonical"]
    cut = list(ready["cut"])
    cutset = set(cut)
    core = list(ready["common_core"])
    bucket = list(ready["bucket"])

    supports = []
    for f in bucket:
        supports.append({_project(f["scope"], row, core) for row in f["rows"]})
    common = sorted(set.intersection(*supports) if supports else set())
    if len(common) != 1:
        return {"status": "OPEN_NONUNIQUE_COMMON_CORE_SUPPORT", "common_support_size": len(common), "bucket_cartesian_combinations_enumerated": 0}
    state = tuple(int(x) for x in common[0])

    target_factors = _raw_factors(ready)
    if [f["id"] for f in bucket] != [f["id"] for f in target_factors]:
        return {"status": "OPEN_INCOMPLETE_TARGET_COMPONENT_COVERAGE", "bucket_cartesian_combinations_enumerated": 0}

    cset = set(core)
    residual = [[v for v in f["scope"] if v not in cset] for f in target_factors]
    overlaps = []
    for i in range(len(residual)):
        for j in range(i + 1, len(residual)):
            shared = sorted(set(residual[i]) & set(residual[j]))
            if shared:
                overlaps.append((i, j, shared))
    if overlaps:
        return {"status": "OPEN_RESIDUAL_CROSS_COUPLING", "cross_couplings": overlaps, "bucket_cartesian_combinations_enumerated": 0}

    boundary_constraints = []
    witness_maps: list[dict[str, Any]] = []
    portfolio_rows = 0
    for ordinal, f in enumerate(target_factors):
        pos = {v: i for i, v in enumerate(f["scope"])}
        conditioned = [row for row in f["rows"] if _project(f["scope"], row, core) == state]
        if not conditioned:
            return {"status": "EXACT_UNSAT_BY_EMPTY_CONDITIONED_FACTOR"}
        bscope = [v for v in residual[ordinal] if v in cutset]
        mapping: dict[tuple[int, ...], tuple[int, ...]] = {}
        for row in conditioned:
            key = tuple(int(row[pos[v]]) for v in bscope)
            mapping.setdefault(key, row)
        portfolio_rows += len(mapping)
        witness_maps.append({"factor": f, "boundary_scope": bscope, "map": mapping})
        if bscope:
            boundary_constraints.append({
                "id": f"ind_boundary_{ordinal}",
                "scope": bscope,
                "allowed": [list(k) for k in sorted(mapping)],
            })

    target = set(int(x) for x in ready["component"])
    transformed_constraints = [
        json.loads(json.dumps(rel))
        for gi, rel in enumerate(canonical["constraints"])
        if gi not in target
    ] + boundary_constraints
    transformed = canonicalize_raw({"variables": list(canonical["variables"]), "constraints": transformed_constraints})
    components = parent_support.constraint_components_after_cut(transformed, cut)
    handoff = guarded.run_guarded_elimination(transformed, cut, components)
    if handoff.get("status") == "EXACT_UNSAT_BY_COMPLETE_GUARDED_ELIMINATION":
        return {"status": "EXACT_UNSAT_BY_UNIQUE_CORE_CONDITIONED_FACTORIZED_BOUNDARY_HANDOFF", "cartesian_products_materialized": 0}
    if handoff.get("status") != "ADMIT_EXACT_GUARDED_BOUNDED_OUTPUT_ELIMINATION":
        return {"status": "OPEN_TRANSFORMED_FACTORIZED_HANDOFF", "handoff": handoff.get("status"), "cartesian_products_materialized": 0}

    assignment = {int(k): int(v) for k, v in handoff["witness"]["assignment"].items()}
    target_internal = {
        v
        for gi in ready["component"]
        for v in canonical["constraints"][gi]["scope"]
        if v not in cutset
    }
    for v in target_internal:
        assignment.pop(v, None)
    for v, bit in zip(core, state):
        assignment[int(v)] = int(bit)

    for rec in witness_maps:
        f = rec["factor"]
        bscope = rec["boundary_scope"]
        key = tuple(int(assignment[v]) for v in bscope)
        row = rec["map"].get(key)
        if row is None:
            return {"status": "OPEN_ORIGINAL_WITNESS_REPLAY_FAILURE", "reason": "MISSING_BOUNDARY_KEY"}
        for v, bit in zip(f["scope"], row):
            bit = int(bit)
            if v in assignment and assignment[v] != bit:
                return {"status": "OPEN_ORIGINAL_WITNESS_REPLAY_FAILURE", "reason": "MERGE_CONFLICT"}
            assignment[v] = bit

    verified = guarded.verify_original_assignment(canonical, assignment)
    return {
        "status": "ADMIT_EXACT_UNIQUE_CORE_CONDITIONED_FACTORIZED_PAYLOAD_PORTFOLIO" if verified else "OPEN_ORIGINAL_WITNESS_REPLAY_FAILURE",
        "witness_verified": verified,
        "common_support_size": 1,
        "residual_scope_count": len(residual),
        "portfolio_boundary_rows": portfolio_rows,
        "cartesian_products_materialized": 0,
        "bucket_combinations_enumerated": 0,
    }


def cross_control() -> dict:
    raw = cc_v1.filtered_still_overbudget_control()
    a = next(r for r in raw["constraints"] if r["id"] == "sticky_0")
    b = next(r for r in raw["constraints"] if r["id"] == "sticky_1")
    b["scope"][-2] = a["scope"][-2]
    return raw


def multiple_control() -> dict:
    raw = cc_v1.filtered_still_overbudget_control()
    y1 = pair_v1._bits(19, 20)
    third = next(r for r in raw["constraints"] if r["id"] == "left_third")
    third["allowed"].append(y1 + [0])
    for rel in raw["constraints"]:
        if rel["id"].startswith("sticky_"):
            rel["allowed"].extend([y1 + [a, b] for a, b in [(0, 0), (0, 1), (1, 0), (1, 1)]])
    return raw


def incomplete_control() -> dict:
    raw = cc_v1.filtered_still_overbudget_control()
    p = max(raw["variables"]) + 1
    raw["variables"].append(p)
    raw["constraints"].insert(-1, {"id": "nonbucket_same_component", "scope": [21, p], "allowed": [[0, 0], [1, 1]]})
    return raw


def run() -> dict:
    positive_raw = cc_v1.filtered_still_overbudget_control()
    cross_raw = cross_control()
    multi_raw = multiple_control()
    incomplete_raw = incomplete_control()

    cp = cand.explain(positive_raw)
    ccross = cand.explain(cross_raw)
    cmulti = cand.explain(multi_raw)
    cinc = cand.explain(incomplete_raw)
    chint = cand.explain(cand.injected_hint_control())
    ctamper = cand.tampered_control()

    ip = independent_solve(positive_raw)
    icross = independent_solve(cross_raw)
    imulti = independent_solve(multi_raw)
    iinc = independent_solve(incomplete_raw)

    ccar = cp.get("carrier", {})
    checks = {
        "G1_candidate_source_guard": cp.get("source_guard", {}).get("ok") is True,
        "G2_predecessor_sticky_open": cc_v11.explain(positive_raw).get("status") == "OPEN_COMMON_CORE_FILTERED_BUCKET_STILL_OVER_L2",
        "G2_filtered_product_gt_l2": int(ccar.get("receipt", {}).get("predecessor_filtered_product", 0)) == 1099511627776,
        "G3_unique_common_state": int(ccar.get("receipt", {}).get("common_support_size", 0)) == 1 and ip.get("common_support_size") == 1,
        "G4_complete_target_coverage": ccar.get("receipt", {}).get("target_factor_count") == len(cc_v11.first_failed_original_bucket_v11(positive_raw)["component"]),
        "G5_residual_disjoint": ccar.get("receipt", {}).get("residual_cross_couplings") == 0,
        "G6_candidate_zero_cartesian": ccar.get("receipt", {}).get("target_cartesian_products_materialized") == 0,
        "G6_independent_zero_cartesian": ip.get("cartesian_products_materialized") == 0,
        "G7_candidate_positive_terminal": cp.get("status") == "ADMIT_EXACT_UNIQUE_CORE_CONDITIONED_FACTORIZED_PAYLOAD_PORTFOLIO",
        "G7_independent_positive_terminal": ip.get("status") == "ADMIT_EXACT_UNIQUE_CORE_CONDITIONED_FACTORIZED_PAYLOAD_PORTFOLIO",
        "G7_candidate_witness": cp.get("carrier", {}).get("witness_verified") is True,
        "G7_independent_witness": ip.get("witness_verified") is True,
        "G8_candidate_multiple_open": cmulti.get("status") == "OPEN_NONUNIQUE_COMMON_CORE_SUPPORT",
        "G8_independent_multiple_open": imulti.get("status") == "OPEN_NONUNIQUE_COMMON_CORE_SUPPORT",
        "G9_candidate_cross_open": ccross.get("status") == "OPEN_RESIDUAL_CROSS_COUPLING",
        "G9_independent_cross_open": icross.get("status") == "OPEN_RESIDUAL_CROSS_COUPLING",
        "G10_candidate_incomplete_open": cinc.get("status") == "OPEN_INCOMPLETE_TARGET_COMPONENT_COVERAGE",
        "G10_independent_incomplete_open": iinc.get("status") == "OPEN_INCOMPLETE_TARGET_COMPONENT_COVERAGE",
        "G11_hint_rejected": chint.get("status") == "REJECT_RAW_INPUT",
        "G11_tamper_rejected": ctamper.get("status") == "REJECT_TAMPERED_PROVENANCE",
        "G12_no_budget_raise": ccar.get("receipt", {}).get("budget_raised") is False,
        "G12_no_alt_orders": ccar.get("receipt", {}).get("alternative_orders") == 0,
        "G12_no_external_solver": ccar.get("receipt", {}).get("external_solver_calls") == 0,
        "G12_no_generic_transfer": ccar.get("receipt", {}).get("generic_transfer_calls") == 0,
        "FW_p_vs_np": cand.firewall()["P_VS_NP"] == "OPEN",
        "FW_general_sat": cand.firewall()["GENERAL_SAT_IN_P"] == "NOT_PROVED",
        "FW_general_factorization": cand.firewall()["GENERAL_CONDITIONED_FACTORIZATION"] == "NOT_PROVED",
    }

    verdict = VERDICT if all(checks.values()) else "FAIL_OR_OPEN_UNIQUE_CORE_CONDITIONED_FACTORIZED_PAYLOAD_V1"
    return {
        "artifact_id": ARTIFACT_ID,
        "authority": "INDEPENDENT_CHECKER__SCOPED_ONLY",
        "checks": checks,
        "controls": {
            "positive_candidate": cp.get("status"),
            "positive_independent": ip.get("status"),
            "positive_predecessor_filtered_product": ccar.get("receipt", {}).get("predecessor_filtered_product"),
            "positive_portfolio_records": ccar.get("receipt", {}).get("portfolio_records"),
            "positive_boundary_rows": ccar.get("receipt", {}).get("portfolio_boundary_rows"),
            "cross_candidate": ccross.get("status"),
            "cross_independent": icross.get("status"),
            "multiple_candidate": cmulti.get("status"),
            "multiple_independent": imulti.get("status"),
            "incomplete_candidate": cinc.get("status"),
            "incomplete_independent": iinc.get("status"),
            "hint": chint.get("status"),
            "tamper": ctamper.get("status"),
        },
        "independent_method": {
            "common_support": "SEPARATE_EXPLICIT_SET_INTERSECTION",
            "residual_dependency": "SEPARATE_PAIRWISE_SCOPE_INTERSECTION_AUDIT",
            "boundary_projection": "SEPARATE_ROW_SCAN_AND_BOUNDARY_MAP",
            "candidate_portfolio_helpers_used": False,
            "cartesian_products_materialized": 0,
        },
        "scientific_firewall": cand.firewall(),
        "verdict": verdict,
    }


def main() -> None:
    print(json.dumps(run(), sort_keys=True))


if __name__ == "__main__":
    main()
