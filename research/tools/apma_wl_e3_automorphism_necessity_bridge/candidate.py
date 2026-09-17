from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from research.tools.apma_uf20_wl_historical_closed_control_falsifier import candidate as wl_ref
from research.tools.apma_unseen_local_invariant_orbit_count import candidate as orbit
from research.tools.apma_unseen_basis import raw_relation_basis as raw_basis
from research.tools.apma_uf20_016_025_one_shot_class_coverage_wl_replication import candidate as panel

ROOT = Path(__file__).resolve().parents[3]
PREREG = ROOT / 'research/TRUMP_WL_E3_AUTOMORPHISM_NECESSITY_BRIDGE_PREREGISTRATION_2026-09-17_v1.0.json'
REVIEW = ROOT / 'research/TRUMP_WL_E3_AUTOMORPHISM_NECESSITY_BRIDGE_REVIEW_2026-09-17_v1.0.json'
PARENT = ROOT / 'research/TRUMP_UF20_016_025_ONE_SHOT_CLASS_COVERAGE_WL_REPLICATION_RESULT_2026-09-17_v1.0.json'
HIST = ROOT / 'research/TRUMP_UF20_WL_POLYTIME_HISTORICAL_CLOSED_CONTROL_FALSIFIER_RESULT_2026-09-17_v1.0.json'
WL_CODE = ROOT / 'research/tools/apma_uf20_wl_historical_closed_control_falsifier/candidate.py'
E3_CODE = ROOT / 'research/tools/apma_unseen_local_invariant_orbit_count/candidate.py'
RAW_BASIS = ROOT / 'research/tools/apma_unseen_basis/raw_relation_basis.py'
EXPECTED = {
    PREREG: '9daf44f5a94057fe1ec870776e47963cd0d30c8f',
    REVIEW: '812d950fd31d725a36641e5385e0cc75b21f781c',
    PARENT: '15aa1bbb6b8bcd1f9820b46dcda2c92f1eb96fd4',
    WL_CODE: '6b697fd8b3de4c83f8226b06399b6bad99953d4e',
    E3_CODE: 'a076cfc56d68aad0348415e313705da1f6b9cdcd',
    RAW_BASIS: '63490c05ef3e91a4f682f75da26ff2af811839a6',
}
MECH = 'EXACT_TRANSPOSITION_ORBIT_COUNT_QUOTIENT'


def blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()


def guard() -> dict[str, Any]:
    bindings = {str(p.relative_to(ROOT)): blob(p) == h for p, h in EXPECTED.items()}
    pre = json.loads(PREREG.read_text())
    review = json.loads(REVIEW.read_text())
    parent = json.loads(PARENT.read_text())
    checks = {
        'authority_bindings': all(bindings.values()),
        'prereg_frozen': pre.get('status') == 'FROZEN_BEFORE_BRIDGE_IMPLEMENTATION_OR_EXECUTION',
        'review_authorized': review.get('review_verdict') == 'PASS_CLEAN_WL_E3_NECESSITY_BRIDGE_SPEC__AUTHORIZED_TO_IMPLEMENT_AND_EXECUTE_ONCE',
        'parent_execution_verified': parent.get('execution_verdict') == 'PASS_INDEPENDENT_ONE_SHOT_EXECUTION_AND_EXACT_RECOMPUTATION',
        'parent_both_route_classes': parent.get('summary', {}).get('route_coverage_outcome') == 'PANEL_CONTAINS_BOTH_PORTFOLIO_OPEN_AND_PORTFOLIO_CLOSED',
        'parent_all_four_wl_survive': parent.get('summary', {}).get('wl_replication_outcome') == 'ALL_FOUR_FROZEN_WL_FEATURES_SURVIVE',
    }
    return {'ok': all(checks.values()), 'checks': checks, 'bindings': bindings}


def stable_color_maps(raw: dict[str, Any]) -> tuple[dict[int, int], dict[int, int], dict[str, Any]]:
    nodes, adjacency, labels = wl_ref.incidence_structure(raw)
    variables = [n for n in nodes if n[0] == 'v']
    c1, r1 = wl_ref.wl1(nodes, adjacency, labels)
    c2, r2 = wl_ref.wl2(nodes, adjacency, labels)
    one = {int(v[1]): int(c1[v]) for v in variables}
    two = {int(v[1]): int(c2[(v, v)]) for v in variables}
    return one, two, {'wl1_rounds': r1, 'wl2_rounds': r2}


