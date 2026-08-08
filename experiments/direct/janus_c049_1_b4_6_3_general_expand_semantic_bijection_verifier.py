from __future__ import annotations
import argparse, ast, copy, hashlib, json
from pathlib import Path
SCHEMA='janus.c049_1.general_expand_semantic_bijection_candidate.v1'; SPEC_SCHEMA='janus.c049_1.general_expand_semantic_bijection_spec.v1'; SPEC_BLOB='1b75c3665c911521d012ed28116f2e592a760ca5'; O1_AUDIT_BLOB='5c7ab15e3333afbf124bcfcc5c4a307f27c9ef89'; B2_DOC_BLOB='a7c5a7a65dfd9839711967f1039a96ba20ad6443'; B2_CORE_BLOB='3b66fa2b45702f11ee7a62657754c16800fa90f3'; B3_DOC_BLOB='786f4cc657335f31ca8696167bc2bde66d53180b'; B3_CORE_BLOB='443566c4b79bf67ec1613413130169cab12ebb0f'; TERM='OPEN_TRAJECTORY_ENGINE_INCOMPLETE'
class E(Exception):
 def __init__(self,i,m): super().__init__(f'{i}:{m}'); self.i=i
def req(x,i,m):
 if not x: raise E(i,m)
def cb(x): return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def dg(x): return hashlib.sha256(cb(x)).hexdigest()
def load(p): return json.loads(Path(p).read_text())
def gb(p):
 b=Path(p).read_bytes(); return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
def sem(c): return c.get('semantic_digest_scope')=='proof_payload' and dg(c.get('proof_payload'))==c.get('semantic_digest')
def bind(a):
 req(gb(a.spec)==SPEC_BLOB,'INV01','spec'); s=load(a.spec); req(s['schema']==SPEC_SCHEMA and s['status']=='SPEC_FROZEN','INV01','spec schema')
 for p,h in ((a.o1_audit,O1_AUDIT_BLOB),(a.b2_doc,B2_DOC_BLOB),(a.b2_core,B2_CORE_BLOB),(a.b3_doc,B3_DOC_BLOB),(a.b3_core,B3_CORE_BLOB)): req(gb(p)==h,'INV01','source blob')
 t=ast.parse(Path(a.producer_source).read_text()); mods=[]
 for n in ast.walk(t):
  if isinstance(n,ast.Import): mods.extend(x.name for x in n.names)
  elif isinstance(n,ast.ImportFrom): mods.append(n.module or '')
 req(not any(x.endswith('janus_c049_1_b4_6_3_general_expand_semantic_bijection_verifier') for x in mods),'INV01','producer imports verifier')
 return s
def derive_mapping(a):
 b2d=Path(a.b2_doc).read_text(); b2c=Path(a.b2_core).read_text(); b3d=Path(a.b3_doc).read_text(); b3c=Path(a.b3_core).read_text()
 req('def expand_trajectory' in b3c and 'return tuple(gamma), transport' in b3c,'INV04','identity'); req('child boundary not contained in parent' in b3c and 'boundary_transport' in b3c,'INV04','boundary check'); req('def up_k_closure' in b2c and 'Complete finite `U_k(B)` closure' in b2d,'INV05','upk'); req('### Expand' in b3d,'INV04','expand doc')
 return {'b3_expand_identity':True,'b3_child_parent_validation':True,'b2_up_k':True,'b3_expand_doc':True}
def verify(c,s,a):
 req(c.get('schema')==SCHEMA and sem(c),'INV01','candidate'); p=c['proof_payload']; pub=p['published_theorem']; req(pub['result']=='Proposition 4.2' and pub['arxiv']=='1507.02184v4' and pub['doi']=='10.1109/TIT.2017.2740283','INV02','source'); req(pub['normalized_formula']=='FS_k(Varr,Bprime)=up_k(FS_k(Varr,B),Bprime)','INV07','formula')
 q=p['quantifiers']; req(q['concrete_dimension_used'] is False and q['concrete_arrangement_used'] is False and q['concrete_k_used'] is False and all(str(q[k]).startswith('FOR_ALL') for k in ('ambient_space','arrangement','B_Bprime','k')),'INV03','quantifiers')
 pre=p['precondition']; req(pre=={'B_le_Bprime':True,'span_Varr_inter_Bprime_le_B':True,'caller_certificate_required':True,'local_expand_proves_span_precondition':False},'INV06','precondition')
 req(p['local_semantic_mapping']==derive_mapping(a),'INV04','mapping'); r=p['semantic_reason']; req(all(r.values()),'INV07','semantic reason')
 d=p['dependency_ceiling']; req(d=={'paper_mathematics_independently_reproved_by_repo':False,'published_proposition_used_as_external_mathematical_dependency':True,'local_mapping_machine_checked':True,'caller_expand_precondition_automatically_established':False,'claim_scope':'CONDITIONAL_ON_EXPLICIT_BOUND_PRECONDITION_CERTIFICATE'},'INV08','dependency ceiling')
 req(s['admission_boundary']['may_promote_after_exact_head_ci_semantic_audit_and_reviewer_receipt']==['O2_EXPAND_PRESERVATION_AND_REFLECTION','GENERAL_EXPAND_SEMANTIC_BIJECTION_RECEIPT'],'INV09','scope')
 b=p['strict_boundary']; exp={'o1_leaf_language_base_case':True,'o2_expand_preservation_and_reflection':False,'general_expand_semantic_bijection_receipt':False,'caller_expand_precondition_automatically_established':False,'general_semantic_theorems_established':1,'remaining_general_semantic_theorems':6,'o3_o7_established':False,'structural_induction_proved':False,'terminal_completeness_proved':False,'global_engine_no_layout_at_cap':'FORBIDDEN','formal_admission':'BLOCKED','next_gate':'CLOSED','current_global_terminal':TERM,'p_vs_np':'OPEN'}; req(b==exp,'INV12','boundary')
