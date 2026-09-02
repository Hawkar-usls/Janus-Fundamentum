#!/usr/bin/env python3
"""R30 counterfactual branch-isolation forensics over the frozen R27/R18 machine.

R30 does not modify Boolean semantics.  It independently rebuilds the exact
R27 state through step 24 and the step-25 local AND twice.  One fresh replay
executes only restrict(false), the other only restrict(true).  No OR is run.
The purpose is only to distinguish an intrinsic single-branch resource wall
from sequential DAG-budget accumulation seen in R29.
"""
from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import time
from pathlib import Path

import janus_trump_r18_shannon_hashcons_interface_dag_discovery as r18
import janus_trump_r19_fresh_unseen_dag_holdout as r19
import janus_trump_r27_local_bucket_factored_shannon_elimination_discovery as r27
import janus_trump_r29_bucket_message_complexity_forensics as r29

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
PREREG_PATH = REPO / 'research' / 'JANUS_TRUMP_R30_RESTRICTION_BRANCH_ISOLATION_FORENSICS_PREREGISTRATION_2026-09-02.json'
WORLD_ID = 'R19-W05'
EXPECTED_FRAME_SHA = 'cd8e7168819401fc2510f351b0c7d319fc9cacfa400b181cf6e91cecd1288384'
EXPECTED_R27_BLOB = 'ff1139a4da7e9eaf43945995db95a6d22fb45dbe'
EXPECTED_R18_BLOB = 'afa95321ec6edbb33bef222d8ee7234fe631a599'
EXPECTED_R29_PREHISTORY_TRAJECTORY_SHA256 = '071887c30e393bfb74f5c15bff6bfa6fde2f3798a48ec204aae823f756ea429b'
FATAL_STEP = 25
FATAL_VAR = 52


def canonical_sha(obj) -> str:
    raw = json.dumps(obj, sort_keys=True, separators=(',', ':')).encode('utf-8')
    return hashlib.sha256(raw).hexdigest()


def load_prereg():
    d = json.loads(PREREG_PATH.read_text(encoding='utf-8'))
    assert d['status'] == 'FROZEN_BEFORE_R30_OBSERVER_IMPLEMENTATION_AND_REPLAY'
    assert d['parent_R29_sealed_result_commit'] == '1f1ca71c4a7a23dcca463fde5e3787772bbeac8e'
    assert d['frozen_inputs']['R27_candidate_git_blob'] == EXPECTED_R27_BLOB
    assert d['frozen_inputs']['R18_machine_git_blob'] == EXPECTED_R18_BLOB
    assert d['frozen_inputs']['world_id'] == WORLD_ID
    assert d['frozen_inputs']['frame_sha256'] == EXPECTED_FRAME_SHA
    assert d['frozen_inputs']['resource_node_cap'] == r18.MAX_NODES == 1_000_000
    assert d['frozen_inputs']['fatal_step'] == FATAL_STEP
    assert d['frozen_inputs']['quantified_var'] == FATAL_VAR
    protocol = d['counterfactual_isolation_protocol']
    assert protocol['final_OR_forbidden'] is True
    assert protocol['Boolean_operator_change_forbidden'] is True
    assert protocol['elimination_order_change_forbidden'] is True
    assert protocol['memoization_or_hashcons_policy_change_forbidden'] is True
    assert protocol['truth_access'] is False
    assert protocol['semantic_verifier'] is False
    assert d['P_VS_NP'] == 'OPEN'
    return d


def dag_fingerprint(dag) -> str:
    """Streaming read-only structural fingerprint; no canonicalization/mutation."""
    before = r29.dag_state(dag)
    h = hashlib.sha256()
    h.update(f'next_id={dag.next_id};nodes={len(dag.nodes)}\n'.encode())
    for nid in sorted(dag.nodes):
        h.update(str(nid).encode()); h.update(b'|')
        h.update(repr(dag.nodes[nid]).encode()); h.update(b'|')
        h.update(str(int(dag.support[nid])).encode()); h.update(b'\n')
    if r29.dag_state(dag) != before:
        raise AssertionError('R30_FINGERPRINT_MUTATED_DAG')
    return h.hexdigest()


