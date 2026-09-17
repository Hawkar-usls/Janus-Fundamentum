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
PREREG = ROOT / 'research/TRUMP_UF20_024_WL_TO_ORBIT_CAUSAL_BRIDGE_DIAGNOSTIC_PREREGISTRATION_2026-09-17_v1.0.json'
REVIEW = ROOT / 'research/TRUMP_UF20_024_WL_TO_ORBIT_CAUSAL_BRIDGE_DIAGNOSTIC_REVIEW_2026-09-17_v1.0.json'
PARENT = ROOT / 'research/TRUMP_UF20_016_025_ONE_SHOT_CLASS_COVERAGE_WL_REPLICATION_RESULT_2026-09-17_v1.0.json'
SOURCE = ROOT / 'research/source_data/SATLIB_UF20_024_2026-09-17.cnf'
CANDIDATE = ROOT / 'research/tools/apma_uf20_024_wl_orbit_causal_bridge/candidate.py'
EXPECTED = {
    PREREG: 'd4e9bdf9b56deac4a279107296004f89ad778473',
    REVIEW: 'be207fa8dd42be23badc52adc78393d22808efce',
    PARENT: '15aa1bbb6b8bcd1f9820b46dcda2c92f1eb96fd4',
    SOURCE: '4281fd62dd97b011481a1196b373ab317dcd622a',
    CANDIDATE: '0b60ce32c06b0302c12f0eb120943ae33e1bcfb9',
}
SEALED_PAIR = [5, 6]
SEALED_REDUCED_SHA = 'a43fb10ccc4dccab0f89d86a1c4d08bddfa2bf8c6ee7ca262bc6c8886db08619'
CANDIDATE_MODULE = 'research.tools.apma_uf20_024_wl_orbit_causal_bridge.candidate'


def blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()


def group_nontrivial(colors: dict[Any, int], keys: list[Any], value_of) -> list[list[int]]:
    buckets: dict[int, list[int]] = defaultdict(list)
    for key in keys:
        buckets[int(colors[key])].append(int(value_of(key)))
    answer = [sorted(values) for values in buckets.values() if len(values) >= 2]
    answer.sort(key=lambda values: (len(values), values))
    return answer


def expected_outcome(classes1: list[list[int]], classes2: list[list[int]], exact: bool | None) -> str:
    if len(classes1) != 1 or len(classes1[0]) != 2:
        return 'FALSIFIED_WL1_NONTRIVIAL_CLASS_NOT_UNIQUE_SIZE_TWO'
    if len(classes2) != 1 or len(classes2[0]) != 2:
        return 'FALSIFIED_WL2_DIAGONAL_NONTRIVIAL_CLASS_NOT_UNIQUE_SIZE_TWO'
    if classes1[0] != classes2[0]:
        return 'FALSIFIED_WL1_WL2_DERIVED_PAIRS_DISAGREE'
    if classes1[0] != SEALED_PAIR:
        return 'FALSIFIED_WL_DERIVED_PAIR_DIFFERS_FROM_SEALED_E3_EDGE'
    if exact is not True:
        return 'FALSIFIED_WL_DERIVED_PAIR_IS_NOT_AN_EXACT_TRANSPOSITION_AUTOMORPHISM'
    return 'PASS_WL_DERIVES_SEALED_E3_TRANSPOSITION_AND_DIRECT_EXACT_SWAP_VERIFIES'


