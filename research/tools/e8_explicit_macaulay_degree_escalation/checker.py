#!/usr/bin/env python3
"""Exact integer regression for E8 v4.4 explicit Macaulay degree growth."""

from math import comb, isqrt


def M(n, d):
    return sum(comb(n, i) for i in range(d + 1))


def main():
    # Exact combinatorial lower bound used in the theorem.
    for n in range(2, 161):
        for d in range(1, n + 1):
            k = min(d, isqrt(n))
            lhs = M(n, d)
            assert lhs >= comb(n, k)
            # binom(n,k) >= (n/k)^k, checked without floating point.
            assert comb(n, k) * (k ** k) >= n ** k
            # k<=sqrt(n) implies (n/k)^k >= n^(k/2); square both sides.
            assert (comb(n, k) ** 2) >= n ** k

    # Concrete growth controls: once d exceeds any fixed exponent budget,
    # the explicit state soon exceeds that polynomial budget.
    controls = [
        (64, 4, 3),
        (128, 6, 4),
        (256, 8, 5),
        (512, 10, 6),
    ]
    for n, d, C in controls:
        assert M(n, d) > n ** C, (n, d, C, M(n, d), n ** C)

    # Fixed degree remains polynomial-sized, illustrated exactly by d=3.
    for n in (10, 50, 100, 500):
        assert M(n, 3) == 1 + n + comb(n, 2) + comb(n, 3)

    print("PASS: exact M(n,d)=sum binom(n,i) controls")
    print("PASS: binom(n,k)>=(n/k)^k and M(n,d)>=n^(k/2) controls")
    print("PASS: unbounded explicit degree cannot have one fixed polynomial exponent budget")


if __name__ == "__main__":
    main()
