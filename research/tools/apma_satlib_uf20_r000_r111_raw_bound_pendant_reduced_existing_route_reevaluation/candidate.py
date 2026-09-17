from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from research.tools.apma_satlib_uf20_r000_r111_projected_core_replay import projection_identity
from research.tools.apma_unseen_basis import compositional_basis
from research.tools.apma_connected_mixed_post_orbit_obstruction_census import census as reference_census
from research.tools.apma_unseen_local_invariant_orbit_count import candidate as orbit_candidate

ROOT = Path(__file__).resolve().parents[3]
PREREG = ROOT / 'research/TRUMP_SATLIB_UF20_R000_R111_RAW_BOUND_PENDANT_REDUCED_EXISTING_ROUTE_REEVALUATION_PREREGISTRATION_2026-09-17_v1.1.json'
REVIEW = ROOT / 'research/TRUMP_SATLIB_UF20_R000_R111_RAW_BOUND_PENDANT_REDUCED_EXISTING_ROUTE_REEVALUATION_PREREGISTRATION_REVIEW_2026-09-17_v1.1.json'
PARENT = ROOT / 'research/TRUMP_SATLIB_UF20_R000_R111_RAW_BOUND_PENDANT_EXACT_SIMULTANEOUS_ONE_ROUND_REDUCTION_RESULT_2026-09-17_v1.1.json'
PROJECTION = ROOT / 'research/tools/apma_satlib_uf20_r000_r111_projected_core_replay/projection_identity.py'
COMPOSITIONAL = ROOT / 'research/tools/apma_unseen_basis/compositional_basis.py'
REFERENCE = ROOT / 'research/tools/apma_connected_mixed_post_orbit_obstruction_census/census.py'
LOG_ALIEN = ROOT / 'research/tools/apma_log_alien_transfer/log_alien_transfer.py'
ORBIT = ROOT / 'research/tools/apma_unseen_local_invariant_orbit_count/candidate.py'
SIGNED = ROOT / 'research/tools/apma_satlib_uf20_r000_r111_projected_signed_exact/certificate.py'
SIGNED_ALIGNMENT = ROOT / 'research/TRUMP_SATLIB_UF20_R000_R111_PROJECTED_SIGNED_VS_SEALED_ORBIT_ALIGNMENT_RESULT_2026-09-16.json'

ORDER = ('UF20_02', 'UF20_03', 'UF20_04', 'UF20_05')
EXPECTED = {
    PREREG: '70d68119c3b61703d2b559f07de16a3f9920a2d6',
    REVIEW: '71cab68e3aadd862dd8b3f29a60adf0f709759a1',
    PARENT: 'd91cb675e3d06fed92f97d96d6b3a0733f8be5df',
    PROJECTION: '2ef48e73974a5f43d3f4fb4809ebd0c09c0f5be4',
    COMPOSITIONAL: 'fdc83a3368a4ad362f00d3ee8aad958f06f8d264',
    REFERENCE: 'f5aa39804983d49149c976e8367a96397bad888e',
    LOG_ALIEN: 'd20cd94fa2e0324e301f55211152c2d410099425',
    ORBIT: 'a076cfc56d68aad0348415e313705da1f6b9cdcd',
    SIGNED: '616a34efa5565c9d96a4f8362bef6c96aba94a54',
    SIGNED_ALIGNMENT: 'd20150284fef9926d828f9903a6b9f5c56c10b01',
}
SOURCES = {
    'UF20_02': (ROOT/'research/source_data/SATLIB_UF20_02_2026-09-16.cnf', 'f924caaef0d868bf62b1658e83e030ad8daee865'),
    'UF20_03': (ROOT/'research/source_data/SATLIB_UF20_03_2026-09-16.cnf', '8f3d15154515457281f49201b843f2a7134dfa9f'),
    'UF20_04': (ROOT/'research/source_data/SATLIB_UF20_04_2026-09-16.cnf', '34ced5c169f967b2dc44ef5e42f2ee2c924813e1'),
    'UF20_05': (ROOT/'research/source_data/SATLIB_UF20_05_2026-09-16.cnf', '3b04eff26ee37bdd0bc21b1066486974f92a2c9b'),
}
CLOSED_ORBIT = {'ADMIT_ORBIT_COUNT_QUOTIENT_SAT', 'ADMIT_ORBIT_COUNT_QUOTIENT_UNSAT'}


def blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()