def replay_completed_step(dag, factors, order, step, var):
    """Exact R29/R27 step, including read-only message measurements."""
    bit = 1 << (int(var) - 1)
    before_factors = len(factors)
    before_live = len(dag.nodes)
    created0 = dag.budget.nodes_created_total
    calls0 = dag.budget.restrict_calls
    hits0 = dag.hashcons_hits
    bucket = tuple(r for r in factors if dag.support[r] & bit)
    rest = tuple(r for r in factors if not (dag.support[r] & bit))
    bucket_union = 0
    for root in bucket:
        bucket_union |= dag.support[root]
    obs = {
        'step': step,
        'quantified_var': int(var),
        **r29.bucket_measurement(dag, bucket),
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
    if not bucket:
        raise AssertionError(f'R30_UNEXPECTED_EMPTY_BUCKET_AT_COMPLETED_STEP:{step}')

    phase0 = r29.phase_counters(dag)
    local_root = bucket[0] if len(bucket) == 1 else dag.AND(*bucket)
    d = r29.phase_delta(phase0, r29.phase_counters(dag))
    obs['phase_nodes_created']['LOCAL_AND'] = d['nodes_created']
    obs['phase_restrict_calls']['LOCAL_AND'] = d['restrict_calls']
    obs['phase_hashcons_hits']['LOCAL_AND'] = d['hashcons_hits']
    obs['local_AND_reachable_nodes'] = len(r29.reachable_nodes(dag, local_root))

    phase0 = r29.phase_counters(dag)
    low, _ = dag.restrict(local_root, int(var), False)
    d = r29.phase_delta(phase0, r29.phase_counters(dag))
    obs['phase_nodes_created']['RESTRICT_FALSE'] = d['nodes_created']
    obs['phase_restrict_calls']['RESTRICT_FALSE'] = d['restrict_calls']
    obs['phase_hashcons_hits']['RESTRICT_FALSE'] = d['hashcons_hits']
    low_nodes = r29.reachable_nodes(dag, low)
    obs['restrict_false_reachable_nodes'] = len(low_nodes)

    phase0 = r29.phase_counters(dag)
    high, _ = dag.restrict(local_root, int(var), True)
    d = r29.phase_delta(phase0, r29.phase_counters(dag))
    obs['phase_nodes_created']['RESTRICT_TRUE'] = d['nodes_created']
    obs['phase_restrict_calls']['RESTRICT_TRUE'] = d['restrict_calls']
    obs['phase_hashcons_hits']['RESTRICT_TRUE'] = d['hashcons_hits']
    high_nodes = r29.reachable_nodes(dag, high)
    obs['restrict_true_reachable_nodes'] = len(high_nodes)
    obs['restrict_branch_intersection_nodes'] = len(low_nodes & high_nodes)
    obs['restrict_branch_union_nodes'] = len(low_nodes | high_nodes)

    phase0 = r29.phase_counters(dag)
    quantified_root = dag.OR(low, high)
    d = r29.phase_delta(phase0, r29.phase_counters(dag))
    obs['phase_nodes_created']['EXISTENTIAL_OR'] = d['nodes_created']
    obs['phase_restrict_calls']['EXISTENTIAL_OR'] = d['restrict_calls']
    obs['phase_hashcons_hits']['EXISTENTIAL_OR'] = d['hashcons_hits']
    obs['existential_OR_reachable_nodes'] = len(r29.reachable_nodes(dag, quantified_root))

    factors = r27.normalize_factors(rest + (quantified_root,))
    pre_gc = len(dag.nodes)
    removed = r27.multi_root_gc(dag, factors)
    after_live = len(dag.nodes)
    remaining = sum(
        1 for v in order[step:]
        if any(dag.support[root] & (1 << (v - 1)) for root in factors)
    )
    return factors, {
        'step': step,
        'quantified_var': int(var),
        'factor_count_before': before_factors,
        'bucket_factor_count': len(bucket),
        'bucket_union_support_size': bucket_union.bit_count(),
        'factor_count_after': len(factors),
        'before_live_nodes': before_live,
        'pre_gc_live_nodes': pre_gc,
        'after_gc_live_nodes': after_live,
        'new_nodes_created_step': dag.budget.nodes_created_total - created0,
        'restrict_calls_step': dag.budget.restrict_calls - calls0,
        'hashcons_hits_step': dag.hashcons_hits - hits0,
        'gc_removed_nodes': removed,
        'remaining_internal_variables_with_support': remaining,
        'message_forensics': obs,
    }


def build_pre_restriction_state(frame, bridge):
    started = time.monotonic()
    budget = r18.Budget(deadline=started + r18.WALL_SECONDS)
    dag = r18.Dag(budget)
    factors = r27.compile_initial_factors(dag, frame)
    order = tuple(r18.elimination_order(frame, bridge))
    if len(order) != len(set(order)):
        raise AssertionError('R30_ORDER_DUPLICATE')
    trajectory = []
    for step, var in enumerate(order[:24], start=1):
        factors, row = replay_completed_step(dag, factors, order, step, var)
        trajectory.append(row)

    if len(trajectory) != 24:
        raise AssertionError('R30_PREHISTORY_LENGTH_MISMATCH')
    if canonical_sha(trajectory) != EXPECTED_R29_PREHISTORY_TRAJECTORY_SHA256:
        raise AssertionError('R30_R29_PREHISTORY_TRAJECTORY_SHA_MISMATCH')

    step = FATAL_STEP
    var = order[step - 1]
    if int(var) != FATAL_VAR:
        raise AssertionError('R30_FATAL_VAR_MISMATCH')
    before_live = len(dag.nodes)
    bit = 1 << (int(var) - 1)
    bucket = tuple(root for root in factors if dag.support[root] & bit)
    rest = tuple(root for root in factors if not (dag.support[root] & bit))
    bucket_obs = r29.bucket_measurement(dag, bucket)
    phase0 = r29.phase_counters(dag)
    local_root = bucket[0] if len(bucket) == 1 else dag.AND(*bucket)
    local_delta = r29.phase_delta(phase0, r29.phase_counters(dag))
    local_nodes = r29.reachable_nodes(dag, local_root)
    pre_nodes = set(dag.nodes)
    state = {
        'dag': dag,
        'local_root': local_root,
        'pre_nodes': pre_nodes,
        'local_nodes': local_nodes,
        'order': order,
        'trajectory': trajectory,
        'prehistory_trajectory_sha256': canonical_sha(trajectory),
        'pre_restriction_DAG_fingerprint': dag_fingerprint(dag),
        'pre_restriction_live_nodes': len(dag.nodes),
        'pre_step_live_nodes_before_local_AND': before_live,
        'pre_restriction_local_root_reachable_nodes': len(local_nodes),
        'bucket_factor_count': len(bucket),
        'bucket_union_support_size': (sum((dag.support[root] for root in bucket), 0)).bit_count() if False else None,
        'bucket_measurement': bucket_obs,
        'local_AND_nodes_created': local_delta['nodes_created'],
        'rest_factor_count': len(rest),
        'elapsed_to_pre_restriction_seconds': time.monotonic() - started,
    }
    union_mask = 0
    for root in bucket:
        union_mask |= dag.support[root]
    state['bucket_union_support_size'] = union_mask.bit_count()
    return state


def run_isolated_branch(frame, bridge, value: bool):
    state = build_pre_restriction_state(frame, bridge)
    dag = state['dag']
    root = state['local_root']
    pre_nodes = state['pre_nodes']
    local_nodes = state['local_nodes']
    start_counters = r29.phase_counters(dag)
    started = time.monotonic()
    terminal = 'UNKNOWN_RESOURCE_LIMIT'
    reason = None
    output_root = None
    output_nodes = None
    try:
        output_root, _ = dag.restrict(root, FATAL_VAR, bool(value))
        output_nodes = r29.reachable_nodes(dag, output_root)
        terminal = 'COMPLETE'
    except r18.ResourceLimit as exc:
        reason = exc.reason
        terminal = 'RESOURCE_OPEN'
    elapsed = time.monotonic() - started
    delta = r29.phase_delta(start_counters, r29.phase_counters(dag))
    row = {
        'branch_value': bool(value),
        'prehistory_trajectory_sha256': state['prehistory_trajectory_sha256'],
        'pre_restriction_DAG_fingerprint': state['pre_restriction_DAG_fingerprint'],
        'pre_step_live_nodes_before_local_AND': state['pre_step_live_nodes_before_local_AND'],
        'pre_restriction_live_nodes': state['pre_restriction_live_nodes'],
        'pre_restriction_local_root_reachable_nodes': state['pre_restriction_local_root_reachable_nodes'],
        'bucket_factor_count': state['bucket_factor_count'],
        'bucket_union_support_size': state['bucket_union_support_size'],
        'bucket_measurement': state['bucket_measurement'],
        'local_AND_nodes_created': state['local_AND_nodes_created'],
        'branch_terminal_or_resource_open': terminal,
        'resource_reason': reason,
        'branch_output_reachable_nodes_if_terminal': len(output_nodes) if output_nodes is not None else None,
        'nodes_created_by_branch': delta['nodes_created'],
        'restrict_calls_by_branch': delta['restrict_calls'],
        'hashcons_hits_by_branch': delta['hashcons_hits'],
        'output_nodes_reused_from_pre_restriction_DAG': len(output_nodes & pre_nodes) if output_nodes is not None else None,
        'output_nodes_new_relative_to_pre_restriction_DAG': len(output_nodes - pre_nodes) if output_nodes is not None else None,
        'output_to_input_reachable_overlap': len(output_nodes & local_nodes) if output_nodes is not None else None,
        'phase_wall_seconds': elapsed,
        'live_nodes_after_branch_or_open': len(dag.nodes),
        'node_cap': r18.MAX_NODES,
    }
    return row


def observer_firewall():
    funcs = (canonical_sha, dag_fingerprint, replay_completed_step, build_pre_restriction_state, run_isolated_branch)
    src = '\n'.join(inspect.getsource(f) for f in funcs)
    forbidden = [
        'Solver(', '.solve(', 'independent_original_allowed', 'factor_set_allowed',
        'allowed_masks', 'truth_table', 'range(1 <<', 'dpll(', 'resolve_on(',
        'dag.OR(low, high)',
    ]
    hits = [token for token in forbidden if token in src]
    # replay_completed_step legitimately replays old frozen OR in steps 1..24;
    # R30's isolated step 25 itself never invokes OR.  The explicit source token
    # below is therefore allowed only inside replay_completed_step.
    hits = [h for h in hits if h != 'dag.OR(low, high)']
    step25_src = inspect.getsource(run_isolated_branch) + inspect.getsource(build_pre_restriction_state)
    step25_or_hit = '.OR(' in step25_src
    return {'pass': not hits and not step25_or_hit, 'forbidden_hits': hits, 'isolated_step_OR_present': step25_or_hit}


def equivalence_gates(false_row, true_row, prereg):
    expected = prereg['R29_observation_to_explain']
    frozen = prereg['frozen_inputs']
    checks = {
        'false_prehistory_sha': false_row['prehistory_trajectory_sha256'] == EXPECTED_R29_PREHISTORY_TRAJECTORY_SHA256,
        'true_prehistory_sha': true_row['prehistory_trajectory_sha256'] == EXPECTED_R29_PREHISTORY_TRAJECTORY_SHA256,
        'independent_pre_DAG_fingerprints_equal': false_row['pre_restriction_DAG_fingerprint'] == true_row['pre_restriction_DAG_fingerprint'],
        'false_pre_step_live': false_row['pre_step_live_nodes_before_local_AND'] == frozen['pre_step_live_nodes'],
        'true_pre_step_live': true_row['pre_step_live_nodes_before_local_AND'] == frozen['pre_step_live_nodes'],
        'false_local_root_reachable': false_row['pre_restriction_local_root_reachable_nodes'] == frozen['local_AND_reachable_nodes'],
        'true_local_root_reachable': true_row['pre_restriction_local_root_reachable_nodes'] == frozen['local_AND_reachable_nodes'],
        'false_bucket_sizes': false_row['bucket_measurement']['bucket_factor_reachable_node_sizes'] == expected['bucket_factor_reachable_node_sizes'],
        'true_bucket_sizes': true_row['bucket_measurement']['bucket_factor_reachable_node_sizes'] == expected['bucket_factor_reachable_node_sizes'],
        'false_bucket_intersection': false_row['bucket_measurement']['bucket_pairwise_intersection_for_two_factor_bucket'] == expected['bucket_pairwise_intersection_nodes'],
        'true_bucket_intersection': true_row['bucket_measurement']['bucket_pairwise_intersection_for_two_factor_bucket'] == expected['bucket_pairwise_intersection_nodes'],
        'false_terminal_complete': false_row['branch_terminal_or_resource_open'] == 'COMPLETE',
        'false_output_reachable': false_row['branch_output_reachable_nodes_if_terminal'] == expected['restrict_false_reachable_nodes'],
        'false_nodes_created': false_row['nodes_created_by_branch'] == expected['restrict_false_nodes_created'],
    }
    return {'pass': all(checks.values()), 'checks': checks}


def classify(eq, true_row):
    if not eq['pass']:
        return 'OBSERVER_EQUIVALENCE_FAIL', None
    if true_row['branch_terminal_or_resource_open'] == 'COMPLETE':
        return 'SEQUENTIAL_ACCUMULATION_DOMINANT', 'BOTH_ISOLATED_BRANCHES_COMPLETE__COMBINATION_UNMEASURED'
    if true_row['branch_terminal_or_resource_open'] == 'RESOURCE_OPEN':
        if true_row['resource_reason'] == 'NODE_CAP':
            return 'TRUE_BRANCH_INTRINSIC_RESOURCE_WALL', None
        return 'UNKNOWN_RESOURCE_LIMIT', None
    return 'UNKNOWN_RESOURCE_LIMIT', None


def run():
    prereg = load_prereg()
    freeze = r19.load_freeze()
    spec = next(w for w in freeze['worlds'] if w['id'] == WORLD_ID)
    if spec['frame_sha256'] != EXPECTED_FRAME_SHA:
        raise AssertionError('R30_FRAME_SHA_DRIFT')
    world = r19.generate_frozen_world(spec)
    firewall = observer_firewall()
    false_row = run_isolated_branch(tuple(world['frame']), tuple(world['bridge']), False)
    true_row = run_isolated_branch(tuple(world['frame']), tuple(world['bridge']), True)
    eq = equivalence_gates(false_row, true_row, prereg)
    primary, secondary = classify(eq, true_row) if firewall['pass'] else ('OBSERVER_EQUIVALENCE_FAIL', None)
    interpretation_allowed = bool(firewall['pass'] and eq['pass'])
    return {
        'schema': 'JANUS/TRUMP/R30/RESTRICTION_BRANCH_ISOLATION_FORENSICS/RESULT/v1.0',
        'created_date': '2026-09-02',
        'status': 'R30_EXECUTED',
        'scientific_role': 'COUNTERFACTUAL_BRANCH_ISOLATION__NO_BOOLEAN_CHANGE__NO_SEMANTIC_TRUTH',
        'world_id': WORLD_ID,
        'frame_sha256': EXPECTED_FRAME_SHA,
        'frozen_R27_blob': EXPECTED_R27_BLOB,
        'frozen_R18_blob': EXPECTED_R18_BLOB,
        'parent_R29_prehistory_trajectory_sha256': EXPECTED_R29_PREHISTORY_TRAJECTORY_SHA256,
        'observer_firewall': firewall,
        'equivalence_gates': eq,
        'isolated_false': false_row,
        'isolated_true': true_row,
        'result_class': primary,
        'secondary_observation_class': secondary,
        'interpretation_allowed': interpretation_allowed,
        'truth_accessed': False,
        'semantic_verifier_ran': False,
        'final_OR_ran_in_isolated_step': False,
        'claim_ceiling': prereg['claim_ceiling'],
        'next_gate_rule': prereg['next_gate_rule'],
        'firewalls': prereg['firewalls'],
        'seal': 'THE_TWO_RESTRICTIONS_RECEIVED_SEPARATE_FRESH_MEMORY_HISTORIES__THE_OR_REMAINED_CLOSED',
        'P_VS_NP': 'OPEN',
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', required=True)
    args = ap.parse_args()
    out = run()
    Path(args.output).write_text(json.dumps(out, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps({
        'result_class': out['result_class'],
        'secondary_observation_class': out['secondary_observation_class'],
        'equivalence': out['equivalence_gates']['pass'],
        'false_terminal': out['isolated_false']['branch_terminal_or_resource_open'],
        'false_output_nodes': out['isolated_false']['branch_output_reachable_nodes_if_terminal'],
        'true_terminal': out['isolated_true']['branch_terminal_or_resource_open'],
        'true_reason': out['isolated_true']['resource_reason'],
        'true_output_nodes': out['isolated_true']['branch_output_reachable_nodes_if_terminal'],
        'true_nodes_created': out['isolated_true']['nodes_created_by_branch'],
        'P_VS_NP': out['P_VS_NP'],
    }, indent=2, sort_keys=True))
    return 2 if out['result_class'] == 'OBSERVER_EQUIVALENCE_FAIL' else 0


if __name__ == '__main__':
    raise SystemExit(main())
