#!/usr/bin/env python3
"""Exact-list SAT-sound cover for positive anti-checker lists.

For any finite list T of distinct satisfiable L-bit formula encodings, a Boolean
circuit can accept exactly the strings in T by OR-composing equality tests.  The
circuit is globally SAT-sound and has O(|T| L) gates under a standard binary
gate accounting.  This is a necessary lower bound on every H124 list.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass


@dataclass(frozen=True)
class ExactListCover:
    length: int
    accepted: frozenset[str]

    def __post_init__(self) -> None:
        if self.length < 1:
            raise ValueError("length must be positive")
        if any(len(item) != self.length or set(item) - {"0", "1"} for item in self.accepted):
            raise ValueError("every item must be a binary string of the declared length")

    def evaluate(self, candidate: str) -> bool:
        if len(candidate) != self.length or set(candidate) - {"0", "1"}:
            raise ValueError("candidate is outside the fixed input domain")
        return candidate in self.accepted

    def gate_upper_bound(self) -> int:
        # Per word: at most L input-negations/XNOR selectors plus L-1 AND gates;
        # then at most |T|-1 OR gates.  The loose 3|T|L bound is encoding-safe.
        return 3 * len(self.accepted) * self.length


def necessary_distinct_list_size(length: int, exponent: int) -> int:
    if length < 2 or exponent < 1:
        raise ValueError("length must be at least two and exponent positive")
    budget = length**exponent
    # Need 3*m*L > L^k, hence m > L^(k-1)/3.
    return budget // (3 * length) + 1


def self_test() -> None:
    positive = frozenset({"000101", "011000", "101011", "111100"})
    cover = ExactListCover(length=6, accepted=positive)
    for word in positive:
        if not cover.evaluate(word):
            raise AssertionError("listed positive word was rejected")
    for word in ("000000", "010101", "111111"):
        if word not in positive and cover.evaluate(word):
            raise AssertionError("unlisted word was accepted")
    if cover.gate_upper_bound() != 72:
        raise AssertionError("unexpected gate bound")
    if necessary_distinct_list_size(16, 3) != 86:
        raise AssertionError("incorrect threshold arithmetic")

    print("JANUS_EXACT_LIST_SOUND_COVER = PASS")
    print("COVER = exact membership in the positive list")
    print("GLOBAL_SAT_SOUNDNESS = follows because every accepted word is listed SAT")
    print("GATE_UPPER_BOUND = 3 * distinct_formulas * L")
    print("H124_NECESSARY_SIZE = more than L^(k-1)/3 distinct formulas")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--length", type=int)
    parser.add_argument("--exponent", type=int)
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.length is not None and args.exponent is not None:
        print(necessary_distinct_list_size(args.length, args.exponent))
        return 0
    parser.error("use --self-test or both --length and --exponent")


if __name__ == "__main__":
    raise SystemExit(main())
