from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
SCHEMA='janus.c049_1.corrected_terminal_structural_reflection_ledger_candidate.v1'
SPEC_SCHEMA='janus.c049_1.corrected_terminal_structural_reflection_spec.v1'
TERM='OPEN_TRAJECTORY_ENGINE_INCOMPLETE'
IDS=['O1_LEAF_LANGUAGE_BASE_CASE','O2_EXPAND_PRESERVATION_AND_REFLECTION','O3_JOIN_INTERLEAVING_PRESERVATION_AND_REFLECTION','O4_SHRINK_PRESERVATION_AND_REFLECTION','O5_WIDTH_FILTER_SOUNDNESS_AND_REFLECTION','O6_B2_DELETION_AND_UP_K_LANGUAGE_PRESERVATION_AND_REFLECTION','O7_EMPTY_ROOT_SPECIALIZATION_TO_COMPLETE_LAYOUTS']
def cb(x): return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def dg(x): return hashlib.sha256(cb(x)).hexdigest()
def load(p): return json.loads(Path(p).read_text())
def text(p): return Path(p).read_text()
def gb(p):
 b=Path(p).read_bytes(); return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
def save(x,p): Path(p).write_bytes(cb(x)+b'\n')
def require(x,m):
 if not x: raise AssertionError(m)
def build(a):
 s=load(a.spec); require(s['schema']==SPEC_SCHEMA and s['status']=='SPEC_FROZEN' and s['admission'] is False,'spec')
 src=s['source_bindings']; files={'b1_doc':a.b1_doc,'b1_core':a.b1_core,'b2_doc':a.b2_doc,'b2_core':a.b2_core,'b3_doc':a.b3_doc,'historical_reflection_obstruction':a.obstruction,'root_biconditional_plan':a.plan,'corrected_root_spec':a.root_spec}
 for k,p in files.items(): require(gb(p)==src[k]['git_blob'],f'blob {k}')
 audit=load(a.pointwise_audit); q=src['admitted_finite_terminal_pointwise']; require(gb(a.pointwise_audit)==q['audit_git_blob'],'audit blob'); require(hashlib.sha256(Path(a.pointwise_audit).read_bytes()).hexdigest()==q['audit_file_sha256'],'audit sha'); require(audit['semantic_digest']==q['audit_semantic_digest'] and dg(audit['audit_payload'])==q['audit_semantic_digest'],'audit semantic')
 b1d,b1c,b2d,b2c,b3d,obs,plan=(text(a.b1_doc),text(a.b1_core),text(a.b2_doc),text(a.b2_core),text(a.b3_doc),text(a.obstruction),text(a.plan)); rs=load(a.root_spec)
 checks={
 'b1_compactify':('def compactify' in b1c and 'exact width preservation' in b1d),
 'b1_scope_ceiling':('does not implement' in b1d and 'complete NO_LAYOUT_AT_CAP' in b1d),
 'b2_preorder':('def extension_preorder_witness' in b2c and 'up_k(original generators) = up_k(retained generators)' in b2d),
 'b2_scope_ceiling':('cannot emit complete `NO_LAYOUT_AT_CAP`' in b2d),
 'b3_ops':all(x in b3d for x in ('### Expand','### Join','### Shrink')),
 'b3_scope_ceiling':('complete `NO_LAYOUT_AT_CAP`' in b3d),
 'plan_not_proved':('JANUS_ROOT_BICONDITIONAL     = NOT_YET_PROVED' in plan),
 'plan_seven':all(x in plan for x in ('Leaf base case','Expand completeness','Join completeness','Shrink completeness','Width filter soundness and reflection','B2 preservation and reflection','Root specialization')),
 'historical_false_positive':('width-1 layouts = 0' in obs and 'width-1 fine refinements = 7,825' in obs and 'semantic inconsistency' in obs),
 'corrected_hv_only':rs['refinement_contract']['ordinary_join_diagonal_allowed'] is False and rs['refinement_contract']['ordinary_join_steps']==[[1,0],[0,1]],
 'b2_diagonal_distinct':rs['canonical_semantics']['extension_preorder_steps']==[[1,0],[0,1],[1,1]],
 'finite_pointwise_only':audit['audit_payload']['semantic_conclusion']['structural_induction_proved'] is False and audit['audit_payload']['semantic_conclusion']['terminal_completeness_proved'] is False and audit['audit_payload']['independent_layout_replay']['permutations_scanned']==720 and audit['audit_payload']['independent_layout_replay']['accepting_layout_count']==0,
 }
 require(all(checks.values()),'source support')
 obligations=[]
 for o in s['obligations']:
  require(o['id'] in IDS,'id'); obligations.append({'id':o['id'],'required_theorem':o['required_theorem'],'evidence_ceiling':o['existing_evidence_ceiling'],'next_receipt':o['required_next_receipt'],'general_semantic_theorem_established':False})
 require([x['id'] for x in obligations]==IDS,'order')
 proof={'phase':'CORRECTED_TERMINAL_STRUCTURAL_REFLECTION_OBLIGATION_LEDGER','status':'CANDIDATE_PENDING_ADMISSION','source_checks':checks,'obligations':obligations,'obligation_count':len(obligations),'general_semantic_theorems_established':0,'remaining_general_semantic_theorems':7,'first_required_next_receipt':'GENERAL_LEAF_SEMANTIC_BIJECTION_RECEIPT','negative_evidence_preserved':True,'finite_pointwise_result_preserved':True,'strict_boundary':{'root_empty_proved':True,'frozen_six_factor_no_layout_at_cap':True,'frozen_instance_root_layout_pointwise_equivalence':True,'structural_reflection_obligation_ledger_complete':False,'structural_induction_proved':False,'terminal_completeness_proved':False,'global_engine_no_layout_at_cap':'FORBIDDEN','found_layout':'FORBIDDEN','formal_admission':'BLOCKED','next_gate':'CLOSED','current_global_terminal':TERM,'p_vs_np':'OPEN'}}
 out={'schema':SCHEMA,'semantic_digest_scope':'proof_payload','proof_payload':proof}; out['semantic_digest']=dg(proof); save(out,a.output); return out
def main():
 p=argparse.ArgumentParser(); p.add_argument('--spec',type=Path,required=True); p.add_argument('--pointwise-audit',type=Path,required=True); p.add_argument('--root-spec',type=Path,required=True); p.add_argument('--b1-doc',type=Path,required=True); p.add_argument('--b1-core',type=Path,required=True); p.add_argument('--b2-doc',type=Path,required=True); p.add_argument('--b2-core',type=Path,required=True); p.add_argument('--b3-doc',type=Path,required=True); p.add_argument('--obstruction',type=Path,required=True); p.add_argument('--plan',type=Path,required=True); p.add_argument('--output',type=Path,required=True); a=p.parse_args(); x=build(a); q=x['proof_payload']; print('JANUS_TERMINAL_STRUCTURAL_REFLECTION_LEDGER_PRODUCER = PASS'); print('OBLIGATIONS =',q['obligation_count']); print('GENERAL_SEMANTIC_THEOREMS_ESTABLISHED =',q['general_semantic_theorems_established']); print('REMAINING_GENERAL_SEMANTIC_THEOREMS =',q['remaining_general_semantic_theorems']); print('FIRST_REQUIRED_NEXT_RECEIPT =',q['first_required_next_receipt']); print('TERMINAL_COMPLETENESS_PROVED = FALSE'); print('GLOBAL_ENGINE_NO_LAYOUT_AT_CAP = FORBIDDEN'); print('P_VS_NP = OPEN')
if __name__=='__main__': main()
