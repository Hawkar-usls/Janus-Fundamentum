from __future__ import annotations
from collections import deque
import time


def canonicalize(raw):
    out = set()
    for clause in raw:
        s = {int(x) for x in clause}
        if any(-x in s for x in s):
            continue
        if not s:
            out.add(tuple())
            continue
        out.add(tuple(sorted(s, key=lambda z: (abs(z), z < 0))))
    return sorted(out, key=lambda c: (len(c), tuple((abs(x), x < 0) for x in c)))


def replay(raw, assignment):
    for clause in raw:
        if not any((lit > 0 and bool(assignment.get(abs(int(lit)), False))) or
                   (lit < 0 and not bool(assignment.get(abs(int(lit)), False)))
                   for lit in clause):
            return False
    return True


def recognize_graph_php(raw):
    cnf = canonicalize(raw)
    if not cnf or any(len(c) == 0 for c in cnf):
        return None
    positives = [c for c in cnf if c and all(x > 0 for x in c)]
    negatives = [c for c in cnf if len(c) == 2 and all(x < 0 for x in c)]
    if len(positives) + len(negatives) != len(cnf) or not positives:
        return None
    owner = {}
    blocks = []
    for u, clause in enumerate(positives):
        block = []
        for var in clause:
            if var in owner:
                return None
            owner[var] = u
            block.append(var)
        blocks.append(tuple(block))
    all_vars = {abs(x) for c in cnf for x in c}
    if set(owner) != all_vars:
        return None

    conflict = {v: set() for v in owner}
    neg_pairs = set()
    for a, b in negatives:
        x, y = -a, -b
        if x == y or x not in owner or y not in owner:
            return None
        if owner[x] == owner[y]:
            return None
        p = tuple(sorted((x, y)))
        neg_pairs.add(p)
        conflict[x].add(y)
        conflict[y].add(x)

    unseen = set(owner)
    components = []
    while unseen:
        start = min(unseen)
        unseen.remove(start)
        stack = [start]
        comp = {start}
        while stack:
            x = stack.pop()
            for y in conflict[x]:
                if y in unseen:
                    unseen.remove(y)
                    comp.add(y)
                    stack.append(y)
        components.append(tuple(sorted(comp)))
    comp_of = {}
    components.sort(key=lambda c: (min(c), len(c)))
    for rid, comp in enumerate(components):
        seen_left = set()
        for x in comp:
            u = owner[x]
            if u in seen_left:
                return None
            seen_left.add(u)
            comp_of[x] = rid
        for i, x in enumerate(comp):
            for y in comp[i + 1:]:
                if tuple(sorted((x, y))) not in neg_pairs:
                    return None

    expected_neg = set()
    for comp in components:
        for i, x in enumerate(comp):
            for y in comp[i + 1:]:
                expected_neg.add(tuple(sorted((x, y))))
    if expected_neg != neg_pairs:
        return None

    adj = {u: [] for u in range(len(blocks))}
    edge_var = {}
    for var, u in owner.items():
        v = comp_of[var]
        if (u, v) in edge_var:
            return None
        edge_var[(u, v)] = var
        adj[u].append(v)
    for u in adj:
        adj[u] = tuple(sorted(adj[u]))

    return {
        'm': len(blocks),
        'n': len(components),
        'blocks': [list(b) for b in blocks],
        'rights': [list(c) for c in components],
        'adj': {str(u): list(vs) for u, vs in adj.items()},
        'edge_var': {f'{u}:{v}': x for (u, v), x in edge_var.items()},
    }


def _decode_graph(g):
    adj = {int(u): tuple(vs) for u, vs in g['adj'].items()}
    edge_var = {}
    for key, var in g['edge_var'].items():
        u, v = map(int, key.split(':'))
        edge_var[(u, v)] = int(var)
    return adj, edge_var


