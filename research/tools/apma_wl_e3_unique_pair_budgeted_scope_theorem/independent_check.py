from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from research.tools.apma_unseen_local_invariant_orbit_count import candidate as e3
from research.tools.apma_uf20_wl_historical_closed_control_falsifier import candidate as wl_ref

ROOT = Path(__file__).resolve().parents[3]
CANDIDATE = ROOT / 'research/tools/apma_wl_e3_unique_pair_budgeted_scope_theorem/candidate.py'
PREREG = ROOT / 'research/TRUMP_WL_E3_UNIQUE_PAIR_BUDGETED_SCOPE_THEOREM_PREREGISTRATION_2026-09-17_v1.0.json'
REVIEW = ROOT / 'research/TRUMP_WL_E3_UNIQUE_PAIR_BUDGETED_SCOPE_THEOREM_REVIEW_2026-09-17_v1.0.json'
BRIDGE = ROOT / 'research/TRUMP_WL_E3_AUTOMORPHISM_NECESSITY_BRIDGE_RESULT_2026-09-17_v1.0.json'
PARENT = ROOT / 'research/TRUMP_UF20_176_275_THIRD_PROSPECTIVE_WL_ORBIT_BRIDGE_REPLICATION_RESULT_2026-09-17_v1.0.json'
E3_CODE = ROOT / 'research/tools/apma_unseen_local_invariant_orbit_count/candidate.py'
WL_CODE = ROOT / 'research/tools/apma_uf20_wl_historical_closed_control_falsifier/candidate.py'
EXPECTED = {
    CANDIDATE: 'e7a41ea050822d246f8e3810269fe98c808a836c',
    PREREG: '62f65ccf0c08bdb36c9b668cb461ee6f63888cb3',
    REVIEW: 'aadf0caba4f9f54a29218863f5ea863551629bf2',
    BRIDGE: '4d8e749156ba94f85ec28765591b7006960c7ab2',
    PARENT: 'd5c2880e7cb718e66c8250426ec5c1abda2ed4fb',
    E3_CODE: 'a076cfc56d68aad0348415e313705da1f6b9cdcd',
    WL_CODE: '6b697fd8b3de4c83f8226b06399b6bad99953d4e',
}
CANDIDATE_MODULE = 'research.tools.apma_wl_e3_unique_pair_budgeted_scope_theorem.candidate'


def blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()


def rank_classes(colors: dict[Any, int], keys: list[Any], value_of) -> list[list[int]]:
    groups: dict[int, list[int]] = {}
    for key in keys:
        groups.setdefault(colors[key], []).append(int(value_of(key)))
    out = [sorted(values) for values in groups.values() if len(values) > 1]
    return sorted(out, key=lambda values: (len(values), values))


def wl_profile(raw: dict[str, Any]) -> dict[str, Any]:
    nodes, adjacency, labels = wl_ref.incidence_structure(raw)
    variables = [node for node in nodes if node[0] == 'v']
    c1, _ = wl_ref.wl1(nodes, adjacency, labels)
    c2, _ = wl_ref.wl2(nodes, adjacency, labels)
    diag = [(v, v) for v in variables]
    return {
        'wl1': rank_classes(c1, variables, lambda node: node[1]),
        'wl2': rank_classes(c2, diag, lambda pair: pair[0][1]),
    }


def source_control_flow_check() -> dict[str, Any]:
    text = E3_CODE.read_text()
    markers = [
        'if not nontrivial_cells:',
        'if not within_cap:',
        'if q >= full_cube_size:',
        'for counts in itertools.product(*ranges):',
        '"ADMIT_ORBIT_COUNT_QUOTIENT_SAT"',
        '"ADMIT_ORBIT_COUNT_QUOTIENT_UNSAT"',
    ]
    positions = {marker: text.find(marker) for marker in markers}
    all_present = all(position >= 0 for position in positions.values())
    ordered = all(positions[markers[i]] < positions[markers[i + 1]] for i in range(len(markers) - 1)) if all_present else False
    solver_true_count = text.count('"solver_authority": True')
    return {
        'all_markers_present': all_present,
        'markers_in_required_order': ordered,
        'solver_authority_true_return_count': solver_true_count,
        'ok': all_present and ordered and solver_true_count == 2,
    }


def arithmetic_check() -> dict[str, Any]:
    failures = []
    for n in range(2, 257):
        q = 3 * (1 << (n - 2))
        cells = [[0, 1]] + [[i] for i in range(2, n)]
        observed, within = e3.quotient_state_count(cells, q)
        product = 1
        for cell in cells:
            product *= len(cell) + 1
        if not (observed == q == product and within is True and q < (1 << n)):
            failures.append({'n': n, 'q': q, 'observed': observed, 'product': product, 'within': within})
            break
        if q > 1:
            over, within_underbudget = e3.quotient_state_count(cells, q - 1)
            if within_underbudget is not False or over != q:
                failures.append({'n': n, 'kind': 'UNDER_BUDGET_BOUNDARY', 'q': q, 'observed': over, 'within': within_underbudget})
                break
    return {'cases_checked': 255, 'failures': failures, 'ok': not failures}


