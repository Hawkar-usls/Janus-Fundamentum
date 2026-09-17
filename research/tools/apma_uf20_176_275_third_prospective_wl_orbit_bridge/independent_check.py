from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

from research.tools.apma_uf20_011_015_fresh_generic_pendant_wl_replication import candidate as frozen
from research.tools.apma_uf20_wl_historical_closed_control_falsifier import candidate as wl_ref
from research.tools.apma_unseen_local_invariant_orbit_count import candidate as orbit

ROOT = Path(__file__).resolve().parents[3]
CANDIDATE = ROOT / 'research/tools/apma_uf20_176_275_third_prospective_wl_orbit_bridge/candidate.py'
SOURCE_FREEZE = ROOT / 'research/TRUMP_UF20_176_275_THIRD_PROSPECTIVE_WL_ORBIT_BRIDGE_SOURCE_ACQUISITION_RESULT_2026-09-17_v1.0.json'
PREREG = ROOT / 'research/TRUMP_UF20_176_275_THIRD_PROSPECTIVE_WL_ORBIT_BRIDGE_EVALUATION_PREREGISTRATION_2026-09-17_v1.0.json'
REVIEW = ROOT / 'research/TRUMP_UF20_176_275_THIRD_PROSPECTIVE_WL_ORBIT_BRIDGE_EVALUATION_REVIEW_2026-09-17_v1.0.json'
FRESH = ROOT / 'research/tools/apma_uf20_011_015_fresh_generic_pendant_wl_replication/candidate.py'
WL = ROOT / 'research/tools/apma_uf20_wl_historical_closed_control_falsifier/candidate.py'
ORBIT = ROOT / 'research/tools/apma_unseen_local_invariant_orbit_count/candidate.py'
EXPECTED = {
    CANDIDATE: 'f7f3f0481f31a8ea85163edc1eb973fba0d1085c',
    SOURCE_FREEZE: '98b059f4116407bf99fb2933b1e58cf1d09eb321',
    PREREG: '2fe7eceb55cfe7ee731107536ebb571bebe0546c',
    REVIEW: '46db2e6678c260bc7c8fc27ada6ab1e875e53449',
    FRESH: '9ec365ae27a6caa7b936cd33040e542f183ded99',
    WL: '6b697fd8b3de4c83f8226b06399b6bad99953d4e',
    ORBIT: 'a076cfc56d68aad0348415e313705da1f6b9cdcd',
}
ORDER = tuple(f'UF20_{i:03d}' for i in range(176, 276))
CANDIDATE_MODULE = 'research.tools.apma_uf20_176_275_third_prospective_wl_orbit_bridge.candidate'


def blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()


