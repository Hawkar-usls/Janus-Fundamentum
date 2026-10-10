#!/usr/bin/env python3
"""Exact finite clustering-width checker for frozen R50G25X residuals.

Public theory:
  Nishimura, Ragde, Szeider, Solving #SAT Using Vertex Covers.
  clustering-width clu(F) = minimum vertex-cover size of the obstruction graph G_F.

This tool:
  1. constructs G_F exactly from overlap and clash obstructions;
  2. computes an exact maximum independent set as a maximum clique in complement(G_F)
     using NetworkX's exact branch-and-bound max_weight_clique;
  3. returns clu(F) = |V(G_F)| - alpha(G_F);
  4. replays the resulting vertex cover and independent set.

Authority:
  FINITE_EXACT_PARAMETER_DIAGNOSTIC_ONLY.
No asymptotic claim follows from the fifteen frozen values.
"""
from __future__ import annotations
import json
import sys
import networkx as nx


def canon_formula(clauses):
    out = []
    for clause in clauses:
        s = set(int(x) for x in clause)
        if any(-x in s for x in s):
            continue
        out.append(frozenset(s))
    # Formula is a set of clauses.
    return list(dict.fromkeys(out))


def clauses_clash(c1, c2):
    return any(-lit in c2 for lit in c1)


def obstruction_graph(clauses):
    F = canon_formula(clauses)
    variables = sorted({abs(lit) for c in F for lit in c})
    edges = set()

    # Literal-pair co-occurrence index.  A clash obstruction with end clauses
    # C1,C3 and middle clause C2 exists for literals a in C1\C3 and b in C3\C1
    # exactly when C1,C3 do not clash and some C2 contains -a and -b.
    co_occurs = set()
    for c in F:
        ls = list(c)
        for i in range(len(ls)):
            for j in range(i + 1, len(ls)):
                co_occurs.add(frozenset((ls[i], ls[j])))

    m = len(F)
    for i in range(m):
        c1 = F[i]
        for j in range(i + 1, m):
            c3 = F[j]

            if clauses_clash(c1, c3):
                continue

            # Overlap obstruction:
            # deletion pair {var(C1 cap C3), var(C1 delta C3)}.
            inter = c1 & c3
            if inter:
                sym = c1 ^ c3
                X = {abs(l) for l in inter}
                Y = {abs(l) for l in sym}
                for x in X:
                    for y in Y:
                        if x != y:
                            edges.add(tuple(sorted((x, y))))

            # Clash obstruction:
            # deletion pair
            # { var((C1\C3) cap complement(C2)),
            #   var((C3\C1) cap complement(C2)) }.
            #
            # We can detect all resulting graph edges without enumerating C2:
            # x-y is contributed iff there are literals a,b of variables x,y
            # unique to the two end clauses and some clause contains -a,-b.
            left = c1 - c3
            right = c3 - c1
            for a in left:
                for b in right:
                    if abs(a) == abs(b):
                        continue
                    if frozenset((-a, -b)) in co_occurs:
                        edges.add(tuple(sorted((abs(a), abs(b)))))

    G = nx.Graph()
    G.add_nodes_from(variables)
    G.add_edges_from(edges)
    return G


def exact_clustering_width(G):
    # Independent sets of G are cliques of complement(G).
    H = nx.complement(G)
    max_independent, _ = nx.algorithms.clique.max_weight_clique(H, weight=None)
    independent = set(max_independent)
    cover = set(G.nodes()) - independent

    # Independent replay.
    assert all(not G.has_edge(u, v)
               for i, u in enumerate(independent)
               for v in list(independent)[i + 1:])
    assert all(u in cover or v in cover for u, v in G.edges())

    return len(cover), sorted(cover), sorted(independent)


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: checker.py R50G25X_ARTIFACT.json")

    data = json.load(open(sys.argv[1], encoding="utf-8"))
    rows = []
    for index, row in enumerate(data["residuals"]):
        G = obstruction_graph(row["residual_formula"])
        k, cover, independent = exact_clustering_width(G)
        rows.append({
            "index": index,
            "family": row["family"],
            "hash": row["residual_hash"],
            "CLV": row["residual_CLV"],
            "obstruction_graph_vertices": G.number_of_nodes(),
            "obstruction_graph_edges": G.number_of_edges(),
            "clustering_width_exact": k,
            "maximum_independent_set_size": len(independent),
            "vertex_cover": cover,
            "maximum_independent_set": independent,
            "replay": {
                "cover_hits_every_edge": True,
                "independent_set_has_no_edges": True
            }
        })

    print(json.dumps({
        "schema": "janus.trump.r50g25x.clustering_width_exact.v1",
        "authority": "FINITE_EXACT_PARAMETER_DIAGNOSTIC__NO_ASYMPTOTIC_CLAIM",
        "public_identity": "clu(F)=minimum vertex-cover size of the Nishimura-Ragde-Szeider obstruction graph",
        "rows": rows,
        "summary": {
            "minimum": min(r["clustering_width_exact"] for r in rows),
            "maximum": max(r["clustering_width_exact"] for r in rows)
        },
        "claim_ceiling": {
            "bounded_clustering_width_family": "NOT_ESTABLISHED",
            "O_log_n_clustering_width_family": "NOT_ESTABLISHED",
            "general_sat_in_p": "NOT_PROVED",
            "p_vs_np": "OPEN"
        }
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
