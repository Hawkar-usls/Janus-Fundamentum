#!/usr/bin/env python3
"""R5 E9 q-Horn-stopped residual DAG census.

Diagnostic only.  It does NOT establish an asymptotic bound.

Implements:
- exact q-Horn recognition via quadratic cover + SCC characterization;
- optional brute validation of the recognizer on tiny instances;
- Shannon decision recursion stopped at q-Horn leaves;
- exact residual-CNF memoization;
- source-native decomposition into variable-disjoint CNF components.
"""

from collections import defaultdict
from itertools import product
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


def brute_qhorn(F):
    variables = sorted({abs(l) for c in F for l in c})
    pos = {v: i for i, v in enumerate(variables)}
    # weights encoded as 0,1,2 for 0,1/2,1; clause bound is <=2.
    for states in product((0, 1, 2), repeat=len(variables)):
        good = True
        for c in F:
            total = 0
            for l in c:
                g = states[pos[abs(l)]]
                total += g if l > 0 else 2 - g
            if total > 2:
                good = False
                break
        if good:
            return True
    return False


def variables(F):
    return sorted({abs(l) for c in F for l in c})


def components(F):
    var_to_clause = defaultdict(list)
    for i, c in enumerate(F):
        for l in c:
            var_to_clause[abs(l)].append(i)
    unseen = set(var_to_clause)
    result = []
    while unseen:
        start = unseen.pop()
        queue = [start]
        var_set = {start}
        clause_set = set()
        while queue:
            v = queue.pop()
            for ci in var_to_clause[v]:
                if ci in clause_set:
                    continue
                clause_set.add(ci)
                for l in F[ci]:
                    w = abs(l)
                    if w not in var_set:
                        var_set.add(w)
                        unseen.discard(w)
                        queue.append(w)
        result.append(canon_cnf(F[i] for i in clause_set))
    return result


def choose_violation_variable(F, triple):
    candidates = {abs(l) for l in triple}
    counts = {
        x: sum(any(abs(l) == x for l in c) for c in F)
        for x in candidates
    }
    return max(candidates, key=lambda x: (counts[x], -x))


def raw_dag_count(F):
    seen = set()
    stack = [F]
    while stack:
        G = stack.pop()
        if G in seen:
            continue
        seen.add(G)
        triple = qhorn_violating_triple(G)
        if triple is None:
            continue
        x = choose_violation_variable(G, triple)
        stack.append(restrict_cnf(G, x, False))
        stack.append(restrict_cnf(G, x, True))
    return len(seen)


def tree_count(F):
    count = 0
    stack = [F]
    while stack:
        G = stack.pop()
        count += 1
        triple = qhorn_violating_triple(G)
        if triple is None:
            continue
        x = choose_violation_variable(G, triple)
        stack.append(restrict_cnf(G, x, False))
        stack.append(restrict_cnf(G, x, True))
    return count


def decomp_dag_count(F):
    seen = set()
    stack = [F]
    while stack:
        G = stack.pop()
        if G in seen:
            continue
        seen.add(G)

        if not G or any(len(c) == 0 for c in G):
            continue

        triple = qhorn_violating_triple(G)
        if triple is None:
            continue

        cs = components(G)
        if len(cs) > 1:
            stack.extend(cs)
            continue

        x = choose_violation_variable(G, triple)
        stack.append(restrict_cnf(G, x, False))
        stack.append(restrict_cnf(G, x, True))
    return len(seen)


def random_3sat(n, m, seed):
    rng = random.Random(seed)
    clauses, used = [], set()
    while len(clauses) < m:
        vs = rng.sample(range(1, n + 1), 3)
        c = frozenset(v if rng.getrandbits(1) else -v for v in vs)
        if c not in used:
            used.add(c)
            clauses.append(c)
    return canon_cnf(clauses)


def validate_recognizer():
    for n in range(1, 7):
        for seed in range(100):
            rng = random.Random(999*n + seed)
            clauses = []
            for _ in range(max(1, 4*n)):
                vs = rng.sample(range(1, n + 1), min(3, n))
                clauses.append(frozenset(
                    v if rng.getrandbits(1) else -v for v in vs))
            F = canon_cnf(clauses)
            assert (qhorn_violating_triple(F) is None) == brute_qhorn(F)


def run_census():
    rows = []
    for n in range(6, 23, 2):
        raw, decomp, tree = [], [], []
        m = round(4.26*n)
        for sample in range(12):
            F = random_3sat(n, m, 0xEA0000 + 100*n + sample)
            raw.append(raw_dag_count(F))
            decomp.append(decomp_dag_count(F))
            tree.append(tree_count(F))
        rows.append((
            n, m,
            statistics.median(tree),
            statistics.median(raw),
            statistics.median(decomp),
        ))
    return rows


def main():
    validate_recognizer()
    print("QHORN_SCC_RECOGNIZER_VS_BRUTE_BETA = PASS")
    print("n m tree_median exact_dag_median decomp_dag_median")
    for row in run_census():
        print(*row)
    print("DIAGNOSTIC_ONLY: no asymptotic complexity claim.")


if __name__ == "__main__":
    main()
