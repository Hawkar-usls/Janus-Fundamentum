#!/usr/bin/env python3
import itertools
from collections import deque


def maximum_matching(clauses, variables, edges):
    adj = {c: [v for v in variables if (c, v) in edges] for c in clauses}
    mate_v = {}
    mate_c = {}

    def augment(c, seen):
        for v in adj[c]:
            if v in seen:
                continue
            seen.add(v)
            if v not in mate_v or augment(mate_v[v], seen):
                old = mate_v.get(v)
                mate_v[v] = c
                mate_c[c] = v
                if old is not None and old != c:
                    mate_c.pop(old, None)
                return True
        return False

    for c in clauses:
        augment(c, set())
    return mate_c, mate_v


def dm_kernel(clauses, variables, edges):
    mate_c, mate_v = maximum_matching(clauses, variables, edges)
    reached_c = {c for c in clauses if c not in mate_c}
    reached_v = set()
    q = deque(("c", c) for c in reached_c)

    while q:
        side, u = q.popleft()
        if side == "c":
            for v in variables:
                if (u, v) in edges and mate_c.get(u) != v and v not in reached_v:
                    reached_v.add(v)
                    q.append(("v", v))
        else:
            c = mate_v.get(u)
            if c is not None and c not in reached_c:
                reached_c.add(c)
                q.append(("c", c))

    autarky_clauses = set(clauses) - reached_c
    autarky_vars = {mate_c[c] for c in autarky_clauses}
    return reached_c, reached_v, autarky_clauses, autarky_vars, mate_c


def neighborhood_clauses(varset, clauses, edges):
    return {c for c in clauses if any((c, v) in edges for v in varset)}


def neighborhood_vars(clause_set, variables, edges):
    return {v for v in variables if any((c, v) in edges for c in clause_set)}


def max_deficiency_and_smallest_tight(clauses, variables, edges):
    best = -10**9
    tight = []
    for r in range(len(clauses) + 1):
        for tup in itertools.combinations(clauses, r):
            s = set(tup)
            d = len(s) - len(neighborhood_vars(s, variables, edges))
            if d > best:
                best = d
                tight = [s]
            elif d == best:
                tight.append(s)
    smallest = set.intersection(*tight) if tight else set()
    return best, smallest


def has_matching_autarky(clauses, variables, edges):
    for r in range(1, len(variables) + 1):
        for tup in itertools.combinations(variables, r):
            x = set(tup)
            touched = neighborhood_clauses(x, clauses, edges)
            if not touched:
                continue
            subedges = {(c, v) for (c, v) in edges if c in touched and v in x}
            mate_c, _ = maximum_matching(list(touched), list(x), subedges)
            if len(mate_c) == len(touched):
                return True
    return False


def exhaustive_small_graph_replay():
    checked = 0
    for nc in range(1, 4):
        for nv in range(1, 4):
            clauses = list(range(nc))
            variables = list(range(nv))
            universe = [(c, v) for c in clauses for v in variables]
            for mask in range(1 << len(universe)):
                edges = {e for i, e in enumerate(universe) if (mask >> i) & 1}
                c0, v0, a, x, mate_c = dm_kernel(clauses, variables, edges)
                d, smallest = max_deficiency_and_smallest_tight(clauses, variables, edges)
                assert c0 == smallest, (clauses, variables, edges, c0, smallest)
                assert len(c0) - len(v0) == d
                assert neighborhood_clauses(x, clauses, edges) == a
                assert all(c in mate_c and mate_c[c] in x for c in a)
                residual_edges = {(c, v) for (c, v) in edges if c in c0 and v in v0}
                assert not has_matching_autarky(list(c0), list(v0), residual_edges)
                checked += 1
    return checked


def matched_terminal_control():
    clauses = [0, 1, 2]
    variables = [0, 1, 2]
    edges = {(0, 0), (1, 0), (1, 1), (2, 1), (2, 2)}
    c0, _, a, _, _ = dm_kernel(clauses, variables, edges)
    assert c0 == set()
    assert a == set(clauses)


def tovey_incidence(original_clauses):
    # Each original-clause entry is an original variable id. Each occurrence gets a fresh copy.
    copies_by_var = {}
    inherited = []
    next_copy = 0
    for ci, clause in enumerate(original_clauses):
        row = []
        for var in clause:
            copy = next_copy
            next_copy += 1
            copies_by_var.setdefault(var, []).append(copy)
            row.append(copy)
        inherited.append(row)

    clauses = []
    edges = set()
    cid = 0
    for row in inherited:
        clauses.append(cid)
        for copy in row:
            edges.add((cid, copy))
        cid += 1

    for var, copies in sorted(copies_by_var.items()):
        assert len(copies) >= 2
        for j, copy in enumerate(copies):
            nxt = copies[(j + 1) % len(copies)]
            clauses.append(cid)
            edges.add((cid, copy))
            edges.add((cid, nxt))
            cid += 1

    variables = list(range(next_copy))
    return clauses, variables, edges


def tovey_source_return_control():
    # Four 3-clauses on four variables; every original variable occurs exactly three times.
    original = [
        (0, 1, 2),
        (0, 1, 3),
        (0, 2, 3),
        (1, 2, 3),
    ]
    clauses, variables, edges = tovey_incidence(original)
    assert len(variables) == 12
    assert len(clauses) == 16
    c0, _, a, _, _ = dm_kernel(clauses, variables, edges)
    assert c0 == set(clauses)
    assert a == set()

    full_delta = len(clauses) - len(variables)
    assert full_delta == 4
    # Exhaustively replay the strict-subset deficiency characterization on this finite control.
    for mask in range((1 << len(clauses)) - 1):
        s = {clauses[i] for i in range(len(clauses)) if (mask >> i) & 1}
        delta = len(s) - len(neighborhood_vars(s, variables, edges))
        assert delta < full_delta


def main():
    checked = exhaustive_small_graph_replay()
    matched_terminal_control()
    tovey_source_return_control()
    print(f"PASS matching-autarky DM kernel: {checked} exhaustive small bipartite graphs")
    print("PASS matched-formula full autarky terminal")
    print("PASS Tovey source-return control: 16-clause copy-cycle image is matching-lean")


if __name__ == "__main__":
    main()
