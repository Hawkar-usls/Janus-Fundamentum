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

PASS_VERDICT = "PASS_SCOPED_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_EXACT_TWO_FACTOR_PROOF_CARRYING_F_FACTOR_CARRIER_V1"

PREREG = Path("research/TRUMP_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_EXACT_TWO_FACTOR_F_FACTOR_CARRIER_FALSIFIER_GATE_PREREGISTRATION_2026-09-16.json")
PREREG_BLOB = "fa34b59bf0f2eb1350c696e0d55b3e3b63f3c8fc"
PARENT_STATE = Path("registry/TRUMP_CURRENT_STATE_2026-09-15_v3.17.json")
PARENT_STATE_BLOB = "bf871e4e574381373f8c4d207eca9a12c9175ea4"
CANDIDATE = Path("research/tools/apma_bucket_exact_two_factor_f_factor_carrier/carrier.py")
CANDIDATE_BLOB = "21c66961f9ce809e7af824c8b0892f2e017463d9"
CC = Path("research/tools/apma_bucket_common_core/common_core_semijoin_prefilter.py")
CC_BLOB = "f103bf9b14e3b208200f429b75d0858c4963fa7c"
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
        "parent_v3_17_blob": git_blob(r / PARENT_STATE) == PARENT_STATE_BLOB,
        "candidate_blob_bound_but_not_imported": git_blob(r / CANDIDATE) == CANDIDATE_BLOB,
        "common_core_blob": git_blob(r / CC) == CC_BLOB,
        "v3_8_prepare_blob": git_blob(r / V38) == V38_BLOB,
    }
    return {"ok": all(checks.values()), "checks": checks}


def exact_two_patterns(arity: int) -> set[tuple[int, ...]]:
    out: set[tuple[int, ...]] = set()
    for chosen in itertools.combinations(range(arity), 2):
        row = [0] * arity
        for p in chosen:
            row[p] = 1
        out.add(tuple(row))
    return out


def build_parent_raw_independently() -> tuple[dict[str, Any], dict[tuple[int, int], int]]:
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
    patterns = sorted(exact_two_patterns(4))
    for vertex, rel in enumerate(targets):
        old_scope = [int(v) for v in rel["scope"]]
        core_scope = old_scope[:-2]
        core_rows = sorted({tuple(int(x) for x in row[:-2]) for row in rel["allowed"]})
        incident = sorted(pair_to_var[tuple(sorted((vertex, other)))] for other in range(5) if other != vertex)
        rel["scope"] = core_scope + incident
        rel["allowed"] = [list(core) + list(bits) for core in core_rows for bits in patterns]
    return raw, pair_to_var


def residual_relation(factor: dict[str, Any], core: list[int]) -> tuple[list[int], set[tuple[int, ...]]]:
    C = set(int(v) for v in core)
    scope = [int(v) for v in factor["scope"]]
    residual = [v for v in scope if v not in C]
    pos = {v: i for i, v in enumerate(scope)}
    rows = {tuple(int(row[pos[v]]) for v in residual) for row in factor["rows"]}
    return residual, rows


def reconstruct_parent_component() -> dict[str, Any]:
    raw, pair_to_var = build_parent_raw_independently()
    prep = v38._prepare(raw)
    if prep.get("status") != "READY":
        raise RuntimeError(f"PARENT_PREP_NOT_READY:{prep.get('status')}")
    core = [int(v) for v in prep["core"]]
    factor_by_vertex: dict[int, dict[str, Any]] = {}
    for vertex in range(5):
        expected_scope = {
            pair_to_var[tuple(sorted((vertex, other)))]
            for other in range(5)
            if other != vertex
        }
        matches = []
        for f in prep["conditioned"]:
            scope, rows = residual_relation(f, core)
            if set(scope) == expected_scope and rows == exact_two_patterns(4):
                matches.append(f)
        if len(matches) != 1:
            raise RuntimeError(f"EXPECTED_ONE_FACTOR_FOR_VERTEX_{vertex}:{len(matches)}")
        factor_by_vertex[vertex] = matches[0]
    factor_ids = sorted(str(f["id"]) for f in factor_by_vertex.values())
    abstract_for_factor = {str(f["id"]): v for v, f in factor_by_vertex.items()}
    return {
        "raw": raw,
        "prep": prep,
        "pair_to_var": pair_to_var,
        "factor_by_vertex": factor_by_vertex,
        "factor_ids_sorted": factor_ids,
        "abstract_for_factor": abstract_for_factor,
        "edge_ids_sorted": sorted(pair_to_var.values()),
    }


