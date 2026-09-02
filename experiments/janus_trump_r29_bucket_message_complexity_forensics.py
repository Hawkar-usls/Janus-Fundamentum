#!/usr/bin/env python3
"""R29 replay-only exact-message forensics for frozen R27/R18.

The candidate Boolean program is unchanged: select the same R27 bucket, build the
same local AND, then execute the byte-frozen R18 sequence
restrict(false) -> restrict(true) -> OR, followed by the same factor
normalization and multi-root GC.  R29 only inserts read-only DAG reachability
measurements between those operations.  It never evaluates semantic truth.
"""
from __future__ import annotations

import argparse
import inspect
import json
import time
from pathlib import Path

import janus_trump_r18_shannon_hashcons_interface_dag_discovery as r18
import janus_trump_r19_fresh_unseen_dag_holdout as r19
import janus_trump_r27_local_bucket_factored_shannon_elimination_discovery as r27

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
PREREG_PATH = REPO / 'research' / 'JANUS_TRUMP_R29_BUCKET_MESSAGE_COMPLEXITY_FORENSICS_PREREGISTRATION_2026-09-02.json'
WORLD_ID = 'R19-W05'
EXPECTED_FRAME_SHA = 'cd8e7168819401fc2510f351b0c7d319fc9cacfa400b181cf6e91cecd1288384'
EXPECTED_R27_BLOB = 'ff1139a4da7e9eaf43945995db95a6d22fb45dbe'
EXPECTED_R18_BLOB = 'afa95321ec6edbb33bef222d8ee7234fe631a599'


def load_prereg():
    d = json.loads(PREREG_PATH.read_text(encoding='utf-8'))
    assert d['status'] == 'FROZEN_BEFORE_R29_OBSERVER_IMPLEMENTATION_AND_REPLAY'
    assert d['parent_R28_result_summary_commit'] == '9059e26a1d797e3cdd75c3a385ede14ed0cfd7b3'
    assert d['frozen_R27_candidate']['git_blob_sha'] == EXPECTED_R27_BLOB
    assert d['frozen_local_machine']['git_blob_sha'] == EXPECTED_R18_BLOB
    assert d['frozen_local_machine']['exists_sequence'] == 'restrict(false), restrict(true), OR'
    assert d['observer_contract']['truth_access'] is False
    assert d['observer_contract']['semantic_verifier'] is False
    assert d['P_VS_NP'] == 'OPEN'
    return d


def dag_state(dag):
    return (
        len(dag.nodes), dag.next_id, dag.budget.nodes_created_total,
        dag.budget.restrict_calls, dag.hashcons_hits, dag.gc_calls,
        dag.gc_removed_total,
    )


def reachable_nodes(dag, root):
    """Read-only exact node-id reachability; mutation is an integrity failure."""
    before = dag_state(dag)
    seen = set()
    stack = [int(root)]
    while stack:
        nid = stack.pop()
        if nid in seen:
            continue
        if nid not in dag.nodes:
            raise AssertionError(f'R29_REACHABILITY_MISSING_NODE:{nid}')
        seen.add(nid)
        node = dag.nodes[nid]
        if node[0] in ('AND', 'OR'):
            stack.extend(node[1])
    if dag_state(dag) != before:
        raise AssertionError('R29_OBSERVER_MUTATED_DAG')
    return seen


def bucket_measurement(dag, bucket):
    sets = [reachable_nodes(dag, r) for r in bucket]
    sizes = [len(s) for s in sets]
    supports = [int(dag.support[int(r)]).bit_count() for r in bucket]
    union = set().union(*sets) if sets else set()
    pair = len(sets[0] & sets[1]) if len(sets) == 2 else None
    return {
        'bucket_factor_reachable_node_sizes': sizes,
        'bucket_factor_support_sizes': supports,
        'bucket_reachable_union_nodes': len(union),
        'bucket_reachable_sum_nodes': sum(sizes),
        'bucket_shared_node_excess': sum(sizes) - len(union),
        'bucket_pairwise_intersection_for_two_factor_bucket': pair,
    }


