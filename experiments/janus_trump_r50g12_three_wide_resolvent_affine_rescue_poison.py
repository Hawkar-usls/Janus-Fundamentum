from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r34_affine_xor_terminal_against_tseitin_core as r34
import janus_trump_r50a_exact_operational_token_tranception_controller as r50a
import janus_trump_r50g4_prefix_closure_microstep_authority as r50g4
import janus_trump_r50g8_wide_survivor_impossibility_from_pre_bve_cleanliness as r50g8
import janus_trump_r50g10_one_step_reachability_lift_and_all_doors_audit as r50g10
import janus_trump_r50g11_width4_xor_cycle_all_existing_doors_counterexample as r50g11

GATE = 'JANUS_TRUMP_R50G12_THREE_WIDE_RESOLVENT_AFFINE_RESCUE_POISON'
WIDTH_CAP = 4
PIVOT = 1
P1 = (1, -101, -102, -103)
P2 = (1, 104, -105, -106)
N1 = (-1, -107, -108)
N2 = (-1, -104, -105)
EXPECTED = {
    (-101, -102, -103, -107, -108),
    (-101, -102, -103, -104, -105),
    (104, -105, -106, -107, -108),
}


def canon(f):
    return r33.canonical_formula(f)


def max_width(f):
    return max((len(c) for c in canon(f)), default=0)


def build_source():
    core, _old = r50g11.build_core_and_source()
    return core, canon(list(core) + [P1, P2, N1, N2])


def run():
    core, source = build_source()
    all_false = {v: False for v in r33.variables(source)}
    if not r33.eval_formula(source, all_false):
        raise AssertionError('R50G12_EXPLICIT_SAT_MODEL_FAIL')

    source_width = max_width(source)
    preclean = source_width <= WIDTH_CAP and r50g8.pre_bve_clean(source)
    direct = r50g4.first_r33_micro_candidate(source) if source_width <= WIDTH_CAP else {'kind': 'OUTSIDE'}
    immediate = False
    resolvents = set()
    if preclean and direct.get('rule') == 'BOUNDED_VARIABLE_ELIMINATION' and int(direct.get('var', -1)) == PIVOT:
        resolvents = {tuple(c) for c in direct.get('resolvents', [])}
        immediate = r50g4.micro_r33_status(source)['status'] == 'IMMEDIATE_BVE_W4_ESCAPE'

    expected_exact = resolvents == EXPECTED
    intersection = None
    if expected_exact:
        sets = [set(abs(x) for x in c) for c in sorted(EXPECTED)]
        intersection = sorted(set.intersection(*sets))
    construction_valid = bool(source_width == 4 and preclean and immediate and expected_exact and intersection == [])

    tokens = []
    doors = None
    refined = None
    if construction_valid:
        for t in r50a.expose_exact_tokens(source):
            tokens.append({
                'pivot': int(t['pivot']),
                'chi_star': int(t['chi_star']),
                'positive_parent_count': int(t['positive_parent_count']),
                'negative_parent_count': int(t['negative_parent_count']),
                'retained_nontautological_pair_count': int(t['retained_nontautological_pair_count']),
                'direct_exact_dp_authorized': bool(t['direct_exact_dp_authorized']),
            })
        doors = r50g10.exhaustive_existing_door_audit(source)
        refined = r50g4.refined_exact_step(source)
        controller_open = refined['kind'] == 'OPEN_OBSTRUCTION'
        if controller_open != bool(doors['all_existing_doors_blocked']):
            raise AssertionError(('R50G12_AUDIT_CONTROLLER_DISAGREE', doors, refined))

    if not construction_valid:
        verdict = 'FROZEN_THREE_WIDE_RESOLVENT_CONSTRUCTION_INVALID_FOR_TARGET'
        local = 'OPEN'
        next_obligation = 'CONSTRUCTION_PRECONDITION_FAILED'
    elif doors['all_existing_doors_blocked']:
        verdict = 'LOCAL_EXISTING_DOOR_THEOREM_REFUTED_BY_EXPLICIT_THREE_WIDE_RESOLVENT_W4_SAT_OPEN_STATE__REACHABILITY_NOT_ESTABLISHED'
        local = 'REFUTED_BY_EXPLICIT_W4_SAT_OPEN'
        next_obligation = 'PROVE_OR_REFUTE_U_MU_REACHABILITY_OF_R50G12_WITNESS_FROM_W3_INPUT_DOMAIN'
    else:
        verdict = 'THREE_WIDE_RESOLVENT_AFFINE_RESCUE_POISON_INCOMPLETE__EXACT_RESCUE_PIVOTS_RECORDED'
        local = 'OPEN'
        next_obligation = 'USE_EXACT_RESCUE_PROFILE_TO_BLOCK_REMAINING_R47J_SAFE_PIVOTS_OR_PROVE_EXISTENTIAL_DOOR_THEOREM'

    return {
        'gate': GATE,
        'mode': 'EXACT_DETERMINISTIC_THREE_WIDE_RESOLVENT_ALL_DOORS_ATTACK',
        'construction': {
            'core_CLV': list(r33.measure(core)),
            'source_hash': r50a.formula_hash(source),
            'source_CLV': list(r33.measure(source)),
            'source_max_width': source_width,
            'source_pre_bve_clean': bool(preclean),
            'first_rule': direct.get('rule'),
            'first_rule_pivot': direct.get('var'),
            'immediate_BVE_escape': bool(immediate),
            'exact_unique_nontaut_resolvents': [list(c) for c in sorted(resolvents)],
            'expected_resolvents_exact': bool(expected_exact),
            'wide_variable_intersection': intersection,
            'construction_valid_for_target': construction_valid,
            'explicit_sat_model_verified': True,
        },
        'R49H_tokens': tokens,
        'all_existing_doors_audit': doors,
        'refined_U_mu_step': None if refined is None else {'kind': refined['kind'], 'lane': refined['lane']},
        'verdict': verdict,
        'critical_next_obligation': next_obligation,
        'firewall': {
            'HEURISTIC_AUTHORITY': False,
            'NEW_SEMANTIC_INFERENCE_RULE': False,
            'LOCAL_EXISTING_DOOR_THEOREM': local,
            'REACHABILITY_OF_R50G12_WITNESS': 'NOT_ESTABLISHED',
            'U_MU': 'OPEN',
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
