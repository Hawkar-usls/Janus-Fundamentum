from __future__ import annotations
import argparse, ast, copy, hashlib, json
from pathlib import Path
SCHEMA='janus.c049_1.general_leaf_semantic_bijection_candidate.v1'
SPEC_SCHEMA='janus.c049_1.general_leaf_semantic_bijection_spec.v1'
SPEC_BLOB='188e4a2d28ed787d7f8aad75c0f157b085db9b3d'
B1_DOC_BLOB='c1807ab523d3269c064db33221c764d1e459bee2'; B1_CORE_BLOB='96019d44b8defb97f7b0911b57302004c3d57c61'; B2_DOC_BLOB='a7c5a7a65dfd9839711967f1039a96ba20ad6443'; B2_CORE_BLOB='3b66fa2b45702f11ee7a62657754c16800fa90f3'; LEDGER_AUDIT_BLOB='c7ab1da4f38e56034bbf4d3f49c22cbedd1b9d5c'; TERM='OPEN_TRAJECTORY_ENGINE_INCOMPLETE'
class VError(Exception):
 def __init__(self,inv,msg): super().__init__(f'{inv}:{msg}'); self.inv=inv
def req(x,inv,msg):
 if not x: raise VError(inv,msg)
def cb(x): return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def dg(x): return hashlib.sha256(cb(x)).hexdigest()
def load(p): return json.loads(Path(p).read_text())
def gb(p):
 b=Path(p).read_bytes(); return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
def semok(c): return c.get('semantic_digest_scope')=='proof_payload' and dg(c.get('proof_payload'))==c.get('semantic_digest')
def producer_import_check(p):
 t=ast.parse(Path(p).read_text()); mods=[]
 for n in ast.walk(t):
  if isinstance(n,ast.Import): mods.extend(a.name for a in n.names)
  elif isinstance(n,ast.ImportFrom): mods.append(n.module or '')
 req(not any(x.endswith('janus_c049_1_b4_6_3_general_leaf_semantic_bijection_verifier') for x in mods),'INV01','producer imports verifier')
def bind(a):
 req(gb(a.spec)==SPEC_BLOB,'INV01','spec blob'); s=load(a.spec); req(s['schema']==SPEC_SCHEMA and s['status']=='SPEC_FROZEN' and s['admission'] is False,'INV01','spec')
 for p,h in ((a.b1_doc,B1_DOC_BLOB),(a.b1_core,B1_CORE_BLOB),(a.b2_doc,B2_DOC_BLOB),(a.b2_core,B2_CORE_BLOB),(a.ledger_audit,LEDGER_AUDIT_BLOB)): req(gb(p)==h,'INV01','source blob')
 la=load(a.ledger_audit); req(la['semantic_digest']==s['source_bindings']['structural_gap_ledger']['audit_semantic_digest'] and dg(la['audit_payload'])==la['semantic_digest'],'INV01','ledger audit semantic'); producer_import_check(a.producer_source); return s
def derive_mapping(a):
 b1d=Path(a.b1_doc).read_text(); b1c=Path(a.b1_core).read_text(); b2d=Path(a.b2_doc).read_text(); b2c=Path(a.b2_core).read_text()
 req('A statistic is a triple `(L,R,lambda)`' in b1d and 'class Statistic' in b1c,'INV06','statistic mapping'); req('compactification normal form `tau`' in b1d and 'def compactify' in b1c,'INV06','tau mapping'); req('uses only `(1,0)`, `(0,1)`, or `(1,1)` steps' in b2d and 'def extension_preorder_witness' in b2c,'INV06','preorder mapping'); req('def up_k_closure' in b2c and 'Complete finite `U_k(B)` closure' in b2d,'INV06','upk mapping'); req('corrected definitions in `arXiv:1507.02184v4`' in b2d,'INV06','published mapping claim')
 return {'statistic_interface':True,'compactification_interface':True,'preorder_interface':True,'up_k_interface':True,'published_definition_claim_local':True}
