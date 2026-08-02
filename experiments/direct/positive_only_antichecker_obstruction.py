#!/usr/bin/env python3
"""Finite audit for the positive-only anti-checker obstruction.

This executable checks the elementary finite statement used by C016. It is not
an asymptotic circuit lower bound and does not resolve P versus NP.
"""

from __future__ import annotations

import argparse
from collections.abc import Callable, Iterable

Bit = int
Classifier = Callable[[Bit], bool]


def all_accepting(_: Bit) -> bool:
    return True


def membership_classifier(accepted: frozenset[Bit]) -> Classifier:
    return lambda x: x in accepted


def false_negatives(classifier: Classifier, positives: Iterable[Bit]) -> list[Bit]:
    return [x for x in positives if not classifier(x)]


def false_positives(
    classifier: Classifier, domain: Iterable[Bit], language: frozenset[Bit]
) -> list[Bit]:
    return [x for x in domain if classifier(x) and x not in language]


def is_sound(
    classifier: Classifier, domain: Iterable[Bit], language: frozenset[Bit]
) -> bool:
    return not false_positives(classifier, domain, language)


def self_test() -> None:
    domain = tuple(range(8))
    language = frozenset({1, 3, 4, 6})
    positive_test_set = frozenset({1, 4, 6})

    if not positive_test_set <= language:
        raise AssertionError("fixture test set must contain positive examples only")
    if language == frozenset(domain):
        raise AssertionError("fixture language must be nontrivial")

    top_false_negatives = false_negatives(all_accepting, positive_test_set)
    top_false_positives = false_positives(all_accepting, domain, language)

    if top_false_negatives:
        raise AssertionError("all-accepting classifier cannot have a false negative")
    if not top_false_positives:
        raise AssertionError("all-accepting classifier must fail on a nontrivial language")

    hardcoded = membership_classifier(positive_test_set)
    if not is_sound(hardcoded, domain, language):
        raise AssertionError("membership in positive examples must be sound")
    if false_negatives(hardcoded, positive_test_set):
        raise AssertionError("hardcoded membership accepts every listed positive")

    print("JANUS_POSITIVE_ONLY_ANTICHECKER_OBSTRUCTION = PASS")
    print(f"DOMAIN_SIZE = {len(domain)}")
    print(f"POSITIVE_TESTS = {len(positive_test_set)}")
    print(f"ALL_ACCEPTING_FALSE_NEGATIVES = {len(top_false_negatives)}")
    print(f"ALL_ACCEPTING_FALSE_POSITIVES = {len(top_false_positives)}")
    print("HARDCODED_POSITIVE_MEMBERSHIP_SOUND = true")
    print("CLAIM_BOUNDARY = finite audit only; no asymptotic lower bound")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.self_test:
        parser.error("use --self-test")
    self_test()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
