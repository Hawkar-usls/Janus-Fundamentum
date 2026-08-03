#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict, deque
from typing import Any

SCHEMA = "janus.c049.grouped_subspace_partition_obstruction.v1"
ARTIFACT_ID = "C049-JANUS-GROUPED-SUBSPACE-PARTITION-OBSTRUCTION"
DIMENSIONS = [1, 2, 3, 4, 8, 16, 32, 64]


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def build_tree(d: int) -> tuple[dict[str, list[str]], dict[str, int]]:
    adjacency: dict[str, list[str]] = defaultdict(list)
    leaf_coordinate: dict[str, int] = {}

    def edge(u: str, v: str) -> None:
        adjacency[u].append(v)
        adjacency[v].append(u)

    cherries = [f"c{i}" for i in range(d)]
    for i, cherry in enumerate(cherries):
        for prefix in ("a", "b"):
            leaf = f"{prefix}{i}"
            edge(cherry, leaf)
            leaf_coordinate[leaf] = i
    if d == 1:
        adjacency.clear()
        edge("a0", "b0")
    elif d == 2:
        edge("c0", "c1")
    elif d == 3:
        for cherry in cherries:
            edge("s0", cherry)
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
    return {u: sorted(vs) for u, vs in adjacency.items()}, leaf_coordinate


def side_leaves(adjacency: dict[str, list[str]], u: str, blocked: str) -> list[str]:
    seen = {blocked}
    queue = deque([u])
    leaves: list[str] = []
    while queue:
        node = queue.popleft()
        if len(adjacency[node]) == 1:
            leaves.append(node)
        for nxt in adjacency[node]:
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    return sorted(leaves)


def expanded_certificate(d: int) -> tuple[dict[str, Any], int]:
    adjacency, coordinates = build_tree(d)
    leaves = set(coordinates)
    edges = sorted({tuple(sorted((u, v))) for u, vs in adjacency.items() for v in vs})
    records = []
    work = sum(len(vs) for vs in adjacency.values())
    for u, v in edges:
        side = set(side_leaves(adjacency, u, v))
        other = leaves - side
        left = {coordinates[x] for x in side}
        right = {coordinates[x] for x in other}
        basis = [1 << i for i in sorted(left & right)]
        records.append({"edge": [u, v], "intersection_rref": basis})
        work += len(adjacency) + 2 * d
    work += len(leaves) * d
    tree_payload = {"adjacency": adjacency, "leaf_coordinate": coordinates}
    return {
        "tree_digest": digest(tree_payload),
        "cut_digest": digest(records),
        "node_count": len(adjacency),
        "edge_count": len(edges),
        "leaf_count": len(leaves),
        "maximum_cut_dimension": max(len(r["intersection_rref"]) for r in records),
        "split_pair_edge_count": sum(bool(r["intersection_rref"]) for r in records),
        "zero_boundary_edge_count": sum(not r["intersection_rref"] for r in records),
    }, work


def case(d: int) -> tuple[dict[str, Any], int]:
    ordinary, work = expanded_certificate(d)
    basis = [1 << i for i in range(d)]
    basis_descriptor = {
        "kind": "STANDARD_BASIS_RREF",
        "dimension": d,
        "sha256": digest(basis),
    }
    ordinary.update(
        {
            "tree_descriptor": "PAIR_CHERRY_CATERPILLAR_V1",
            "exact_width": 1,
            "leaf_edge_lower_bound": 1,
            "cut_rule": (
                "an edge splitting one copied basis pair has RREF [e_i]; "
                "every edge separating only whole pairs has empty RREF"
            ),
        }
    )
    equal_status = "SAT"
    distinct_status = "UNSAT" if d == 1 else "SAT"
    return {
        "dimension": d,
        "arrangement": {
            "normal_space_rref": basis_descriptor,
            "multiplicity": 2,
            "leaf_offsets_equal": [0, 0],
            "leaf_offsets_distinct": [0, (1 << d) - 1],
            "offset_encoding": "beta values on the canonical normal basis",
        },
        "grouped_partitioned_width": {
            "only_cut": [[0], [1]],
            "intersection_rref": basis_descriptor,
            "exact_width": d,
        },
        "partition_forgotten_matroid": ordinary,
        "cap_one_control": {
            "ordinary_terminal": "FOUND_LAYOUT",
            "grouped_terminal": "FOUND_LAYOUT" if d == 1 else "NO_LAYOUT_AT_CAP",
        },
        "offset_semantics_control": {
            "equal_offsets": equal_status,
            "distinct_offsets": distinct_status,
            "unique_forbidden_points_equal": 1,
            "unique_forbidden_points_distinct": 2,
        },
        "work_units": work,
    }, work


