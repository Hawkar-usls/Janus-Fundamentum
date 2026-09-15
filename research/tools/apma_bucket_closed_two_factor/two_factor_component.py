from __future__ import annotations

import hashlib
import itertools
import json
import math
from typing import Any

from research.tools.apma_bucket_closed_two_factor import matching_core


def canonical_bytes(obj: Any) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_obj(obj: Any) -> str:
    return hashlib.sha256(canonical_bytes(obj)).hexdigest()


def residual_scope(factor: dict[str, Any], core: list[int]) -> list[int]:
    core_set = {int(v) for v in core}
    return [int(v) for v in factor["scope"] if int(v) not in core_set]


def residual_rows(factor: dict[str, Any], core: list[int]) -> list[tuple[int, ...]]:
    scope = [int(v) for v in factor["scope"]]
    residual = residual_scope(factor, core)
    pos = {v: i for i, v in enumerate(scope)}
    return sorted({tuple(int(row[pos[v]]) for v in residual) for row in factor["rows"]})


def _exact_weight_two_relation(scope: list[int], rows: list[tuple[int, ...]]) -> dict[str, Any]:
    d = len(scope)
    expected_count = math.comb(d, 2) if d >= 2 else 0
    if d < 2:
        return {"ok": False, "reason": "RESIDUAL_ARITY_LT_2", "arity": d}
    if len(rows) != expected_count:
        return {
            "ok": False,
            "reason": "ROW_COUNT_NOT_D_CHOOSE_2",
            "arity": d,
            "row_count": len(rows),
            "expected_row_count": expected_count,
        }
    seen_pairs: set[tuple[int, int]] = set()
    for row in rows:
        if len(row) != d or any(bit not in (0, 1) for bit in row):
            return {"ok": False, "reason": "NON_BOOLEAN_OR_WRONG_ARITY_ROW"}
        ones = tuple(i for i, bit in enumerate(row) if int(bit) == 1)
        if len(ones) != 2:
            return {"ok": False, "reason": "ROW_NOT_HAMMING_WEIGHT_TWO", "row": list(row)}
        if ones in seen_pairs:
            return {"ok": False, "reason": "DUPLICATE_ONE_POSITION_PAIR", "pair": list(ones)}
        seen_pairs.add(ones)
    if len(seen_pairs) != expected_count:
        return {"ok": False, "reason": "INCOMPLETE_ONE_POSITION_PAIR_COVERAGE"}
    return {
        "ok": True,
        "reason": "EXACT_HAMMING_WEIGHT_TWO_RELATION",
        "arity": d,
        "row_count": len(rows),
        "one_position_pair_count": len(seen_pairs),
    }


def recognize_component(
    conditioned: list[dict[str, Any]],
    component: list[int],
    core: list[int],
    cut: list[int] | set[int],
) -> dict[str, Any]:
    comp = sorted(int(i) for i in component)
    if len(comp) < 3:
        return {"status": "NOT_GT2_COMPONENT", "component": comp}

    factor_records: list[dict[str, Any]] = []
    occurrence: dict[int, list[int]] = {}
    for local_vertex, conditioned_index in enumerate(comp):
        factor = conditioned[conditioned_index]
        scope = residual_scope(factor, core)
        rows = residual_rows(factor, core)
        relation_check = _exact_weight_two_relation(scope, rows)
        if not relation_check["ok"]:
            return {
                "status": "NOT_EXACT_TWO_FACTOR_COMPONENT",
                "reason": relation_check["reason"],
                "component": comp,
                "factor_id": str(factor["id"]),
                "conditioned_index": conditioned_index,
                "relation_check": relation_check,
            }
        factor_records.append({
            "local_vertex": local_vertex,
            "conditioned_index": conditioned_index,
            "factor_id": str(factor["id"]),
            "residual_scope": scope,
            "residual_rows": [list(row) for row in rows],
            "arity": len(scope),
        })
        for var in scope:
            occurrence.setdefault(int(var), []).append(local_vertex)

    edge_records: list[dict[str, Any]] = []
    for var in sorted(occurrence):
        endpoints = sorted(set(occurrence[var]))
        if len(endpoints) != 2 or len(occurrence[var]) != 2 or endpoints[0] == endpoints[1]:
            return {
                "status": "NOT_EXACT_TWO_FACTOR_COMPONENT",
                "reason": "RESIDUAL_VARIABLE_INCIDENCE_NOT_EXACTLY_TWO_DISTINCT_FACTORS",
                "component": comp,
                "residual_variable": int(var),
                "occurrence_vertices": list(occurrence[var]),
            }
        edge_records.append({
            "var": int(var),
            "u": int(endpoints[0]),
            "v": int(endpoints[1]),
        })

    cut_set = {int(v) for v in cut}
    boundary = sorted(var for var in occurrence if var in cut_set)
    graph_public = {
        "factor_count": len(factor_records),
        "edge_count": len(edge_records),
        "factor_ids": [r["factor_id"] for r in factor_records],
        "component_conditioned_indices": comp,
        "edges": edge_records,
    }
    graph_public["graph_sha256"] = sha256_obj(graph_public)

    if boundary:
        return {
            "status": "OPEN_TWO_FACTOR_BOUNDARY_INTERFACE_NOT_SEALED",
            "component": comp,
            "boundary_scope": boundary,
            "graph": graph_public,
        }

    return {
        "status": "ADMIT_CLOSED_INTERNAL_EXACT_TWO_FACTOR_COMPONENT",
        "component": comp,
        "boundary_scope": [],
        "factor_records": factor_records,
        "edge_records": edge_records,
        "graph": graph_public,
    }