def phase_counters(dag):
    return {
        'nodes_created_total': int(dag.budget.nodes_created_total),
        'restrict_calls_total': int(dag.budget.restrict_calls),
        'hashcons_hits_total': int(dag.hashcons_hits),
    }


def phase_delta(before, after):
    return {
        'nodes_created': after['nodes_created_total'] - before['nodes_created_total'],
        'restrict_calls': after['restrict_calls_total'] - before['restrict_calls_total'],
        'hashcons_hits': after['hashcons_hits_total'] - before['hashcons_hits_total'],
    }


def deterministic_summary(candidate):
    p = candidate.get('partial_open_step') or {}
    return {
        'status': candidate.get('status'),
        'reason': candidate.get('reason'),
        'completed_quantification_steps': candidate.get('completed_quantification_steps'),
        'active_nodes_at_open': candidate.get('active_nodes_at_open'),
        'maximum_live_nodes': candidate.get('maximum_live_nodes'),
        'nodes_created_total': candidate.get('nodes_created_total'),
        'restrict_calls_total': candidate.get('restrict_calls_total'),
        'hashcons_hits': candidate.get('hashcons_hits'),
        'gc_calls': candidate.get('gc_calls'),
        'gc_removed_total': candidate.get('gc_removed_total'),
        'partial_open_step': {
            'step': p.get('step'),
            'quantified_var': p.get('quantified_var'),
            'factor_count_before': p.get('factor_count_before'),
            'bucket_factor_count': p.get('bucket_factor_count'),
            'bucket_union_support_size': p.get('bucket_union_support_size'),
            'before_live_nodes': p.get('before_live_nodes'),
            'active_nodes_at_open': p.get('active_nodes_at_open'),
            'partial_nodes_created_step': p.get('partial_nodes_created_step'),
            'partial_restrict_calls_step': p.get('partial_restrict_calls_step'),
            'partial_hashcons_hits_step': p.get('partial_hashcons_hits_step'),
        },
    }


def equivalence_check(candidate, prereg):
    got = deterministic_summary(candidate)
    ref = prereg['R27_equivalence_reference']
    checks = {}
    for k, v in ref.items():
        if k != 'partial_open_step':
            checks[k] = got.get(k) == v
    for k, v in ref['partial_open_step'].items():
        checks['partial_open_step.' + k] = got['partial_open_step'].get(k) == v
    return {'pass': all(checks.values()), 'checks': checks, 'expected': ref, 'observed': got}


