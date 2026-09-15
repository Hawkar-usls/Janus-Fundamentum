from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
import math
from pathlib import Path
from typing import Any

from research.tools.apma_bucket_common_core import common_core_semijoin_prefilter as cc_v1
from research.tools.apma_bucket_residual_single_separator import residual_single_separator_factorized_payload as v38
from research.tools.apma_guarded_elimination import guarded_bounded_output_elimination as guarded
from research.tools.apma_bucket_k5_raw_semantic_forensic import forensic as k5_parent

VERDICT = "PASS_SCOPED_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_CLOSED_INTERNAL_TWO_FACTOR_F_FACTOR_CARRIER_V1"

PREREG = Path("research/TRUMP_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_CLOSED_INTERNAL_TWO_FACTOR_F_FACTOR_CARRIER_PREREGISTRATION_2026-09-15.json")
PREREG_BLOB = "1240d183461bfab4defe42df14ffdb2df31396da"
THEOREM = Path("research/TRUMP_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_CLOSED_INTERNAL_TWO_FACTOR_F_FACTOR_CARRIER_THEOREM_CANDIDATE_2026-09-15.md")
THEOREM_BLOB = "3c3db06ec64f6f130deca98fef0e0f0f060ac562"
PARENT_STATE = Path("registry/TRUMP_CURRENT_STATE_2026-09-15_v3.17.json")
PARENT_STATE_BLOB = "bf871e4e574381373f8c4d207eca9a12c9175ea4"
CANDIDATE = Path("research/tools/apma_bucket_closed_two_factor/closed_two_factor_carrier.py")
CANDIDATE_BLOB = "2e81d4f908deea1c08a6e8c32b0ca26b7cb532eb"
COMPONENT = Path("research/tools/apma_bucket_closed_two_factor/two_factor_component.py")
COMPONENT_BLOB = "06a8980dc56d8d098618ddee0fe74e5b328dcac7"
MATCHING = Path("research/tools/apma_bucket_closed_two_factor/matching_core.py")
MATCHING_BLOB = "347022fca80b5b5788fc3946368a5cfaf69bd762"
K5_PARENT = Path("research/tools/apma_bucket_k5_raw_semantic_forensic/forensic.py")
K5_PARENT_BLOB = "4128f0db77dfc1391b6ec539f201250bfb3d8b6e"


def root() -> Path:
    return Path(__file__).resolve().parents[3]


def git_blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def canonical_bytes(obj: Any) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_obj(obj: Any) -> str:
    return hashlib.sha256(canonical_bytes(obj)).hexdigest()


def source_guard() -> dict[str, Any]:
    r = root()
    checks = {
        "prereg_blob": git_blob(r / PREREG) == PREREG_BLOB,
        "theorem_blob": git_blob(r / THEOREM) == THEOREM_BLOB,
        "parent_v3_17_blob": git_blob(r / PARENT_STATE) == PARENT_STATE_BLOB,
        "candidate_blob_bound_but_not_imported": git_blob(r / CANDIDATE) == CANDIDATE_BLOB,
        "component_blob_bound_but_not_imported": git_blob(r / COMPONENT) == COMPONENT_BLOB,
        "matching_blob_bound_but_not_used_as_truth": git_blob(r / MATCHING) == MATCHING_BLOB,
        "k5_parent_blob": git_blob(r / K5_PARENT) == K5_PARENT_BLOB,
    }
    return {"ok": all(checks.values()), "checks": checks}


def residual_scope(factor: dict[str, Any], core: list[int]) -> list[int]:
    core_set = {int(v) for v in core}
    return [int(v) for v in factor["scope"] if int(v) not in core_set]


def residual_rows(factor: dict[str, Any], core: list[int]) -> set[tuple[int, ...]]:
    scope = [int(v) for v in factor["scope"]]
    res = residual_scope(factor, core)
    pos = {v: i for i, v in enumerate(scope)}
    return {tuple(int(row[pos[v]]) for v in res) for row in factor["rows"]}