def build_tutte_gadget(recognized: dict[str, Any]) -> dict[str, Any]:
    if recognized.get("status") != "ADMIT_CLOSED_INTERNAL_EXACT_TWO_FACTOR_COMPONENT":
        raise ValueError("COMPONENT_NOT_ADMITTED_TWO_FACTOR")
    factor_count = len(recognized["factor_records"])
    incident: dict[int, list[int]] = {v: [] for v in range(factor_count)}
    endpoints: dict[int, tuple[int, int]] = {}
    for edge in recognized["edge_records"]:
        var = int(edge["var"])
        u, v = int(edge["u"]), int(edge["v"])
        incident[u].append(var)
        incident[v].append(var)
        endpoints[var] = (u, v)
    for v in incident:
        incident[v].sort()

    vertex_info: dict[int, dict[str, Any]] = {}
    incidence_vertex: dict[tuple[int, int], int] = {}
    next_id = 0
    for v in range(factor_count):
        for var in incident[v]:
            incidence_vertex[(v, var)] = next_id
            vertex_info[next_id] = {"kind": "A", "factor_vertex": v, "residual_var": var}
            next_id += 1

    auxiliary_vertices: dict[int, list[int]] = {}
    for v in range(factor_count):
        count = len(incident[v]) - 2
        if count < 0:
            raise ValueError("DEGREE_LT_2_REACHED_TUTTE_GADGET")
        auxiliary_vertices[v] = []
        for j in range(count):
            auxiliary_vertices[v].append(next_id)
            vertex_info[next_id] = {"kind": "B", "factor_vertex": v, "aux_index": j}
            next_id += 1

    edges: set[tuple[int, int]] = set()
    local_edge_count = 0
    for v in range(factor_count):
        for a in [incidence_vertex[(v, var)] for var in incident[v]]:
            for b in auxiliary_vertices[v]:
                edge = (a, b) if a < b else (b, a)
                edges.add(edge)
                local_edge_count += 1

    cross_edge_to_var: dict[tuple[int, int], int] = {}
    for var in sorted(endpoints):
        u, v = endpoints[var]
        a = incidence_vertex[(u, var)]
        b = incidence_vertex[(v, var)]
        edge = (a, b) if a < b else (b, a)
        edges.add(edge)
        cross_edge_to_var[edge] = var

    vertices = list(range(next_id))
    edge_list = sorted(edges)
    public = {
        "vertices": vertices,
        "edges": [list(e) for e in edge_list],
        "vertex_count": len(vertices),
        "edge_count": len(edge_list),
        "local_biclique_edge_count": local_edge_count,
        "cross_edge_count": len(cross_edge_to_var),
        "vertex_info": {str(k): v for k, v in sorted(vertex_info.items())},
        "cross_edge_to_residual_var": {
            f"{a}:{b}": int(var) for (a, b), var in sorted(cross_edge_to_var.items())
        },
    }
    public["gadget_sha256"] = sha256_obj(public)
    return {
        "public": public,
        "vertices": vertices,
        "edges": edge_list,
        "vertex_info": vertex_info,
        "cross_edge_to_var": cross_edge_to_var,
        "incidence_vertex": incidence_vertex,
    }


def _selected_from_matching(gadget: dict[str, Any], matching_edges: list[tuple[int, int]]) -> list[int]:
    selected: list[int] = []
    cross = gadget["cross_edge_to_var"]
    for raw_a, raw_b in matching_edges:
        a, b = int(raw_a), int(raw_b)
        edge = (a, b) if a < b else (b, a)
        if edge in cross:
            selected.append(int(cross[edge]))
    return sorted(selected)


