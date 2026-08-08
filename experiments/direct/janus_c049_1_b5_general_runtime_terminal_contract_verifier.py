from __future__ import annotations
import argparse, copy, hashlib, json
from pathlib import Path

SCHEMA='janus.c049_1.b5.general_runtime_terminal_integration_spec.v1'

def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def gb(p):
    b=Path(p).read_bytes(); return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()

def verify(s,a):
    if s.get('schema')!=SCHEMA or s.get('version')!='1.0' or s.get('status')!='SPEC_ONLY_FROZEN_NO_GENERIC_CAPABILITY_PROMOTION': raise AssertionError('spec identity')
    auth=s['authority_inputs']
    if gb(a.frontier_receipt)!=auth['current_frontier']['receipt_git_blob']!='': raise AssertionError('frontier receipt blob')
    fr=load(a.frontier_receipt)['audit_payload']
    if fr['admission_review_id']!=auth['current_frontier']['review_id'] or fr['exact_proof_head']!=auth['current_frontier']['proof_head']: raise AssertionError('frontier authority')
    if fr['semantic_findings']['next_gate']!='C049.1_B5_GENERAL_RUNTIME_AND_TERMINAL_INTEGRATION_CONTRACT': raise AssertionError('frontier next gate')
    if fr['strict_boundary']['b5_complete'] is not False or fr['strict_boundary']['p_vs_np']!='OPEN': raise AssertionError('frontier ceiling')

    if gb(a.general_spec)!=auth['general_algorithm1_composition']['spec_git_blob']: raise AssertionError('general spec blob')
    g=load(a.general_spec)
    if g['local_trace_contract']['ordinary_join_path_domain']!=[[1,0],[0,1]]: raise AssertionError('ordinary H/V')
    if g['local_trace_contract']['preorder_path_domain']!=[[1,0],[0,1],[1,1]]: raise AssertionError('preorder domain')
    if g['structural_induction_contract']['root_conclusion']!='FOR_ANY_COMPLETE_ALGORITHM1_COMPATIBLE_TRACE: F_root = FS_k(V,{0})': raise AssertionError('general root theorem')
    if auth['general_algorithm1_composition']['review_id']!=4888039239: raise AssertionError('general review')

    if gb(a.b5_plan)!=auth['historical_b5_plan']['git_blob']: raise AssertionError('B5 plan blob')
    plan=Path(a.b5_plan).read_text(encoding='utf-8')
    for t in ('B5 — terminal integration with C047','replayable `FOUND_LAYOUT` and `NO_LAYOUT_AT_CAP`','exact C047 SAT/UNSAT composition'):
        if t not in plan: raise AssertionError('B5 plan semantics')

    if gb(a.phase_a_core)!=auth['phase_a_layout_core']['git_blob']: raise AssertionError('phase A core blob')
    core=Path(a.phase_a_core).read_text(encoding='utf-8')
    for t in ('def layout_data_from_spaces(','if sorted(order_positions) != list(range(len(spaces))):','ordered = [spaces[index] for index in order_positions]','boundary = intersection(prefix[index], suffix[index], dimension)'):
        if t not in core: raise AssertionError('Phase A layout semantics')

    if gb(a.phase_a_solver)!=auth['phase_a_c047_solver']['git_blob']: raise AssertionError('Phase A solver blob')
    solver=Path(a.phase_a_solver).read_text(encoding='utf-8')
    for t in ('def compile_order_probe(','if terminal == "NO_LAYOUT_AT_CAP":','OPEN_UNVERIFIED_NO_LAYOUT_TRANSCRIPT','if terminal != "FOUND_LAYOUT":','original_layout = layout_data_from_spaces(spaces, order_positions, dimension, meter)','trellis = compile_order_probe(','"reason": "FOUND_LAYOUT_VERIFIED_AND_C047_COMPILED"'):
        if t not in solver: raise AssertionError('Phase A C047 interface')

    if gb(a.b42)!=auth['b4_2_scaffold']['git_blob']: raise AssertionError('B4.2 blob')
    b42=Path(a.b42).read_text(encoding='utf-8')
    for t in ('def scaffold(blocks,old_order,new,d,k,betas=None):','if max(old_w,default=0)>k: raise ValueError','if len(blocks[new])>2*k:','\'affine_offsets\':list(betas','\'scaffold_width_at_most_3k\':maxw<=3*k'):
        if t not in b42: raise AssertionError('B4.2 round lemma')

    inp=s['input_contract']
    if inp['field']!='GF(2)' or inp['factor_split']!='FORBIDDEN' or inp['factor_omission']!='FORBIDDEN' or inp['factor_duplication']!='FORBIDDEN': raise AssertionError('input partition')
    if inp['ambient_dimension']!='ARBITRARY_FINITE_NONNEGATIVE_INTEGER' or not inp['requested_k'].startswith('ARBITRARY_FINITE_NONNEGATIVE_INTEGER'): raise AssertionError('generic dimensions')
    if inp['affine_offset_identity']!='MUST_SURVIVE_PREPROCESSING_DISCOVERY_RECONSTRUCTION_AND_C047_HANDOFF': raise AssertionError('affine identity')
    if inp['capability_refusal']!='OPEN_ONLY_NEVER_COERCED_TO_FOUND_OR_NO_LAYOUT': raise AssertionError('refusal policy')

    rt=s['runtime_trace_contract']
    if rt['leaf_coverage']!='EXACTLY_ONE_ATOMIC_WHOLE_FACTOR_UNIT_PER_LEAF': raise AssertionError('leaf coverage')
    if rt['ordinary_join_domain']!='H_V_ONLY' or rt['extension_preorder_domain']!='H_V_DIAGONAL': raise AssertionError('path domains')
    if rt['root_boundary']!='ZERO': raise AssertionError('root boundary')
    required_node={'node_id','child_ids_or_leaf_factor_id','covered_factor_ids','B_v_rref','Bprime_v_rref_if_internal','caller_premise_certificates','input_full_set_digest_or_leaf_digest','complete_refinement_inventory_or_exact_symbolic_equivalent','up_k_receipt','output_full_set_digest','charged_work','capability_status'}
    if set(rt['required_node_receipt'])!=required_node: raise AssertionError('node receipt')

    it=s['iterative_compression_contract']
    if 'NO_FIXED_NODE_COUNT_OR_FIXED_FACTOR_VALUES' not in it['round_full_set_obligation']: raise AssertionError('anti-fixture runtime')
    if 'DIMENSION_AT_MOST_2K' not in it['new_reduced_factor_dimension_obligation']: raise AssertionError('2k obligation')
    if 'WIDTH_AT_MOST_3K' not in it['scaffold_obligation']: raise AssertionError('3k obligation')
    if not it['round_failure'].startswith('CAPABILITY_OR_RESOURCE_EXHAUSTION_IS_OPEN'): raise AssertionError('round refusal')

    pos=s['positive_terminal_contract']; neg=s['negative_terminal_contract']; c47=s['c047_handoff_contract']
    if pos['generic_found_layout_enabled_before_separate_admission'] is not False: raise AssertionError('positive promotion')
    if neg['generic_no_layout_enabled_before_separate_admission'] is not False or neg['target_enumeration_forbidden_as_general_proof'] is not True: raise AssertionError('negative promotion')
    if c47['must_recompute_layout_before_c047'] is not True or c47['bare_no_layout_transcript_to_phase_a']!='FORBIDDEN': raise AssertionError('C047 handoff')

    sub=s['subgates']
    expected=[('C049.1_B5.1_GENERIC_CORRECTED_RUNTIME_TRACE_EXECUTOR','NEXT'),('C049.1_B5.2_GENERIC_POSITIVE_ROOT_ANCESTRY_RECONSTRUCTION','BLOCKED_ON_B5_1'),('C049.1_B5.3_GENERIC_EMPTY_ROOT_TERMINAL_COMPOSITION','BLOCKED_ON_B5_1'),('C049.1_B5.4_CORRECTED_DISCOVERY_TO_PHASE_A_C047_REBOUND','BLOCKED_ON_B5_2')]
    if [(x['id'],x['status']) for x in sub]!=expected: raise AssertionError('subgate order')

    r=s['resource_and_refusal_contract']
    if set(r['open_never_implies'])!={'FOUND_LAYOUT','NO_LAYOUT_AT_CAP','B5_COMPLETE'} or r['asymptotic_claim_before_generic_runtime_admission']!='FORBIDDEN': raise AssertionError('resource boundary')
    anti=s['anti_fixture_requirements']
    forbidden={'fixed_factor_count_6','fixed_ambient_dimension_3','fixed_k_1','fixed_blocks_2_4_6_3_5_1','historical_720_layout_count','historical_34968_root_refinement_count','historical_node6_node7_node8_node9_ids','fixed_positive_fixture_1_2_1'}
    if set(anti['forbidden_acceptance_oracles'])!=forbidden or anti['controls_are_not_general_proof'] is not True: raise AssertionError('anti fixture')

    b=s['strict_boundary']
    expected_boundary={'b5_contract_frozen':True,'b5_1_generic_runtime_trace_executor':False,'b5_2_generic_found_layout_reconstruction':False,'b5_3_generic_no_layout_terminal':False,'b5_4_corrected_discovery_to_c047_rebound':False,'generic_found_layout_enabled':False,'generic_no_layout_at_cap_enabled':False,'arbitrary_input_global_engine_theorem':False,'b5_complete':False,'global_formal_admission':'BLOCKED','next_gate':'C049.1_B5.1_GENERIC_CORRECTED_RUNTIME_TRACE_EXECUTOR','p_vs_np':'OPEN'}
    if b!=expected_boundary: raise AssertionError('strict boundary')
    if len(s['tamper_attack_classes'])!=16: raise AssertionError('tamper catalog')

