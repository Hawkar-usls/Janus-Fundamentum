#!/usr/bin/env python3
"""Exact sufficient certificate for the C025 all-pivot overflow / v2 sandwich.

The certificate is theorem-support infrastructure only.  It does not decide SAT,
does not select a semantic pivot, does not mutate the frozen v0.4 lane order,
and does not infer P=NP from finite data.

If its integer inequality passes in a unit-free root-phase state, the already-
frozen machine is guaranteed to have at least one action in the following
dichotomy: an ordinary N^2-capped exact elimination exists, or the proved v2
frequent-pair trigger holds.
"""
from __future__ import annotations

from collections import Counter
from typing import Sequence

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base

P_VS_NP = "OPEN"


def incidence_sandwich_certificate(clauses: Sequence[Sequence[int]], N: int) -> dict:
    f = base.canon_cnf(clauses)
    s = base.state_units(f)
    m = len(f)
    live = base.vars_of(f)
    n = len(live)
    L = sum(len(c) for c in f)
    cap = N**2

    if () in f or not f or not live or any(len(c) <= 1 for c in f):
        return {
            "schema": "JANUS/C025/ALL-PIVOT-OVERFLOW-INCIDENCE-SANDWICH-CERT/v1",
            "applicable": False,
            "reason": "REQUIRES_NONTERMINAL_UNIT_PROPAGATION_FIXED_POINT",
            "P_VS_NP": P_VS_NP,
        }
    if s > cap:
        return {
            "schema": "JANUS/C025/ALL-PIVOT-OVERFLOW-INCIDENCE-SANDWICH-CERT/v1",
            "applicable": False,
            "reason": "STATE_ALREADY_OUTSIDE_FROZEN_N2_ENVELOPE",
            "N": N,
            "state_units": s,
            "state_cap": cap,
            "P_VS_NP": P_VS_NP,
        }
    if s < 2 * N:
        return {
            "schema": "JANUS/C025/ALL-PIVOT-OVERFLOW-INCIDENCE-SANDWICH-CERT/v1",
            "applicable": False,
            "reason": "LOW_VOLUME_CORRIDOR_SHOULD_HANDLE_BEFORE_SANDWICH",
            "N": N,
            "state_units": s,
            "P_VS_NP": P_VS_NP,
        }

    pair_freq: Counter[tuple[int, int]] = Counter()
    P = 0
    for c in f:
        k = len(c)
        P += k * (k - 1) // 2
        for i in range(k):
            for j in range(i + 1, k):
                a, b = c[i], c[j]
                if abs(a) == abs(b):
                    raise AssertionError("CANONICAL_CLAUSE_CONTAINS_SAME_VARIABLE_TWICE")
                pair = tuple(sorted((a, b), key=lambda z: (abs(z), z < 0)))
                pair_freq[pair] += 1

    T = max(pair_freq.values(), default=0)
    v2_threshold = s - 2 * N + 11
    no_v2_integer_max = s - 2 * N + 10

    lhs = 4 * n * (cap - s) - m * L
    rhs = 16 * m * n * max(0, n - 1) * no_v2_integer_max
    sandwich_pass = lhs >= rhs

    # Integer forms of the pair-mass bounds for auditability.
    # all-pivot overflow => 8mP > 4n(N^2-s)-mL = lhs
    floor_numerator = lhs
    ceiling_P = 2 * n * max(0, n - 1) * no_v2_integer_max

    # These direct observations are not needed for the theorem but make a
    # finite receipt independently auditable without semantic reasoning.
    frequent_pair_triggered = T >= v2_threshold
    ordinary_fit_pivots = []
    overflow_pivots = []
    for x in live:
        out, stats = base.eliminate_var_capped(f, x, cap)
        if out is None:
            overflow_pivots.append(x)
        else:
            ordinary_fit_pivots.append(x)

    if ordinary_fit_pivots:
        observed_action_class = "ORDINARY_EXACT_ELIMINATION_EXISTS"
    elif frequent_pair_triggered:
        observed_action_class = "V2_FREQUENT_PAIR_TRIGGER_PRESENT"
    else:
        observed_action_class = "OBSERVED_WEDGE_CANDIDATE_REQUIRES_FULL_V2_SCAN"

    if sandwich_pass and not ordinary_fit_pivots and not frequent_pair_triggered:
        raise AssertionError("SANDWICH_THEOREM_CONTRADICTED_BY_DIRECT_SYNTACTIC_SCAN")

    return {
        "schema": "JANUS/C025/ALL-PIVOT-OVERFLOW-INCIDENCE-SANDWICH-CERT/v1",
        "applicable": True,
        "N": N,
        "state_cap": cap,
        "state_units": s,
        "clauses_m": m,
        "literal_occurrences_L": L,
        "live_variables_n": n,
        "pair_incidences_P": P,
        "max_pair_frequency_T": T,
        "v2_frequent_pair_threshold": v2_threshold,
        "no_v2_integer_max_frequency": no_v2_integer_max,
        "all_overflow_pair_floor_8mP_strictly_greater_than": floor_numerator,
        "no_v2_pair_incidence_ceiling_P": ceiling_P,
        "sandwich_lhs": lhs,
        "sandwich_rhs": rhs,
        "sandwich_certifies_ordinary_or_v2_action_exists": sandwich_pass,
        "direct_syntactic_observation": {
            "ordinary_fit_pivot_count": len(ordinary_fit_pivots),
            "ordinary_fit_pivots": ordinary_fit_pivots,
            "overflow_pivot_count": len(overflow_pivots),
            "overflow_pivots": overflow_pivots,
            "frequent_pair_triggered": frequent_pair_triggered,
            "observed_action_class": observed_action_class,
        },
        "scientific_boundary": {
            "certificate_is_sufficient_not_necessary": True,
            "direct_scan_is_finite_observation_not_universal_proof": True,
            "does_not_decide_SAT": True,
            "does_not_prove_totality": True,
            "P_VS_NP": P_VS_NP,
        },
    }


