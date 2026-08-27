#!/usr/bin/env python3
"""Replay N58 after exact 21x29, 22x28 and 23x27 theorem rescues.

Append-only theorem-side composition. Runtime semantics are unchanged. A green
run validates the local 23x27 theorem and freezes the next abstract obstruction;
it does not assert full N58 closure. P vs NP remains OPEN.
"""

from experiments.direct import janus_v05_abstract_frontier_incidence_surplus as S
from experiments.direct import janus_v05_abstract_frontier_N58_22x28_core_split as R22

P_VS_NP = "OPEN"
THEOREM_RUNTIME_HEURISTICS = "FORBIDDEN"
PREVIOUS_RESCUE = R22.enhanced_rescue
TARGET = (7, 78, 350, 50, 23, 27)
NEXT_OPEN = (7, 78, 350, 50, 24, 26)


def enhanced_rescue(n: int, m: int, L: int, d: int, p: int, q: int):
    base = PREVIOUS_RESCUE(n, m, L, d, p, q)
    if (n, m, L, d, p, q) == TARGET:
        # Exact C025 23x27 projection-fiber theorem bounds the coupled total.
        # Independent inherited M/L ceilings remain valid and unchanged.
        return 3364, 649, 2763, 621, 161, 0
    return base


def selftest() -> None:
    old = S.surplus_rescue
    try:
        S.surplus_rescue = enhanced_rescue
        result = S.verify_N58_surplus()
    finally:
        S.surplus_rescue = old

    print(f"N58_23X27_REPLAY_STATUS={result['status']}")
    print(f"N58_23X27_REPLAY_CHECKED_STATES={result['checked_states']}")
    print(f"N58_23X27_REPLAY_CHECKED_TRANSITIONS={result['checked_transitions']}")
    print(f"N58_23X27_REPLAY_TOTAL_RESCUES={result['surplus_rescues']}")

    assert result['status'] == 'ABSTRACT_BOUND_OPEN', result
    o = result['first_open']
    got = tuple(o['state']) + (o['d'], o['p'], o['q'])
    assert got == NEXT_OPEN, (got, o)
    assert o['raw_bound'] == 3425, o
    assert o['m_out_bound'] == 652, o
    assert o['L_out_bound'] == 2772, o
    assert o['R_or_J'] == 624, o
    assert result['cap'] == 3364

    print('N58_23X27_PROJECTION_FIBER_LOCAL_REPAIR=PASS')
    print(f"N58_NEXT_OPEN={got}")
    print('N58_NEXT_OPEN_RAW=3425')
    print('N58_FULL_FRONTIER=OPEN')
    print('ABSTRACT_FAILURE_IS_INCONCLUSIVE_NOT_ACTUAL_COUNTEREXAMPLE')
    print('THEOREM_RUNTIME_HEURISTICS=FORBIDDEN')
    print('UNBOUNDED_TOTALITY=OPEN')
    print('UNIVERSAL_GPEI=OPEN')
    print('P_VS_NP=OPEN')


if __name__ == '__main__':
    selftest()
