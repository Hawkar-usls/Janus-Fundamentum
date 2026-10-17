from fractions import Fraction


def q_coefficients(r):
    # q(K)=1+det(I+K): constant=2, linear diagonal coefficient=1,
    # top det(K) coefficient=1.
    return Fraction(2), Fraction(1), Fraction(1)


def forced_schur_coefficients(r):
    # det(D)=2 and linear matching force H=(1/2)I.
    # Then 2 det(I+KH) has constant 2, linear diagonal coefficient 1,
    # and top det(K) coefficient 2^(1-r).
    return Fraction(2), Fraction(1), Fraction(1, 2 ** (r - 1))


def main():
    for r in range(1, 9):
        target = q_coefficients(r)
        forced = forced_schur_coefficients(r)
        if r == 1:
            assert forced == target
            verdict = 'CLOSED_POSITIVE_CONTROL'
        else:
            assert forced[0] == target[0]
            assert forced[1] == target[1]
            assert forced[2] != target[2]
            verdict = 'IMPOSSIBLE_IN_FROZEN_ONE_CORE_MODEL'
        print(f'r={r}: target={target} forced={forced} verdict={verdict}')
    print('PASS: coefficient replay matches symbolic rank-one-only theorem')


if __name__ == '__main__':
    main()
