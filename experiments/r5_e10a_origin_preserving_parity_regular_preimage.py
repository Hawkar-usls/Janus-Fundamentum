#!/usr/bin/env python3
"""Finite exact controls for the E10A origin-preserving k_tau=m counterfamily.

The theorem is in the companion research note.  This checker only enumerates
small unit-weight GF(2)^2 base instances and verifies the exact label costs,
origin lift, fragment crossing count, and transformed scalar optimum.
"""

from __future__ import annotations

from collections import defaultdict
import heapq
import itertools
import json
import math


def make_instance(m: int):
    assert m >= 2
    L = 4 * m + 5
    edges = []

    def add(u, v, alpha=0, beta=0):
        edges.append((u, v, alpha, beta))

    # Cheap 00 path.
    add("s", "v")
    add("v", "w")
    add("w", "t")

    # Long 01 target path Q_m of length 2m.
    add("s", "x1", 0, 1)
    for i in range(1, m):
        add(f"x{i}", f"y{i}")
        add(f"y{i}", f"x{i+1}")
    add(f"x{m}", "t")

    # Cheap alpha=1 controls, making 01 the unique strict maximum.
    add("s", "p10", 1, 0)
    add("p10", "t", 0, 0)
    add("s", "p11", 1, 1)
    add("p11", "t", 0, 0)

    # For each x_i, two long w--x_i connector paths:
    # A has total alpha 0, B has total alpha 1.  All beta labels are 0.
    connector_names = set()
    for i in range(1, m + 1):
        for kind, flip in (("A", 0), ("B", 1)):
            prev = "w"
            for j in range(1, L):
                z = f"z{i}{kind}{j}"
                connector_names.add(z)
                add(prev, z, 0, 0)
                prev = z
            add(prev, f"x{i}", flip, 0)

    nodes = set()
    for u, v, _, _ in edges:
        nodes.add(u)
        nodes.add(v)

    return {
        "m": m,
        "connector_length": L,
        "edges": edges,
        "nodes": nodes,
        "connector_names": connector_names,
    }


def cover_adjacency(inst):
    adj = defaultdict(list)
    for u, v, alpha, beta in inst["edges"]:
        for sheet in (0, 1):
            a = (u, sheet)
            b = (v, sheet ^ alpha)
            adj[a].append((b, beta))
            adj[b].append((a, beta))
    return adj


def fragment_nodes(inst):
    # Split-space V_tau.  The base arc is i_(w,0): (w,0)^- -> (w,0)^+.
    # Its mate i_(w,1) is the anti-base.  Remove the outside endpoints
    # (w,0)^- and (w,1)^+ and include all split copies of connector/x nodes.
    names = {"w"} | {f"x{i}" for i in range(1, inst["m"] + 1)}
    names |= set(inst["connector_names"])
    out = set()
    for name in names:
        if name == "w":
            out.add((("w", 0), "+"))
            out.add((("w", 1), "-"))
        else:
            for sheet in (0, 1):
                out.add(((name, sheet), "-"))
                out.add(((name, sheet), "+"))
    return out


def split_fragment_chi(path, vtau):
    # Lift a cover path through Rudolph vertex splitting and the fresh
    # endpoint gadget.  Gadget arcs have zero characteristic value.
    arcs = [("gadget", ("a", None), (path[0], "-"))]
    for i, u in enumerate(path):
        arcs.append(("internal", (u, "-"), (u, "+")))
        if i + 1 < len(path):
            arcs.append(("transfer", (u, "+"), (path[i + 1], "-")))
    arcs.append(("gadget", (path[-1], "+"), ("abar", None)))

    chi = 0
    for kind, tail, head in arcs:
        if kind == "internal" and tail[0] == ("w", 0):
            chi += 1  # base
        elif kind == "internal" and tail[0] == ("w", 1):
            chi += 1  # anti-base
        elif (tail in vtau) != (head in vtau):
            chi -= 1  # every other boundary arc
    return chi


def enumerate_regular_cover_paths(inst):
    # A regular cover path never uses both sheets of one original base vertex.
    adj = cover_adjacency(inst)
    vtau = fragment_nodes(inst)
    best = {(a, b): math.inf for a in (0, 1) for b in (0, 1)}
    t0_records = []

    def dfs(u, used_base_vertices, used_cover_vertices, beta, path):
        if u[0] == "t":
            key = (u[1], beta)
            cost = len(path) - 1
            best[key] = min(best[key], cost)
            if u == ("t", 0):
                t0_records.append(
                    {
                        "cost": cost,
                        "beta": beta,
                        "chi": split_fragment_chi(path, vtau),
                    }
                )
            return

        for nxt, edge_beta in adj[u]:
            if nxt in used_cover_vertices:
                continue
            if nxt[0] in used_base_vertices:
                continue
            dfs(
                nxt,
                used_base_vertices | {nxt[0]},
                used_cover_vertices | {nxt},
                beta ^ edge_beta,
                path + [nxt],
            )

    start = ("s", 0)
    dfs(start, {"s"}, {start}, 0, [start])
    return best, t0_records



