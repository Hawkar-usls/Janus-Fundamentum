#!/usr/bin/env python3
"""JANUS C025 PIRC decision-core v0.5 proof-selector candidate.

This file DOES NOT modify the frozen v0.4 source file.  It supplies a separate,
deterministic pivot-order policy for research replay:

    root class before extension class (same class priority as v0.4),
    then exact incidence degree d_x,
    then frozen canonical tie-break.

No heuristic score, randomness, learned quantity, SAT oracle, semantic oracle, or
future prediction participates in the order.  The purpose of the policy is to
constructively realize the minimum-incidence witness used by existing proofs.

P vs NP remains OPEN.
"""

from __future__ import annotations

from typing import List, Optional

from experiments.direct import janus_unified_proof_carrying_akinator_jec as core

P_VS_NP = "OPEN"
SELECTOR_VERSION = "PIRC_DECISION_CORE_V0_5_PROOF_SELECTOR_CANDIDATE"
THEOREM_RUNTIME_HEURISTICS = "FORBIDDEN"


def incidence_degree(cnf: core.CNF, var: int) -> int:
    """Exact syntactic clause-incidence degree d_x."""
    v = abs(int(var))
    return sum(1 for clause in cnf if v in clause or -v in clause)


def proof_pivot_order(state: core.EngineState, cnf: Optional[core.CNF] = None) -> List[int]:
    """Deterministic root-preserving minimum-incidence pivot order.

    The old root-before-extension class partition is preserved.  Within each
    class the order is (exact incidence degree, frozen canonical position).
    """
    f = state.residual if cnf is None else cnf
    live = set(core.vars_of(f))
    root_position = {v: i for i, v in enumerate(state.root_vars)}

    roots = [v for v in state.root_vars if v in live]
    roots.sort(key=lambda v: (incidence_degree(f, v), root_position[v]))

    rootset = set(state.root_vars)
    exts = sorted((v for v in live if v not in rootset), key=lambda v: (incidence_degree(f, v), v))
    return roots + exts


def selected_min_degree_in_active_class(state: core.EngineState, cnf: Optional[core.CNF] = None) -> Optional[int]:
    """Return the first pivot that the proof-selector will inspect."""
    order = proof_pivot_order(state, cnf)
    return order[0] if order else None


def activate_on_imported_core() -> None:
    """Install the candidate order in this Python process only.

    The repository's frozen v0.4 file is untouched.  All exact transition,
    replay, cap and terminal code continues to be the v0.4 implementation; only
    canonical_pivot_order is replaced for this candidate process.
    """
    core.canonical_pivot_order = proof_pivot_order


def selector_certificate(cnf: core.CNF, variables: List[int]) -> dict:
    rows = [(v, incidence_degree(cnf, v)) for v in variables]
    if not rows:
        return {"kind": "NO_LIVE_PIVOT", "rows": []}
    dmin = min(d for _, d in rows)
    witnesses = [v for v, d in rows if d == dmin]
    return {
        "kind": "EXACT_MIN_INCIDENCE_SELECTOR_CERTIFICATE",
        "rows": rows,
        "minimum_degree": dmin,
        "minimum_witnesses": witnesses,
        "selected_canonical_witness": witnesses[0],
    }


def selftest() -> None:
    class Stub:
        pass

    # Degrees: d1=2, d2=3, d3=2, d4=1.  Root order deliberately places 4 last.
    cnf = core.canon_cnf([(1, 2), (-1, 2, 3), (-2, 3), (4, 3)])
    st = Stub()
    st.residual = cnf
    st.root_vars = (1, 2, 3, 4)
    order = proof_pivot_order(st)
    degrees = [incidence_degree(cnf, v) for v in order]
    assert degrees == sorted(degrees), (order, degrees)
    assert order[0] == 4, (order, degrees)

    # Canonical tie-break inside equal degree.
    cnf2 = core.canon_cnf([(1, 2), (-1, 3), (2, 4), (3, 4)])
    st2 = Stub()
    st2.residual = cnf2
    st2.root_vars = (3, 1, 2, 4)
    order2 = proof_pivot_order(st2)
    dmin = min(incidence_degree(cnf2, v) for v in st2.root_vars)
    expected = next(v for v in st2.root_vars if incidence_degree(cnf2, v) == dmin)
    assert order2[0] == expected

    # Root-before-extension class priority is preserved even if extension degree is lower.
    cnf3 = core.canon_cnf([(1, 2), (-1, 2), (9, 2)])
    st3 = Stub()
    st3.residual = cnf3
    st3.root_vars = (1, 2)
    order3 = proof_pivot_order(st3)
    assert order3[:2] == sorted(order3[:2], key=lambda v: (incidence_degree(cnf3, v), st3.root_vars.index(v)))
    assert order3[-1] == 9

    print("PROOF_SELECTOR_MIN_INCIDENCE=PASS")
    print("ROOT_BEFORE_EXTENSION_PRIORITY=PASS")
    print("DETERMINISTIC_CANONICAL_TIEBREAK=PASS")
    print("THEOREM_RUNTIME_HEURISTICS=FORBIDDEN")
    print("P_VS_NP=OPEN")


if __name__ == "__main__":
    selftest()