def attacks(base,a):
    out=[]
    def add(name,fn): y=copy.deepcopy(base); fn(y); out.append((name,y))
    add('T01_GENERIC_FROM_FROZEN',lambda x:x['strict_boundary'].__setitem__('b5_1_generic_runtime_trace_executor',True))
    add('T02_FACTOR_SPLIT',lambda x:x['input_contract'].__setitem__('factor_split','ALLOWED'))
    add('T03_AFFINE_ERASE',lambda x:x['input_contract'].__setitem__('affine_offset_identity','NOT_REQUIRED'))
    add('T04_DIAGONAL_JOIN',lambda x:x['runtime_trace_contract'].__setitem__('ordinary_join_domain','H_V_DIAGONAL'))
    add('T05_INCOMPLETE_SOURCE',lambda x:x['runtime_trace_contract']['required_node_receipt'].remove('complete_refinement_inventory_or_exact_symbolic_equivalent'))
    add('T06_OPEN_TO_NO',lambda x:x['resource_and_refusal_contract']['open_never_implies'].remove('NO_LAYOUT_AT_CAP'))
    add('T07_OPEN_TO_FOUND',lambda x:x['resource_and_refusal_contract']['open_never_implies'].remove('FOUND_LAYOUT'))
    add('T08_FIXTURE_TO_FOUND',lambda x:x['positive_terminal_contract'].__setitem__('generic_found_layout_enabled_before_separate_admission',True))
    add('T09_SKIP_LAYOUT_REPLAY',lambda x:x['c047_handoff_contract'].__setitem__('must_recompute_layout_before_c047',False))
    add('T10_BARE_NO_TO_C047',lambda x:x['c047_handoff_contract'].__setitem__('bare_no_layout_transcript_to_phase_a','ALLOWED'))
    add('T11_REMOVE_FIXED_ORACLE_GUARD',lambda x:x['anti_fixture_requirements']['forbidden_acceptance_oracles'].remove('fixed_factor_count_6'))
    add('T12_GENERIC_NEGATIVE',lambda x:x['strict_boundary'].__setitem__('generic_no_layout_at_cap_enabled',True))
    add('T13_GENERIC_POSITIVE',lambda x:x['strict_boundary'].__setitem__('generic_found_layout_enabled',True))
    add('T14_C047_REBOUND',lambda x:x['strict_boundary'].__setitem__('b5_4_corrected_discovery_to_c047_rebound',True))
    add('T15_B5_COMPLETE',lambda x:x['strict_boundary'].__setitem__('b5_complete',True))
    add('T16_PVNP',lambda x:x['strict_boundary'].__setitem__('p_vs_np','CLOSED'))
    rejected=0
    for name,y in out:
        try: verify(y,a)
        except Exception: rejected+=1; continue
        raise AssertionError(name+' survived')
    return rejected,len(out)

