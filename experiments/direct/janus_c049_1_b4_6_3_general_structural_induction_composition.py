from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

SCHEMA='janus.c049_1.general_structural_induction_composition_candidate.v1'
SPEC_GATE='C049.1_B4.6.3_GENERAL_STRUCTURAL_INDUCTION_COMPOSITION'
TERM='OPEN_TRAJECTORY_ENGINE_INCOMPLETE'

def cb(x): return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def dg(x): return hashlib.sha256(cb(x)).hexdigest()
def load(p): return json.loads(Path(p).read_text())
def save(x,p): Path(p).write_bytes(cb(x)+b'\n')
def req(x,m):
    if not x: raise AssertionError(m)

def audit_semantic(a):
    req(a.get('semantic_digest_scope')=='audit_payload','audit scope')
    req(dg(a.get('audit_payload'))==a.get('semantic_digest'),'audit semantic')
    return a['semantic_digest']

def build(a):
    s=load(a.spec)
    req(s['gate']==SPEC_GATE and s['version']=='1.0' and s['admission'] is False,'spec')
    audits=[load(p) for p in a.audits]
    req(len(audits)==7,'audit count')
    sem=[audit_semantic(x) for x in audits]
    receipts=s['local_semantic_receipts']
    req(list(receipts)==[f'O{i}' for i in range(1,8)],'receipt order')
    req(all(receipts[f'O{i}']['status'].startswith('ESTABLISHED') for i in range(1,8)),'receipt status')
    pub=s['published_source']; req(pub['source']=='arXiv:1507.02184v4' and pub['source_version_required']=='v4','source version')
    req(pub['dependency_status']=='PUBLISHED_LEMMA_2_7_AND_PROPOSITION_5_8_INDUCTION_BOUND_NOT_INDEPENDENTLY_REPROVED','source ceiling')
    t=s['local_trace_contract']; c=s['structural_induction_contract']; cp=c['caller_precondition_discharge']
    req(t['ordinary_join_path_domain']==[[1,0],[0,1]],'ordinary path')
    req(t['preorder_path_domain']==[[1,0],[0,1],[1,1]],'preorder path')
    req(t['required_boundary_definitions']=={'B_v':'SPAN(V_v) INTER SPAN(V_MINUS_V_v)','Bprime_v':'B_w1 PLUS B_w2'},'boundary definitions')
    req(cp['expand_child_i']=='SPAN(V_wi) INTER (B_w1 PLUS B_w2) = B_wi','expand premise')
    req(cp['join']=='(SPAN(V_w1) PLUS Bprime_v) INTER (SPAN(V_w2) PLUS Bprime_v) = Bprime_v','join premise')
    req(cp['shrink']=='B_v SUBSET Bprime_v','shrink premise')
    steps=[
      {'step':'LEAF','receipt':'O1','premise':'B_v SUBSET V_leaf','conclusion':'F_v = FS_k(V_v,B_v)'},
      {'step':'EXPAND_CHILDREN','receipt':'O2','premise_source':'JKO_LEMMA_2_7','premise':cp['expand_child_i'],'conclusion':'F_v_child_i_expanded = FS_k(V_wi,Bprime_v)'},
      {'step':'CORRECTED_HV_JOIN','receipt':'O3','premise_source':'JKO_LEMMA_2_7','premise':cp['join'],'ordinary_path_domain':[[1,0],[0,1]],'conclusion':'JOIN_SOURCE_FAMILY_REPRESENTS_FS_k(V_v,Bprime_v)_BEFORE_CAP_CLOSURE'},
      {'step':'WIDTH_CAP','receipt':'O5','premise':cp['width_filter'],'conclusion':'WIDTH_GT_K_SOURCES_MAY_BE_REMOVED_WITHOUT_LOSING_ANY_FS_k_TARGET'},
      {'step':'B2_LANGUAGE_CLOSURE','receipt':'O6','premise':cp['b2_language_preservation'],'conclusion':'Fprime_v = FS_k(V_v,Bprime_v)'},
      {'step':'SHRINK','receipt':'O4','premise_source':'JKO_LEMMA_2_7','premise':cp['shrink'],'conclusion':'F_v = FS_k(V_v,B_v)'},
      {'step':'ROOT','receipt':'O7','premise':'COMPLETE_ALGORITHM1_COMPATIBLE_TRACE_AND_F_root_EQUALS_FS_k(V,{0})','conclusion':'F_root_NONEMPTY_IFF_COMPLETE_LAYOUT_WIDTH_LE_K'}
    ]
    proof={
      'phase':'GENERAL_STRUCTURAL_INDUCTION_COMPOSITION',
      'status':'CANDIDATE_PENDING_ADMISSION',
      'published_dependency_status':pub['dependency_status'],
      'published_source':pub['source'],
      'audit_semantic_digests':{f'O{i+1}':sem[i] for i in range(7)},
      'receipt_proof_heads':{k:v['proof_head'] for k,v in receipts.items()},
      'composition_steps':steps,
      'lemma_2_7_caller_preconditions_discharge_candidate':True,
      'algorithm1_compatible_trace_full_set_identity_candidate':True,
      'root_full_set_identity_candidate':'FOR_ANY_COMPLETE_ALGORITHM1_COMPATIBLE_TRACE_F_root_EQUALS_FS_k(V,{0})',
      'terminal_biconditional_candidate_for_complete_trace':True,
      'actual_corrected_engine_complete_algorithm1_trace_established':False,
      'general_semantic_receipt_count':7,
      'strict_boundary':s['strict_boundary']
    }
    out={'schema':SCHEMA,'semantic_digest_scope':'proof_payload','proof_payload':proof}
    out['semantic_digest']=dg(proof); save(out,a.output); return out

def main():
    p=argparse.ArgumentParser(); p.add_argument('--spec',type=Path,required=True)
    for i in range(1,8): p.add_argument(f'--o{i}-audit',dest=f'o{i}_audit',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True); a=p.parse_args(); a.audits=[getattr(a,f'o{i}_audit') for i in range(1,8)]
    x=build(a); q=x['proof_payload']
    print('JANUS_GENERAL_STRUCTURAL_INDUCTION_COMPOSITION_BINDER = PASS')
    print('BOUND_GENERAL_SEMANTIC_RECEIPTS = 7/7')
    print('LEMMA_2_7_CALLER_PRECONDITIONS_DISCHARGE = PASS_AS_PUBLISHED_DEPENDENCY_CANDIDATE')
    print('ALGORITHM1_COMPATIBLE_TRACE_FULL_SET_IDENTITY = PASS_AS_DERIVED_CANDIDATE')
    print('ACTUAL_CORRECTED_ENGINE_COMPLETE_ALGORITHM1_TRACE_ESTABLISHED = FALSE')
    print('TERMINAL_COMPLETENESS_PROVED = FALSE')
    print('GLOBAL_ENGINE_NO_LAYOUT_AT_CAP = FORBIDDEN')
    print('P_VS_NP = OPEN')
if __name__=='__main__': main()
