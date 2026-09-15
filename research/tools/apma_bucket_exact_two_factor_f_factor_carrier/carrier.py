from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path
from typing import Any

import networkx as nx

from research.tools.apma_bucket_k5_raw_semantic_forensic import forensic as parent

ARTIFACT_ID = "JANUS-TRUMP-BICAMERAL-BUCKET-UNIQUE-CORE-RESIDUAL-EXACT-TWO-FACTOR-PROOF-CARRYING-F-FACTOR-CARRIER-2026-09-16-v1.0"
PASS_VERDICT = "PASS_SCOPED_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_EXACT_TWO_FACTOR_PROOF_CARRYING_F_FACTOR_CARRIER_V1"
FAIL_VERDICT = "FAIL_OR_PARTIAL_EXACT_TWO_FACTOR_F_FACTOR_CARRIER_GATE__NO_PROMOTION"
AUTHORITY = "CANDIDATE_IMPLEMENTATION__NO_SCIENTIFIC_PROMOTION_UNTIL_INDEPENDENT_CHECK"

PREREG = Path("research/TRUMP_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_EXACT_TWO_FACTOR_F_FACTOR_CARRIER_FALSIFIER_GATE_PREREGISTRATION_2026-09-16.json")
PREREG_BLOB = "fa34b59bf0f2eb1350c696e0d55b3e3b63f3c8fc"
PARENT_STATE = Path("registry/TRUMP_CURRENT_STATE_2026-09-15_v3.17.json")
PARENT_STATE_BLOB = "bf871e4e574381373f8c4d207eca9a12c9175ea4"
PARENT_RAW = Path("research/tools/apma_bucket_k5_raw_semantic_forensic/forensic.py")
PARENT_RAW_BLOB = "4128f0db77dfc1391b6ec539f201250bfb3d8b6e"


def root() -> Path:
    return Path(__file__).resolve().parents[3]


def git_blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def canonical_sha256(obj: Any) -> str:
    data = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def source_guard() -> dict[str, Any]:
    r = root()
    checks = {
        "prereg_blob": git_blob(r / PREREG) == PREREG_BLOB,
        "parent_v3_17_blob": git_blob(r / PARENT_STATE) == PARENT_STATE_BLOB,
        "parent_raw_semantic_forensic_blob": git_blob(r / PARENT_RAW) == PARENT_RAW_BLOB,
        "networkx_version_pinned": nx.__version__ == "3.6.1",
    }
    return {"ok": all(checks.values()), "checks": checks, "networkx_version": nx.__version__}


def exact_two_rows(arity: int) -> set[tuple[int, ...]]:
    if arity < 0:
        raise ValueError("NEGATIVE_ARITY")
    out: set[tuple[int, ...]] = set()
    for chosen in itertools.combinations(range(arity), 2):
        row = [0] * arity
        for p in chosen:
            row[p] = 1
        out.add(tuple(row))
    return out


