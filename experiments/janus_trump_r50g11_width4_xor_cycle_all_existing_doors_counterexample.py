from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r34_affine_xor_terminal_against_tseitin_core as r34
import janus_trump_r47j_normalization_fixpoint_restart_v25_gap as r47j
import janus_trump_r50a_exact_operational_token_tranception_controller as r50a
import janus_trump_r50g4_prefix_closure_microstep_authority as r50g4
import janus_trump_r50g8_wide_survivor_impossibility_from_pre_bve_cleanliness as r50g8
import janus_trump_r50g10_one_step_reachability_lift_and_all_doors_audit as r50g10

GATE = "JANUS_TRUMP_R50G11_WIDTH4_XOR_CYCLE_ALL_EXISTING_DOORS_COUNTEREXAMPLE"
WIDTH_CAP = 4
PIVOT = 1
EQUATIONS = (
    (101, 102, 103, 104),
    (103, 104, 105, 106),
    (105, 106, 107, 108),
    (107, 108, 101, 102),
)
POS_PARENT = (1, -101, -103, -105)
NEG_PARENT = (-1, -107, -108)
EXPECTED_WIDE = (-101, -103, -105, -107, -108)


def canon(f):
    return r33.canonical_formula(f)


def max_width(f):
    return max((len(c) for c in canon(f)), default=0)


def build_core_and_source():
    clauses = []
    for variables in EQUATIONS:
        clauses.extend(r34.xor_bundle(tuple(variables), 0))
    core = canon(clauses)
    source = canon(list(core) + [POS_PARENT, NEG_PARENT])
    return core, source


def compact_tokens(formula):
    rows = []
    for token in r50a.expose_exact_tokens(formula):
        rows.append({
            'pivot': int(token['pivot']),
            'positive_parent_count': int(token['positive_parent_count']),
            'negative_parent_count': int(token['negative_parent_count']),
            'retained_nontautological_pair_count': int(token['retained_nontautological_pair_count']),
            'chi_star': int(token['chi_star']),
            'bipolar': bool(token['bipolar']),
            'direct_exact_dp_authorized': bool(token['direct_exact_dp_authorized']),
            'token_sha256': token['token_sha256'],
        })
    return rows


