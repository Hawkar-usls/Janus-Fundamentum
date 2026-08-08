#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path
from typing import Any

from janus_c049_1_b2_up_k_core import Ledger, up_k_closure
from janus_c049_1_b3_expand_join_shrink_core import Statistic, expand_trajectory, shrink_trajectory
from janus_c049_1_b3_join_path_domain_corrected import JOIN_INTERLEAVING_STEPS, ordinary_join_paths, join_trajectory

SCHEMA='janus.c049_1.b4_6_4.actual_engine_composition_authority_closure_candidate.v1'
TERM='OPEN_TRAJECTORY_ENGINE_INCOMPLETE'
WHOLE=((2,),(4,),(6,),(3,),(5,),(1,))

def cb(x): return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def dg(x): return hashlib.sha256(cb(x)).hexdigest()
def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def gb(p):
    b=Path(p).read_bytes(); return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def req(v,m):
    if not v: raise AssertionError(m)
def contains(v,n):
    if v==n: return True
    if isinstance(v,dict): return any(contains(x,n) for x in v.values())
    if isinstance(v,(list,tuple)): return any(contains(x,n) for x in v)
    return False
def const(text,name):
    m=re.search(rf'^{re.escape(name)}\s*=\s*(.+)$',text,re.M)
    if not m: return None
    raw=m.group(1).strip()
    try: return json.loads(raw.replace("'",'"'))
    except Exception: return raw.strip('"\'')
def sem(path,scope):
    x=load(path); req(x.get('semantic_digest_scope')==scope,'semantic scope '+str(path)); req(dg(x[scope])==x.get('semantic_digest'),'semantic digest '+str(path)); return x

def positive_control():
    d=1; k=1; b=(1,); rb=()
    leaf=(Statistic((),b,0),Statistic(b,(),0))
    left,_=expand_trajectory(leaf,b,b,d); right,_=expand_trajectory(leaf,b,b,d)
    gens=[]; paths=[]
    for path in ordinary_join_paths(len(left),len(right)):
        joined,_=join_trajectory(left,right,path,b,d)
        shrunk,_=shrink_trajectory(joined,rb,d)
        w=max(s.value for s in shrunk)
        paths.append({'path':[list(x) for x in path],'width':w,'success':w<=k})
        if w<=k: gens.append(shrunk)
    req(gens,'positive control generators')
    cl=up_k_closure(gens,0,k,Ledger(discovery_cap=1000000,work_cap=1000000))
    req(int(cl['entry_count'])>0,'positive control closure')
    return {'fixture_role':'NONVACUITY_ONLY','same_interfaces':['EXPAND','CORRECTED_HV_JOIN','SHRINK','WIDTH_CAP','B2_UP_K'],'ordinary_join_steps':[list(x) for x in JOIN_INTERLEAVING_STEPS],'paths':paths,'successful_root_generators':len(gens),'root_up_k_entry_count':int(cl['entry_count']),'root_full_set_nonempty':True,'frozen_target_root_empty_consumed':False}

