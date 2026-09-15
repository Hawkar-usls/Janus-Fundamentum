from __future__ import annotations

import itertools
import json
from collections import deque

ARTIFACT_ID = "JANUS-TRUMP-BICAMERAL-BUCKET-UNIQUE-CORE-RESIDUAL-FIXED-DEPTH-1-2-2-NO-SKELETON-STRUCTURE-FORENSIC-2026-09-15-v1.0"
VERDICT = "PASS_DIAGNOSTIC_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_FIXED_DEPTH_1_2_2_NO_SKELETON_STRUCTURE_FORENSIC"


def build_edge_map() -> dict[tuple[int, int], int]:
    edge_var: dict[tuple[int, int], int] = {}
    nxt = 200
    for i in range(5):
        for j in range(i + 1, 5):
            edge_var[(i, j)] = nxt
            nxt += 1
    return edge_var


def build_frozen_control() -> list[dict]:
    edge_var = build_edge_map()
    factors = []
    for i in range(5):
        scope = tuple(sorted(edge_var[tuple(sorted((i, j)))] for j in range(5) if j != i))
        rows = tuple(itertools.product((0, 1), repeat=len(scope)))
        factors.append({"id": f"unit_k5_{i}", "scope": scope, "rows": rows})
    return factors


def verify_full_cube(factors: list[dict]) -> bool:
    for f in factors:
        expected = set(itertools.product((0, 1), repeat=len(f["scope"])))
        if set(f["rows"]) != expected:
            return False
    return True


def relation_graph(factors: list[dict], removed: frozenset[int] = frozenset()) -> dict[int, set[int]]:
    scopes = [set(f["scope"]) - set(removed) for f in factors]
    g = {i: set() for i in range(len(factors))}
    for i in range(len(factors)):
        for j in range(i + 1, len(factors)):
            if scopes[i] & scopes[j]:
                g[i].add(j)
                g[j].add(i)
    return g


def components(g: dict[int, set[int]]) -> list[tuple[int, ...]]:
    unseen = set(g)
    out: list[tuple[int, ...]] = []
    while unseen:
        root = min(unseen)
        q = deque([root])
        unseen.remove(root)
        comp = []
        while q:
            u = q.popleft()
            comp.append(u)
            for v in sorted(g[u]):
                if v in unseen:
                    unseen.remove(v)
                    q.append(v)
        out.append(tuple(sorted(comp)))
    return sorted(out, key=lambda c: (len(c), c))


def graph_signature(g: dict[int, set[int]], vertices: tuple[int, ...]) -> dict:
    vs = set(vertices)
    edge_count = sum(1 for u in vs for v in g[u] if v in vs and u < v)
    degrees = sorted(sum(1 for v in g[u] if v in vs) for u in vs)
    return {
        "vertex_count": len(vertices),
        "edge_count": edge_count,
        "degree_sequence": degrees,
        "is_k4": len(vertices) == 4 and edge_count == 6 and degrees == [3, 3, 3, 3],
    }


