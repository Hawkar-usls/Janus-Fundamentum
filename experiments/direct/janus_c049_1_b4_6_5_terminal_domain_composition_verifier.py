from __future__ import annotations
import argparse, copy, hashlib, json
from pathlib import Path

SCHEMA='janus.c049_1.b4_6_5.terminal_domain_composition_candidate.v1'
SPEC_SCHEMA='janus.c049_1.b4_6_5_terminal_domain_composition_spec.v1'

def cb(x): return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def dg(x): return hashlib.sha256(cb(x)).hexdigest()
def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def gb(p):
    b=Path(p).read_bytes(); return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
def sem_ok(x): return x.get('semantic_digest_scope')=='audit_payload' and dg(x.get('audit_payload'))==x.get('semantic_digest')

def source_facts(a,spec):
    b=spec['input_bindings']; facts={}
    for attr,key in [('phase_a','phase_a_layout_domain_core'),('group_rule','grouped_partition_rule'),('root_spec','root_spec'),('o7_spec','o7_spec'),('o7_audit','o7_empty_root_specialization_authority'),('actual_receipt','actual_engine_composition_final_receipt'),('root_empty_audit','root_empty_authority'),('root_empty_review','root_empty_review_bridge')]:
        path=getattr(a,attr); facts[key+'_blob']=(gb(path)==b[key]['git_blob'])
    phase=Path(a.phase_a).read_text(encoding='utf-8')
    facts['phase_permutation_guard']='if sorted(order_positions) != list(range(len(spaces))):' in phase
    facts['phase_order_map']='ordered = [spaces[index] for index in order_positions]' in phase
    facts['phase_prefix']='prefix.append(span(prefix[-1], space, dimension=dimension))' in phase
    facts['phase_suffix']='suffix[index] = span(ordered[index], suffix[index + 1], dimension=dimension)' in phase
    facts['phase_intersection']='boundary = intersection(prefix[index], suffix[index], dimension)' in phase and 'widths.append(len(boundary))' in phase
    grouping=Path(a.group_rule).read_text(encoding='utf-8')
    facts['whole_factor_rule']='preserve whole factor normal spaces as leaves' in grouping
    facts['partition_loss_forbidden']='basis-block partition is discarded' in grouping
    rs=load(a.root_spec); facts['root_blocks']=rs['scaffold']['whole_factor_blocks']; facts['root_d']=rs['canonical_semantics']['ambient_dim']; facts['root_k']=rs['canonical_semantics']['k']
    o7s=load(a.o7_spec)
    facts['o7_biconditional']=o7s['derived_theorem']['biconditional']=='FS_k(V,{0}) != EMPTY IFF THERE EXISTS A COMPLETE LINEAR LAYOUT OF V WITH WIDTH <= k'
    facts['o7_zero_width']='dim(prefix span INTER suffix span)' in o7s['published_source']['canonical_zero_boundary']
    o7a=load(a.o7_audit); facts['o7_audit_sem']=sem_ok(o7a) and o7a['semantic_digest']==b['o7_empty_root_specialization_authority']['semantic_digest']
    if facts['o7_audit_sem']:
        op=o7a['audit_payload']['proof_subject']; facts['o7_review']=op['review_id']==b['o7_empty_root_specialization_authority']['review_id']; facts['o7_head']=op['exact_head']==b['o7_empty_root_specialization_authority']['exact_proof_head']
    else: facts['o7_review']=facts['o7_head']=False
    ac=load(a.actual_receipt); facts['actual_schema']=ac.get('schema')=='janus.c049_1.b4_6_4.actual_engine_composition_final_admission_receipt.v2'
    if facts['actual_schema']:
        ap=ac['audit_payload']; sc=ap['semantic_conclusion']; facts['actual_review']=ap['admission_review_id']==b['actual_engine_composition_final_receipt']['review_id']; facts['actual_head']=ap['exact_proof_head']==b['actual_engine_composition_final_receipt']['exact_proof_head']; facts['actual_root_identity']=bool(sc['actual_corrected_engine_complete_algorithm1_trace_established'] and sc['engine_root_full_set_equals_fs_k_v_zero'] and sc['structural_induction_proved']); facts['actual_ceiling']=sc['terminal_completeness_proved'] is False and sc['no_layout_at_cap']=='FORBIDDEN'
    else: facts['actual_review']=facts['actual_head']=facts['actual_root_identity']=facts['actual_ceiling']=False
    re=load(a.root_empty_audit); facts['root_empty_sem']=sem_ok(re) and re['semantic_digest']==b['root_empty_authority']['semantic_digest']
    if facts['root_empty_sem']:
        rp=re['audit_payload']; facts['root_empty_head']=rp['exact_pr_head']==b['root_empty_authority']['exact_proof_head']; facts['root_empty']=rp['independent_up_k']['closure_empty'] is True and rp['independent_up_k']['closure_entry_count']==0
    else: facts['root_empty_head']=facts['root_empty']=False
    rb=load(a.root_empty_review); rba=rb.get('audit_payload',{}); facts['root_review']=rba.get('canonical_numeric_review_id')==b['root_empty_authority']['review_id'] and rba.get('exact_proof_head')==b['root_empty_authority']['exact_proof_head'] and rba.get('independent_semantic_audit',{}).get('git_blob')==b['root_empty_authority']['git_blob']
    return facts

