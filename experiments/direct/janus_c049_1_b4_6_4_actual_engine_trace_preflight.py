#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, random
from pathlib import Path

SCHEMA = 'janus.c049_1.b4_6_4.actual_engine_trace_preflight_candidate.v1'
BLOCKS = ((2,), (4,), (6,), (3,), (5,), (1,))
K = 1
D = 3
SEED = 0xC049164A


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':')).encode()

def digest(x):
    return hashlib.sha256(canonical(x)).hexdigest()

def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def save(x, path):
    Path(path).write_bytes(canonical(x) + b'\n')

def basis(rows):
    table = {}
    for raw in rows:
        x = int(raw)
        if x < 0 or x >= (1 << D):
            raise AssertionError('vector range')
        while x:
            p = x.bit_length() - 1
            if p in table:
                x ^= table[p]
                continue
            table[p] = x
            for q, r in list(table.items()):
                if q != p and ((r >> p) & 1):
                    table[q] = r ^ x
            break
    for p in sorted(table):
        for q in sorted(table, reverse=True):
            if q != p and ((table[q] >> p) & 1):
                table[q] ^= table[p]
    return tuple(table[p] for p in sorted(table, reverse=True))

def span(rows):
    out = {0}
    for row in basis(rows):
        out |= {x ^ row for x in tuple(out)}
    return out

def meet(a, b):
    return basis(sorted(span(a) & span(b)))

def plus(a, b):
    return basis((*a, *b))

def subset(a, b):
    return span(a) <= span(b)

def factor_span(indices):
    return basis(v for i in indices for v in BLOCKS[i])

def boundary(indices):
    inside = set(indices)
    return meet(factor_span(indices), factor_span([i for i in range(len(BLOCKS)) if i not in inside]))

def ordered_nodes(mode):
    nodes = list(range(6, 11))
    if mode == 'REVERSED':
        nodes.reverse()
    elif mode == 'SEEDED_SHUFFLE':
        random.Random(SEED).shuffle(nodes)
    elif mode != 'ORIGINAL':
        raise AssertionError('order mode')
    return nodes

def node_record(node):
    right_factor = node - 5
    covered = tuple(range(right_factor + 1))
    left = tuple(range(right_factor))
    right = (right_factor,)
    left_b = boundary(left)
    right_b = boundary(right)
    parent_b = boundary(covered)
    bprime = plus(left_b, right_b)
    lv = factor_span(left)
    rv = factor_span(right)
    expand_left = subset(left_b, bprime) and meet(lv, bprime) == left_b
    expand_right = subset(right_b, bprime) and meet(rv, bprime) == right_b
    join_sep = meet(plus(lv, bprime), plus(rv, bprime)) == bprime
    shrink = subset(parent_b, bprime)
    return {
        'node_id': node,
        'left_factor_indices': list(left),
        'right_factor_indices': list(right),
        'covered_factor_indices': list(covered),
        'left_boundary': list(left_b),
        'right_boundary': list(right_b),
        'join_boundary_bprime': list(bprime),
        'parent_boundary': list(parent_b),
        'left_span': list(lv),
        'right_span': list(rv),
        'caller_certificates': {
            'o2_expand_left': expand_left,
            'o2_expand_right': expand_right,
            'o3_join_separation': join_sep,
            'o4_shrink_containment': shrink,
        },
    }

