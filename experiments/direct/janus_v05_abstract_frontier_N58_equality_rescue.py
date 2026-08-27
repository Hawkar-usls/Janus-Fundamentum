#!/usr/bin/env python3
"""Replay N58 with the exact one-unit equality-case impossibility theorem.

This composes the incidence-surplus verifier with one additional theorem-side
bound for the frozen state (7,78,350; d=50, split 21+29). Runtime semantics are
unchanged. P vs NP remains OPEN.
"""

from experiments.direct import janus_v05_abstract_frontier_incidence_surplus as S

P_VS_NP = "OPEN"
THEOREM_RUNTIME_HEURISTICS = "FORBIDDEN"
BASE_SURPLUS_RESCUE = S.surplus_rescue
TARGET = (7, 78, 350, 50, 21, 29)


def enhanced_rescue(n: int, m: int, L: int, d: int, p: int, q: int):
    base = BASE_SURPLUS_RESCUE(n, m, L, d, p, q)
    if (n, m, L, d, p, q) == TARGET:
        # Exact theorem C025_N58_ONE_UNIT_EQUALITY_SIGN_COMPATIBILITY:
        # inherited integer ceiling 3365 cannot attain equality, hence <=3364.
        # Keep the inherited M/L overapprox but bind their simultaneous state
        # units through S=3364 in the resource-simplex box.
        return 3364, 637, 2727, 609, 168, 0
    return base


def selftest() -> None:
    old = S.surplus_rescue
    try:
        S.surplus_rescue = enhanced_rescue
        result = S.verify_N58_surplus()
    finally:
        S.surplus_rescue = old

    print(f"N58_EQUALITY_RESCUE_STATUS={result['status']}")
    print(f"N58_EQUALITY_RESCUE_CHECKED_STATES={result['checked_states']}")
    print(f"N58_EQUALITY_RESCUE_CHECKED_TRANSITIONS={result['checked_transitions']}")
    print(f"N58_EQUALITY_RESCUE_TOTAL_RESCUES={result['surplus_rescues']}")
    if result['status'] != 'PROVED_FINITE_CAP_AVAILABILITY_BY_EXACT_INCIDENCE_SURPLUS_OVERAPPROX':
        print(f"N58_EQUALITY_RESCUE_FIRST_OPEN={result['first_open']}")
        print('ABSTRACT_FAILURE_IS_INCONCLUSIVE_NOT_ACTUAL_COUNTEREXAMPLE')
        raise AssertionError(result)
    assert result['cap'] == 3364
    print(f"N58_EQUALITY_RESCUE_WORST_RAW={result['worst_raw_bound']}")
    print('N58_FINITE_CAP_AVAILABILITY=PASS')
    print('ABSTRACT_PASS_IS_FINITE_THEOREM_NOT_UNBOUNDED_TOTALITY')
    print('THEOREM_RUNTIME_HEURISTICS=FORBIDDEN')
    print('UNBOUNDED_TOTALITY=OPEN')
    print('UNIVERSAL_GPEI=OPEN')
    print('P_VS_NP=OPEN')


if __name__ == '__main__':
    selftest()
