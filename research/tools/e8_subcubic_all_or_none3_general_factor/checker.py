from itertools import product


def sat_eval(formula, assignment):
    return all(any((assignment[abs(l)] if l > 0 else 1 - assignment[abs(l)]) for l in clause) for clause in formula)


def brute_sat(formula):
    vars_ = sorted({abs(l) for c in formula for l in c})
    for vals in product((0, 1), repeat=len(vars_)):
        a = dict(zip(vars_, vals))
        if sat_eval(formula, a):
            return True, a
    return False, None


def build_factor(formula):
    edges = []
    constraints = {}
    # vertices are tuples ('v',i), ('c',j), ('n',occ)
    occ_by_var = {}
    occ = 0
    for ci, clause in enumerate(formula):
        c = ('c', ci)
        constraints[c] = None
        for lit in clause:
            v = ('v', abs(lit))
            occ_by_var.setdefault(abs(lit), 0)
            occ_by_var[abs(lit)] += 1
            if lit > 0:
                edges.append((v, c))
            else:
                inv = ('n', occ)
                constraints[inv] = {1}
                edges.append((v, inv))
                edges.append((inv, c))
            occ += 1
    # degree-dependent constraints
    deg = {}
    for u, w in edges:
        deg[u] = deg.get(u, 0) + 1
        deg[w] = deg.get(w, 0) + 1
    for var, d in occ_by_var.items():
        constraints[('v', var)] = {0, d}
    for ci, clause in enumerate(formula):
        d = deg[('c', ci)]
        constraints[('c', ci)] = set(range(1, d + 1))
    assert max(deg.values(), default=0) <= 3
    return edges, constraints


def factor_ok(mask, edges, constraints):
    d = {v: 0 for v in constraints}
    for i, (u, w) in enumerate(edges):
        if (mask >> i) & 1:
            d[u] += 1
            d[w] += 1
    return all(d[v] in allowed for v, allowed in constraints.items())


def brute_factor(formula):
    edges, constraints = build_factor(formula)
    for mask in range(1 << len(edges)):
        if factor_ok(mask, edges, constraints):
            return True, mask, len(edges)
    return False, None, len(edges)


def check(formula):
    # This checker is for the bounded-occurrence frontier only.
    counts = {}
    for c in formula:
        assert len(c) in (2, 3)
        for l in c:
            counts[abs(l)] = counts.get(abs(l), 0) + 1
    assert all(v <= 3 for v in counts.values()), counts
    s, a = brute_sat(formula)
    f, mask, m = brute_factor(formula)
    assert s == f, (formula, s, f, a, mask)
    print(f'clauses={len(formula)} vars={len(counts)} factor_edges={m} SAT={int(s)} FACTOR={int(f)} PASS')


def main():
    controls = [
        [(1, 2), (-1, 3)],
        [(1, 2, 3), (-1, 2)],
        [(1, 2), (1, -2), (-1, 3), (-3, 4), (-3, -4)],  # v1.5 explicit UNSAT
        [(1, 2, 3), (-1, -2), (-3, 4)],
    ]
    for f in controls:
        check(f)
    print('PASS: bounded-occurrence SAT iff subcubic all-or-none3 general factor feasibility')


if __name__ == '__main__':
    main()
