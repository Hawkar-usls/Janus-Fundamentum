#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from fractions import Fraction
from itertools import product
from pathlib import Path

SERIES = (8, 10, 12, 14, 16)
GRAPH_SALT = "U_PAIR_1J_TSEITIN_EXPANDER_SEARCH_V1"
ORDER_SALT = "U_PAIR_1J_TSEITIN_BOUNDARY_ORDER_V1"
SCHEMA = "CNF_SKOL_SEARCH_RELATION_V1"


def canonical_bytes(obj):
    return (json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n").encode()


def canonical_cnf(clauses):
    out = set()
    for clause in clauses:
        lits = set(int(x) for x in clause)
        if any(-lit in lits for lit in lits):
            continue
        out.add(tuple(sorted(lits, key=lambda z: (abs(z), z < 0))))
    return tuple(sorted(out, key=lambda c: (len(c), c)))


def graph_from_nonce(n, nonce):
    stubs = [(v, k) for v in range(n) for k in range(3)]
    stubs.sort(
        key=lambda t: hashlib.sha256(
            f"{GRAPH_SALT}|{n}|{nonce}|{t[0]}|{t[1]}".encode()
        ).digest()
    )
    edges = []
    seen = set()
    for i in range(0, len(stubs), 2):
        a, b = stubs[i][0], stubs[i + 1][0]
        if a == b:
            return None
        edge = tuple(sorted((a, b)))
        if edge in seen:
            return None
        seen.add(edge)
        edges.append(edge)
    edges = tuple(sorted(edges))
    degree = [0] * n
    adjacency = [[] for _ in range(n)]
    for a, b in edges:
        degree[a] += 1
        degree[b] += 1
        adjacency[a].append(b)
        adjacency[b].append(a)
    if any(d != 3 for d in degree):
        return None
    reached = {0}
    stack = [0]
    while stack:
        v = stack.pop()
        for u in adjacency[v]:
            if u not in reached:
                reached.add(u)
                stack.append(u)
    if len(reached) != n:
        return None
    return edges


def exact_edge_expansion(n, edges):
    best = None
    best_mask = None
    for mask in range(1, 1 << n):
        size = mask.bit_count()
        if size > n // 2:
            continue
        if n % 2 == 0 and size == n // 2 and not (mask & 1):
            continue
        cut = 0
        for a, b in edges:
            cut += ((mask >> a) & 1) ^ ((mask >> b) & 1)
        ratio = Fraction(cut, size)
        if best is None or ratio < best:
            best = ratio
            best_mask = mask
    assert best is not None
    return best, best_mask


def first_expansion_screened_graph(n):
    nonce = 0
    while True:
        edges = graph_from_nonce(n, nonce)
        if edges is not None:
            h, mask = exact_edge_expansion(n, edges)
            if h >= Fraction(1, 2):
                return nonce, edges, h, mask
        nonce += 1


def build_relation(n, edges):
    edge_var = {edge: idx + 1 for idx, edge in enumerate(edges)}
    boundary = tuple(range(1, len(edges) + 1))
    internal = tuple(range(len(edges) + 1, len(edges) + n + 1))
    charges = [1] + [0] * (n - 1)
    clauses = [tuple(internal)]

    for v in range(n):
        incident_edges = [edge for edge in edges if v in edge]
        assert len(incident_edges) == 3
        incident_vars = [edge_var[e] for e in incident_edges]
        selector = internal[v]
        for bits in product((0, 1), repeat=3):
            if sum(bits) % 2 != charges[v]:
                continue
            block = [-selector]
            for var, bit in zip(incident_vars, bits):
                block.append(var if bit == 0 else -var)
            clauses.append(tuple(block))

    clauses = canonical_cnf(clauses)
    source_payload = {
        "schema": SCHEMA,
        "boundary_variables": list(boundary),
        "internal_variables": list(internal),
        "clauses": [list(c) for c in clauses],
    }
    source_digest = hashlib.sha256(canonical_bytes(source_payload)).hexdigest()
    boundary_order = sorted(
        boundary,
        key=lambda var: (
            hashlib.sha256(
                f"{ORDER_SALT}|{source_digest}|{var}".encode()
            ).digest(),
            var,
        ),
    )
    final_payload = {
        "schema": SCHEMA,
        "boundary_variables": list(boundary),
        "internal_variables": list(internal),
        "boundary_order": list(boundary_order),
        "clauses": [list(c) for c in clauses],
    }
    input_digest = hashlib.sha256(canonical_bytes(final_payload)).hexdigest()
    blind = dict(final_payload)
    blind["source_digest_sha256"] = source_digest
    blind["input_digest_sha256"] = input_digest
    return blind


def main(outdir):
    root = Path(outdir)
    graphs_dir = root / "source_graphs"
    blind_dir = root / "blind_inputs"
    graphs_dir.mkdir(parents=True, exist_ok=True)
    blind_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "artifact_id": "JANUS-U-PAIR-1J-TSEITIN-EXPANDER-SOURCE-FREEZE-v1",
        "series": [],
        "source_only_exhaustive_expansion_check": True,
        "blind_constructor_visibility": "BLIND_INPUT_FILES_ONLY",
    }

    for n in SERIES:
        nonce, edges, h, witness_mask = first_expansion_screened_graph(n)
        graph_obj = {
            "n": n,
            "degree": 3,
            "nonce": nonce,
            "edges": [list(e) for e in edges],
            "charge_vector": [1] + [0] * (n - 1),
            "edge_expansion_exact": {
                "numerator": h.numerator,
                "denominator": h.denominator,
                "minimum_subset_mask": witness_mask,
                "threshold_pass_ge_half": h >= Fraction(1, 2),
            },
        }
        blind = build_relation(n, edges)
        graph_path = graphs_dir / f"graph_n{n}.json"
        blind_path = blind_dir / f"relation_n{n}.json"
        graph_path.write_text(json.dumps(graph_obj, indent=2, sort_keys=True) + "\n")
        blind_path.write_text(json.dumps(blind, indent=2, sort_keys=True) + "\n")
        manifest["series"].append(
            {
                "n": n,
                "graph_path": str(graph_path),
                "blind_path": str(blind_path),
                "graph_sha256": hashlib.sha256(graph_path.read_bytes()).hexdigest(),
                "blind_sha256": hashlib.sha256(blind_path.read_bytes()).hexdigest(),
                "input_digest_sha256": blind["input_digest_sha256"],
                "boundary_count": len(blind["boundary_variables"]),
                "internal_count": len(blind["internal_variables"]),
                "clause_count": len(blind["clauses"]),
            }
        )

    (root / "source_freeze_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(manifest, sort_keys=True))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: source_builder.py OUTDIR")
    main(sys.argv[1])