def recognize_component(
    scopes: dict[str, list[int]],
    rows: dict[str, set[tuple[int, ...]]],
    provenance: dict[str, Any] | None = None,
) -> dict[str, Any]:
    factor_ids = sorted(scopes)
    if not factor_ids or set(factor_ids) != set(rows):
        return {"status": "REJECT_FACTOR_KEY_MISMATCH"}

    for fid in factor_ids:
        scope = [int(v) for v in scopes[fid]]
        if len(scope) != len(set(scope)):
            return {"status": "REJECT_DUPLICATE_VARIABLE_IN_FACTOR_SCOPE", "factor_id": fid}
        normalized_rows = {tuple(int(x) for x in row) for row in rows[fid]}
        if any(len(row) != len(scope) or any(x not in (0, 1) for x in row) for row in normalized_rows):
            return {"status": "REJECT_MALFORMED_RELATION_ROWS", "factor_id": fid}
        if normalized_rows != exact_two_rows(len(scope)):
            return {"status": "REJECT_NON_EXACT_WEIGHT_TWO_RELATION", "factor_id": fid}

    occurrences: dict[int, list[str]] = {}
    for fid in factor_ids:
        for var in scopes[fid]:
            occurrences.setdefault(int(var), []).append(fid)
    if not occurrences:
        # A component with no edge variables can still be recognized as the empty exact-degree-two system,
        # but every factor has degree < 2 and the solver will issue a local UNSAT certificate.
        occurrences = {}

    edges = []
    for var in sorted(occurrences):
        ends = occurrences[var]
        if len(ends) != 2:
            return {"status": f"REJECT_EDGE_VARIABLE_OCCURS_{len(ends)}_TIMES", "variable": var, "occurrences": sorted(ends)}
        if ends[0] == ends[1]:
            return {"status": "REJECT_SELF_LOOP_OCCURRENCE", "variable": var}
        u, v = sorted(ends)
        edges.append({"id": int(var), "u": u, "v": v})

    degree = {fid: len(scopes[fid]) for fid in factor_ids}
    edge_ids = [e["id"] for e in edges]
    return {
        "status": "READY_EXACT_TWO_FACTOR_COMPONENT",
        "vertices": factor_ids,
        "edges": edges,
        "edge_ids": edge_ids,
        "scopes": {fid: [int(v) for v in scopes[fid]] for fid in factor_ids},
        "degree": degree,
        "provenance": provenance or {},
    }


def _model_endpoints(model: dict[str, Any]) -> dict[int, tuple[str, str]]:
    return {int(e["id"]): (str(e["u"]), str(e["v"])) for e in model["edges"]}


def build_tutte_graph(model: dict[str, Any]) -> dict[str, Any]:
    if model.get("status") != "READY_EXACT_TWO_FACTOR_COMPONENT":
        raise ValueError("MODEL_NOT_READY")
    vertices = list(model["vertices"])
    edge_ids = [int(e) for e in model["edge_ids"]]
    edge_index = {e: i for i, e in enumerate(edge_ids)}
    vertex_index = {v: i for i, v in enumerate(vertices)}
    endpoints = _model_endpoints(model)

    H = nx.Graph()
    ports: dict[str, dict[int, str]] = {v: {} for v in vertices}
    for v in vertices:
        vi = vertex_index[v]
        incident = sorted(int(e) for e in model["scopes"][v])
        for e in incident:
            node = f"A|{vi}|{edge_index[e]}"
            H.add_node(node, kind="port", source_vertex=v, source_edge=e)
            ports[v][e] = node
        slack_count = len(incident) - 2
        if slack_count < 0:
            continue
        for j in range(slack_count):
            b = f"B|{vi}|{j}"
            H.add_node(b, kind="slack", source_vertex=v)
            for e in incident:
                H.add_edge(ports[v][e], b, kind="slack")

    cross_map: dict[frozenset[str], int] = {}
    for e in edge_ids:
        u, v = endpoints[e]
        a = ports[u][e]
        b = ports[v][e]
        H.add_edge(a, b, kind="cross", source_edge=e)
        cross_map[frozenset((a, b))] = e

    return {
        "graph": H,
        "ports": ports,
        "cross_map": cross_map,
        "vertex_index": vertex_index,
        "edge_index": edge_index,
        "node_count": H.number_of_nodes(),
        "edge_count": H.number_of_edges(),
    }


def normalize_matching(matching: set[tuple[str, str]] | list[tuple[str, str]]) -> list[list[str]]:
    pairs = []
    for a, b in matching:
        x, y = sorted((str(a), str(b)))
        pairs.append([x, y])
    return sorted(pairs)


def verify_perfect_matching(H: nx.Graph, matching: list[list[str]] | list[tuple[str, str]]) -> bool:
    used: set[str] = set()
    for pair in matching:
        if len(pair) != 2:
            return False
        a, b = str(pair[0]), str(pair[1])
        if a == b or a not in H or b not in H or not H.has_edge(a, b):
            return False
        if a in used or b in used:
            return False
        used.add(a)
        used.add(b)
    return len(used) == H.number_of_nodes()


