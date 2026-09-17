from __future__ import annotations

import hashlib
import itertools
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from research.tools.apma_satlib_uf20_r000_r111_projected_core_replay import projection_identity

ROOT = Path(__file__).resolve().parents[3]
PREREG = ROOT / "research/TRUMP_UF20_02_04_05_COMMON_INVARIANT_DIFFERENTIAL_PROFILING_PREREGISTRATION_2026-09-17_v1.0.json"
REVIEW = ROOT / "research/TRUMP_UF20_02_04_05_COMMON_INVARIANT_DIFFERENTIAL_PROFILING_REVIEW_2026-09-17_v1.0.json"
REDUCTION = ROOT / "research/TRUMP_SATLIB_UF20_R000_R111_RAW_BOUND_PENDANT_EXACT_SIMULTANEOUS_ONE_ROUND_REDUCTION_RESULT_2026-09-17_v1.1.json"
PROJECTION = ROOT / "research/tools/apma_satlib_uf20_r000_r111_projected_core_replay/projection_identity.py"

EXPECTED_BLOBS = {
    PREREG: "253da0ce5aa987dcb4bc4bfd84165166315d8348",
    REVIEW: "5b4eaa77a0bc2cd442f160f4eaaa40c0623c9f2e",
    REDUCTION: "d91cb675e3d06fed92f97d96d6b3a0733f8be5df",
    PROJECTION: "2ef48e73974a5f43d3f4fb4809ebd0c09c0f5be4",
}
SOURCE_BLOBS = {
    "UF20_02": (ROOT / "research/source_data/SATLIB_UF20_02_2026-09-16.cnf", "f924caaef0d868bf62b1658e83e030ad8daee865"),
    "UF20_03": (ROOT / "research/source_data/SATLIB_UF20_03_2026-09-16.cnf", "8f3d15154515457281f49201b843f2a7134dfa9f"),
    "UF20_04": (ROOT / "research/source_data/SATLIB_UF20_04_2026-09-16.cnf", "34ced5c169f967b2dc44ef5e42f2ee2c924813e1"),
    "UF20_05": (ROOT / "research/source_data/SATLIB_UF20_05_2026-09-16.cnf", "3b04eff26ee37bdd0bc21b1066486974f92a2c9b"),
}
ORDER = ("UF20_02", "UF20_03", "UF20_04", "UF20_05")
BLOCKERS = ("UF20_02", "UF20_04", "UF20_05")
CONTROL = "UF20_03"
ELIGIBLE_FEATURES = (
    "ARTICULATION_AND_BICONNECTED_BLOCK_COUNTS",
    "CONSTRAINT_ARITY_MULTISET",
    "CONSTRAINT_COUNT",
    "EXACT_LOCAL_RELATION_TABLE_SIGNATURES",
    "INCIDENCE_CONNECTEDNESS",
    "INCIDENCE_CYCLE_RANK",
    "PAIRWISE_VARIABLE_COOCCURRENCE_COUNTS",
    "VARIABLE_COUNT",
    "VARIABLE_DEGREE_MULTISET",
)


