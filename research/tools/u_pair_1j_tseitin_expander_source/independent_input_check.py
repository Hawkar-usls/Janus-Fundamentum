#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from fractions import Fraction
from itertools import product
from pathlib import Path

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


def exact_edge_expansion(n, edges):
    best = None
    for mask in range(1, 1 << n):
        size = mask.bit_count()
        if size > n // 2:
            continue
        if n % 2 == 0 and size == n // 2 and not (mask & 1):
            continue
        cut = sum((((mask >> a) & 1) ^ ((mask >> b) & 1)) for a, b in edges)
        ratio = Fraction(cut, size)
        if best is None or ratio < best:
            best = ratio
    return best


def rebuild_cnf(n, edges):
    edge_var = {edge: idx + 1 for idx, edge in enumerate(edges)}
    boundary = tuple(range(1, len(edges) + 1))
    internal = tuple(range(len(edges) + 1, len(edges) + n + 1))
    charges = [1] + [0] * (n - 1)
    clauses = [tuple(internal)]
    for v in range(n):
        incident = [edge for edge in edges if v in edge]
        assert len(incident) == 3
        vars_ = [edge_var[e] for e in incident]
        selector = internal[v]
        for bits in product((0, 1), repeat=3):
            if sum(bits) % 2 != charges[v]:
                continue
            clause = [-selector]
            clause += [var if bit == 0 else -var for var, bit in zip(vars_, bits)]
            clauses.append(tuple(clause))
    return boundary, internal, canonical_cnf(clauses)


def check(graph, rel):
    n = int(graph["n"])
    edges = tuple(sorted(tuple(sorted(map(int, e))) for e in graph["edges"]))
    assert len(edges) == 3 * n // 2
    assert len(set(edges)) == len(edges)
    assert all(a != b for a, b in edges)

    deg = [0] * n
    adj = [[] for _ in range(n)]
    for a, b in edges:
        assert 0 <= a < n and 0 <= b < n
        deg[a] += 1
        deg[b] += 1
        adj[a].append(b)
        adj[b].append(a)
    assert all(d == 3 for d in deg)

    reached = {0}
    stack = [0]
    while stack:
        v = stack.pop()
        for u in adj[v]:
            if u not in reached:
                reached.add(u)
                stack.append(u)
    assert len(reached) == n

    h = exact_edge_expansion(n, edges)
    assert h >= Fraction(1, 2)
    recorded = graph["edge_expansion_exact"]
    assert Fraction(int(recorded["numerator"]), int(recorded["denominator"])) == h
    assert graph["charge_vector"] == [1] + [0] * (n - 1)

    boundary, internal, clauses = rebuild_cnf(n, edges)
    assert rel["schema"] == SCHEMA
    assert tuple(map(int, rel["boundary_variables"])) == boundary
    assert tuple(map(int, rel["internal_variables"])) == internal
    assert canonical_cnf(rel["clauses"]) == clauses

    source_payload = {
        "schema": SCHEMA,
        "boundary_variables": list(boundary),
        "internal_variables": list(internal),
        "clauses": [list(c) for c in clauses],
    }
    source_digest = hashlib.sha256(canonical_bytes(source_payload)).hexdigest()
    assert rel["source_digest_sha256"] == source_digest

    expected_order = sorted(
        boundary,
        key=lambda var: (
            hashlib.sha256(f"{ORDER_SALT}|{source_digest}|{var}".encode()).digest(),
            var,
        ),
    )
    assert list(map(int, rel["boundary_order"])) == expected_order

    final_payload = {
        "schema": SCHEMA,
        "boundary_variables": list(boundary),
        "internal_variables": list(internal),
        "boundary_order": expected_order,
        "clauses": [list(c) for c in clauses],
    }
    input_digest = hashlib.sha256(canonical_bytes(final_payload)).hexdigest()
    assert rel["input_digest_sha256"] == input_digest

    return {
        "n": n,
        "edge_expansion": f"{h.numerator}/{h.denominator}",
        "boundary_count": len(boundary),
        "internal_count": len(internal),
        "clause_count": len(clauses),
        "input_digest_sha256": input_digest,
        "verdict": "PASS_INDEPENDENT_SOURCE_INPUT_CHECK",
    }


def main(graph_path, rel_path, out_path):
    graph = json.loads(Path(graph_path).read_text())
    rel = json.loads(Path(rel_path).read_text())
    result = check(graph, rel)
    Path(out_path).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit("usage: independent_input_check.py GRAPH.json RELATION.json OUT.json")
    main(sys.argv[1], sys.argv[2], sys.argv[3])