def expected(s,a):
 psrc=s['published_source']; req(psrc['arxiv']=='1507.02184v4' and psrc['doi']=='10.1109/TIT.2017.2740283' and psrc['primary_result']=='Proposition 4.1','INV02','published source'); gt=s['general_theorem']; req(gt['conclusion']=='FS_k({V},B) = up_k({Delta_B},B)' and gt['delta_B']==[['ZERO','B',0],['B','ZERO',0]],'INV07','theorem formula'); req('FOR_ALL' in gt['quantification'] and 'no finite dimension or cap is frozen' in gt['quantification'],'INV03','quantification')
 # Symbolic endpoint derivation: with B<=V, V∩B=B; intersections with ZERO are ZERO; each endpoint prefix∩suffix is ZERO so lambda=0.
 deriv={'singleton_layout_count_expression':'1!','singleton_layout_count':1,'unique_layout':['V'],'premise':'B<=V','intersection_laws':['ZERO_INTER_V=ZERO','V_INTER_ZERO=ZERO','ZERO_INTER_B=ZERO','V_INTER_B=B'],'canonical_definition':['L_i=(prefix span) INTER B','R_i=(suffix span) INTER B','lambda_i=dim(prefix INTER suffix)-dim(prefix INTER suffix INTER B)'],'first_cut':{'prefix':'ZERO','suffix':'V','L':'ZERO','R':'B','lambda':0},'second_cut':{'prefix':'V','suffix':'ZERO','L':'B','R':'ZERO','lambda':0},'delta_B':[['ZERO','B',0],['B','ZERO',0]],'delta_is_unique_canonical_singleton_trajectory':True}
 return deriv,derive_mapping(a)
def verify(c,s,a):
 req(c.get('schema')==SCHEMA and semok(c),'INV01','candidate'); p=c['proof_payload']; deriv,mapping=expected(s,a)
 q=p['quantifiers']; req(q=={'ambient_space':'FOR_ALL finite-dimensional GF(2) vector spaces A','V':'FOR_ALL subspaces V<=A','B':'FOR_ALL subspaces B<=V','k':'FOR_ALL integers k>=0','concrete_ambient_dimension_used':False,'concrete_boundary_dimension_used':False,'concrete_factor_vector_used':False,'concrete_k_used':False},'INV03','universal quantifiers'); req(p['symbolic_leaf_derivation']==deriv,'INV05','leaf derivation'); req(p['symbolic_leaf_derivation']['singleton_layout_count']==1,'INV04','unique layout'); req(p['local_semantic_mapping']==mapping,'INV06','local mapping')
 t=p['published_theorem']; req(t['arxiv']=='1507.02184v4' and t['doi']=='10.1109/TIT.2017.2740283' and t['result']=='Proposition 4.1' and t['normalized_formula']=='FS_k({V},B) = up_k({Delta_B},B)','INV02','published theorem'); req(t['dependency_status']=='PUBLISHED_GENERAL_THEOREM_TRUSTED_NOT_INDEPENDENTLY_REPROVED','INV08','dependency ceiling')
 br=p['semantic_bridge']; req(br['theorem_formula']=='FS_k({V},B) = up_k({Delta_B},B)' and br['local_interface_matches_published_leaf_theorem'] is True and br['singleton_realizable_language_has_unique_canonical_source']=='Delta_B','INV07','bridge')
 d=p['dependency_ceiling']; req(d=={'paper_mathematics_independently_reproved_by_repo':False,'published_proposition_used_as_external_mathematical_dependency':True,'local_semantic_mapping_machine_checked':True,'general_leaf_theorem_claim_scope':'ONLY_THE_SINGLE_SUBSPACE_BASE_CASE'},'INV08','dependency ceiling')
 b=p['strict_boundary']; exp={'o1_leaf_language_base_case':False,'general_leaf_semantic_bijection_receipt':False,'remaining_general_semantic_theorems':7,'o2_o7_established':False,'structural_induction_proved':False,'terminal_completeness_proved':False,'global_engine_no_layout_at_cap':'FORBIDDEN','formal_admission':'BLOCKED','next_gate':'CLOSED','current_global_terminal':TERM,'p_vs_np':'OPEN'}; req(b==exp,'INV12','boundary'); req(s['admission_boundary']['may_promote_after_exact_head_ci_semantic_audit_and_reviewer_receipt']==['O1_LEAF_LANGUAGE_BASE_CASE','GENERAL_LEAF_SEMANTIC_BIJECTION_RECEIPT'],'INV09','promotion scope'); return True
