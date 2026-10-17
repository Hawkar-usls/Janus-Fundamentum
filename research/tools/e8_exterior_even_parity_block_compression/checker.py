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


def local_character_check(max_d=6):
    for d in range(1, max_d + 1):
        even_signs = [t for t in product((-1, 1), repeat=d) if __import__('math').prod(t) == 1]
        assert len(even_signs) == 2 ** (d - 1)
        for mask in range(1 << d):
            coeff = sum(__import__('math').prod(t[j] for j in range(d) if (mask >> j) & 1) for t in even_signs)
            expected = 2 ** (d - 1) if mask in (0, (1 << d) - 1) else 0
            assert coeff == expected, (d, mask, coeff, expected)


def build_occurrence_rank1(formula):
    assert all(len(c) in (2, 3) for c in formula)
    q = sum(len(c) for c in formula)
    dim = q
    M0 = [[0] * dim for _ in range(dim)]
    U = [[0] * dim for _ in range(q)]
    V = [[0] * dim for _ in range(q)]
    groups = {}
    occ = 0
    base = 0
    for clause in formula:
        k = len(clause)
        for d in range(k):
            M0[base + d][base + d] = 1
        if k == 2:
            coords = [(base, base + 1, +1), (base + 1, base, +1)]
        else:
            coords = [(base, base + 1, +1), (base + 1, base + 2, +1), (base + 2, base, -1)]
        for lit, (row, col, clause_sign) in zip(clause, coords):
            var = abs(lit)
            groups.setdefault(var, []).append(occ)
            # Entry is clause_sign*f, f=(1-z) for positive and f=z for negative.
            if lit > 0:
                M0[row][col] += clause_sign
                coeff = -clause_sign
            else:
                coeff = clause_sign
            U[occ][row] = coeff
            V[occ][col] = 1
            occ += 1
        base += k
    return M0, U, V, groups


def exterior_rows(M0, U, V):
    m = len(M0)
    q = len(U)
    N = m + q
    top = [M0[i][:] + [U[o][i] for o in range(q)] for i in range(m)]
    a_rows = []
    b_rows = []
    for o in range(q):
        a = [0] * N
        a[m + o] = 1
        b = [0] * N
        for j in range(m):
            b[j] = -V[o][j]
        b[m + o] = 1
        a_rows.append(a)
        b_rows.append(b)
    return top, a_rows, b_rows


def permutation_sign(p):
    inv = sum(1 for i in range(len(p)) for j in range(i + 1, len(p)) if p[i] > p[j])
    return -1 if inv % 2 else 1


def eval_formula(formula, assignment):
    return all(any(assignment[abs(lit)] if lit > 0 else 1 - assignment[abs(lit)] for lit in clause) for clause in formula)


def brute_sat_count(formula):
    vars_ = sorted({abs(l) for c in formula for l in c})
    return sum(
        int(eval_formula(formula, dict(zip(vars_, bits))))
        for bits in product((0, 1), repeat=len(vars_))
    )


def coherent_block_sum(formula):
    M0, U, V, groups = build_occurrence_rank1(formula)
    top, a_rows, b_rows = exterior_rows(M0, U, V)
    vars_ = sorted(groups)
    grouped_occurrences = [o for v in vars_ for o in groups[v]]
    sigma = permutation_sign(grouped_occurrences)

    total = 0
    for choice in product((0, 1), repeat=len(vars_)):
        bottom = []
        for bit, v in zip(choice, vars_):
            source = b_rows if bit else a_rows
            bottom.extend(source[o] for o in groups[v])
        total += det_bareiss(top + bottom)
    return sigma, total, {v: len(groups[v]) for v in vars_}


def check_formula(formula, require_degree_le_3=False):
    sigma, exterior_sum, degrees = coherent_block_sum(formula)
    if require_degree_le_3:
        assert max(degrees.values()) <= 3, degrees
    sat_count = brute_sat_count(formula)
    assert sigma * exterior_sum == sat_count, (formula, sigma, exterior_sum, sat_count, degrees)
    print(f'clauses={len(formula)} vars={len(degrees)} degrees={sorted(degrees.values())} sigma={sigma:+d} #SAT={sat_count} PASS')


def main():
    local_character_check()

    bounded_controls = [
        [(1, 2, 3), (-1, 2), (-2, 3)],
        # Frozen bounded-occurrence UNSAT witness from the zero-syndrome barrier.
        [(1, 2), (1, -2), (-1, 3), (-3, 4), (-3, -4)],
        [(1, 2), (2, 3), (-1, -3)],
    ]
    for f in bounded_controls:
        check_formula(f, require_degree_le_3=True)

    # General identity control beyond the bounded-occurrence specialization.
    check_formula([(1, 2, 3), (1, -2, -3), (-1, 2, -3), (-1, -2, 3)])

    print('PASS_EXTERIOR_EVEN_PARITY_BLOCK_COMPRESSION')
    print('Even Fourier characters collapse exactly to two coherent blades per variable.')
    print('E8_D1=EMPTY P_VS_NP=OPEN')


if __name__ == '__main__':
    main()