def verify_candidate(c,a,spec):
    if c.get('schema')!=SCHEMA or c.get('semantic_digest_scope')!='proof_payload' or dg(c.get('proof_payload'))!=c.get('semantic_digest'): raise AssertionError('candidate digest/schema')
    p=c['proof_payload']; target=spec['target']; facts=source_facts(a,spec)
    if not all(v for k,v in facts.items() if k.endswith('_blob')): raise AssertionError('immutable source blob')
    if not all(facts[k] for k in ('phase_permutation_guard','phase_order_map','phase_prefix','phase_suffix','phase_intersection')): raise AssertionError('phase-a semantics')
    if not facts['whole_factor_rule'] or not facts['partition_loss_forbidden']: raise AssertionError('whole-factor rule')
    if facts['root_blocks']!=target['whole_factor_blocks'] or facts['root_d']!=target['ambient_dim'] or facts['root_k']!=target['k']: raise AssertionError('target identity')
    if not (facts['o7_biconditional'] and facts['o7_zero_width'] and facts['o7_audit_sem'] and facts['o7_review'] and facts['o7_head']): raise AssertionError('o7 authority')
    if not (facts['actual_schema'] and facts['actual_review'] and facts['actual_head'] and facts['actual_root_identity'] and facts['actual_ceiling']): raise AssertionError('actual composition authority')
    if not (facts['root_empty_sem'] and facts['root_empty_head'] and facts['root_empty'] and facts['root_review']): raise AssertionError('root-empty authority')
    d=p['domain_identity']; expected_units=[{'index':i,'ambient_rref':list(v)} for i,v in enumerate(target['whole_factor_blocks'])]
    if d['repository_units']!=expected_units or d['o7_instantiated_units']!=expected_units or d['same_indexed_units'] is not True: raise AssertionError('unit catalog')
    if d['permutation_guard_exact'] is not True or d['factor_splitting_allowed'] is not False or d['omission_allowed'] is not False or d['duplication_allowed'] is not False or d['repository_legal_orders_equal_o7_complete_layouts'] is not True: raise AssertionError('domain identity')
    w=p['width_identity']
    if w['repository_formula']!='dim(span(prefix) INTER span(suffix))' or w['o7_zero_boundary_formula']!='dim(prefix span INTER suffix span)' or w['same_cut_function'] is not True: raise AssertionError('width identity')
    prem={x['id']:x['value'] for x in p['premises']}
    if prem!= {'P1_REPOSITORY_DOMAIN':'PERMUTATION_ALL_INPUT_SPACES_EXACTLY_ONCE','P2_GROUP_INDIVISIBILITY':'WHOLE_FACTOR_NORMAL_SPACE','P3_WIDTH_IDENTITY':'DIM_PREFIX_SPAN_INTER_SUFFIX_SPAN','P4_O7_LAYOUT_IMPLIES_FS_NONEMPTY':True,'P5_ACTUAL_ROOT_EQUALS_FS':True,'P6_ACTUAL_ROOT_EMPTY':True}: raise AssertionError('premise vector')
    l=p['logical_composition']
    if l['assumption']!='EXISTS_REPOSITORY_LEGAL_LAYOUT_WIDTH_LE_K' or l['step_1_domain_identity']!='SAME_ORDER_IS_O7_COMPLETE_LINEAR_LAYOUT_WIDTH_LE_K' or l['step_2_o7']!='FS_K_V_ZERO_NONEMPTY' or l['step_3_actual_root_identity']!='CORRECTED_ENGINE_ROOT_FULL_SET_NONEMPTY' or l['step_4_root_empty_authority']!='CORRECTED_ENGINE_ROOT_FULL_SET_EMPTY' or l['contradiction'] is not True or l['terminal_completeness_candidate'] is not True or l['no_layout_at_cap_candidate'] is not True: raise AssertionError('logical composition')
    o=p['oracle_policy']
    if o['enumerated_target_layouts']!=0 or o['historical_layout_counts_consumed'] is not False or o['historical_root_refinement_counts_consumed'] is not False or o['pointwise_crosscheck_consumed_as_premise'] is not False or o['empty_set_agreement_consumed_as_premise'] is not False: raise AssertionError('oracle shortcut')
    s=p['strict_boundary']
    if s!={'terminal_completeness_proved':False,'no_layout_at_cap':'FORBIDDEN_PENDING_REVIEW','found_layout':'FORBIDDEN','formal_admission':'BLOCKED_PENDING_REVIEW','p_vs_np':'OPEN'}: raise AssertionError('review ceiling')
    if p['result']!='TERMINAL_NO_LAYOUT_COMPOSITION_CANDIDATE_READY_FOR_INDEPENDENT_REVIEW': raise AssertionError('result')
    return facts

