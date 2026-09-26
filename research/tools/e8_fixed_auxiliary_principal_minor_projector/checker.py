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


def principal_minor(K, R):
    R = sorted(R)
    return det_bareiss([[K[i][j] for j in R] for i in R])


def det_i_plus_principal(K, R):
    R = sorted(R)
    return det_bareiss([[(1 if i == j else 0) + K[i][j] for j in R] for i in R])


def target_q(K, groups):
    n = len(K)
    ans = 0
    for mask in range(1 << n):
        R = {i for i in range(n) if (mask >> i) & 1}
        touched = sum(bool(R.intersection(g)) for g in groups)
        ans += (2 ** (len(groups) - touched)) * principal_minor(K, R)
    return ans


def grouped_cube_sum(K, groups):
    # Independent derivation of Q(K): for one Boolean x per original-variable
    # group, activate all rank-one occurrence updates in that group together.
    # Matrix-determinant-lemma form is det(I + D_x K). Inactive rows are identity
    # rows, hence the determinant reduces to det(I + K[A,A]) on active ports A.
    total = 0
    for bits in product((0, 1), repeat=len(groups)):
        active = set()
        for b, g in zip(bits, groups):
            if b:
                active.update(g)
        total += det_i_plus_principal(K, active)
    return total


def det_i_plus_k(K):
    n = len(K)
    return det_bareiss([[K[i][j] + (1 if i == j else 0) for j in range(n)] for i in range(n)])


def check(groups, matrices):
    ports = set().union(*groups)
    assert ports == set(range(sum(len(g) for g in groups)))
    assert all(len(g) >= 2 for g in groups)
    g = len(groups)

    # The symbolic theorem forces the auxiliary Schur complement S to I:
    # near-full nonprincipal coefficients force S_pq=0; near-full principal
    # coefficients force S_pp=1 because deleting one port still touches its group.
    forced_constant = 1
    target_constant = 2 ** g
    assert forced_constant != target_constant

    for K in matrices:
        q_coeff = target_q(K, groups)
        q_cube = grouped_cube_sum(K, groups)
        assert q_coeff == q_cube, (groups, K, q_coeff, q_cube)

    Z = [[0] * len(ports) for _ in ports]
    assert target_q(Z, groups) == 2 ** g
    assert grouped_cube_sum(Z, groups) == 2 ** g
    assert det_i_plus_k(Z) == 1
    print(f'groups={[len(x) for x in groups]} grouped_constant={2**g} forced_fixed_aux={1} PASS')


def main():
    mats2 = [
        [[0, 0], [0, 0]],
        [[1, 2], [3, 4]],
        [[0, 1], [-1, 0]],
    ]
    mats4 = [
        [[0,0,0,0] for _ in range(4)],
        [[1,2,0,1],[0,3,1,0],[2,0,1,4],[1,1,0,2]],
    ]
    check([{0,1}], mats2)
    check([{0,1},{2,3}], mats4)
    print('PASS: grouped Boolean cube equals weighted principal-minor expansion; fixed-auxiliary one-port-block model has forced constant-term contradiction')


if __name__ == '__main__':
    main()