def selected_original_edges(tutte: dict[str, Any], matching: list[list[str]]) -> list[int]:
    selected = []
    cross_map: dict[frozenset[str], int] = tutte["cross_map"]
    for a, b in matching:
        key = frozenset((str(a), str(b)))
        if key in cross_map:
            selected.append(int(cross_map[key]))
    return sorted(selected)


def verify_two_factor_selection(model: dict[str, Any], selected: list[int]) -> bool:
    selected_set = set(int(e) for e in selected)
    if not selected_set <= set(int(e) for e in model["edge_ids"]):
        return False
    endpoints = _model_endpoints(model)
    degree = {v: 0 for v in model["vertices"]}
    for e in selected_set:
        u, v = endpoints[e]
        degree[u] += 1
        degree[v] += 1
    return all(degree[v] == 2 for v in model["vertices"])


def maximum_matching(H: nx.Graph) -> list[list[str]]:
    matching = nx.algorithms.matching.max_weight_matching(H, maxcardinality=True)
    return normalize_matching(matching)


def verify_tutte_barrier(H: nx.Graph, barrier: list[str]) -> dict[str, Any]:
    A = {str(x) for x in barrier}
    if len(A) != len(barrier) or not A <= set(str(x) for x in H.nodes):
        return {"valid": False, "reason": "UNKNOWN_OR_DUPLICATE_BARRIER_VERTEX"}
    remaining = [x for x in H.nodes if str(x) not in A]
    sub = H.subgraph(remaining)
    components = [sorted(str(x) for x in c) for c in nx.connected_components(sub)]
    odd = [c for c in components if len(c) % 2 == 1]
    return {
        "valid": len(odd) > len(A),
        "barrier_size": len(A),
        "odd_component_count": len(odd),
        "component_sizes": sorted(len(c) for c in components),
    }


def generate_tutte_barrier(H: nx.Graph, base_matching: list[list[str]]) -> tuple[list[str], int]:
    nu = len(base_matching)
    calls = 0
    D: set[str] = set()
    nodes = sorted(str(x) for x in H.nodes)
    for x in nodes:
        Gx = H.copy()
        Gx.remove_node(x)
        mx = maximum_matching(Gx)
        calls += 1
        if len(mx) == nu:
            D.add(x)
    A: set[str] = set()
    for x in D:
        for y in H.neighbors(x):
            sy = str(y)
            if sy not in D:
                A.add(sy)
    return sorted(A), calls


def solve_model(model: dict[str, Any]) -> dict[str, Any]:
    if model.get("status") != "READY_EXACT_TWO_FACTOR_COMPONENT":
        return {"status": "REJECT_SCOPE", "recognition_status": model.get("status"), "matching_calls": 0}

    low = sorted(v for v, d in model["degree"].items() if int(d) < 2)
    if low:
        cert = {"kind": "LOCAL_DEGREE_LT_TWO", "vertices": low}
        valid = all(int(model["degree"][v]) < 2 for v in low)
        return {
            "status": "EXACT_UNSAT_LOCAL_DEGREE_LT_TWO" if valid else "UNKNOWN_INTERNAL_LOCAL_CERTIFICATE_FAILURE",
            "certificate": cert,
            "certificate_verified": valid,
            "matching_calls": 0,
            "selected_edge_ids": [],
        }

    tutte = build_tutte_graph(model)
    H: nx.Graph = tutte["graph"]
    matching = maximum_matching(H)
    calls = 1
    if verify_perfect_matching(H, matching):
        selected = selected_original_edges(tutte, matching)
        valid_two_factor = verify_two_factor_selection(model, selected)
        return {
            "status": "EXACT_SAT_TWO_FACTOR",
            "certificate": {"kind": "PERFECT_MATCHING", "matching": matching},
            "certificate_verified": valid_two_factor,
            "perfect_matching_verified": True,
            "selected_edge_ids": selected,
            "matching_calls": calls,
            "tutte_graph_vertices": tutte["node_count"],
            "tutte_graph_edges": tutte["edge_count"],
        } if valid_two_factor else {
            "status": "UNKNOWN_INTERNAL_RECONSTRUCTION_FAILURE",
            "certificate_verified": False,
            "matching_calls": calls,
        }

    barrier, extra = generate_tutte_barrier(H, matching)
    calls += extra
    check = verify_tutte_barrier(H, barrier)
    if not check["valid"]:
        return {
            "status": "UNKNOWN_INTERNAL_UNSAT_CERTIFICATE_FAILURE",
            "certificate": {"kind": "TUTTE_BARRIER", "barrier": barrier, "verification": check},
            "certificate_verified": False,
            "matching_calls": calls,
            "tutte_graph_vertices": tutte["node_count"],
            "tutte_graph_edges": tutte["edge_count"],
        }
    return {
        "status": "EXACT_UNSAT_TUTTE_BARRIER",
        "certificate": {"kind": "TUTTE_BARRIER", "barrier": barrier, "verification": check},
        "certificate_verified": True,
        "selected_edge_ids": [],
        "matching_calls": calls,
        "tutte_graph_vertices": tutte["node_count"],
        "tutte_graph_edges": tutte["edge_count"],
    }


