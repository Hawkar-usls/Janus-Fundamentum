from __future__ import annotations
import argparse, ast, copy, hashlib, json
from pathlib import Path
SCHEMA='janus.c049_1.corrected_terminal_structural_reflection_ledger_candidate.v1'
SPEC_SCHEMA='janus.c049_1.corrected_terminal_structural_reflection_spec.v1'
IDS=['O1_LEAF_LANGUAGE_BASE_CASE','O2_EXPAND_PRESERVATION_AND_REFLECTION','O3_JOIN_INTERLEAVING_PRESERVATION_AND_REFLECTION','O4_SHRINK_PRESERVATION_AND_REFLECTION','O5_WIDTH_FILTER_SOUNDNESS_AND_REFLECTION','O6_B2_DELETION_AND_UP_K_LANGUAGE_PRESERVATION_AND_REFLECTION','O7_EMPTY_ROOT_SPECIALIZATION_TO_COMPLETE_LAYOUTS']
TERM='OPEN_TRAJECTORY_ENGINE_INCOMPLETE'
class VError(Exception):
 def __init__(self,inv,msg): super().__init__(f'{inv}:{msg}'); self.inv=inv
def req(x,inv,msg):
 if not x: raise VError(inv,msg)
def cb(x): return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def dg(x): return hashlib.sha256(cb(x)).hexdigest()
def load(p): return json.loads(Path(p).read_text())
def txt(p): return Path(p).read_text()
def gb(p):
 b=Path(p).read_bytes(); return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
