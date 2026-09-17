from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from research.tools.apma_uf20_011_015_fresh_generic_pendant_wl_replication import independent_check as frozen

ROOT = Path(__file__).resolve().parents[3]
PREREG = ROOT / 'research/TRUMP_UF20_016_025_ONE_SHOT_CLASS_COVERAGE_WL_REPLICATION_PREREGISTRATION_2026-09-17_v1.0.json'
REVIEW = ROOT / 'research/TRUMP_UF20_016_025_ONE_SHOT_CLASS_COVERAGE_WL_REPLICATION_REVIEW_2026-09-17_v1.0.json'
SOURCE_FREEZE = ROOT / 'research/TRUMP_UF20_016_025_INDEPENDENT_CLASS_COVERAGE_SOURCE_ACQUISITION_RESULT_2026-09-17_v1.0.json'
FROZEN_CHECKER = ROOT / 'research/tools/apma_uf20_011_015_fresh_generic_pendant_wl_replication/independent_check.py'
EXPECTED = {
    PREREG: 'f077b541689d8e2a8e7027f17d7627a78ebb9820',
    REVIEW: '679391417b68acd2705027da2500a8c905c1902c',
    SOURCE_FREEZE: '32175d14369230ea4395c234a53a1207c2e8d10d',
    FROZEN_CHECKER: 'd47a89a377cb655c01d0470328635211792c63c4',
}
ORDER = tuple(f'UF20_{i:03d}' for i in range(16, 26))
FEATURES = frozen.FEATURES
BLOCK = frozen.BLOCK


def blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()


def authority_guard() -> dict[str, Any]:
    bindings = {str(path.relative_to(ROOT)): blob(path) == expected for path, expected in EXPECTED.items()}
    prereg = json.loads(PREREG.read_text())
    review = json.loads(REVIEW.read_text())
    source_freeze = json.loads(SOURCE_FREEZE.read_text())
    receipts = source_freeze.get('source_receipts', [])
    checks = {
        'authority_bindings': all(bindings.values()),
        'prereg_status': prereg.get('status') == 'FROZEN_AFTER_SOURCE_FREEZE__BEFORE_FIRST_PROJECTED_PENDANT_WL_OR_ROUTE_COMPUTATION_ON_UF20_016_TO_UF20_025',
        'review_authorized': review.get('review_verdict') == 'PASS_CLEAN_UF20_016_025_ONE_SHOT_CLASS_COVERAGE_WL_REPLICATION_SPEC__AUTHORIZED_TO_IMPLEMENT_AND_EXECUTE_ONCE',
        'source_freeze_pass': source_freeze.get('verdict') == 'PASS_UF20_016_025_DUAL_MIRROR_SOURCE_ACQUISITION_AND_FORMULA_FREEZE',
        'source_order_exact': tuple(row.get('source') for row in receipts) == ORDER,
        'source_count_exact': len(receipts) == 10,
        'source_verified': all(row.get('independent_verified') is True and row.get('status') == 'SOURCE_FROZEN' for row in receipts),
    }
    return {'ok': all(checks.values()), 'checks': checks, 'bindings': bindings}


def route_coverage_outcome(labels: list[str]) -> str:
    if labels == ['PORTFOLIO_CLOSED', 'PORTFOLIO_OPEN']:
        return 'PANEL_CONTAINS_BOTH_PORTFOLIO_OPEN_AND_PORTFOLIO_CLOSED'
    if labels == ['PORTFOLIO_OPEN']:
        return 'PANEL_CONTAINS_ONLY_PORTFOLIO_OPEN'
    if labels == ['PORTFOLIO_CLOSED']:
        return 'PANEL_CONTAINS_ONLY_PORTFOLIO_CLOSED'
    raise RuntimeError(f'UNEXPECTED_ROUTE_LABEL_SET:{labels}')


def wl_outcome(survivors: list[str]) -> str:
    if len(survivors) == len(FEATURES):
        return 'ALL_FOUR_FROZEN_WL_FEATURES_SURVIVE'
    if survivors:
        return 'PARTIAL_FROZEN_WL_FEATURE_SURVIVOR_SET'
    return 'ALL_FOUR_FROZEN_WL_FEATURES_FALSIFIED'


