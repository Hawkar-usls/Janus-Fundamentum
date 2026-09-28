#!/usr/bin/env python3
from __future__ import annotations

from itertools import product
import json


def relation(nodes, edges, kinds):
    edges = [tuple(sorted(e)) for e in edges]
    inc = {v: [] for v in nodes}
    for ei, (u, v) in enumerate(edges):
        inc[u].append(ei)
        inc[v].append(ei)
    assert all(len(inc[v]) <= 3 for v in nodes)

    boundary = []
    b_by = {v: [] for v in nodes}
    for v in nodes:
        for _ in range(3 - len(inc[v])):
            b_by[v].append(len(boundary))
            boundary.append(v)

    total = len(edges) + len(boundary)
    by_boundary = {}
    for bits in product((0, 1), repeat=total):
        ebits = bits[: len(edges)]
        bbits = bits[len(edges) :]
        eq_state = {}
        ok = True
        for v in nodes:
            local = [ebits[i] for i in inc[v]] + [bbits[i] for i in b_by[v]]
            assert len(local) == 3
            if kinds[v] == "E":
                good = local[0] == local[1] == local[2]
                if good:
                    eq_state[v] = local[0]
            else:
                good = sum(local) == 1
            if not good:
                ok = False
                break
        if not ok:
            continue
        key = tuple(bbits)
        rec = (tuple(ebits), tuple(sorted(eq_state.items())))
        by_boundary.setdefault(key, []).append(rec)
    return boundary, by_boundary


def support(t):
    return frozenset(i for i, b in enumerate(t) if b)


def is_delta(rel):
    fam = {support(t) for t in rel}
    for x in fam:
        for y in fam:
            sym = x ^ y
            for e in sym:
                good = False
                for f in sym:
                    toggle = {e} if e == f else {e, f}
                    if x ^ toggle in fam:
                        good = True
                        break
                if not good:
                    return False
    return True


def verify_fixture(name, nodes, edges, kinds, expect_delta):
    boundary, table = relation(nodes, edges, kinds)
    assert table, name

    # AGMB-2: one internal extension per feasible boundary tuple.
    assert all(len(v) == 1 for v in table.values()), name

    items = [(b, recs[0]) for b, recs in table.items()]
    eq_nodes = [v for v in nodes if kinds[v] == "E"]

    # AGMB-1 finite replay: changing an EQ state costs >=3 boundary flips.
    for i in range(len(items)):
        b1, (_, s1t) = items[i]
        s1 = dict(s1t)
        for j in range(i):
            b2, (_, s2t) = items[j]
            s2 = dict(s2t)
            if any(s1[v] != s2[v] for v in eq_nodes):
                hd = sum(x != y for x, y in zip(b1, b2))
                assert hd >= 3, (name, b1, b2, hd)

    # Every EQ state occurs both ways on each EQ node (AGMB-3 replay).
    for v in eq_nodes:
        vals = {dict(recs[0][1])[v] for recs in table.values()}
        assert vals == {0, 1}, (name, v, vals)

    got_delta = is_delta(table.keys())
    assert got_delta == expect_delta, (name, got_delta, expect_delta)
    return {
        "name": name,
        "factors": len(nodes),
        "boundary_ports": len(boundary),
        "feasible_boundary_tuples": len(table),
        "eq_nodes": len(eq_nodes),
        "delta_matroid": got_delta,
    }


def path_fixture(n, first="E"):
    nodes = list(range(n))
    edges = [(i, i + 1) for i in range(n - 1)]
    kinds = {}
    for i in nodes:
        if (i % 2 == 0) == (first == "E"):
            kinds[i] = "E"
        else:
            kinds[i] = "X"
    return nodes, edges, kinds


def bipartite_kinds(nodes, edges, root_kind="E"):
    adj = {v: [] for v in nodes}
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    color = {nodes[0]: 0}
    stack = [nodes[0]]
    while stack:
        u = stack.pop()
        for v in adj[u]:
            if v not in color:
                color[v] = 1 - color[u]
                stack.append(v)
            else:
                assert color[v] != color[u]
    return {v: (root_kind if color[v] == 0 else ("X" if root_kind == "E" else "E")) for v in nodes}


def main():
    results = []

    # Exact positive control deliberately outside the theorem.
    results.append(verify_fixture("single_EXACT1", [0], [], {0: "X"}, True))
    results.append(verify_fixture("single_EQ3", [0], [], {0: "E"}, False))

    for n in range(2, 8):
        for first in ("E", "X"):
            nodes, edges, kinds = path_fixture(n, first)
            results.append(verify_fixture(f"path_{n}_{first}", nodes, edges, kinds, False))

    fixtures = {
        "star_center_X": ([0, 1, 2, 3], [(0, 1), (0, 2), (0, 3)], "X"),
        "star_center_E": ([0, 1, 2, 3], [(0, 1), (0, 2), (0, 3)], "E"),
        "binary7": ([0, 1, 2, 3, 4, 5, 6], [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6)], "E"),
        "fork8": ([0, 1, 2, 3, 4, 5, 6, 7], [(0, 1), (1, 2), (1, 3), (2, 4), (2, 5), (3, 6), (3, 7)], "E"),
    }
    for name, (nodes, edges, root_kind) in fixtures.items():
        kinds = bipartite_kinds(nodes, edges, root_kind)
        results.append(verify_fixture(name, nodes, edges, kinds, False))

    out = {
        "status": "PASS_ACYCLIC_GROUPED_MATCHING_DELTA_MATROID_BARRIER",
        "theorem_replay": {
            "boundary_extension_unique_on_all_fixtures": True,
            "eq_state_change_requires_boundary_hamming_at_least_3": True,
            "each_eq_node_realizes_both_states": True,
            "all_tree_fixtures_with_EQ3_fail_delta_matroid": True,
            "single_EXACT1_positive_control_is_delta_matroid": True,
        },
        "fixtures": results,
        "boundary": {
            "arbitrary_size_claim": "PROOF_IN_RESEARCH_ARTIFACT_NOT_FINITE_ENUMERATION",
            "ordinary_matching_tree_grouping": "BLOCKED",
            "cyclic_grouping": "OPEN",
            "universal_solver": "OPEN",
            "E8_D1": "EMPTY",
            "P_VS_NP": "OPEN",
        },
    }
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