def verify_sat_certificate(
    recognized: dict[str, Any],
    certificate: dict[str, Any],
) -> dict[str, Any]:
    gadget = build_tutte_gadget(recognized)
    if certificate.get("gadget_sha256") != gadget["public"]["gadget_sha256"]:
        return {"ok": False, "reason": "GADGET_HASH_MISMATCH"}
    matching_edges = [tuple(int(x) for x in e) for e in certificate.get("perfect_matching", [])]
    static_matching = matching_core.verify_perfect_matching(gadget["vertices"], gadget["edges"], matching_edges)
    if not static_matching["ok"]:
        return {"ok": False, "reason": "STATIC_PERFECT_MATCHING_REJECTED", "detail": static_matching}
    selected = _selected_from_matching(gadget, matching_edges)
    claimed_selected = sorted(int(v) for v in certificate.get("selected_residual_vars", []))
    if selected != claimed_selected:
        return {"ok": False, "reason": "SELECTED_RESIDUAL_VAR_MAP_MISMATCH", "derived": selected, "claimed": claimed_selected}

    selected_set = set(selected)
    factor_rows: dict[str, list[int]] = {}
    factor_selected: dict[str, list[int]] = {}
    edge_by_var = {int(e["var"]): e for e in recognized["edge_records"]}
    for factor in recognized["factor_records"]:
        local_vertex = int(factor["local_vertex"])
        incident = sorted(
            var
            for var, edge in edge_by_var.items()
            if local_vertex in (int(edge["u"]), int(edge["v"]))
        )
        chosen = [var for var in incident if var in selected_set]
        if len(chosen) != 2:
            return {"ok": False, "reason": "FACTOR_SELECTED_DEGREE_NOT_TWO", "factor_id": factor["factor_id"], "chosen": chosen}
        assignment = {var: int(var in selected_set) for var in incident}
        row = [assignment[var] for var in factor["residual_scope"]]
        allowed = {tuple(int(x) for x in r) for r in factor["residual_rows"]}
        if tuple(row) not in allowed:
            return {"ok": False, "reason": "SELECTED_RESIDUAL_ROW_NOT_IN_FACTOR", "factor_id": factor["factor_id"], "row": row}
        factor_rows[str(factor["factor_id"])] = row
        factor_selected[str(factor["factor_id"])] = chosen

    claimed_map = {
        str(k): sorted(int(v) for v in values)
        for k, values in certificate.get("factor_selected_incident_vars", {}).items()
    }
    if claimed_map != factor_selected:
        return {"ok": False, "reason": "FACTOR_SELECTED_INCIDENT_MAP_MISMATCH", "derived": factor_selected, "claimed": claimed_map}

    residual_assignment = {
        int(edge["var"]): int(int(edge["var"]) in selected_set)
        for edge in recognized["edge_records"]
    }
    return {
        "ok": True,
        "reason": "STATIC_TWO_FACTOR_SAT_CERTIFICATE_VERIFIED",
        "selected_residual_vars": selected,
        "residual_assignment": residual_assignment,
        "factor_residual_rows": factor_rows,
        "factor_selected_incident_vars": factor_selected,
        "static_matching": static_matching,
    }


def verify_unsat_certificate(
    recognized: dict[str, Any],
    certificate: dict[str, Any],
) -> dict[str, Any]:
    gadget = build_tutte_gadget(recognized)
    if certificate.get("gadget_sha256") != gadget["public"]["gadget_sha256"]:
        return {"ok": False, "reason": "GADGET_HASH_MISMATCH"}
    obstruction = [int(v) for v in certificate.get("tutte_obstruction_U", [])]
    static = matching_core.verify_tutte_obstruction(gadget["vertices"], gadget["edges"], obstruction)
    if not static["ok"]:
        return {"ok": False, "reason": "STATIC_TUTTE_OBSTRUCTION_REJECTED", "detail": static}
    return {
        "ok": True,
        "reason": "STATIC_TWO_FACTOR_UNSAT_CERTIFICATE_VERIFIED",
        "tutte_obstruction": static,
    }


