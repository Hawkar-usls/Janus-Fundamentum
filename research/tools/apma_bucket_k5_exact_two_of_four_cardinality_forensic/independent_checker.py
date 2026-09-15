from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any

from research.tools.apma_bucket_common_core import common_core_semijoin_prefilter as cc_v1
from research.tools.apma_bucket_residual_single_separator import residual_single_separator_factorized_payload as v38

VERDICT = "PASS_DIAGNOSTIC_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_K5_EXACT_TWO_OF_FOUR_CARDINALITY_STRUCTURE_FORENSIC"

PREREG = Path("research/TRUMP_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_K5_EXACT_TWO_OF_FOUR_CARDINALITY_STRUCTURE_FORENSIC_PREREGISTRATION_2026-09-15.json")
PREREG_BLOB = "11198e102ab32d12c8d49c215f2d196a624e4e50"
PARENT_STATE = Path("registry/TRUMP_CURRENT_STATE_2026-09-15_v3.16.json")
PARENT_STATE_BLOB = "32408b17271ae7f23b78b01756c47b5fc6e8d8ef"
CANDIDATE = Path("research/tools/apma_bucket_k5_exact_two_of_four_cardinality_forensic/forensic.py")
CANDIDATE_BLOB = "603457ed11867ebbc6132aa937b882bfd4257b79"
COMMON_CORE = Path("research/tools/apma_bucket_common_core/common_core_semijoin_prefilter.py")
COMMON_CORE_BLOB = "f103bf9b14e3b208200f429b75d0858c4963fa7c"
V38 = Path("research/tools/apma_bucket_residual_single_separator/residual_single_separator_factorized_payload.py")
V38_BLOB = "cd17292b7451b03b966dbcf62d1b6e4c767f7ac0"


def root() -> Path:
    return Path(__file__).resolve().parents[3]


def git_blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def source_guard() -> dict[str, Any]:
    r = root()
    checks = {
        "prereg_blob": git_blob(r / PREREG) == PREREG_BLOB,
        "parent_v3_16_blob": git_blob(r / PARENT_STATE) == PARENT_STATE_BLOB,
        "candidate_blob_bound_but_not_imported": git_blob(r / CANDIDATE) == CANDIDATE_BLOB,
        "common_core_blob": git_blob(r / COMMON_CORE) == COMMON_CORE_BLOB,
        "v3_8_prepare_blob": git_blob(r / V38) == V38_BLOB,
    }
    return {"ok": all(checks.values()), "checks": checks}


def exact_two_patterns() -> list[tuple[int, int, int, int]]:
    out: list[tuple[int, int, int, int]] = []
    for chosen in itertools.combinations(range(4), 2):
        row = [0, 0, 0, 0]
        for p in chosen:
            row[p] = 1
        out.append(tuple(row))
    return sorted(out)


def build_raw_probe_independently() -> tuple[dict[str, Any], dict[tuple[int, int], int]]:
    raw = copy.deepcopy(cc_v1.filtered_still_overbudget_control())
    targets = [next(r for r in raw["constraints"] if r["id"] == f"sticky_{i}") for i in range(5)]
    start = max(int(v) for v in raw["variables"]) + 1
    pair_to_var: dict[tuple[int, int], int] = {}
    nxt = start
    for a in range(5):
        for b in range(a + 1, 5):
            pair_to_var[(a, b)] = nxt
            nxt += 1
    raw["variables"].extend(range(start, nxt))
    patterns = exact_two_patterns()
    for vertex, rel in enumerate(targets):
        scope = [int(v) for v in rel["scope"]]
        core_scope = scope[:-2]
        core_rows = sorted({tuple(int(x) for x in row[:-2]) for row in rel["allowed"]})
        incident_vars = sorted(
            pair_to_var[tuple(sorted((vertex, other)))]
            for other in range(5)
            if other != vertex
        )
        rel["scope"] = core_scope + incident_vars
        rel["allowed"] = [list(core) + list(bits) for core in core_rows for bits in patterns]
    return raw, pair_to_var