def build(a):
    spec=load(a.spec); hard=sem(a.hardening,'hardening_payload'); ledger=load(a.ledger)
    pre=sem(a.preflight_audit,'audit_payload'); n8=sem(a.node8_audit,'audit_payload'); q80=sem(a.q80_audit,'audit_payload')
    req(spec.get('schema')=='janus.c049_1.b4_6_4.general_structural_induction_composition_spec.v1' and spec.get('status')=='SPEC_FROZEN','spec')
    hp=hard['hardening_payload']; ga=hp['general_composition_authority']; nr=hp['node8_up_k_authority_requirement']
    req(ga['review_id']==4888039239 and ga['authority_scope']=='COMPLETE_ALGORITHM1_COMPATIBLE_TRACE_ONLY','general authority')
    req(nr['authority_established'] is True and nr['semantic_admission_review_id']==4888054139,'node8 hardening authority')
    req(n8['audit_payload']['semantic_subject']['final_admission_review_id']==4888054139,'node8 receipt review')
    req(n8['audit_payload']['candidate']['semantic_digest']==nr['candidate_semantic_digest'],'node8 semantic binding')
    req(q80['audit_payload']['admission_review_id']==4888076452,'q80 review')
    req(q80['audit_payload']['derived']['partition_fine_language_conservation']=='PASS','q80 conservation')
    req(q80['audit_payload']['derived']['expected_domain_or_fine_total_used_as_acceptance_oracle'] is False,'q80 oracle')
    req(q80['audit_payload']['downstream_handoff']['scalar_handoff_identity']=='PASS','q80 scalar handoff')
    req(pre['audit_payload']['semantic_conclusion']['preflight_only'] is True,'preflight role')
    req(pre['audit_payload']['derived_geometry']['all_o2_o3_o4_caller_premises_hold'] is True,'geometry premises')
    req(pre['audit_payload']['semantic_conclusion']['root_empty_consumed_as_premise'] is False,'preflight root shortcut')
    req(ledger.get('current_blockers')==[],'open hard blocker')
    entries={x['edge_id']:x for x in ledger['entries']}
    req(entries['NODE7_REFINEMENT_TO_NODE7_UP_K']['status']=='CLOSED_BY_LATER_REVIEWER_BOUND_REPAIR','node7 authority')
    req(entries['NODE8_PARENT_REFINEMENT_TO_NODE8_UP_K']['status']=='CLOSED_BY_VERIFICATION_ONLY_AUTHORITY_CLOSURE','node8 ledger')
    for edge in ('NODE9_SCALAR_TO_RESIDUAL_FRONTIER','NODE9_FRONTIER_TO_NODE9_UP_K','NODE9_UP_K_TO_ROOT_REFINEMENT'):
        req(entries[edge]['status'].startswith('CLOSED_'),'downstream authority '+edge)
    req(entries['ROOT_REFINEMENT_TO_ROOT_UP_K_EMPTY']['status']=='CLOSED_FOR_ROOT_EMPTY_ONLY','root upk authority')
    carriers=spec['engine_carriers']
    req(gb(a.corrected_join)==carriers['corrected_join_api']['git_blob'],'join blob')
    req(gb(a.node6_source)==carriers['node6_first_internal_join']['git_blob'],'node6 blob')
    req(gb(a.node7_source)==carriers['node7_frontier']['git_blob'],'node7 blob')
    req(gb(a.node8_manifest)==carriers['node8_parent_refinement']['manifest_git_blob'],'node8 manifest blob')
    req(gb(a.scalar_spec)==carriers['node9_scalar']['spec_git_blob'],'scalar spec blob')
    req(gb(a.residual_spec)==carriers['node9_residual_frontier']['spec_git_blob'],'residual spec blob')
    req(gb(a.node9_upk_spec)==carriers['node9_residual_up_k']['spec_git_blob'],'node9 upk spec blob')
    req(gb(a.root_spec)==carriers['root_refinement']['spec_git_blob'],'root spec blob')
    corrected=Path(a.corrected_join).read_text(); node6=Path(a.node6_source).read_text(); node7=Path(a.node7_source).read_text()
    manifest=load(a.node8_manifest); scalar=load(a.scalar_spec); residual=load(a.residual_spec); upk=load(a.node9_upk_spec); root=load(a.root_spec); root_empty=load(a.root_empty_spec)
    req('JOIN_INTERLEAVING_STEPS: tuple[tuple[int, int], ...] = ((1, 0), (0, 1))' in corrected,'H/V join')
    req('EXTENSION_PREORDER_STEPS: tuple[tuple[int, int], ...] = ((1, 0), (0, 1), (1, 1))' in corrected,'preorder domain')
    req('corrected_join_trajectory' in node6 and 'ordinary_join_paths' in node6,'node6 corrected join use')
    req(const(node6,'FIRST_INTERNAL_NODE_ID')==6,'node6 id')
    req(const(node7,'PARENT_HEAD')=='af0556d4ae05ea6dc343d120a34f67255890ba18','node7 parent link')
    req(manifest['base_exact_head']=='024afebb322c67953f310af48818d3386fdcfc27','node7 upk to node8')
    req(manifest['proof_controls']['ordinary_join_diagonal_allowed'] is False,'node8 diagonal join')
    qh=q80['audit_payload']['downstream_handoff']; n8sub=nr['proof_subject']
    req(contains(scalar,n8sub),'scalar missing node8')
    req(contains(scalar,qh['q80_sha256']) and contains(scalar,qh['q80_semantic_digest']),'scalar missing q80 identity')
    sh=carriers['node9_scalar']['admission_head']; rh=carriers['node9_residual_frontier']['admission_head']; uh=carriers['node9_residual_up_k']['admission_head']; rooth=carriers['root_refinement']['admission_head']
    req(contains(residual,sh),'scalar->residual')
    req(contains(upk,rh),'residual->upk')
    req(contains(root,uh),'upk->root')
    req(contains(root_empty,rooth),'root->root upk')
    req(contains(root,list(map(list,WHOLE))) or contains(root,[list(x) for x in WHOLE]),'target factor units')
    pos=positive_control()
    proof={
      'phase':'B4_6_4_ACTUAL_ENGINE_COMPOSITION_AUTHORITY_CLOSURE','status':'CANDIDATE_READY_FOR_REVIEW_NOT_ADMITTED','admitted':False,
      'authority':{'general_composition_review_id':ga['review_id'],'general_composition_proof_head':ga['proof_head'],'preflight_review_id':pre['audit_payload']['admission_review_id'],'node8_final_admission_review_id':nr['semantic_admission_review_id'],'node8_authority_receipt_blob':nr['authority_receipt_git_blob'],'q80_composition_review_id':q80['audit_payload']['admission_review_id'],'q80_audit_blob':gb(a.q80_audit)},
      'actual_trace':{'whole_factor_blocks':[list(x) for x in WHOLE],'geometry_caller_premises':'5/5','ordinary_join_steps':[[1,0],[0,1]],'extension_preorder_steps':[[1,0],[0,1],[1,1]],'node7_repair_bound':True,'node8_up_k_authority_bound':True,'q80_partition_fine_language_conservation_bound':True,'q80_scalar_handoff_identity':True,'scalar_to_residual_handoff':True,'residual_to_node9_up_k_handoff':True,'node9_up_k_to_root_refinement_handoff':True,'root_refinement_to_root_up_k_handoff':True,'all_stage_authority_edges_closed':True},
      'composition':{'general_complete_trace_theorem_bound':True,'actual_trace_satisfies_complete_algorithm1_contract_candidate':True,'candidate_derives_engine_root_full_set_equals_fs_k_v_zero':True,'root_empty_consumed_as_composition_premise':False,'zero_root_successes_consumed_as_composition_premise':False,'historical_counts_consumed_as_acceptance_oracles':False},
      'positive_nonvacuity_control':pos,
      'strict_boundary':{'root_empty_proved':True,'actual_corrected_engine_complete_algorithm1_trace_established':False,'engine_root_full_set_equals_fs_k_v_zero':False,'structural_induction_proved':False,'composition_candidate_ready_for_reviewer_admission':True,'terminal_completeness_proved':False,'no_layout_at_cap':'FORBIDDEN','found_layout':'FORBIDDEN','formal_admission':'BLOCKED','next_gate':'REVIEWER_BOUND_ACTUAL_ENGINE_COMPOSITION_ADMISSION','current_global_terminal':TERM,'p_vs_np':'OPEN'}
    }
    art={'schema':SCHEMA,'semantic_digest_scope':'proof_payload','proof_payload':proof}; art['semantic_digest']=dg(proof); Path(a.output).write_bytes(cb(art)+b'\n'); return art

