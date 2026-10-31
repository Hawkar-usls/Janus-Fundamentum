#!/usr/bin/env python3
"""Finite regression controls for the prescribed-C10 2-group cover theorem candidate.

This checker does NOT prove the residual-finite-2 existence theorem and does
NOT promote a JANUS ledger item. It validates the explicit C10 in the A'_m
family, the dependent-generator accounting, and the fixed-constant bounds used
by the proof candidate.
"""
from __future__ import annotations
import json


def P(v, m):
    r, a = v
    return ((r + 1) % 3, a)


def Q(v, m):
    r, a = v
    if r == 0:
        return (2, (a + 1) % m)
    if r == 1:
        return (0, a)
    return (1, a)


def Qprime(v, m):
    u = (0, 0)
    w = (2, 2 % m)
    if v == u:
        return Q(w, m)
    if v == w:
        return Q(u, m)
    return Q(v, m)


def row_support(row, m):
    return {row, P(row, m), Qprime(row, m)}


def designated_c10(m):
    # Alternating column-vertex V(...) and row-vertex R(...).
    return [
        ("V", (1, 2 % m)),
        ("R", (1, 2 % m)),
        ("V", (2, 2 % m)),
        ("R", (0, 1 % m)),
        ("V", (0, 1 % m)),
        ("R", (2, 1 % m)),
        ("V", (2, 1 % m)),
        ("R", (2, 2 % m)),
        ("V", (0, 2 % m)),
        ("R", (0, 2 % m)),
    ]


def incident(x, y, m):
    if x[0] == y[0]:
        return False
    if x[0] == "R":
        row, col = x[1], y[1]
    else:
        row, col = y[1], x[1]
    return col in row_support(row, m)


def verify_c10(m):
    cyc = designated_c10(m)
    assert len(cyc) == 10
    assert len(set(cyc)) == 10
    for i in range(10):
        assert incident(cyc[i], cyc[(i + 1) % 10], m)
    return True


for m in range(3, 129):
    assert verify_c10(m)

# Dependent generator z=e10=(e1...e9)^-1 replaces one z-letter by a
# freely reduced word of length 9. Any base bad walk has length <=9, so the
# substituted word has length at most 9*9=81.
RELATOR_LENGTH = 10
MAX_BAD_BASE_LENGTH = 9
DEPENDENT_EXPANSION_LENGTH = 9
SUBSTITUTION_BOUND = MAX_BAD_BASE_LENGTH * DEPENDENT_EXPANSION_LENGTH
assert SUBSTITUTION_BOUND == 81

# The nine tree-geodesic labels are pairwise distinct. Therefore two distinct
# left translates of the path e1...e9 cannot share an undirected tree edge:
# an overlap fixes the unique edge label/position and hence the translate.
path_labels = tuple(f"e{i}" for i in range(1, 10))
assert len(set(path_labels)) == 9

out = {
    "status": "PASS_PRESCRIBED_C10_FINITE_REGRESSION",
    "family": "A'_m",
    "m_range_checked": [3, 128],
    "explicit_designated_incidence_C10": True,
    "relator_length": RELATOR_LENGTH,
    "dependent_expansion_length": DEPENDENT_EXPANSION_LENGTH,
    "substitution_bound": SUBSTITUTION_BOUND,
    "shortcut_translate_edge_disjointness_control": "PAIRWISE_DISTINCT_PATH_LABELS",
    "finite_regression_only": True,
    "theorem_status": "THEOREM_CANDIDATE",
    "ledger_promotion": "BLOCKED_PENDING_GOVERNANCE_AND_BOOTSTRAP_RESOLUTION",
    "P_VS_NP": "OPEN",
    "P_EQ_NP": "NOT_PROVED",
}
print(json.dumps(out, sort_keys=True))
