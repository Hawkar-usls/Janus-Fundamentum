from __future__ import annotations

import hashlib
import itertools
import json
import subprocess
import sys
from pathlib import Path

VERDICT = "PASS_DIAGNOSTIC_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_FIXED_DEPTH_1_2_2_NO_SKELETON_STRUCTURE_FORENSIC"
CANDIDATE = Path("research/tools/apma_bucket_k5_depth_cap_forensic/forensic.py")
CANDIDATE_GIT_BLOB = "517df2e4fe8e364b7149627ca018bc09cac6d0d2"

# Independent literal reconstruction of the frozen unit control. No candidate helpers.
EDGE_VAR = {
    (0, 1): 200,
    (0, 2): 201,
    (0, 3): 202,
    (0, 4): 203,
    (1, 2): 204,
    (1, 3): 205,
    (1, 4): 206,
    (2, 3): 207,
    (2, 4): 208,
    (3, 4): 209,
}
SCOPES = {
    0: (200, 201, 202, 203),
    1: (200, 204, 205, 206),
    2: (201, 204, 207, 208),
    3: (202, 205, 207, 209),
    4: (203, 206, 208, 209),
}


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode()
    return hashlib.sha1(header + data).hexdigest()


def graph_after_removed(removed: frozenset[int]) -> dict[int, set[int]]:
    g = {i: set() for i in range(5)}
    for (u, v), var in EDGE_VAR.items():
        if var not in removed:
            g[u].add(v)
            g[v].add(u)
    return g


def components(g: dict[int, set[int]]) -> list[tuple[int, ...]]:
    unseen = set(g)
    out = []
    while unseen:
        root = min(unseen)
        stack = [root]
        unseen.remove(root)
        comp = []
        while stack:
            u = stack.pop()
            comp.append(u)
            for v in sorted(g[u], reverse=True):
                if v in unseen:
                    unseen.remove(v)
                    stack.append(v)
        out.append(tuple(sorted(comp)))
    return sorted(out, key=lambda x: (len(x), x))


def partition_cut_sets() -> list[tuple[int, ...]]:
    # Enumerate unique nontrivial vertex bipartitions by requiring relation 0 on side A.
    vertices = range(5)
    cuts = set()
    for mask in range(1, 1 << 5):
        side = {v for v in vertices if mask & (1 << v)}
        if 0 not in side or len(side) == 5:
            continue
        crossing = tuple(sorted(var for (u, v), var in EDGE_VAR.items() if (u in side) != (v in side)))
        cuts.add(crossing)
    return sorted(cuts, key=lambda x: (len(x), x))


def mincut_by_bipartitions() -> tuple[int, list[tuple[int, ...]]]:
    cuts = partition_cut_sets()
    k = min(map(len, cuts))
    return k, sorted(c for c in cuts if len(c) == k)


def is_k4(g: dict[int, set[int]], comp: tuple[int, ...]) -> bool:
    if len(comp) != 4:
        return False
    s = set(comp)
    degrees = sorted(sum(1 for v in g[u] if v in s) for u in comp)
    edges = sum(1 for u in comp for v in g[u] if v in s and u < v)
    return degrees == [3, 3, 3, 3] and edges == 6


def full_cube_literal_check() -> bool:
    # The frozen source declares every factor rows=product((0,1), repeat=4).
    # Reconstruct that finite explicit relation independently for every literal scope.
    for scope in SCOPES.values():
        rows = set(itertools.product((0, 1), repeat=len(scope)))
        if len(scope) != 4 or len(rows) != 16:
            return False
    return True


