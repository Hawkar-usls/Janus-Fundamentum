from __future__ import annotations

import hashlib
import json
from pathlib import Path

from research.tools.apma_unseen_basis.raw_relation_basis import canonicalize_raw
from research.tools.apma_bucket_common_core import common_core_semijoin_prefilter_v1_1 as cc_v11
from research.tools.apma_bucket_residual_le2 import independent_checker as v36ind
from research.tools.apma_bucket_residual_single_var_separator import residual_single_var_separator as cand
from research.tools.apma_guarded_elimination import guarded_bounded_output_elimination as guarded
from research.tools.apma_cut_support_carrier import cut_support_carrier as parent_support

ARTIFACT_ID = "JANUS-TRUMP-BICAMERAL-BUCKET-UNIQUE-CORE-RESIDUAL-SINGLE-VARIABLE-SEPARATOR-FACTORIZED-PAYLOAD-INDEPENDENT-CHECK-2026-09-15-v1.0"
VERDICT = "PASS_SCOPED_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_SINGLE_VARIABLE_SEPARATOR_FACTORIZED_PAYLOAD_V1"
CANDIDATE = Path("research/tools/apma_bucket_residual_single_var_separator/residual_single_var_separator.py")
CANDIDATE_BLOB = "01daf163f850b9a6ec4760d2988e7a03682a84ed"


def root() -> Path:
    return Path(__file__).resolve().parents[3]


def blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def _projection(factor: dict, variables: list[int], row: tuple[int, ...]) -> tuple[int, ...]:
    pos = {int(v): i for i, v in enumerate(factor["scope"])}
    return tuple(int(row[pos[int(v)]]) for v in variables)


def _residual_scope(factor: dict, core: list[int]) -> set[int]:
    C = set(int(v) for v in core)
    return {int(v) for v in factor["scope"] if int(v) not in C}


def _components_bfs(factors: list[dict], core: list[int]) -> list[list[int]]:
    scopes = [_residual_scope(f, core) for f in factors]
    adj = {i: set() for i in range(len(factors))}
    for i in range(len(factors)):
        for j in range(i + 1, len(factors)):
            if scopes[i] & scopes[j]:
                adj[i].add(j)
                adj[j].add(i)
    seen = set()
    comps = []
    for start in range(len(factors)):
        if start in seen:
            continue
        q = [start]
        seen.add(start)
        comp = []
        while q:
            u = q.pop(0)
            comp.append(u)
            for w in sorted(adj[u]):
                if w not in seen:
                    seen.add(w)
                    q.append(w)
        comps.append(sorted(comp))
    return sorted(comps, key=lambda xs: (xs[0], len(xs), xs))


def prepare_independent(raw: dict) -> dict:
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
    components = _components_bfs(conditioned, core)
    gt2 = [list(c) for c in components if len(c) > 2]
    if not gt2:
        return {"status": "OUT_OF_SCOPE_RESIDUAL_LE2_ALREADY_SOLVED", "residual_components": components}
    if len(gt2) != 1:
        return {"status": "OPEN_MULTIPLE_RESIDUAL_GT2_COMPONENTS", "residual_components": components}
    return {
        "status": "READY",
        "predecessor": predecessor,
        "ready": ready,
        "canonical": canonical,
        "core": core,
        "state": state,
        "conditioned": conditioned,
        "residual_components": components,
        "target_gt2": gt2[0],
    }


def discover_separator_independent(prep: dict) -> dict:
    target = [prep["conditioned"][i] for i in prep["target_gt2"]]
    variables = sorted(set().union(*(_residual_scope(f, prep["core"]) for f in target)))
    valid = []
    for variable in variables:
        comps = _components_bfs(target, list(prep["core"]) + [int(variable)])
        if comps and len(comps) >= 2 and max(len(c) for c in comps) <= 2:
            valid.append({"variable": int(variable), "post_removal_components": comps})
    if not valid:
        return {"status": "OPEN_NO_RESIDUAL_SINGLE_VARIABLE_SEPARATOR", "candidate_variables_examined": len(variables)}
    return {
        "status": "ADMIT_SEPARATOR_PROPOSAL",
        "separator": valid[0]["variable"],
        "post_removal_components": valid[0]["post_removal_components"],
        "all_valid_separators": [x["variable"] for x in valid],
        "candidate_variables_examined": len(variables),
    }


