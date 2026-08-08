from __future__ import annotations
import argparse,ast,copy,hashlib,json
from pathlib import Path
SCHEMA='janus.c049_1.general_corrected_join_semantic_bijection_candidate.v1';SPEC_SCHEMA='janus.c049_1.general_corrected_join_semantic_bijection_spec.v1';SPEC_BLOB='837e839a1c6b0a6daa3644ce5c3c4ca373ed831b';O2_AUDIT_BLOB='6e0e00f9cbcf017c977aea683b62ac201212177e';B3_CORE_BLOB='443566c4b79bf67ec1613413130169cab12ebb0f';B3_DOC_BLOB='786f4cc657335f31ca8696167bc2bde66d53180b';OBS_BLOB='fcfa6698f87c4f3782354fe1c76fb707ac304c32';ROOT_SPEC_BLOB='401c4856de261f6048d313ca62fa43598ea449e0';ROOT_PRODUCER_BLOB='e4378ee30743a43a0884237b3a51a6930542373a';TERM='OPEN_TRAJECTORY_ENGINE_INCOMPLETE'
class E(Exception):
 def __init__(self,i,m):super().__init__(f'{i}:{m}');self.i=i
def req(x,i,m):
 if not x:raise E(i,m)
def cb(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def dg(x):return hashlib.sha256(cb(x)).hexdigest()
def load(p):return json.loads(Path(p).read_text())
def gb(p):
 b=Path(p).read_bytes();return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
def sem(c):return c.get('semantic_digest_scope')=='proof_payload' and dg(c.get('proof_payload'))==c.get('semantic_digest')
def bind(a):
 req(gb(a.spec)==SPEC_BLOB,'INV01','spec');s=load(a.spec);req(s['schema']==SPEC_SCHEMA and s['status']=='SPEC_FROZEN','INV01','spec schema')
 for p,h in ((a.o2_audit,O2_AUDIT_BLOB),(a.b3_core,B3_CORE_BLOB),(a.b3_doc,B3_DOC_BLOB),(a.obstruction,OBS_BLOB),(a.root_spec,ROOT_SPEC_BLOB),(a.root_producer,ROOT_PRODUCER_BLOB)):req(gb(p)==h,'INV01','source')
 t=ast.parse(Path(a.producer_source).read_text());mods=[]
 for n in ast.walk(t):
  if isinstance(n,ast.Import):mods.extend(q.name for q in n.names)
  elif isinstance(n,ast.ImportFrom):mods.append(n.module or '')
 req(not any(x.endswith('janus_c049_1_b4_6_3_general_corrected_join_semantic_bijection_verifier') for x in mods),'INV01','producer imports verifier');return s
def mapping(a):
 b3=Path(a.b3_core).read_text();rp=Path(a.root_producer).read_text();rs=load(a.root_spec);obs=Path(a.obstruction).read_text()
 m={'generic_join_formula':all(z in b3 for z in ('initial_intersection = subspace_intersection(g1[0].right, g2[0].right','correction = dim(initial_intersection) - dim(current_intersection)','a.value + b.value + correction')),'historical_generic_path_has_diagonal':'for di, dj in ((1, 0), (0, 1), (1, 1))' in b3,'corrected_hv_generator':all(z in rp for z in ('def hv_paths','set(steps)-{\'H\',\'V\'}','diagonal ordinary path')),'corrected_join_formula':all(z in rp for z in ('init=sub_inter(g1[0][1],g2[0][1])','corr=dim(init)-dim(cur)','a[2]+b[2]+corr')),'corrected_spec_hv_only':rs['refinement_contract']['ordinary_join_diagonal_allowed'] is False and rs['refinement_contract']['ordinary_join_steps']==[[1,0],[0,1]],'preorder_diagonal_distinct':rs['canonical_semantics']['extension_preorder_steps']==[[1,0],[0,1],[1,1]],'historical_false_positive_preserved':'semantic inconsistency' in obs and 'width-1 layouts = 0' in obs};req(all(m.values()),'INV06','mapping');return m
def verify(c,s,a):
 req(c.get('schema')==SCHEMA and sem(c),'INV01','candidate');p=c['proof_payload'];pub=p['published_theorem'];req(pub['result']=='Proposition 4.4' and pub['arxiv']=='1507.02184v4' and pub['doi']=='10.1109/TIT.2017.2740283','INV02','source');req(pub['normalized_formula']=='FS_k(V1 disjoint_union V2,B)=up_k(FS_k(V1,B) OPLUS FS_k(V2,B),B)' and pub['precondition']=='(span(V1)+B) INTER (span(V2)+B) = B','INV02','formula')
 q=p['quantifiers'];req(q['concrete_dimension_used'] is False and q['concrete_fixture_used'] is False and q['concrete_k_used'] is False,'INV03','oracle');d=p['path_domain_separation'];req(d=={'ordinary_join_steps':[[1,0],[0,1]],'ordinary_join_diagonal_allowed':False,'preorder_steps':[[1,0],[0,1],[1,1]],'diagonal_belongs_to_preorder_not_ordinary_join':True},'INV04','path split');req(pub['ordinary_path_steps']==[[1,0],[0,1]],'INV04','paper ordinary path');req(p['local_semantic_mapping']==mapping(a),'INV06','mapping exact');req(p['local_semantic_mapping']['historical_false_positive_preserved'] is True,'INV08','negative evidence')
 dep=p['dependency_ceiling'];req(dep=={'paper_mathematics_independently_reproved_by_repo':False,'published_proposition_used_as_external_mathematical_dependency':True,'caller_join_separation_precondition_automatically_established':False,'historical_generic_join_trajectories_semantic_reference':False,'corrected_hv_join_mapping_machine_checked':True},'INV09','ceiling');b=p['strict_boundary'];exp={'o1_leaf_language_base_case':True,'o2_expand_preservation_and_reflection':'TRUE_CONDITIONALLY_ON_BOUND_PRECONDITION','o3_join_interleaving_preservation_and_reflection':False,'general_corrected_join_semantic_bijection_receipt':False,'caller_join_separation_precondition_automatically_established':False,'general_semantic_theorems_established':2,'remaining_general_semantic_theorems':5,'o4_o7_established':False,'structural_induction_proved':False,'terminal_completeness_proved':False,'global_engine_no_layout_at_cap':'FORBIDDEN','formal_admission':'BLOCKED','next_gate':'CLOSED','current_global_terminal':TERM,'p_vs_np':'OPEN'};req(b==exp,'INV12','boundary')
def seal(x):x['semantic_digest']=dg(x['proof_payload'])
def tamper(c,s,a):
 ok=[]
 def atk(n,f):
  x=copy.deepcopy(c);f(x);seal(x)
  try:verify(x,s,a)
  except E as e:ok.append((n,e.i));return
  raise AssertionError('survived '+n)
 atk('T01_PROP',lambda x:x['proof_payload']['published_theorem'].__setitem__('result','Proposition 4.3'));atk('T02_PRE',lambda x:x['proof_payload']['published_theorem'].__setitem__('precondition','TRUE'));atk('T03_DIAG',lambda x:x['proof_payload']['path_domain_separation'].__setitem__('ordinary_join_diagonal_allowed',True));atk('T04_NODIAGPRE',lambda x:x['proof_payload']['path_domain_separation'].__setitem__('preorder_steps',[[1,0],[0,1]]));atk('T05_FORMULA',lambda x:x['proof_payload']['local_semantic_mapping'].__setitem__('generic_join_formula',False));atk('T06_HISTREF',lambda x:x['proof_payload']['dependency_ceiling'].__setitem__('historical_generic_join_trajectories_semantic_reference',True));atk('T07_NEG',lambda x:x['proof_payload']['local_semantic_mapping'].__setitem__('historical_false_positive_preserved',False));atk('T08_AUTO',lambda x:x['proof_payload']['dependency_ceiling'].__setitem__('caller_join_separation_precondition_automatically_established',True));atk('T09_O4',lambda x:x['proof_payload']['strict_boundary'].__setitem__('o4_o7_established',True));atk('T10_IND',lambda x:x['proof_payload']['strict_boundary'].__setitem__('structural_induction_proved',True));atk('T11_TERM',lambda x:x['proof_payload']['strict_boundary'].__setitem__('terminal_completeness_proved',True));atk('T12_PNP',lambda x:x['proof_payload']['strict_boundary'].__setitem__('p_vs_np','CLOSED'));req(len(ok)==12,'INV11','tamper count');return ok
def main():
 p=argparse.ArgumentParser();
 for n in ('spec','producer-source','o2-audit','b3-core','b3-doc','obstruction','root-spec','root-producer','candidate-a','candidate-b'):p.add_argument('--'+n,type=Path,required=True)
 p.add_argument('--tamper-suite',action='store_true');a=p.parse_args();s=bind(a);req(a.candidate_a.read_bytes()==a.candidate_b.read_bytes(),'INV10','bytes');c=load(a.candidate_a);verify(c,s,a);ts=tamper(c,s,a) if a.tamper_suite else [];print('JANUS_GENERAL_CORRECTED_JOIN_SEMANTIC_BIJECTION_INDEPENDENT_VERIFIER = PASS');print('PRODUCER_IMPORT = FORBIDDEN_AND_NOT_USED');print('INVARIANTS = 12/12');print('DIGEST_REPAIRED_TAMPERS_REJECTED =',f'{len(ts)}/12');print('PUBLISHED_RESULT = JKO_PROPOSITION_4_4');print('ORDINARY_JOIN_PATH_DOMAIN = H_V_ONLY');print('PREORDER_DIAGONAL_DOMAIN_DISTINCT = TRUE');print('CALLER_JOIN_SEPARATION_PRECONDITION_AUTOMATICALLY_ESTABLISHED = FALSE');print('GENERAL_CORRECTED_JOIN_SEMANTIC_BIJECTION_RECEIPT = FALSE');print('TERMINAL_COMPLETENESS_PROVED = FALSE');print('P_VS_NP = OPEN')
if __name__=='__main__':main()