def residual_relation(factor: dict[str, Any], core: list[int]) -> tuple[list[int], set[tuple[int, ...]]]:
    core_set = set(int(v) for v in core)
    scope = [int(v) for v in factor["scope"]]
    residual = [v for v in scope if v not in core_set]
    pos = {v: i for i, v in enumerate(scope)}
    rows = {
        tuple(int(row[pos[v]]) for v in residual)
        for row in factor["rows"]
    }
    return residual, rows


def cycle_traversal(selected_pairs: set[tuple[int, int]]) -> dict[str, Any]:
    adj = {v: [] for v in range(5)}
    for a, b in selected_pairs:
        adj[a].append(b)
        adj[b].append(a)
    degree_vector = [len(adj[v]) for v in range(5)]
    if degree_vector != [2, 2, 2, 2, 2]:
        return {"degree_vector": degree_vector, "single_five_cycle": False, "visited": []}
    visited = [0]
    prev = None
    cur = 0
    for _ in range(4):
        choices = sorted(w for w in adj[cur] if w != prev)
        nxt = next((w for w in choices if w not in visited), choices[0] if choices else None)
        if nxt is None:
            break
        visited.append(nxt)
        prev, cur = cur, nxt
    connected = len(set(visited)) == 5
    closes = connected and 0 in adj[cur]
    return {
        "degree_vector": degree_vector,
        "single_five_cycle": connected and closes,
        "visited": visited,
    }


