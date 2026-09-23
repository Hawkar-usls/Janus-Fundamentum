#!/usr/bin/env python3
"""R5 E9 source-backed NAE4PART q-Horn-stopped stress census.

Diagnostic only; no asymptotic claim.

Generates linear 3-uniform hypergraphs whose edges are the union of four
partitions of the variable set into triples.  Every NAE edge {x,y,z} is encoded as
    (x or y or z) and (~x or ~y or ~z)
which is exactly one dual-Horn plus one Horn clause.

The q-Horn recognizer is the quadratic-cover/SCC implementation already used in
R5 E9.  The state count uses exact residual memoization plus variable-disjoint
component decomposition.
"""

from collections import defaultdict
import random
import statistics


def canon_cnf(clauses):
    out = []
    for clause in clauses:
        c = frozenset(clause)
        if any(-l in c for l in c):
            continue
        out.append(c)
    return tuple(sorted(set(out), key=lambda c: (len(c), tuple(sorted(c)))))


def restrict_cnf(F, var, value):
    true_lit = var if value else -var
    false_lit = -true_lit
    out = []
    for c in F:
        if true_lit in c:
            continue
        out.append(frozenset(l for l in c if l != false_lit))
    return canon_cnf(out)


def quadratic_cover(F):
    max_var = max((abs(l) for c in F for l in c), default=0)
    next_var = max_var + 1
    q = []
    for c in F:
        lits = sorted(c, key=lambda l: (abs(l), l < 0))
        r = len(lits)
        if r <= 1:
            continue
        ys = list(range(next_var, next_var + r - 1))
        next_var += r - 1
        for i in range(r - 1):
            q.append((lits[i], ys[i]))
            q.append((-ys[i], lits[i + 1]))
        for i in range(r - 2):
            q.append((-ys[i], ys[i + 1]))
    return q


def scc_map_2cnf(binary_clauses):
    graph = defaultdict(list)
    nodes = set()
    for a, b in binary_clauses:
        graph[-a].append(b)
        graph[-b].append(a)
        nodes.update((a, -a, b, -b))

    index = 0
    stack = []
    on_stack = set()
    idx, low, comp = {}, {}, {}
    comp_id = 0

    def dfs(v):
        nonlocal index, comp_id
        idx[v] = low[v] = index
        index += 1
        stack.append(v)
        on_stack.add(v)
        for w in graph[v]:
            if w not in idx:
                dfs(w)
                low[v] = min(low[v], low[w])
            elif w in on_stack:
                low[v] = min(low[v], idx[w])
        if low[v] == idx[v]:
            while True:
                w = stack.pop()
                on_stack.remove(w)
                comp[w] = comp_id
                if w == v:
                    break
            comp_id += 1

    for v in list(nodes):
        if v not in idx:
            dfs(v)
    return comp


def qhorn_violating_triple(F):
    comp = scc_map_2cnf(quadratic_cover(F))
    for c in F:
        bad = [l for l in c
               if l in comp and -l in comp and comp[l] == comp[-l]]
        if len(bad) >= 3:
            return tuple(bad[:3])
    return None


def components(F):
    var_to_clause = defaultdict(list)
    for i, c in enumerate(F):
        for l in c:
            var_to_clause[abs(l)].append(i)
    unseen = set(var_to_clause)
    out = []
    while unseen:
        start = unseen.pop()
        queue = [start]
        vars_seen = {start}
        clauses_seen = set()
        while queue:
            v = queue.pop()
            for ci in var_to_clause[v]:
                if ci in clauses_seen:
                    continue
                clauses_seen.add(ci)
                for l in F[ci]:
                    w = abs(l)
                    if w not in vars_seen:
                        vars_seen.add(w)
                        unseen.discard(w)
                        queue.append(w)
        out.append(canon_cnf(F[i] for i in clauses_seen))
    return out


def choose_variable(F, triple):
    candidates = {abs(l) for l in triple}
    counts = {
        x: sum(any(abs(l) == x for l in c) for c in F)
        for x in candidates
    }
    return max(candidates, key=lambda x: (counts[x], -x))


def decomp_dag_count(F, cap=2_000_000):
    seen = set()
    stack = [F]
    while stack:
        G = stack.pop()
        if G in seen:
            continue
        seen.add(G)
        if len(seen) > cap:
            return None

        if not G or any(len(c) == 0 for c in G):
            continue

        triple = qhorn_violating_triple(G)
        if triple is None:
            continue

        cs = components(G)
        if len(cs) > 1:
            stack.extend(cs)
            continue

        x = choose_variable(G, triple)
        stack.append(restrict_cnf(G, x, False))
        stack.append(restrict_cnf(G, x, True))

    return len(seen)


def generate_linear_four_partition_instance(n, seed, max_tries=10000):
    assert n % 3 == 0
    rng = random.Random(seed)
    edges = []
    used_pairs = set()

    for _part in range(4):
        accepted = False
        for _ in range(max_tries):
            vs = list(range(1, n + 1))
            rng.shuffle(vs)
            groups = [tuple(sorted(vs[i:i+3])) for i in range(0, n, 3)]

            pairs = []
            ok = True
            for g in groups:
                gpairs = [(g[0], g[1]), (g[0], g[2]), (g[1], g[2])]
                if any(p in used_pairs for p in gpairs):
                    ok = False
                    break
                pairs.extend(gpairs)

            if ok:
                edges.extend(groups)
                used_pairs.update(pairs)
                accepted = True
                break

        if not accepted:
            return None

    clauses = []
    for x, y, z in edges:
        clauses.append(frozenset((x, y, z)))
        clauses.append(frozenset((-x, -y, -z)))

    return canon_cnf(clauses)


def main():
    print("n successful_samples median_states counts")
    for n in (15, 18, 21, 24, 27, 30):
        counts = []
        for sample in range(6):
            F = generate_linear_four_partition_instance(
                n, 0xABCD + 100*n + sample)
            if F is None:
                continue
            counts.append(decomp_dag_count(F))
        print(n, len(counts), statistics.median(counts), counts)

    print("DIAGNOSTIC_ONLY: no asymptotic complexity claim.")


if __name__ == "__main__":
    main()