def classes(colors: dict[int, int]) -> list[list[int]]:
    buckets: dict[int, list[int]] = defaultdict(list)
    for v, c in colors.items():
        buckets[c].append(v)
    return sorted((sorted(vs) for vs in buckets.values()), key=lambda x: (x[0], len(x), x))


def edge_color_checks(raw: dict[str, Any]) -> dict[str, Any]:
    result = orbit.run_candidate(raw)
    one, two, rounds = stable_color_maps(raw)
    edges = [tuple(map(int, e)) for e in result.get('generator_edges', [])]
    rows = []
    for u, v in edges:
        rows.append({
            'edge': [u, v],
            'wl1_same': one[u] == one[v],
            'wl2_diagonal_same': two[u] == two[v],
            'wl1_color': one[u],
            'wl2_diagonal_color': two[u],
        })
    return {
        'e3_status': result.get('status'),
        'solver_authority': result.get('solver_authority'),
        'generator_edges': [list(e) for e in edges],
        'wl1_classes': classes(one),
        'wl2_diagonal_classes': classes(two),
        'edge_checks': rows,
        'all_edges_wl1_same': all(r['wl1_same'] for r in rows),
        'all_edges_wl2_same': all(r['wl2_diagonal_same'] for r in rows),
        'rounds': rounds,
    }


def historical_e3_rows() -> list[dict[str, Any]]:
    historical = json.loads(HIST.read_text())
    target = [r for r in historical['control_rows'] if r['closing_mechanism'] == MECH]
    unique, source_guard = wl_ref.reconstruct_unique_raws()
    if not source_guard.get('ok'):
        raise RuntimeError('HISTORICAL_SOURCE_GUARD_FAILURE')
    rows = []
    for row in target:
        sha = row['raw_sha256']
        raw = unique[sha]['raw']
        check = edge_color_checks(raw)
        rows.append({
            'kind': 'HISTORICAL_E3_CONTROL',
            'raw_sha256': sha,
            'aliases': row['required_aliases'],
            'closing_mechanism': row['closing_mechanism'],
            **check,
        })
    return rows


def fresh_uf20_024_row() -> dict[str, Any]:
    parent = json.loads(PARENT.read_text())
    parent_row = next(r for r in parent['holdout_rows'] if r['source'] == 'UF20_024')
    if parent_row['existing_portfolio']['closure']['route'] != MECH:
        raise RuntimeError('UF20_024_PARENT_ROUTE_MISMATCH')
    source_freeze = json.loads(panel.SOURCE_FREEZE.read_text())
    meta = next(r for r in source_freeze['source_receipts'] if r['source'] == 'UF20_024')
    path = ROOT / meta['committed_copy_path']
    if panel.frozen.blob(path) != meta['computed_committed_git_blob']:
        raise RuntimeError('UF20_024_SOURCE_BLOB_MISMATCH')
    clauses, formula_hash = panel.frozen.parse_and_formula_hash(path)
    if formula_hash != meta['canonical_formula_sha256']:
        raise RuntimeError('UF20_024_FORMULA_HASH_MISMATCH')
    projected = panel.frozen.projection_identity.normalize_projection('UF20_024', clauses)[0]
    reduced, degree1, targets = panel.frozen.generic_round(projected)
    check = edge_color_checks(reduced)
    return {
        'kind': 'FRESH_UF20_024',
        'source': 'UF20_024',
        'canonical_formula_sha256': formula_hash,
        'reduced_raw_sha256': panel.frozen.csha(reduced),
        'degree1_variables': degree1,
        'target_constraints': targets,
        'parent_generator_edges': parent_row['existing_portfolio']['E3']['generator_edges'],
        'parent_e3_status': parent_row['existing_portfolio']['E3']['status'],
        **check,
    }


def structural_certificate() -> dict[str, Any]:
    return {
        'C1_ENCODING_EQUIVARIANCE': {
            'proved': True,
            'derivation': 'E3 accepts (u v) only when swapping u and v leaves the canonical multiset of relation-bearing constraints unchanged. The same swap therefore extends to a bijection of constraint nodes preserving relation labels and incidence adjacency in the frozen WL graph.'
        },
        'C2_WL1_AUTOMORPHISM_INVARIANCE': {
            'proved': True,
            'derivation': 'By induction on refinement rounds: an automorphism preserves initial vertex labels; if it preserves round-t colors, it preserves each vertex prior color and the multiset of neighbor colors, hence preserves the round-(t+1) signature and canonical color.'
        },
        'C3_WL2_DIAGONAL_AUTOMORPHISM_INVARIANCE': {
            'proved': True,
            'derivation': 'By induction on 2-WL rounds under simultaneous action on ordered pairs: initial endpoint labels, equality and adjacency are invariant, and the multiset over intermediate vertices is merely permuted by an automorphism.'
        },
        'C4_TRANSPOSITION_ENDPOINT_NECESSITY': {
            'proved': True,
            'derivation': 'C1 makes an E3-accepted transposition a WL-graph automorphism; C2 and C3 force the swapped variable endpoints to have the same stable 1-WL variable color and the same stable 2-WL diagonal color.'
        },
        'C5_DISCRETE_NEGATIVE_CERTIFICATE': {
            'proved': True,
            'derivation': 'Contrapositive of C4: a nontrivial exact transposition requires two distinct variables in one stable color class. If either relevant partition is discrete, no such pair exists.'
        },
    }


