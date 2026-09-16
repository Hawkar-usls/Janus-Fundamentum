from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from research.tools.apma_satlib_uf20_r000_r111_projected_core_replay import projection_identity
from research.tools.apma_satlib_uf20_r000_r111_projected_signature_ablation import replay as ablation
from research.tools.apma_satlib_uf20_r000_r111_residual_local_invariant_falsifier import candidate as frozen_falsifier

ROOT = Path(__file__).resolve().parents[3]
PREREG = ROOT / 'research/TRUMP_SATLIB_UF20_R000_R111_L3_WL3_EXISTING_SIGNATURE_EQUIVALENCE_AUDIT_PREREGISTRATION_2026-09-17.json'
REVIEW = ROOT / 'research/TRUMP_SATLIB_UF20_R000_R111_L3_WL3_EXISTING_SIGNATURE_EQUIVALENCE_AUDIT_PREREGISTRATION_REVIEW_2026-09-17.json'
FALSIFIER_RESULT = ROOT / 'research/TRUMP_SATLIB_UF20_R000_R111_RESIDUAL_LOCAL_INVARIANT_FALSIFIER_RESULT_2026-09-16.json'
ABLATION_RESULT = ROOT / 'research/TRUMP_SATLIB_UF20_R000_R111_PROJECTED_CORE_EXISTING_SIGNATURE_ABLATION_REPLAY_RESULT_2026-09-16.json'
ABLATION_IMPL = ROOT / 'research/tools/apma_satlib_uf20_r000_r111_projected_signature_ablation/replay.py'
L3_IMPL = ROOT / 'research/tools/apma_satlib_uf20_r000_r111_residual_local_invariant_falsifier/candidate.py'
EXPECTED = {
    PREREG: 'cc3e3a4b8c8b0a5c00f8558471e7efa451bc0a25',
    REVIEW: '945dd3009dec8eb768d9224edfe413c80a1b1a43',
    FALSIFIER_RESULT: '954893935bee1d46a77c5f635086e0e278b05fac',
    ABLATION_RESULT: 'b7ba5bd772c3092e0436dde8bd717dc28985983c',
    ABLATION_IMPL: '2edad57e6017cb34bf797313e4451c1ce014900b',
    L3_IMPL: '4ec02d6d42e6cad7d91f16b1acfdcbe51dbd65df',
    ROOT / 'research/tools/apma_satlib_uf20_r000_r111_projected_core_replay/projection_identity.py': '2ef48e73974a5f43d3f4fb4809ebd0c09c0f5be4',
}
SOURCES = {
    'UF20_01': (ROOT/'research/source_data/SATLIB_UF20_01_2026-09-16.cnf','8330041b292e0501f8d74c1b1d32ca96c4498864'),
    'UF20_02': (ROOT/'research/source_data/SATLIB_UF20_02_2026-09-16.cnf','f924caaef0d868bf62b1658e83e030ad8daee865'),
    'UF20_03': (ROOT/'research/source_data/SATLIB_UF20_03_2026-09-16.cnf','8f3d15154515457281f49201b843f2a7134dfa9f'),
    'UF20_04': (ROOT/'research/source_data/SATLIB_UF20_04_2026-09-16.cnf','34ced5c169f967b2dc44ef5e42f2ee2c924813e1'),
    'UF20_05': (ROOT/'research/source_data/SATLIB_UF20_05_2026-09-16.cnf','3b04eff26ee37bdd0bc21b1066486974f92a2c9b'),
}
LEVELS = ('S0','S1','S2','S3')


def blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()


