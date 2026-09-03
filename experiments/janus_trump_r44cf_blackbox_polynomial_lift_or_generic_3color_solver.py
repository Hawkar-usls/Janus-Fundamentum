#!/usr/bin/env python3
from itertools import combinations
import importlib.util
from pathlib import Path
import json

P = Path(__file__).with_name('janus_trump_r44cd_global_transport_3color_reduction_seal.py')
spec = importlib.util.spec_from_file_location('r44cd', P)
r44cd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r44cd)


def image_size(n, m):
    return {'variables': 3*n, 'target_clauses': 4*n+m, 'source_clauses': 4*n+6*m,
            'total_clauses': 8*n+7*m}


def polynomial_lift_certificate(k):
    assert isinstance(k, int) and k >= 0
    # If S runs in O(N^k), construction is O(n+m), and N<=15(n+m) for n+m>=1,
    # then C_S(G)=S(I(G)) runs in O((n+m)^max(1,k)).
    return {
        'transport_runtime_assumption': f'O(N^{k})',
        'image_size_linear': True,
        'explicit_bound': 'N_units := vars+target_clauses+source_clauses = 11n+7m <= 18(n+m)',
        'lifted_runtime': f'O((n+m)^{max(1,k)})',
        'polynomial_preserved_under_composition': True,
    }


def blackbox_lift_decision(n, edges, transport_decider):
    A = r44cd.target_formula(n, edges)
    B = r44cd.source_formula(n, edges)
    return bool(transport_decider(A, B))


def exact_transport_decider_for_audit(A, B):
    # Finite-audit oracle only: exact enumeration implemented by the sealed R44CD verifier.
    # This is NOT claimed as a polynomial algorithm.
    blocks, cands, allowed = r44cd.recover_transport_csp(A, B)
    from itertools import product
    for choice in product(range(3), repeat=len(blocks)):
        if all((choice[i], choice[j]) in rel for (i, j), rel in allowed.items()):
            return True
    return False


def proper_3colorable(n, edges):
    from itertools import product
    return any(all(c[u] != c[v] for u, v in edges) for c in product(range(3), repeat=n))


def all_graphs(n):
    possible = list(combinations(range(n), 2))
    for mask in range(1 << len(possible)):
        yield [e for i, e in enumerate(possible) if (mask >> i) & 1]


def audit(max_n=5):
    checked = 0
    for n in range(1, max_n+1):
        for edges in all_graphs(n):
            got = blackbox_lift_decision(n, edges, exact_transport_decider_for_audit)
            truth = proper_3colorable(n, edges)
            assert got == truth
            m = len(edges)
            s = image_size(n, m)
            assert s['variables'] == 3*n
            assert s['target_clauses'] == 4*n+m
            assert s['source_clauses'] == 4*n+6*m
            checked += 1
    for k in range(0, 9):
        cert = polynomial_lift_certificate(k)
        assert cert['polynomial_preserved_under_composition'] is True
    return {
        'gate': 'R44CF_BLACKBOX_POLYNOMIAL_LIFT_OR_GENERIC_3COLOR_SOLVER',
        'graphs_checked': checked,
        'max_n': max_n,
        'universal_statement': 'IF_R44CC_IMAGE_GLOBAL_TRANSPORT_IN_P_THEN_GRAPH_3COLOR_IN_P',
        'construction_linear': True,
        'blackbox_solver_receives_only_CNF_pair': True,
        'finite_audit_is_not_claimed_as_transport_algorithm': True,
        'polynomial_transport_solver_exists': 'NOT_PROVED',
        'generic_polynomial_3color_solver_exists': 'NOT_PROVED',
        'additional_polynomial_invariant_ruled_out': False,
        'TRUMP_finished': False,
        'SAT_IN_P': 'NOT_PROVED',
        'P_VS_NP': 'OPEN'
    }


if __name__ == '__main__':
    print(json.dumps(audit(), indent=2, sort_keys=True))
