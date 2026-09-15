from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path
from typing import Any

from research.tools.apma_bucket_k5_raw_semantic_forensic import forensic as parent

ARTIFACT_ID = "JANUS-TRUMP-BICAMERAL-BUCKET-UNIQUE-CORE-RESIDUAL-K5-EXACT-TWO-OF-FOUR-CARDINALITY-FORENSIC-2026-09-15-v1.0"
VERDICT = "PASS_DIAGNOSTIC_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_K5_EXACT_TWO_OF_FOUR_CARDINALITY_STRUCTURE_FORENSIC"
AUTHORITY = "DIAGNOSTIC_ONLY__NO_SCIENTIFIC_PROMOTION"

PREREG = Path("research/TRUMP_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_K5_EXACT_TWO_OF_FOUR_CARDINALITY_STRUCTURE_FORENSIC_PREREGISTRATION_2026-09-15.json")
PREREG_BLOB = "11198e102ab32d12c8d49c215f2d196a624e4e50"
PARENT_STATE = Path("registry/TRUMP_CURRENT_STATE_2026-09-15_v3.16.json")
PARENT_STATE_BLOB = "32408b17271ae7f23b78b01756c47b5fc6e8d8ef"
PARENT_FORENSIC = Path("research/tools/apma_bucket_k5_raw_semantic_forensic/forensic.py")
PARENT_FORENSIC_BLOB = "4128f0db77dfc1391b6ec539f201250bfb3d8b6e"


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
        "parent_raw_semantic_forensic_blob": git_blob(r / PARENT_FORENSIC) == PARENT_FORENSIC_BLOB,
    }
    return {"ok": all(checks.values()), "checks": checks}


def factor_index(fid: str) -> int:
    if not fid.startswith("sticky_"):
        raise ValueError(f"UNEXPECTED_FACTOR_ID:{fid}")
    return int(fid.split("_", 1)[1])


def reconstruct_probe() -> dict[str, Any]:
    raw = parent.build_raw_k5("EXACT_2_OF_4")
    prep = parent.v38._prepare(raw)
    if prep.get("status") != "READY":
        raise RuntimeError(f"PREDECESSOR_NOT_READY:{prep.get('status')}")
    core = [int(v) for v in prep["core"]]
    factors = sorted(
        [f for f in prep["conditioned"] if str(f["id"]).startswith("sticky_")],
        key=lambda f: factor_index(str(f["id"])),
    )
    if len(factors) != 5:
        raise RuntimeError(f"EXPECTED_FIVE_TARGET_FACTORS:{len(factors)}")

    scopes: dict[int, list[int]] = {}
    rows: dict[int, set[tuple[int, ...]]] = {}
    for f in factors:
        i = factor_index(str(f["id"]))
        scope, rel_rows = parent.residual_relation(f, core)
        scopes[i] = [int(v) for v in scope]
        rows[i] = {tuple(int(x) for x in row) for row in rel_rows}

    occurrences: dict[int, list[int]] = {}
    for i, scope in scopes.items():
        for var in scope:
            occurrences.setdefault(var, []).append(i)
    edge_endpoint_map: dict[int, tuple[int, int]] = {}
    for var, endpoints in occurrences.items():
        eps = tuple(sorted(endpoints))
        if len(eps) != 2 or eps[0] == eps[1]:
            raise RuntimeError(f"NON_EDGE_OCCURRENCE:{var}:{eps}")
        edge_endpoint_map[int(var)] = (int(eps[0]), int(eps[1]))

    return {
        "raw": raw,
        "core": core,
        "scopes": scopes,
        "rows": rows,
        "edge_endpoint_map": dict(sorted(edge_endpoint_map.items())),
    }


def exact_two_rows(arity: int) -> set[tuple[int, ...]]:
    return {
        tuple(int(x) for x in bits)
        for bits in itertools.product((0, 1), repeat=arity)
        if sum(bits) == 2
    }


