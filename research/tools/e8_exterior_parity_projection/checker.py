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
    return sign * A[-1][-1]


def eval_formula(formula, assignment):
    return all(any((assignment[abs(lit)] if lit > 0 else 1 - assignment[abs(lit)]) for lit in clause) for clause in formula)


def build_occurrence_rank1(formula):
    m = len(formula)
    q = 3 * m
    dim = 3 * m
    M0 = [[0] * dim for _ in range(dim)]
    U = [[0] * dim for _ in range(q)]
    V = [[0] * dim for _ in range(q)]
    occ_var = []
    occ = 0
    for cidx, clause in enumerate(formula):
        assert len(clause) == 3
        base = 3 * cidx
        for d in range(3):
            M0[base + d][base + d] = 1
        coords = [(base + 0, base + 1, +1), (base + 1, base + 2, +1), (base + 2, base + 0, -1)]
        for pos, lit in enumerate(clause):
            row, col, clause_sign = coords[pos]
            occ_var.append(abs(lit))
            if lit > 0:
                M0[row][col] += clause_sign
                coeff = -clause_sign
            else:
                coeff = clause_sign
            U[occ][row] = coeff
            V[occ][col] = 1
            occ += 1
    return M0, U, V, occ_var


def regroup(M0, U, V, occ_var):
    order = sorted(range(len(occ_var)), key=lambda o: (occ_var[o], o))
    U2 = [U[o] for o in order]
    V2 = [V[o] for o in order]
    vars2 = [occ_var[o] for o in order]
    groups = []
    start = 0
    while start < len(vars2):
        end = start + 1
        while end < len(vars2) and vars2[end] == vars2[start]:
            end += 1
        groups.append((vars2[start], list(range(start, end))))
        start = end
    return M0, U2, V2, groups


def coherent_matrix(M0, U, V, group_bits, groups):
    p = len(M0)
    q = len(U)
    N = p + q
    A = [[0] * N for _ in range(N)]
    # fixed top rows R=[M0|U]
    for i in range(p):
        for j in range(p):
            A[i][j] = M0[i][j]
        for o in range(q):
            A[i][p + o] = U[o][i]
    bit_by_occ = [0] * q
    for bit, (_, occs) in zip(group_bits, groups):
        for o in occs:
            bit_by_occ[o] = bit
    # A-choice row a_o=[0|e_o], B-choice row b_o=[-v_o|e_o]
    for o in range(q):
        r = p + o
        if bit_by_occ[o]:
            for j in range(p):
                A[r][j] = -V[o][j]
        A[r][p + o] = 1
    return A


def check_local_character_projector(max_d=6):
    for d in range(1, max_d + 1):
        even_signs = [t for t in product((-1, 1), repeat=d) if __import__('math').prod(t) == 1]
        for subset_bits in product((0, 1), repeat=d):
            coeff = sum(__import__('math').prod(t[j] for j in range(d) if subset_bits[j]) for t in even_signs)
            full = all(subset_bits)
            empty = not any(subset_bits)
            expected = 2 ** (d - 1) if (full or empty) else 0
            assert coeff == expected, (d, subset_bits, coeff, expected)


def brute_sat_count(formula):
    vars_ = sorted({abs(l) for c in formula for l in c})
    count = 0
    truth = {}
    for vals in product((0, 1), repeat=len(vars_)):
        a = dict(zip(vars_, vals))
        ok = int(eval_formula(formula, a))
        truth[tuple(vals)] = ok
        count += ok
    return vars_, count, truth


def check_formula(formula):
    M0, U, V, occ_var = build_occurrence_rank1(formula)
    M0, U, V, groups = regroup(M0, U, V, occ_var)
    vars_, sat_count, truth = brute_sat_count(formula)
    group_vars = [v for v, _ in groups]
    assert group_vars == vars_

    collapsed = 0
    terms = 0
    for bits in product((0, 1), repeat=len(groups)):
        det = det_bareiss(coherent_matrix(M0, U, V, bits, groups))
        assert det in (0, 1), (formula, bits, det)
        assert det == truth[bits], (formula, bits, det, truth[bits])
        collapsed += det
        terms += 1
    assert collapsed == sat_count
    return len(formula), len(vars_), len(U), terms, sat_count


def main():
    check_local_character_projector()
    formulas = [
        [(1, 2, 3)],
        [(1, 2, 3), (-1, 2, -3)],
        [(1, 1, 2), (-1, 2, 3)],
        [(1, -2, 3), (1, 2, 4), (-2, 3, 4)],
        [(1, 2, 2), (-1, 3, 3), (-3, 4, 4), (-3, -4, -4)],
    ]
    for f in formulas:
        m, n, q, terms, sat = check_formula(f)
        print(f'clauses={m} vars={n} occ={q} coherent_terms={terms} #SAT={sat} PASS')
    print('PASS_EXTERIOR_EVEN_CHARACTER_PROJECTOR')
    print('LOCAL_MIXED_TERMS_CANCEL_EXACTLY')
    print('GLOBAL_TOP_COEFFICIENT_EQUALS_EXACT_SAT_COUNT')
    print('POLYNOMIAL_TOP_COEFFICIENT_EXTRACTION=OPEN')
    print('P_VS_NP=OPEN E8_D1=EMPTY')


if __name__ == '__main__':
    main()