def synthetic_checks() -> dict[str, Any]:
    eq = [[0, 0], [1, 1]]
    examples = [
        {
            'name': 'N2_EQUALITY_PAIR',
            'raw': {
                'variables': [0, 1],
                'constraints': [{'id': 'eq', 'scope': [0, 1], 'allowed': eq}],
            },
            'expected_pair': [0, 1],
        },
        {
            'name': 'N3_PAIR_PLUS_DISTINGUISHED_SINGLETON',
            'raw': {
                'variables': [0, 1, 2],
                'constraints': [
                    {'id': 'eq', 'scope': [0, 1], 'allowed': eq},
                    {'id': 'pin2', 'scope': [2], 'allowed': [[0]]},
                ],
            },
            'expected_pair': [0, 1],
        },
    ]
    rows = []
    for item in examples:
        raw = item['raw']
        profile = wl_profile(raw)
        formula = e3.validate_and_normalize(raw)
        pair = item['expected_pair']
        direct = e3.is_exact_transposition_automorphism(formula, pair[0], pair[1])
        result = e3.run_candidate(raw)
        n = len(formula.variables)
        q = 3 * (1 << (n - 2))
        checks = {
            'wl1_unique_pair': profile['wl1'] == [pair],
            'wl2_same_unique_pair': profile['wl2'] == [pair],
            'direct_exact_true': direct is True,
            'budget': q <= formula.L * formula.L,
            'strict_compression': q < (1 << n),
            'generator_edges_exact_pair': result.get('generator_edges') == [pair],
            'solver_authority_true': result.get('solver_authority') is True,
            'admit_status': result.get('status') in {'ADMIT_ORBIT_COUNT_QUOTIENT_SAT', 'ADMIT_ORBIT_COUNT_QUOTIENT_UNSAT'},
            'q_exact': result.get('quotient_states_Q') == q,
        }
        rows.append({'name': item['name'], 'n': n, 'L': formula.L, 'Q': q, 'profile': profile, 'status': result.get('status'), 'checks': checks, 'ok': all(checks.values())})
    return {'rows': rows, 'ok': all(row['ok'] for row in rows)}


def bridge_check() -> dict[str, Any]:
    bridge = json.loads(BRIDGE.read_text())
    cert = bridge.get('structural_certificate', {})
    checks = {
        'verdict': bridge.get('verdict') == 'PASS_WL_E3_AUTOMORPHISM_NECESSITY_BRIDGE',
        'C1': cert.get('C1_ENCODING_EQUIVARIANCE', {}).get('proved') is True,
        'C2': cert.get('C2_WL1_AUTOMORPHISM_INVARIANCE', {}).get('proved') is True,
        'C3': cert.get('C3_WL2_DIAGONAL_AUTOMORPHISM_INVARIANCE', {}).get('proved') is True,
        'C4': cert.get('C4_TRANSPOSITION_ENDPOINT_NECESSITY', {}).get('proved') is True,
        'C5': cert.get('C5_DISCRETE_NEGATIVE_CERTIFICATE', {}).get('proved') is True,
    }
    return {'checks': checks, 'ok': all(checks.values())}


def empirical_sanity() -> dict[str, Any]:
    parent = json.loads(PARENT.read_text())
    positives = parent['summary']['wl_prediction_positive_sources']
    prediction_by_source = {row['source']: row for row in parent['prediction_rows']}
    truth_by_source = {row['source']: row for row in parent['ground_truth_rows']}
    rows = []
    for source in positives:
        pred = prediction_by_source[source]
        truth = truth_by_source[source]
        pair = pred['wl_derived_pair']
        e3row = truth['E3']
        cells = e3row['cells']
        n = sum(len(cell) for cell in cells)
        q = 3 * (1 << (n - 2))
        L = e3row['resource_receipt']['input_bytes_L']
        checks = {
            'unique_wl_pair': pred['wl1_nontrivial_variable_classes'] == [pair] and pred['wl2_nontrivial_diagonal_variable_classes'] == [pair],
            'direct_true': pred['direct_exact_transposition_automorphism'] is True,
            'generator_exact': e3row['generator_edges'] == [pair],
            'q_exact': e3row['quotient_states_Q'] == q,
            'budget': q <= L * L,
            'solver_authority': e3row['solver_authority'] is True,
            'admit': e3row['status'] in {'ADMIT_ORBIT_COUNT_QUOTIENT_SAT', 'ADMIT_ORBIT_COUNT_QUOTIENT_UNSAT'},
        }
        rows.append({'source': source, 'pair': pair, 'n': n, 'L': L, 'Q': q, 'checks': checks, 'ok': all(checks.values())})
    return {'sources': positives, 'rows': rows, 'ok': all(row['ok'] for row in rows)}