def graph_connected(selected: set[int], edge_endpoint_map: dict[int, tuple[int, int]]) -> bool:
    adj = {v: set() for v in range(5)}
    for edge in selected:
        a, b = edge_endpoint_map[edge]
        adj[a].add(b)
        adj[b].add(a)
    seen = {0}
    todo = [0]
    while todo:
        v = todo.pop()
        for w in adj[v]:
            if w not in seen:
                seen.add(w)
                todo.append(w)
    return len(seen) == 5


def assignment_receipt(probe: dict[str, Any]) -> dict[str, Any]:
    scopes: dict[int, list[int]] = probe["scopes"]
    rows: dict[int, set[tuple[int, ...]]] = probe["rows"]
    edge_endpoint_map: dict[int, tuple[int, int]] = probe["edge_endpoint_map"]
    edge_vars = sorted(edge_endpoint_map)
    if len(edge_vars) != 10:
        raise RuntimeError(f"EXPECTED_TEN_EDGE_VARIABLES:{len(edge_vars)}")

    local_relation_checks = {
        str(i): rows[i] == exact_two_rows(len(scopes[i])) and len(scopes[i]) == 4
        for i in range(5)
    }

    semantic_mismatches: list[dict[str, Any]] = []
    satisfying_edge_sets: list[list[int]] = []
    solution_graph_receipts: list[dict[str, Any]] = []

    for bits in itertools.product((0, 1), repeat=len(edge_vars)):
        assignment = dict(zip(edge_vars, (int(x) for x in bits)))
        relation_sat = all(tuple(assignment[v] for v in scopes[i]) in rows[i] for i in range(5))
        degrees = {
            v: sum(assignment[e] for e, endpoints in edge_endpoint_map.items() if v in endpoints)
            for v in range(5)
        }
        degree_two_sat = all(degrees[v] == 2 for v in range(5))
        if relation_sat != degree_two_sat:
            semantic_mismatches.append({
                "assignment": [assignment[v] for v in edge_vars],
                "relation_sat": relation_sat,
                "degree_two_sat": degree_two_sat,
                "degrees": degrees,
            })
        if relation_sat:
            selected = {v for v in edge_vars if assignment[v] == 1}
            connected = graph_connected(selected, edge_endpoint_map)
            two_regular = all(degrees[v] == 2 for v in range(5))
            single_five_cycle = two_regular and connected and len(selected) == 5
            edge_list = sorted(selected)
            satisfying_edge_sets.append(edge_list)
            solution_graph_receipts.append({
                "selected_edges": edge_list,
                "degree_vector": [degrees[v] for v in range(5)],
                "selected_edge_count": len(selected),
                "connected": connected,
                "two_regular": two_regular,
                "single_five_cycle": single_five_cycle,
            })

    satisfying_edge_sets.sort()
    return {
        "edge_variables": edge_vars,
        "edge_endpoint_map": {str(k): list(v) for k, v in edge_endpoint_map.items()},
        "local_relation_exact_degree_two": local_relation_checks,
        "all_local_relations_exact_degree_two": all(local_relation_checks.values()),
        "assignment_count_checked": 2 ** len(edge_vars),
        "semantic_mismatch_count": len(semantic_mismatches),
        "semantic_mismatches": semantic_mismatches[:8],
        "relation_sat_equals_degree_two_on_all_assignments": not semantic_mismatches,
        "satisfying_edge_sets": satisfying_edge_sets,
        "satisfying_edge_set_count": len(satisfying_edge_sets),
        "solution_graph_receipts": solution_graph_receipts,
        "every_solution_two_regular": all(r["two_regular"] for r in solution_graph_receipts),
        "every_solution_single_five_cycle": all(r["single_five_cycle"] for r in solution_graph_receipts),
        "every_solution_selects_five_edges": all(r["selected_edge_count"] == 5 for r in solution_graph_receipts),
    }