def compile_observed(frame, bridge):
    """Execute exactly R27 while measuring exact-message structure read-only."""
    started = time.monotonic()
    budget = r18.Budget(deadline=started + r18.WALL_SECONDS)
    dag = r18.Dag(budget)
    trajectory = []
    partial = None
    current_observation = None
    phase = 'INITIALIZATION'
    phase_start = phase_counters(dag)
    max_live = len(dag.nodes)
    try:
        factors = r27.compile_initial_factors(dag, frame)
        max_live = max(max_live, len(dag.nodes), dag.max_nodes_seen)
        order = tuple(r18.elimination_order(frame, bridge))
        if len(order) != len(set(order)):
            raise AssertionError('R18_ORDER_DUPLICATE')
        for step, var in enumerate(order, start=1):
            bit = 1 << (int(var) - 1)
            before_factors = len(factors)
            before_live = len(dag.nodes)
            created0 = budget.nodes_created_total
            calls0 = budget.restrict_calls
            hits0 = dag.hashcons_hits
            bucket = tuple(r for r in factors if dag.support[r] & bit)
            rest = tuple(r for r in factors if not (dag.support[r] & bit))
            bucket_union = 0
            for r in bucket:
                bucket_union |= dag.support[r]
            current_observation = {
                'step': step,
                'quantified_var': int(var),
                **bucket_measurement(dag, bucket),
                'local_AND_reachable_nodes': None,
                'restrict_false_reachable_nodes': None,
                'restrict_true_reachable_nodes': None,
                'restrict_branch_intersection_nodes': None,
                'restrict_branch_union_nodes': None,
                'existential_OR_reachable_nodes': None,
                'phase_nodes_created': {},
                'phase_restrict_calls': {},
                'phase_hashcons_hits': {},
                'phase_at_resource_open': None,
            }
            partial = {
                'step': step,
                'quantified_var': int(var),
                'before_factors': before_factors,
                'before_live': before_live,
                'bucket_factor_count': len(bucket),
                'bucket_union_support_size': bucket_union.bit_count(),
                'created0': created0,
                'calls0': calls0,
                'hits0': hits0,
            }
            if bucket:
                phase = 'LOCAL_AND'
                phase_start = phase_counters(dag)
                local_root = bucket[0] if len(bucket) == 1 else dag.AND(*bucket)
                after = phase_counters(dag)
                d = phase_delta(phase_start, after)
                current_observation['phase_nodes_created']['LOCAL_AND'] = d['nodes_created']
                current_observation['phase_restrict_calls']['LOCAL_AND'] = d['restrict_calls']
                current_observation['phase_hashcons_hits']['LOCAL_AND'] = d['hashcons_hits']
                current_observation['local_AND_reachable_nodes'] = len(reachable_nodes(dag, local_root))

                phase = 'RESTRICT_FALSE'
                phase_start = phase_counters(dag)
                low, _memo_false = dag.restrict(local_root, int(var), False)
                after = phase_counters(dag)
                d = phase_delta(phase_start, after)
                current_observation['phase_nodes_created']['RESTRICT_FALSE'] = d['nodes_created']
                current_observation['phase_restrict_calls']['RESTRICT_FALSE'] = d['restrict_calls']
                current_observation['phase_hashcons_hits']['RESTRICT_FALSE'] = d['hashcons_hits']
                low_nodes = reachable_nodes(dag, low)
                current_observation['restrict_false_reachable_nodes'] = len(low_nodes)

                phase = 'RESTRICT_TRUE'
                phase_start = phase_counters(dag)
                high, _memo_true = dag.restrict(local_root, int(var), True)
                after = phase_counters(dag)
                d = phase_delta(phase_start, after)
                current_observation['phase_nodes_created']['RESTRICT_TRUE'] = d['nodes_created']
                current_observation['phase_restrict_calls']['RESTRICT_TRUE'] = d['restrict_calls']
                current_observation['phase_hashcons_hits']['RESTRICT_TRUE'] = d['hashcons_hits']
                high_nodes = reachable_nodes(dag, high)
                current_observation['restrict_true_reachable_nodes'] = len(high_nodes)
                current_observation['restrict_branch_intersection_nodes'] = len(low_nodes & high_nodes)
                current_observation['restrict_branch_union_nodes'] = len(low_nodes | high_nodes)

                phase = 'EXISTENTIAL_OR'
                phase_start = phase_counters(dag)
                quantified_root = dag.OR(low, high)
                after = phase_counters(dag)
                d = phase_delta(phase_start, after)
                current_observation['phase_nodes_created']['EXISTENTIAL_OR'] = d['nodes_created']
                current_observation['phase_restrict_calls']['EXISTENTIAL_OR'] = d['restrict_calls']
                current_observation['phase_hashcons_hits']['EXISTENTIAL_OR'] = d['hashcons_hits']
                current_observation['existential_OR_reachable_nodes'] = len(reachable_nodes(dag, quantified_root))

                factors = r27.normalize_factors(rest + (quantified_root,))
                pre_gc = len(dag.nodes)
                phase = 'MULTI_ROOT_GC'
                removed = r27.multi_root_gc(dag, factors)
                after_live = len(dag.nodes)
            else:
                pre_gc = len(dag.nodes)
                removed = 0
                after_live = len(dag.nodes)
            max_live = max(max_live, pre_gc, after_live, dag.max_nodes_seen)
            remaining = sum(
                1 for v in order[step:]
                if any(dag.support[r] & (1 << (v - 1)) for r in factors)
            )
            trajectory.append({
                'step': step,
                'quantified_var': int(var),
                'factor_count_before': before_factors,
                'bucket_factor_count': len(bucket),
                'bucket_union_support_size': bucket_union.bit_count(),
                'factor_count_after': len(factors),
                'before_live_nodes': before_live,
                'pre_gc_live_nodes': pre_gc,
                'after_gc_live_nodes': after_live,
                'new_nodes_created_step': budget.nodes_created_total - created0,
                'restrict_calls_step': budget.restrict_calls - calls0,
                'hashcons_hits_step': dag.hashcons_hits - hits0,
                'gc_removed_nodes': removed,
                'remaining_internal_variables_with_support': remaining,
                'message_forensics': current_observation,
            })
            partial = None
            current_observation = None
            phase = 'BETWEEN_STEPS'
        return {
            'status': 'COMPLETE_FACTORED_BRIDGE_INTERFACE',
            'completed_quantification_steps': len(trajectory),
            'active_nodes_at_open': None,
            'maximum_live_nodes': max(max_live, dag.max_nodes_seen),
            'nodes_created_total': budget.nodes_created_total,
            'restrict_calls_total': budget.restrict_calls,
            'hashcons_hits': dag.hashcons_hits,
            'gc_calls': dag.gc_calls,
            'gc_removed_total': dag.gc_removed_total,
            'partial_open_step': None,
            'trajectory': trajectory,
        }
    except r18.ResourceLimit as e:
        if current_observation is not None:
            current_observation['phase_at_resource_open'] = phase
            now = phase_counters(dag)
            d = phase_delta(phase_start, now)
            current_observation['phase_nodes_created'][phase] = d['nodes_created']
            current_observation['phase_restrict_calls'][phase] = d['restrict_calls']
            current_observation['phase_hashcons_hits'][phase] = d['hashcons_hits']
        open_partial = None
        if partial is not None:
            open_partial = {
                'step': partial['step'],
                'quantified_var': partial['quantified_var'],
                'factor_count_before': partial['before_factors'],
                'bucket_factor_count': partial['bucket_factor_count'],
                'bucket_union_support_size': partial['bucket_union_support_size'],
                'before_live_nodes': partial['before_live'],
                'active_nodes_at_open': len(dag.nodes),
                'partial_nodes_created_step': budget.nodes_created_total - partial['created0'],
                'partial_restrict_calls_step': budget.restrict_calls - partial['calls0'],
                'partial_hashcons_hits_step': dag.hashcons_hits - partial['hits0'],
                'message_forensics': current_observation,
            }
        return {
            'status': 'OPEN_RESOURCE_LIMIT',
            'reason': e.reason,
            'completed_quantification_steps': len(trajectory),
            'active_nodes_at_open': len(dag.nodes),
            'maximum_live_nodes': max(max_live, dag.max_nodes_seen),
            'nodes_created_total': budget.nodes_created_total,
            'restrict_calls_total': budget.restrict_calls,
            'hashcons_hits': dag.hashcons_hits,
            'gc_calls': dag.gc_calls,
            'gc_removed_total': dag.gc_removed_total,
            'partial_open_step': open_partial,
            'trajectory': trajectory,
        }