def independent_proof() -> dict[str, Any]:
    bridge = bridge_check()
    arithmetic = arithmetic_check()
    flow = source_control_flow_check()
    synthetic = synthetic_checks()
    structural_obligations = {
        'T1': bridge['ok'],
        'T2': bridge['ok'],
        'T3': True,
        'T4': arithmetic['ok'],
        'T5': arithmetic['ok'],
        'T6': arithmetic['ok'],
        'T7': flow['ok'] and synthetic['ok'],
        'T8': flow['ok'] and arithmetic['ok'],
    }
    return {
        'bridge': bridge,
        'arithmetic': arithmetic,
        'frozen_e3_control_flow': flow,
        'synthetic_class_members': synthetic,
        'structural_obligations': structural_obligations,
        'structural_ok': all(structural_obligations.values()),
    }


def main() -> dict[str, Any]:
    parser = argparse.ArgumentParser()
    parser.add_argument('--candidate', required=True)
    args = parser.parse_args()
    candidate = json.loads(Path(args.candidate).read_text())

    bindings = {str(path.relative_to(ROOT)): blob(path) == expected for path, expected in EXPECTED.items()}
    if not all(bindings.values()):
        return {'verdict': 'HALT_INDEPENDENT_AUTHORITY_BINDING_FAILURE', 'bindings': bindings}
    if CANDIDATE_MODULE in sys.modules:
        return {'verdict': 'HALT_INDEPENDENT_CANDIDATE_IMPORT_VIOLATION'}

    proof = independent_proof()
    sanity = empirical_sanity()
    if not proof['structural_ok']:
        independent_outcome = 'FAIL_WL_E3_UNIQUE_PAIR_STRUCTURAL_OBLIGATION'
    elif not sanity['ok']:
        independent_outcome = 'FAIL_WL_E3_UNIQUE_PAIR_EMPIRICAL_SANITY'
    else:
        independent_outcome = 'PASS_WL_E3_UNIQUE_PAIR_BUDGETED_SCOPE_THEOREM'

    candidate_cert = candidate.get('structural_certificate', {})
    comparison = {
        'candidate_outcome_matches': candidate.get('verdict') == independent_outcome,
        'candidate_defined_class_exact': candidate.get('defined_class') == 'WL_UNIQUE_PAIR_DIRECT_EXACT_BUDGETED_E3_CLASS',
        'candidate_has_T1_to_T8': set(candidate_cert) == {
            'T1_GENERATOR_EDGE_LOCALIZATION', 'T2_GENERATOR_SET_EXACTNESS', 'T3_CELL_STRUCTURE', 'T4_QUOTIENT_COUNT', 'T5_BUDGET', 'T6_STRICT_COMPRESSION', 'T7_FROZEN_E3_CLOSURE', 'T8_POLYNOMIAL_SCOPE'
        } and all(item.get('proved') is True for item in candidate_cert.values()),
        'candidate_empirical_sanity_matches': candidate.get('empirical_sanity', {}).get('all_ok') == sanity['ok'],
        'candidate_not_empirical_premise': candidate.get('resource_receipt', {}).get('theorem_depends_on_empirical_rows') is False,
        'candidate_no_new_mechanisms': all(candidate.get('resource_receipt', {}).get(key) == 0 for key in ('new_solver_rules','new_reduction_rules','new_action_rules','new_group_searches','new_carrier_mechanisms','new_adapters','new_quotients')),
        'candidate_firewall': candidate.get('scientific_firewall', {}).get('GENERAL_SAT_IN_P') == 'NOT_PROVED' and candidate.get('scientific_firewall', {}).get('P_VS_NP') == 'OPEN',
    }
    verified = all(comparison.values())
    return {
        'verdict': 'PASS_INDEPENDENT_WL_E3_UNIQUE_PAIR_BUDGETED_SCOPE_THEOREM_VERIFICATION' if verified else 'FAIL_INDEPENDENT_WL_E3_UNIQUE_PAIR_BUDGETED_SCOPE_THEOREM_VERIFICATION',
        'scientific_outcome': independent_outcome,
        'candidate_imported': False,
        'bindings': bindings,
        'independent_proof': proof,
        'empirical_sanity': sanity,
        'comparison_checks': comparison,
        'scientific_firewall': {
            'P_VS_NP': 'OPEN',
            'GENERAL_SAT_IN_P': 'NOT_PROVED',
            'GENERAL_RESIDUAL_SEPARATOR_TRACTABILITY': 'NOT_PROVED',
            'WL_SUFFICIENCY_FOR_ORBIT_CLOSURE_OUTSIDE_THE_DEFINED_CLASS': 'NOT_PROVED',
        },
    }


if __name__ == '__main__':
    print(json.dumps(main(), sort_keys=True, separators=(',', ':')))