def candidate_named_tutte_adjacency(factor_ids: list[str], edge_ids: list[int], endpoints_by_factor: dict[int, tuple[str, str]]) -> dict[str, set[str]]:
    edge_index = {e: i for i, e in enumerate(edge_ids)}
    vertex_index = {fid: i for i, fid in enumerate(factor_ids)}
    scopes = {fid: [] for fid in factor_ids}
    for e in edge_ids:
        u, v = endpoints_by_factor[e]
        scopes[u].append(e)
        scopes[v].append(e)
    adj: dict[str, set[str]] = {}
    def add_node(x: str) -> None:
        adj.setdefault(x, set())
    def add_edge(a: str, b: str) -> None:
        add_node(a); add_node(b); adj[a].add(b); adj[b].add(a)
    port: dict[tuple[str, int], str] = {}
    for fid in factor_ids:
        vi = vertex_index[fid]
        inc = sorted(scopes[fid])
        for e in inc:
            p = f"A|{vi}|{edge_index[e]}"
            port[(fid, e)] = p
            add_node(p)
        for j in range(max(0, len(inc) - 2)):
            s = f"B|{vi}|{j}"
            add_node(s)
            for e in inc:
                add_edge(port[(fid, e)], s)
    for e in edge_ids:
        u, v = endpoints_by_factor[e]
        add_edge(port[(u, e)], port[(v, e)])
    return adj


def verify_matching_adj(adj: dict[str, set[str]], matching: list[list[str]]) -> bool:
    used: set[str] = set()
    for pair in matching:
        if len(pair) != 2:
            return False
        a, b = str(pair[0]), str(pair[1])
        if a not in adj or b not in adj or b not in adj[a] or a == b:
            return False
        if a in used or b in used:
            return False
        used.add(a); used.add(b)
    return len(used) == len(adj)


def component_sizes_after_removal(adj: dict[str, set[str]], removed: set[str]) -> list[int]:
    live = set(adj) - removed
    seen: set[str] = set()
    sizes = []
    for s in sorted(live):
        if s in seen:
            continue
        todo = [s]
        seen.add(s)
        size = 0
        while todo:
            x = todo.pop()
            size += 1
            for y in adj[x]:
                if y in live and y not in seen:
                    seen.add(y)
                    todo.append(y)
        sizes.append(size)
    return sorted(sizes)


def verify_barrier_adj(adj: dict[str, set[str]], barrier: list[str]) -> dict[str, Any]:
    A = set(str(x) for x in barrier)
    if len(A) != len(barrier) or not A <= set(adj):
        return {"valid": False, "reason": "UNKNOWN_OR_DUPLICATE_VERTEX"}
    sizes = component_sizes_after_removal(adj, A)
    odd = sum(1 for n in sizes if n % 2 == 1)
    return {"valid": odd > len(A), "odd_component_count": odd, "barrier_size": len(A), "component_sizes": sizes}


def brute_force_two_factor_truth(n: int, edges: list[tuple[int, int]]) -> bool:
    # Independent method: enumerate only subsets of the forced cardinality n,
    # because a 2-factor on n vertices has total degree 2n and therefore n edges.
    if len(edges) < n:
        return False
    for chosen_indices in itertools.combinations(range(len(edges)), n):
        chosen = set(chosen_indices)
        deg = [0] * n
        for i, (a, b) in enumerate(edges):
            if i in chosen:
                deg[a] += 1
                deg[b] += 1
        if deg == [2] * n:
            return True
    return False


def exhaustive_truth_vector() -> dict[str, Any]:
    statuses = []
    total = 0
    sat = 0
    for n in (3, 4, 5):
        possible = list(itertools.combinations(range(n), 2))
        for mask in range(1 << len(possible)):
            edges = [possible[i] for i in range(len(possible)) if (mask >> i) & 1]
            truth = brute_force_two_factor_truth(n, edges)
            statuses.append("S" if truth else "U")
            total += 1
            sat += int(truth)
    return {
        "graph_count": total,
        "sat_count": sat,
        "status_vector_sha256": hashlib.sha256("".join(statuses).encode("ascii")).hexdigest(),
    }


def parent_endpoints_by_factor(case: dict[str, Any]) -> dict[int, tuple[str, str]]:
    var_to_pair = {int(v): pair for pair, v in case["pair_to_var"].items()}
    factor_for_abstract = {v: str(f["id"]) for v, f in case["factor_by_vertex"].items()}
    out = {}
    for var, (a, b) in var_to_pair.items():
        out[var] = tuple(sorted((factor_for_abstract[a], factor_for_abstract[b])))
    return out


