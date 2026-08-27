#!/usr/bin/env python3
"""Reverse-prime stress-probe scheduler for JANUS MAD-LAB.

This file does not prove any theorem. It only produces an isolated experimental
schedule and normalized result envelopes for stress testing.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass

LANE = "JANUS_MAD_LAB"
STATUS = "EXPERIMENTAL_NOT_THEOREM"
P_VS_NP = "OPEN"
THEOREM_RUNTIME_HEURISTICS = "FORBIDDEN"


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def reverse_primes(start: int = 937, stop: int = 2) -> list[int]:
    if start < stop:
        raise ValueError("start must be >= stop")
    return [n for n in range(start, stop - 1, -1) if is_prime(n)]


@dataclass(frozen=True)
class ProbeEnvelope:
    N: int
    lane: str = LANE
    status: str = STATUS
    P_VS_NP: str = P_VS_NP
    theorem_runtime_heuristics: str = THEOREM_RUNTIME_HEURISTICS
    proves_intermediate_N: bool = False
    proves_unbounded_totality: bool = False
    automatic_promotion: bool = False


def schedule(limit: int | None = None) -> list[ProbeEnvelope]:
    ps = reverse_primes()
    if limit is not None:
        ps = ps[:limit]
    return [ProbeEnvelope(N=n) for n in ps]


def selftest() -> None:
    ps = reverse_primes(937, 880)
    assert ps[:8] == [937, 929, 919, 911, 907, 887, 883, 881], ps[:8]
    assert all(is_prime(n) for n in ps)
    assert all(a > b for a, b in zip(ps, ps[1:]))
    env = asdict(schedule(1)[0])
    assert env["N"] == 937
    assert env["status"] == STATUS
    assert env["P_VS_NP"] == "OPEN"
    assert env["automatic_promotion"] is False
    print("MAD_LAB_REVERSE_PRIME_SCHEDULE=PASS")
    print(json.dumps([asdict(x) for x in schedule(8)], indent=2))
    print("P_VS_NP=OPEN")


if __name__ == "__main__":
    selftest()