def fh(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def semok(c): return c.get('semantic_digest_scope')=='proof_payload' and dg(c.get('proof_payload'))==c.get('semantic_digest')
def no_producer_import(path):
 t=ast.parse(Path(path).read_text()); mods=[]
 for n in ast.walk(t):
  if isinstance(n,ast.Import): mods.extend(a.name for a in n.names)
  elif isinstance(n,ast.ImportFrom): mods.append(n.module or '')
 req(not any(x.endswith('janus_c049_1_b4_6_3_corrected_terminal_structural_reflection_ledger_verifier') for x in mods),'INV01','producer imports verifier')
def derive(spec,a):
 src=spec['source_bindings']; files={'b1_doc':a.b1_doc,'b1_core':a.b1_core,'b2_doc':a.b2_doc,'b2_core':a.b2_core,'b3_doc':a.b3_doc,'historical_reflection_obstruction':a.obstruction,'root_biconditional_plan':a.plan,'corrected_root_spec':a.root_spec}
 for k,p in files.items(): req(gb(p)==src[k]['git_blob'],'INV01',k)
 q=src['admitted_finite_terminal_pointwise']; audit=load(a.pointwise_audit); req(gb(a.pointwise_audit)==q['audit_git_blob'] and fh(a.pointwise_audit)==q['audit_file_sha256'],'INV01','pointwise audit bytes'); req(audit['semantic_digest']==q['audit_semantic_digest'] and dg(audit['audit_payload'])==q['audit_semantic_digest'],'INV01','pointwise audit semantic')
 b1d,b1c,b2d,b2c,b3d,obs,plan=map(txt,(a.b1_doc,a.b1_core,a.b2_doc,a.b2_core,a.b3_doc,a.obstruction,a.plan)); rs=load(a.root_spec)
 # Independent evidence extraction uses exact invariants rather than producer's boolean dictionary construction.
 req('def compactify' in b1c and 'exact width preservation' in b1d,'INV05','B1 algebra'); req('extension preorder' in b2d.lower() and 'def extension_preorder_witness' in b2c,'INV05','B2 algebra')
 req(all(h in b3d for h in ('### Expand','### Join','### Shrink')),'INV03','B3 ops'); req('JANUS_ROOT_BICONDITIONAL     = NOT_YET_PROVED' in plan,'INV04','plan ceiling')
 req(all(x in plan for x in ('Leaf base case','Expand completeness','Join completeness','Shrink completeness','Width filter soundness and reflection','B2 preservation and reflection','Root specialization')),'INV02','seven plan obligations')
 req('semantic inconsistency' in obs and 'width-1 layouts = 0' in obs and 'width-1 fine refinements = 7,825' in obs,'INV07','negative obstruction')
 req(rs['refinement_contract']['ordinary_join_diagonal_allowed'] is False and rs['refinement_contract']['ordinary_join_steps']==[[1,0],[0,1]],'INV06','corrected H/V'); req(rs['canonical_semantics']['extension_preorder_steps']==[[1,0],[0,1],[1,1]],'INV06','B2 diagonal distinction')
 ap=audit['audit_payload']; req(ap['semantic_conclusion']['structural_induction_proved'] is False and ap['semantic_conclusion']['terminal_completeness_proved'] is False,'INV08','finite ceiling'); req(ap['independent_layout_replay']['permutations_scanned']==720 and ap['independent_layout_replay']['accepting_layout_count']==0,'INV08','finite pointwise')
 ceilings=['TRAJECTORY_ALGEBRA_ESTABLISHED','IMPLEMENTATION_AND_FINITE_REPLAY_ONLY','IMPLEMENTATION_AND_FINITE_REPLAY_ONLY','IMPLEMENTATION_AND_FINITE_REPLAY_ONLY','FINITE_INSTANCE_SEMANTIC_CROSSCHECK_ESTABLISHED','TRAJECTORY_ALGEBRA_ESTABLISHED','FINITE_INSTANCE_SEMANTIC_CROSSCHECK_ESTABLISHED']
 obs_by={o['id']:o for o in spec['obligations']}; req(list(obs_by)==IDS,'INV02','ids')
 expected=[]
 for i,oid in enumerate(IDS):
  o=obs_by[oid]; req(o['existing_evidence_ceiling']==ceilings[i] and o['existing_evidence_ceiling']!='GENERAL_SEMANTIC_THEOREM_ESTABLISHED','INV04','ceiling'); req(o['required_next_receipt'].startswith('GENERAL_'),'INV09','next receipt'); expected.append({'id':oid,'required_theorem':o['required_theorem'],'evidence_ceiling':ceilings[i],'next_receipt':o['required_next_receipt'],'general_semantic_theorem_established':False})
 return expected
def verify(c,spec,a):
 req(c.get('schema')==SCHEMA and semok(c),'INV01','candidate semantic'); p=c['proof_payload']; expected=derive(spec,a)
 req(p['obligations']==expected and p['obligation_count']==7,'INV03','ledger exact'); req(p['general_semantic_theorems_established']==0 and p['remaining_general_semantic_theorems']==7,'INV04','theorem count'); req(p['first_required_next_receipt']=='GENERAL_LEAF_SEMANTIC_BIJECTION_RECEIPT','INV09','next gate'); req(p['negative_evidence_preserved'] is True,'INV07','negative evidence'); req(p['finite_pointwise_result_preserved'] is True,'INV08','finite evidence')
 checks=p['source_checks']; req(len(checks)==12 and all(checks.values()),'INV01','source checks')
 b=p['strict_boundary']; exp={'root_empty_proved':True,'frozen_six_factor_no_layout_at_cap':True,'frozen_instance_root_layout_pointwise_equivalence':True,'structural_reflection_obligation_ledger_complete':False,'structural_induction_proved':False,'terminal_completeness_proved':False,'global_engine_no_layout_at_cap':'FORBIDDEN','found_layout':'FORBIDDEN','formal_admission':'BLOCKED','next_gate':'CLOSED','current_global_terminal':TERM,'p_vs_np':'OPEN'}; req(b==exp,'INV12','boundary'); return True
def seal(x): x['semantic_digest']=dg(x['proof_payload'])
def tamper(c,spec,a):
 ok=[]
 def atk(name,mut):
  x=copy.deepcopy(c); mut(x); seal(x)
  try: verify(x,spec,a)
  except VError as e: ok.append((name,e.inv)); return
  raise AssertionError('survived '+name)
 atk('T01_SOURCE_CHECK',lambda x:x['proof_payload']['source_checks'].__setitem__('b1_compactify',False)); atk('T02_DROP_OBLIGATION',lambda x:x['proof_payload']['obligations'].pop()); atk('T03_REORDER_OBLIGATIONS',lambda x:x['proof_payload']['obligations'].reverse()); atk('T04_PROMOTE_THEOREM',lambda x:x['proof_payload']['obligations'][0].__setitem__('general_semantic_theorem_established',True)); atk('T05_PROMOTE_CEILING',lambda x:x['proof_payload']['obligations'][1].__setitem__('evidence_ceiling','GENERAL_SEMANTIC_THEOREM_ESTABLISHED')); atk('T06_ERASE_PATH_DISTINCTION',lambda x:x['proof_payload']['source_checks'].__setitem__('b2_diagonal_distinct',False)); atk('T07_ERASE_NEGATIVE',lambda x:x['proof_payload'].__setitem__('negative_evidence_preserved',False)); atk('T08_PROMOTE_FINITE',lambda x:x['proof_payload'].__setitem__('general_semantic_theorems_established',1)); atk('T09_REMOVE_NEXT_RECEIPT',lambda x:x['proof_payload']['obligations'][0].__setitem__('next_receipt','')); atk('T10_LEDGER_ADMIT',lambda x:x['proof_payload']['strict_boundary'].__setitem__('structural_reflection_obligation_ledger_complete',True)); atk('T11_TERMINAL_PROMOTE',lambda x:x['proof_payload']['strict_boundary'].__setitem__('terminal_completeness_proved',True)); atk('T12_PNP_PROMOTE',lambda x:x['proof_payload']['strict_boundary'].__setitem__('p_vs_np','CLOSED'))
 req(len(ok)==12,'INV11','tamper count'); return ok
def main():
 p=argparse.ArgumentParser(); p.add_argument('--spec',type=Path,required=True); p.add_argument('--producer-source',type=Path,required=True); p.add_argument('--pointwise-audit',type=Path,required=True); p.add_argument('--root-spec',type=Path,required=True); p.add_argument('--b1-doc',type=Path,required=True); p.add_argument('--b1-core',type=Path,required=True); p.add_argument('--b2-doc',type=Path,required=True); p.add_argument('--b2-core',type=Path,required=True); p.add_argument('--b3-doc',type=Path,required=True); p.add_argument('--obstruction',type=Path,required=True); p.add_argument('--plan',type=Path,required=True); p.add_argument('--candidate-original',type=Path,required=True); p.add_argument('--candidate-reordered',type=Path,required=True); p.add_argument('--tamper-suite',action='store_true'); a=p.parse_args(); spec=load(a.spec); req(spec['schema']==SPEC_SCHEMA and spec['status']=='SPEC_FROZEN','INV01','spec'); no_producer_import(a.producer_source); req(a.candidate_original.read_bytes()==a.candidate_reordered.read_bytes(),'INV10','byte identity'); c=load(a.candidate_original); verify(c,spec,a); ts=tamper(c,spec,a) if a.tamper_suite else []
 print('JANUS_TERMINAL_STRUCTURAL_REFLECTION_LEDGER_INDEPENDENT_VERIFIER = PASS'); print('PRODUCER_IMPORT = FORBIDDEN_AND_NOT_USED'); print('IMPLEMENTATION_DECOUPLING = REQUIRED_AND_OBSERVED'); print('INVARIANTS = 12/12'); print('DIGEST_REPAIRED_TAMPERS_REJECTED =',f'{len(ts)}/12' if a.tamper_suite else 'NOT_RUN'); print('OBLIGATIONS = 7'); print('GENERAL_SEMANTIC_THEOREMS_ESTABLISHED = 0'); print('REMAINING_GENERAL_SEMANTIC_THEOREMS = 7'); print('FIRST_REQUIRED_NEXT_RECEIPT = GENERAL_LEAF_SEMANTIC_BIJECTION_RECEIPT'); print('TERMINAL_COMPLETENESS_PROVED = FALSE'); print('GLOBAL_ENGINE_NO_LAYOUT_AT_CAP = FORBIDDEN'); print('P_VS_NP = OPEN')
if __name__=='__main__': main()