def recompute() -> dict[str, Any]:
    bindings = {str(p.relative_to(ROOT)): blob(p) == h for p, h in EXPECTED.items()}
    if not all(bindings.values()):
        return {'verdict': 'HALT_INDEPENDENT_AUTHORITY_BINDING_FAILURE', 'bindings': bindings}
    if CANDIDATE_MODULE in sys.modules:
        return {'verdict': 'HALT_INDEPENDENT_CANDIDATE_IMPORT_VIOLATION'}

    clauses, formula_hash = frozen.parse_and_formula_hash(SOURCE)
    projected = frozen.projection_identity.normalize_projection('UF20_024', clauses)[0]
    reduced, degree1_variables, target_constraints = frozen.generic_round(projected)
    reduced_sha = frozen.csha(reduced)
    if reduced_sha != SEALED_REDUCED_SHA:
        return {'verdict': 'HALT_INDEPENDENT_TARGET_RECONSTRUCTION_FAILURE', 'observed_reduced_sha256': reduced_sha}

    nodes, adjacency, labels = wl_ref.incidence_structure(reduced)
    variables = [node for node in nodes if node[0] == 'v']
    c1, rounds1 = wl_ref.wl1(nodes, adjacency, labels)
    c2, rounds2 = wl_ref.wl2(nodes, adjacency, labels)
    classes1 = group_nontrivial(c1, variables, lambda node: node[1])
    diagonal = [(node, node) for node in variables]
    classes2 = group_nontrivial(c2, diagonal, lambda pair: pair[0][1])

    exact = None
    direct_checks = 0
    if len(classes1) == 1 and len(classes1[0]) == 2 and len(classes2) == 1 and classes2[0] == classes1[0] and classes1[0] == SEALED_PAIR:
        normalized = orbit.validate_and_normalize(reduced)
        direct_checks = 1
        exact = orbit.is_exact_transposition_automorphism(normalized, SEALED_PAIR[0], SEALED_PAIR[1])
    derived_pair = classes1[0] if len(classes1) == 1 and len(classes1[0]) == 2 else None
    scientific_outcome = expected_outcome(classes1, classes2, exact)

    return {
        'verdict': 'PASS_INDEPENDENT_WL_ORBIT_CAUSAL_DIAGNOSTIC_RECOMPUTATION',
        'scientific_outcome': scientific_outcome,
        'candidate_imported': CANDIDATE_MODULE in sys.modules,
        'canonical_formula_sha256': formula_hash,
        'reduced_raw_sha256': reduced_sha,
        'degree1_variables': degree1_variables,
        'target_constraints': target_constraints,
        'wl1_nontrivial_variable_classes': classes1,
        'wl2_nontrivial_diagonal_variable_classes': classes2,
        'wl_rounds': {'wl1': rounds1, 'wl2': rounds2},
        'derived_pair': derived_pair,
        'sealed_e3_generator_edge': SEALED_PAIR,
        'direct_exact_transposition_automorphism': exact,
        'resource_receipt': {
            'full_transposition_searches': 0,
            'automorphism_or_group_searches': 0,
            'direct_exact_transposition_checks': direct_checks,
            'sat_solver_invocations': 0,
            'orbit_quotient_state_enumerations': 0,
        },
    }


def main() -> dict[str, Any]:
    parser = argparse.ArgumentParser()
    parser.add_argument('--candidate', required=True)
    args = parser.parse_args()
    candidate = json.loads(Path(args.candidate).read_text())
    independent = recompute()
    if independent.get('verdict') != 'PASS_INDEPENDENT_WL_ORBIT_CAUSAL_DIAGNOSTIC_RECOMPUTATION':
        return independent

    outcome = independent['scientific_outcome']
    checks = {
        'candidate_not_imported': independent['candidate_imported'] is False,
        'reduced_sha_equal': candidate.get('reduced_raw_sha256') == independent['reduced_raw_sha256'],
        'wl1_classes_equal': candidate.get('wl1_nontrivial_variable_classes') == independent['wl1_nontrivial_variable_classes'],
        'wl2_classes_equal': candidate.get('wl2_nontrivial_diagonal_variable_classes') == independent['wl2_nontrivial_diagonal_variable_classes'],
        'candidate_verdict_exact': candidate.get('verdict') == outcome,
        'resource_no_search': candidate.get('resource_receipt', {}).get('full_transposition_searches') == 0 and independent['resource_receipt']['full_transposition_searches'] == 0,
        'direct_check_cap': candidate.get('resource_receipt', {}).get('direct_exact_transposition_checks', 0) <= 1 and independent['resource_receipt']['direct_exact_transposition_checks'] <= 1,
    }
    if outcome == 'PASS_WL_DERIVES_SEALED_E3_TRANSPOSITION_AND_DIRECT_EXACT_SWAP_VERIFIES':
        checks['pair_equal'] = candidate.get('wl_derived_pair') == independent['derived_pair'] == SEALED_PAIR
        checks['direct_swap_equal'] = candidate.get('direct_exact_transposition_automorphism') is True and independent['direct_exact_transposition_automorphism'] is True

    return {
        **independent,
        'comparison_checks': checks,
        'candidate_verdict': candidate.get('verdict'),
        'verdict': 'PASS_INDEPENDENT_WL_ORBIT_CAUSAL_DIAGNOSTIC_VERIFICATION' if all(checks.values()) else 'FAIL_INDEPENDENT_WL_ORBIT_CAUSAL_DIAGNOSTIC_MISMATCH',
    }


if __name__ == '__main__':
    print(json.dumps(main(), sort_keys=True, separators=(',', ':')))