def transformed_split_shortest(inst, epsilon):
    """Ordinary (not regularity-filtered) shortest a--abar path after one fragment transform."""
    vtau = fragment_nodes(inst)
    adj = defaultdict(list)

    cover_nodes = [(name, sheet) for name in inst["nodes"] for sheet in (0, 1)]

    # Split internal arcs.  The two w internal arcs are base/anti-base (+1).
    for u in cover_nodes:
        tail = (u, "-")
        head = (u, "+")
        if u in (("w", 0), ("w", 1)):
            chi = 1
        else:
            chi = -1 if ((tail in vtau) != (head in vtau)) else 0
        adj[tail].append((head, epsilon * chi))

    # Every undirected base edge gives both directed cover orientations.
    for u, v, alpha, _beta in inst["edges"]:
        for sheet in (0, 1):
            cu = (u, sheet)
            cv = (v, sheet ^ alpha)
            for x, y in ((cu, cv), (cv, cu)):
                tail = (x, "+")
                head = (y, "-")
                chi = -1 if ((tail in vtau) != (head in vtau)) else 0
                adj[tail].append((head, 1 + epsilon * chi))

    a = ("endpoint_a", None)
    abar = ("endpoint_abar", None)
    for tail, head in (
        (a, (("s", 0), "-")),
        ((("s", 1), "+"), abar),
        ((("t", 0), "+"), abar),
        (a, (("t", 1), "-")),
    ):
        adj[tail].append((head, 0.0))

    dist = {a: 0.0}
    counter = itertools.count()
    pq = [(0.0, next(counter), a)]
    while pq:
        d, _, u = heapq.heappop(pq)
        if abs(d - dist[u]) > 1e-12:
            continue
        if u == abar:
            return d
        for v, w in adj[u]:
            nd = d + w
            if nd < dist.get(v, math.inf) - 1e-12:
                dist[v] = nd
                heapq.heappush(pq, (nd, next(counter), v))
    return math.inf


def target_path(m):
    p = [("s", 0), ("x1", 0)]
    for i in range(1, m):
        p.extend([(f"y{i}", 0), (f"x{i+1}", 0)])
    p.append(("t", 0))
    return p


def check_m(m):
    inst = make_instance(m)
    best, records = enumerate_regular_cover_paths(inst)
    expected = {(0, 0): 3, (0, 1): 2 * m, (1, 0): 2, (1, 1): 2}
    assert best == expected, (m, best)

    vtau = fragment_nodes(inst)
    q = target_path(m)
    chi = split_fragment_chi(q, vtau)
    assert chi == -2 * m
    k_tau = -chi // 2
    assert k_tau == m

    epsilon = 1 - 3 / (2 * m)
    assert epsilon > 0
    transformed_min = min(r["cost"] + epsilon * r["chi"] for r in records)
    assert abs(transformed_min - 3.0) < 1e-12
    ordinary_transformed_min = transformed_split_shortest(inst, epsilon)
    assert abs(ordinary_transformed_min - 3.0) < 1e-12
    assert abs((2 * m) + epsilon * (-2 * m) - 3.0) < 1e-12

    return {
        "m": m,
        "connector_length": inst["connector_length"],
        "exact_label_costs": {
            "00": best[(0, 0)],
            "01": best[(0, 1)],
            "10": best[(1, 0)],
            "11": best[(1, 1)],
        },
        "target": "01",
        "target_unique_strict_maximum": True,
        "target_fragment_chi": chi,
        "k_tau": k_tau,
        "epsilon_tau": epsilon,
        "transformed_regular_optimum": transformed_min,
        "transformed_ordinary_optimum": ordinary_transformed_min,
        "finite_cover_paths_to_t0_checked": len(records),
    }


def main():
    controls = [check_m(m) for m in range(2, 6)]
    print(
        json.dumps(
            {
                "status": "PASS_FINITE_ORIGIN_PREIMAGE_CONTROLS",
                "base_class": "UNDIRECTED_UNIT_WEIGHT_GF2_SQUARED",
                "bridge": "ALPHA_DOUBLE_COVER_PLUS_VERTEX_SPLIT_ENDPOINT_GADGET",
                "controls": controls,
                "theorem_family": "k_tau=m_FOR_ARBITRARY_m_GE_2",
                "claim_ceiling": (
                    "FINITE_CHECKER_ONLY__GENERAL_FAMILY_PROVED_IN_COMPANION_NOTE__"
                    "NO_DETERMINISTIC_SOLVER_CLAIM"
                ),
                "boundary": {
                    "D1": "EMPTY",
                    "P_VS_NP": "OPEN",
                    "P_EQ_NP": "NOT_PROVED",
                },
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
