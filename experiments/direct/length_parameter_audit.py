#!/usr/bin/env python3
"""Audit the parameter mismatch in H116 and the repair used by H124.

H116 compares candidate circuits with n^k while allowing formula length
L_k(n)=n^{d(k)}.  A hypothetical SAT circuit of size L^c then has size
n^{c d(k)}, which need not fit inside n^k even after choosing k: for example
 d(k)=k^2.

H124 measures both the formulas and the circuit budget by the same actual input
length L, eliminating this circular exponent comparison.
"""

from __future__ import annotations

import argparse


def h116_budget(k: int, sat_exponent: int) -> tuple[int, int]:
    length_exponent = k * k
    target_exponent = k
    inherited_sat_exponent = sat_exponent * length_exponent
    return target_exponent, inherited_sat_exponent


def h124_budget(k: int, sat_exponent: int) -> tuple[int, int]:
    # Both exponents are now with respect to the same formula length L.
    return k, sat_exponent


def self_test() -> None:
    sat_exponent = 3
    failures = []
    for k in range(1, 50):
        target, inherited = h116_budget(k, sat_exponent)
        if inherited <= target:
            failures.append(k)
    if failures:
        raise AssertionError(f"unexpected H116 exponent domination: {failures}")

    repaired = []
    for k in range(1, 10):
        target, inherited = h124_budget(k, sat_exponent)
        if k > sat_exponent and inherited < target:
            repaired.append(k)
    if repaired != [4, 5, 6, 7, 8, 9]:
        raise AssertionError(f"unexpected H124 comparison: {repaired}")

    print("JANUS_LENGTH_PARAMETER_AUDIT = PASS")
    print("H116_EXAMPLE_LENGTH_EXPONENT = k^2")
    print("H116_TARGET_EXPONENT = k")
    print("H116_INHERITED_SAT_EXPONENT = 3k^2")
    print("H116_NO_K_CLOSES_THE_IMPLICATION = true")
    print("H124_COMMON_PARAMETER = ACTUAL_FORMULA_LENGTH_L")
    print("H124_K_ABOVE_SAT_EXPONENT_CLOSES_THE_FORMAL_IMPLICATION = true")
    print("CLAIM_BOUNDARY = parameter audit only; no circuit lower bound")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    parser.error("only --self-test is supported")


if __name__ == "__main__":
    raise SystemExit(main())
