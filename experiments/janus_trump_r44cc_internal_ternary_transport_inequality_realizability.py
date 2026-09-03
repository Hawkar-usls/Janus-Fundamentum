#!/usr/bin/env python3
from collections import Counter, defaultdict
from itertools import combinations, permutations, product
import json

LOCAL = [[1, -2], [1, 2, 3], [-1, 3], [2, -3]]


def canon(C):
    return tuple(sorted(set(C), key=lambda z: (abs(z), z)))


def vars_clause(C):
    return {abs(l) for l in C}


def rename_clause(C, mapping):
    return [(1 if l > 0 else -1) * mapping[abs(l)] for l in C]


def block_map(i):
    return {1: 3 * i + 1, 2: 3 * i + 2, 3: 3 * i + 3}


def target_formula(n, edges):
    maps = [block_map(i) for i in range(n)]
    F = []
    for m in maps:
        F.extend(rename_clause(C, m) for C in LOCAL)
    for u, v in edges:
        F.append([maps[u][1], maps[v][1]])
    return F


def source_formula(n, edges):
    maps = [block_map(i) for i in range(n)]
    F = []
    for m in maps:
        F.extend(rename_clause(C, m) for C in LOCAL)
    for u, v in edges:
        for a in (1, 2, 3):
            for b in (1, 2, 3):
                if a != b:
                    F.append([maps[u][a], maps[v][b]])
    return F


def common_clause_multiset(A, B):
    a = Counter(canon(C) for C in A)
    b = Counter(canon(C) for C in B)
    out = []
    for C in sorted(set(a) & set(b)):
        out.extend([list(C)] * min(a[C], b[C]))
    return out


def recover_blocks(A, B):
    common = common_clause_multiset(A, B)
    V = {abs(l) for C in A + B for l in C}
    adj = {v: set() for v in V}
    touched = set()
    for C in common:
        vs = sorted(vars_clause(C))
        touched.update(vs)
        for i, u in enumerate(vs):
            for w in vs[i + 1:]:
                adj[u].add(w)
                adj[w].add(u)
    if touched != V:
        return None
    comps = []
    seen = set()
    for s in sorted(V):
        if s in seen:
            continue
        stack = [s]
        comp = set()
        while stack:
            u = stack.pop()
            if u in comp:
                continue
            comp.add(u)
            seen.add(u)
            stack.extend(adj[u] - comp)
        comps.append(frozenset(comp))
    return sorted(comps, key=lambda B: min(B))


def signed_maps(block):
    B = tuple(sorted(block))
    for perm in permutations(B):
        for signs in product((1, -1), repeat=len(B)):
            yield {v: s * w for v, w, s in zip(B, perm, signs)}


def apply_clause(C, pi):
    out = set()
    for l in C:
        z = pi[abs(l)]
        out.add(z if l > 0 else -z)
    return out


def taut(image):
    return any(-l in image for l in image)


def transport_clause_ok(C, pi, source_sets):
    im = apply_clause(C, pi)
    return taut(im) or any(D.issubset(im) for D in source_sets)


def local_candidates(target, source, block):
    T = [C for C in target if vars_clause(C).issubset(block)]
    S = [set(C) for C in source if vars_clause(C).issubset(block)]
    cands = [pi for pi in signed_maps(block) if all(transport_clause_ok(C, pi, S) for C in T)]
    cands.sort(key=lambda pi: tuple(pi[v] for v in sorted(block)))
    return cands


def recovered_interactions(target, blocks):
    owner = {v: i for i, B in enumerate(blocks) for v in B}
    edge_clauses = defaultdict(list)
    for C in target:
        ids = tuple(sorted({owner[abs(l)] for l in C}))
        if len(ids) <= 1:
            continue
        if len(ids) != 2:
            raise AssertionError("non-pairwise target interaction")
        edge_clauses[ids].append(C)
    return edge_clauses