def repaired(x):
    y=copy.deepcopy(x); y['semantic_digest']=dg(y['proof_payload']); return y

def tamper_suite(base,a,spec):
    attacks=[]
    def add(name,fn):
        y=copy.deepcopy(base); fn(y['proof_payload']); attacks.append((name,repaired(y)))
    add('T01_PHASE_A_BINDING',lambda p:p['source_bindings'].__setitem__('phase_a_git_blob','0'*40))
    add('T02_PERMUTATION_GUARD',lambda p:p['domain_identity'].__setitem__('permutation_guard_exact',False))
    add('T03_FACTOR_SPLIT',lambda p:p['domain_identity'].__setitem__('factor_splitting_allowed',True))
    add('T04_TARGET_UNIT',lambda p:p['domain_identity']['repository_units'][0].__setitem__('ambient_rref',[2,1]))
    add('T05_WIDTH_FORMULA',lambda p:p['width_identity'].__setitem__('same_cut_function',False))
    add('T06_O7_REVIEW',lambda p:p['source_bindings'].__setitem__('o7_review_id',0))
    add('T07_O7_DIRECTION',lambda p:p['logical_composition'].__setitem__('step_2_o7','UNPROVED'))
    add('T08_ACTUAL_ROOT_IDENTITY',lambda p:p['premises'][4].__setitem__('value',False))
    add('T09_ROOT_EMPTY',lambda p:p['logical_composition'].__setitem__('step_4_root_empty_authority','UNKNOWN'))
    add('T10_HISTORICAL_COUNTS',lambda p:p['oracle_policy'].__setitem__('historical_layout_counts_consumed',True))
    add('T11_EMPTY_AGREEMENT',lambda p:p['oracle_policy'].__setitem__('empty_set_agreement_consumed_as_premise',True))
    add('T12_FOUND_LAYOUT',lambda p:p['strict_boundary'].__setitem__('found_layout','ALLOWED'))
    add('T13_PREMATURE_NO_LAYOUT',lambda p:p['strict_boundary'].__setitem__('no_layout_at_cap','TRUE'))
    add('T14_P_VS_NP',lambda p:p['strict_boundary'].__setitem__('p_vs_np','CLOSED'))
    rejected=0
    for name,c in attacks:
        try: verify_candidate(c,a,spec)
        except Exception: rejected+=1; continue
        raise AssertionError(name+' survived')
    return rejected,len(attacks)

