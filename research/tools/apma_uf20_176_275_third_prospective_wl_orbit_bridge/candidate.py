from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from research.tools.apma_uf20_011_015_fresh_generic_pendant_wl_replication import candidate as frozen
from research.tools.apma_uf20_wl_historical_closed_control_falsifier import candidate as wl_ref
from research.tools.apma_unseen_local_invariant_orbit_count import candidate as orbit

ROOT = Path(__file__).resolve().parents[3]
PREREG = ROOT / 'research/TRUMP_UF20_176_275_THIRD_PROSPECTIVE_WL_ORBIT_BRIDGE_EVALUATION_PREREGISTRATION_2026-09-17_v1.0.json'
REVIEW = ROOT / 'research/TRUMP_UF20_176_275_THIRD_PROSPECTIVE_WL_ORBIT_BRIDGE_EVALUATION_REVIEW_2026-09-17_v1.0.json'
SOURCE_FREEZE = ROOT / 'research/TRUMP_UF20_176_275_THIRD_PROSPECTIVE_WL_ORBIT_BRIDGE_SOURCE_ACQUISITION_RESULT_2026-09-17_v1.0.json'
SECOND_RESULT = ROOT / 'research/TRUMP_UF20_076_175_SECOND_PROSPECTIVE_WL_ORBIT_BRIDGE_REPLICATION_RESULT_2026-09-17_v1.0.json'
FRESH = ROOT / 'research/tools/apma_uf20_011_015_fresh_generic_pendant_wl_replication/candidate.py'
WL = ROOT / 'research/tools/apma_uf20_wl_historical_closed_control_falsifier/candidate.py'
ORBIT = ROOT / 'research/tools/apma_unseen_local_invariant_orbit_count/candidate.py'
EXPECTED = {
    PREREG: '2fe7eceb55cfe7ee731107536ebb571bebe0546c',
    REVIEW: '46db2e6678c260bc7c8fc27ada6ab1e875e53449',
    SOURCE_FREEZE: '98b059f4116407bf99fb2933b1e58cf1d09eb321',
    SECOND_RESULT: 'c9946977912e8761914d9bcd1957977285da42e7',
    FRESH: '9ec365ae27a6caa7b936cd33040e542f183ded99',
    WL: '6b697fd8b3de4c83f8226b06399b6bad99953d4e',
    ORBIT: 'a076cfc56d68aad0348415e313705da1f6b9cdcd',
}
ORDER = tuple(f'UF20_{i:03d}' for i in range(176, 276))


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


def guard() -> dict[str, Any]:
    bindings = {str(path.relative_to(ROOT)): blob(path) == expected for path, expected in EXPECTED.items()}
    prereg = json.loads(PREREG.read_text())
    review = json.loads(REVIEW.read_text())
    source_freeze = json.loads(SOURCE_FREEZE.read_text())
    second = json.loads(SECOND_RESULT.read_text())
    receipts = source_freeze.get('source_receipts', [])
    checks = {
        'authority_bindings': all(bindings.values()),
        'prereg_frozen_before_structural_execution': prereg.get('status') == 'FROZEN_AFTER_SOURCE_FREEZE__BEFORE_FIRST_WL_CLASS_MEMBERSHIP_OR_E3_WITNESS_COMPUTATION_ON_THE_THIRD_ONE_HUNDRED_SOURCE_PANEL',
        'review_authorized': review.get('review_verdict') == 'PASS_CLEAN_THIRD_PROSPECTIVE_ONE_HUNDRED_SOURCE_WL_ORBIT_BRIDGE_SPEC__AUTHORIZED_TO_IMPLEMENT_AND_EXECUTE_ONCE',
        'source_freeze_pass': source_freeze.get('verdict') == 'PASS_UF20_176_275_DUAL_MIRROR_SOURCE_ACQUISITION_AND_FORMULA_FREEZE',
        'source_freeze_independent': source_freeze.get('execution', {}).get('independent_verdict') == 'PASS_INDEPENDENT_UF20_176_275_SOURCE_FREEZE_VERIFICATION',
        'source_count': len(receipts) == 100,
        'source_order': tuple(row.get('source') for row in receipts) == ORDER,
        'sources_independently_frozen': all(row.get('independent_verified') is True and row.get('status') == 'SOURCE_FROZEN' for row in receipts),
        'source_freeze_structural_zero': all(int(value) == 0 for value in source_freeze.get('blind_barrier_receipt', {}).values()),
        'second_panel_independent_pass': second.get('execution_verdict') == 'PASS_INDEPENDENT_SECOND_PROSPECTIVE_RECOMPUTATION',
        'second_panel_partial_only_for_coverage': second.get('scientific_outcome') == 'PARTIAL_SECOND_PANEL_FEWER_THAN_TWO_E3_CLOSED_CASES',
        'second_panel_no_misses': second.get('summary', {}).get('e3_closed_misses') == [],
        'second_panel_no_open_false_positives': second.get('summary', {}).get('open_false_positives') == [],
    }
    return {'ok': all(checks.values()), 'checks': checks, 'bindings': bindings}