def reconstruct_component_independently(raw: dict[str, Any]) -> dict[str, Any]:
    prep = v38._prepare(raw)
    if prep.get("status") != "READY":
        return {"status": "PREP_NOT_READY", "prep_status": prep.get("status")}
    gt2 = [list(c) for c in prep["residual_components"] if len(c) > 2]
    if len(gt2) != 1:
        return {"status": "EXPECTED_ONE_GT2", "gt2": gt2}
    comp = sorted(gt2[0])
    factor_records: list[dict[str, Any]] = []
    occurrence: dict[int, list[int]] = {}
    for local, idx in enumerate(comp):
        factor = prep["conditioned"][idx]
        scope = residual_scope(factor, prep["core"])
        rows = residual_rows(factor, prep["core"])
        expected = math.comb(len(scope), 2) if len(scope) >= 2 else 0
        relation_ok = (
            len(scope) >= 2
            and len(rows) == expected
            and all(len(row) == len(scope) and all(bit in (0, 1) for bit in row) and sum(row) == 2 for row in rows)
            and len({tuple(i for i, bit in enumerate(row) if bit == 1) for row in rows}) == expected
        )
        if not relation_ok:
            return {"status": "RELATION_NOT_EXACT_WEIGHT_TWO", "factor_id": str(factor["id"])}
        factor_records.append({
            "local": local,
            "conditioned_index": idx,
            "factor_id": str(factor["id"]),
            "scope": scope,
            "rows": rows,
        })
        for var in scope:
            occurrence.setdefault(int(var), []).append(local)

    edges: list[dict[str, int]] = []
    for var in sorted(occurrence):
        ends = sorted(occurrence[var])
        if len(ends) != 2 or ends[0] == ends[1]:
            return {"status": "INCIDENCE_NOT_TWO", "variable": var, "ends": ends}
        edges.append({"var": int(var), "u": int(ends[0]), "v": int(ends[1])})
    boundary = sorted(set(occurrence) & {int(v) for v in prep["ready"]["cut"]})
    return {
        "status": "READY",
        "prep": prep,
        "component": comp,
        "factor_records": factor_records,
        "edges": edges,
        "boundary": boundary,
    }


def build_gadget_independently(component: dict[str, Any]) -> dict[str, Any]:
    factors = component["factor_records"]
    edges = component["edges"]
    n = len(factors)
    incident = {v: [] for v in range(n)}
    endpoint = {}
    for e in edges:
        var, u, v = int(e["var"]), int(e["u"]), int(e["v"])
        incident[u].append(var)
        incident[v].append(var)
        endpoint[var] = (u, v)
    for v in incident:
        incident[v].sort()

    vertex_info = {}
    incidence = {}
    next_id = 0
    for v in range(n):
        for var in incident[v]:
            incidence[(v, var)] = next_id
            vertex_info[next_id] = {"kind": "A", "factor_vertex": v, "residual_var": var}
            next_id += 1
    auxiliaries = {}
    for v in range(n):
        auxiliaries[v] = []
        for j in range(len(incident[v]) - 2):
            auxiliaries[v].append(next_id)
            vertex_info[next_id] = {"kind": "B", "factor_vertex": v, "aux_index": j}
            next_id += 1
    gadget_edges = set()
    local_count = 0
    for v in range(n):
        for var in incident[v]:
            a = incidence[(v, var)]
            for b in auxiliaries[v]:
                gadget_edges.add(tuple(sorted((a, b))))
                local_count += 1
    cross = {}
    for var in sorted(endpoint):
        u, v = endpoint[var]
        edge = tuple(sorted((incidence[(u, var)], incidence[(v, var)])))
        gadget_edges.add(edge)
        cross[edge] = var
    edge_list = sorted(gadget_edges)
    public = {
        "vertices": list(range(next_id)),
        "edges": [list(e) for e in edge_list],
        "vertex_count": next_id,
        "edge_count": len(edge_list),
        "local_biclique_edge_count": local_count,
        "cross_edge_count": len(cross),
        "vertex_info": {str(k): v for k, v in sorted(vertex_info.items())},
        "cross_edge_to_residual_var": {f"{a}:{b}": int(var) for (a, b), var in sorted(cross.items())},
    }
    public["gadget_sha256"] = sha256_obj(public)
    return {"public": public, "vertices": list(range(next_id)), "edges": edge_list, "cross": cross}