def main():
    p=argparse.ArgumentParser()
    for name in ('spec','phase-a','group-rule','root-spec','o7-spec','o7-audit','actual-receipt','root-empty-audit','root-empty-review','candidate'):
        p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--tamper-suite',action='store_true'); a=p.parse_args()
    spec=load(a.spec)
    if spec.get('schema')!=SPEC_SCHEMA or spec.get('status')!='SPEC_FROZEN' or spec.get('admission') is not False: raise AssertionError('spec')
    c=load(a.candidate); facts=verify_candidate(c,a,spec)
    inv=[
      all(v for k,v in facts.items() if k.endswith('_blob')),
      all(facts[k] for k in ('phase_permutation_guard','phase_order_map','phase_prefix','phase_suffix','phase_intersection')),
      facts['whole_factor_rule'] and facts['partition_loss_forbidden'],
      facts['root_blocks']==spec['target']['whole_factor_blocks'],
      facts['o7_zero_width'],facts['o7_biconditional'] and facts['o7_audit_sem'] and facts['o7_review'],
      facts['actual_root_identity'] and facts['actual_review'],facts['root_empty'] and facts['root_review'],
      c['proof_payload']['domain_identity']['repository_legal_orders_equal_o7_complete_layouts'],
      c['proof_payload']['logical_composition']['contradiction'],
      not any((c['proof_payload']['oracle_policy']['historical_layout_counts_consumed'],c['proof_payload']['oracle_policy']['historical_root_refinement_counts_consumed'],c['proof_payload']['oracle_policy']['pointwise_crosscheck_consumed_as_premise'])),
      c['proof_payload']['strict_boundary']['no_layout_at_cap']=='FORBIDDEN_PENDING_REVIEW' and c['proof_payload']['strict_boundary']['p_vs_np']=='OPEN']
    if not all(inv): raise AssertionError('invariant vector')
    rejected=total=(0,0)
    if a.tamper_suite: rejected,total=tamper_suite(c,a,spec)
    print('JANUS_TERMINAL_DOMAIN_COMPOSITION_INDEPENDENT_VERIFIER = PASS')
    print('INVARIANTS = 12/12')
    if a.tamper_suite: print(f'DIGEST_REPAIRED_TAMPERS_REJECTED = {rejected}/{total}')
    print('REPOSITORY_DOMAIN_EQUALS_O7_LAYOUT_DOMAIN = TRUE')
    print('WIDTH_DEFINITION_IDENTITY = PASS')
    print('LOGICAL_CONTRADICTION_COMPOSITION = PASS')
    print('TARGET_LAYOUT_ENUMERATION_USED = FALSE')
    print('TERMINAL_COMPLETENESS_CANDIDATE = TRUE')
    print('NO_LAYOUT_AT_CAP_CANDIDATE = TRUE')
    print('FORMAL_ADMISSION = BLOCKED_PENDING_REVIEW')
    print('FOUND_LAYOUT = FORBIDDEN')
    print('P_VS_NP = OPEN')
if __name__=='__main__': main()