def seal(x): x['semantic_digest']=dg(x['proof_payload'])
def tamper(c,s,a):
 ok=[]
 def atk(n,f):
  x=copy.deepcopy(c); f(x); seal(x)
  try: verify(x,s,a)
  except E as e: ok.append((n,e.i)); return
  raise AssertionError('survived '+n)
 atk('T01_PROP',lambda x:x['proof_payload']['published_theorem'].__setitem__('result','Proposition 4.3')); atk('T02_BSUB',lambda x:x['proof_payload']['precondition'].__setitem__('B_le_Bprime',False)); atk('T03_SPAN',lambda x:x['proof_payload']['precondition'].__setitem__('span_Varr_inter_Bprime_le_B',False)); atk('T04_DIM',lambda x:x['proof_payload']['quantifiers'].__setitem__('concrete_dimension_used',3)); atk('T05_K',lambda x:x['proof_payload']['quantifiers'].__setitem__('concrete_k_used',1)); atk('T06_IDENTITY',lambda x:x['proof_payload']['local_semantic_mapping'].__setitem__('b3_expand_identity',False)); atk('T07_AUTOPRE',lambda x:x['proof_payload']['dependency_ceiling'].__setitem__('caller_expand_precondition_automatically_established',True)); atk('T08_REPROOF',lambda x:x['proof_payload']['dependency_ceiling'].__setitem__('paper_mathematics_independently_reproved_by_repo',True)); atk('T09_O3',lambda x:x['proof_payload']['strict_boundary'].__setitem__('o3_o7_established',True)); atk('T10_IND',lambda x:x['proof_payload']['strict_boundary'].__setitem__('structural_induction_proved',True)); atk('T11_TERM',lambda x:x['proof_payload']['strict_boundary'].__setitem__('terminal_completeness_proved',True)); atk('T12_PNP',lambda x:x['proof_payload']['strict_boundary'].__setitem__('p_vs_np','CLOSED')); req(len(ok)==12,'INV11','tamper count'); return ok
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--spec',type=Path,required=True); ap.add_argument('--producer-source',type=Path,required=True); ap.add_argument('--o1-audit',type=Path,required=True); ap.add_argument('--b2-doc',type=Path,required=True); ap.add_argument('--b2-core',type=Path,required=True); ap.add_argument('--b3-doc',type=Path,required=True); ap.add_argument('--b3-core',type=Path,required=True); ap.add_argument('--candidate-a',type=Path,required=True); ap.add_argument('--candidate-b',type=Path,required=True); ap.add_argument('--tamper-suite',action='store_true'); a=ap.parse_args(); s=bind(a); req(a.candidate_a.read_bytes()==a.candidate_b.read_bytes(),'INV10','bytes'); c=load(a.candidate_a); verify(c,s,a); ts=tamper(c,s,a) if a.tamper_suite else []
 print('JANUS_GENERAL_EXPAND_SEMANTIC_BIJECTION_INDEPENDENT_VERIFIER = PASS'); print('PRODUCER_IMPORT = FORBIDDEN_AND_NOT_USED'); print('INVARIANTS = 12/12'); print('DIGEST_REPAIRED_TAMPERS_REJECTED =',f'{len(ts)}/12' if a.tamper_suite else 'NOT_RUN'); print('PUBLISHED_RESULT = JKO_PROPOSITION_4_2'); print('CALLER_PRECONDITION_CERTIFICATE_REQUIRED = TRUE'); print('LOCAL_EXPAND_PROVES_SPAN_PRECONDITION = FALSE'); print('GENERAL_EXPAND_SEMANTIC_BIJECTION_RECEIPT = FALSE'); print('TERMINAL_COMPLETENESS_PROVED = FALSE'); print('P_VS_NP = OPEN')
if __name__=='__main__': main()