def main(candidate_path: Path) -> dict[str, Any]:
    candidate = json.loads(candidate_path.read_text())
    guard = authority_guard()
    if not guard['ok']:
        return {'verdict': 'FAIL_INDEPENDENT_AUTHORITY_BINDING', 'candidate_imported': False, 'authority_guard': guard}

    training_ok, training = frozen.regression()
    if candidate.get('verdict') == 'HALT_PREUNBLINDING_TRAINING_REGRESSION_FAILURE':
        good = (not training_ok and candidate.get('training_regression') == training and candidate.get('new_panel_formula_reads') == 0)
        return {
            'verdict': 'PASS_INDEPENDENT_PREUNBLINDING_HALT' if good else 'FAIL_INDEPENDENT_PREUNBLINDING_HALT',
            'candidate_imported': False,
            'new_panel_formula_reads': 0,
            'training_regression': training,
        }
    if not training_ok:
        return {'verdict': 'FAIL_INDEPENDENT_TRAINING_REGRESSION_DISAGREEMENT', 'candidate_imported': False, 'new_panel_formula_reads': 0, 'training_regression': training}

    source_freeze = json.loads(SOURCE_FREEZE.read_text())
    metadata = {row['source']: row for row in source_freeze['source_receipts']}
    rows = []
    for source in ORDER:
        meta = metadata[source]
        path = ROOT / meta['committed_copy_path']
        source_blob = blob(path)
        clauses, formula_hash = frozen.parse(path)
        if source_blob != meta['computed_committed_git_blob'] or formula_hash != meta['canonical_formula_sha256']:
            return {'verdict': 'FAIL_INDEPENDENT_SOURCE_BINDING', 'candidate_imported': False, 'reason': source}
        raw = frozen.projection_identity.normalize_projection(source, clauses)[0]
        reduced, degree1_variables, target_constraints = frozen.reduce_once(raw)
        wl = frozen.wl(reduced)
        route = frozen.route(reduced)
        rows.append({
            'source': source,
            'source_git_blob': source_blob,
            'canonical_formula_sha256': formula_hash,
            'projected_raw_sha256': frozen.csha(raw),
            'projected_variables': len(raw['variables']),
            'projected_constraints': len(raw['constraints']),
            'degree1_variables': degree1_variables,
            'target_constraints': target_constraints,
            'reduced_raw_sha256': frozen.csha(reduced),
            'reduced_variables': len(reduced['variables']),
            'reduced_constraints': len(reduced['constraints']),
            'wl_features': {feature: wl[feature] for feature in FEATURES},
            'wl_receipt': wl['_receipt'],
            'existing_portfolio': route,
        })

    scores = {}
    for feature in FEATURES:
        tests = []
        for row in rows:
            blocker = row['wl_features'][feature] == BLOCK[feature]
            open_label = row['existing_portfolio']['label'] == 'PORTFOLIO_OPEN'
            tests.append({
                'source': row['source'],
                'feature_value': row['wl_features'][feature],
                'blocker_value': BLOCK[feature],
                'is_blocker': blocker,
                'route_label': row['existing_portfolio']['label'],
                'matches_prediction': blocker == open_label,
            })
        scores[feature] = {
            'tests': tests,
            'matches': sum(test['matches_prediction'] for test in tests),
            'survives': all(test['matches_prediction'] for test in tests),
        }

    survivors = sorted(feature for feature in FEATURES if scores[feature]['survives'])
    labels = sorted({row['existing_portfolio']['label'] for row in rows})
    checks = {
        'candidate_evaluation_pass': candidate.get('verdict') == 'PASS_ONE_SHOT_CLASS_COVERAGE_WL_REPLICATION_EVALUATION',
        'training_exact': candidate.get('training_regression') == training,
        'holdout_rows_exact': candidate.get('holdout_rows') == rows,
        'scores_exact': candidate.get('per_feature_scores') == scores,
        'survivors_exact': candidate.get('surviving_features') == survivors,
        'falsified_exact': candidate.get('falsified_features') == sorted(set(FEATURES) - set(survivors)),
        'route_coverage_exact': candidate.get('route_class_coverage') == labels,
        'route_outcome_exact': candidate.get('route_coverage_outcome') == route_coverage_outcome(labels),
        'wl_outcome_exact': candidate.get('wl_replication_outcome') == wl_outcome(survivors),
        'one_round_only': candidate.get('resource_receipt', {}).get('generic_reduction_rounds_per_source') == 1 and candidate.get('resource_receipt', {}).get('iterated_peeling_rounds') == 0,
        'no_new_route_or_retuning': candidate.get('resource_receipt', {}).get('new_routes') == 0 and candidate.get('resource_receipt', {}).get('signed_route_invocations') == 0 and candidate.get('resource_receipt', {}).get('posthoc_thresholds_or_combinations') == 0,
        'firewall': candidate.get('scientific_firewall', {}).get('P_VS_NP') == 'OPEN' and candidate.get('scientific_firewall', {}).get('GENERAL_SAT_IN_P') == 'NOT_PROVED',
    }
    return {
        'artifact_id': 'JANUS-TRUMP-UF20-016-025-ONE-SHOT-CLASS-COVERAGE-WL-REPLICATION-INDEPENDENT-CHECK-2026-09-17-v1.0',
        'verdict': 'PASS_INDEPENDENT_UF20_016_025_CLASS_COVERAGE_WL_REPLICATION_VERIFICATION' if all(checks.values()) else 'FAIL_INDEPENDENT_UF20_016_025_CLASS_COVERAGE_WL_REPLICATION_VERIFICATION',
        'checks': checks,
        'candidate_imported': False,
        'independent_holdout_rows': rows,
        'independent_scores': scores,
        'independent_surviving_features': survivors,
        'route_class_coverage': labels,
        'route_coverage_outcome': route_coverage_outcome(labels),
        'wl_replication_outcome': wl_outcome(survivors),
        'new_panel_formula_reads': 10,
        'scientific_firewall': {'P_VS_NP': 'OPEN', 'GENERAL_SAT_IN_P': 'NOT_PROVED'},
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--candidate', required=True)
    args = parser.parse_args()
    result = main(Path(args.candidate))
    print(json.dumps(result, sort_keys=True, separators=(',', ':')))
    raise SystemExit(0 if result['verdict'].startswith('PASS_') else 1)