def component_from_simple_graph(n: int, edge_pairs: list[tuple[int, int]], edge_offset: int = 1000) -> dict[str, Any]:
    factor_ids = [f"v{i}" for i in range(n)]
    scopes = {v: [] for v in factor_ids}
    for k, (a, b) in enumerate(edge_pairs):
        if not (0 <= a < b < n):
            raise ValueError("NON_CANONICAL_SIMPLE_EDGE")
        eid = edge_offset + k
        scopes[f"v{a}"].append(eid)
        scopes[f"v{b}"].append(eid)
    scopes = {v: sorted(es) for v, es in scopes.items()}
    rows = {v: exact_two_rows(len(scopes[v])) for v in factor_ids}
    return recognize_component(scopes, rows, {"kind": "GENERATED_SIMPLE_GRAPH", "n": n, "edges": [list(e) for e in edge_pairs]})


def brute_force_two_factor_truth(n: int, edge_pairs: list[tuple[int, int]]) -> bool:
    m = len(edge_pairs)
    for bits in itertools.product((0, 1), repeat=m):
        deg = [0] * n
        for bit, (a, b) in zip(bits, edge_pairs):
            if bit:
                deg[a] += 1
                deg[b] += 1
        if all(d == 2 for d in deg):
            return True
    return False


def extract_parent_k5_model() -> dict[str, Any]:
    raw = parent.build_raw_k5("EXACT_2_OF_4")
    prep = parent.v38._prepare(raw)
    if prep.get("status") != "READY":
        raise RuntimeError(f"PARENT_PREP_NOT_READY:{prep.get('status')}")
    factors = prep["conditioned"]
    core = [int(v) for v in prep["core"]]
    candidates = []
    for comp in parent.components(factors, core):
        if len(comp) < 3:
            continue
        scopes: dict[str, list[int]] = {}
        rows: dict[str, set[tuple[int, ...]]] = {}
        for i in comp:
            f = factors[i]
            scope, rel_rows = parent.residual_relation(f, core)
            scopes[str(f["id"])] = [int(v) for v in scope]
            rows[str(f["id"])] = {tuple(int(x) for x in r) for r in rel_rows}
        model = recognize_component(scopes, rows, {
            "kind": "PARENT_RAW_K5_EXACT_2_OF_4",
            "core": core,
            "core_state": [int(x) for x in prep["state"]],
            "factor_ids": sorted(scopes),
        })
        if model.get("status") == "READY_EXACT_TWO_FACTOR_COMPONENT":
            candidates.append((model, comp))
    if len(candidates) != 1:
        raise RuntimeError(f"EXPECTED_ONE_RECOGNIZED_PARENT_COMPONENT:{len(candidates)}")
    model, comp = candidates[0]
    return {"raw": raw, "prep": prep, "model": model, "component": comp}