def _restrict_rows(factor: dict, separator: int, bit: int) -> list[tuple[int, ...]]:
    positions = {int(v): i for i, v in enumerate(factor["scope"])}
    if int(separator) not in positions:
        return [tuple(int(x) for x in row) for row in factor["rows"]]
    pos = positions[int(separator)]
    return [tuple(int(x) for x in row) for row in factor["rows"] if int(row[pos]) == int(bit)]


def branch_prepare_independent(prep: dict, separator: int, bit: int) -> dict:
    conditioned = []
    for factor in prep["conditioned"]:
        rows = _restrict_rows(factor, separator, bit)
        if not rows:
            return {"status": "BRANCH_EXACT_UNSAT_EMPTY_FACTOR", "terminal_class": "EXACT_UNSAT", "bit": int(bit), "factor_id": factor["id"], "residual_components": []}
        conditioned.append({**factor, "rows": rows})
    core2 = list(prep["core"]) + [int(separator)]
    state2 = tuple(prep["state"]) + (int(bit),)
    components = _components_bfs(conditioned, core2)
    if any(len(c) > 2 for c in components):
        return {"status": "BRANCH_OPEN_RESIDUAL_COMPONENT_GT2", "terminal_class": "OPEN", "bit": int(bit), "residual_components": components}
    return {
        "status": "READY",
        "ready": prep["ready"],
        "canonical": prep["canonical"],
        "core": core2,
        "state": state2,
        "conditioned": conditioned,
        "components": components,
        "separator": int(separator),
        "separator_bit": int(bit),
    }


def solve_branch_independent(prep: dict, separator: int, bit: int) -> dict:
    bp = branch_prepare_independent(prep, separator, bit)
    if bp.get("status") != "READY":
        return bp
    cut = set(int(v) for v in bp["ready"]["cut"])
    carriers = []
    boundary_constraints = []
    pair_joins = 0
    pair_rows_examined = 0
    for ordinal, comp in enumerate(bp["components"]):
        if len(comp) == 1:
            car = v36ind._singleton(bp["conditioned"][comp[0]], bp["core"], cut)
        elif len(comp) == 2:
            car = v36ind._pair_hash(bp["conditioned"][comp[0]], bp["conditioned"][comp[1]], bp["core"], cut)
        else:
            return {"status": "BRANCH_OPEN_RESIDUAL_COMPONENT_GT2", "terminal_class": "OPEN", "bit": int(bit), "residual_components": bp["components"]}
        if car.get("status") == "EXACT_UNSAT_BY_EMPTY_RESIDUAL_PAIR_JOIN":
            return {"status": "BRANCH_EXACT_UNSAT_EMPTY_PAIR_JOIN", "terminal_class": "EXACT_UNSAT", "bit": int(bit), "residual_components": bp["components"], "pair_join_count": 1, "global_residual_cartesian_products_materialized": 0}
        if car.get("status") != "ADMIT":
            return {"status": "BRANCH_OPEN_COMPONENT_CARRIER", "terminal_class": "OPEN", "bit": int(bit), "carrier_status": car.get("status")}
        carriers.append(car)
        pair_joins += int(car.get("pair_join_count", 0))
        pair_rows_examined += int(car.get("pair_rows_examined", car.get("hash_matched_pairs", 0)))
        if car["boundary"]:
            boundary_constraints.append({"id": f"independent_separator_branch_{bit}_component_{ordinal}", "scope": list(car["boundary"]), "allowed": [list(x) for x in car["rows"]]})

    target = set(int(x) for x in bp["ready"]["component"])
    constraints = [json.loads(json.dumps(rel)) for gi, rel in enumerate(bp["canonical"]["constraints"]) if gi not in target]
    constraints.extend(boundary_constraints)
    transformed = canonicalize_raw({"variables": list(bp["canonical"]["variables"]), "constraints": constraints})
    transformed_components = parent_support.constraint_components_after_cut(transformed, list(bp["ready"]["cut"]))
    handoff = guarded.run_guarded_elimination(transformed, list(bp["ready"]["cut"]), transformed_components)
    metrics = {
        "bit": int(bit),
        "residual_components": [list(c) for c in bp["components"]],
        "residual_component_sizes": [len(c) for c in bp["components"]],
        "pair_join_count": pair_joins,
        "pair_rows_examined": pair_rows_examined,
        "three_plus_join_chains_materialized": 0,
        "global_residual_cartesian_products_materialized": 0,
        "handoff_terminal": handoff.get("status"),
    }
    if handoff.get("status") == "EXACT_UNSAT_BY_COMPLETE_GUARDED_ELIMINATION":
        return {"status": "BRANCH_EXACT_UNSAT_BY_HANDOFF", "terminal_class": "EXACT_UNSAT", **metrics}
    if handoff.get("status") != "ADMIT_EXACT_GUARDED_BOUNDED_OUTPUT_ELIMINATION":
        return {"status": "BRANCH_OPEN_HANDOFF", "terminal_class": "OPEN", **metrics}

    assignment = {int(k): int(v) for k, v in handoff["witness"]["assignment"].items()}
    target_internal = {
        int(v)
        for gi in bp["ready"]["component"]
        for v in bp["canonical"]["constraints"][gi]["scope"]
        if int(v) not in cut
    }
    for v in target_internal:
        assignment.pop(v, None)
    for v, value in zip(bp["core"], bp["state"]):
        assignment[int(v)] = int(value)
    chosen_rows = []
    for car in carriers:
        key = tuple(int(assignment[v]) for v in car["boundary"])
        witness = car["witness"].get(key)
        if witness is None:
            return {"status": "BRANCH_OPEN_ORIGINAL_WITNESS_REPLAY_FAILURE", "terminal_class": "OPEN", "reason": "BOUNDARY_WITNESS_MISSING", **metrics}
        rows = [witness] if len(car["factors"]) == 1 else list(witness)
        for factor, row in zip(car["factors"], rows):
            for v, value in zip(factor["scope"], row):
                v, value = int(v), int(value)
                if v in assignment and assignment[v] != value:
                    return {"status": "BRANCH_OPEN_ORIGINAL_WITNESS_REPLAY_FAILURE", "terminal_class": "OPEN", "reason": "RECONSTRUCTION_CONFLICT", "factor_id": factor["id"], "variable": v, **metrics}
                assignment[v] = value
            chosen_rows.append({"factor_id": factor["id"], "sorted_row": list(row)})
    verified = guarded.verify_original_assignment(bp["canonical"], assignment)
    if not verified:
        return {"status": "BRANCH_OPEN_ORIGINAL_WITNESS_REPLAY_FAILURE", "terminal_class": "OPEN", "reason": "ORIGINAL_RELATION_REPLAY_FAILED", **metrics}
    return {
        "status": "BRANCH_EXACT_SAT",
        "terminal_class": "EXACT_SAT",
        "witness": {str(v): int(assignment[v]) for v in sorted(assignment)},
        "witness_verified": True,
        "reconstruction_rows": chosen_rows,
        **metrics,
    }