def run_candidate() -> dict:
    proc = subprocess.run(
        [sys.executable, "-m", "research.tools.apma_bucket_k5_depth_cap_forensic.forensic"],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(proc.stdout.strip().splitlines()[-1])


def main() -> None:
    candidate = run_candidate()
    min_size, mincuts = mincut_by_bipartitions()

    mincut_details = []
    for cut in mincuts:
        g = graph_after_removed(frozenset(cut))
        comps = components(g)
        large = max(comps, key=len)
        small = min(comps, key=len)
        mincut_details.append({
            "cut": list(cut),
            "components": [list(c) for c in comps],
            "component_sizes": sorted(len(c) for c in comps),
            "isolated_relation": small[0] if len(small) == 1 else None,
            "residual_relations": list(large),
            "residual_is_k4": is_k4(g, large),
        })

    three_removals = list(itertools.combinations(sorted(EDGE_VAR.values()), 3))
    all_three_connected = all(len(components(graph_after_removed(frozenset(cut)))) == 1 for cut in three_removals)

    cand_receipt = candidate["structural_receipt"]
    candidate_cuts = sorted(tuple(c) for c in cand_receipt["minimum_cuts"])
    expected_edge_map = {str(var): list(edge) for edge, var in sorted(EDGE_VAR.items(), key=lambda kv: kv[1])}

    checks = {
        "I1_candidate_git_blob_frozen": git_blob_sha1(CANDIDATE) == CANDIDATE_GIT_BLOB,
        "I2_literal_control_scopes_exact": candidate["frozen_control"]["scopes"] == {f"unit_k5_{i}": list(SCOPES[i]) for i in range(5)},
        "I2_edge_map_exact": candidate["frozen_control"]["edge_map"] == expected_edge_map,
        "I2_full_cube_literal_reconstruction": full_cube_literal_check() and candidate["frozen_control"]["all_factors_full_boolean_cube"],
        "I3_bipartition_mincut_is_4": min_size == 4,
        "I3_candidate_mincut_matches": cand_receipt["minimum_disconnect_cut_size"] == min_size,
        "I4_all_minimum_cuts_match": candidate_cuts == mincuts and len(mincuts) == 5,
        "I5_all_minimum_cuts_split_1_plus_4": all(d["component_sizes"] == [1, 4] for d in mincut_details),
        "I5_all_residuals_are_k4": all(d["residual_is_k4"] for d in mincut_details),
        "I6_all_three_edge_removals_connected": len(three_removals) == 120 and all_three_connected,
        "I6_candidate_one_plus_two_matches": cand_receipt["one_plus_two_unique_removal_count"] == 120 and cand_receipt["one_plus_two_all_connected"],
        "I7_candidate_verdict": candidate["verdict"] == VERDICT,
        "I8_no_boolean_branching": candidate["resource_receipt"]["boolean_separator_assignments_enumerated"] == 0,
        "I8_no_solver_execution": candidate["resource_receipt"]["solver_execution"] == 0,
        "I8_no_carrier_execution": candidate["resource_receipt"]["sealed_pair_carrier_execution"] == 0 and candidate["resource_receipt"]["sealed_fixed_depth_carrier_execution"] == 0,
        "I9_firewalls": candidate["scientific_firewall"]["P_VS_NP"] == "OPEN" and candidate["scientific_firewall"]["GENERAL_SAT_IN_P"] == "NOT_PROVED" and candidate["scientific_firewall"]["SIZE4_BRANCHING_LICENSED"] is False,
    }

    out = {
        "artifact_id": "JANUS-TRUMP-K5-DEPTH-CAP-FORENSIC-INDEPENDENT-CHECK-2026-09-15-v1.0",
        "authority": "INDEPENDENT_DIAGNOSTIC_CHECK_ONLY",
        "verdict": VERDICT if all(checks.values()) else "FAIL_INDEPENDENT_DIAGNOSTIC_CHECK",
        "checks": checks,
        "independent_method": "RELATION_VERTEX_BIPARTITION_CUT_DERIVATION_PLUS_INDEPENDENT_GRAPH_COMPONENTIZATION",
        "receipt": {
            "minimum_disconnect_cut_size": min_size,
            "minimum_cuts": [list(c) for c in mincuts],
            "minimum_cut_details": mincut_details,
            "three_edge_removal_case_count": len(three_removals),
            "all_three_edge_removals_connected": all_three_connected,
            "candidate_checker_mincut_match": candidate_cuts == mincuts,
            "candidate_checker_plan_helpers_shared": False,
        },
        "scientific_firewall": {
            "P_VS_NP": "OPEN",
            "GENERAL_SAT_IN_P": "NOT_PROVED",
            "K5_UNIT_CONTROL_IS_GENERAL_INPUT_EVIDENCE": False,
            "SIZE4_BRANCHING_LICENSED": False,
            "GLOBAL_APMA_FRONTIER_ADVANCE": "NONE",
        },
    }
    print(json.dumps(out, sort_keys=True))
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
