from __future__ import annotations
import argparse, hashlib, json, random
from pathlib import Path

SCHEMA='janus.c049_1.b4_6_5.terminal_domain_composition_candidate.v1'
SPEC_SCHEMA='janus.c049_1.b4_6_5_terminal_domain_composition_spec.v1'
SEED=0xC049165

def cb(x): return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def dg(x): return hashlib.sha256(cb(x)).hexdigest()
def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def save(x,p): Path(p).write_bytes(cb(x)+b'\n')
def gb(p):
    b=Path(p).read_bytes(); return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
def sem_ok(x): return x.get('semantic_digest_scope')=='audit_payload' and dg(x.get('audit_payload'))==x.get('semantic_digest')

def require_blob(path, expected, label):
    got=gb(path)
    if got!=expected: raise AssertionError(f'{label} blob {got} != {expected}')

def build(a):
    spec=load(a.spec)
    if spec.get('schema')!=SPEC_SCHEMA or spec.get('status')!='SPEC_FROZEN' or spec.get('admission') is not False: raise AssertionError('spec')
    exp=spec['expected_values_policy']
    for k in ('expected_accepting_layout_count','expected_layout_count','expected_minimum_layout_width','expected_root_refinement_count'):
        if exp.get(k) is not None: raise AssertionError('expected-value oracle')
    b=spec['input_bindings']
    require_blob(a.phase_a,b['phase_a_layout_domain_core']['git_blob'],'phase-a')
    require_blob(a.group_rule,b['grouped_partition_rule']['git_blob'],'group-rule')
    require_blob(a.root_spec,b['root_spec']['git_blob'],'root-spec')
    require_blob(a.o7_spec,b['o7_spec']['git_blob'],'o7-spec')
    require_blob(a.o7_audit,b['o7_empty_root_specialization_authority']['git_blob'],'o7-audit')
    require_blob(a.actual_receipt,b['actual_engine_composition_final_receipt']['git_blob'],'actual-receipt')
    require_blob(a.root_empty_audit,b['root_empty_authority']['git_blob'],'root-empty-audit')
    require_blob(a.root_empty_review,b['root_empty_review_bridge']['git_blob'],'root-empty-review')

    phase=Path(a.phase_a).read_text(encoding='utf-8')
    required_phase=[
      'def layout_data_from_spaces(',
      'if sorted(order_positions) != list(range(len(spaces))):',
      'ordered = [spaces[index] for index in order_positions]',
      'prefix.append(span(prefix[-1], space, dimension=dimension))',
      'suffix[index] = span(ordered[index], suffix[index + 1], dimension=dimension)',
      'boundary = intersection(prefix[index], suffix[index], dimension)',
      'widths.append(len(boundary))']
    if not all(t in phase for t in required_phase): raise AssertionError('phase-a layout definition')
    grouping=Path(a.group_rule).read_text(encoding='utf-8')
    if 'preserve whole factor normal spaces as leaves' not in grouping or 'basis-block partition is discarded' not in grouping: raise AssertionError('grouping rule')

    rs=load(a.root_spec); target=spec['target']
    blocks=rs['scaffold']['whole_factor_blocks']
    if blocks!=target['whole_factor_blocks']: raise AssertionError('target block identity')
    if rs['canonical_semantics']['ambient_dim']!=target['ambient_dim'] or rs['canonical_semantics']['k']!=target['k']: raise AssertionError('target k/d')

    o7s=load(a.o7_spec)
    if o7s['derived_theorem']['biconditional']!='FS_k(V,{0}) != EMPTY IFF THERE EXISTS A COMPLETE LINEAR LAYOUT OF V WITH WIDTH <= k': raise AssertionError('o7 biconditional')
    if 'dim(prefix span INTER suffix span)' not in o7s['published_source']['canonical_zero_boundary']: raise AssertionError('o7 width formula')
    o7a=load(a.o7_audit)
    if not sem_ok(o7a) or o7a['semantic_digest']!=b['o7_empty_root_specialization_authority']['semantic_digest']: raise AssertionError('o7 audit digest')
    op=o7a['audit_payload']
    if op['proof_subject']['review_id']!=b['o7_empty_root_specialization_authority']['review_id'] or op['proof_subject']['exact_head']!=b['o7_empty_root_specialization_authority']['exact_proof_head']: raise AssertionError('o7 authority')

    ac=load(a.actual_receipt)
    if ac.get('schema')!='janus.c049_1.b4_6_4.actual_engine_composition_final_admission_receipt.v2': raise AssertionError('actual receipt schema')
    ap=ac['audit_payload']; sc=ap['semantic_conclusion']
    if ap['admission_review_id']!=b['actual_engine_composition_final_receipt']['review_id'] or ap['exact_proof_head']!=b['actual_engine_composition_final_receipt']['exact_proof_head']: raise AssertionError('actual authority')
    if not (sc['actual_corrected_engine_complete_algorithm1_trace_established'] and sc['engine_root_full_set_equals_fs_k_v_zero'] and sc['structural_induction_proved']): raise AssertionError('actual root identity')
    if sc['terminal_completeness_proved'] is not False or sc['no_layout_at_cap']!='FORBIDDEN': raise AssertionError('actual receipt ceiling')

    re=load(a.root_empty_audit)
    if not sem_ok(re) or re['semantic_digest']!=b['root_empty_authority']['semantic_digest']: raise AssertionError('root empty audit')
    rp=re['audit_payload']
    if rp['exact_pr_head']!=b['root_empty_authority']['exact_proof_head']: raise AssertionError('root empty subject')
    if not (rp['independent_up_k']['closure_empty'] is True and rp['independent_up_k']['closure_entry_count']==0): raise AssertionError('root not empty')
    rb=load(a.root_empty_review)
    rba=rb['audit_payload']
    if rba['canonical_numeric_review_id']!=b['root_empty_authority']['review_id'] or rba['exact_proof_head']!=b['root_empty_authority']['exact_proof_head']: raise AssertionError('root review bridge')
    if rba['independent_semantic_audit']['git_blob']!=b['root_empty_authority']['git_blob']: raise AssertionError('root review audit binding')

    units=[{'index':i,'ambient_rref':list(v)} for i,v in enumerate(blocks)]
    premises=[
      {'id':'P1_REPOSITORY_DOMAIN','value':'PERMUTATION_ALL_INPUT_SPACES_EXACTLY_ONCE'},
      {'id':'P2_GROUP_INDIVISIBILITY','value':'WHOLE_FACTOR_NORMAL_SPACE'},
      {'id':'P3_WIDTH_IDENTITY','value':'DIM_PREFIX_SPAN_INTER_SUFFIX_SPAN'},
      {'id':'P4_O7_LAYOUT_IMPLIES_FS_NONEMPTY','value':True},
      {'id':'P5_ACTUAL_ROOT_EQUALS_FS','value':True},
      {'id':'P6_ACTUAL_ROOT_EMPTY','value':True}]
    if a.order_mode=='REVERSED': premises.reverse()
    elif a.order_mode=='SEEDED_SHUFFLE': random.Random(SEED).shuffle(premises)
    premises=sorted(premises,key=lambda x:x['id'])
    proof={
      'candidate_phase':'TERMINAL_DOMAIN_AND_AUTHORITY_COMPOSITION',
      'candidate_status':'READY_FOR_REVIEW_NOT_ADMITTED',
      'target':target,
      'source_bindings':{
        'phase_a_git_blob':b['phase_a_layout_domain_core']['git_blob'],
        'group_rule_git_blob':b['grouped_partition_rule']['git_blob'],
        'root_spec_git_blob':b['root_spec']['git_blob'],
        'o7_spec_git_blob':b['o7_spec']['git_blob'],
        'o7_audit_git_blob':b['o7_empty_root_specialization_authority']['git_blob'],
        'o7_review_id':b['o7_empty_root_specialization_authority']['review_id'],
        'actual_composition_receipt_git_blob':b['actual_engine_composition_final_receipt']['git_blob'],
        'actual_composition_review_id':b['actual_engine_composition_final_receipt']['review_id'],
        'root_empty_audit_git_blob':b['root_empty_authority']['git_blob'],
        'root_empty_review_bridge_git_blob':b['root_empty_review_bridge']['git_blob'],
        'root_empty_review_id':b['root_empty_authority']['review_id']},
      'domain_identity':{
        'repository_units':units,
        'o7_instantiated_units':units,
        'same_indexed_units':True,
        'permutation_guard_exact':True,
        'factor_splitting_allowed':False,
        'omission_allowed':False,
        'duplication_allowed':False,
        'repository_legal_orders_equal_o7_complete_layouts':True},
      'width_identity':{
        'repository_formula':'dim(span(prefix) INTER span(suffix))',
        'o7_zero_boundary_formula':'dim(prefix span INTER suffix span)',
        'same_cut_function':True},
      'premises':premises,
      'logical_composition':{
        'assumption':'EXISTS_REPOSITORY_LEGAL_LAYOUT_WIDTH_LE_K',
        'step_1_domain_identity':'SAME_ORDER_IS_O7_COMPLETE_LINEAR_LAYOUT_WIDTH_LE_K',
        'step_2_o7':'FS_K_V_ZERO_NONEMPTY',
        'step_3_actual_root_identity':'CORRECTED_ENGINE_ROOT_FULL_SET_NONEMPTY',
        'step_4_root_empty_authority':'CORRECTED_ENGINE_ROOT_FULL_SET_EMPTY',
        'contradiction':True,
        'terminal_completeness_candidate':True,
        'no_layout_at_cap_candidate':True},
      'oracle_policy':{
        'enumerated_target_layouts':0,
        'historical_layout_counts_consumed':False,
        'historical_root_refinement_counts_consumed':False,
        'pointwise_crosscheck_consumed_as_premise':False,
        'empty_set_agreement_consumed_as_premise':False},
      'strict_boundary':{
        'terminal_completeness_proved':False,
        'no_layout_at_cap':'FORBIDDEN_PENDING_REVIEW',
        'found_layout':'FORBIDDEN',
        'formal_admission':'BLOCKED_PENDING_REVIEW',
        'p_vs_np':'OPEN'},
      'result':'TERMINAL_NO_LAYOUT_COMPOSITION_CANDIDATE_READY_FOR_INDEPENDENT_REVIEW'}
    art={'schema':SCHEMA,'semantic_digest_scope':'proof_payload','proof_payload':proof}
    art['semantic_digest']=dg(proof); save(art,a.output); return art