def replay_parent_component(parent_case: dict[str, Any], selected: list[int]) -> dict[str, Any]:
    prep = parent_case["prep"]
    model = parent_case["model"]
    assignment = {int(v): int(x) for v, x in zip(prep["core"], prep["state"])}
    selected_set = set(int(e) for e in selected)
    for e in model["edge_ids"]:
        assignment[int(e)] = int(int(e) in selected_set)

    original_bucket = {str(f["id"]): f for f in prep["ready"]["bucket"]}
    checks = {}
    for fid in model["vertices"]:
        f = original_bucket[fid]
        scope = [int(v) for v in f["scope"]]
        if not all(v in assignment for v in scope):
            checks[fid] = False
            continue
        row = tuple(assignment[v] for v in scope)
        allowed = {tuple(int(x) for x in r) for r in f["rows"]}
        checks[fid] = row in allowed
    return {"ok": all(checks.values()), "factor_checks": checks, "assigned_variable_count": len(assignment)}


def tamper_checks(model: dict[str, Any], solution: dict[str, Any]) -> dict[str, bool]:
    tutte = build_tutte_graph(model)
    H: nx.Graph = tutte["graph"]
    sat_reject = True
    if solution.get("status") == "EXACT_SAT_TWO_FACTOR":
        matching = [list(x) for x in solution["certificate"]["matching"]]
        tampered = matching[:-1] if matching else [["NO_SUCH_NODE", "ALSO_NO_SUCH_NODE"]]
        sat_reject = not verify_perfect_matching(H, tampered)

    # Exercise UNSAT certificate tampering using the preregistered bowtie control.
    bowtie_edges = [(0, 1), (0, 2), (1, 2), (0, 3), (0, 4), (3, 4)]
    bowtie = component_from_simple_graph(5, bowtie_edges, 3000)
    bsol = solve_model(bowtie)
    unsat_reject = False
    if bsol.get("status") == "EXACT_UNSAT_TUTTE_BARRIER":
        Hb = build_tutte_graph(bowtie)["graph"]
        bad = list(bsol["certificate"]["barrier"]) + ["NO_SUCH_NODE"]
        unsat_reject = not verify_tutte_barrier(Hb, bad)["valid"]
    return {"tampered_sat_matching_rejected": sat_reject, "tampered_unsat_barrier_rejected": unsat_reject}


def exhaustive_small_graph_census() -> dict[str, Any]:
    statuses: list[str] = []
    mismatches = 0
    unknown = 0
    total = 0
    sat_truth = 0
    sat_carrier = 0
    max_matching_calls = 0
    for n in (3, 4, 5):
        possible = list(itertools.combinations(range(n), 2))
        for graph_mask in range(1 << len(possible)):
            edges = [possible[i] for i in range(len(possible)) if (graph_mask >> i) & 1]
            truth = brute_force_two_factor_truth(n, edges)
            model = component_from_simple_graph(n, edges, edge_offset=10000 + n * 100 + graph_mask * 20)
            sol = solve_model(model)
            if sol["status"] == "EXACT_SAT_TWO_FACTOR":
                got = True
                statuses.append("S")
                sat_carrier += 1
            elif sol["status"] in {"EXACT_UNSAT_TUTTE_BARRIER", "EXACT_UNSAT_LOCAL_DEGREE_LT_TWO"}:
                got = False
                statuses.append("U")
            else:
                got = None
                statuses.append("X")
                unknown += 1
            if truth:
                sat_truth += 1
            if got is None or got != truth:
                mismatches += 1
            total += 1
            max_matching_calls = max(max_matching_calls, int(sol.get("matching_calls", 0)))
    return {
        "graph_count": total,
        "sat_truth_count": sat_truth,
        "sat_carrier_count": sat_carrier,
        "mismatch_count": mismatches,
        "unknown_count": unknown,
        "status_vector_sha256": hashlib.sha256("".join(statuses).encode("ascii")).hexdigest(),
        "maximum_matching_calls_for_one_graph": max_matching_calls,
    }