def solve_component(recognized: dict[str, Any]) -> dict[str, Any]:
    gadget = build_tutte_gadget(recognized)
    matching = matching_core.maximum_matching(gadget["vertices"], gadget["edges"])
    if matching["perfect"]:
        matching_edges = [tuple(int(x) for x in e) for e in matching["matching"]]
        selected = _selected_from_matching(gadget, matching_edges)
        edge_by_var = {int(e["var"]): e for e in recognized["edge_records"]}
        factor_selected: dict[str, list[int]] = {}
        for factor in recognized["factor_records"]:
            lv = int(factor["local_vertex"])
            factor_selected[str(factor["factor_id"])] = sorted(
                var
                for var in selected
                if lv in (int(edge_by_var[var]["u"]), int(edge_by_var[var]["v"]))
            )
        certificate = {
            "kind": "PERFECT_MATCHING_TWO_FACTOR_SAT_CERTIFICATE",
            "gadget_sha256": gadget["public"]["gadget_sha256"],
            "perfect_matching": [list(e) for e in matching_edges],
            "selected_residual_vars": selected,
            "factor_selected_incident_vars": factor_selected,
        }
        static = verify_sat_certificate(recognized, certificate)
        if not static["ok"]:
            return {
                "status": "OPEN_MATCHING_CARRIER_INTERNAL_FAILURE",
                "reason": "CANDIDATE_SAT_CERTIFICATE_FAILED_STATIC_VERIFICATION",
                "certificate": certificate,
                "static_verification": static,
                "gadget_public": gadget["public"],
            }
        return {
            "status": "SAT_BY_VERIFIED_TWO_FACTOR_PERFECT_MATCHING",
            "certificate": certificate,
            "static_verification": static,
            "gadget_public": gadget["public"],
            "matching_solver_receipt": matching,
        }

    obstruction = matching_core.derive_tutte_obstruction(gadget["vertices"], gadget["edges"])
    if obstruction.get("status") != "VERIFIED_TUTTE_OBSTRUCTION":
        return {
            "status": "OPEN_MATCHING_CARRIER_INTERNAL_FAILURE",
            "reason": "NO_PERFECT_MATCHING_BUT_NO_STATIC_TUTTE_CERTIFICATE",
            "obstruction_derivation": obstruction,
            "gadget_public": gadget["public"],
            "matching_solver_receipt": matching,
        }
    certificate = {
        "kind": "TUTTE_OBSTRUCTION_TWO_FACTOR_UNSAT_CERTIFICATE",
        "gadget_sha256": gadget["public"]["gadget_sha256"],
        "tutte_obstruction_U": list(obstruction["U"]),
    }
    static = verify_unsat_certificate(recognized, certificate)
    if not static["ok"]:
        return {
            "status": "OPEN_MATCHING_CARRIER_INTERNAL_FAILURE",
            "reason": "CANDIDATE_UNSAT_CERTIFICATE_FAILED_STATIC_VERIFICATION",
            "certificate": certificate,
            "static_verification": static,
            "obstruction_derivation": obstruction,
            "gadget_public": gadget["public"],
        }
    return {
        "status": "UNSAT_BY_VERIFIED_TWO_FACTOR_TUTTE_OBSTRUCTION",
        "certificate": certificate,
        "static_verification": static,
        "obstruction_derivation": obstruction,
        "gadget_public": gadget["public"],
        "matching_solver_receipt": matching,
    }


def recover_conditioned_factor_rows(
    conditioned: list[dict[str, Any]],
    recognized: dict[str, Any],
    core: list[int],
    state: tuple[int, ...],
    residual_assignment: dict[int, int],
) -> dict[str, Any]:
    core_assignment = {int(v): int(bit) for v, bit in zip(core, state)}
    chosen: list[dict[str, Any]] = []
    for record in recognized["factor_records"]:
        factor = conditioned[int(record["conditioned_index"])]
        assignment = dict(core_assignment)
        for var in record["residual_scope"]:
            if int(var) not in residual_assignment:
                return {"ok": False, "reason": "RESIDUAL_ASSIGNMENT_INCOMPLETE", "factor_id": factor["id"], "variable": int(var)}
            assignment[int(var)] = int(residual_assignment[int(var)])
        target = tuple(int(assignment[int(v)]) for v in factor["scope"])
        allowed = {tuple(int(x) for x in row) for row in factor["rows"]}
        if target not in allowed:
            return {"ok": False, "reason": "CONDITIONED_FACTOR_ROW_REPLAY_FAILED", "factor_id": factor["id"], "row": list(target)}
        chosen.append({
            "conditioned_index": int(record["conditioned_index"]),
            "factor_id": str(factor["id"]),
            "sorted_row": list(target),
        })
    return {"ok": True, "reason": "CONDITIONED_TWO_FACTOR_ROWS_REPLAYED", "chosen_rows": chosen}