def verify_perfect_matching_independently(gadget: dict[str, Any], cert: dict[str, Any]) -> dict[str, Any]:
    if cert.get("gadget_sha256") != gadget["public"]["gadget_sha256"]:
        return {"ok": False, "reason": "GADGET_HASH_MISMATCH"}
    edge_set = set(gadget["edges"])
    used = set()
    matching = []
    for raw in cert.get("perfect_matching", []):
        edge = tuple(sorted((int(raw[0]), int(raw[1]))))
        if edge not in edge_set:
            return {"ok": False, "reason": "MATCH_EDGE_ABSENT", "edge": edge}
        if edge[0] in used or edge[1] in used:
            return {"ok": False, "reason": "MATCH_VERTEX_REUSED", "edge": edge}
        used.update(edge)
        matching.append(edge)
    if used != set(gadget["vertices"]):
        return {"ok": False, "reason": "NOT_PERFECT", "covered": len(used), "total": len(gadget["vertices"])}
    selected = sorted(gadget["cross"][e] for e in matching if e in gadget["cross"])
    if selected != sorted(int(v) for v in cert.get("selected_residual_vars", [])):
        return {"ok": False, "reason": "SELECTED_VAR_MAP_MISMATCH"}
    return {"ok": True, "selected": selected, "matching": matching}


def components_after_delete(vertices: list[int], edges: list[tuple[int, int]], deleted: set[int]) -> list[list[int]]:
    kept = [v for v in vertices if v not in deleted]
    adj = {v: [] for v in kept}
    kept_set = set(kept)
    for a, b in edges:
        if a in kept_set and b in kept_set:
            adj[a].append(b)
            adj[b].append(a)
    seen = set()
    comps = []
    for start in kept:
        if start in seen:
            continue
        seen.add(start)
        todo = [start]
        comp = []
        while todo:
            v = todo.pop()
            comp.append(v)
            for w in adj[v]:
                if w not in seen:
                    seen.add(w)
                    todo.append(w)
        comps.append(sorted(comp))
    return comps


def verify_tutte_independently(gadget: dict[str, Any], cert: dict[str, Any]) -> dict[str, Any]:
    if cert.get("gadget_sha256") != gadget["public"]["gadget_sha256"]:
        return {"ok": False, "reason": "GADGET_HASH_MISMATCH"}
    u = {int(v) for v in cert.get("tutte_obstruction_U", [])}
    if not u.issubset(set(gadget["vertices"])):
        return {"ok": False, "reason": "U_OUTSIDE_GRAPH"}
    comps = components_after_delete(gadget["vertices"], gadget["edges"], u)
    q = sum(len(c) % 2 for c in comps)
    return {
        "ok": q > len(u),
        "U_size": len(u),
        "odd_component_count": q,
        "component_sizes": [len(c) for c in comps],
        "deficiency_lower_bound": q - len(u),
    }


def brute_two_factor_solutions(component: dict[str, Any], cap_edges: int = 12) -> list[list[int]]:
    edges = component["edges"]
    if len(edges) > cap_edges:
        raise ValueError("FINITE_BRUTE_FORCE_EDGE_CAP_EXCEEDED")
    vars_ = [int(e["var"]) for e in edges]
    endpoint = {int(e["var"]): (int(e["u"]), int(e["v"])) for e in edges}
    n = len(component["factor_records"])
    solutions = []
    for bits in itertools.product((0, 1), repeat=len(vars_)):
        selected = [var for var, bit in zip(vars_, bits) if bit]
        deg = [sum(1 for var in selected if v in endpoint[var]) for v in range(n)]
        if deg == [2] * n:
            solutions.append(sorted(selected))
    return sorted(solutions)


def brute_has_perfect_matching(vertices: list[int], graph_edges: list[tuple[int, int]]) -> bool:
    adjacency = {v: set() for v in vertices}
    for a, b in graph_edges:
        adjacency[a].add(b)
        adjacency[b].add(a)

    def rec(remaining: tuple[int, ...]) -> bool:
        if not remaining:
            return True
        v = remaining[0]
        rem_set = set(remaining)
        for w in sorted(adjacency[v] & rem_set):
            if w == v:
                continue
            nxt = tuple(x for x in remaining if x not in (v, w))
            if rec(nxt):
                return True
        return False

    return rec(tuple(sorted(vertices)))


