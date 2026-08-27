#!/usr/bin/env python3
"""Retry/extend N58..N62 with the append-only global raw-universe transfer."""

from experiments.direct import janus_v05_abstract_frontier_support_mass as A
from experiments.direct import janus_v05_abstract_frontier_global_raw_universe as G


def selftest() -> None:
    G.verify_N58_open_repair()
    G.activate()
    previous = 57
    for N in range(58, 63):
        result = A.verify_N(N, previous)
        print(f"GLOBAL_RAW_N{N}_STATUS={result['status']}")
        print(f"GLOBAL_RAW_N{N}_CHECKED_STATES={result['checked_states']}")
        print(f"GLOBAL_RAW_N{N}_CHECKED_TRANSITIONS={result['checked_transitions']}")
        if result['status'] != 'PROVED_FINITE_CAP_AVAILABILITY_BY_EXACT_ABSTRACT_OVERAPPROX':
            print(f"GLOBAL_RAW_N{N}_FIRST_OPEN={result['first_open']}")
            print('ABSTRACT_FAILURE_IS_INCONCLUSIVE_NOT_ACTUAL_COUNTEREXAMPLE')
            raise AssertionError(result)
        print(f"GLOBAL_RAW_N{N}_WORST_RAW={result['worst_raw_bound']}")
        previous = N
        G.clear_caches()
        G.activate()
    print('V05_GLOBAL_RAW_ABSTRACT_FRONTIER_N58_TO_N62=PASS')
    print('THEOREM_RUNTIME_HEURISTICS=FORBIDDEN')
    print('UNBOUNDED_TOTALITY=OPEN')
    print('UNIVERSAL_GPEI=OPEN')
    print('P_VS_NP=OPEN')


if __name__ == '__main__':
    selftest()
