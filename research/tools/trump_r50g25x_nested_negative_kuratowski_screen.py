#!/usr/bin/env python3
"""Exact finite nested-CNF negative screen for frozen R50G25X residuals.

Public characterization:
  F is nested iff inc+u(F) is planar,
where inc+u(F) is the incidence graph after adding one universal clause
adjacent to every variable.

For a negative result we:
  1) build inc+u(F),
  2) obtain a Kuratowski counterexample from a deterministic planarity test,
  3) verify every witness edge belongs to inc+u(F),
  4) suppress degree-2 subdivision vertices,
  5) require the reduced core to be exactly K5 or K3,3.

Thus each NOT_NESTED row contains a small Boolean graph witness rather than
only a library verdict.
"""
from __future__ import annotations
import json, sys
import networkx as nx


def node_key(node):
    kind, value = node
    return [kind, value]


def build_augmented_incidence(clauses):
    G = nx.Graph()
    variables = sorted({abs(l) for c in clauses for l in c})
    for v in variables:
        G.add_node(("v", v))
    for ci, clause in enumerate(clauses):
        c = ("c", ci)
        G.add_node(c)
        for lit in clause:
            G.add_edge(("v", abs(lit)), c)
    u = ("c", "UNIVERSAL")
    G.add_node(u)
    for v in variables:
        G.add_edge(("v", v), u)
    return G


def suppress_to_kuratowski_core(H):
    C = H.copy()
    changed = True
    while changed:
        changed = False
        for v in list(C.nodes()):
            if C.degree(v) == 2:
                a, b = list(C.neighbors(v))
                C.remove_node(v)
                if a != b:
                    C.add_edge(a, b)
                changed = True
                break
    n, m = C.number_of_nodes(), C.number_of_edges()
    degrees = sorted(dict(C.degree()).values())
    if n == 5 and m == 10 and degrees == [4] * 5:
        return "K5", C
    if n == 6 and m == 9 and degrees == [3] * 6 and nx.is_bipartite(C):
        return "K3,3", C
    raise AssertionError(("NOT_KURATOWSKI_CORE", n, m, degrees))


def screen(clauses):
    G = build_augmented_incidence(clauses)
    planar, witness = nx.check_planarity(G, counterexample=True)
    if planar:
        return {"nested": True}

    # Witness must literally be a subgraph of inc+u(F).
    for a, b in witness.edges():
        if not G.has_edge(a, b):
            raise AssertionError(("WITNESS_EDGE_NOT_IN_AUGMENTED_INCIDENCE", a, b))

    core_type, core = suppress_to_kuratowski_core(witness)
    return {
        "nested": False,
        "certificate_type": "KURATOWSKI_SUBDIVISION",
        "kuratowski_core": core_type,
        "witness_nodes": [node_key(x) for x in sorted(witness.nodes(), key=repr)],
        "witness_edges": [
            [node_key(a), node_key(b)]
            for a, b in sorted(witness.edges(), key=lambda e: (repr(e[0]), repr(e[1])))
        ],
        "witness_node_count": witness.number_of_nodes(),
        "witness_edge_count": witness.number_of_edges(),
        "reduced_core_nodes": [node_key(x) for x in sorted(core.nodes(), key=repr)],
        "reduced_core_edges": [
            [node_key(a), node_key(b)]
            for a, b in sorted(core.edges(), key=lambda e: (repr(e[0]), repr(e[1])))
        ],
    }


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: nested_screen.py R50G25X_ARTIFACT.json")
    data = json.load(open(sys.argv[1], encoding="utf-8"))
    rows = []
    for index, row in enumerate(data["residuals"]):
        result = screen(row["residual_formula"])
        result.update({
            "index": index,
            "family": row["family"],
            "hash": row["residual_hash"],
            "CLV": row["residual_CLV"],
            "max_clause_width": max(map(len, row["residual_formula"])),
        })
        rows.append(result)

    out = {
        "schema": "janus.trump.r50g25x.nested_negative_screen.v1",
        "authority": "FINITE_EXACT_COMBINATORIAL_NEGATIVE_SCREEN",
        "characterization": "F nested iff augmented incidence graph inc+u(F) is planar",
        "rows": rows,
        "all_fifteen_not_nested": all(not r["nested"] for r in rows),
        "claim_ceiling": {
            "strong_nested_backdoor": "UNTESTED",
            "general_sat_in_p": "NOT_PROVED",
            "p_vs_np": "OPEN",
        },
    }
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
