from __future__ import annotations

import argparse
import copy
import hashlib
import json
from typing import Any

from janus_c049_1_b3_expand_join_shrink_core import (
    compactify,
    decode_trajectory,
    encode_trajectory,
    expand_trajectory,
    grouped_partition_digest_payload,
    join_trajectory,
    lattice_paths,
    shrink_trajectory,
    subspace_intersection,
    subspace_sum,
    up_k,
    validate_grouped_partition,
    width,
    xor_basis,
)

SOURCE = {
    'primary': 'Jeong-Kim-Oum arXiv:1507.02184v4 Sections 3.3-3.5 and Propositions 4.2-4.4',
    'grouped_partition': 'C049 PR #74 / Jeong-Kim-Oum arXiv:1711.01381v3',
    'normal_form_dependency': 'C049.1 Phase B1 PR #76',
    'up_k_dependency': 'C049.1 Phase B2 PR #77',
}

CLOSED = 'CLOSED_EXACT'
OPEN_WORK = 'OPEN_WORK_BUDGET'
OPEN_CERT = 'OPEN_CERTIFICATE_VOLUME'


def canonical_json(value: Any, pretty: bool = False) -> bytes:
    if pretty:
        return (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def bind_case(payload: dict, certificate_cap: int = 1_000_000) -> dict:
    out = copy.deepcopy(payload)
    out.pop('integrity', None)
    out['certificate_bytes'] = 0
    while True:
        body = dict(out)
        body.pop('integrity', None)
        out['integrity'] = digest(body)
        measured = len(canonical_json(out, pretty=True))
        if measured == out['certificate_bytes']:
            break
        out['certificate_bytes'] = measured
    if out['certificate_bytes'] <= certificate_cap:
        return out
    refusal = {
        'case_id': payload['case_id'],
        'terminal': OPEN_CERT,
        'required_certificate_bytes': out['certificate_bytes'],
        'certificate_cap': certificate_cap,
        'source': SOURCE,
        'p_vs_np': 'OPEN',
    }
    refusal['certificate_bytes'] = 0
    while True:
        body = dict(refusal)
        body.pop('integrity', None)
        refusal['integrity'] = digest(body)
        measured = len(canonical_json(refusal, pretty=True))
        if measured == refusal['certificate_bytes']:
            break
        refusal['certificate_bytes'] = measured
    return refusal


def expand_case() -> dict:
    ambient = 3
    child_boundary_raw = [3, 1]
    parent_boundary_raw = [3, 2, 4]
    child_boundary = xor_basis(child_boundary_raw, ambient)
    parent_boundary = xor_basis(parent_boundary_raw, ambient)
    gamma = decode_trajectory([
        {'left': [], 'right': [3, 1], 'value': 0},
        {'left': [1, 2], 'right': [], 'value': 0},
    ], child_boundary, ambient)
    expanded, receipt = expand_trajectory(gamma, child_boundary_raw, parent_boundary_raw, ambient)
    arrangement_span = xor_basis([1, 2], ambient)
    condition_intersection = subspace_intersection(arrangement_span, parent_boundary, ambient)
    if not set(condition_intersection).issubset(set(child_boundary)):
        raise AssertionError('expand condition failed')
    return bind_case({
        'case_id': 'EXPAND_NONCANONICAL_BOUNDARY_BASIS',
        'terminal': CLOSED,
        'ambient_dim': ambient,
        'child_boundary_raw': child_boundary_raw,
        'parent_boundary_raw': parent_boundary_raw,
        'arrangement_span': list(arrangement_span),
        'expand_condition_intersection': list(condition_intersection),
        'input': encode_trajectory(gamma),
        'output': encode_trajectory(expanded),
        'transport': receipt,
        'boundary_coordinate_changes': len(receipt['child_basis_in_parent_coordinates']),
        'source': SOURCE,
        'p_vs_np': 'OPEN',
    })


def join_case() -> dict:
    ambient = 3
    boundary = xor_basis([4], ambient)
    child1_span = xor_basis([1, 4], ambient)
    child2_span = xor_basis([2, 4], ambient)
    left_aug = subspace_sum(child1_span, boundary, ambient)
    right_aug = subspace_sum(child2_span, boundary, ambient)
    condition = subspace_intersection(left_aug, right_aug, ambient)
    if condition != boundary:
        raise AssertionError('join precondition failed')
    blocks = validate_grouped_partition([[1, 4], [2, 4]], 2, ambient)
    child = decode_trajectory([
        {'left': [], 'right': [4], 'value': 0},
        {'left': [4], 'right': [], 'value': 0},
    ], boundary, ambient)
    joins = []
    raw_total = 0
    for path in lattice_paths(len(child), len(child)):
        compact, receipt = join_trajectory(child, child, path, boundary, ambient)
        raw_total += receipt['raw_length']
        joins.append(receipt)
    return bind_case({
        'case_id': 'JOIN_PARTITION_AWARE_ALL_LATTICE_PATHS',
        'terminal': CLOSED,
        'ambient_dim': ambient,
        'boundary': list(boundary),
        'child_spans': [list(child1_span), list(child2_span)],
        'grouped_factor_blocks': grouped_partition_digest_payload(blocks, ambient),
        'join_precondition_intersection': list(condition),
        'child_trajectory': encode_trajectory(child),
        'lattice_path_count': len(joins),
        'precompact_statistics_charged': raw_total,
        'joins': joins,
        'source': SOURCE,
        'p_vs_np': 'OPEN',
    })


def shrink_case() -> dict:
    ambient = 3
    boundary = xor_basis([1, 2], ambient)
    target = xor_basis([1], ambient)
    gamma = decode_trajectory([
        {'left': [], 'right': [1, 2], 'value': 0},
        {'left': [1], 'right': [2], 'value': 1},
        {'left': [1, 2], 'right': [], 'value': 0},
    ], boundary, ambient)
    compact, receipt = shrink_trajectory(gamma, target, ambient)
    return bind_case({
        'case_id': 'SHRINK_EXACT_LAMBDA_PROJECTION',
        'terminal': CLOSED,
        'ambient_dim': ambient,
        'source_boundary': list(boundary),
        'target_boundary': list(target),
        'input': encode_trajectory(gamma),
        'output': encode_trajectory(compact),
        'projection': receipt,
        'source_width': width(gamma),
        'projected_width': width(compact),
        'source': SOURCE,
        'p_vs_np': 'OPEN',
    })


def spike_case(work_cap: int = 1_000_000, certificate_cap: int = 1_000_000) -> dict:
    ambient = 1
    boundary: tuple[int, ...] = ()
    left_values = [2, 1, 4, 0, 5, 0, 3]
    right_values = [1, 2, 0, 5, 1, 4]
    left = decode_trajectory([{'left': [], 'right': [], 'value': x} for x in left_values], boundary, ambient)
    right = decode_trajectory([{'left': [], 'right': [], 'value': x} for x in right_values], boundary, ambient)
    path = [[0, 0], [1, 0], [1, 1], [2, 2], [2, 3], [2, 4], [2, 5], [3, 5], [4, 5], [5, 5], [6, 5]]
    compact, receipt = join_trajectory(left, right, path, boundary, ambient)
    attempted = receipt['raw_length']
    if attempted > work_cap:
        return bind_case({
            'case_id': 'INTERMEDIATE_JOIN_VOLUME_BUDGET',
            'terminal': OPEN_WORK,
            'work_counter': 'precompact_join_statistics',
            'attempted': attempted,
            'work_cap': work_cap,
            'path': path,
            'source': SOURCE,
            'p_vs_np': 'OPEN',
        }, certificate_cap)
    return bind_case({
        'case_id': 'INTERMEDIATE_JOIN_VOLUME_CHARGED',
        'terminal': CLOSED,
        'ambient_dim': ambient,
        'boundary': [],
        'left': encode_trajectory(left),
        'right': encode_trajectory(right),
        'join': receipt,
        'intermediate_excess': receipt['raw_length'] - receipt['compact_length'],
        'small_final_does_not_erase_intermediate_charge': True,
        'source': SOURCE,
        'p_vs_np': 'OPEN',
    }, certificate_cap)


def pipeline_case() -> dict:
    ambient = 3
    common_boundary = xor_basis([4], ambient)
    root_boundary: tuple[int, ...] = ()
    child = decode_trajectory([
        {'left': [], 'right': [4], 'value': 0},
        {'left': [4], 'right': [], 'value': 0},
    ], common_boundary, ambient)
    join_generators = []
    join_receipts = []
    for path in lattice_paths(len(child), len(child)):
        compact, receipt = join_trajectory(child, child, path, common_boundary, ambient)
        join_generators.append(compact)
        join_receipts.append(receipt)
    joined_closure = up_k(join_generators, common_boundary, ambient, 0)
    projected_generators = []
    shrink_receipts = []
    for entry in joined_closure['entries']:
        gamma = decode_trajectory(entry['trajectory'], common_boundary, ambient)
        projected, receipt = shrink_trajectory(gamma, root_boundary, ambient)
        projected_generators.append(projected)
        shrink_receipts.append(receipt)
    root_closure = up_k(projected_generators, root_boundary, ambient, 0)
    return bind_case({
        'case_id': 'EXPAND_JOIN_SHRINK_UP_K_PIPELINE_SMALL',
        'terminal': CLOSED,
        'ambient_dim': ambient,
        'k': 0,
        'common_boundary': list(common_boundary),
        'root_boundary': [],
        'child_trajectory': encode_trajectory(child),
        'join_receipts': join_receipts,
        'joined_closure': joined_closure,
        'shrink_receipts': shrink_receipts,
        'root_closure': root_closure,
        'expected_root_entry_count': 1,
        'source': SOURCE,
        'p_vs_np': 'OPEN',
    })


def partition_rejection_case() -> dict:
    ambient = 3
    whole_blocks = [[1, 4], [2, 4]]
    split_blocks = [[1], [4], [2], [4]]
    accepted = validate_grouped_partition(whole_blocks, 2, ambient)
    rejected = False
    reason = None
    try:
        validate_grouped_partition(split_blocks, 2, ambient)
    except ValueError as exc:
        rejected = True
        reason = str(exc)
    if not rejected:
        raise AssertionError('partition-loss control was not rejected')
    return bind_case({
        'case_id': 'GROUPED_PARTITION_LOSS_REJECTED',
        'terminal': CLOSED,
        'ambient_dim': ambient,
        'whole_blocks': grouped_partition_digest_payload(accepted, ambient),
        'split_blocks': split_blocks,
        'rejected': rejected,
        'reason': reason,
        'source': SOURCE,
        'p_vs_np': 'OPEN',
    })


def build() -> dict:
    cases = [
        expand_case(),
        join_case(),
        shrink_case(),
        spike_case(),
        pipeline_case(),
        partition_rejection_case(),
        spike_case(work_cap=5),
        spike_case(certificate_cap=300),
    ]
    summary = {
        'cases': len(cases),
        'closed_exact': sum(c['terminal'] == CLOSED for c in cases),
        'open_work_budget': sum(c['terminal'] == OPEN_WORK for c in cases),
        'open_certificate_volume': sum(c['terminal'] == OPEN_CERT for c in cases),
        'lattice_paths_replayed': cases[1]['lattice_path_count'] + len(cases[4]['join_receipts']),
        'precompact_statistics_charged': cases[1]['precompact_statistics_charged'] + cases[3]['join']['raw_length'] + sum(x['raw_length'] for x in cases[4]['join_receipts']),
        'full_pipeline_root_entries': cases[4]['root_closure']['entry_count'],
        'partition_loss_rejected': cases[5]['rejected'],
        'failures': 0,
    }
    artifact = {
        'artifact_id': 'C049.1-JANUS-PHASE-B3-PARTITION-AWARE-EXPAND-JOIN-SHRINK',
        'cycle': 'C049.1',
        'phase': 'B3',
        'status': 'EXPAND_JOIN_SHRINK_ALGEBRA_IMPLEMENTED_ITERATIVE_COMPRESSION_PENDING',
        'source': SOURCE,
        'cases': cases,
        'summary': summary,
        'strict_boundary': {
            'implemented': [
                'boundary-basis transport for expand',
                'all Delannoy lattice paths for join',
                'full precompact join receipts',
                'exact join lambda correction',
                'projection/shrink lambda correction',
                'B1 compactification receipts',
                'bounded exact up_k closure integration',
                'whole-factor grouped partition enforcement',
                'intermediate volume accounting before compactification',
            ],
            'pending': [
                'branch-decomposition dynamic program over arbitrary tree',
                'iterative compression',
                'FOUND_LAYOUT reconstruction',
                'complete NO_LAYOUT_AT_CAP replay',
                'C047 composition from a discovered layout',
            ],
            'current_global_terminal': 'OPEN_TRAJECTORY_ENGINE_INCOMPLETE',
            'next_gate': 'C049.1_PHASE_B4_ITERATIVE_COMPRESSION',
            'complete_no_layout_at_cap_enabled': False,
            'p_vs_np': 'OPEN',
        },
    }
    artifact['integrity'] = digest(artifact)
    return artifact


def self_test() -> None:
    artifact = build()
    assert artifact['summary'] == {
        'cases': 8,
        'closed_exact': 6,
        'open_work_budget': 1,
        'open_certificate_volume': 1,
        'lattice_paths_replayed': 6,
        'precompact_statistics_charged': 27,
        'full_pipeline_root_entries': 1,
        'partition_loss_rejected': True,
        'failures': 0,
    }
    assert artifact['cases'][3]['join']['raw_length'] == 11
    assert artifact['cases'][3]['join']['compact_length'] == 5


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output')
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    if args.self_test:
        self_test()
    artifact = build()
    if args.output:
        with open(args.output, 'wb') as handle:
            handle.write(canonical_json(artifact, pretty=True))
    elif not args.self_test:
        print(canonical_json(artifact, pretty=True).decode(), end='')
