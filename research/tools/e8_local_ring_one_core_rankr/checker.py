from itertools import product


def det2(M, mod):
    return (M[0][0] * M[1][1] - M[0][1] * M[1][0]) % mod


def target(K, mod):
    Iplus = [[(K[i][j] + (1 if i == j else 0)) % mod for j in range(2)] for i in range(2)]
    return (1 + det2(Iplus, mod)) % mod


def candidate(K, S, mod):
    return det2([[(K[i][j] + S[i][j]) % mod for j in range(2)] for i in range(2)], mod)


def exhaustive_normalized_control(mod):
    vals = range(mod)
    Ks = [((a,b),(c,d)) for a,b,c,d in product(vals, repeat=4)]
    count = 0
    for s00,s01,s10,s11 in product(vals, repeat=4):
        S = ((s00,s01),(s10,s11))
        count += 1
        if all(candidate(K, S, mod) == target(K, mod) for K in Ks):
            raise AssertionError((mod, S))
    print(f'mod={mod}: checked {count} normalized S matrices; no identity PASS')


def coefficient_forcing_control(mod):
    # Near-full coefficients in det(K+S) force S_01=S_10=0 and S_00=S_11=1.
    # Then K=0 gives det(S)=1 while target constant is 2 mod m.
    S = ((1 % mod, 0), (0, 1 % mod))
    lhs = det2(S, mod)
    rhs = 2 % mod
    assert lhs != rhs, (mod, lhs, rhs)
    print(f'mod={mod}: forced S=I has constant {lhs}, target {rhs}; contradiction PASS')


def main():
    for mod in (2, 3, 4):
        exhaustive_normalized_control(mod)
        coefficient_forcing_control(mod)
    print('PASS: finite local-ring controls agree with the symbolic one-core rank-r barrier')


if __name__ == '__main__':
    main()