def csha(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()


def firewall() -> dict[str, Any]:
    return {
        'P_VS_NP': 'OPEN',
        'GENERAL_SAT_IN_P': 'NOT_PROVED',
        'GENERAL_GT2_TRACTABILITY': 'NOT_PROVED',
        'CONNECTED_MIXED_CORE_SOLVED': 'NO',
        'SCOPED_EXISTING_ROUTE_CLOSURE_IMPLIES_GENERAL_TRACTABILITY': False,
    }


def reconstruct(source: str, parent_row: dict[str, Any], prereg: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    source_path, expected_blob = SOURCES[source]
    if blob(source_path) != expected_blob:
        raise RuntimeError(f'SOURCE_BLOB_MISMATCH:{source}')
    original, _ = projection_identity.normalize_projection(source, projection_identity.parse(source_path))
    expected_original = prereg['reconstruction_binding']['sources'][source]['original_projected_sha256']
    observed_original = csha(original)
    if observed_original != expected_original:
        raise RuntimeError(f'ORIGINAL_PROJECTED_SHA_MISMATCH:{source}:{observed_original}:{expected_original}')
    remove_ids = set(parent_row['removed_constraint_ids'])
    remove_leaves = {int(v) for v in parent_row['removed_leaves']}
    remaining_constraints = [c for c in original['constraints'] if c['id'] not in remove_ids]
    remaining_variables = [int(v) for v in original['variables'] if int(v) not in remove_leaves]
    reduced = {'variables': remaining_variables, 'constraints': remaining_constraints}
    target = prereg['target_reduced_raw_identities'][source]
    observed = {'variables': len(remaining_variables), 'constraints': len(remaining_constraints), 'sha256': csha(reduced)}
    if observed != target:
        raise RuntimeError(f'REDUCED_IDENTITY_MISMATCH:{source}:{observed}:{target}')
    if any(remove_leaves & {int(v) for v in c['scope']} for c in remaining_constraints):
        raise RuntimeError(f'REMOVED_LEAF_SURVIVED:{source}')
    return reduced, {'original_projected_sha256': observed_original, 'reduced_identity': observed}


def route_row(source: str, reduced: dict[str, Any], parent_row: dict[str, Any]) -> dict[str, Any]:
    elig = reference_census.eligibility(reduced)
    comp = compositional_basis.induce_compositional_basis(reduced)
    comp_status = comp.get('status')
    schaefer_bases = list(elig.get('global_candidate_bases') or [])
    basis_closed = bool(schaefer_bases) or comp_status == 'ADMIT_COMPOSITIONAL_BASIS_PORTFOLIO'
    row: dict[str, Any] = {
        'source': source,
        'reduced_raw_sha256': csha(reduced),
        'reduced_variables': len(reduced['variables']),
        'reduced_constraints': len(reduced['constraints']),
        'E1_connected_and_schaefer_compositional': {
            'incidence_component_count': elig.get('incidence_component_count'),
            'eligibility_class_under_v3_23_definition': elig.get('eligibility_class'),
            'global_language_fingerprint': elig.get('global_language_fingerprint'),
            'global_candidate_bases': schaefer_bases,
            'compositional_status': comp_status,
            'compositional_component_count': comp.get('component_count'),
            'compositional_open_component_count': comp.get('open_component_count'),
            'existing_basis_route_closed': basis_closed,
        },
    }
    closure = None
    if basis_closed:
        closure = {'route': 'EXISTING_SCHAEFER_OR_COMPOSITIONAL_BASIS', 'status': comp_status, 'solver_authority': False, 'scope': 'ROUTE_ADMISSION_ONLY'}
        row['E2_log_alien'] = {'executed': False, 'reason': 'STOP_ON_FIRST_EXISTING_ROUTE_ADMISSION'}
        row['E3_orbit_count_v1'] = {'executed': False, 'reason': 'STOP_ON_FIRST_EXISTING_ROUTE_ADMISSION'}
    else:
        log_alien = reference_census.replay_log_alien(reduced)
        row['E2_log_alien'] = log_alien
        if log_alien.get('closed'):
            win = log_alien.get('winning_attempt') or {}
            closure = {'route': 'SEALED_LOG_ALIEN_CONSTRAINT_EXACT_TRANSFER', 'status': win.get('status'), 'solver_authority': True, 'scope': 'THIS_REDUCED_RAW_ONLY'}
            row['E3_orbit_count_v1'] = {'executed': False, 'reason': 'STOP_ON_FIRST_EXISTING_AUTHORITATIVE_CLOSURE'}
        else:
            orbit = orbit_candidate.run_candidate(reduced)
            orbit_rec = {
                'executed': True,
                'status': orbit.get('status'),
                'solver_authority': orbit.get('solver_authority'),
                'raw_semantic_sha256': orbit.get('raw_semantic_sha256'),
                'cells': orbit.get('cells'),
                'generator_edges': orbit.get('generator_edges'),
                'quotient_states_Q': orbit.get('quotient_states_Q'),
                'resource_receipt': orbit.get('resource_receipt', {}),
                'certificate_type': (orbit.get('certificate') or {}).get('type'),
            }
            row['E3_orbit_count_v1'] = orbit_rec
            if orbit.get('status') in CLOSED_ORBIT and orbit.get('solver_authority') is True:
                closure = {'route': 'EXACT_TRANSPOSITION_ORBIT_COUNT_QUOTIENT', 'status': orbit.get('status'), 'solver_authority': True, 'scope': 'THIS_REDUCED_RAW_ONLY'}
    original_sha = parent_row['original_projected_raw']['sha256']
    signed_applicable = row['reduced_raw_sha256'] == original_sha
    row['E4_existing_signed_route_contract'] = {
        'status': 'APPLICABLE_EXISTING_SOURCE_BOUND_IDENTITY' if signed_applicable else 'NOT_APPLICABLE_SOURCE_BOUND_IDENTITY_CONTRACT',
        'reduced_raw_sha256': row['reduced_raw_sha256'],
        'frozen_original_projected_raw_sha256': original_sha,
        'new_signed_action_tests': 0,
        'new_group_searches': 0,
    }
    row['existing_route_closure'] = closure
    if closure is None:
        row['post_reduction_residual_blockers'] = {
            'basis_or_compositional': comp_status,
            'log_alien': row['E2_log_alien'].get('reason') if not row['E2_log_alien'].get('applicable', False) else row['E2_log_alien'].get('attempts'),
            'orbit_count_v1': row['E3_orbit_count_v1'].get('status'),
            'signed_route': row['E4_existing_signed_route_contract']['status'],
        }
    return row


def main() -> None:
    bindings = {str(p.relative_to(ROOT)): blob(p) == sha for p, sha in EXPECTED.items()}
    source_bindings = {name: blob(p) == sha for name, (p, sha) in SOURCES.items()}
    pre = json.loads(PREREG.read_text())
    review = json.loads(REVIEW.read_text())
    parent = json.loads(PARENT.read_text())
    guard_checks = {
        'all_pinned_blobs': all(bindings.values()),
        'all_source_blobs': all(source_bindings.values()),
        'prereg_status': pre.get('status') == 'FROZEN_BEFORE_ANY_POST_REDUCTION_ROUTE_REEVALUATION_VALUE_COMPUTATION',
        'review_authorized': review.get('verdict') == 'PASS_PREREGISTRATION_CLEAN__AUTHORIZED_TO_IMPLEMENT_AND_EXECUTE_ONCE',
        'parent_pass': parent.get('verdict') == 'PASS_EXACT_SIMULTANEOUS_ONE_ROUND_REDUCTION',
        'holdout_forbidden': pre.get('fresh_holdout_firewall', {}).get('values_may_be_read_or_computed') is False,
    }
    if not all(guard_checks.values()):
        print(json.dumps({'verdict': 'HALT_FROZEN_AUTHORITY_BINDING_FAILURE', 'guards': guard_checks, 'bindings': bindings, 'source_bindings': source_bindings, 'scientific_firewall': firewall()}, sort_keys=True))
        return
    parent_rows = {r['source']: r for r in parent['source_receipts']}
    rows = []
    try:
        for source in ORDER:
            reduced, identity = reconstruct(source, parent_rows[source], pre)
            row = route_row(source, reduced, parent_rows[source])
            row['E0_reduced_identity_guard'] = {'pass': True, **identity}
            rows.append(row)
    except Exception as exc:
        print(json.dumps({'verdict': 'HALT_FROZEN_AUTHORITY_BINDING_FAILURE', 'reason': str(exc), 'guards': guard_checks, 'bindings': bindings, 'source_bindings': source_bindings, 'scientific_firewall': firewall()}, sort_keys=True))
        return
    closures = [r for r in rows if r.get('existing_route_closure') is not None]
    verdict = 'EXISTING_ROUTE_NEWLY_CLOSES_AT_LEAST_ONE_REDUCED_RAW' if closures else 'NO_EXISTING_ROUTE_NEWLY_CLOSES__POST_REDUCTION_RESIDUAL_BLOCKERS_FROZEN'
    out = {
        'artifact_id': 'JANUS-TRUMP-SATLIB-UF20-R000-R111-RAW-BOUND-PENDANT-REDUCED-EXISTING-ROUTE-REEVALUATION-CANDIDATE-2026-09-17-v1.1',
        'authority': 'DIAGNOSTIC_EXISTING_FROZEN_ROUTE_REEVALUATION_ONLY__NO_NEW_FEATURE_SOLVER_CARRIER_ADAPTER_QUOTIENT_GROUP_OR_SECOND_REDUCTION',
        'verdict': verdict,
        'guards': guard_checks,
        'bindings': bindings,
        'source_bindings': source_bindings,
        'rows': rows,
        'closed_source_count': len(closures),
        'closed_sources': [r['source'] for r in closures],
        'resource_receipt': {
            'target_sources': 4,
            'reduction_rounds': 0,
            'post_round_target_discoveries': 0,
            'new_relations_added': 0,
            'new_solver_mechanisms': 0,
            'new_carrier_mechanisms': 0,
            'new_representation_adapters': 0,
            'new_action_families': 0,
            'new_signed_action_tests': 0,
            'new_group_searches': 0,
            'fresh_holdout_values_read': 0,
            'budget_raise': False,
        },
        'scientific_firewall': firewall(),
    }
    print(json.dumps(out, sort_keys=True, separators=(',', ':')))


if __name__ == '__main__':
    main()
