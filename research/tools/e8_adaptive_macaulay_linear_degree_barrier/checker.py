#!/usr/bin/env python3
from math import comb, floor


def macaulay_dim(n, d):
    return sum(comb(n, j) for j in range(d + 1))


def elementary_binomial_lower_bound(n, d):
    # binom(n,d) >= (n/d)^d, checked exactly after cross multiplication
    # via product inequality (n-i)/(d-i) >= n/d for i=0,...,d-1.
    lhs_num = 1
    lhs_den = 1
    for i in range(d):
        assert (n - i) * d >= n * (d - i)
        lhs_num *= (n - i)
        lhs_den *= (d - i)
    assert lhs_num // lhs_den == comb(n, d)
    return comb(n, d)


def main():
    # Exact finite regression at several fixed positive linear degree fractions.
    for den in (4, 5, 8, 10):
        alpha = 1 / den
        previous = None
        for n in (40, 80, 120, 160, 200):
            d = floor(n / den)
            D = macaulay_dim(n, d)
            b = elementary_binomial_lower_bound(n, d)
            assert D >= b
            # Since n/d = den on these chosen multiples, binom(n,d) >= den^d.
            assert b >= den ** d
            if previous is not None:
                # Exponential lower bound should strictly grow on these controls.
                assert b > previous
            previous = b
        print(f"alpha=1/{den}: verified D(n,floor(alpha n)) >= {den}^floor(n/{den})")

    # Explicitly contrast constant degree with linear degree.
    for n in (50, 100, 200):
        d3 = macaulay_dim(n, 3)
        assert d3 == 1 + n + comb(n, 2) + comb(n, 3)
        dlin = macaulay_dim(n, n // 10)
        assert dlin >= 10 ** (n // 10)
        print(f"n={n}: degree3_dim={d3}; degree_n/10_dim>={10 ** (n//10)}")

    print("PASS E8 adaptive Macaulay linear-degree exponential barrier")


if __name__ == "__main__":
    main()