def profile() -> dict[str, Any]:
    guard = source_guard()
    parent_case = extract_parent_k5_model()
    parent_model = parent_case["model"]
    parent_solution = solve_model(parent_model)
    parent_replay = replay_parent_component(parent_case, parent_solution.get("selected_edge_ids", [])) if parent_solution.get("status") == "EXACT_SAT_TWO_FACTOR" else {"ok": False}

    c5 = component_from_simple_graph(5, [(0, 1), (1, 2), (2, 3), (3, 4), (0, 4)], 2000)
    k4 = component_from_simple_graph(4, list(itertools.combinations(range(4), 2)), 2100)
    bowtie = component_from_simple_graph(5, [(0, 1), (0, 2), (1, 2), (0, 3), (0, 4), (3, 4)], 2200)
    path3 = component_from_simple_graph(3, [(0, 1), (1, 2)], 2300)
    controls = {
        "C5": solve_model(c5),
        "K4": solve_model(k4),
        "BOWTIE": solve_model(bowtie),
        "DEGREE_LT_TWO": solve_model(path3),
    }

    # Recognition falsifiers.
    bad_rows_scopes = {"a": [1, 2], "b": [1, 2]}
    bad_rows = {"a": {(0, 0), (1, 1)}, "b": exact_two_rows(2)}
    non_exact = recognize_component(bad_rows_scopes, bad_rows)
    once = recognize_component({"a": [1, 2], "b": [2, 3]}, {"a": exact_two_rows(2), "b": exact_two_rows(2)})
    thrice = recognize_component(
        {"a": [1, 2], "b": [1, 3], "c": [1, 4], "d": [2, 3, 4]},
        {k: exact_two_rows(len(v)) for k, v in {"a": [1, 2], "b": [1, 3], "c": [1, 4], "d": [2, 3, 4]}.items()},
    )
    self_loop = recognize_component({"a": [1, 1]}, {"a": exact_two_rows(2)})

    tamper = tamper_checks(parent_model, parent_solution)
    census = exhaustive_small_graph_census()

    bowtie_cert_ok = controls["BOWTIE"].get("status") == "EXACT_UNSAT_TUTTE_BARRIER" and controls["BOWTIE"].get("certificate_verified") is True
    parent_tutte = build_tutte_graph(parent_model)
    m = len(parent_model["edge_ids"])
    n_h_bound = int(parent_tutte["node_count"]) <= 4 * m
    edge_bound_poly = int(parent_tutte["edge_count"]) <= m + (2 * m) ** 2

    checks = {
        "source_guard": guard["ok"],
        "parent_recognized": parent_model.get("status") == "READY_EXACT_TWO_FACTOR_COMPONENT",
        "parent_sat": parent_solution.get("status") == "EXACT_SAT_TWO_FACTOR",
        "parent_sat_certificate_verified": parent_solution.get("certificate_verified") is True,
        "parent_original_relation_replay": parent_replay.get("ok") is True,
        "parent_selected_edges_form_two_factor": verify_two_factor_selection(parent_model, parent_solution.get("selected_edge_ids", [])),
        "C5_sat": controls["C5"].get("status") == "EXACT_SAT_TWO_FACTOR",
        "K4_sat": controls["K4"].get("status") == "EXACT_SAT_TWO_FACTOR",
        "bowtie_exact_unsat_with_tutte_certificate": bowtie_cert_ok,
        "degree_lt_two_exact_local_unsat": controls["DEGREE_LT_TWO"].get("status") == "EXACT_UNSAT_LOCAL_DEGREE_LT_TWO",
        "non_exact_weight_two_rejected": non_exact.get("status") == "REJECT_NON_EXACT_WEIGHT_TWO_RELATION",
        "variable_occurs_once_rejected": once.get("status") == "REJECT_EDGE_VARIABLE_OCCURS_1_TIMES",
        "variable_occurs_three_times_rejected": thrice.get("status") == "REJECT_EDGE_VARIABLE_OCCURS_3_TIMES",
        "self_loop_or_duplicate_scope_rejected": self_loop.get("status") == "REJECT_DUPLICATE_VARIABLE_IN_FACTOR_SCOPE",
        "tampered_sat_matching_rejected": tamper["tampered_sat_matching_rejected"],
        "tampered_unsat_barrier_rejected": tamper["tampered_unsat_barrier_rejected"],
        "small_graph_census_zero_mismatch": census["mismatch_count"] == 0,
        "small_graph_census_zero_unknown": census["unknown_count"] == 0,
        "tutte_vertex_bound": n_h_bound,
        "tutte_edge_polynomial_bound": edge_bound_poly,
        "matching_call_bound_parent": int(parent_solution.get("matching_calls", 0)) <= int(parent_tutte["node_count"]) + 1,
    }
    passed = all(checks.values())

    return {
        "artifact_id": ARTIFACT_ID,
        "authority": AUTHORITY,
        "verdict": PASS_VERDICT if passed else FAIL_VERDICT,
        "source_guard": guard,
        "checks": checks,
        "parent_raw_k5": {
            "recognition_status": parent_model.get("status"),
            "vertex_count": len(parent_model["vertices"]),
            "edge_count": len(parent_model["edge_ids"]),
            "solve": parent_solution,
            "original_relation_replay": parent_replay,
            "selected_edge_count": len(parent_solution.get("selected_edge_ids", [])),
        },
        "controls": controls,
        "recognition_falsifiers": {
            "non_exact_weight_two": non_exact,
            "variable_occurs_once": once,
            "variable_occurs_three_times": thrice,
            "duplicate_scope_self_loop": self_loop,
        },
        "tamper_checks": tamper,
        "exhaustive_small_graph_census": census,
        "resource_receipt": {
            "original_component_edge_count_m": m,
            "parent_tutte_vertices": parent_tutte["node_count"],
            "parent_tutte_edges": parent_tutte["edge_count"],
            "symbolic_vertex_bound": "N_H<=4m",
            "symbolic_edge_bound": "M_H<=m+(2m)^2=O(m^2)",
            "maximum_matching_call_bound": "AT_MOST_N_H+1",
            "documented_per_matching_call": "O(N_H^3)",
            "total_matching_bound": "O(N_H^4)=POLYNOMIAL_IN_ORIGINAL_EXPLICIT_INPUT_SIZE",
            "certificate_bytes": "O(N_H)_MATCHING_OR_BARRIER_PLUS_POLYNOMIAL_PROVENANCE",
            "size4_boolean_separator_assignments_enumerated": 0,
            "separator_sets_size_ge_3_executed_as_boolean_branches": 0,
            "unbounded_recursive_calls": 0,
            "three_plus_join_chains_materialized": 0,
            "global_residual_cartesian_products_materialized": 0,
            "budget_raise": False,
        },
        "carrier_contract": {
            "semantic_object": "UNDIRECTED_TWO_FACTOR__F_FACTOR_WITH_F_V_EQUALS_TWO",
            "tutte_reduction": "INCIDENCE_PORTS_A(v,e)_PLUS_d(v)-2_SLACK_VERTICES_B(v,j)",
            "matching_backend": f"networkx-{nx.__version__}:max_weight_matching(maxcardinality=True)",
            "oracle_authority": "NONE_WITHOUT_CERTIFICATE",
            "SAT_certificate": "PERFECT_MATCHING_PLUS_RECONSTRUCTED_EDGE_ASSIGNMENT_AND_ORIGINAL_RELATION_REPLAY",
            "UNSAT_certificate": "DIRECTLY_VERIFIED_TUTTE_BARRIER_odd_components(H-A)>|A|",
            "failure_mode": "UNKNOWN_INTERNAL_FAIL_CLOSED",
        },
        "scientific_firewall": {
            "P_VS_NP": "OPEN",
            "GENERAL_SAT_IN_P": "NOT_PROVED",
            "CONNECTED_MIXED_CORE_SOLVED": "NO",
            "GENERAL_RESIDUAL_SEPARATOR_TRACTABILITY": "NOT_PROVED",
            "GENERAL_TWO_FACTOR_CARRIER_IN_TRUMP": "SEALED_ONLY_IF_THIS_GATE_AND_INDEPENDENT_CHECKER_PASS",
            "SIZE4_BRANCHING_LICENSED": False,
            "EXTRA_RECURSION_AUTHORIZED": False,
            "GLOBAL_APMA_FRONTIER_ADVANCE": "NONE_PENDING_HQ_REVIEW",
        },
    }


if __name__ == "__main__":
    print(json.dumps(profile(), ensure_ascii=False, sort_keys=True))