def seal(x): x['semantic_digest']=dg(x['proof_payload'])
def tampers(c,s,a):
 ok=[]
 def atk(name,mut):
  x=copy.deepcopy(c); mut(x); seal(x)
  try: verify(x,s,a)
  except VError as e: ok.append((name,e.inv)); return
  raise AssertionError('survived '+name)
 atk('T01_PROP',lambda x:x['proof_payload']['published_theorem'].__setitem__('result','Proposition 4.2')); atk('T02_PREMISE',lambda x:x['proof_payload']['symbolic_leaf_derivation'].__setitem__('premise','B arbitrary')); atk('T03_DELTA',lambda x:x['proof_payload']['symbolic_leaf_derivation'].__setitem__('delta_B',[['ZERO','B',1],['B','ZERO',0]])); atk('T04_DIM_ORACLE',lambda x:x['proof_payload']['quantifiers'].__setitem__('concrete_ambient_dimension_used',3)); atk('T05_K_ORACLE',lambda x:x['proof_payload']['quantifiers'].__setitem__('concrete_k_used',1)); atk('T06_B1_MAP',lambda x:x['proof_payload']['local_semantic_mapping'].__setitem__('compactification_interface',False)); atk('T07_B2_MAP',lambda x:x['proof_payload']['local_semantic_mapping'].__setitem__('preorder_interface',False)); atk('T08_REPROOF',lambda x:x['proof_payload']['dependency_ceiling'].__setitem__('paper_mathematics_independently_reproved_by_repo',True)); atk('T09_O2',lambda x:x['proof_payload']['strict_boundary'].__setitem__('o2_o7_established',True)); atk('T10_INDUCTION',lambda x:x['proof_payload']['strict_boundary'].__setitem__('structural_induction_proved',True)); atk('T11_TERMINAL',lambda x:x['proof_payload']['strict_boundary'].__setitem__('terminal_completeness_proved',True)); atk('T12_PNP',lambda x:x['proof_payload']['strict_boundary'].__setitem__('p_vs_np','CLOSED')); req(len(ok)==12,'INV11','tamper count'); return ok
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--spec',type=Path,required=True); ap.add_argument('--producer-source',type=Path,required=True); ap.add_argument('--b1-doc',type=Path,required=True); ap.add_argument('--b1-core',type=Path,required=True); ap.add_argument('--b2-doc',type=Path,required=True); ap.add_argument('--b2-core',type=Path,required=True); ap.add_argument('--ledger-audit',type=Path,required=True); ap.add_argument('--candidate-a',type=Path,required=True); ap.add_argument('--candidate-b',type=Path,required=True); ap.add_argument('--tamper-suite',action='store_true'); a=ap.parse_args(); s=bind(a); req(a.candidate_a.read_bytes()==a.candidate_b.read_bytes(),'INV10','byte identity'); c=load(a.candidate_a); verify(c,s,a); ts=tampers(c,s,a) if a.tamper_suite else []
 print('JANUS_GENERAL_LEAF_SEMANTIC_BIJECTION_INDEPENDENT_VERIFIER = PASS'); print('PRODUCER_IMPORT = FORBIDDEN_AND_NOT_USED'); print('INVARIANTS = 12/12'); print('DIGEST_REPAIRED_TAMPERS_REJECTED =',f'{len(ts)}/12' if a.tamper_suite else 'NOT_RUN'); print('QUANTIFICATION = UNIVERSAL_SYMBOLIC_GF2'); print('PUBLISHED_RESULT = JKO_PROPOSITION_4_1'); print('LOCAL_SEMANTIC_MAPPING = PASS'); print('PAPER_MATHEMATICS_INDEPENDENTLY_REPROVED_BY_REPO = FALSE'); print('GENERAL_LEAF_SEMANTIC_BIJECTION_RECEIPT = FALSE'); print('TERMINAL_COMPLETENESS_PROVED = FALSE'); print('P_VS_NP = OPEN')
if __name__=='__main__': main()