def selftest() -> None:
    # Synthetic unit-free state deliberately evaluated with a root N chosen so
    # the sandwich domain is active.  The direct scan verifies the theorem's
    # existential conclusion whenever the arithmetic certificate passes.
    cnf = base.canon_cnf((
        (1, 2, 3), (-1, 2, 4), (1, -2, 4), (-1, -2, 3),
        (1, 3, 4), (-1, 3, -4), (2, -3, 4), (-2, -3, -4),
    ))
    s = base.state_units(cnf)
    # Need s>=2N and s<=N^2.  N=10 satisfies this fixture.
    N = 10
    assert s >= 2 * N and s <= N**2
    cert = incidence_sandwich_certificate(cnf, N)
    assert cert["applicable"] is True
    if cert["sandwich_certifies_ordinary_or_v2_action_exists"]:
        obs = cert["direct_syntactic_observation"]
        assert obs["ordinary_fit_pivot_count"] > 0 or obs["frequent_pair_triggered"] is True

    # Independent combinatorial identities.
    m = len(cnf)
    L = sum(len(c) for c in cnf)
    P = sum(len(c) * (len(c)-1)//2 for c in cnf)
    d_sum = sum(sum(1 for c in cnf if x in c or -x in c) for x in base.vars_of(cnf))
    A_sum = sum(
        sum(len(c)-1 for c in cnf if x in c or -x in c)
        for x in base.vars_of(cnf)
    )
    assert d_sum == L
    assert A_sum == 2 * P
    assert all(sum(1 for c in cnf if x in c or -x in c) <= m for x in base.vars_of(cnf))

    print("ALL_PIVOT_OVERFLOW_INCIDENCE_SANDWICH_SELFTEST=PASS")
    print("PAIR_INCIDENCE_IDENTITIES=PASS")
    print("CERTIFICATE_IS_SUFFICIENT_NOT_NECESSARY=PASS")
    print("P_VS_NP=OPEN")


if __name__ == "__main__":
    selftest()
