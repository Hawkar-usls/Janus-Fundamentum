#!/usr/bin/env python3
from itertools import combinations, product
import importlib.util
import json
from pathlib import Path

R44CC_PATH = Path(__file__).with_name("janus_trump_r44cc_internal_ternary_transport_inequality_realizability.py")
spec = importlib.util.spec_from_file_location("r44cc", R44CC_PATH)
r44cc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r44cc)


def all_graphs(n):
    possible = list(combinations(range(n), 2))
    for mask in range(1 << len(possible)):
        yield [e for i, e in enumerate(possible) if (mask >> i) & 1]


def independent_3colorings(n, edges):
    return {
        c for c in product(range(3), repeat=n)
        if all(c[u] != c[v] for u, v in edges)
    }


def transport_assignments_from_formulas(A, B):
    blocks, cands, allowed = r44cc.recover_transport_csp(A, B)
    out = set()
    for choice in product(range(3), repeat=len(blocks)):
        if all((choice[i], choice[j]) in rel for (i, j), rel in allowed.items()):
            decoded = tuple(r44cc.candidate_color(cands[i][choice[i]], blocks[i]) for i in range(len(blocks)))
            out.add(decoded)
    return out, blocks, cands, allowed


def verify_instance(n, edges):
    A = r44cc.target_formula(n, edges)
    B = r44cc.source_formula(n, edges)

    recovered, blocks, cands, allowed = transport_assignments_from_formulas(A, B)
    truth = independent_3colorings(n, edges)
    expected_neq3 = {(a, b) for a in range(3) for b in range(3) if a != b}

    assert len(A) == 4 * n + len(edges)
    assert len(B) == 4 * n + 6 * len(edges)
    assert len({abs(l) for C in A + B for l in C}) == 3 * n
    assert len(blocks) == n
    assert all(len(Bi) == 3 for Bi in blocks)
    assert all(len(Ci) == 3 for Ci in cands)
    assert len(allowed) == len(edges)
    assert all(rel == expected_neq3 for rel in allowed.values())
    assert recovered == truth

    return {
        "transport_exists": bool(recovered),
        "graph_3colorable": bool(truth),
        "assignment_count": len(recovered),
    }


def audit(max_n=5):
    checked = 0
    yes_instances = 0
    no_instances = 0
    for n in range(1, max_n + 1):
        for edges in all_graphs(n):
            result = verify_instance(n, edges)
            assert result["transport_exists"] == result["graph_3colorable"]
            checked += 1
            if result["graph_3colorable"]:
                yes_instances += 1
            else:
                no_instances += 1

    triangle = [(0, 1), (1, 2), (0, 2)]
    k4 = list(combinations(range(4), 2))
    tri = verify_instance(3, triangle)
    k4r = verify_instance(4, k4)
    assert tri["assignment_count"] == 6
    assert k4r["assignment_count"] == 0

    return {
        "gate": "R44CD_GLOBAL_TRANSPORT_3COLOR_REDUCTION_SEAL",
        "graphs_checked": checked,
        "max_n": max_n,
        "yes_instances": yes_instances,
        "no_instances": no_instances,
        "triangle_global_transport_count": tri["assignment_count"],
        "k4_global_transport_count": k4r["assignment_count"],
        "formula_only_recovery": True,
        "local_candidate_count": 3,
        "edge_relation": "EXACT_NEQ3",
        "exact_bijection_on_enumerated_universe": True,
        "reduction": "GRAPH_3_COLORING <=m GLOBAL_TRANSPORT_EXISTENCE_ON_R44CC_FAMILY",
        "construction_size": "variables=3n,target_clauses=4n+m,source_clauses=4n+6m",
        "construction_polynomial": True,
        "finite_audit_uses_exhaustive_verification_only": True,
        "finite_audit_is_not_claimed_as_transport_algorithm": True,
        "conditional_consequence": "POLYTIME_GLOBAL_TRANSPORT_ON_THIS_FAMILY_IMPLIES_POLYTIME_GRAPH_3_COLORING",
        "additional_polynomial_invariant_ruled_out": False,
        "full_TRUMP_polynomiality_proven": False,
        "TRUMP_finished": False,
        "SAT_IN_P": "NOT_PROVED",
        "P_VS_NP": "OPEN",
    }


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2, sort_keys=True))