def canonical_sha(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def classes(colors, keys, value_of):
    groups = defaultdict(list)
    for key in keys:
        groups[colors[key]].append(int(value_of(key)))
    out = [sorted(values) for values in groups.values() if len(values) > 1]
    out.sort(key=lambda x: (len(x), x))
    return out


def prediction(reduced: dict[str, Any]) -> dict[str, Any]:
    nodes, adjacency, labels = wl_ref.incidence_structure(reduced)
    variables = [node for node in nodes if node[0] == 'v']
    colors1, rounds1 = wl_ref.wl1(nodes, adjacency, labels)
    colors2, rounds2 = wl_ref.wl2(nodes, adjacency, labels)
    classes1 = classes(colors1, variables, lambda node: node[1])
    diagonal = [(v, v) for v in variables]
    classes2 = classes(colors2, diagonal, lambda pair: pair[0][1])
    pair = None
    exact = None
    direct_checks = 0
    if len(classes1) == 1 and len(classes1[0]) == 2 and len(classes2) == 1 and classes2[0] == classes1[0]:
        pair = classes1[0]
        direct_checks = 1
        exact = orbit.is_exact_transposition_automorphism(
            orbit.validate_and_normalize(reduced), pair[0], pair[1]
        )
    return {
        'wl1_nontrivial_variable_classes': classes1,
        'wl2_nontrivial_diagonal_variable_classes': classes2,
        'wl_rounds': {'wl1': rounds1, 'wl2': rounds2},
        'wl_derived_pair': pair,
        'direct_exact_transposition_automorphism': exact,
        'prediction_positive': bool(pair is not None and exact is True),
        'direct_checks': direct_checks,
    }


def recompute() -> dict[str, Any]:
    bindings = {str(path.relative_to(ROOT)): blob(path) == expected for path, expected in EXPECTED.items()}
    if not all(bindings.values()):
        return {'verdict': 'HALT_INDEPENDENT_AUTHORITY_BINDING_FAILURE', 'bindings': bindings}
    if CANDIDATE_MODULE in sys.modules:
        return {'verdict': 'HALT_INDEPENDENT_CANDIDATE_IMPORT_VIOLATION'}

    source_freeze = json.loads(SOURCE_FREEZE.read_text())
    if source_freeze.get('execution', {}).get('sources_verified') != 100:
        return {'verdict': 'HALT_INDEPENDENT_SOURCE_FREEZE_COUNT_FAILURE'}
    if any(int(value) != 0 for value in source_freeze.get('blind_barrier_receipt', {}).values()):
        return {'verdict': 'HALT_INDEPENDENT_SOURCE_FREEZE_BLINDNESS_FAILURE'}
    if tuple(row.get('source') for row in source_freeze.get('source_receipts', [])) != ORDER:
        return {'verdict': 'HALT_INDEPENDENT_SOURCE_ORDER_FAILURE'}

    training_ok, training = frozen.training_regression()
    if not training_ok:
        return {'verdict': 'HALT_INDEPENDENT_TRAINING_REGRESSION_FAILURE'}

    metadata = {row['source']: row for row in source_freeze['source_receipts']}
    prediction_rows = []
    prepared = []
    direct_checks = 0

    # Independent prediction stage; no route_row call until all 100 prediction rows and digest exist.
    for source in ORDER:
        meta = metadata[source]
        path = ROOT / meta['committed_copy_path']
        clauses, formula_hash = frozen.parse_and_formula_hash(path)
        source_blob = frozen.blob(path)
        if source_blob != meta['committed_git_blob'] or formula_hash != meta['canonical_formula_sha256']:
            return {'verdict': 'HALT_INDEPENDENT_SOURCE_BINDING_FAILURE', 'source': source}
        projected = frozen.projection_identity.normalize_projection(source, clauses)[0]
        reduced, degree1_variables, target_constraints = frozen.generic_round(projected)
        pred = prediction(reduced)
        direct_checks += pred.pop('direct_checks')
        prediction_rows.append({
            'source': source,
            'source_git_blob': source_blob,
            'canonical_formula_sha256': formula_hash,
            'projected_raw_sha256': frozen.csha(projected),
            'reduced_raw_sha256': frozen.csha(reduced),
            'degree1_variables': degree1_variables,
            'target_constraints': target_constraints,
            **pred,
        })
        prepared.append((source, reduced))

    assert len(prediction_rows) == 100
    prediction_digest = canonical_sha(prediction_rows)
    prediction_positive_sources = [row['source'] for row in prediction_rows if row['prediction_positive']]

    # Independent ground truth starts only now.
    prediction_by_source = {row['source']: row for row in prediction_rows}
    e3_closed_sources = []
    e3_closed_misses = []
    open_false_positives = []
    portfolio_open_sources = []
    portfolio_closed_sources = []

    for source, reduced in prepared:
        route = frozen.route_row(reduced)
        pred = prediction_by_source[source]
        e3 = route.get('E3', {})
        e3_positive = bool(e3.get('solver_authority') is True and e3.get('status') in frozen.CLOSED_ORBIT)
        generator_edges = [sorted(map(int, edge)) for edge in (e3.get('generator_edges') or [])]
        recovered = bool(e3_positive and pred['prediction_positive'] and pred['wl_derived_pair'] in generator_edges)
        is_open = route.get('label') == 'PORTFOLIO_OPEN'
        false_positive = bool(is_open and pred['prediction_positive'])
        if e3_positive:
            e3_closed_sources.append(source)
        if e3_positive and not recovered:
            e3_closed_misses.append(source)
        if false_positive:
            open_false_positives.append(source)
        (portfolio_open_sources if is_open else portfolio_closed_sources).append(source)

    if e3_closed_misses:
        outcome = 'FALSIFIED_THIRD_PANEL_AT_LEAST_ONE_E3_CLOSED_CASE_NOT_RECOVERED'
    elif open_false_positives:
        outcome = 'FALSIFIED_THIRD_PANEL_AT_LEAST_ONE_PORTFOLIO_OPEN_WL_DIRECT_EXACT_FALSE_POSITIVE'
    elif len(e3_closed_sources) < 2:
        outcome = 'PARTIAL_THIRD_PANEL_FEWER_THAN_TWO_E3_CLOSED_CASES'
    else:
        outcome = 'PASS_THIRD_PROSPECTIVE_MULTI_CLOSED_WL_TO_E3_WITNESS_REPLICATION'

    return {
        'verdict': 'PASS_INDEPENDENT_THIRD_PROSPECTIVE_WL_ORBIT_RECOMPUTATION',
        'scientific_outcome': outcome,
        'candidate_imported': False,
        'prediction_stage_count': 100,
        'prediction_stage_sha256': prediction_digest,
        'prediction_positive_sources': prediction_positive_sources,
        'e3_closed_sources': e3_closed_sources,
        'e3_closed_misses': e3_closed_misses,
        'portfolio_open_sources': portfolio_open_sources,
        'portfolio_closed_sources': portfolio_closed_sources,
        'open_false_positives': open_false_positives,
        'direct_exact_checks': direct_checks,
        'prediction_full_transposition_searches': 0,
        'signed_route_invocations': 0,
        'prior_partial_closed_cases_counted_toward_third_panel_threshold': 0,
        'bindings': bindings,
    }


def main() -> dict[str, Any]:
    parser = argparse.ArgumentParser()
    parser.add_argument('--candidate', required=True)
    args = parser.parse_args()
    candidate = json.loads(Path(args.candidate).read_text())
    independent = recompute()
    if independent.get('verdict') != 'PASS_INDEPENDENT_THIRD_PROSPECTIVE_WL_ORBIT_RECOMPUTATION':
        return independent

    summary = candidate.get('summary', {})
    receipt = candidate.get('resource_receipt', {})
    checks = {
        'candidate_not_imported': independent['candidate_imported'] is False,
        'prediction_stage_count': candidate.get('prediction_stage_count') == 100,
        'prediction_stage_completed_before_ground_truth': candidate.get('prediction_stage_completed_before_ground_truth') is True,
        'prediction_digest': candidate.get('prediction_stage_sha256') == independent['prediction_stage_sha256'],
        'prediction_positive_sources': summary.get('wl_prediction_positive_sources') == independent['prediction_positive_sources'],
        'e3_closed_sources': summary.get('e3_closed_sources') == independent['e3_closed_sources'],
        'e3_closed_misses': summary.get('e3_closed_misses') == independent['e3_closed_misses'],
        'portfolio_open_sources': summary.get('portfolio_open_sources') == independent['portfolio_open_sources'],
        'portfolio_closed_sources': summary.get('portfolio_closed_sources') == independent['portfolio_closed_sources'],
        'open_false_positives': summary.get('open_false_positives') == independent['open_false_positives'],
        'scientific_outcome': candidate.get('verdict') == independent['scientific_outcome'],
        'resource_no_prediction_search': receipt.get('prediction_full_transposition_searches') == 0,
        'signed_route_zero': receipt.get('signed_route_invocations') == 0,
        'direct_checks_equal': receipt.get('prediction_direct_exact_checks') == independent['direct_exact_checks'],
        'prior_partial_cases_not_counted': receipt.get('prior_partial_closed_cases_counted_toward_third_panel_threshold') == 0 and independent['prior_partial_closed_cases_counted_toward_third_panel_threshold'] == 0,
        'no_new_mechanisms': all(receipt.get(key) == 0 for key in (
            'new_solver_mechanisms', 'new_reduction_rules', 'new_action_rules', 'new_carrier_mechanisms', 'new_adapters', 'new_quotients', 'posthoc_thresholds_or_pair_rules'
        )),
    }
    return {
        **independent,
        'comparison_checks': checks,
        'candidate_verdict': candidate.get('verdict'),
        'verdict': 'PASS_INDEPENDENT_THIRD_PROSPECTIVE_WL_ORBIT_BRIDGE_VERIFICATION' if all(checks.values()) else 'FAIL_INDEPENDENT_THIRD_PROSPECTIVE_WL_ORBIT_BRIDGE_MISMATCH',
    }


if __name__ == '__main__':
    print(json.dumps(main(), sort_keys=True, separators=(',', ':')))