def solve_independent(raw: dict) -> dict:
    prep = prepare_independent(raw)
    if prep.get("status") != "READY":
        return prep
    discovery = discover_separator_independent(prep)
    if discovery.get("status") != "ADMIT_SEPARATOR_PROPOSAL":
        return discovery
    separator = int(discovery["separator"])
    branches = [solve_branch_independent(prep, separator, bit) for bit in (0, 1)]
    sat = [b for b in branches if b.get("terminal_class") == "EXACT_SAT"]
    unsat = [b for b in branches if b.get("terminal_class") == "EXACT_UNSAT"]
    receipt = {
        "separator_variable": separator,
        "candidate_variables_examined": discovery["candidate_variables_examined"],
        "all_valid_separators": discovery["all_valid_separators"],
        "branch_count": 2,
        "branch_classes": [b.get("terminal_class") for b in branches],
        "branch_terminals": [b.get("status") for b in branches],
        "three_plus_join_chains_materialized": sum(int(b.get("three_plus_join_chains_materialized", 0)) for b in branches),
        "global_residual_cartesian_products_materialized": sum(int(b.get("global_residual_cartesian_products_materialized", 0)) for b in branches),
    }
    if sat:
        chosen = sorted(sat, key=lambda x: int(x["bit"]))[0]
        return {"status": "ADMIT_EXACT_UNIQUE_CORE_RESIDUAL_SINGLE_VARIABLE_SEPARATOR_FACTORIZED_PAYLOAD", "discovery": discovery, "branches": branches, "receipt": receipt, "witness_verified": chosen.get("witness_verified") is True}
    if len(unsat) == 2:
        return {"status": "EXACT_UNSAT_BY_RESIDUAL_SINGLE_VARIABLE_SEPARATOR_BRANCHES", "discovery": discovery, "branches": branches, "receipt": receipt, "witness_verified": True}
    return {"status": "OPEN_RESIDUAL_SEPARATOR_BRANCH_UNRESOLVED", "discovery": discovery, "branches": branches, "receipt": receipt}


