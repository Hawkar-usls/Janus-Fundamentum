from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import defaultdict
from pathlib import Path

SCHEMA = 'janus.c049_1.corrected_node9_residual_compact_frontier_candidate.v1'
SPEC_SCHEMA = 'janus.c049_1.corrected_node9_residual_compact_frontier_spec.v1'
SCALAR_SCHEMA = 'janus.c049_1.corrected_node9_scalar_symbolic_automaton_candidate.v1'
Q80_SCHEMA = 'C049.1-B4.6.3-CORRECTED-NODE9-QUOTIENT-SKELETON-STABILITY-ANALYSIS-v1'
SPEC_SHA = '5e7141cfe628a2e0324bafec22febb1d9cec5776c2fb0dea516dfb2252b582c8'
SCALAR_SHA = 'b953c89f95f3deee18fe92080b0988846603a46c17e0f51bcfa2eef50d325aca'
SCALAR_SEM = 'cecafe9a26119c2b035db65d3d98f8f4f81cb033ce5616b8089c3e3207d7eae1'
Q80_SHA = 'fa21c129ad7c03cad0f46c5a5baeb3941d0c94baadea54718d8059652f3a3375'
Q80_SEM = '1463974e2378c60ca6f2ebba961c5366a98c59f9efc65603851e87239229f4a1'
SEED = 0xC049120
TERM = 'OPEN_TRAJECTORY_ENGINE_INCOMPLETE'


