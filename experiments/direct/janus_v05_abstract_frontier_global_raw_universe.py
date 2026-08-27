#!/usr/bin/env python3
"""Append-only v2 transfer for the JANUS v0.5 finite abstract verifier.

This module does NOT modify runtime semantics and does NOT rewrite the N57
verifier used as frozen evidence.  It strengthens only theorem-side abstract
resource accounting by adding the global raw signed-clause-universe bound.
"""

from functools import lru_cache

from experiments.direct import janus_v05_abstract_frontier_support_mass as A

P_VS_NP = "OPEN"
THEOREM_RUNTIME_HEURISTICS = "FORBIDDEN"


@lru_cache(maxsize=None)
def transfer_bounds_global(n: int, m: int, L: int, d: int, p: int, q: int) -> tuple[int, int, int, int]:
    assert p + q == d
    r = n - 1
    c = m - d
    retained_L_cap = min(c * r, max(0, L - 2 * d))

    if p == 0 or q == 0:
        K = min(c, 3 ** r)
        raw_local = 1 + c + retained_L_cap
        raw_global = 1 + K + A.wmax(r, K)
        return min(raw_local, raw_global), K, min(retained_L_cap, A.wmax(r, K)), 0

    R = A.support_resolvent_ceiling(n, m, d, p, q)
    if d == m:
        R = min(R, min(p, q))
    elif d == m - 1:
        R = min(R, A.near_full_resolvent_ceiling(m, p, q))

    # All retained clauses and distinct resolvents share ONE raw set/universe.
    K = min(c + R, 3 ** r)
    m_out = K
    k = max(p, q)

    L_transport = k * (L - d) - 2 * (k - 1) * c
    L_support_separate = retained_L_cap + A.wmax(r, R)
    L_global = A.wmax(r, K)
    L_out = max(0, min(L_transport, L_support_separate, L_global, m_out * r))

    raw_support_separate = 1 + c + retained_L_cap + R + A.wmax(r, R)
    raw_transport = 1 + c + p * q + max(0, L_transport)
    raw_global = 1 + K + L_global
    raw = min(raw_support_separate, raw_transport, raw_global)
    return raw, m_out, L_out, R


def activate() -> None:
    """Install stronger theorem-side transfer into the imported abstract checker."""
    A.transfer_bounds = transfer_bounds_global


def clear_caches() -> None:
    transfer_bounds_global.cache_clear()
    A.wmax.cache_clear()
    A.omission_product_max.cache_clear()
    A.support_resolvent_ceiling.cache_clear()


def verify_N58_open_repair() -> None:
    raw, mout, Lout, R = transfer_bounds_global(7, 75, 343, 49, 22, 27)
    assert R == 594, R
    assert mout == 620, mout
    assert A.wmax(6, 620) == 2676
    assert raw == 3297, raw
    assert raw < 58 * 58
    assert Lout <= 2676
    print('GLOBAL_RAW_N58_REPAIR_R=594')
    print('GLOBAL_RAW_N58_REPAIR_K=620')
    print('GLOBAL_RAW_N58_REPAIR_WMAX=2676')
    print('GLOBAL_RAW_N58_REPAIR_RAW=3297')
    print('GLOBAL_RAW_N58_LOCAL_REPAIR=PASS')


def selftest() -> None:
    verify_N58_open_repair()
    activate()
    result = A.verify_N(58, 57)
    print(f"GLOBAL_RAW_ABSTRACT_N58_STATUS={result['status']}")
    print(f"GLOBAL_RAW_ABSTRACT_N58_CHECKED_STATES={result['checked_states']}")
    print(f"GLOBAL_RAW_ABSTRACT_N58_CHECKED_TRANSITIONS={result['checked_transitions']}")
    if result['status'] != 'PROVED_FINITE_CAP_AVAILABILITY_BY_EXACT_ABSTRACT_OVERAPPROX':
        print(f"GLOBAL_RAW_ABSTRACT_N58_FIRST_OPEN={result['first_open']}")
        raise AssertionError(result)
    print(f"GLOBAL_RAW_ABSTRACT_N58_WORST_RAW={result['worst_raw_bound']}")
    print('GLOBAL_RAW_ABSTRACT_N58=PASS')
    print('THEOREM_RUNTIME_HEURISTICS=FORBIDDEN')
    print('UNBOUNDED_TOTALITY=OPEN')
    print('P_VS_NP=OPEN')


if __name__ == '__main__':
    selftest()
