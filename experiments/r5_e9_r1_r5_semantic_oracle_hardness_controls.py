#!/usr/bin/env python3
"""R1/R5 semantic-oracle hardness controls.

This executable is a finite reduction/control checker, not an admitted E8-D1 SAT
algorithm. Exhaustive enumeration is used only on fixed tiny fixtures to certify
the probe gadget and the reduction truth table.
"""
from __future__ import annotations
from itertools import product
import json

Hypergraph = tuple[tuple[int, int, int], ...]


def vars_of(H: Hypergraph) -> tuple[int, ...]:
    return tuple(sorted({v for e in H for v in e}))


def is_exact_one_model(H: Hypergraph, a: dict[int, int]) -> bool:
    return all(sum(a[v] for v in e) == 1 for e in H)


def models(H: Hypergraph) -> list[dict[int, int]]:
    vs = vars_of(H)
    out = []
    for bits in product((0, 1), repeat=len(vs)):
        a = dict(zip(vs, bits))
        if is_exact_one_model(H, a):
            out.append(a)
    return out


def is_cubic_3uniform(H: Hypergraph) -> bool:
    if any(len(set(e)) != 3 for e in H):
        return False
    deg = {v: 0 for v in vars_of(H)}
    for e in H:
        for v in e:
            deg[v] += 1
    return all(d == 3 for d in deg.values())


def is_linear(H: Hypergraph) -> bool:
    E = [set(e) for e in H]
    return all(len(E[i] & E[j]) <= 1 for i in range(len(E)) for j in range(i))


def disjoint_union(A: Hypergraph, B: Hypergraph) -> tuple[Hypergraph, dict[int, int]]:
    """Return A disjoint-union a relabelled copy of B and map old-B -> new labels."""
    av = vars_of(A)
    offset = (max(av) + 1) if av else 0
    bv = vars_of(B)
    rel = {v: offset + i for i, v in enumerate(bv)}
    B2 = tuple(tuple(rel[v] for v in e) for e in B)
    return A + B2, rel


def sat(H: Hypergraph) -> bool:
    return bool(models(H))


def semantic_equal(H: Hypergraph, p: int, q: int) -> bool:
    # Vacuous truth on UNSAT instances is exactly the semantic behavior used by
    # the reduction.
    return all(a[p] == a[q] for a in models(H))


def branch(H: Hypergraph, q: int, value: int) -> Hypergraph | None:
    """Not used as a transformed hypergraph; kept only for interface clarity."""
    return H


def sat_with_pin(H: Hypergraph, q: int, value: int) -> bool:
    return any(a[q] == value for a in models(H))


# Fixed cubic, 3-uniform, linear probe. Its rational solution set to A x = 1 is
# (t,t,1-2t,t,t,t,1-2t,1-2t,t); Booleanity forces t=0. Therefore the unique
# exact-one model is 001000110 (variables 0..8).
PROBE: Hypergraph = (
    (0, 7, 5),
    (1, 6, 0),
    (2, 8, 3),
    (3, 5, 6),
    (4, 0, 2),
    (5, 2, 1),
    (6, 4, 8),
    (7, 3, 4),
    (8, 1, 7),
)
EXPECTED = {0: 0, 1: 0, 2: 1, 3: 0, 4: 0, 5: 0, 6: 1, 7: 1, 8: 0}
assert is_cubic_3uniform(PROBE)
assert is_linear(PROBE)
pm = models(PROBE)
assert pm == [EXPECTED]
# p and q are forced unequal; q is forced true.
p0, q1 = 0, 2
assert pm[0][p0] == 0 and pm[0][q1] == 1

# Fano plane: cubic, 3-uniform, linear, and Exact-One UNSAT. The latter also
# follows immediately from 3|S|=7, but exhaustive verification is retained as
# a tiny independent control.
FANO: Hypergraph = (
    (0, 1, 3),
    (0, 2, 5),
    (0, 4, 6),
    (1, 2, 6),
    (1, 4, 5),
    (2, 3, 4),
    (3, 5, 6),
)
assert is_cubic_3uniform(FANO)
assert is_linear(FANO)
assert not sat(FANO)

# A SAT source for the other side of the reduction truth table.
SAT_SOURCE = PROBE
assert sat(SAT_SOURCE)

# Reduction control:
# G = F disjoint-union PROBE.
# If F is UNSAT then G is UNSAT, hence p==q holds vacuously and pinning forced
# q to 0 preserves UNSAT.
# If F is SAT then G is SAT, the fixed probe has p=0,q=1, hence p==q is false;
# pinning q to 0 destroys every model.
reduction_rows = []
for source_name, F in (("UNSAT_FANO", FANO), ("SAT_PROBE", SAT_SOURCE)):
    G, rel = disjoint_union(F, PROBE)
    p, q = rel[p0], rel[q1]
    row = {
        "source": source_name,
        "source_sat": sat(F),
        "union_sat": sat(G),
        "semantic_p_eq_q": semantic_equal(G, p, q),
        "union_sat_with_q_eq_0": sat_with_pin(G, q, 0),
        "safe_branch_q_eq_0": sat(G) == sat_with_pin(G, q, 0),
    }
    reduction_rows.append(row)

assert reduction_rows[0] == {
    "source": "UNSAT_FANO",
    "source_sat": False,
    "union_sat": False,
    "semantic_p_eq_q": True,
    "union_sat_with_q_eq_0": False,
    "safe_branch_q_eq_0": True,
}
assert reduction_rows[1] == {
    "source": "SAT_PROBE",
    "source_sat": True,
    "union_sat": True,
    "semantic_p_eq_q": False,
    "union_sat_with_q_eq_0": False,
    "safe_branch_q_eq_0": False,
}

print(json.dumps({
    "status": "PASS_R1_R5_SEMANTIC_ORACLE_HARDNESS_CONTROLS",
    "probe": {
        "vertices": 9,
        "edges": 9,
        "cubic": True,
        "linear": True,
        "unique_model": [EXPECTED[i] for i in range(9)],
        "forced_unequal_pair": [p0, q1],
        "forced_true_variable": q1,
    },
    "reduction_truth_table": reduction_rows,
    "role": "OFFLINE_FIXED_GADGET_AND_REDUCTION_CONTROL__NOT_D1_SOLVER",
    "R1_semantic_equivalence": "CO_NP_HARDNESS_REDUCTION_SUPPORTED",
    "R5_semantic_safe_branch": "CO_NP_HARDNESS_REDUCTION_SUPPORTED",
    "D1": "EMPTY",
    "P_VS_NP": "OPEN",
}, sort_keys=True))