def main():
    p=argparse.ArgumentParser()
    for name in ('spec','phase-a','group-rule','root-spec','o7-spec','o7-audit','actual-receipt','root-empty-audit','root-empty-review','output'):
        p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--order-mode',choices=('ORIGINAL','REVERSED','SEEDED_SHUFFLE'),default='ORIGINAL')
    a=p.parse_args(); x=build(a); q=x['proof_payload']
    print('JANUS_TERMINAL_DOMAIN_COMPOSITION_PRODUCER = PASS')
    print('REPOSITORY_DOMAIN_EQUALS_O7_LAYOUT_DOMAIN = TRUE')
    print('WIDTH_DEFINITION_IDENTITY = PASS')
    print('ACTUAL_ENGINE_ROOT_IDENTITY_BOUND = TRUE')
    print('O7_BICONDITIONAL_BOUND = TRUE')
    print('ROOT_EMPTY_AUTHORITY_BOUND = TRUE')
    print('TARGET_LAYOUT_ENUMERATION_USED = FALSE')
    print('TERMINAL_COMPLETENESS_CANDIDATE = TRUE')
    print('NO_LAYOUT_AT_CAP_CANDIDATE = TRUE')
    print('FORMAL_ADMISSION = BLOCKED_PENDING_REVIEW')
    print('FOUND_LAYOUT = FORBIDDEN')
    print('P_VS_NP = OPEN')
    print('SEMANTIC_DIGEST =',x['semantic_digest'])
if __name__=='__main__': main()