def run():
    core, source = build_core_and_source()

    affine = r34.recognize_complete_affine_cnf(core)
    core_affine = bool(affine['recognized'])
    core_sat = False
    core_affine_verify = False
    if core_affine:
        solution = r34.solve_gf2_with_certificate(affine['equations'])
        verify = r34.verify_affine_certificate(core, affine, solution)
        core_sat = bool(solution['sat'])
        core_affine_verify = bool(verify['pass'])
    if not (core_affine and core_sat and core_affine_verify):
        raise AssertionError(("R50G11_CORE_NOT_CERTIFIED_SAT_AFFINE", affine))

    explicit_model = {v: False for v in r33.variables(source)}
    source_sat_model = bool(r33.eval_formula(source, explicit_model))
    if not source_sat_model:
        raise AssertionError("R50G11_ALL_FALSE_SOURCE_MODEL_FAIL")

    source_width = max_width(source)
    preclean = bool(r50g8.pre_bve_clean(source)) if source_width <= WIDTH_CAP else False
    direct = r50g4.first_r33_micro_candidate(source) if source_width <= WIDTH_CAP else {'kind': 'OUTSIDE_W4'}
    immediate = False
    post_dp = None
    same_pivot = None
    if source_width <= WIDTH_CAP and preclean and direct.get('rule') == 'BOUNDED_VARIABLE_ELIMINATION' and int(direct.get('var', -1)) == PIVOT:
        micro = r50g4.micro_r33_status(source)
        immediate = micro['status'] == 'IMMEDIATE_BVE_W4_ESCAPE'
        if immediate:
            post_dp = canon(direct['after'])
            if EXPECTED_WIDE not in post_dp:
                raise AssertionError(("R50G11_EXPECTED_WIDE_RESOLVENT_MISSING", direct.get('resolvents')))
            same_pivot = r47j.macro_candidate_fixpoint(source, PIVOT)
            if same_pivot is None:
                raise AssertionError("R50G11_SAME_PIVOT_R47J_MISSING")
            replay = r47j.independent_fixpoint_macro_replay(source, same_pivot)
            if not replay['pass']:
                raise AssertionError(("R50G11_SAME_PIVOT_REPLAY_FAIL", replay))

    construction_valid = bool(source_width <= WIDTH_CAP and preclean and immediate)
    tokens = compact_tokens(source) if construction_valid else []
    doors = r50g10.exhaustive_existing_door_audit(source) if construction_valid else None
    refined = r50g4.refined_exact_step(source) if construction_valid else None

    if not construction_valid:
        verdict = "FROZEN_WIDTH4_XOR_CYCLE_CONSTRUCTION_INVALID_FOR_IMMEDIATE_BVE_TARGET"
        local_theorem = "OPEN"
        critical = "CONSTRUCTION_PRECONDITION_FAILED__DO_NOT_INFER_ANYTHING_ABOUT_EXISTING_DOOR_THEOREM"
    else:
        all_blocked = bool(doors['all_existing_doors_blocked'])
        refined_open = refined['kind'] == 'OPEN_OBSTRUCTION'
        if refined_open != all_blocked:
            raise AssertionError(("R50G11_EXHAUSTIVE_AUDIT_CONTROLLER_DISAGREEMENT", doors, refined))
        if all_blocked:
            verdict = "LOCAL_EXISTING_DOOR_THEOREM_REFUTED_BY_EXPLICIT_W4_SAT_OPEN_STATE__REACHABILITY_NOT_ESTABLISHED"
            local_theorem = "REFUTED_BY_EXPLICIT_W4_SAT_OPEN"
            critical = "PROVE_OR_REFUTE_U_MU_REACHABILITY_OF_R50G11_WITNESS_FROM_W3_INPUT_DOMAIN"
        else:
            verdict = "FROZEN_XOR_CYCLE_CANDIDATE_RESCUED_BY_EXISTING_CERTIFIED_DOOR__LOCAL_EXISTING_DOOR_THEOREM_REMAINS_OPEN"
            local_theorem = "OPEN"
            critical = "USE_EXACT_RESCUE_PROFILE_TO_STRENGTHEN_DOOR_BLOCKING_CONSTRUCTION_OR_PROVE_EXISTENTIAL_DOOR_THEOREM"

    same_pivot_summary = None
    if same_pivot is not None:
        final = canon(same_pivot['normalization']['final_formula'])
        same_pivot_summary = {
            'terminal': same_pivot['normalization']['terminal'],
            'final_hash': r50a.formula_hash(final),
            'final_CLV': list(r33.measure(final)),
            'final_width': max_width(final),
            'safe': bool(same_pivot['normalization']['terminal'] is not None or max_width(final) <= WIDTH_CAP),
            'independent_replay_pass': True,
        }

    return {
        'gate': GATE,
        'mode': 'EXACT_DETERMINISTIC_LOCAL_ALL_EXISTING_DOORS_THEOREM_ATTACK',
        'construction': {
            'equations': [list(x) for x in EQUATIONS],
            'core_CLV': list(r33.measure(core)),
            'core_max_width': max_width(core),
            'core_complete_affine_certified_sat': True,
            'source_hash': r50a.formula_hash(source),
            'source_CLV': list(r33.measure(source)),
            'source_max_width': source_width,
            'source_explicit_sat_model_verified': source_sat_model,
            'source_pre_bve_clean': preclean,
            'first_rule': direct.get('rule'),
            'first_rule_pivot': direct.get('var'),
            'immediate_BVE_escape': immediate,
            'expected_width5_resolvent': list(EXPECTED_WIDE),
            'post_DP_width': max_width(post_dp) if post_dp is not None else None,
            'construction_valid_for_target': construction_valid,
        },
        'same_pivot_R47J': same_pivot_summary,
        'R49H_tokens': tokens,
        'all_existing_doors_audit': doors,
        'refined_U_mu_step': None if refined is None else {'kind': refined['kind'], 'lane': refined['lane']},
        'verdict': verdict,
        'critical_next_obligation': critical,
        'firewall': {
            'HEURISTIC_AUTHORITY': False,
            'NEW_SEMANTIC_INFERENCE_RULE': False,
            'LOCAL_EXISTING_DOOR_THEOREM': local_theorem,
            'REACHABILITY_OF_R50G11_WITNESS': 'NOT_ESTABLISHED',
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
