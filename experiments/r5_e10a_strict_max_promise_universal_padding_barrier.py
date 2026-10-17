#!/usr/bin/env python3
"""Exact controls for the GF(2)^2 strict-max promise padding barrier."""

from __future__ import annotations

import json
import random
from collections import defaultdict

SEED = 29102026
INF = 10**9


def add_edge(adj, edges, u, v, label, kind="base", original_edge=None):
    assert u != v
    eid = len(edges)
    edges.append({
        "u": u, "v": v, "label": label,
        "kind": kind, "original_edge": original_edge,
    })
    adj[u].append((v, eid))
    adj[v].append((u, eid))
    return eid


def enumerate_simple_paths(adj, edges, s, t):
    """Return (cost,label,vertices,edge_ids) for every simple s-t path."""
    out = []
    visited = {s}
    vpath = [s]
    epath = []

    def dfs(u, label):
        if u == t:
            out.append((len(epath), label, tuple(vpath), tuple(epath)))
            return
        for v, eid in adj[u]:
            if v in visited:
                continue
            visited.add(v)
            vpath.append(v)
            epath.append(eid)
            dfs(v, label ^ edges[eid]["label"])
            epath.pop()
            vpath.pop()
            visited.remove(v)

    dfs(s, 0)
    return out


def label_minima(paths):
    best = [INF] * 4
    witness = [None] * 4
    for cost, lab, verts, eids in paths:
        if cost < best[lab]:
            best[lab] = cost
            witness[lab] = (cost, lab, verts, eids)
    return best, witness


def build_random_graph(rng, n):
    s, t = 0, n - 1
    adj = defaultdict(list)
    edges = []

    # Begin with a random spanning tree so s,t are connected.
    for v in range(1, n):
        u = rng.randrange(v)
        add_edge(adj, edges, u, v, rng.randrange(4))

    # Add a few extra non-edges; keep graph simple.
    present = {frozenset((e["u"], e["v"])) for e in edges}
    candidates = [
        (u, v)
        for u in range(n)
        for v in range(u + 1, n)
        if frozenset((u, v)) not in present
    ]
    rng.shuffle(candidates)
    for u, v in candidates[: rng.randint(0, min(3, len(candidates)))]:
        add_edge(adj, edges, u, v, rng.randrange(4))

    return adj, edges, s, t


def pad_instance(adj, edges, s, t, target):
    """Apply the exact 4-stretch + three cheap wrong-label routes."""
    out_adj = defaultdict(list)
    out_edges = []
    next_vertex = max(adj.keys() | {s, t}) + 1

    # Replace each original edge by an internally disjoint four-edge path.
    # Put its label on the first segment and zero on the remaining three.
    for orig_id, e in enumerate(edges):
        u, v, lab = e["u"], e["v"], e["label"]
        a, b, c = next_vertex, next_vertex + 1, next_vertex + 2
        next_vertex += 3
        chain = [(u, a, lab), (a, b, 0), (b, c, 0), (c, v, 0)]
        for x, y, ell in chain:
            add_edge(
                out_adj, out_edges, x, y, ell,
                kind="core", original_edge=orig_id,
            )

    wrong = [g for g in range(4) if g != target]
    for length, lab in zip((1, 2, 3), wrong):
        prev = s
        for i in range(length):
            last = (i == length - 1)
            nxt = t if last else next_vertex
            if not last:
                next_vertex += 1
            add_edge(
                out_adj, out_edges, prev, nxt,
                lab if i == 0 else 0,
                kind="cheap", original_edge=None,
            )
            prev = nxt

    return out_adj, out_edges


def contract_core_witness(path, padded_edges, original_edges):
    """Contract a padded-core witness back to the original edge sequence."""
    _, _, verts, eids = path
    assert all(padded_edges[eid]["kind"] == "core" for eid in eids)

    orig_seq = [padded_edges[eid]["original_edge"] for eid in eids]
    assert len(orig_seq) % 4 == 0

    contracted = []
    for i in range(0, len(orig_seq), 4):
        block = orig_seq[i : i + 4]
        assert len(set(block)) == 1
        contracted.append(block[0])

    cur = verts[0]
    vseq = [cur]
    label = 0
    for oid in contracted:
        e = original_edges[oid]
        assert cur in (e["u"], e["v"])
        cur = e["v"] if cur == e["u"] else e["u"]
        vseq.append(cur)
        label ^= e["label"]
    return tuple(vseq), tuple(contracted), label