def git_blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def canonical_sha(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def node_key(node: tuple[str, Any]) -> tuple[str, str]:
    return (node[0], str(node[1]))


def build_graph(raw: dict[str, Any]):
    adjacency: dict[tuple[str, Any], set[tuple[str, Any]]] = defaultdict(set)
    variables = sorted({int(v) for v in raw["variables"]})
    for v in variables:
        adjacency[("v", v)]
    for c in raw["constraints"]:
        cn = ("c", str(c["id"]))
        adjacency[cn]
        for v in sorted({int(x) for x in c["scope"]}):
            vn = ("v", v)
            adjacency[vn].add(cn)
            adjacency[cn].add(vn)
    return adjacency


def component_count(adjacency) -> int:
    seen = set()
    count = 0
    for start in sorted(adjacency, key=node_key):
        if start in seen:
            continue
        count += 1
        stack = [start]
        seen.add(start)
        while stack:
            u = stack.pop()
            for v in sorted(adjacency[u], key=node_key):
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
    return count


def articulation_and_blocks(adjacency) -> list[int]:
    disc: dict[Any, int] = {}
    low: dict[Any, int] = {}
    parent: dict[Any, Any] = {}
    articulation = set()
    edge_stack: list[tuple[Any, Any]] = []
    blocks = 0
    clock = 0

    def dfs(u):
        nonlocal clock, blocks
        clock += 1
        disc[u] = low[u] = clock
        children = 0
        for v in sorted(adjacency[u], key=node_key):
            if v not in disc:
                parent[v] = u
                children += 1
                edge_stack.append((u, v))
                dfs(v)
                low[u] = min(low[u], low[v])
                is_root = u not in parent
                if (is_root and children > 1) or ((not is_root) and low[v] >= disc[u]):
                    articulation.add(u)
                if low[v] >= disc[u]:
                    blocks += 1
                    while edge_stack:
                        e = edge_stack.pop()
                        if e == (u, v):
                            break
            elif parent.get(u) != v and disc[v] < disc[u]:
                low[u] = min(low[u], disc[v])
                edge_stack.append((u, v))

    for start in sorted(adjacency, key=node_key):
        if start not in disc:
            dfs(start)
            if edge_stack:
                blocks += 1
                edge_stack.clear()
    return [len(articulation), blocks]


def relation_signature(constraint: dict[str, Any]) -> str:
    arity = len({int(v) for v in constraint["scope"]})
    allowed = sorted("".join(str(int(bit)) for bit in row) for row in constraint["allowed"])
    return f"arity={arity}|allowed={'/'.join(allowed)}"


def features(raw: dict[str, Any]) -> dict[str, Any]:
    variables = sorted({int(v) for v in raw["variables"]})
    constraints = list(raw["constraints"])
    adjacency = build_graph(raw)
    comps = component_count(adjacency)
    degrees = {v: 0 for v in variables}
    co = {(a, b): 0 for a, b in itertools.combinations(variables, 2)}
    edge_count = 0
    arities = []
    for c in constraints:
        scope = sorted({int(v) for v in c["scope"]})
        arities.append(len(scope))
        edge_count += len(scope)
        for v in scope:
            degrees[v] += 1
        for pair in itertools.combinations(scope, 2):
            co[pair] += 1
    return {
        "VARIABLE_COUNT": len(variables),
        "CONSTRAINT_COUNT": len(constraints),
        "INCIDENCE_CONNECTEDNESS": comps == 1,
        "VARIABLE_DEGREE_MULTISET": sorted(degrees.values()),
        "CONSTRAINT_ARITY_MULTISET": sorted(arities),
        "PAIRWISE_VARIABLE_COOCCURRENCE_COUNTS": sorted(co.values()),
        "INCIDENCE_CYCLE_RANK": edge_count - len(adjacency) + comps,
        "ARTICULATION_AND_BICONNECTED_BLOCK_COUNTS": articulation_and_blocks(adjacency),
        "EXACT_LOCAL_RELATION_TABLE_SIGNATURES": sorted(relation_signature(c) for c in constraints),
        "AUTOMORPHISM_ORBIT_PARTITION_IF_COMPUTED_EXACTLY": "NOT_COMPUTED_NO_PREEXISTING_BOUNDED_EXACT_IMPLEMENTATION_SELECTED",
        "FROZEN_ROUTE_APPLICABILITY_BITS_FOR_EXISTING_ROUTES_ONLY": "CALIBRATION_EXCLUDED_FROM_CANDIDATE_SELECTION",
    }


def reconstruct_four() -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    reduction = json.loads(REDUCTION.read_text())
    receipts = {r["source"]: r for r in reduction["source_receipts"]}
    raws: dict[str, dict[str, Any]] = {}
    guards: dict[str, Any] = {}
    for source in ORDER:
        path, expected_source_blob = SOURCE_BLOBS[source]
        source_blob_ok = git_blob(path) == expected_source_blob
        original, _ = projection_identity.normalize_projection(source, projection_identity.parse(path))
        receipt = receipts[source]
        original_sha = canonical_sha(original)
        remove_ids = set(receipt["removed_constraint_ids"])
        remove_leaves = {int(x) for x in receipt["removed_leaves"]}
        reduced = {
            "variables": [int(v) for v in original["variables"] if int(v) not in remove_leaves],
            "constraints": [c for c in original["constraints"] if c["id"] not in remove_ids],
        }
        reduced_sha = canonical_sha(reduced)
        guard = {
            "source_blob_ok": source_blob_ok,
            "original_projected_sha_ok": original_sha == receipt["original_projected_raw"]["sha256"],
            "reduced_sha_ok": reduced_sha == receipt["reduced_raw"]["sha256"],
            "variable_count_ok": len(reduced["variables"]) == receipt["reduced_raw"]["variables"],
            "constraint_count_ok": len(reduced["constraints"]) == receipt["reduced_raw"]["constraints"],
            "observed_reduced_sha256": reduced_sha,
            "expected_reduced_sha256": receipt["reduced_raw"]["sha256"],
        }
        guard["all_ok"] = all(v for k, v in guard.items() if k.endswith("_ok"))
        guards[source] = guard
        if not guard["all_ok"]:
            raise RuntimeError(f"identity guard failure for {source}: {guard}")
        raws[source] = reduced
    return raws, guards


def main() -> dict[str, Any]:
    authority_bindings = {str(p.relative_to(ROOT)): git_blob(p) == expected for p, expected in EXPECTED_BLOBS.items()}
    if not all(authority_bindings.values()):
        return {"verdict": "FAIL_AUTHORITY_BINDING", "authority_bindings": authority_bindings}
    review = json.loads(REVIEW.read_text())
    if review.get("review_verdict") != "PASS_SCOPE_AND_SELECTION_POLICY_FROZEN_BEFORE_PROFILING_IMPLEMENTATION":
        return {"verdict": "FAIL_REVIEW_NOT_AUTHORIZED", "review_verdict": review.get("review_verdict")}
    raws, identity_guards = reconstruct_four()
    feature_rows = {source: features(raws[source]) for source in ORDER}
    candidates = []
    for name in ELIGIBLE_FEATURES:
        blocker_values = [feature_rows[s][name] for s in BLOCKERS]
        if blocker_values[0] == blocker_values[1] == blocker_values[2] and blocker_values[0] != feature_rows[CONTROL][name]:
            candidates.append(name)
    candidates = sorted(candidates)
    verdict = "COMMON_PRIMITIVE_INVARIANT_CANDIDATE_SET_FOUND__BLIND_FALSIFIER_REQUIRED" if candidates else "NO_COMMON_INVARIANT_FOUND_ON_FROZEN_PRIMITIVE_FEATURE_BASIS"
    return {
        "artifact_id": "JANUS-TRUMP-UF20-02-04-05-COMMON-INVARIANT-DIFFERENTIAL-PROFILING-CANDIDATE-2026-09-17-v1.0",
        "gate": "TRUMP_SATLIB_UF20_02_04_05_COMMON_INVARIANT_DIFFERENTIAL_PROFILING_GATE",
        "authority": "DIAGNOSTIC_ONLY__FOUR_OBJECT_DISCOVERY_VISIBILITY__NO_HISTORICAL_CONTROL_FEATURE_VALUES_READ",
        "verdict": verdict,
        "authority_bindings": authority_bindings,
        "identity_guards": identity_guards,
        "feature_rows": feature_rows,
        "eligible_feature_names": list(ELIGIBLE_FEATURES),
        "candidate_invariant_set": candidates,
        "candidate_selection_rule": "ALL_AND_ONLY_PREREGISTERED_ELIGIBLE_PRIMITIVES_WITH_IDENTICAL_VALUE_ON_UF20_02_04_05_AND_DIFFERENT_VALUE_ON_UF20_03",
        "excluded_features": {
            "AUTOMORPHISM_ORBIT_PARTITION_IF_COMPUTED_EXACTLY": "NOT_COMPUTED_NO_PREEXISTING_BOUNDED_EXACT_IMPLEMENTATION_SELECTED",
            "FROZEN_ROUTE_APPLICABILITY_BITS_FOR_EXISTING_ROUTES_ONLY": "CALIBRATION_ONLY_INELIGIBLE_BY_FROZEN_REVIEW",
        },
        "blindness_receipt": {
            "historical_control_feature_values_read": 0,
            "fresh_holdout_values_read": 0,
            "feature_conjunctions_tested": 0,
            "feature_disjunctions_tested": 0,
            "fitted_thresholds_tested": 0,
            "weighted_combinations_tested": 0,
        },
        "resource_receipt": {
            "solver_invocations": 0,
            "new_solver_rules": 0,
            "new_action_rules": 0,
            "new_carrier_mechanisms": 0,
            "new_reduction_mechanisms": 0,
            "synthetic_blockers_generated": 0,
        },
        "scientific_firewall": {
            "P_VS_NP": "OPEN",
            "GENERAL_SAT_IN_P": "NOT_PROVED",
            "CONNECTED_MIXED_CORE_SOLVED": "NO",
            "GENERAL_RESIDUAL_SEPARATOR_TRACTABILITY": "NOT_PROVED",
        },
    }


if __name__ == "__main__":
    print(json.dumps(main(), sort_keys=True, separators=(",", ":")))