def canonical_sha(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()


def guard() -> dict[str, Any]:
    bindings = {str(p.relative_to(ROOT)): blob(p) == sha for p, sha in EXPECTED.items()}
    source_bindings = {name: blob(path) == sha for name, (path, sha) in SOURCES.items()}
    pre = json.loads(PREREG.read_text())
    review = json.loads(REVIEW.read_text())
    checks = {
        'bindings': all(bindings.values()),
        'source_bindings': all(source_bindings.values()),
        'prereg_status': pre.get('status') == 'FROZEN_BEFORE_ANY_EQUIVALENCE_AUDIT_EXECUTION',
        'review_authorized': review.get('verdict') == 'PASS_PREREGISTRATION_CLEAN__AUTHORIZED_TO_IMPLEMENT_AND_EXECUTE_ONCE',
        'levels_exact': tuple(pre.get('audit_scope', {}).get('existing_stages', ())) == LEVELS,
        'candidate_exact': pre.get('audit_scope', {}).get('candidate_under_audit') == 'L3_THREE_ROUND_INCIDENCE_WL_ROOT_COLOR',
    }
    return {'ok': all(checks.values()), 'checks': checks, 'bindings': bindings, 'source_bindings': source_bindings}


def refines(p: list[list[int]], q: list[list[int]]) -> bool:
    qsets = [set(c) for c in q]
    return all(any(set(c) <= d for d in qsets) for c in p)


def relation(l3p: list[list[int]], skp: list[list[int]]) -> dict[str, Any]:
    l3_ref = refines(l3p, skp)
    sk_ref = refines(skp, l3p)
    if l3_ref and sk_ref:
        label = 'EQUAL'
    elif l3_ref:
        label = 'L3_STRICTLY_FINER_THAN_Sk'
    elif sk_ref:
        label = 'Sk_STRICTLY_FINER_THAN_L3'
    else:
        label = 'INCOMPARABLE'
    return {'l3_refines_sk': l3_ref, 'sk_refines_l3': sk_ref, 'relation': label}


def source_row(name: str, path: Path, expected_raw_sha: str) -> dict[str, Any]:
    clauses = projection_identity.parse(path)
    raw, _ = projection_identity.normalize_projection(name, clauses)
    raw_sha = canonical_sha(raw)
    if raw_sha != expected_raw_sha:
        return {'source': name, 'status': 'PROJECTED_RAW_BINDING_FAILURE', 'observed_raw_sha256': raw_sha, 'expected_raw_sha256': expected_raw_sha}

    frozen_features = ablation.features(raw, ablation.projected_clauses(path))
    V, edges, l3_raw_sha = frozen_falsifier.source_scope_projection(name, path)
    if l3_raw_sha != raw_sha:
        return {'source': name, 'status': 'FROZEN_IMPLEMENTATION_RAW_DISAGREEMENT', 'ablation_raw_sha256': raw_sha, 'l3_raw_sha256': l3_raw_sha}
    l3_sig = frozen_falsifier.l3(V, edges)
    l3_partition, l3_signature_map_sha256 = frozen_falsifier.partition(l3_sig)

    stages: dict[str, Any] = {}
    for level in LEVELS:
        sk_partition = ablation.partition(frozen_features, level)
        cmp = relation(l3_partition, sk_partition)
        stages[level] = {
            'sk_partition': sk_partition,
            'sk_partition_sha256': canonical_sha(sk_partition),
            **cmp,
        }
    return {
        'source': name,
        'status': 'AUDITED',
        'raw_sha256': raw_sha,
        'variable_count': len(V),
        'l3_partition': l3_partition,
        'l3_partition_sha256': canonical_sha(l3_partition),
        'l3_signature_map_sha256': l3_signature_map_sha256,
        'stages': stages,
    }


def firewall() -> dict[str, Any]:
    return {
        'P_VS_NP': 'OPEN',
        'GENERAL_SAT_IN_P': 'NOT_PROVED',
        'GENERAL_GT2_TRACTABILITY': 'NOT_PROVED',
        'CONNECTED_MIXED_CORE_SOLVED': 'NO',
        'L3_IS_HARDNESS_INVARIANT': False,
        'L3_IS_TRACTABILITY_CRITERION': False,
        'L3_GENERALIZES_BEYOND_FIVE_FROZEN_PROJECTIONS': False,
        'PARTITION_NOVELTY_LICENSES_SOLVER': False,
        'NEW_SOLVER_MECHANISM_LICENSED': False,
        'NEW_CARRIER_MECHANISM_LICENSED': False,
    }


def main() -> dict[str, Any]:
    g = guard()
    if not g['ok']:
        return {'verdict': 'HALT_BINDING_OR_PREREGISTRATION_GUARD_FAILURE', 'source_guard': g, 'scientific_firewall': firewall()}
    pre = json.loads(PREREG.read_text())
    expected_raw = pre['frozen_projected_raw_sha256']
    rows = [source_row(name, path, expected_raw[name]) for name, (path, _) in SOURCES.items()]
    if any(r.get('status') != 'AUDITED' for r in rows):
        return {'verdict': 'HALT_BINDING_OR_PARTITION_RECOMPUTATION_DISAGREEMENT', 'source_guard': g, 'rows': rows, 'scientific_firewall': firewall()}

    sanity = {
        'UF20_01_L3_class_containing_7': next(c for c in rows[0]['l3_partition'] if 7 in c),
        'UF20_02_L3_all_singleton': all(len(c) == 1 for c in rows[1]['l3_partition']),
        'UF20_03_L3_all_singleton': all(len(c) == 1 for c in rows[2]['l3_partition']),
        'UF20_04_L3_all_singleton': all(len(c) == 1 for c in rows[3]['l3_partition']),
        'UF20_05_L3_all_singleton': all(len(c) == 1 for c in rows[4]['l3_partition']),
        'UF20_01_S3_non_singleton_classes': [c for c in rows[0]['stages']['S3']['sk_partition'] if len(c) > 1],
        'UF20_03_S3_non_singleton_classes': [c for c in rows[2]['stages']['S3']['sk_partition'] if len(c) > 1],
    }
    expected_sanity = {k: v for k, v in pre['predeclared_sanity_receipts'].items() if k != 'note'}
    if sanity != expected_sanity:
        return {'verdict': 'HALT_BINDING_OR_PARTITION_RECOMPUTATION_DISAGREEMENT', 'source_guard': g, 'sanity': sanity, 'expected_sanity': expected_sanity, 'rows': rows, 'scientific_firewall': firewall()}

    stage_summary = {}
    equivalent_stages = []
    for level in LEVELS:
        rels = {r['source']: r['stages'][level]['relation'] for r in rows}
        all_equal = all(x == 'EQUAL' for x in rels.values())
        all_l3_refines = all(r['stages'][level]['l3_refines_sk'] for r in rows)
        all_sk_refines = all(r['stages'][level]['sk_refines_l3'] for r in rows)
        if all_equal:
            equivalent_stages.append(level)
        stage_summary[level] = {
            'relations_by_source': rels,
            'partition_equivalent_on_all_five_sources': all_equal,
            'l3_refines_stage_on_all_five_sources': all_l3_refines,
            'stage_refines_l3_on_all_five_sources': all_sk_refines,
            'strictly_finer_sources': [r['source'] for r in rows if r['stages'][level]['relation'] == 'L3_STRICTLY_FINER_THAN_Sk'],
            'strictly_coarser_sources': [r['source'] for r in rows if r['stages'][level]['relation'] == 'Sk_STRICTLY_FINER_THAN_L3'],
            'incomparable_sources': [r['source'] for r in rows if r['stages'][level]['relation'] == 'INCOMPARABLE'],
        }

    if equivalent_stages:
        verdict = 'PASS_AUDIT_L3_PARTITION_EQUIVALENT_TO_EXISTING_STAGE__NOT_NOVEL'
        scoped_partition_novelty = False
    else:
        verdict = 'PASS_SCOPED_PARTITION_NOVELTY_L3_NOT_EQUIVALENT_TO_ANY_EXISTING_STAGE'
        scoped_partition_novelty = True

    return {
        'artifact_id': 'JANUS-TRUMP-SATLIB-UF20-R000-R111-L3-WL3-EXISTING-SIGNATURE-EQUIVALENCE-AUDIT-CANDIDATE-2026-09-17-v1.0',
        'authority': 'DIAGNOSTIC_CROSS_CERTIFICATE_PARTITION_EQUIVALENCE_AUDIT_ONLY__NO_NEW_FEATURE_SOLVER_CARRIER_ADAPTER_QUOTIENT_OR_GROUP_SEARCH',
        'verdict': verdict,
        'source_guard': g,
        'sanity_receipts': sanity,
        'rows': rows,
        'stage_summary': stage_summary,
        'partition_equivalent_existing_stages': equivalent_stages,
        'scoped_partition_novelty': scoped_partition_novelty,
        'resource_receipt': {
            'source_count': 5,
            'existing_stage_count': 4,
            'source_stage_partition_comparisons': 20,
            'full_assignment_cube_enumerations': 0,
            'solver_invocations': 0,
            'group_searches': 0,
            'new_feature_definitions': 0,
            'new_graph_statistics': 0,
            'new_solver_mechanisms': 0,
            'new_carrier_mechanisms': 0,
            'new_adapters': 0,
            'new_quotients': 0,
            'budget_raise': False,
        },
        'scientific_firewall': firewall(),
    }


if __name__ == '__main__':
    print(json.dumps(main(), sort_keys=True, separators=(',', ':')))