def explicit_control():
    adj = defaultdict(list)
    edges = []
    # Core has target 11 on the unique 0-4 route of length 3.
    add_edge(adj, edges, 0, 1, 3)
    add_edge(adj, edges, 1, 2, 0)
    add_edge(adj, edges, 2, 4, 0)
    # Other core route creates extra non-target structure.
    add_edge(adj, edges, 0, 3, 1)
    add_edge(adj, edges, 3, 4, 0)
    s, t, target = 0, 4, 3

    paths = enumerate_simple_paths(adj, edges, s, t)
    before, _ = label_minima(paths)
    assert before[target] == 3

    pa, pe = pad_instance(adj, edges, s, t, target)
    ppaths = enumerate_simple_paths(pa, pe, s, t)
    after, witnesses = label_minima(ppaths)

    assert after[target] == 12
    assert max(after[g] for g in range(4) if g != target) <= 3
    assert after[target] > max(after[g] for g in range(4) if g != target)

    w = witnesses[target]
    vseq, _, lab = contract_core_witness(w, pe, edges)
    assert vseq[0] == s and vseq[-1] == t and lab == target
    assert len(vseq) - 1 == before[target]

    return {"before": before, "after": after}


def infeasible_control():
    adj = defaultdict(list)
    edges = []
    add_edge(adj, edges, 0, 1, 0)
    add_edge(adj, edges, 1, 2, 0)
    s, t, target = 0, 2, 3
    before, _ = label_minima(enumerate_simple_paths(adj, edges, s, t))
    assert before[target] >= INF

    pa, pe = pad_instance(adj, edges, s, t, target)
    after, _ = label_minima(enumerate_simple_paths(pa, pe, s, t))
    assert after[target] >= INF
    assert all(after[g] <= 3 for g in range(4) if g != target)
    return {"before": before, "after": after, "target": target}


def random_controls(trials=180):
    rng = random.Random(SEED)
    feasible = 0
    threshold_checks = 0
    witness_checks = 0

    for _ in range(trials):
        n = rng.choice((4, 5, 6))
        adj, edges, s, t = build_random_graph(rng, n)
        paths = enumerate_simple_paths(adj, edges, s, t)
        before, _ = label_minima(paths)

        feasible_labels = [g for g in range(4) if before[g] < INF]
        target = rng.choice(feasible_labels)
        pa, pe = pad_instance(adj, edges, s, t, target)
        ppaths = enumerate_simple_paths(pa, pe, s, t)
        after, witnesses = label_minima(ppaths)

        feasible += 1
        assert after[target] == 4 * before[target]
        for g in range(4):
            if g != target:
                assert after[g] <= 3
        assert after[target] >= 4
        assert after[target] > max(after[g] for g in range(4) if g != target)

        for threshold in range(0, n + 2):
            assert (before[target] <= threshold) == (
                after[target] <= 4 * threshold
            )
            assert (before[target] == threshold) == (
                after[target] == 4 * threshold
            )
            threshold_checks += 2

        witness = witnesses[target]
        assert witness is not None
        assert all(pe[eid]["kind"] == "core" for eid in witness[3])
        vseq, oids, lab = contract_core_witness(witness, pe, edges)
        assert vseq[0] == s and vseq[-1] == t
        assert len(vseq) == len(set(vseq))
        assert lab == target
        assert len(oids) == before[target]
        witness_checks += 1

    assert feasible == trials
    return {
        "trials": trials,
        "feasible_targets": feasible,
        "threshold_checks": threshold_checks,
        "witness_checks": witness_checks,
    }


def main():
    receipt = {
        "status": "PASS",
        "theorem": "GF2_SQUARED_STRICT_MAX_PROMISE_UNIVERSAL_PADDING_BARRIER",
        "explicit_control": explicit_control(),
        "infeasible_control": infeasible_control(),
        "random_controls": random_controls(),
        "verified": [
            "m_prime_c == 4*m_c for every feasible sampled target",
            "m_prime_d <= 3 for all d != c",
            "c is the unique strict maximum whenever feasible",
            "threshold and exact-equality scaling by factor four",
            "shortest target witness contracts back to a shortest original witness",
            "infeasible target remains infeasible",
        ],
        "claim_ceiling": (
            "PROMISE_REDUCTION_BARRIER_ONLY__NO_DETERMINISTIC_XCSP2_SOLVER__"
            "NO_P_VS_NP_PROMOTION"
        ),
    }
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
