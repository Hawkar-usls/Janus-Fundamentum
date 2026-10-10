#!/usr/bin/env python3
from __future__ import annotations

from itertools import product


def phi(edges: int, attachments: list[int]) -> int:
    assert all(a >= 1 for a in attachments)
    return edges + sum(a - 1 for a in attachments)


def contract_path_state(edges: int, attachments: list[int], i: int) -> tuple[int, list[int]]:
    """Contract adjacent supernodes i and i+1 of one coherence path."""
    assert 0 <= i < len(attachments) - 1
    assert edges == len(attachments) - 1
    out = attachments[:i] + [attachments[i] + attachments[i + 1]] + attachments[i + 2:]
    return edges - 1, out


def exhaustive(d: int) -> int:
    # State is a composition of d positive attachment counts in path order.
    # Every such state is reachable by some sequence of adjacent contractions.
    checked = 0
    def rec(prefix: list[int], remaining: int) -> None:
        nonlocal checked
        if remaining == 0:
            if not prefix:
                return
            edges = len(prefix) - 1
            assert sum(prefix) == d
            assert phi(edges, prefix) == d - 1
            for i in range(len(prefix) - 1):
                e2, a2 = contract_path_state(edges, prefix, i)
                assert phi(e2, a2) == phi(edges, prefix)
                checked += 1
            return
        for x in range(1, remaining + 1):
            rec(prefix + [x], remaining - x)
    rec([], d)
    return checked


def main() -> None:
    total = 0
    for d in range(1, 11):
        total += exhaustive(d)
    print(f"EXHAUSTIVE_COMPOSITION_STATES_D_LE_10 = PASS")
    print(f"ADJACENT_CONTRACTIONS_CHECKED = {total}")
    print("PHI_X = XOR_PATH_EDGES + FANOUT_EXCESS")
    print("PHI_X_INITIAL = d-1")
    print("ONE_CONTRACTION_DELTA = (-1) + (+1) = 0")
    print("LOCAL_XOR_PATH_SUBSTITUTION_STRICT_PROGRESS = FALSIFIED")
    print("D1 = EMPTY")
    print("P_VS_NP = OPEN")


if __name__ == "__main__":
    main()
