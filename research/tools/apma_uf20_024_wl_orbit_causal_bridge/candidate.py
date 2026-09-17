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
PREREG = ROOT / 'research/TRUMP_UF20_024_WL_TO_ORBIT_CAUSAL_BRIDGE_DIAGNOSTIC_PREREGISTRATION_2026-09-17_v1.0.json'
REVIEW = ROOT / 'research/TRUMP_UF20_024_WL_TO_ORBIT_CAUSAL_BRIDGE_DIAGNOSTIC_REVIEW_2026-09-17_v1.0.json'
PARENT = ROOT / 'research/TRUMP_UF20_016_025_ONE_SHOT_CLASS_COVERAGE_WL_REPLICATION_RESULT_2026-09-17_v1.0.json'
SOURCE = ROOT / 'research/source_data/SATLIB_UF20_024_2026-09-17.cnf'
WL_IMPL = ROOT / 'research/tools/apma_uf20_wl_historical_closed_control_falsifier/candidate.py'
ORBIT_IMPL = ROOT / 'research/tools/apma_unseen_local_invariant_orbit_count/candidate.py'
FRESH_IMPL = ROOT / 'research/tools/apma_uf20_011_015_fresh_generic_pendant_wl_replication/candidate.py'
EXPECTED = {
    PREREG: 'd4e9bdf9b56deac4a279107296004f89ad778473',
    REVIEW: 'be207fa8dd42be23badc52adc78393d22808efce',
    PARENT: '15aa1bbb6b8bcd1f9820b46dcda2c92f1eb96fd4',
    SOURCE: '4281fd62dd97b011481a1196b373ab317dcd622a',
    WL_IMPL: '6b697fd8b3de4c83f8226b06399b6bad99953d4e',
    ORBIT_IMPL: 'a076cfc56d68aad0348415e313705da1f6b9cdcd',
    FRESH_IMPL: '9ec365ae27a6caa7b936cd33040e542f183ded99',
}
SEALED_PAIR = [5, 6]
SEALED_REDUCED_SHA = 'a43fb10ccc4dccab0f89d86a1c4d08bddfa2bf8c6ee7ca262bc6c8886db08619'


def blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()


def authority_guard() -> dict[str, Any]:
    bindings = {str(p.relative_to(ROOT)): blob(p) == h for p, h in EXPECTED.items()}
    review = json.loads(REVIEW.read_text())
    parent = json.loads(PARENT.read_text())
    row = next((r for r in parent.get('holdout_rows', []) if r.get('source') == 'UF20_024'), None)
    checks = {
        'bindings': all(bindings.values()),
        'review_authorized': review.get('review_verdict') == 'PASS_CLEAN_POST_REPLICATION_CAUSAL_DIAGNOSTIC_SPEC__AUTHORIZED_TO_IMPLEMENT_AND_EXECUTE_ONCE',
        'parent_execution': parent.get('execution_verdict') == 'PASS_INDEPENDENT_ONE_SHOT_EXECUTION_AND_EXACT_RECOMPUTATION',
        'parent_row_present': row is not None,
        'sealed_reduced_sha': bool(row) and row.get('reduced_raw_sha256') == SEALED_REDUCED_SHA,
        'sealed_route_closed': bool(row) and row.get('existing_portfolio', {}).get('label') == 'PORTFOLIO_CLOSED',
        'sealed_generator_edge': bool(row) and row.get('existing_portfolio', {}).get('E3', {}).get('generator_edges') == [SEALED_PAIR],
        'sealed_e3_status': bool(row) and row.get('existing_portfolio', {}).get('E3', {}).get('status') == 'ADMIT_ORBIT_COUNT_QUOTIENT_SAT',
    }
    return {'ok': all(checks.values()), 'checks': checks, 'bindings': bindings}


def nontrivial_classes(colors: dict[Any, int], keys: list[Any], unwrap) -> list[list[int]]:
    groups: dict[int, list[int]] = defaultdict(list)
    for key in keys:
        groups[colors[key]].append(int(unwrap(key)))
    return sorted((sorted(vs) for vs in groups.values() if len(vs) > 1), key=lambda x: (len(x), x))