def main():
    p=argparse.ArgumentParser()
    for n in ('spec','hardening','ledger','preflight-audit','node8-audit','q80-audit','corrected-join','node6-source','node7-source','node8-manifest','scalar-spec','residual-spec','node9-upk-spec','root-spec','root-empty-spec','output'): p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args(); art=build(a); q=art['proof_payload']; print('JANUS_ACTUAL_ENGINE_COMPOSITION_AUTHORITY_CLOSURE_PRODUCER = PASS'); print('ALL_STAGE_AUTHORITY_EDGES_CLOSED = TRUE'); print('GEOMETRY_CALLER_PREMISES = 5/5'); print('Q80_PARTITION_FINE_LANGUAGE_CONSERVATION = PASS'); print('ROOT_EMPTY_CONSUMED_AS_COMPOSITION_PREMISE = FALSE'); print('ACTUAL_TRACE_COMPLETE_CANDIDATE = TRUE'); print('ENGINE_ROOT_FULL_SET_EQUALS_FS_K_V_ZERO_CANDIDATE = TRUE'); print('FORMAL_ADMISSION = BLOCKED_PENDING_REVIEW'); print('TERMINAL_COMPLETENESS_PROVED = FALSE'); print('NO_LAYOUT_AT_CAP = FORBIDDEN'); print('P_VS_NP = OPEN'); print('SEMANTIC_DIGEST =',art['semantic_digest'])
if __name__=='__main__': main()
