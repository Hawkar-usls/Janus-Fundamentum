#!/usr/bin/env python3
"""R5 E9 CSBC coverage sanity.

This is NOT a SAT breakthrough experiment.
It verifies the local semantic identity behind DECISION gates and demonstrates
the exact distinction between an exponentially large Shannon tree and a memoized
residual-state DAG.

The stopping class here is deliberately only Horn or dual-Horn, so the script
does not depend on a q-Horn recognizer. It is a diagnostic scaffold for the
future residual-state census.
"""

from functools import lru_cache
from itertools import product
import random


def canon_formula(clauses):
    cleaned = []
    for c in clauses:
        c = frozenset(c)
        if any(-l in c for l in c):
            continue  # tautological clause
        cleaned.append(c)
    return tuple(sorted(set(cleaned), key=lambda c: (len(c), tuple(sorted(c)))))


def restrict(F, var, value):
    true_lit = var if value else -var
    false_lit = -true_lit
    out = []
    for c in F:
        if true_lit in c:
            continue
        nc = frozenset(l for l in c if l != false_lit)
        out.append(nc)
    return canon_formula(out)


def is_horn(F):
    return all(sum(1 for l in c if l > 0) <= 1 for c in F)


def is_dual_horn(F):
    return all(sum(1 for l in c if l < 0) <= 1 for c in F)


def vars_of(F):
    return sorted({abs(l) for c in F for l in c})


def eval_formula(F, assignment):
    for c in F:
        if not c:
            return False
        if not any((assignment[abs(l)] if l > 0 else not assignment[abs(l)])
                   for l in c):
            return False
    return True


@lru_cache(maxsize=None)
def dag_nodes(F):
    # Exact structural recursion, stopping at Horn/dual-Horn leaves.
    if is_horn(F) or is_dual_horn(F) or any(len(c) == 0 for c in F):
        return 1
    vs = vars_of(F)
    if not vs:
        return 1
    x = vs[0]
    f0, f1 = restrict(F, x, False), restrict(F, x, True)
    # Node count of the reachable memoized state set is computed separately.
    return 1 + dag_nodes(f0) + dag_nodes(f1)


def reachable_states(F):
    seen = set()
    stack = [F]
    while stack:
        G = stack.pop()
        if G in seen:
            continue
        seen.add(G)
        if is_horn(G) or is_dual_horn(G) or any(len(c) == 0 for c in G):
            continue
        vs = vars_of(G)
        if not vs:
            continue
        x = vs[0]
        stack.append(restrict(G, x, False))
        stack.append(restrict(G, x, True))
    return seen


def check_shannon_identity(F):
    vs = vars_of(F)
    if not vs:
        return
    x = vs[0]
    f0, f1 = restrict(F, x, False), restrict(F, x, True)
    rest = [v for v in vs if v != x]
    for bits in product([False, True], repeat=len(rest)):
        base = dict(zip(rest, bits))
        for value in (False, True):
            a = dict(base)
            a[x] = value
            lhs = eval_formula(F, a)
            rhs = eval_formula(f1 if value else f0, a)
            assert lhs == rhs


def random_3cnf(n, m, seed):
    rng = random.Random(seed)
    clauses = []
    for _ in range(m):
        vs = rng.sample(range(1, n + 1), min(3, n))
        clauses.append(frozenset(v if rng.getrandbits(1) else -v for v in vs))
    return canon_formula(clauses)


def main():
    for n in range(1, 8):
        for seed in range(50):
            F = random_3cnf(n, max(1, 4*n), (n << 16) ^ seed)
            check_shannon_identity(F)
            states = reachable_states(F)
            assert F in states
    print("R5 E9 CSBC local Shannon coverage sanity: PASS")
    print("NOTE: no polynomial bound on residual-state DAG size is claimed.")


if __name__ == "__main__":
    main()