def recover_transport_csp(target, source):
    blocks = recover_blocks(target, source)
    if blocks is None or any(len(B) != 3 for B in blocks):
        raise AssertionError("block recovery failed")
    cands = [local_candidates(target, source, B) for B in blocks]
    if any(len(C) != 3 for C in cands):
        raise AssertionError(("expected exactly three local candidates", [len(C) for C in cands]))
    edge_clauses = recovered_interactions(target, blocks)
    source_sets = [set(C) for C in source]
    allowed = {}
    for (i, j), clauses in edge_clauses.items():
        relation = set()
        for ai, pi in enumerate(cands[i]):
            for bj, pj in enumerate(cands[j]):
                merged = dict(pi)
                merged.update(pj)
                if all(transport_clause_ok(C, merged, source_sets) for C in clauses):
                    relation.add((ai, bj))
        allowed[(i, j)] = relation
    return blocks, cands, allowed


def candidate_color(pi, block):
    B = sorted(block)
    first = B[0]
    image = pi[first]
    if image < 0:
        raise AssertionError("expected positive cyclic candidate")
    return B.index(image)


def recovered_transport_colorings(target, source):
    blocks, cands, allowed = recover_transport_csp(target, source)
    color_of = [[candidate_color(pi, B) for pi in C] for B, C in zip(blocks, cands)]
    out = set()
    for choice in product(range(3), repeat=len(blocks)):
        if all((choice[i], choice[j]) in rel for (i, j), rel in allowed.items()):
            out.add(tuple(color_of[i][choice[i]] for i in range(len(blocks))))
    return out, blocks, cands, allowed


def proper_colorings(n, edges):
    return {
        colors
        for colors in product(range(3), repeat=n)
        if all(colors[u] != colors[v] for u, v in edges)
    }


def all_graphs(n):
    possible = list(combinations(range(n), 2))
    for mask in range(1 << len(possible)):
        yield [e for i, e in enumerate(possible) if (mask >> i) & 1]


def audit(max_n=5):
    expected_relation = {(a, b) for a in range(3) for b in range(3) if a != b}
    checked = 0
    for n in range(1, max_n + 1):
        for edges in all_graphs(n):
            A = target_formula(n, edges)
            B = source_formula(n, edges)
            recovered, blocks, cands, allowed = recovered_transport_colorings(A, B)
            truth = proper_colorings(n, edges)
            assert recovered == truth
            assert len(A) == 4 * n + len(edges)
            assert len(B) == 4 * n + 6 * len(edges)
            assert all(len(block) == 3 for block in blocks)
            assert all(len(C) == 3 for C in cands)
            assert all(rel == expected_relation for rel in allowed.values())
            checked += 1

    triangle = [(0, 1), (1, 2), (0, 2)]
    k4 = list(combinations(range(4), 2))
    tri, _, _, tri_allowed = recovered_transport_colorings(target_formula(3, triangle), source_formula(3, triangle))
    k4c, _, _, _ = recovered_transport_colorings(target_formula(4, k4), source_formula(4, k4))
    assert len(tri) == 6
    assert len(k4c) == 0
    assert all(rel == expected_relation for rel in tri_allowed.values())

    return {
        "gate": "R44CC_INTERNAL_TERNARY_TRANSPORT_INEQUALITY_REALIZABILITY",
        "graphs_checked": checked,
        "max_n": max_n,
        "local_block_size": 3,
        "local_transport_candidate_count": 3,
        "edge_relation": "EXACT_INEQUALITY_ON_THREE_RECOVERED_TRANSPORT_CANDIDATES",
        "blocks_recovered_from_formula_common_core": True,
        "construction_labels_supplied_to_recovery": False,
        "triangle_transport_assignment_count": len(tri),
        "k4_transport_assignment_count": len(k4c),
        "exact_bijection_with_graph_3colorings_on_enumerated_universe": True,
        "formula_size": {"target": "4n+m", "source": "4n+6m"},
        "internal_ternary_inequality_realizable": True,
        "all_domain3_transport_discovery_is_hard": False,
        "full_transport_polynomiality_proven": False,
        "SAT_IN_P": "NOT_PROVED",
        "P_VS_NP": "OPEN"
    }


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2, sort_keys=True))
