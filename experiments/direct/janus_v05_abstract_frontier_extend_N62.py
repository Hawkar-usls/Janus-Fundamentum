#!/usr/bin/env python3
"""Extend the exact v0.5 abstract cap frontier from N=58 through N=62.

PASS at each N is a finite theorem over the frozen abstract overapproximation.
A failure is abstraction OPEN, not automatically an actual CNF counterexample.
"""

from experiments.direct import janus_v05_abstract_frontier_support_mass as A


def clear_caches() -> None:
    A.wmax.cache_clear()
    A.omission_product_max.cache_clear()
    A.support_resolvent_ceiling.cache_clear()
    A.transfer_bounds.cache_clear()


def selftest() -> None:
    previous = 57
    for N in range(58, 63):
        result = A.verify_N(N, previous)
        print(f"ABSTRACT_N{N}_STATUS={result['status']}")
        print(f"ABSTRACT_N{N}_CHECKED_STATES={result['checked_states']}")
        print(f"ABSTRACT_N{N}_CHECKED_TRANSITIONS={result['checked_transitions']}")
        if result['status'] != 'PROVED_FINITE_CAP_AVAILABILITY_BY_EXACT_ABSTRACT_OVERAPPROX':
            print(f"ABSTRACT_N{N}_FIRST_OPEN={result['first_open']}")
            print('ABSTRACT_FAILURE_IS_INCONCLUSIVE_NOT_ACTUAL_COUNTEREXAMPLE')
            raise AssertionError(result)
        print(f"ABSTRACT_N{N}_WORST_RAW_BOUND={result['worst_raw_bound']}")
        assert result['worst_raw_bound'] <= N * N
        previous = N
        clear_caches()
    print('V05_ABSTRACT_FRONTIER_N58_TO_N62=PASS')
    print('THEOREM_RUNTIME_HEURISTICS=FORBIDDEN')
    print('UNBOUNDED_TOTALITY=OPEN')
    print('UNIVERSAL_GPEI=OPEN')
    print('P_VS_NP=OPEN')


if __name__ == '__main__':
    selftest()