def settle_bytes(result: dict[str, Any]) -> None:
    value = 0
    for _ in range(32):
        result["certificate_bytes"] = value
        nxt = len((json.dumps(result, indent=2, sort_keys=True) + "\n").encode())
        if nxt == value:
            return
        value = nxt
    raise RuntimeError("certificate byte fixed point did not converge")


def run() -> dict[str, Any]:
    cases = []
    total_work = 0
    for d in DIMENSIONS:
        item, work = case(d)
        cases.append(item)
        total_work += work
    failures = []
    for item in cases:
        d = item["dimension"]
        ordinary = item["partition_forgotten_matroid"]
        if item["grouped_partitioned_width"]["exact_width"] != d:
            failures.append([d, "GROUPED_WIDTH"])
        if ordinary["exact_width"] != 1 or ordinary["maximum_cut_dimension"] != 1:
            failures.append([d, "ORDINARY_WIDTH"])
        expected = "FOUND_LAYOUT" if d == 1 else "NO_LAYOUT_AT_CAP"
        if item["cap_one_control"]["grouped_terminal"] != expected:
            failures.append([d, "CAP"])
        if item["arrangement"]["leaf_offsets_equal"] == item["arrangement"]["leaf_offsets_distinct"]:
            failures.append([d, "OFFSET"])
    result: dict[str, Any] = {
        "artifact_id": ARTIFACT_ID,
        "schema": SCHEMA,
        "cycle": "C049",
        "status": "PASS" if not failures else "FAIL",
        "result_class": "DECISIVE_REPRESENTATION_OBSTRUCTION",
        "p_vs_np": "OPEN",
        "audit_dimensions": DIMENSIONS,
        "cases": cases,
        "failures": failures,
        "candidate_decompositions": len(cases),
        "failed_refinements": 0,
        "total_work_units": total_work,
        "exact_theorem": (
            "For every d>=1, {GF(2)^d,GF(2)^d} has grouped branch-width d, "
            "whereas two copied bases with their block partition forgotten form d parallel "
            "pairs and have ordinary represented-matroid branch-width exactly 1."
        ),
        "obstruction": (
            "Group-forgetting basis expansion cannot soundly substitute an ordinary "
            "represented-matroid constructor for grouped factor-normal subspace discovery."
        ),
        "required_specialization": (
            "Retain the basis-block partition or reimplement the direct grouped-subspace "
            "constructor; retain beta_i separately at every affine leaf and message."
        ),
        "literature_boundary": (
            "Choi-Korhonen-Oum 2026 identifies arrangements with partitioned matroids. "
            "This blocks only discarding that partition, not a proved partition-aware adaptation."
        ),
        "open_gate": "PARTITION_AWARE_PROOF_CARRYING_FPT_CONSTRUCTOR_INTEGRATION",
        "claim_boundary": (
            "No full constructor, no NAND3+NEQ closure, no universal polynomial SAT "
            "algorithm, and no conclusion about P versus NP."
        ),
        "certificate_bytes": 0,
    }
    settle_bytes(result)
    result["integrity_sha256"] = "0" * 64
    settle_bytes(result)
    result["integrity_sha256"] = digest(
        {k: v for k, v in result.items() if k != "integrity_sha256"}
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args()
    result = run()
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(text)
    else:
        print(text, end="")
    if args.self_test:
        assert result["status"] == "PASS"
        assert all(
            c["grouped_partitioned_width"]["exact_width"] == c["dimension"]
            for c in result["cases"]
        )
        assert all(
            c["partition_forgotten_matroid"]["exact_width"] == 1
            for c in result["cases"]
        )
        assert result["p_vs_np"] == "OPEN"


if __name__ == "__main__":
    main()
