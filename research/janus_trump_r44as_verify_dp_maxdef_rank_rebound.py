#!/usr/bin/env python3
from itertools import combinations, product

F = [
    (2,3,-4),
    (-1,2,4),
    (-2,-5,-6),
    (1,-3,-4),
    (1,-5,6),
    (-3,5,-6),
    (-2,3,6),
    (-1,4,5),
]
N = 6


def vars_of(clauses):
    return {abs(l) for C in clauses for l in C}


def deficiency(clauses):
    return len(clauses) - len(vars_of(clauses))


def max_def(clauses):
    m = len(clauses)
    best = -10**9
    for mask in range(1 << m):
        sub = [clauses[i] for i in range(m) if (mask >> i) & 1]
        best = max(best, deficiency(sub))
    return best


def matching_lean(clauses):
    d = deficiency(clauses)
    m = len(clauses)
    for mask in range((1 << m) - 1):
        sub = [clauses[i] for i in range(m) if (mask >> i) & 1]
        if deficiency(sub) >= d:
            return False
    return True


def surplus(clauses, n):
    best = 10**9
    for mask in range(1, 1 << n):
        V = {i + 1 for i in range(n) if (mask >> i) & 1}
        gamma = sum(bool(vars_of([C]) & V) for C in clauses)
        best = min(best, gamma - len(V))
    return best


def simplify(clauses, v, value):
    satlit = v if value else -v
    falselit = -v if value else v
    out = []
    seen = set()
    for C in clauses:
        if satlit in C:
            continue
        D = tuple(l for l in C if l != falselit)
        if D not in seen:
            seen.add(D)
            out.append(D)
    return out


def canonical_clause(lits):
    return tuple(sorted(lits, key=lambda x: (abs(x), x < 0)))


def dp_eliminate(clauses, v):
    P = [C for C in clauses if v in C]
    Q = [C for C in clauses if -v in C]
    rest = [C for C in clauses if v not in C and -v not in C]
    resolvents = []
    seen = set()
    for A in P:
        for B in Q:
            lits = (set(A) - {v}) | (set(B) - {-v})
            assert not any(-l in lits for l in lits), (A, B, lits)
            R = canonical_clause(lits)
            if R not in seen:
                seen.add(R)
                resolvents.append(R)
    return P, Q, rest + resolvents, resolvents


def sat(clauses, n):
    for bits in product([False, True], repeat=n):
        if all(any(bits[abs(l)-1] if l > 0 else not bits[abs(l)-1] for l in C) for C in clauses):
            return bits
    return None


def main():
    assert len(F) == 8 and len(vars_of(F)) == 6
    assert deficiency(F) == 2
    assert max_def(F) == 2
    assert matching_lean(F)
    assert surplus(F, N) == 2

    counts = {v: [0,0] for v in range(1, N+1)}
    for C in F:
        for l in C:
            counts[abs(l)][0 if l > 0 else 1] += 1
    assert all(counts[v] == [2,2] for v in counts), counts
    assert sat(F, N) == (False, False, False, False, False, False)

    c0 = simplify(F, 2, False)
    c1 = simplify(F, 2, True)
    assert max_def(c0) == 1
    assert max_def(c1) == 1

    P, Q, D, R = dp_eliminate(F, 2)
    assert len(P) == 2 and len(Q) == 2
    assert len(R) == 4 and len(set(R)) == 4
    expected = {
        canonical_clause((3,-4,-5,-6)),
        canonical_clause((3,-4,6)),
        canonical_clause((-1,4,-5,-6)),
        canonical_clause((-1,3,4,6)),
    }
    assert set(R) == expected, R
    assert len(D) == 8 and len(vars_of(D)) == 5
    assert deficiency(D) == 3
    assert max_def(D) == 3

    print('PASS')
    print('base: delta*=2, sigma=2, matching-lean, every variable polarity count=2+2')
    print('cofactors on v=2: delta*=1 and delta*=1')
    print('exact DP projection: 4 distinct non-tautological resolvents, delta*=3')
    print('rank rebound: branch 2->1, merged DP 2->3')


if __name__ == '__main__':
    main()
