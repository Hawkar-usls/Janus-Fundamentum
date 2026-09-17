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
CANDIDATE = ROOT / 'research/tools/apma_uf20_076_175_second_prospective_wl_orbit_bridge/candidate.py'
SOURCE_FREEZE = ROOT / 'research/TRUMP_UF20_076_175_SECOND_PROSPECTIVE_WL_ORBIT_BRIDGE_CORRECTED_SOURCE_ACQUISITION_RESULT_2026-09-17_v1.0.json'
PREREG = ROOT / 'research/TRUMP_UF20_076_175_SECOND_PROSPECTIVE_WL_ORBIT_BRIDGE_EVALUATION_PREREGISTRATION_2026-09-17_v1.0.json'
REVIEW = ROOT / 'research/TRUMP_UF20_076_175_SECOND_PROSPECTIVE_WL_ORBIT_BRIDGE_EVALUATION_REVIEW_2026-09-17_v1.0.json'
FRESH = ROOT / 'research/tools/apma_uf20_011_015_fresh_generic_pendant_wl_replication/candidate.py'
WL = ROOT / 'research/tools/apma_uf20_wl_historical_closed_control_falsifier/candidate.py'
ORBIT = ROOT / 'research/tools/apma_unseen_local_invariant_orbit_count/candidate.py'
EXPECTED = {
    CANDIDATE: '81d32fbcfd1ea3c257be92212604361302615186',
    SOURCE_FREEZE: '2be4d6d0dbdb8a771647d69900ced5a98fffe6b4',
    PREREG: '588d9d2281e19db15d30923313159a236dbad9e6',
    REVIEW: '80feb22b50c2083aa6c664dfdecf0dbbcbe27780',
    FRESH: '9ec365ae27a6caa7b936cd33040e542f183ded99',
    WL: '6b697fd8b3de4c83f8226b06399b6bad99953d4e',
    ORBIT: 'a076cfc56d68aad0348415e313705da1f6b9cdcd',
}
ORDER = tuple(f'UF20_{i:03d}' for i in range(76, 176))
CANDIDATE_MODULE = 'research.tools.apma_uf20_076_175_second_prospective_wl_orbit_bridge.candidate'


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
    variables = [n for n in nodes if n[0] == 'v']
    c1, r1 = wl_ref.wl1(nodes, adjacency, labels)
    c2, r2 = wl_ref.wl2(nodes, adjacency, labels)
    cl1 = classes(c1, variables, lambda n: n[1])
    diagonal = [(v, v) for v in variables]
    cl2 = classes(c2, diagonal, lambda p: p[0][1])
    pair = None
    exact = None
    checks = 0
    if len(cl1) == 1 and len(cl1[0]) == 2 and len(cl2) == 1 and cl2[0] == cl1[0]:
        pair = cl1[0]
        checks = 1
        exact = orbit.is_exact_transposition_automorphism(orbit.validate_and_normalize(reduced), pair[0], pair[1])
    return {
        'wl1_nontrivial_variable_classes': cl1,
        'wl2_nontrivial_diagonal_variable_classes': cl2,
        'wl_rounds': {'wl1': r1, 'wl2': r2},
        'wl_derived_pair': pair,
        'direct_exact_transposition_automorphism': exact,
        'prediction_positive': bool(pair is not None and exact is True),
        'direct_checks': checks,
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
    if any(int(v) != 0 for v in source_freeze.get('blind_barrier_receipt', {}).values()):
        return {'verdict': 'HALT_INDEPENDENT_SOURCE_FREEZE_BLINDNESS_FAILURE'}

    training_ok, training = frozen.training_regression()
    if not training_ok:
        return {'verdict': 'HALT_INDEPENDENT_TRAINING_REGRESSION_FAILURE'}

    metadata = {r['source']: r for r in source_freeze['source_receipts']}
    if tuple(r['source'] for r in source_freeze['source_receipts']) != ORDER:
        return {'verdict': 'HALT_INDEPENDENT_SOURCE_ORDER_FAILURE'}

    predictions = []
    prepared = []
    direct_checks = 0

    # Independent prediction stage. No route_row call before this loop is complete.
    for source in ORDER:
        meta = metadata[source]
        path = ROOT / meta['committed_copy_path']
        clauses, formula_hash = frozen.parse_and_formula_hash(path)
        source_blob = frozen.blob(path)
        if source_blob != meta['committed_git_blob'] or formula_hash != meta['canonical_formula_sha256']:
            return {'verdict': 'HALT_INDEPENDENT_SOURCE_BINDING_FAILURE', 'source': source}
        projected = frozen.projection_identity.normalize_projection(source, clauses)[0]
        reduced, degree1, targets = frozen.generic_round(projected)
        pred = prediction(reduced)
        direct_checks += pred.pop('direct_checks')
        predictions.append({
            'source': source,
            'source_git_blob': source_blob,
            'canonical_formula_sha256': formula_hash,
            'projected_raw_sha256': frozen.csha(projected),
            'reduced_raw_sha256': frozen.csha(reduced),
            'degree1_variables': degree1,
            'target_constraints': targets,
            **pred,
        })
        prepared.append((source, reduced))

    assert len(predictions) == 100
    digest = canonical_sha(predictions)
    prediction_positive_sources = [r['source'] for r in predictions if r['prediction_positive']]

    # Independent ground truth begins only after the 100-row prediction digest exists.
    pred_by = {r['source']: r for r in predictions}
    e3_closed = []
    misses = []
    open_false_positives = []
    portfolio_open = []
    portfolio_closed = []

    for source, reduced in prepared:
        route = frozen.route_row(reduced)
        pred = pred_by[source]
        e3 = route.get('E3', {})
        e3_positive = bool(e3.get('solver_authority') is True and e3.get('status') in frozen.CLOSED_ORBIT)
        edges = [sorted(map(int, edge)) for edge in (e3.get('generator_edges') or [])]
        recovered = bool(e3_positive and pred['prediction_positive'] and pred['wl_derived_pair'] in edges)
        is_open = route.get('label') == 'PORTFOLIO_OPEN'
        false_positive = bool(is_open and pred['prediction_positive'])
        if e3_positive:
            e3_closed.append(source)
        if e3_positive and not recovered:
            misses.append(source)
        if false_positive:
            open_false_positives.append(source)
        (portfolio_open if is_open else portfolio_closed).append(source)

    if misses:
        outcome = 'FALSIFIED_SECOND_PANEL_AT_LEAST_ONE_E3_CLOSED_CASE_NOT_RECOVERED'
    elif open_false_positives:
        outcome = 'FALSIFIED_SECOND_PANEL_AT_LEAST_ONE_PORTFOLIO_OPEN_WL_DIRECT_EXACT_FALSE_POSITIVE'
    elif len(e3_closed) < 2:
        outcome = 'PARTIAL_SECOND_PANEL_FEWER_THAN_TWO_E3_CLOSED_CASES'
    else:
        outcome = 'PASS_SECOND_PROSPECTIVE_MULTI_CLOSED_WL_TO_E3_WITNESS_REPLICATION'

    return {
        'verdict': 'PASS_INDEPENDENT_SECOND_PROSPECTIVE_WL_ORBIT_RECOMPUTATION',
        'scientific_outcome': outcome,
        'candidate_imported': False,
        'prediction_stage_count': 100,
        'prediction_stage_sha256': digest,
        'prediction_positive_sources': prediction_positive_sources,
        'e3_closed_sources': e3_closed,
        'e3_closed_misses': misses,
        'portfolio_open_sources': portfolio_open,
        'portfolio_closed_sources': portfolio_closed,
        'open_false_positives': open_false_positives,
        'direct_exact_checks': direct_checks,
        'prediction_full_transposition_searches': 0,
        'signed_route_invocations': 0,
        'bindings': bindings,
    }


def main() -> dict[str, Any]:
    parser = argparse.ArgumentParser()
    parser.add_argument('--candidate', required=True)
    args = parser.parse_args()
    candidate = json.loads(Path(args.candidate).read_text())
    independent = recompute()
    if independent.get('verdict') != 'PASS_INDEPENDENT_SECOND_PROSPECTIVE_WL_ORBIT_RECOMPUTATION':
        return independent

    summary = candidate.get('summary', {})
    checks = {
        'candidate_not_imported': independent['candidate_imported'] is False,
        'candidate_prediction_stage_count': candidate.get('prediction_stage_count') == 100,
        'prediction_digest': candidate.get('prediction_stage_sha256') == independent['prediction_stage_sha256'],
        'prediction_positive_sources': summary.get('wl_prediction_positive_sources') == independent['prediction_positive_sources'],
        'e3_closed_sources': summary.get('e3_closed_sources') == independent['e3_closed_sources'],
        'e3_closed_misses': summary.get('e3_closed_misses') == independent['e3_closed_misses'],
        'portfolio_open_sources': summary.get('portfolio_open_sources') == independent['portfolio_open_sources'],
        'portfolio_closed_sources': summary.get('portfolio_closed_sources') == independent['portfolio_closed_sources'],
        'open_false_positives': summary.get('open_false_positives') == independent['open_false_positives'],
        'scientific_outcome': candidate.get('verdict') == independent['scientific_outcome'],
        'resource_no_prediction_search': candidate.get('resource_receipt', {}).get('prediction_full_transposition_searches') == 0,
        'signed_route_zero': candidate.get('resource_receipt', {}).get('signed_route_invocations') == 0,
        'direct_checks_equal': candidate.get('resource_receipt', {}).get('prediction_direct_exact_checks') == independent['direct_exact_checks'],
        'no_new_mechanisms': all(candidate.get('resource_receipt', {}).get(k) == 0 for k in ('new_solver_mechanisms', 'new_action_rules', 'new_carrier_mechanisms', 'posthoc_thresholds_or_pair_rules')),
    }
    return {
        **independent,
        'comparison_checks': checks,
        'candidate_verdict': candidate.get('verdict'),
        'verdict': 'PASS_INDEPENDENT_SECOND_PROSPECTIVE_WL_ORBIT_BRIDGE_VERIFICATION' if all(checks.values()) else 'FAIL_INDEPENDENT_SECOND_PROSPECTIVE_WL_ORBIT_BRIDGE_MISMATCH',
    }


if __name__ == '__main__':
    print(json.dumps(main(), sort_keys=True, separators=(',', ':')))
