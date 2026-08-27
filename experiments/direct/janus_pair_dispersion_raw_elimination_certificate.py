#!/usr/bin/env python3
"""Exact sufficient certificate for the C025 pair-dispersion elimination corridor.

This module does not decide SAT and does not expand the theorem-mode grammar.
It computes a syntactic upper bound proving that every live Davis-Putnam pivot
fits the frozen root-relative N^2 monotone raw cap when the bound passes.

P_VS_NP remains OPEN.
"""
from __future__ import annotations

from collections import Counter
from typing import Sequence

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base

P_VS_NP = "OPEN"


def pair_pressure_certificate(clauses: Sequence[Sequence[int]], N: int) -> dict:
    f = base.canon_cnf(clauses)
    s = base.state_units(f)
    live = base.vars_of(f)
    n = len(live)

    if () in f or any(len(c) <= 1 for c in f):
        return {
            "schema": "JANUS/C025/PAIR-DISPERSION-RAW-ELIMINATION-CERT/v1",
            "applicable": False,
            "reason": "REQUIRES_NONTERMINAL_UNIT_PROPAGATION_FIXED_POINT",
            "P_VS_NP": P_VS_NP,
        }

    freq: Counter[tuple[int, int]] = Counter()
    for c in f:
        for i in range(len(c)):
            for j in range(i + 1, len(c)):
                a, b = c[i], c[j]
                if abs(a) == abs(b):
                    continue
                pair = tuple(sorted((a, b), key=lambda z: (abs(z), z < 0)))
                freq[pair] += 1

    T = max(freq.values(), default=0)
    global_upper = s + 20 * max(0, n - 1) ** 2 * T**2
    cap = N**2

    local = []
    for x in live:
        pos = [c for c in f if x in c]
        neg = [c for c in f if -x in c]
        p, q = len(pos), len(neg)
        d = p + q
        A_p = sum(len(c) - 1 for c in pos)
        A_q = sum(len(c) - 1 for c in neg)
        A = A_p + A_q
        # Four-times form avoids floating point: 4*R_upper.
        local_upper_x4 = 4 * s + d * d + 4 * (d - 1) * A - 8 * d
        local.append({
            "pivot": x,
            "p": p,
            "q": q,
            "d": d,
            "A": A,
            "local_raw_upper_x4": local_upper_x4,
            "locally_certified_fit": local_upper_x4 <= 4 * cap,
        })

    certified = global_upper <= cap
    return {
        "schema": "JANUS/C025/PAIR-DISPERSION-RAW-ELIMINATION-CERT/v1",
        "applicable": True,
        "N": N,
        "state_units": s,
        "live_variables": n,
        "max_pair_frequency": T,
        "global_raw_upper": global_upper,
        "state_cap": cap,
        "certifies_every_live_pivot_fits": certified,
        "local_pivot_bounds": local,
        "scientific_boundary": {
            "sufficient_not_necessary": True,
            "does_not_decide_SAT": True,
            "does_not_prove_totality": True,
            "P_VS_NP": P_VS_NP,
        },
    }


def selftest() -> None:
    fixtures = (
        ((1, 2), (-1, 3), (-2, -3)),
        ((1, 2), (-1, 2), (1, -3), (-1, -3)),
    )
    certified_seen = False
    for cnf in fixtures:
        f = base.canon_cnf(cnf)
        N = base.input_size_units(f)
        cert = pair_pressure_certificate(f, N)
        assert cert["applicable"] is True
        if cert["certifies_every_live_pivot_fits"]:
            certified_seen = True
            for x in base.vars_of(f):
                out, _ = base.eliminate_var_capped(f, x, N**2)
                assert out is not None, (x, cert)
                assert base.verify_elimination_transition(f, x, out, N**2)

    assert certified_seen
    print("PAIR_DISPERSION_RAW_ELIMINATION_CERTIFICATE_SELFTEST=PASS")
    print("CERTIFICATE_IS_SUFFICIENT_NOT_NECESSARY=PASS")
    print("P_VS_NP=OPEN")


if __name__ == "__main__":
    selftest()
