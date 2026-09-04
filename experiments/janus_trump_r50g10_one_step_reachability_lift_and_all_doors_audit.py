from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r47j_normalization_fixpoint_restart_v25_gap as r47j
import janus_trump_r50a_exact_operational_token_tranception_controller as r50a
import janus_trump_r50g2_guarded_full_smallest_first_deadcore as r50g2
import janus_trump_r50g4_prefix_closure_microstep_authority as r50g4
import janus_trump_r50g8_wide_survivor_impossibility_from_pre_bve_cleanliness as r50g8
import janus_trump_r50g9_explicit_local_wide_fixpoint_counterexample as r50g9

GATE = "JANUS_TRUMP_R50G10_ONE_STEP_REACHABILITY_LIFT_AND_ALL_DOORS_AUDIT"
WIDTH_CAP = 4
PREDECESSOR_PIVOT = 1
DANGEROUS_PIVOT = 2
ROOT_POS_Y = (1, 2, -101)
ROOT_NEG_Y = (-1, -102, -103)
X_NEG_PARENT = (-2, -104, -107)
EXPECTED_REACHED_X_POS = (2, -101, -102, -103)
EXPECTED_WIDE = (-101, -102, -103, -104, -107)


def canon(f):
    return r33.canonical_formula(f)


def max_width(f):
    return max((len(c) for c in canon(f)), default=0)


def build_root_and_reached():
    core = r50g9.shift_formula(r50g9.even_prism_tseitin())
    root = canon(list(core) + [ROOT_POS_Y, ROOT_NEG_Y, X_NEG_PARENT])
    reached = canon(list(core) + [EXPECTED_REACHED_X_POS, X_NEG_PARENT])
    return core, root, reached


def exhaustive_existing_door_audit(formula):
    f = canon(formula)
    variables = tuple(int(v) for v in r33.variables(f))
    tokens = r50a.expose_exact_tokens(f)
    token_by_var = {int(t['var']): t for t in tokens}
    direct_pivots = sorted(int(v) for v, t in token_by_var.items() if t['direct_exact_dp_authorized'])

    fallback_rows = []
    safe_pivots = []
    for var in sorted(variables):
        row, candidate = r50a._fallback_candidate(f, int(var))
        replay_pass = True
        if candidate is not None:
            replay = r47j.independent_fixpoint_macro_replay(f, candidate)
            replay_pass = bool(replay['pass'])
            if not replay_pass:
                raise AssertionError(("R50G10_R47J_REPLAY_FAIL", var, replay))
        rr = dict(row)
        rr['independent_replay_pass'] = replay_pass
        fallback_rows.append(rr)
        if rr.get('width4_safe', False):
            safe_pivots.append(int(var))

    return {
        'variables_checked': list(sorted(variables)),
        'variable_count': len(variables),
        'R49H_direct_pivots': direct_pivots,
        'R47J_safe_pivots': safe_pivots,
        'R47J_rows': fallback_rows,
        'all_existing_doors_blocked': not direct_pivots and not safe_pivots,
    }