def check(candidate: dict[str, Any]) -> dict[str, Any]:
    guard = source_guard()
    raw, pair_to_var = build_raw_probe_independently()
    prep = v38._prepare(raw)
    if prep.get("status") != "READY":
        raise RuntimeError(f"PREDECESSOR_NOT_READY:{prep.get('status')}")
    core = [int(v) for v in prep["core"]]
    factors = sorted(
        [f for f in prep["conditioned"] if str(f["id"]).startswith("sticky_")],
        key=lambda f: int(str(f["id"]).split("_", 1)[1]),
    )
    if len(factors) != 5:
        raise RuntimeError(f"EXPECTED_FIVE_TARGET_FACTORS:{len(factors)}")

    scopes: dict[int, list[int]] = {}
    rows: dict[int, set[tuple[int, ...]]] = {}
    for i, factor in enumerate(factors):
        scope, rel_rows = residual_relation(factor, core)
        scopes[i] = scope
        rows[i] = rel_rows

    expected_local_rows = set(exact_two_patterns())
    local_exact = {
        str(i): len(scopes[i]) == 4 and rows[i] == expected_local_rows
        for i in range(5)
    }

    var_to_pair = {int(var): tuple(pair) for pair, var in pair_to_var.items()}
    edge_vars = sorted(var_to_pair)
    incidence_matches_scopes = all(
        set(scopes[v]) == {
            pair_to_var[tuple(sorted((v, other)))]
            for other in range(5)
            if other != v
        }
        for v in range(5)
    )

    satisfying: list[list[int]] = []
    cycle_receipts: list[dict[str, Any]] = []
    relation_disagreements: list[list[int]] = []

    # Independent method: local exact-degree-two rows imply five selected edges by
    # the handshake identity. Enumerate only C(10,5) candidate edge subsets.
    for chosen in itertools.combinations(edge_vars, 5):
        chosen_set = set(chosen)
        degrees = [
            sum(1 for e in chosen_set if vertex in var_to_pair[e])
            for vertex in range(5)
        ]
        degree_two = degrees == [2, 2, 2, 2, 2]
        assignment = {e: int(e in chosen_set) for e in edge_vars}
        relation_sat = all(tuple(assignment[e] for e in scopes[v]) in rows[v] for v in range(5))
        if degree_two != relation_sat:
            relation_disagreements.append(list(chosen))
        if degree_two:
            selected_pairs = {var_to_pair[e] for e in chosen_set}
            cycle = cycle_traversal(selected_pairs)
            satisfying.append(sorted(chosen_set))
            cycle_receipts.append({"selected_edges": sorted(chosen_set), **cycle})

    satisfying.sort()
    candidate_receipt = candidate["finite_k5_receipt"]
    candidate_edge_map = candidate_receipt["edge_endpoint_map"]
    independent_edge_map = {str(k): list(v) for k, v in sorted(var_to_pair.items())}

    general_class = {
        "exact_equivalence": "FOR_ANY_UNDIRECTED_GRAPH_G_WITH_ONE_BOOLEAN_VARIABLE_PER_EDGE__CONJUNCTION_OVER_VERTICES_OF_SUM_INCIDENT_X_E_EQUALS_TWO_IFF_THE_SELECTED_EDGE_SET_IS_A_SPANNING_TWO_FACTOR_OF_G",
        "object": "UNDIRECTED_TWO_FACTOR",
        "f_factor_specialization": "F_FACTOR_WITH_F_V_EQUALS_TWO_FOR_EVERY_CONSTRAINED_VERTEX",
        "representation_change": "IDENTITY_ON_EDGE_VARIABLES__NO_SEMANTIC_QUOTIENT",
    }

    comparisons = {
        "edge_endpoint_map": candidate_edge_map == independent_edge_map,
        "local_relation_equals_degree_two": all(local_exact.values()) and candidate_receipt["all_local_relations_exact_degree_two"],
        "satisfying_edge_set_family": candidate_receipt["satisfying_edge_sets"] == satisfying,
        "satisfying_edge_set_count": candidate_receipt["satisfying_edge_set_count"] == len(satisfying),
        "every_solution_two_regular": candidate_receipt["every_solution_two_regular"] and all(r["degree_vector"] == [2, 2, 2, 2, 2] for r in cycle_receipts),
        "every_k5_solution_single_five_cycle": candidate_receipt["every_solution_single_five_cycle"] and all(r["single_five_cycle"] for r in cycle_receipts),
        "two_factor_semantic_classification": candidate["general_semantic_classification"]["object"] == general_class["object"],
    }

    pass_ok = all([
        guard["ok"],
        prep.get("status") == "READY",
        incidence_matches_scopes,
        all(local_exact.values()),
        not relation_disagreements,
        len(satisfying) == 12,
        all(r["single_five_cycle"] for r in cycle_receipts),
        all(comparisons.values()),
        candidate.get("verdict") == VERDICT,
    ])

    return {
        "verdict": VERDICT if pass_ok else "FAIL_INDEPENDENT_K5_EXACT_TWO_OF_FOUR_CARDINALITY_CHECK",
        "source_guard": guard,
        "method": "INDEPENDENT_RAW_RECONSTRUCTION_PLUS_FIXED_CARDINALITY_EDGE_SUBSET_ENUMERATION_PLUS_CYCLE_TRAVERSAL",
        "candidate_helpers_imported": False,
        "raw_prepare_status": prep.get("status"),
        "edge_endpoint_map": independent_edge_map,
        "incidence_matches_residual_scopes": incidence_matches_scopes,
        "local_relation_exact_degree_two": local_exact,
        "handshake_selected_edge_count_for_any_global_solution": 5,
        "fixed_cardinality_subsets_checked": 252,
        "relation_degree_disagreement_count": len(relation_disagreements),
        "satisfying_edge_sets": satisfying,
        "satisfying_edge_set_count": len(satisfying),
        "every_solution_single_five_cycle": all(r["single_five_cycle"] for r in cycle_receipts),
        "general_semantic_classification": general_class,
        "comparisons": comparisons,
        "resource_receipt": {
            "size4_boolean_separator_assignments_enumerated": 0,
            "solver_calls": 0,
            "carrier_calls": 0,
            "unbounded_recursive_calls": 0,
            "three_plus_join_chains_materialized": 0,
            "global_residual_cartesian_products_materialized": 0,
            "budget_raise": False,
        },
        "scientific_firewall": {
            "P_VS_NP": "OPEN",
            "GENERAL_SAT_IN_P": "NOT_PROVED",
            "GENERAL_K5_OR_F_FACTOR_CARRIER": "NOT_YET_SEALED",
            "SIZE4_BRANCHING_LICENSED": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-json", required=True)
    args = parser.parse_args()
    candidate = json.loads(Path(args.candidate_json).read_text(encoding="utf-8"))
    print(json.dumps(check(candidate), ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
