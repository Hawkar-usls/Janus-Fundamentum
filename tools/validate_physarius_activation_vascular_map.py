#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def fail(msg: str) -> None:
    raise SystemExit(f"PHYSARIUS_ACTIVATION_VASCULAR_MAP_INVALID: {msg}")


def load(path: str) -> dict:
    obj = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        fail(f"{path} must contain a JSON object")
    return obj


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--map", default="registry/PHYSARIUS_ACTIVATION_CIRCUIT_VASCULAR_MAP_v1.json")
    ap.add_argument("--constitution", default="registry/PHYSARIUS_ACTIVATION_CIRCUIT_VASCULAR_CONSTITUTION_v1.json")
    ap.add_argument("--strict", action="store_true", help="also require every node binding and every edge to be fully vascularized")
    args = ap.parse_args()

    vascular = load(args.map)
    constitution = load(args.constitution)

    required_laws = {
        "NO_CROSS_REPO_STATE_WITHOUT_VESSEL_RECEIPT",
        "VESSEL_NE_PERMISSION",
        "DELIVERY_NE_EXECUTION",
        "TWO_TRANSPORTS_NE_TWO_EXECUTIONS",
        "MISSING_OR_AMBIGUOUS_BINDING_FAILS_CLOSED",
    }
    laws = set(constitution.get("laws") or [])
    missing_laws = sorted(required_laws - laws)
    if missing_laws:
        fail(f"missing constitutional laws: {missing_laws}")

    nodes = vascular.get("nodes")
    edges = vascular.get("edges")
    if not isinstance(nodes, list) or not nodes:
        fail("nodes must be a non-empty list")
    if not isinstance(edges, list) or not edges:
        fail("edges must be a non-empty list")

    node_by_id: dict[str, dict] = {}
    unresolved: list[str] = []
    for node in nodes:
        if not isinstance(node, dict):
            fail("node entry is not an object")
        node_id = str(node.get("id") or "").strip()
        if not node_id or node_id in node_by_id:
            fail(f"invalid or duplicate node id: {node_id!r}")
        node_by_id[node_id] = node
        binding = str(node.get("binding") or "")
        repo = node.get("repository")
        if binding == "CONFIRMED":
            if not isinstance(repo, str) or repo.count("/") != 1:
                fail(f"confirmed node {node_id} lacks owner/repo binding")
        else:
            unresolved.append(node_id)
            if repo is not None:
                fail(f"unresolved node {node_id} must not carry speculative repository binding")

    edge_ids: set[str] = set()
    migration_edges: list[str] = []
    blocked_edges: list[str] = []
    design_edges: list[str] = []
    live_edges: list[str] = []

    for edge in edges:
        if not isinstance(edge, dict):
            fail("edge entry is not an object")
        edge_id = str(edge.get("edge_id") or "").strip()
        if not edge_id or edge_id in edge_ids:
            fail(f"invalid or duplicate edge id: {edge_id!r}")
        edge_ids.add(edge_id)

        src = str(edge.get("source") or "")
        dst = str(edge.get("destination") or "")
        if src not in node_by_id or dst not in node_by_id:
            fail(f"edge {edge_id} references unknown node: {src}->{dst}")
        if edge.get("receipt_required") is not True:
            fail(f"edge {edge_id} violates NO_CROSS_REPO_STATE_WITHOUT_VESSEL_RECEIPT")
        if not str(edge.get("authority_ceiling") or "").strip():
            fail(f"edge {edge_id} lacks authority ceiling")

        state = str(edge.get("state") or "")
        src_bound = node_by_id[src].get("binding") == "CONFIRMED"
        dst_bound = node_by_id[dst].get("binding") == "CONFIRMED"
        if (not src_bound or not dst_bound) and not (state.startswith("BLOCKED_") or state == "DESIGN_REQUIRED"):
            fail(f"edge {edge_id} uses unresolved endpoint without fail-closed state")

        if state == "LIVE":
            live_edges.append(edge_id)
        elif "LEGACY_TO_VASCULARIZE" in state or "STANDARD_PHYSARIUS_VESSEL_BINDING_REQUIRED" in state:
            migration_edges.append(edge_id)
        elif state.startswith("BLOCKED_"):
            blocked_edges.append(edge_id)
        elif state == "DESIGN_REQUIRED":
            design_edges.append(edge_id)

        if edge.get("class") == "MOTOR_GRANT":
            if edge.get("create_only_execution_claim_required") is not True:
                fail(f"motor edge {edge_id} lacks create-only execution claim law")
            if edge.get("dual_transport_single_execution") is not True:
                fail(f"motor edge {edge_id} lacks two-transports-ne-two-executions law")

    strict_open = bool(unresolved or migration_edges or blocked_edges or design_edges)
    if args.strict and strict_open:
        fail(
            "strict vascularization incomplete: "
            + json.dumps(
                {
                    "unresolved_nodes": unresolved,
                    "migration_edges": migration_edges,
                    "blocked_edges": blocked_edges,
                    "design_edges": design_edges,
                },
                sort_keys=True,
            )
        )

    result = {
        "schema": "janus.physarius.activation_circuit_vascular_validation.v1",
        "status": "STRUCTURAL_PASS" if strict_open else "FULL_VASCULARIZATION_PASS",
        "strict_complete": not strict_open,
        "nodes": len(nodes),
        "edges": len(edges),
        "live_edges": live_edges,
        "unresolved_nodes": unresolved,
        "migration_edges": migration_edges,
        "blocked_edges": blocked_edges,
        "design_edges": design_edges,
        "laws_verified": sorted(required_laws),
        "terminal": "OPEN_VASCULARIZATION" if strict_open else "ALL_DECLARED_CROSS_REPO_EDGES_VASCULARIZED",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