def main() -> dict[str, Any]:
    authority = guard()
    if not authority['ok']:
        return {
            'verdict': 'HALT_AUTHORITY_OR_SOURCE_BINDING_FAILURE',
            'authority_guard': authority,
            'third_panel_structural_reads': 0,
            'scientific_firewall': {'P_VS_NP': 'OPEN', 'GENERAL_SAT_IN_P': 'NOT_PROVED'},
        }

    training_ok, training = frozen.training_regression()
    if not training_ok:
        return {
            'verdict': 'HALT_PREUNBLINDING_TRAINING_REGRESSION_FAILURE',
            'authority_guard': authority,
            'training_regression': training,
            'third_panel_structural_reads': 0,
        }

    source_freeze = json.loads(SOURCE_FREEZE.read_text())
    metadata = {row['source']: row for row in source_freeze['source_receipts']}
    prediction_rows = []
    prepared = []
    direct_checks = 0

    # Blind prediction stage: no route_row / E1 / E2 / E3 ground truth call is permitted here.
    for source in ORDER:
        meta = metadata[source]
        path = ROOT / meta['committed_copy_path']
        source_blob = frozen.blob(path)
        clauses, formula_hash = frozen.parse_and_formula_hash(path)
        if source_blob != meta['committed_git_blob'] or formula_hash != meta['canonical_formula_sha256']:
            return {
                'verdict': 'HALT_AUTHORITY_OR_SOURCE_BINDING_FAILURE',
                'reason': source,
                'training_regression': training,
                'third_panel_structural_reads': len(prediction_rows),
            }
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

    # Ground truth starts only after all 100 prediction rows and their digest exist.
    prediction_by_source = {row['source']: row for row in prediction_rows}
    ground_truth_rows = []
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
        pair = pred['wl_derived_pair']
        recovered = bool(e3_positive and pred['prediction_positive'] and pair in generator_edges)
        is_open = route.get('label') == 'PORTFOLIO_OPEN'
        false_positive = bool(is_open and pred['prediction_positive'])
        ground_truth_rows.append({
            'source': source,
            'portfolio_label': route.get('label'),
            'closure': route.get('closure'),
            'E1': route.get('E1'),
            'E2': route.get('E2'),
            'E3': route.get('E3'),
            'e3_positive': e3_positive,
            'e3_generator_edges': generator_edges,
            'wl_pair_recovered_e3_witness': recovered,
            'open_false_positive': false_positive,
        })
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
        'artifact_id': 'JANUS-TRUMP-UF20-176-275-THIRD-PROSPECTIVE-WL-ORBIT-BRIDGE-CANDIDATE-2026-09-17-v1.0',
        'gate': 'TRUMP_UF20_176_275_THIRD_PROSPECTIVE_WL_ORBIT_BRIDGE_EVALUATION_GATE',
        'verdict': outcome,
        'authority_guard': authority,
        'training_regression': training,
        'prediction_stage_completed_before_ground_truth': True,
        'prediction_stage_count': 100,
        'prediction_stage_sha256': prediction_digest,
        'prediction_rows': prediction_rows,
        'ground_truth_rows': ground_truth_rows,
        'summary': {
            'e3_closed_sources': e3_closed_sources,
            'e3_closed_count': len(e3_closed_sources),
            'e3_closed_misses': e3_closed_misses,
            'portfolio_open_sources': portfolio_open_sources,
            'portfolio_open_count': len(portfolio_open_sources),
            'portfolio_closed_sources': portfolio_closed_sources,
            'portfolio_closed_count': len(portfolio_closed_sources),
            'open_false_positives': open_false_positives,
            'wl_prediction_positive_sources': prediction_positive_sources,
        },
        'resource_receipt': {
            'third_panel_sources_read': 100,
            'generic_reduction_rounds_per_source': 1,
            'iterated_peeling_rounds': 0,
            'prediction_full_transposition_searches': 0,
            'prediction_direct_exact_checks': direct_checks,
            'existing_portfolio_replays': 100,
            'signed_route_invocations': 0,
            'new_solver_mechanisms': 0,
            'new_reduction_rules': 0,
            'new_action_rules': 0,
            'new_carrier_mechanisms': 0,
            'new_adapters': 0,
            'new_quotients': 0,
            'posthoc_thresholds_or_pair_rules': 0,
            'prior_partial_closed_cases_counted_toward_third_panel_threshold': 0,
        },
        'claim_ceiling': 'THIRD_PROSPECTIVE_FINITE_ONE_HUNDRED_SOURCE_REPLICATION_OF_THE_FROZEN_WL_TO_EXACT_TRANSPOSITION_WITNESS_RULE_AGAINST_THE_EXISTING_E3_GROUND_TRUTH_ONLY',
        'scientific_firewall': {
            'P_VS_NP': 'OPEN',
            'GENERAL_SAT_IN_P': 'NOT_PROVED',
            'GENERAL_RESIDUAL_SEPARATOR_TRACTABILITY': 'NOT_PROVED',
            'WL_SUFFICIENCY_FOR_ORBIT_CLOSURE': 'NOT_PROVED',
        },
    }


if __name__ == '__main__':
    print(json.dumps(main(), sort_keys=True, separators=(',', ':')))