def profile() -> dict[str, Any]:
    guard = source_guard()
    probe = reconstruct_probe()
    receipt = assignment_receipt(probe)

    edge_pairs = sorted(tuple(v) for v in probe["edge_endpoint_map"].values())
    expected_pairs = list(itertools.combinations(range(5), 2))
    k5_edge_incidence_exact = edge_pairs == expected_pairs

    general_semantic_classification = {
        "exact_equivalence": "FOR_ANY_UNDIRECTED_GRAPH_G_WITH_ONE_BOOLEAN_VARIABLE_PER_EDGE__CONJUNCTION_OVER_VERTICES_OF_SUM_INCIDENT_X_E_EQUALS_TWO_IFF_THE_SELECTED_EDGE_SET_IS_A_SPANNING_TWO_FACTOR_OF_G",
        "object": "UNDIRECTED_TWO_FACTOR",
        "f_factor_specialization": "F_FACTOR_WITH_F_V_EQUALS_TWO_FOR_EVERY_CONSTRAINED_VERTEX",
        "representation_change": "IDENTITY_ON_EDGE_VARIABLES__NO_SEMANTIC_QUOTIENT",
        "known_polynomial_carrier_candidate": "CLASSICAL_F_FACTOR_OR_PERFECT_MATCHING_REDUCTION__REQUIRES_SEPARATE_PROOF_CARRYING_SEAL_BEFORE_USE",
        "carrier_sealed_here": False,
    }

    pass_ok = all([
        guard["ok"],
        k5_edge_incidence_exact,
        receipt["all_local_relations_exact_degree_two"],
        receipt["relation_sat_equals_degree_two_on_all_assignments"],
        receipt["satisfying_edge_set_count"] == 12,
        receipt["every_solution_two_regular"],
        receipt["every_solution_single_five_cycle"],
        receipt["every_solution_selects_five_edges"],
    ])

    return {
        "artifact_id": ARTIFACT_ID,
        "authority": AUTHORITY,
        "verdict": VERDICT if pass_ok else "FAIL_DIAGNOSTIC_K5_EXACT_TWO_OF_FOUR_CARDINALITY_STRUCTURE_FORENSIC",
        "source_guard": guard,
        "probe": {
            "common_core": probe["core"],
            "factor_count": len(probe["scopes"]),
            "edge_variable_count": len(probe["edge_endpoint_map"]),
            "k5_edge_incidence_exact": k5_edge_incidence_exact,
        },
        "finite_k5_receipt": receipt,
        "general_semantic_classification": general_semantic_classification,
        "captain_obvious": {
            "cheaper_structure_found": pass_ok,
            "structure": "EXACT_TWO_FACTOR_SEMANTICS",
            "next_obligation_if_pass": "SEPARATELY_SEAL_AN_EXACT_PROOF_CARRYING_TWO_FACTOR_F_FACTOR_CARRIER_WITH_POLYNOMIAL_TOTAL_RESOURCE_ACCOUNTING_BEFORE_ANY_SIZE4_SEPARATOR_BRANCHING",
            "SIZE4_BRANCHING_LICENSED": False,
        },
        "resource_receipt": {
            "finite_k5_assignment_enumeration": 1024,
            "size4_boolean_separator_assignments_enumerated": 0,
            "separator_sets_size_ge_3_executed_as_boolean_branches": 0,
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
            "CONNECTED_MIXED_CORE_SOLVED": "NO",
            "GENERAL_RESIDUAL_SEPARATOR_TRACTABILITY": "NOT_PROVED",
            "GENERAL_K5_OR_F_FACTOR_CARRIER": "NOT_YET_SEALED",
            "GLOBAL_APMA_FRONTIER_ADVANCE": "NONE",
        },
    }


if __name__ == "__main__":
    print(json.dumps(profile(), ensure_ascii=False, sort_keys=True))
