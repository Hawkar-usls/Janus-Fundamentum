from itertools import product


def det_bareiss(A):
    A = [list(map(int, row)) for row in A]
    n = len(A)
    if n == 0:
        return 1
    sign = 1
    prev = 1
    for k in range(n - 1):
        if A[k][k] == 0:
            p = next((r for r in range(k + 1, n) if A[r][k] != 0), None)
            if p is None:
                return 0
            A[k], A[p] = A[p], A[k]
            sign *= -1
        pivot = A[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                A[i][j] = (A[i][j] * pivot - A[i][k] * A[k][j]) // prev
        prev = pivot
        for i in range(k + 1, n):
            A[i][k] = 0
        for j in range(k + 1, n):
            A[k][j] = 0
    return sign * A[n - 1][n - 1]


def eval_formula(formula, assignment):
    return all(any((assignment[abs(lit)] if lit > 0 else 1 - assignment[abs(lit)]) for lit in clause) for clause in formula)


def build_occurrence_rank1(formula):
    m = len(formula)
    q = 3 * m
    dim = 3 * m
    M0 = [[0] * dim for _ in range(dim)]
    U = [[0] * dim for _ in range(q)]
    V = [[0] * dim for _ in range(q)]
    groups = {}
    occ = 0
    for cidx, clause in enumerate(formula):
        base = 3 * cidx
        # diagonal ones
        for d in range(3):
            M0[base + d][base + d] = 1
        coords = [(base + 0, base + 1, +1), (base + 1, base + 2, +1), (base + 2, base + 0, -1)]
        for pos, lit in enumerate(clause):
            row, col, clause_sign = coords[pos]
            var = abs(lit)
            groups.setdefault(var, []).append(occ)
            # Entry is clause_sign * f, where f=(1-z) for positive lit and z for negative lit.
            if lit > 0:
                M0[row][col] += clause_sign
                coeff = -clause_sign
            else:
                coeff = clause_sign
            U[occ][row] = coeff
            V[occ][col] = 1
            occ += 1
    return M0, U, V, groups


def augmented_det(M0, U, V, t):
    m = len(M0)
    q = len(t)
    N = m + q
    A = [[0] * N for _ in range(N)]
    for i in range(m):
        for j in range(m):
            A[i][j] = M0[i][j]
    for o in range(q):
        for i in range(m):
            A[i][m + o] = U[o][i]
            A[m + o][i] = -t[o] * V[o][i]
        A[m + o][m + o] = 1 + t[o]
    return det_bareiss(A)


def even_masks(groups, q):
    # Enumerate all s with even parity in every occurrence group.
    for bits in product((0, 1), repeat=q):
        if all(sum(bits[o] for o in occs) % 2 == 0 for occs in groups.values()):
            yield bits


def brute_sat_count(formula):
    vars_ = sorted({abs(l) for c in formula for l in c})
    count = 0
    for vals in product((0, 1), repeat=len(vars_)):
        a = dict(zip(vars_, vals))
        count += int(eval_formula(formula, a))
    return count, len(vars_)


def check(formula):
    M0, U, V, groups = build_occurrence_rank1(formula)
    q = len(U)
    sat_count, n = brute_sat_count(formula)
    total = 0
    chars = 0
    for s in even_masks(groups, q):
        t = [(-1 if b else 1) for b in s]
        total += augmented_det(M0, U, V, t)
        chars += 1
    expected = (2 ** (q - n)) * sat_count
    assert total == expected, (formula, total, expected, sat_count, q, n)
    print(f'clauses={len(formula)} vars={n} occ={q} |E|={chars} #SAT={sat_count} scaled={total} PASS')


def main():
    formulas = [
        [(1, 2, 3)],
        [(1, 2, 3), (-1, 2, -3)],
        [(1, 1, 2), (-1, 2, 3)],
        [(1, -2, 3), (1, 2, 4), (-2, 3, 4)],
    ]
    for f in formulas:
        check(f)
    print('PASS: occurrence-rank1 determinant + even-character projection reproduces scaled #SAT exactly')


if __name__ == '__main__':
    main()
