#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict, deque
from pathlib import Path
from typing import Any

SCHEMA = "janus.c049.grouped_subspace_partition_obstruction.v1"
ARTIFACT = "C049-JANUS-GROUPED-SUBSPACE-PARTITION-OBSTRUCTION"
DIMENSIONS = [1, 2, 3, 4, 8, 16, 32, 64]


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode()).hexdigest()


def build_tree(d: int) -> tuple[dict[str, list[str]], dict[str, int]]:
    graph: dict[str, list[str]] = defaultdict(list)
    coords: dict[str, int] = {}

    def edge(u: str, v: str) -> None:
        graph[u].append(v)
        graph[v].append(u)

    cherries = [f"c{i}" for i in range(d)]
    for i, c in enumerate(cherries):
        edge(c, f"a{i}")
        edge(c, f"b{i}")
        coords[f"a{i}"] = coords[f"b{i}"] = i
    if d == 1:
        graph.clear()
        edge("a0", "b0")
    elif d == 2:
        edge("c0", "c1")
    elif d == 3:
        for c in cherries:
            edge("s0", c)
    else:
        spine = [f"s{i}" for i in range(d - 2)]
        edge(spine[0], cherries[0])
        edge(spine[0], cherries[1])
        for j in range(1, d - 3):
            edge(spine[j - 1], spine[j])
            edge(spine[j], cherries[j + 1])
        edge(spine[-2], spine[-1])
        edge(spine[-1], cherries[-2])
        edge(spine[-1], cherries[-1])
    return {u: sorted(vs) for u, vs in graph.items()}, coords


def side_leaves(graph: dict[str, list[str]], u: str, blocked: str) -> set[str]:
    seen = {blocked}
    queue = deque([u])
    leaves = set()
    while queue:
        x = queue.popleft()
        if len(graph[x]) == 1:
            leaves.add(x)
        for y in graph[x]:
            if y not in seen:
                seen.add(y)
                queue.append(y)
    return leaves


def replay(d: int) -> tuple[dict[str, Any], int]:
    graph, coords = build_tree(d)
    nodes = set(graph)
    leaves = set(coords)
    assert all(
        (u in leaves and len(vs) == 1) or (u not in leaves and len(vs) == 3)
        for u, vs in graph.items()
    )
    edges = sorted({tuple(sorted((u, v))) for u, vs in graph.items() for v in vs})
    assert len(edges) == len(nodes) - 1
    reached = set()
    queue = deque([next(iter(nodes))])
    while queue:
        x = queue.popleft()
        if x in reached:
            continue
        reached.add(x)
        queue.extend(graph[x])
    assert reached == nodes
    records = []
    work = sum(len(vs) for vs in graph.values())
    for u, v in edges:
        side = side_leaves(graph, u, v)
        other = leaves - side
        left = {coords[x] for x in side}
        right = {coords[x] for x in other}
        records.append(
            {
                "edge": [u, v],
                "intersection_rref": [1 << i for i in sorted(left & right)],
            }
        )
        work += len(graph) + 2 * d
    work += len(leaves) * d
    tree_payload = {"adjacency": graph, "leaf_coordinate": coords}
    return {
        "tree_digest": digest(tree_payload),
        "cut_digest": digest(records),
        "node_count": len(graph),
        "edge_count": len(edges),
        "leaf_count": len(leaves),
        "maximum_cut_dimension": max(len(r["intersection_rref"]) for r in records),
        "split_pair_edge_count": sum(bool(r["intersection_rref"]) for r in records),
        "zero_boundary_edge_count": sum(not r["intersection_rref"] for r in records),
    }, work


def verify(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    data = json.loads(raw)
    assert data["artifact_id"] == ARTIFACT and data["schema"] == SCHEMA
    assert data["cycle"] == "C049" and data["status"] == "PASS"
    assert data["result_class"] == "DECISIVE_REPRESENTATION_OBSTRUCTION"
    assert data["p_vs_np"] == "OPEN" and data["audit_dimensions"] == DIMENSIONS
    assert data["certificate_bytes"] == len(raw)
    assert data["integrity_sha256"] == digest(
        {k: v for k, v in data.items() if k != "integrity_sha256"}
    )
    assert data["failures"] == [] and len(data["cases"]) == len(DIMENSIONS)
    total_work = 0
    for d, item in zip(DIMENSIONS, data["cases"]):
        assert item["dimension"] == d
        basis = [1 << i for i in range(d)]
        basis_descriptor = {
            "kind": "STANDARD_BASIS_RREF",
            "dimension": d,
            "sha256": digest(basis),
        }
        arrangement = item["arrangement"]
        assert arrangement["normal_space_rref"] == basis_descriptor
        assert arrangement["multiplicity"] == 2
        assert arrangement["leaf_offsets_equal"] == [0, 0]
        assert arrangement["leaf_offsets_distinct"] == [0, (1 << d) - 1]
        grouped = item["grouped_partitioned_width"]
        assert grouped["only_cut"] == [[0], [1]]
        assert grouped["intersection_rref"] == basis_descriptor
        assert grouped["exact_width"] == d
        replayed, work = replay(d)
        ordinary = item["partition_forgotten_matroid"]
        for key, value in replayed.items():
            assert ordinary[key] == value
        assert ordinary["tree_descriptor"] == "PAIR_CHERRY_CATERPILLAR_V1"
        assert ordinary["exact_width"] == ordinary["leaf_edge_lower_bound"] == 1
        assert item["work_units"] == work
        total_work += work
        assert item["cap_one_control"]["ordinary_terminal"] == "FOUND_LAYOUT"
        expected = "FOUND_LAYOUT" if d == 1 else "NO_LAYOUT_AT_CAP"
        assert item["cap_one_control"]["grouped_terminal"] == expected
        semantics = item["offset_semantics_control"]
        assert semantics["equal_offsets"] == "SAT"
        assert semantics["distinct_offsets"] == ("UNSAT" if d == 1 else "SAT")
        assert semantics["unique_forbidden_points_equal"] == 1
        assert semantics["unique_forbidden_points_distinct"] == 2
    assert data["total_work_units"] == total_work
    assert data["candidate_decompositions"] == len(DIMENSIONS)
    assert data["failed_refinements"] == 0
    assert data["open_gate"] == (
        "PARTITION_AWARE_PROOF_CARRYING_FPT_CONSTRUCTOR_INTEGRATION"
    )
    return {
        "status": "VERIFIED",
        "artifact_id": ARTIFACT,
        "cases": len(DIMENSIONS),
        "maximum_gap": max(DIMENSIONS),
        "certificate_bytes": len(raw),
        "p_vs_np": "OPEN",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    args = parser.parse_args()
    print(json.dumps(verify(Path(args.artifact)), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