def canonical_bytes(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def digest(value):
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(value, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_bytes(canonical_bytes(value) + b'\n')


def semantic_ok(artifact):
    return (
        artifact.get('semantic_digest_scope') == 'proof_payload'
        and digest(artifact.get('proof_payload')) == artifact.get('semantic_digest')
    )


def ordered(items, mode, tag):
    out = list(items)
    if mode == 'REVERSED':
        out.reverse()
    elif mode == 'SEEDED_SHUFFLE':
        salt = int(hashlib.sha256(tag.encode()).hexdigest()[:16], 16)
        random.Random(SEED ^ salt).shuffle(out)
    return out


def check_spec(path):
    if file_sha(path) != SPEC_SHA:
        raise AssertionError('SPEC_SHA')
    spec = load(path)
    if (
        spec.get('schema') != SPEC_SCHEMA
        or spec.get('status') != 'SPEC_FROZEN'
        or spec.get('admission') is not False
        or spec.get('next_gate') != 'CLOSED'
    ):
        raise AssertionError('SPEC_BINDING')
    policy = spec['expected_values_policy']
    keys = (
        'expected_mixed_domain_count',
        'expected_accepted_run_count',
        'expected_global_compact_outcome_count',
        'expected_per_domain_compact_outcome_count',
        'expected_post_compact_generator_count',
    )
    if any(policy[key] is not None for key in keys):
        raise AssertionError('OUTPUT_ORACLE')
    if policy['historical_or_local_values_may_seed_expected_values'] is not False:
        raise AssertionError('OUTPUT_ORACLE_POLICY')
    return spec


def bind(path, sha, semantic, schema):
    if file_sha(path) != sha:
        raise AssertionError(('FILE_SHA', str(path)))
    artifact = load(path)
    if artifact.get('schema') != schema or not semantic_ok(artifact):
        raise AssertionError(('SEMANTIC_BINDING', str(path)))
    if artifact.get('semantic_digest') != semantic:
        raise AssertionError(('SEMANTIC_DIGEST', str(path)))
    return artifact


def languages(receipt):
    return tuple(
        tuple(tuple(int(value) for value in word) for word in segment['words'])
        for segment in receipt['segment_languages']
    )


def encode_stat(stat):
    left, right, value = stat
    return {'left': list(left), 'right': list(right), 'value': int(value)}


def encode_sequence(sequence):
    return [encode_stat(stat) for stat in sequence]


def sequence_digest(sequence):
    return digest(encode_sequence(sequence))


def interval_rule(sequence, i, j):
    if j - i <= 1:
        return False
    if (sequence[i][0], sequence[i][1]) != (sequence[j][0], sequence[j][1]):
        return False
    start = sequence[i][2]
    end = sequence[j][2]
    interior = [stat[2] for stat in sequence[i + 1:j]]
    increasing = start <= end and all(start <= value <= end for value in interior)
    decreasing = start >= end and all(start >= value >= end for value in interior)
    return increasing or decreasing


def compactify(sequence):
    sequence = list(sequence)
    if not sequence:
        raise ValueError('empty trajectory')
    trace = []
    while True:
        changed = False
        for index in range(1, len(sequence)):
            if sequence[index - 1] != sequence[index]:
                continue
            removed = [sequence[index]]
            before = len(sequence)
            del sequence[index]
            trace.append({
                'rule': 'duplicate',
                'start': index - 1,
                'end': index,
                'before_length': before,
                'removed_entries': encode_sequence(removed),
                'after_length': len(sequence),
                'after_digest': sequence_digest(sequence),
            })
            changed = True
            break
        if changed:
            continue
        for i in range(len(sequence)):
            for j in range(i + 2, len(sequence)):
                if not interval_rule(sequence, i, j):
                    continue
                removed = sequence[i + 1:j]
                before = len(sequence)
                del sequence[i + 1:j]
                trace.append({
                    'rule': 'interval',
                    'start': i,
                    'end': j,
                    'before_length': before,
                    'removed_entries': encode_sequence(removed),
                    'after_length': len(sequence),
                    'after_digest': sequence_digest(sequence),
                })
                changed = True
                break
            if changed:
                break
        if not changed:
            return tuple(sequence), trace


def contains(big, small):
    return not small or big == (1,)


def validate_compact(sequence):
    if not sequence or sequence[0][1] != sequence[-1][0]:
        raise AssertionError('COMPACT_ENDPOINT')
    for left, right in zip(sequence, sequence[1:]):
        if not contains(right[0], left[0]) or not contains(left[1], right[1]):
            raise AssertionError('COMPACT_MONOTONICITY')
    if compactify(sequence)[0] != tuple(sequence):
        raise AssertionError('NOT_COMPACT')
    if max(stat[2] for stat in sequence) > 1:
        raise AssertionError('COMPACT_WIDTH')


def run_record(domain, left_profile, right_profile, steps, state_path):
    quotient = [tuple(map(int, cell)) for cell in domain['quotient_path']]
    geometry = [
        (tuple(map(int, row['left'])), tuple(map(int, row['right'])))
        for row in domain['projected_geometry']
    ]
    correction = [
        int(join) + int(shrink)
        for join, shrink in zip(
            domain['join_correction_vector'], domain['shrink_correction_vector']
        )
    ]
    precompact = []
    for quotient_cell_index, left_offset, right_offset in state_path:
        left_segment, right_segment = quotient[quotient_cell_index]
        value = (
            left_profile[left_segment][left_offset]
            + right_profile[right_segment][right_offset]
            + correction[quotient_cell_index]
        )
        if value > 1:
            raise AssertionError('NON_ACCEPTED_RUN')
        left, right = geometry[quotient_cell_index]
        precompact.append((left, right, value))
    compact, trace = compactify(precompact)
    validate_compact(compact)
    provenance = {
        'domain_id': domain['domain_id'],
        'left_profile': [list(word) for word in left_profile],
        'right_profile': [list(word) for word in right_profile],
        'fine_steps': list(steps),
        'fine_state_path': [
            {
                'quotient_cell_index': q,
                'left_offset': i,
                'right_offset': j,
            }
            for q, i, j in state_path
        ],
    }
    run_id = 'AR-' + digest(provenance)[:24]
    compact_encoded = encode_sequence(compact)
    compact_id = 'CT-' + digest(compact_encoded)[:24]
    record = {
        'run_id': run_id,
        'domain_id': domain['domain_id'],
        'source_class_id': domain['source_class_id'],
        'provenance': provenance,
        'precompact_trajectory': encode_sequence(precompact),
        'precompact_trajectory_digest': sequence_digest(precompact),
        'compact_trajectory_id': compact_id,
        'compact_trajectory': compact_encoded,
        'compact_trajectory_digest': digest(compact_encoded),
        'compactification_trace': trace,
        'compactification_trace_digest': digest(trace),
        'compact_width': max(stat[2] for stat in compact),
    }
    record['run_record_digest'] = digest(record)
    return record


def enumerate_domain(domain, left_languages, right_languages, mode):
    quotient = tuple(tuple(map(int, cell)) for cell in domain['quotient_path'])
    if not quotient or quotient[0] != (0, 0):
        raise AssertionError('QPATH_START')
    if quotient[-1] != (len(left_languages) - 1, len(right_languages) - 1):
        raise AssertionError('QPATH_END')
    correction = tuple(
        int(join) + int(shrink)
        for join, shrink in zip(
            domain['join_correction_vector'], domain['shrink_correction_vector']
        )
    )
    starts = []
    for left_word in ordered(left_languages[0], mode, domain['domain_id'] + ':L0'):
        for right_word in ordered(right_languages[0], mode, domain['domain_id'] + ':R0'):
            starts.append((
                0, left_word, right_word, 0, 0,
                (left_word,), (right_word,), tuple(), ((0, 0, 0),),
            ))
    starts = ordered(starts, mode, domain['domain_id'] + ':STARTS')
    output = []

    def value(q, left_word, right_word, left_offset, right_offset):
        return left_word[left_offset] + right_word[right_offset] + correction[q]

    def terminal(q, left_word, right_word, left_offset, right_offset):
        left_segment, right_segment = quotient[q]
        return (
            q == len(quotient) - 1
            and left_segment == len(left_languages) - 1
            and right_segment == len(right_languages) - 1
            and left_offset == len(left_word) - 1
            and right_offset == len(right_word) - 1
        )

    def visit(state):
        q, left_word, right_word, i, j, left_profile, right_profile, steps, path = state
        if value(q, left_word, right_word, i, j) > 1:
            return
        if terminal(q, left_word, right_word, i, j):
            if len(left_profile) != len(left_languages) or len(right_profile) != len(right_languages):
                raise AssertionError('INCOMPLETE_PROFILE')
            output.append(run_record(domain, left_profile, right_profile, steps, path))
            return
        left_segment, right_segment = quotient[q]
        successors = []
        if i + 1 < len(left_word):
            successors.append((q, left_word, right_word, i + 1, j, left_profile, right_profile, steps + ('H_INTERNAL',), path + ((q, i + 1, j),)))
        elif q + 1 < len(quotient) and quotient[q + 1] == (left_segment + 1, right_segment):
            for next_left in ordered(left_languages[left_segment + 1], mode, domain['domain_id'] + f':L{left_segment + 1}'):
                successors.append((q + 1, next_left, right_word, 0, j, left_profile + (next_left,), right_profile, steps + ('H_CELL',), path + ((q + 1, 0, j),)))
        if j + 1 < len(right_word):
            successors.append((q, left_word, right_word, i, j + 1, left_profile, right_profile, steps + ('V_INTERNAL',), path + ((q, i, j + 1),)))
        elif q + 1 < len(quotient) and quotient[q + 1] == (left_segment, right_segment + 1):
            for next_right in ordered(right_languages[right_segment + 1], mode, domain['domain_id'] + f':R{right_segment + 1}'):
                successors.append((q + 1, left_word, next_right, i, 0, left_profile, right_profile + (next_right,), steps + ('V_CELL',), path + ((q + 1, i, 0),)))
        if mode == 'REVERSED':
            successors.reverse()
        elif mode == 'SEEDED_SHUFFLE':
            salt = int(hashlib.sha256((domain['domain_id'] + str(path)).encode()).hexdigest()[:16], 16)
            random.Random(SEED ^ salt).shuffle(successors)
        for successor in successors:
            visit(successor)

    for start in starts:
        visit(start)
    unique = {record['run_id']: record for record in output}
    if len(unique) != len(output):
        raise AssertionError('RUN_DUPLICATE')
    return [unique[key] for key in sorted(unique)]


def outcome_record(trajectory_id, trajectory, runs):
    run_ids = sorted(run['run_id'] for run in runs)
    return {
        'compact_trajectory_id': trajectory_id,
        'trajectory': trajectory,
        'trajectory_digest': digest(trajectory),
        'width': max(row['value'] for row in trajectory),
        'length': len(trajectory),
        'accepted_run_multiplicity': len(runs),
        'run_ids_digest': digest(run_ids),
    }


def build(spec_path, scalar_path, q80_path, output_path, mode):
    spec = check_spec(spec_path)
    scalar = bind(scalar_path, SCALAR_SHA, SCALAR_SEM, SCALAR_SCHEMA)
    q80 = bind(q80_path, Q80_SHA, Q80_SEM, Q80_SCHEMA)
    scalar_payload = scalar['proof_payload']
    q80_payload = q80['proof_payload']
    if scalar_payload['classification_summary']['classification_promoted_to_repository_success_or_failure'] is not False:
        raise AssertionError('UPSTREAM_PROMOTION')
    q80_by_id = {row['domain_id']: row for row in q80_payload['quotient_domains']}
    receipt_by_class = {
        row['source_class_id']: row
        for row in scalar_payload['scalar_factorization']['node8_source_class_receipts']
    }
    right_languages = languages(scalar_payload['scalar_factorization']['leaf5_receipt'])
    mixed = ordered(
        [row for row in scalar_payload['domain_records'] if row['classification'] == 'MIXED'],
        mode,
        'MIXED_DOMAINS',
    )
    all_runs = []
    domain_frontiers = []
    for scalar_row in mixed:
        domain = q80_by_id.get(scalar_row['domain_id'])
        if domain is None:
            raise AssertionError('Q80_DOMAIN_MISSING')
        for key in ('source_class_id', 'quotient_path', 'join_correction_vector', 'shrink_correction_vector'):
            if scalar_row[key] != domain[key]:
                raise AssertionError(('Q80_LINK', scalar_row['domain_id'], key))
        if (
            scalar_row['q80_fine_lift_domain_digest'] != domain['fine_lift_domain_digest']
            or scalar_row['q80_fine_lift_multiplicity'] != domain['fine_lift_multiplicity']
        ):
            raise AssertionError('Q80_MULTIPLICITY_LINK')
        left_languages = languages(receipt_by_class[scalar_row['source_class_id']])
        runs = enumerate_domain(domain, left_languages, right_languages, mode)
        upstream_accepted = scalar_row['width_filtered_automaton']['run_multiplicity']
        if len(runs) != upstream_accepted:
            raise AssertionError(('ACCEPTED_COUNT', scalar_row['domain_id']))
        all_runs.extend(runs)
        grouped = defaultdict(list)
        for run in runs:
            grouped[run['compact_trajectory_id']].append(run)
        outcomes = [
            outcome_record(trajectory_id, grouped[trajectory_id][0]['compact_trajectory'], grouped[trajectory_id])
            for trajectory_id in sorted(grouped)
        ]
        domain_frontiers.append({
            'domain_id': scalar_row['domain_id'],
            'source_class_id': scalar_row['source_class_id'],
            'upstream_accepted_run_multiplicity': upstream_accepted,
            'materialized_accepted_run_count': len(runs),
            'accepted_run_ids_digest': digest(sorted(run['run_id'] for run in runs)),
            'distinct_compact_outcome_count': len(outcomes),
            'compact_outcomes': outcomes,
        })
    all_runs.sort(key=lambda row: row['run_id'])
    domain_frontiers.sort(key=lambda row: row['domain_id'])
    if len({row['run_id'] for row in all_runs}) != len(all_runs):
        raise AssertionError('GLOBAL_RUN_DUPLICATE')
    global_grouped = defaultdict(list)
    for run in all_runs:
        global_grouped[run['compact_trajectory_id']].append(run)
    global_outcomes = []
    for trajectory_id in sorted(global_grouped):
        runs = global_grouped[trajectory_id]
        row = outcome_record(trajectory_id, runs[0]['compact_trajectory'], runs)
        row['source_domain_ids'] = sorted({run['domain_id'] for run in runs})
        global_outcomes.append(row)
    ledger = scalar_payload['conservation_ledger']
    total = ledger['derived_unrestricted_symbolic_run_total']
    accepted = ledger['derived_width_le_1_run_total']
    rejected = ledger['derived_width_gt_1_run_total']
    if len(all_runs) != accepted or total != accepted + rejected:
        raise AssertionError('CONSERVATION')
    if sum(row['accepted_run_multiplicity'] for row in global_outcomes) != accepted:
        raise AssertionError('FRONTIER_MULTIPLICITY')
    proof = {
        'candidate_phase': 'RESIDUAL_COMPACT_FRONTIER',
        'candidate_status': 'PRODUCER_DERIVED_CANDIDATE',
        'admitted': False,
        'spec_binding': {
            'spec_schema': SPEC_SCHEMA,
            'spec_file_sha256': SPEC_SHA,
            'parent_scalar_spec_subject': spec['parent_scalar_spec']['subject'],
            'upstream_admission_review_id': spec['upstream_scalar_candidate_admission']['review_id'],
            'upstream_head_subject': spec['upstream_scalar_candidate_admission']['head_subject'],
        },
        'source_binding_receipt': {
            'scalar_candidate_sha256': SCALAR_SHA,
            'scalar_candidate_semantic_digest': SCALAR_SEM,
            'q80_sha256': Q80_SHA,
            'q80_semantic_digest': Q80_SEM,
        },
        'residual_domain_selection': {
            'selection_rule': 'classification == MIXED',
            'selected_domain_count': len(domain_frontiers),
            'selected_domain_ids': sorted(row['domain_id'] for row in domain_frontiers),
            'expected_count_used': False,
        },
        'accepted_run_records': all_runs,
        'domain_frontiers': domain_frontiers,
        'global_compact_frontier': {
            'distinct_compact_trajectory_count': len(global_outcomes),
            'outcomes': global_outcomes,
            'frontier_catalog_digest': digest(global_outcomes),
            'expected_count_used': False,
        },
        'conservation_ledger': {
            'upstream_fine_refinements': total,
            'upstream_width_le_1_multiplicity': accepted,
            'upstream_width_gt_1_multiplicity': rejected,
            'materialized_accepted_runs': len(all_runs),
            'materialized_failed_fine_paths': 0,
            'global_compact_outcome_multiplicity_sum': sum(row['accepted_run_multiplicity'] for row in global_outcomes),
            'omitted_accepted_runs': 0,
            'duplicated_accepted_runs': 0,
            'fine_refinement_partition_preserved': total == accepted + rejected,
        },
        'work_ledger': {
            'mixed_domains_processed': len(domain_frontiers),
            'accepted_runs_materialized': len(all_runs),
            'failed_fine_paths_materialized': 0,
            'compactification_traces_materialized': len(all_runs),
            'global_compact_outcomes_materialized': len(global_outcomes),
        },
        'determinism': {
            'required_order_modes': ['ORIGINAL', 'REVERSED', 'SEEDED_SHUFFLE'],
            'seed_hex': '0xC049120',
            'input_order_mode_not_serialized': True,
            'canonical_run_order': True,
            'canonical_domain_order': True,
            'canonical_frontier_order': True,
            'byte_identical_output_required': True,
        },
        'strict_boundary': {
            'node9_scalar_automaton_candidate_complete': True,
            'node9_residual_compact_frontier_spec_frozen': True,
            'node9_residual_compact_frontier_producer_created': True,
            'node9_residual_compact_frontier_verifier_created': False,
            'node9_frontier_candidate_complete': False,
            'node9_parent_refinement_complete': False,
            'node9_parent_up_k_complete': False,
            'node9_integrated_into_bottom_up_executor': False,
            'repository_failed_domains': 0,
            'repository_successful_domains': 0,
            'root_reached': False,
            'found_layout': 'FORBIDDEN',
            'no_layout_at_cap': 'FORBIDDEN',
            'formal_admission': 'BLOCKED',
            'next_gate': 'CLOSED',
            'current_global_terminal': TERM,
            'p_vs_np': 'OPEN',
        },
        'result': 'PRODUCER_DERIVED_RESIDUAL_COMPACT_FRONTIER_WITHOUT_ADMISSION',
    }
    artifact = {
        'schema': SCHEMA,
        'semantic_digest_scope': 'proof_payload',
        'proof_payload': proof,
    }
    artifact['semantic_digest'] = digest(proof)
    save(artifact, output_path)
    return artifact


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--spec', type=Path, required=True)
    parser.add_argument('--scalar-artifact', type=Path, required=True)
    parser.add_argument('--q80-artifact', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--order-mode', choices=('ORIGINAL', 'REVERSED', 'SEEDED_SHUFFLE'), default='ORIGINAL')
    args = parser.parse_args()
    artifact = build(args.spec, args.scalar_artifact, args.q80_artifact, args.output, args.order_mode)
    payload = artifact['proof_payload']
    print('JANUS_NODE9_RESIDUAL_COMPACT_FRONTIER_PRODUCER = PASS')
    print('MIXED_DOMAINS_PROCESSED =', payload['residual_domain_selection']['selected_domain_count'])
    print('ACCEPTED_RUNS_MATERIALIZED =', payload['conservation_ledger']['materialized_accepted_runs'])
    print('GLOBAL_COMPACT_TRAJECTORIES =', payload['global_compact_frontier']['distinct_compact_trajectory_count'])
    print('FAILED_FINE_PATHS_MATERIALIZED =', payload['conservation_ledger']['materialized_failed_fine_paths'])
    print('SEMANTIC_DIGEST =', artifact['semantic_digest'])
    print('FORMAL_ADMISSION = BLOCKED')
    print('NEXT_GATE = CLOSED')
    print('P_VS_NP = OPEN')


if __name__ == '__main__':
    main()
