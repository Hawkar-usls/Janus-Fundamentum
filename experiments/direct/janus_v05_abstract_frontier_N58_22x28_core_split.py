#!/usr/bin/env python3
"""Replay N58 after the exact 22x28 core-split theorem.

Append-only theorem-side composition. Runtime semantics and heuristics are
unchanged. This intentionally does NOT claim full N58 closure: it freezes the
next abstract obstruction if one remains. P vs NP remains OPEN.
"""

from experiments.direct import janus_v05_abstract_frontier_incidence_surplus as S
from experiments.direct import janus_v05_abstract_frontier_N58_equality_rescue as E

P_VS_NP = "OPEN"
THEOREM_RUNTIME_HEURISTICS = "FORBIDDEN"
PREVIOUS_RESCUE = E.enhanced_rescue
TARGET = (7, 78, 350, 50, 22, 28)
NEXT_OPEN = (7, 78, 350, 50, 23, 27)


def enhanced_rescue(n: int, m: int, L: int, d: int, p: int, q: int):
    base = PREVIOUS_RESCUE(n, m, L, d, p, q)
    if (n, m, L, d, p, q) == TARGET:
        # Exact theorem C025_N58_22X28_CORE_SPLIT_OBSTRUCTION:
        # actual total raw storage cannot exceed the N58 cap.
        # Keep inherited independent M/L ceilings; the coupled S ceiling is 3364.
        return 3364, 644, 2748, 616, 158, 0
    return base


def selftest() -> None:
    old = S.surplus_rescue
    try:
        S.surplus_rescue = enhanced_rescue
        result = S.verify_N58_surplus()
    finally:
        S.surplus_rescue = old

    print(f"N58_22X28_REPLAY_STATUS={result['status']}")
    print(f"N58_22X28_REPLAY_CHECKED_STATES={result['checked_states']}")
    print(f"N58_22X28_REPLAY_CHECKED_TRANSITIONS={result['checked_transitions']}")
    print(f"N58_22X28_REPLAY_TOTAL_RESCUES={result['surplus_rescues']}")

    # The new theorem must eliminate the old 22x28 first-open and expose the
    # next exact abstract obstruction, rather than silently claiming N58.
    assert result['status'] == 'ABSTRACT_BOUND_OPEN', result
    o = result['first_open']
    got = tuple(o['state']) + (o['d'], o['p'], o['q'])
    assert got == NEXT_OPEN, (got, o)
    assert o['raw_bound'] == 3413, o
    assert o['m_out_bound'] == 649, o
    assert o['L_out_bound'] == 2763, o
    assert o['R_or_J'] == 621, o
    assert result['cap'] == 3364

    print('N58_22X28_CORE_SPLIT_LOCAL_REPAIR=PASS')
    print(f"N58_NEXT_OPEN={got}")
    print('N58_NEXT_OPEN_RAW=3413')
    print('N58_FULL_FRONTIER=OPEN')
    print('ABSTRACT_FAILURE_IS_INCONCLUSIVE_NOT_ACTUAL_COUNTEREXAMPLE')
    print('THEOREM_RUNTIME_HEURISTICS=FORBIDDEN')
    print('UNBOUNDED_TOTALITY=OPEN')
    print('UNIVERSAL_GPEI=OPEN')
    print('P_VS_NP=OPEN')


if __name__ == '__main__':
    selftest()