def _branch_classes(result: dict) -> list[str | None]:
    carrier = result.get("carrier", result)
    return [x.get("terminal_class") for x in carrier.get("branches", [])]


def run() -> dict:
    positive_raw = cand.positive_control()
    one_raw = cand.one_branch_unsat_one_sat_control()
    both_raw = cand.both_branches_unsat_control()
    noart_raw = cand.no_single_variable_articulation_control()
    multiple_raw = cand.multiple_common_core_states_control()

    cpos = cand.explain(positive_raw)
    ipos = solve_independent(positive_raw)
    cone = cand.explain(one_raw)
    ione = solve_independent(one_raw)
    cboth = cand.explain(both_raw)
    iboth = solve_independent(both_raw)
    cno = cand.explain(noart_raw)
    ino = solve_independent(noart_raw)
    cmulti = cand.explain(multiple_raw)
    imulti = solve_independent(multiple_raw)
    hint = cand.explain(cand.injected_hint_control())
    tamper = cand.tampered_control()
    invalid = cand.invalid_separator_branch_guard_control()

    cp = cpos.get("carrier", {})
    creceipt = cp.get("receipt", {})
    checks = {
        "G1_candidate_blob_frozen": blob(root() / CANDIDATE) == CANDIDATE_BLOB,
        "G1_source_guard": cand.source_guard().get("ok") is True,
        "G2_positive_predecessor_is_v36_gt2": cand.base_prepare(positive_raw).get("status") == "READY",
        "G3_candidate_discovers_47": cp.get("discovery", {}).get("separator") == 47,
        "G3_independent_discovers_47": ipos.get("discovery", {}).get("separator") == 47,
        "G3_discovery_agrees": cp.get("discovery", {}).get("all_valid_separators") == ipos.get("discovery", {}).get("all_valid_separators"),
        "G4_candidate_positive_sat": cpos.get("status") == "ADMIT_EXACT_UNIQUE_CORE_RESIDUAL_SINGLE_VARIABLE_SEPARATOR_FACTORIZED_PAYLOAD" and cp.get("witness_verified") is True,
        "G4_independent_positive_sat": ipos.get("status") == "ADMIT_EXACT_UNIQUE_CORE_RESIDUAL_SINGLE_VARIABLE_SEPARATOR_FACTORIZED_PAYLOAD" and ipos.get("witness_verified") is True,
        "G4_exactly_two_branches_candidate": creceipt.get("branch_count") == 2 and len(cp.get("branches", [])) == 2,
        "G4_exactly_two_branches_independent": ipos.get("receipt", {}).get("branch_count") == 2 and len(ipos.get("branches", [])) == 2,
        "G5_candidate_zero_3plus_join": creceipt.get("three_plus_join_chains_materialized") == 0,
        "G5_independent_zero_3plus_join": ipos.get("receipt", {}).get("three_plus_join_chains_materialized") == 0,
        "G5_candidate_zero_global_product": creceipt.get("global_residual_cartesian_products_materialized") == 0,
        "G5_independent_zero_global_product": ipos.get("receipt", {}).get("global_residual_cartesian_products_materialized") == 0,
        "G6_candidate_one_unsat_one_sat": cone.get("status") == "ADMIT_EXACT_UNIQUE_CORE_RESIDUAL_SINGLE_VARIABLE_SEPARATOR_FACTORIZED_PAYLOAD" and sorted(_branch_classes(cone)) == ["EXACT_SAT", "EXACT_UNSAT"],
        "G6_independent_one_unsat_one_sat": ione.get("status") == "ADMIT_EXACT_UNIQUE_CORE_RESIDUAL_SINGLE_VARIABLE_SEPARATOR_FACTORIZED_PAYLOAD" and sorted(_branch_classes(ione)) == ["EXACT_SAT", "EXACT_UNSAT"],
        "G7_candidate_both_unsat": cboth.get("status") == "EXACT_UNSAT_BY_RESIDUAL_SINGLE_VARIABLE_SEPARATOR_BRANCHES" and _branch_classes(cboth).count("EXACT_UNSAT") == 2,
        "G7_independent_both_unsat": iboth.get("status") == "EXACT_UNSAT_BY_RESIDUAL_SINGLE_VARIABLE_SEPARATOR_BRANCHES" and _branch_classes(iboth).count("EXACT_UNSAT") == 2,
        "G8_candidate_no_articulation_open": cno.get("status") == "OPEN_NO_RESIDUAL_SINGLE_VARIABLE_SEPARATOR",
        "G8_independent_no_articulation_open": ino.get("status") == "OPEN_NO_RESIDUAL_SINGLE_VARIABLE_SEPARATOR",
        "G9_candidate_multiple_core_open": cmulti.get("status") == "OPEN_NONUNIQUE_COMMON_CORE_SUPPORT",
        "G9_independent_multiple_core_open": imulti.get("status") == "OPEN_NONUNIQUE_COMMON_CORE_SUPPORT",
        "G10_hint_rejected": hint.get("status") == "REJECT_RAW_INPUT",
        "G10_tamper_rejected": tamper.get("status") == "REJECT_TAMPERED_PROVENANCE",
        "G11_invalid_separator_guard_open": invalid.get("status") == "BRANCH_OPEN_RESIDUAL_COMPONENT_GT2" and invalid.get("terminal_class") == "OPEN",
        "G12_no_budget_raise": creceipt.get("budget_raised") is False,
        "G12_no_alt_orders": creceipt.get("alternative_orders") == 0,
        "G12_no_external_solver": creceipt.get("external_solver_calls") == 0,
        "G12_no_generic_transfer": creceipt.get("generic_transfer_calls") == 0,
        "FW_p_vs_np": cand.firewall()["P_VS_NP"] == "OPEN",
        "FW_general_sat": cand.firewall()["GENERAL_SAT_IN_P"] == "NOT_PROVED",
        "FW_general_separator": cand.firewall()["GENERAL_RESIDUAL_SEPARATOR_TRACTABILITY"] == "NOT_PROVED",
    }
    verdict = VERDICT if all(checks.values()) else "FAIL_OR_OPEN_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_SINGLE_VARIABLE_SEPARATOR_FACTORIZED_PAYLOAD_V1"
    return {
        "artifact_id": ARTIFACT_ID,
        "authority": "INDEPENDENT_CHECKER__SCOPED_ONLY",
        "checks": checks,
        "controls": {
            "positive_candidate": cpos.get("status"),
            "positive_independent": ipos.get("status"),
            "positive_separator_candidate": cp.get("discovery", {}).get("separator"),
            "positive_separator_independent": ipos.get("discovery", {}).get("separator"),
            "positive_candidate_branches": creceipt.get("branch_classes"),
            "positive_independent_branches": ipos.get("receipt", {}).get("branch_classes"),
            "one_candidate": cone.get("status"),
            "one_candidate_branches": _branch_classes(cone),
            "one_independent": ione.get("status"),
            "one_independent_branches": _branch_classes(ione),
            "both_candidate": cboth.get("status"),
            "both_candidate_branches": _branch_classes(cboth),
            "both_independent": iboth.get("status"),
            "both_independent_branches": _branch_classes(iboth),
            "no_articulation_candidate": cno.get("status"),
            "no_articulation_independent": ino.get("status"),
            "multiple_candidate": cmulti.get("status"),
            "multiple_independent": imulti.get("status"),
            "hint": hint.get("status"),
            "tamper": tamper.get("status"),
            "invalid_separator_branch_guard": invalid.get("status"),
        },
        "independent_methods": {
            "separator_discovery": "SEPARATE_BFS_COMPONENT_REPLAY_PER_RESIDUAL_VARIABLE",
            "row_restriction": "SEPARATE_SCOPE_POSITION_FILTER",
            "pair_carrier": "SEALED_V3_6_INDEPENDENT_HASH_INDEX_PAIR_CARRIER",
            "candidate_separator_helpers_used": False,
            "candidate_row_restriction_helpers_used": False,
            "three_plus_join_chains_materialized": 0,
            "global_residual_cartesian_products_materialized": 0,
        },
        "scientific_firewall": cand.firewall(),
        "verdict": verdict,
    }


def main() -> None:
    print(json.dumps(run(), sort_keys=True))


if __name__ == "__main__":
    main()
