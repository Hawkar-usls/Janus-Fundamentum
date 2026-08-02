#!/usr/bin/env python3
"""Compact diagnostic wrapper for the historical novelty audit."""

from __future__ import annotations

import traceback

from janus_tear_gt_novel_branch_audit import audit


def self_test() -> None:
    failures = []
    for n in range(4, 9):
        try:
            data = audit(n)
            print(
                f"NOVEL_DEBUG n={n} PASS calls={data['calls']} "
                f"max_novelty={data['maximum_novelty']} "
                f"target={data['target_level']} "
                f"distinct={data['first_target_distinct_restrictions']}"
            )
        except Exception as error:  # diagnostic artifact intentionally broad
            text = "".join(
                traceback.format_exception(type(error), error, error.__traceback__)
            )
            tail = " | ".join(line.strip() for line in text.splitlines()[-8:])
            failures.append((n, type(error).__name__, str(error), tail))
            print(f"NOVEL_DEBUG n={n} FAILURE type={type(error).__name__}")
            print(f"NOVEL_DEBUG message={error!r}")
            print(f"NOVEL_DEBUG traceback_tail={tail}")
            break

    print(f"NOVEL_DEBUG failures={failures}")
    print("claim_boundary = diagnostic wrapper; a failure is data, not a theorem")


if __name__ == "__main__":
    self_test()
