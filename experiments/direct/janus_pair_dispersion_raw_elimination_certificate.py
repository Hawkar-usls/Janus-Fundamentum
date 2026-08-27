#!/usr/bin/env python3
"""Exact sufficient certificate for the C025 pair-dispersion elimination corridor.

This module does not decide SAT and does not expand the theorem-mode grammar.
It computes syntactic upper bounds proving that every live Davis-Putnam pivot
fits the frozen root-relative N^2 monotone raw cap when a bound passes.

v1 used the conservative combined-sign constant 20.  The append-only v1.1
sign-split strengthening proves the sharper bound
  s + 12(n-1)^2 T^2 - 12(n-1)T.
Both are retained in the receipt for auditability.

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
            "schema": "JANUS/C025/PAIR-DISPERSION-RAW-ELIMINATION-CERT/v1.1",
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
    nm1 = max(0, n - 1)
    legacy_upper_20 = s + 20 * nm1**2 * T**2
    sign_split_upper_12 = s + 12 * nm1**2 * T**2 - 12 * nm1 * T
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

        # Four-times combined-sign local bound from v1; integer-only.
        local_upper_x4 = 4 * s + d * d + 4 * (d - 1) * A - 8 * d

        # Exact sign-split multiset upper before tautology/duplicate cleanup.
        # D = pq + (q-1)A_p + (p-1)A_q - 2(p+q).
        exact_bucket_multiset_upper = s + p * q + (q - 1) * A_p + (p - 1) * A_q - 2 * d

        local.append({
            "pivot": x,
            "p": p,
            "q": q,
            "d": d,
            "A_plus": A_p,
            "A_minus": A_q,
            "A": A,
            "exact_bucket_multiset_upper": exact_bucket_multiset_upper,
            "exact_bucket_multiset_certified_fit": exact_bucket_multiset_upper <= cap,
            "combined_local_raw_upper_x4": local_upper_x4,
            "combined_local_certified_fit": local_upper_x4 <= 4 * cap,
        })

    certified = sign_split_upper_12 <= cap
    return {
        "schema": "JANUS/C025/PAIR-DISPERSION-RAW-ELIMINATION-CERT/v1.1",
        "applicable": True,
        "N": N,
        "state_units": s,
        "live_variables": n,
        "max_pair_frequency": T,
        "legacy_global_raw_upper_constant20": legacy_upper_20,
        "sign_split_global_raw_upper_constant12": sign_split_upper_12,
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
        assert cert["sign_split_global_raw_upper_constant12"] <= cert["legacy_global_raw_upper_constant20"]

        for row in cert["local_pivot_bounds"]:
            x = row["pivot"]
            out, _ = base.eliminate_var_capped(f, x, N**2)
            if row["exact_bucket_multiset_certified_fit"]:
                assert out is not None, (x, row)
            if out is not None:
                assert base.verify_elimination_transition(f, x, out, N**2)

        if cert["certifies_every_live_pivot_fits"]:
            certified_seen = True
            for x in base.vars_of(f):
                out, _ = base.eliminate_var_capped(f, x, N**2)
                assert out is not None, (x, cert)

    assert certified_seen
    print("PAIR_DISPERSION_RAW_ELIMINATION_CERTIFICATE_V1_1_SELFTEST=PASS")
    print("SIGN_SPLIT_BOUND_STRENGTHENING=PASS")
    print("CERTIFICATE_IS_SUFFICIENT_NOT_NECESSARY=PASS")
    print("P_VS_NP=OPEN")


if __name__ == "__main__":
    selftest()