def build_cubic_unsat_raw_independently() -> tuple[dict[str, Any], list[tuple[int, int]]]:
    raw = copy.deepcopy(cc_v1.filtered_still_overbudget_control())
    central = 15
    graph_edges = []
    for lobe in range(3):
        base = 5 * lobe
        x, a, b, c, d = base, base + 1, base + 2, base + 3, base + 4
        graph_edges += [(a, c), (a, d), (b, c), (b, d), (c, d), (a, x), (x, b), (x, central)]
    graph_edges = sorted(set(tuple(sorted(e)) for e in graph_edges))
    start = max(int(v) for v in raw["variables"]) + 1
    pair_to_var = {edge: start + i for i, edge in enumerate(graph_edges)}
    raw["variables"].extend(range(start, start + len(graph_edges)))
    patterns = []
    for chosen in itertools.combinations(range(3), 2):
        row = [0, 0, 0]
        for p in chosen:
            row[p] = 1
        patterns.append(tuple(row))
    for vertex in range(16):
        rel = next(r for r in raw["constraints"] if r["id"] == f"sticky_{vertex}")
        core_scope = [int(v) for v in rel["scope"][:-2]]
        core_rows = sorted({tuple(int(x) for x in row[:-2]) for row in rel["allowed"]})
        incident = sorted(pair_to_var[e] for e in graph_edges if vertex in e)
        rel["scope"] = core_scope + incident
        rel["allowed"] = [list(core) + list(bits) for core in core_rows for bits in patterns]
    return raw, graph_edges


def candidate_two_factor_record(candidate_case: dict[str, Any]) -> dict[str, Any]:
    carrier = candidate_case["carrier"]
    return next(item for item in carrier.get("portfolio", []) if item.get("carrier_class") == "CLOSED_INTERNAL_TWO_FACTOR")