def compute() -> dict[str, Any]:
    guard = authority_guard()
    if not guard['ok']:
        return {'verdict': 'HALT_AUTHORITY_OR_TARGET_BINDING_FAILURE', 'authority_guard': guard, 'resource_receipt': {'full_transposition_searches': 0, 'direct_exact_transposition_checks': 0}}

    clauses, formula_hash = frozen.parse_and_formula_hash(SOURCE)
    raw = frozen.projection_identity.normalize_projection('UF20_024', clauses)[0]
    reduced, degree1_variables, target_constraints = frozen.generic_round(raw)
    reduced_sha = frozen.csha(reduced)
    if reduced_sha != SEALED_REDUCED_SHA:
        return {'verdict': 'HALT_AUTHORITY_OR_TARGET_BINDING_FAILURE', 'reason': 'REDUCED_SHA_MISMATCH', 'observed': reduced_sha, 'resource_receipt': {'full_transposition_searches': 0, 'direct_exact_transposition_checks': 0}}

    nodes, adjacency, labels = wl_ref.incidence_structure(reduced)
    variables = [n for n in nodes if n[0] == 'v']
    colors1, rounds1 = wl_ref.wl1(nodes, adjacency, labels)
    colors2, rounds2 = wl_ref.wl2(nodes, adjacency, labels)
    classes1 = nontrivial_classes(colors1, variables, lambda k: k[1])
    diag_keys = [(v, v) for v in variables]
    classes2 = nontrivial_classes(colors2, diag_keys, lambda k: k[0][1])

    base = {
        'artifact_id': 'JANUS-TRUMP-UF20-024-WL-TO-ORBIT-CAUSAL-BRIDGE-DIAGNOSTIC-CANDIDATE-2026-09-17-v1.0',
        'source': 'UF20_024',
        'canonical_formula_sha256': formula_hash,
        'reduced_raw_sha256': reduced_sha,
        'degree1_variables': degree1_variables,
        'target_constraints': target_constraints,
        'wl1_nontrivial_variable_classes': classes1,
        'wl2_nontrivial_diagonal_variable_classes': classes2,
        'wl_rounds': {'wl1': rounds1, 'wl2': rounds2},
        'sealed_e3_generator_edge': SEALED_PAIR,
        'authority_guard': guard,
    }

    if len(classes1) != 1 or len(classes1[0]) != 2:
        return {**base, 'verdict': 'FALSIFIED_WL1_NONTRIVIAL_CLASS_NOT_UNIQUE_SIZE_TWO', 'resource_receipt': receipt(0)}
    if len(classes2) != 1 or len(classes2[0]) != 2:
        return {**base, 'verdict': 'FALSIFIED_WL2_DIAGONAL_NONTRIVIAL_CLASS_NOT_UNIQUE_SIZE_TWO', 'resource_receipt': receipt(0)}
    pair1, pair2 = classes1[0], classes2[0]
    if pair1 != pair2:
        return {**base, 'wl1_derived_pair': pair1, 'wl2_derived_pair': pair2, 'verdict': 'FALSIFIED_WL1_WL2_DERIVED_PAIRS_DISAGREE', 'resource_receipt': receipt(0)}
    if pair1 != SEALED_PAIR:
        return {**base, 'wl_derived_pair': pair1, 'verdict': 'FALSIFIED_WL_DERIVED_PAIR_DIFFERS_FROM_SEALED_E3_EDGE', 'resource_receipt': receipt(0)}

    formula = orbit.validate_and_normalize(reduced)
    exact = orbit.is_exact_transposition_automorphism(formula, pair1[0], pair1[1])
    verdict = 'PASS_WL_DERIVES_SEALED_E3_TRANSPOSITION_AND_DIRECT_EXACT_SWAP_VERIFIES' if exact else 'FALSIFIED_WL_DERIVED_PAIR_IS_NOT_AN_EXACT_TRANSPOSITION_AUTOMORPHISM'
    return {
        **base,
        'wl_derived_pair': pair1,
        'matches_sealed_e3_pair': pair1 == SEALED_PAIR,
        'direct_exact_transposition_automorphism': exact,
        'verdict': verdict,
        'resource_receipt': receipt(1),
        'claim_ceiling': 'POST_REPLICATION_SINGLE_INSTANCE_CONSTRUCTIVE_WITNESS_DIAGNOSTIC_ONLY',
        'scientific_firewall': {'P_VS_NP': 'OPEN', 'GENERAL_SAT_IN_P': 'NOT_PROVED', 'GENERAL_RESIDUAL_SEPARATOR_TRACTABILITY': 'NOT_PROVED', 'WL_SUFFICIENCY_FOR_ORBIT_CLOSURE': 'NOT_PROVED'},
    }


def receipt(direct_checks: int) -> dict[str, int]:
    return {
        'full_transposition_searches': 0,
        'automorphism_or_group_searches': 0,
        'direct_exact_transposition_checks': direct_checks,
        'sat_solver_invocations': 0,
        'orbit_quotient_state_enumerations': 0,
        'new_solver_rules': 0,
        'new_action_rules': 0,
        'new_carrier_mechanisms': 0,
        'wl_feature_or_threshold_retuning': 0,
    }


if __name__ == '__main__':
    print(json.dumps(compute(), sort_keys=True, separators=(',', ':')))