def maximum_matching(g):
    adj, edge_var = _decode_graph(g)
    U = list(range(g['m']))
    pair_u = {u: None for u in U}
    pair_v = {v: None for v in range(g['n'])}
    dist = {}

    def bfs():
        q = deque()
        found = False
        for u in U:
            if pair_u[u] is None:
                dist[u] = 0
                q.append(u)
            else:
                dist[u] = -1
        while q:
            u = q.popleft()
            for v in adj[u]:
                u2 = pair_v[v]
                if u2 is None:
                    found = True
                elif dist[u2] < 0:
                    dist[u2] = dist[u] + 1
                    q.append(u2)
        return found

    def dfs(u):
        for v in adj[u]:
            u2 = pair_v[v]
            if u2 is None or (dist.get(u2, -1) == dist[u] + 1 and dfs(u2)):
                pair_u[u] = v
                pair_v[v] = u
                return True
        dist[u] = -1
        return False
    matching_size = 0
    while bfs():
        for u in U:
            if pair_u[u] is None and dfs(u):
                matching_size += 1
    return pair_u, pair_v, matching_size, edge_var


def hall_witness(g, pair_u, pair_v):
    adj, _ = _decode_graph(g)
    roots = [u for u in range(g['m']) if pair_u[u] is None]
    zl = set(roots)
    zr = set()
    q = deque(roots)
    while q:
        u = q.popleft()
        for v in adj[u]:
            if pair_u[u] == v:
                continue
            if v in zr:
                continue
            zr.add(v)
            u2 = pair_v[v]
            if u2 is not None and u2 not in zl:
                zl.add(u2)
                q.append(u2)
    exact_n = set()
    for u in zl:
        exact_n.update(adj[u])
    if len(exact_n) >= len(zl):
        raise AssertionError(('HALL_WITNESS_NOT_DEFICIENT', len(zl), len(exact_n)))
    return sorted(zl), sorted(exact_n)


def counting_baseline(g):
    if g['m'] > g['n']:
        return {'decision': 'UNSAT', 'reason': 'GLOBAL_CARDINALITY_M_GT_N'}
    return {'decision': 'UNKNOWN', 'reason': 'GLOBAL_CARDINALITY_INSUFFICIENT'}


def solve(raw):
    t0 = time.perf_counter()
    g = recognize_graph_php(raw)
    t1 = time.perf_counter()
    if g is None:
        return {'admitted': False, 'decision': None, 'reason': 'RECOGNIZER_REJECT'}
    pair_u, pair_v, size, edge_var = maximum_matching(g)
    t2 = time.perf_counter()
    base = counting_baseline(g)
    if size == g['m']:
        matching = []
        assignment = {abs(int(x)): False for c in raw for x in c}
        for u in range(g['m']):
            v = pair_u[u]
            var = edge_var[(u, v)]
            assignment[var] = True
            matching.append([u, v, var])
        ok = replay(raw, assignment)
        t3 = time.perf_counter()
        if not ok:
            raise AssertionError('RECONSTRUCTED_ASSIGNMENT_FAILED_ROOT_REPLAY')
        return {
            'admitted': True, 'decision': 'SAT', 'graph': g,
            'certificate': {'kind': 'SATURATING_MATCHING', 'matching': matching},
            'assignment': assignment, 'counting_baseline': base,
            'timing_ms': {'recognize_construct': (t1-t0)*1000, 'matching_hall': (t2-t1)*1000,
                          'reconstruct_verify': (t3-t2)*1000}
        }
    S, N = hall_witness(g, pair_u, pair_v)
    t3 = time.perf_counter()
    return {
        'admitted': True, 'decision': 'UNSAT', 'graph': g,
        'certificate': {'kind': 'HALL_DEFICIENT_SET', 'S': S, 'N': N},
        'assignment': None, 'counting_baseline': base,
        'timing_ms': {'recognize_construct': (t1-t0)*1000, 'matching_hall': (t2-t1)*1000,
                      'reconstruct_verify': (t3-t2)*1000}
    }