def main():
    p=argparse.ArgumentParser()
    for n in ('spec','frontier-receipt','general-spec','b5-plan','phase-a-core','phase-a-solver','b42'):
        p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--tamper-suite',action='store_true'); a=p.parse_args()
    s=load(a.spec); verify(s,a)
    print('JANUS_B5_GENERAL_RUNTIME_TERMINAL_CONTRACT_INDEPENDENT_VERIFIER = PASS')
    print('CONTRACT_INVARIANTS = 16/16')
    print('B5_SUBGATES = 4/4')
    print('NEXT_GATE = C049.1_B5.1_GENERIC_CORRECTED_RUNTIME_TRACE_EXECUTOR')
    print('PHASE_A_C047_EXISTING_INTERFACE = BOUND')
    print('CORRECTED_GENERIC_C047_HANDOFF = NOT_ADMITTED')
    print('GENERIC_FOUND_LAYOUT_ENABLED = FALSE')
    print('GENERIC_NO_LAYOUT_AT_CAP_ENABLED = FALSE')
    print('B5_COMPLETE = FALSE')
    print('P_VS_NP = OPEN')
    if a.tamper_suite:
        r,t=attacks(s,a); print(f'SEMANTIC_TAMPERS_REJECTED = {r}/{t}')
if __name__=='__main__': main()