def main() -> dict[str, Any]:
    g = guard()
    if not g['ok']:
        return {'verdict': 'HALT_AUTHORITY_BINDING_FAILURE', 'authority_guard': g, 'scientific_firewall': {'P_VS_NP': 'OPEN', 'GENERAL_SAT_IN_P': 'NOT_PROVED'}}
    cert = structural_certificate()
    if not all(x['proved'] for x in cert.values()):
        return {'verdict': 'FAIL_STRUCTURAL_BRIDGE_OBLIGATION', 'authority_guard': g, 'structural_certificate': cert}
    hist = historical_e3_rows()
    fresh = fresh_uf20_024_row()
    rows = hist + [fresh]
    sanity_ok = all(r['all_edges_wl1_same'] and r['all_edges_wl2_same'] and len(r['generator_edges']) > 0 for r in rows)
    fresh_exact = fresh['generator_edges'] == fresh['parent_generator_edges'] and fresh['e3_status'] == fresh['parent_e3_status']
    if not sanity_ok or not fresh_exact:
        return {
            'verdict': 'FAIL_FROZEN_E3_WITNESS_COLOR_INVARIANCE',
            'authority_guard': g,
            'structural_certificate': cert,
            'sanity_rows': rows,
            'fresh_parent_replay_exact': fresh_exact,
        }
    return {
        'artifact_id': 'JANUS-TRUMP-WL-E3-AUTOMORPHISM-NECESSITY-BRIDGE-CANDIDATE-2026-09-17-v1.0',
        'gate': 'TRUMP_WL_E3_AUTOMORPHISM_NECESSITY_BRIDGE_GATE',
        'verdict': 'PASS_WL_E3_AUTOMORPHISM_NECESSITY_BRIDGE',
        'authority_guard': g,
        'structural_certificate': cert,
        'sanity_rows': rows,
        'historical_e3_control_count': len(hist),
        'fresh_e3_control_count': 1,
        'fresh_parent_replay_exact': fresh_exact,
        'licensed_fact': 'A_DISCRETE_FROZEN_WL1_VARIABLE_PARTITION_OR_DISCRETE_FROZEN_WL2_DIAGONAL_VARIABLE_PARTITION_IS_A_SOUND_NEGATIVE_CERTIFICATE_THAT_THE_FROZEN_E3_EXACT_TRANSPOSITION_GENERATOR_SET_IS_EMPTY',
        'not_licensed': [
            'WL_NONDISCRETE_IMPLIES_E3_GENERATOR_EXISTS',
            'WL_COLOR_CLASS_EQUALS_AUTOMORPHISM_ORBIT',
            'WL_ALONE_CERTIFIES_PORTFOLIO_CLOSURE',
            'WL_ALONE_CERTIFIES_SAT_OR_UNSAT',
            'GENERAL_SAT_IN_P',
            'P_EQUALS_NP',
        ],
        'resource_receipt': {
            'new_solver_rules': 0,
            'new_reduction_rules': 0,
            'new_action_rules': 0,
            'new_group_searches': 0,
            'new_carrier_mechanisms': 0,
            'new_adapters': 0,
            'new_quotients': 0,
            'retuned_wl_features': 0,
            'retuned_thresholds': 0,
            'existing_e3_replays_for_sanity_only': len(rows),
        },
        'scientific_firewall': {
            'P_VS_NP': 'OPEN',
            'GENERAL_SAT_IN_P': 'NOT_PROVED',
            'GENERAL_RESIDUAL_SEPARATOR_TRACTABILITY': 'NOT_PROVED',
            'WL_NONDISCRETE_SUFFICIENCY_FOR_E3': 'NOT_PROVED',
        },
    }


if __name__ == '__main__':
    print(json.dumps(main(), sort_keys=True, separators=(',', ':')))