def independently_replay_parent(case: dict[str, Any], selected: list[int]) -> dict[str, Any]:
    prep = case["prep"]
    assignment = {int(v): int(x) for v, x in zip(prep["core"], prep["state"])}
    selected_set = set(int(e) for e in selected)
    for e in case["edge_ids_sorted"]:
        assignment[e] = int(e in selected_set)
    bucket = {str(f["id"]): f for f in prep["ready"]["bucket"]}
    checks = {}
    for f in case["factor_by_vertex"].values():
        fid = str(f["id"])
        orig = bucket[fid]
        scope = [int(v) for v in orig["scope"]]
        if not all(v in assignment for v in scope):
            checks[fid] = False
            continue
        row = tuple(assignment[v] for v in scope)
        allowed = {tuple(int(x) for x in r) for r in orig["rows"]}
        checks[fid] = row in allowed
    return {"ok": all(checks.values()), "factor_checks": checks}


def selected_is_five_cycle(case: dict[str, Any], selected: list[int]) -> bool:
    var_to_pair = {int(v): pair for pair, v in case["pair_to_var"].items()}
    deg = [0] * 5
    adj = {v: set() for v in range(5)}
    for e in selected:
        if int(e) not in var_to_pair:
            return False
        a, b = var_to_pair[int(e)]
        deg[a] += 1; deg[b] += 1
        adj[a].add(b); adj[b].add(a)
    if deg != [2] * 5 or len(selected) != 5:
        return False
    seen = {0}; todo = [0]
    while todo:
        x = todo.pop()
        for y in adj[x]:
            if y not in seen:
                seen.add(y); todo.append(y)
    return len(seen) == 5


def build_simple_candidate_adj(n: int, edge_pairs: list[tuple[int, int]], edge_offset: int) -> dict[str, set[str]]:
    fids = [f"v{i}" for i in range(n)]
    edge_ids = [edge_offset + i for i in range(len(edge_pairs))]
    endpoints = {edge_ids[i]: (f"v{a}", f"v{b}") for i, (a, b) in enumerate(edge_pairs)}
    return candidate_named_tutte_adjacency(fids, edge_ids, endpoints)