def observer_firewall():
    src = '\n'.join(inspect.getsource(f) for f in (
        dag_state, reachable_nodes, bucket_measurement, phase_counters,
        phase_delta, compile_observed,
    ))
    forbidden = [
        'Solver(', '.solve(', 'independent_original_allowed', 'factor_set_allowed',
        'allowed_masks', 'truth_table', 'range(1 <<', 'dpll(', 'resolve_on(',
    ]
    hits = [x for x in forbidden if x in src]
    return {'pass': not hits, 'forbidden_hits': hits}


def run():
    prereg = load_prereg()
    freeze = r19.load_freeze()
    spec = next(w for w in freeze['worlds'] if w['id'] == WORLD_ID)
    world = r19.generate_frozen_world(spec)
    if spec['frame_sha256'] != EXPECTED_FRAME_SHA:
        raise AssertionError('R19-W05 frame drift')
    fw = observer_firewall()
    candidate = compile_observed(tuple(world['frame']), tuple(world['bridge']))
    eq = equivalence_check(candidate, prereg)
    interpretation_allowed = bool(fw['pass'] and eq['pass'])
    partial = candidate.get('partial_open_step') or {}
    partial_forensics = partial.get('message_forensics') if interpretation_allowed else None
    verdict = (
        'R29_BUCKET_MESSAGE_COMPLEXITY_CAPTURED'
        if interpretation_allowed else 'R29_FAIL_OBSERVER_EQUIVALENCE'
    )
    return {
        'schema': 'JANUS/TRUMP/R29/BUCKET_MESSAGE_COMPLEXITY_FORENSICS/RESULT/v1.0',
        'created_date': '2026-09-02',
        'scientific_role': 'REPLAY_ONLY_EXACT_MESSAGE_FORENSICS__NO_LOGIC_CHANGE__NO_SEMANTIC_TRUTH',
        'world_id': WORLD_ID,
        'frame_sha256': EXPECTED_FRAME_SHA,
        'frozen_R27_blob': EXPECTED_R27_BLOB,
        'frozen_R18_blob': EXPECTED_R18_BLOB,
        'verdict': verdict,
        'observer_firewall': fw,
        'R27_observer_equivalence': eq,
        'analysis': {
            'trajectory': candidate.get('trajectory', []) if interpretation_allowed else None,
            'partial_open_step': partial if interpretation_allowed else None,
            'fatal_message_forensics': partial_forensics,
            'phase_at_resource_open': (
                partial_forensics.get('phase_at_resource_open')
                if partial_forensics else None
            ),
            'interpretation_allowed': interpretation_allowed,
        },
        'truth_accessed': False,
        'semantic_verifier_ran': False,
        'claim_ceiling': prereg['claim_ceiling'],
        'next_gate_rule': prereg['next_gate_rule'],
        'seal': 'THE_OBSERVER_COUNTED_THE_MESSAGE_WITHOUT_EDITING_A_SINGLE_BOOLEAN_OPERATION',
        'P_VS_NP': 'OPEN',
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', required=True)
    args = ap.parse_args()
    out = run()
    Path(args.output).write_text(
        json.dumps(out, indent=2, sort_keys=True) + '\n', encoding='utf-8'
    )
    f = (out.get('analysis') or {}).get('fatal_message_forensics') or {}
    print(json.dumps({
        'verdict': out['verdict'],
        'equivalence': out['R27_observer_equivalence']['pass'],
        'phase_at_resource_open': f.get('phase_at_resource_open'),
        'fatal_bucket_factor_nodes': f.get('bucket_factor_reachable_node_sizes'),
        'fatal_bucket_shared_node_excess': f.get('bucket_shared_node_excess'),
        'fatal_local_AND_reachable_nodes': f.get('local_AND_reachable_nodes'),
        'fatal_restrict_false_reachable_nodes': f.get('restrict_false_reachable_nodes'),
        'fatal_restrict_true_reachable_nodes': f.get('restrict_true_reachable_nodes'),
        'fatal_restrict_branch_intersection_nodes': f.get('restrict_branch_intersection_nodes'),
        'fatal_existential_OR_reachable_nodes': f.get('existential_OR_reachable_nodes'),
        'P_VS_NP': 'OPEN',
    }, indent=2, sort_keys=True))
    return 2 if out['verdict'] == 'R29_FAIL_OBSERVER_EQUIVALENCE' else 0


if __name__ == '__main__':
    raise SystemExit(main())