def build(ledger_path, hardening_path, out_path, mode):
    ledger = load(ledger_path)
    hardening = load(hardening_path)
    if ledger.get('schema') != 'janus.c049_1.b4_6_4.general_structural_induction_authority_gap_ledger.v1':
        raise AssertionError('ledger schema')
    hp = hardening.get('hardening_payload', {})
    if hardening.get('semantic_digest_scope') != 'hardening_payload' or digest(hp) != hardening.get('semantic_digest'):
        raise AssertionError('hardening semantic digest')
    if hp.get('implementation_gate', {}).get('may_admit_actual_engine_composition_without_node8_authority') is not False:
        raise AssertionError('node8 authority bypass')
    records = [node_record(n) for n in ordered_nodes(mode)]
    records.sort(key=lambda x: x['node_id'])
    if not all(all(r['caller_certificates'].values()) for r in records):
        raise AssertionError('caller premise failure')
    entries = {x['edge_id']: x for x in ledger['entries']}
    node8 = entries['NODE8_PARENT_REFINEMENT_TO_NODE8_UP_K']
    q80 = entries['NODE8_UP_K_TO_NODE9_Q80']
    payload = {
        'phase': 'ACTUAL_CORRECTED_ENGINE_TRACE_PREFLIGHT',
        'status': 'PREFLIGHT_COMPLETE_BLOCKED_ON_AUTHORITY_AND_REQUIRED_REPLAYS',
        'admitted': False,
        'target': {'ambient_dim': D, 'k': K, 'whole_factor_blocks': [list(x) for x in BLOCKS], 'tree': 'LEFT_DEEP_6_FACTOR'},
        'derived_leaf_boundaries': [{'factor_index': i, 'boundary': list(boundary((i,)))} for i in range(len(BLOCKS))],
        'derived_internal_nodes': records,
        'path_domains': {'ordinary_join_steps': [[1,0],[0,1]], 'ordinary_join_diagonal_allowed': False, 'extension_preorder_steps': [[1,0],[0,1],[1,1]]},
        'authority': {
            'general_composition_receipt': hp['general_composition_authority'],
            'node8_up_k': {
                'proof_subject': node8['candidate_proof_head'],
                'semantic_audit': node8['semantic_audit'],
                'semantic_audit_review_id': node8['independent_semantic_audit_review_id'],
                'exact_head_ci': node8['exact_head_ci'],
                'semantic_admission': node8['semantic_admission'],
                'status': node8['status'],
            },
            'q80': {
                'historical_standalone_admission': q80['q80_historical_reviewer_bound_admission'],
                'composition_replay_required': True,
                'status': q80['status'],
            },
        },
        'blockers': sorted(ledger['current_blockers']),
        'required_replays': sorted(ledger['composition_replays_required']),
        'preflight_conclusions': {
            'all_o2_o3_o4_geometry_caller_premises_hold_on_frozen_tree': True,
            'general_composition_authority_bound': True,
            'node8_authority_closed': node8['status'] != 'OPEN_HARD_BLOCKER',
            'q80_composition_replay_complete': False,
            'root_empty_consumed_as_premise': False,
            'actual_corrected_engine_complete_algorithm1_trace_established': False,
            'engine_root_full_set_equals_fs_k_v_zero': False,
            'ready_for_composition_admission': False,
        },
        'strict_boundary': {
            'root_empty_proved': True,
            'structural_induction_proved_for_actual_engine': False,
            'terminal_completeness_proved': False,
            'no_layout_at_cap': 'FORBIDDEN',
            'found_layout': 'FORBIDDEN',
            'formal_admission': 'BLOCKED',
            'current_global_terminal': 'OPEN_TRAJECTORY_ENGINE_INCOMPLETE',
            'p_vs_np': 'OPEN',
        },
        'determinism': {'required_order_modes': ['ORIGINAL','REVERSED','SEEDED_SHUFFLE'], 'input_order_mode_not_serialized': True, 'seed_hex': '0xC049164A'},
    }
    art = {'schema': SCHEMA, 'semantic_digest_scope': 'proof_payload', 'proof_payload': payload}
    art['semantic_digest'] = digest(payload)
    save(art, out_path)
    return art

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ledger', type=Path, required=True)
    ap.add_argument('--hardening', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--order-mode', choices=('ORIGINAL','REVERSED','SEEDED_SHUFFLE'), default='ORIGINAL')
    a = ap.parse_args()
    art = build(a.ledger, a.hardening, a.output, a.order_mode)
    p = art['proof_payload']
    print('JANUS_ACTUAL_ENGINE_TRACE_PREFLIGHT_PRODUCER = PASS')
    print('INTERNAL_NODE_CALLER_PREMISES = 5/5')
    print('NODE8_AUTHORITY_CLOSED =', p['preflight_conclusions']['node8_authority_closed'])
    print('Q80_COMPOSITION_REPLAY_COMPLETE = FALSE')
    print('ROOT_EMPTY_CONSUMED_AS_PREMISE = FALSE')
    print('ACTUAL_CORRECTED_ENGINE_COMPLETE_ALGORITHM1_TRACE_ESTABLISHED = FALSE')
    print('READY_FOR_COMPOSITION_ADMISSION = FALSE')
    print('P_VS_NP = OPEN')
    print('SEMANTIC_DIGEST =', art['semantic_digest'])

if __name__ == '__main__':
    main()