def check(candidate: dict[str, Any]) -> dict[str, Any]:
    guard = source_guard()

    positive_raw = k5_parent.build_raw_k5("EXACT_2_OF_4")
    pos_component = reconstruct_component_independently(positive_raw)
    pos_candidate = candidate["positive_k5"]
    pos_record = candidate_two_factor_record(pos_candidate)
    pos_gadget = build_gadget_independently(pos_component)
    pos_matching = verify_perfect_matching_independently(pos_gadget, pos_record["certificate"])
    pos_solutions = brute_two_factor_solutions(pos_component, cap_edges=10)
    pos_selected = sorted(pos_matching.get("selected", []))
    pos_truth_contains_candidate = pos_selected in pos_solutions
    pos_original_replay = guarded.verify_original_assignment(
        pos_component["prep"]["canonical"],
        {int(k): int(v) for k, v in pos_candidate["carrier"]["witness"].items()},
    ) if pos_candidate.get("status") == "ADMIT_EXACT_UNIQUE_CORE_RESIDUAL_CLOSED_INTERNAL_TWO_FACTOR_FACTORIZED_PAYLOAD_PORTFOLIO" else False

    unsat_raw, cubic_edges = build_cubic_unsat_raw_independently()
    unsat_component = reconstruct_component_independently(unsat_raw)
    unsat_candidate = candidate["unsat_cubic_three_bridge"]
    unsat_carrier = unsat_candidate["carrier"]
    unsat_gadget = build_gadget_independently(unsat_component)
    unsat_static = verify_tutte_independently(unsat_gadget, unsat_carrier["certificate"])
    cubic_perfect_matching_exists = brute_has_perfect_matching(list(range(16)), cubic_edges)
    cubic_degree = {v: 0 for v in range(16)}
    for a, b in cubic_edges:
        cubic_degree[a] += 1
        cubic_degree[b] += 1
    cubic_is_3_regular = all(cubic_degree[v] == 3 for v in range(16))
    # In a cubic graph, a 2-factor exists iff its edge-complement is a perfect matching.
    finite_unsat_truth = cubic_is_3_regular and not cubic_perfect_matching_exists

    controls = {
        "malformed_relation": candidate["malformed_relation"].get("status") == "OPEN_UNADMITTED_RESIDUAL_GT2_COMPONENT_BEFORE_SOLVER_EXECUTION",
        "invalid_incidence": candidate["invalid_incidence"].get("status") == "OPEN_UNADMITTED_RESIDUAL_GT2_COMPONENT_BEFORE_SOLVER_EXECUTION",
        "boundary_bearing": candidate["boundary_bearing_unit"].get("status") == "OPEN_TWO_FACTOR_BOUNDARY_INTERFACE_NOT_SEALED",
        "multiple_common_core": candidate["multiple_common_core"].get("status") == "OPEN_NONUNIQUE_COMMON_CORE_SUPPORT",
        "tampered_proposal": candidate["tampered_proposal"].get("status") == "REJECT_TAMPERED_PROVENANCE",
        "tampered_sat_certificate": candidate["tampered_sat_certificate"].get("ok") is False,
        "tampered_unsat_certificate": candidate["tampered_unsat_certificate"].get("ok") is False,
    }

    comparisons = {
        "positive_prepare_ready": pos_component.get("status") == "READY",
        "positive_boundary_empty": pos_component.get("boundary") == [],
        "positive_candidate_status": pos_candidate.get("status") == "ADMIT_EXACT_UNIQUE_CORE_RESIDUAL_CLOSED_INTERNAL_TWO_FACTOR_FACTORIZED_PAYLOAD_PORTFOLIO",
        "positive_gadget_matches": pos_record.get("gadget") == pos_gadget["public"],
        "positive_static_matching": pos_matching.get("ok") is True,
        "positive_finite_solution_count_12": len(pos_solutions) == 12,
        "positive_candidate_selected_is_true_solution": pos_truth_contains_candidate,
        "positive_original_raw_replay": bool(pos_original_replay),
        "unsat_prepare_ready": unsat_component.get("status") == "READY",
        "unsat_candidate_status": unsat_candidate.get("status") == "EXACT_UNSAT_BY_VERIFIED_CLOSED_INTERNAL_TWO_FACTOR_TUTTE_OBSTRUCTION",
        "unsat_gadget_matches": unsat_carrier.get("gadget") == unsat_gadget["public"],
        "unsat_static_tutte_certificate": unsat_static.get("ok") is True,
        "unsat_independent_finite_truth": finite_unsat_truth,
        "all_negative_controls_fail_closed": all(controls.values()),
    }

    pass_ok = guard["ok"] and all(comparisons.values())
    return {
        "verdict": VERDICT if pass_ok else "FAIL_INDEPENDENT_CLOSED_INTERNAL_TWO_FACTOR_CARRIER_CHECK",
        "source_guard": guard,
        "method": "INDEPENDENT_RAW_COMPONENT_RECONSTRUCTION_PLUS_INDEPENDENT_TUTTE_GADGET_PLUS_STATIC_CERTIFICATE_CHECKS_PLUS_FINITE_BRUTE_FORCE",
        "candidate_helpers_imported": False,
        "shared_matching_solver_used_as_truth": False,
        "positive": {
            "solution_count": len(pos_solutions),
            "selected_candidate_solution": pos_selected,
            "static_matching": pos_matching,
            "original_raw_replay": bool(pos_original_replay),
        },
        "unsat_cubic": {
            "vertex_count": 16,
            "edge_count": len(cubic_edges),
            "three_regular": cubic_is_3_regular,
            "independent_perfect_matching_exists": cubic_perfect_matching_exists,
            "independent_two_factor_exists": not finite_unsat_truth,
            "static_tutte": unsat_static,
        },
        "controls": controls,
        "comparisons": comparisons,
        "scientific_firewall": {
            "P_VS_NP": "OPEN",
            "GENERAL_SAT_IN_P": "NOT_PROVED",
            "SIZE4_BRANCHING_LICENSED": False,
            "BOUNDARY_BEARING_TWO_FACTOR_COMPONENTS": "OPEN",
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