def run():
    core, root, reached = build_root_and_reached()

    if max_width(root) > 3:
        raise AssertionError(("R50G10_ROOT_NOT_W3", max_width(root)))
    if not r50g8.pre_bve_clean(root):
        raise AssertionError("R50G10_ROOT_NOT_PRE_BVE_CLEAN")

    direct_root = r50g4.first_r33_micro_candidate(root)
    if direct_root.get('rule') != 'BOUNDED_VARIABLE_ELIMINATION' or int(direct_root.get('var', -1)) != PREDECESSOR_PIVOT:
        raise AssertionError(("R50G10_ROOT_FIRST_RULE_NOT_Y_BVE", direct_root))
    if canon(direct_root['after']) != reached:
        raise AssertionError(("R50G10_Y_BVE_DOES_NOT_REACH_FROZEN_STATE", r50g4.fhash(direct_root['after']), r50g4.fhash(reached)))

    root_micro = r50g4.micro_r33_status(root)
    if root_micro['status'] != 'AUTHORIZED_R33_MICROSTEP' or max_width(root_micro['after']) != WIDTH_CAP:
        raise AssertionError(("R50G10_ROOT_MICROSTEP_NOT_AUTHORIZED_W4", root_micro))
    root_step = r50g4.refined_exact_step(root)
    if root_step['kind'] != 'NONTERMINAL' or root_step['lane'] != 'R33_EXACT_W4_MICROSTEP':
        raise AssertionError(("R50G10_U_MU_DID_NOT_AUTHORIZE_REACHABILITY_STEP", root_step))
    if canon(root_step['successor']) != reached:
        raise AssertionError("R50G10_U_MU_SUCCESSOR_MISMATCH")

    if not r50g8.pre_bve_clean(reached):
        raise AssertionError("R50G10_REACHED_STATE_NOT_PRE_BVE_CLEAN")
    reached_direct = r50g4.first_r33_micro_candidate(reached)
    if reached_direct.get('rule') != 'BOUNDED_VARIABLE_ELIMINATION' or int(reached_direct.get('var', -1)) != DANGEROUS_PIVOT:
        raise AssertionError(("R50G10_REACHED_FIRST_RULE_NOT_X_BVE", reached_direct))
    reached_micro = r50g4.micro_r33_status(reached)
    if reached_micro['status'] != 'IMMEDIATE_BVE_W4_ESCAPE':
        raise AssertionError(("R50G10_REACHED_NOT_IMMEDIATE_ESCAPE", reached_micro))
    if EXPECTED_WIDE not in canon(reached_direct['after']):
        raise AssertionError("R50G10_EXPECTED_WIDE_RESOLVENT_MISSING")

    inspection = r50g8.inspect_immediate_bve_state(reached)
    if not inspection['applicable'] or int(inspection['pivot']) != DANGEROUS_PIVOT:
        raise AssertionError(("R50G10_REACHED_INSPECTION_NOT_APPLICABLE", inspection))
    if inspection['same_pivot_safe']:
        raise AssertionError(("R50G10_REACHED_SAME_PIVOT_UNEXPECTEDLY_SAFE", inspection))
    if not inspection['final_nonterminal_wide'] or inspection['final_width'] <= WIDTH_CAP:
        raise AssertionError(("R50G10_REACHED_DID_NOT_REPRODUCE_WIDE_FIXPOINT", inspection))

    doors = exhaustive_existing_door_audit(reached)
    independent = r50g2.exact_guarded_open_test(reached)
    if not independent.get('applicable'):
        raise AssertionError(("R50G10_EXACT_GUARDED_AUDIT_NOT_APPLICABLE", independent))

    expected_open = bool(doors['all_existing_doors_blocked'])
    if bool(independent.get('open')) != expected_open:
        raise AssertionError(("R50G10_ALL_DOORS_AUDIT_DISAGREEMENT", doors, independent))

    refined_at_reached = r50g4.refined_exact_step(reached)
    refined_open = refined_at_reached['kind'] == 'OPEN_OBSTRUCTION'
    if refined_open != expected_open:
        raise AssertionError(("R50G10_U_MU_STEP_DISAGREES_WITH_ALL_DOORS_AUDIT", refined_at_reached, doors))

    explicit_model_root = {v: False for v in r33.variables(root)}
    explicit_model_reached = {v: False for v in r33.variables(reached)}
    if not r33.eval_formula(root, explicit_model_root):
        raise AssertionError("R50G10_ROOT_EXPLICIT_SAT_MODEL_FAIL")
    if not r33.eval_formula(reached, explicit_model_reached):
        raise AssertionError("R50G10_REACHED_EXPLICIT_SAT_MODEL_FAIL")

    if expected_open:
        verdict = "EXPLICIT_U_MU_REACHABLE_SAT_OPEN_STATE_FOUND__CURRENT_U_MU_UNIVERSAL_PROGRESS_REFUTED"
        u_mu = "REFUTED_BY_EXPLICIT_ONE_STEP_REACHABLE_SAT_OPEN"
        next_obligation = "CURRENT_U_MU_MACHINE_REQUIRES_A_NEW_EXACT_CERTIFIED_DOOR_OR_A_DIFFERENT_POLYNOMIAL_INVARIANT_DESCENT_MACHINE"
    else:
        verdict = "R50G9_BAD_SAME_PIVOT_STATE_IS_U_MU_REACHABLE_BUT_RESCUED_BY_EXISTING_CERTIFIED_DOOR__SAME_PIVOT_THEOREM_REFUTED__U_MU_REMAINS_OPEN"
        u_mu = "OPEN"
        next_obligation = "PROVE_OR_REFUTE_IMMEDIATE_BVE_ESCAPE_IMPLIES_EXISTS_EXISTING_R49H_OR_R47J_SAFE_DOOR_ON_THE_U_MU_REACHABLE_DOMAIN"

    return {
        'gate': GATE,
        'mode': 'EXACT_ONE_STEP_REACHABILITY_CERTIFICATE_PLUS_EXHAUSTIVE_EXISTING_DOOR_AUDIT',
        'reachability_certificate': {
            'root_hash': r50g4.fhash(root),
            'root_measure': list(r33.measure(root)),
            'root_width': max_width(root),
            'root_pre_bve_clean': True,
            'predecessor_pivot': PREDECESSOR_PIVOT,
            'root_positive_y_parent': list(ROOT_POS_Y),
            'root_negative_y_parent': list(ROOT_NEG_Y),
            'authorized_successor_hash': r50g4.fhash(reached),
            'authorized_successor_measure': list(r33.measure(reached)),
            'authorized_successor_width': max_width(reached),
            'u_mu_lane': root_step['lane'],
            'one_step_U_mu_reachability_proved': True,
            'explicit_root_sat_model_verified': True,
            'explicit_reached_sat_model_verified': True,
        },
        'reached_state': {
            'hash': r50g4.fhash(reached),
            'measure': list(r33.measure(reached)),
            'width': max_width(reached),
            'dangerous_pivot': DANGEROUS_PIVOT,
            'immediate_BVE_escape': True,
            'expected_width5_resolvent': list(EXPECTED_WIDE),
            'same_pivot_R47J_safe': False,
            'same_pivot_final_width': inspection['final_width'],
            'same_pivot_terminal': inspection['terminal'],
            'wide_fixpoint_certificate': inspection['wide_fixpoint_certificate'],
        },
        'all_existing_doors_audit': doors,
        'independent_guarded_open_test': independent,
        'refined_U_mu_step': {
            'kind': refined_at_reached['kind'],
            'lane': refined_at_reached['lane'],
        },
        'verdict': verdict,
        'critical_next_obligation': next_obligation,
        'firewall': {
            'HEURISTIC_AUTHORITY': False,
            'NEW_SEMANTIC_INFERENCE_RULE': False,
            'REACHABILITY_OF_R50G9_ISOMORPH': 'PROVED_BY_EXPLICIT_ONE_STEP_U_MU_TRACE',
            'REACHABLE_SAME_PIVOT_W4_SAFETY': 'REFUTED',
            'IMMEDIATE_BVE_CASE_ELIMINATED': False,
            'U_MU': u_mu,
            'SAT_IN_P': 'NOT_PROVED',
            'P_EQ_NP': 'NOT_PROVED',
            'P_NE_NP': 'NOT_PROVED',
            'P_VS_NP': 'OPEN',
            'TRUMP_finished': False,
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    out = run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, sort_keys=True, indent=2) + '\n')
    print(json.dumps(out, sort_keys=True))


if __name__ == '__main__':
    main()
