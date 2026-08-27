#!/usr/bin/env python3
"""Negative control for the first N=58 abstract frontier OPEN.

This intentionally asserts that the current exact overapproximation is
inconclusive at N=58.  That is not an actual CNF counterexample and does not
change the v0.5 runtime.  P vs NP remains OPEN.
"""

from experiments.direct import janus_v05_abstract_frontier_support_mass as A

P_VS_NP = "OPEN"
THEOREM_RUNTIME_HEURISTICS = "FORBIDDEN"


def selftest() -> None:
    result = A.verify_N(58, 57)
    assert result["status"] == "ABSTRACT_BOUND_OPEN", result
    assert result["claim_ceiling"] == "ABSTRACTION_INCONCLUSIVE_NOT_ACTUAL_COUNTEREXAMPLE"
    w = result["first_open"]
    assert w["state"] == [7, 75, 343], w
    assert w["d"] == 49, w
    assert (w["p"], w["q"]) == (22, 27), w
    assert w["raw_bound"] == 3375, w
    assert w["m_out_bound"] == 620, w
    assert w["L_out_bound"] == 2754, w
    assert w["distinct_resolvent_bound"] == 594, w
    assert result["cap"] == 3364
    assert w["raw_bound"] - result["cap"] == 11

    print("V05_N58_ABSTRACT_FIRST_OPEN=REPRODUCED")
    print("V05_N58_FIRST_OPEN_STATE=7,75,343")
    print("V05_N58_FIRST_OPEN_DEGREE=49")
    print("V05_N58_FIRST_OPEN_SPLIT=22,27")
    print("V05_N58_RAW_BOUND=3375")
    print("V05_N58_CAP=3364")
    print("V05_N58_CAP_EXCESS=11")
    print("ACTUAL_REACHABLE_COUNTEREXAMPLE=NOT_ESTABLISHED")
    print("THEOREM_RUNTIME_HEURISTICS=FORBIDDEN")
    print("UNBOUNDED_TOTALITY=OPEN")
    print("UNIVERSAL_GPEI=OPEN")
    print("P_VS_NP=OPEN")


if __name__ == "__main__":
    selftest()