def profile() -> dict:
    factors = build_frozen_control()
    edge_var = build_edge_map()
    variables = tuple(sorted(edge_var.values()))
    base_graph = relation_graph(factors)
    base_components = components(base_graph)

    cut_records = []
    disconnected_counts: dict[int, int] = {}
    tested_counts: dict[int, int] = {}
    minimum_size = None
    minimum_records = []

    for k in range(5):
        tested = 0
        disconnected = 0
        records_k = []
        for cut in itertools.combinations(variables, k):
            tested += 1
            g = relation_graph(factors, frozenset(cut))
            comps = components(g)
            if len(comps) > 1:
                disconnected += 1
                record = {
                    "cut": list(cut),
                    "components": [list(c) for c in comps],
                    "component_sizes": sorted(len(c) for c in comps),
                }
                records_k.append(record)
                cut_records.append(record)
        tested_counts[k] = tested
        disconnected_counts[k] = disconnected
        if disconnected and minimum_size is None:
            minimum_size = k
            minimum_records = records_k

    one_plus_two_unique = set()
    for root in variables:
        remaining = [v for v in variables if v != root]
        for pair in itertools.combinations(remaining, 2):
            one_plus_two_unique.add(tuple(sorted((root,) + pair)))
    one_plus_two_profiles = []
    for removed in sorted(one_plus_two_unique):
        comps = components(relation_graph(factors, frozenset(removed)))
        one_plus_two_profiles.append((removed, tuple(sorted(len(c) for c in comps))))

    mincut_details = []
    for rec in minimum_records:
        cut = tuple(rec["cut"])
        g = relation_graph(factors, frozenset(cut))
        comps = components(g)
        nontrivial = max(comps, key=len)
        isolated = min(comps, key=len)
        sig = graph_signature(g, nontrivial)
        residual_vars = sorted(
            v for v, endpoints in ((var, edge) for edge, var in edge_var.items())
            if v not in cut and endpoints[0] in nontrivial and endpoints[1] in nontrivial
        )
        mincut_details.append({
            "cut": list(cut),
            "isolated_relation": isolated[0] if len(isolated) == 1 else None,
            "residual_relations": list(nontrivial),
            "residual_variables": residual_vars,
            "component_sizes": sorted(len(c) for c in comps),
            "residual_graph_signature": sig,
        })

    expected_edges = {str(var): list(edge) for edge, var in sorted(edge_var.items(), key=lambda kv: kv[1])}
    checks = {
        "F1_full_cube_factors": verify_full_cube(factors),
        "F2_factor_count_5": len(factors) == 5,
        "F2_edge_variable_count_10": len(edge_var) == 10 and variables == tuple(range(200, 210)),
        "F3_base_graph_k5": base_components == [(0, 1, 2, 3, 4)] and all(len(base_graph[i]) == 4 for i in base_graph),
        "F4_no_disconnect_cut_le3": all(disconnected_counts[k] == 0 for k in range(4)),
        "F5_min_disconnect_cut_4": minimum_size == 4,
        "F5_min_cut_count_5": len(minimum_records) == 5,
        "F6_all_min_cuts_one_plus_four": all(d["component_sizes"] == [1, 4] for d in mincut_details),
        "F6_all_residuals_k4": all(d["residual_graph_signature"]["is_k4"] for d in mincut_details),
        "F7_all_one_plus_two_removals_connected": len(one_plus_two_profiles) == 120 and all(pat == (5,) for _, pat in one_plus_two_profiles),
        "F8_zero_boolean_assignment_branches": True,
        "F8_zero_solver_execution": True,
        "F8_zero_carrier_execution": True,
    }

    return {
        "artifact_id": ARTIFACT_ID,
        "authority": "DIAGNOSTIC_ONLY__NO_SCIENTIFIC_PROMOTION",
        "verdict": VERDICT if all(checks.values()) else "FAIL_DIAGNOSTIC_RECEIPT_MISMATCH",
        "checks": checks,
        "frozen_control": {
            "factor_count": len(factors),
            "residual_variable_count": len(variables),
            "edge_map": expected_edges,
            "scopes": {f["id"]: list(f["scope"]) for f in factors},
            "all_factors_full_boolean_cube": verify_full_cube(factors),
            "raw_reachability_authority": False,
            "unit_test_only": True,
        },
        "structural_receipt": {
            "tested_cut_counts_by_cardinality": {str(k): tested_counts[k] for k in tested_counts},
            "disconnected_cut_counts_by_cardinality": {str(k): disconnected_counts[k] for k in disconnected_counts},
            "minimum_disconnect_cut_size": minimum_size,
            "minimum_cut_count": len(minimum_records),
            "minimum_cuts": [d["cut"] for d in mincut_details],
            "minimum_cut_details": mincut_details,
            "one_plus_two_unique_removal_count": len(one_plus_two_profiles),
            "one_plus_two_all_connected": all(pat == (5,) for _, pat in one_plus_two_profiles),
            "captain_explanation": "K5_RELATION_OVERLAP_EDGE_CONNECTIVITY_4__THE_FROZEN_1_PLUS_2_STRUCTURAL_REMOVAL_CAN_DELETE_ONLY_THREE_DISTINCT_OVERLAP_EDGES_SO_THE_FIVE_RELATION_COMPONENT_CANNOT_DISCONNECT_AT_THAT_STAGE",
            "cheapest_visible_post_cut_shape": "FOUR_EDGE_MINCUT_DISCONNECTS_AS_SINGLETON_PLUS_K4__DIAGNOSTIC_ONLY__NO_BRANCHING_LICENSE",
        },
        "resource_receipt": {
            "boolean_separator_assignments_enumerated": 0,
            "sat_branch_execution": 0,
            "solver_execution": 0,
            "sealed_pair_carrier_execution": 0,
            "sealed_fixed_depth_carrier_execution": 0,
            "three_plus_join_chains_materialized": 0,
            "global_residual_cartesian_products_materialized": 0,
            "unbounded_recursive_search": False,
            "budget_raise": False,
        },
        "scientific_firewall": {
            "P_VS_NP": "OPEN",
            "GENERAL_SAT_IN_P": "NOT_PROVED",
            "CONNECTED_MIXED_CORE_SOLVED": "NO",
            "GENERAL_RESIDUAL_SEPARATOR_TRACTABILITY": "NOT_PROVED",
            "K5_UNIT_CONTROL_IS_GENERAL_INPUT_EVIDENCE": False,
            "SIZE4_BRANCHING_LICENSED": False,
            "GLOBAL_APMA_FRONTIER_ADVANCE": "NONE",
        },
    }


def main() -> None:
    print(json.dumps(profile(), sort_keys=True))


if __name__ == "__main__":
    main()