def check(candidate: dict[str, Any]) -> dict[str, Any]:
    guard = source_guard()
    case = reconstruct_parent_component()
    endpoints = parent_endpoints_by_factor(case)
    parent_adj = candidate_named_tutte_adjacency(case["factor_ids_sorted"], case["edge_ids_sorted"], endpoints)

    parent_out = candidate["parent_raw_k5"]
    solve = parent_out["solve"]
    parent_matching = solve["certificate"]["matching"] if solve.get("status") == "EXACT_SAT_TWO_FACTOR" else []
    parent_match_valid = verify_matching_adj(parent_adj, parent_matching)
    selected = [int(e) for e in solve.get("selected_edge_ids", [])]
    parent_cycle = selected_is_five_cycle(case, selected)
    parent_replay = independently_replay_parent(case, selected)

    # Verify the candidate's preregistered UNSAT bowtie certificate without candidate helpers.
    bowtie_edges = [(0, 1), (0, 2), (1, 2), (0, 3), (0, 4), (3, 4)]
    bowtie_adj = build_simple_candidate_adj(5, bowtie_edges, 2200)
    bowtie_out = candidate["controls"]["BOWTIE"]
    bowtie_barrier = bowtie_out.get("certificate", {}).get("barrier", [])
    bowtie_cert = verify_barrier_adj(bowtie_adj, bowtie_barrier)

    truth = exhaustive_truth_vector()
    candidate_census = candidate["exhaustive_small_graph_census"]

    # Independently enumerate all 12 K5 2-factors and verify the forward Tutte map constructively.
    k5_edges = sorted(case["pair_to_var"].values())
    var_to_pair = {int(v): pair for pair, v in case["pair_to_var"].items()}
    k5_solutions = []
    for chosen in itertools.combinations(k5_edges, 5):
        deg = [0] * 5
        for e in chosen:
            a, b = var_to_pair[e]
            deg[a] += 1; deg[b] += 1
        if deg == [2] * 5:
            k5_solutions.append(list(chosen))
    forward_all_valid = True
    edge_index = {e: i for i, e in enumerate(case["edge_ids_sorted"])}
    vertex_index = {fid: i for i, fid in enumerate(case["factor_ids_sorted"])}
    abstract_to_fid = {v: str(f["id"]) for v, f in case["factor_by_vertex"].items()}
    for chosen in k5_solutions:
        chosen_set = set(chosen)
        matching: list[list[str]] = []
        used_ports: set[tuple[str, int]] = set()
        for e in chosen:
            u, v = endpoints[e]
            matching.append([f"A|{vertex_index[u]}|{edge_index[e]}", f"A|{vertex_index[v]}|{edge_index[e]}"])
            used_ports.add((u, e)); used_ports.add((v, e))
        for abstract_v in range(5):
            fid = abstract_to_fid[abstract_v]
            incident = sorted(case["pair_to_var"][tuple(sorted((abstract_v, other)))] for other in range(5) if other != abstract_v)
            unselected = [e for e in incident if e not in chosen_set]
            if len(unselected) != 2:
                forward_all_valid = False
                break
            for j, e in enumerate(unselected):
                matching.append([f"A|{vertex_index[fid]}|{edge_index[e]}", f"B|{vertex_index[fid]}|{j}"])
        if not verify_matching_adj(parent_adj, matching):
            forward_all_valid = False
            break

    checks = {
        "source_guard": guard["ok"],
        "candidate_verdict": candidate.get("verdict") == PASS_VERDICT,
        "candidate_all_checks_true": all(candidate.get("checks", {}).values()),
        "parent_tutte_graph_counts": len(parent_adj) == 30 and sum(len(v) for v in parent_adj.values()) // 2 == 50,
        "parent_sat_matching_certificate_valid": parent_match_valid,
        "parent_selected_edges_are_one_five_cycle": parent_cycle,
        "parent_original_relation_replay": parent_replay["ok"],
        "bowtie_candidate_status_unsat": bowtie_out.get("status") == "EXACT_UNSAT_TUTTE_BARRIER",
        "bowtie_tutte_barrier_valid_independently": bowtie_cert["valid"],
        "small_graph_graph_count_match": candidate_census["graph_count"] == truth["graph_count"] == 1096,
        "small_graph_sat_count_match": candidate_census["sat_carrier_count"] == truth["sat_count"],
        "small_graph_status_vector_hash_match": candidate_census["status_vector_sha256"] == truth["status_vector_sha256"],
        "small_graph_candidate_zero_unknown": candidate_census["unknown_count"] == 0,
        "small_graph_candidate_zero_mismatch": candidate_census["mismatch_count"] == 0,
        "k5_solution_count_independent": len(k5_solutions) == 12,
        "all_k5_two_factors_construct_valid_perfect_matchings": forward_all_valid,
        "tamper_checks_reported": all(candidate.get("tamper_checks", {}).values()),
        "size4_branching_still_forbidden": candidate["scientific_firewall"]["SIZE4_BRANCHING_LICENSED"] is False,
        "p_vs_np_open": candidate["scientific_firewall"]["P_VS_NP"] == "OPEN",
        "general_sat_not_proved": candidate["scientific_firewall"]["GENERAL_SAT_IN_P"] == "NOT_PROVED",
    }
    passed = all(checks.values())
    return {
        "artifact_id": "JANUS-TRUMP-EXACT-TWO-FACTOR-F-FACTOR-CARRIER-INDEPENDENT-CHECK-2026-09-16-v1.0",
        "authority": "INDEPENDENT_CHECKER__SCOPED_ONLY",
        "verdict": PASS_VERDICT if passed else "FAIL_INDEPENDENT_EXACT_TWO_FACTOR_F_FACTOR_CARRIER_CHECK",
        "source_guard": guard,
        "checks": checks,
        "independent_method": "INDEPENDENT_RAW_K5_RECONSTRUCTION_PLUS_INDEPENDENT_TUTTE_ADJACENCY_PLUS_DIRECT_CERTIFICATE_REPLAY_PLUS_FIXED_CARDINALITY_BRUTE_FORCE_SMALL_GRAPH_CENSUS",
        "candidate_helpers_imported": False,
        "parent_receipt": {
            "tutte_vertices": len(parent_adj),
            "tutte_edges": sum(len(v) for v in parent_adj.values()) // 2,
            "matching_certificate_valid": parent_match_valid,
            "selected_edge_count": len(selected),
            "selected_is_five_cycle": parent_cycle,
            "original_relation_replay": parent_replay,
        },
        "bowtie_unsat_receipt": bowtie_cert,
        "exhaustive_small_graph_truth": truth,
        "k5_forward_map_receipt": {
            "independent_two_factor_count": len(k5_solutions),
            "all_constructed_perfect_matchings_valid": forward_all_valid,
        },
        "scientific_firewall": {
            "P_VS_NP": "OPEN",
            "GENERAL_SAT_IN_P": "NOT_PROVED",
            "SIZE4_BRANCHING_LICENSED": False,
            "GLOBAL_APMA_FRONTIER_ADVANCE": "NONE_PENDING_HQ_REVIEW",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-json", required=True)
    args = parser.parse_args()
    candidate = json.loads(Path(args.candidate_json).read_text(encoding="utf-8").strip().splitlines()[-1])
    print(json.dumps(check(candidate), ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
