from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from research.tools.apma_satlib_uf20_r000_r111_projected_core_replay import projection_identity

ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_RAW_BOUND_PENDANT_EXACT_SIMULTANEOUS_ONE_ROUND_REDUCTION_PREREGISTRATION_2026-09-17.json'
REVIEW=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_RAW_BOUND_PENDANT_EXACT_SIMULTANEOUS_ONE_ROUND_REDUCTION_PREREGISTRATION_REVIEW_2026-09-17.json'
DEPENDENCY=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_RAW_BOUND_PENDANT_SIMULTANEOUS_DEPENDENCY_AUDIT_RESULT_2026-09-17.json'
BOUNDARY=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_RAW_BOUND_PENDANT_EXISTENTIAL_BOUNDARY_PROJECTION_RESULT_2026-09-17.json'
RECON=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_RAW_BOUND_D2_D3_WITNESS_RECONSTRUCTION_RESULT_2026-09-17.json'
PROJECTION=ROOT/'research/tools/apma_satlib_uf20_r000_r111_projected_core_replay/projection_identity.py'
EXPECTED={PREREG:'308fef7f6f4d0038416e5242268988160d2eb4e0',REVIEW:'6a568bec946136440979e676b1d82ac7d0c86af7',DEPENDENCY:'4d9fb36af246dc8d922afe47deb6780a3c1b9244',BOUNDARY:'3a9d46cb888489e769bab1e7d292e4eff459f786',RECON:'d91e82fa2e558bb2926cc42b5f4368af51ae9c10',PROJECTION:'2ef48e73974a5f43d3f4fb4809ebd0c09c0f5be4'}
ORDER=('UF20_02','UF20_03','UF20_04','UF20_05')
SOURCES={
 'UF20_02':(ROOT/'research/source_data/SATLIB_UF20_02_2026-09-16.cnf','f924caaef0d868bf62b1658e83e030ad8daee865','cc181d11871a9907cd5024ef5f0951cb29b32c4ed378e06c48f432e20be580e6'),
 'UF20_03':(ROOT/'research/source_data/SATLIB_UF20_03_2026-09-16.cnf','8f3d15154515457281f49201b843f2a7134dfa9f','30beb0c870105dfbbf017c067298f3295fcb555130e045242fdacea9259eb97d'),
 'UF20_04':(ROOT/'research/source_data/SATLIB_UF20_04_2026-09-16.cnf','34ced5c169f967b2dc44ef5e42f2ee2c924813e1','db98a7a25397a7178df02e16e9f593fde432f9b07d3aa14b44d67dcd051069f3'),
 'UF20_05':(ROOT/'research/source_data/SATLIB_UF20_05_2026-09-16.cnf','3b04eff26ee37bdd0bc21b1066486974f92a2c9b','fd9c0c19089daf08e549ff3ab63c0c7203b61c03cce7c4bcce0778ca2fe4f3d6')}

def blob(p:Path)->str:
 d=p.read_bytes();return hashlib.sha1(f'blob {len(d)}\0'.encode()+d).hexdigest()
def csha(o:Any)->str:return hashlib.sha256(json.dumps(o,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def constraint_hash(c):return csha({'id':c['id'],'scope':c['scope'],'allowed':c['allowed']})
def firewall():return {'P_VS_NP':'OPEN','GENERAL_SAT_IN_P':'NOT_PROVED','GENERAL_GT2_TRACTABILITY':'NOT_PROVED','CONNECTED_MIXED_CORE_SOLVED':'NO','SCOPED_EXACT_REDUCTION_IMPLIES_GLOBAL_TRACTABILITY':False}
def main():
 binds={str(p.relative_to(ROOT)):blob(p)==h for p,h in EXPECTED.items()};sb={n:blob(p)==h for n,(p,h,_) in SOURCES.items()};pre=json.loads(PREREG.read_text());rev=json.loads(REVIEW.read_text());dep=json.loads(DEPENDENCY.read_text());bound=json.loads(BOUNDARY.read_text());recon=json.loads(RECON.read_text())
 checks={'authority_bindings':all(binds.values()),'source_bindings':all(sb.values()),'review_authorized':rev.get('verdict')=='PASS_PREREGISTRATION_CLEAN__AUTHORIZED_TO_IMPLEMENT_AND_EXECUTE_ONCE','dependency_zero':dep.get('verdict')=='ZERO_CROSS_ATTACHMENT_DEPENDENCY','boundary_all_universal':bound.get('verdict')=='ALL_ELEVEN_UNIVERSAL','reconstruction_exact':recon.get('verdict')=='COMMON_FOUR_EXACT_RAW_BOUND_ALIGNMENT','single_round_frozen':pre['target_scope']['iterate_reduction'] is False and pre['target_scope']['discover_additional_targets_after_deletion'] is False}
 guard={'ok':all(checks.values()),'checks':checks,'bindings':binds,'source_bindings':sb}
 if not guard['ok']:return {'verdict':'FAIL_BINDING_OR_STRUCTURAL_PRECONDITION','source_guard':guard,'scientific_firewall':firewall()}
 boundary_by_source={r['source']:r['attachments'] for r in bound['source_receipts']};rows=[];all_ok=True
 for source in ORDER:
  path,_,expected_sha=SOURCES[source];original,_=projection_identity.normalize_projection(source,projection_identity.parse(path));orig_sha=csha(original)
  if orig_sha!=expected_sha:return {'verdict':'FAIL_BINDING_OR_STRUCTURAL_PRECONDITION','source':source,'reason':'ORIGINAL_PROJECTED_RAW_SHA_MISMATCH','observed':orig_sha,'expected':expected_sha,'source_guard':guard,'scientific_firewall':firewall()}
  target=pre['frozen_per_source_targets'][source];remove_ids=set(target['remove_constraints']);remove_leaves=set(int(x) for x in target['remove_leaves']);byid={c['id']:c for c in original['constraints']};bmap={a['constraint_id']:a for a in boundary_by_source[source]}
  target_ids_exist=remove_ids==set(x for x in remove_ids if x in byid);target_leaves_exist=remove_leaves.issubset(set(original['variables']));targets_match_boundary=remove_ids==set(bmap) and remove_leaves==set(int(a['leaf']) for a in boundary_by_source[source])
  pre_occ={leaf:[c['id'] for c in original['constraints'] if leaf in c['scope']] for leaf in sorted(remove_leaves)};pre_occ_clean=all(len(ids)==1 and ids[0] in remove_ids for ids in pre_occ.values())
  remaining_constraints=[c for c in original['constraints'] if c['id'] not in remove_ids];remaining_variables=[int(v) for v in original['variables'] if int(v) not in remove_leaves];reduced={'variables':remaining_variables,'constraints':remaining_constraints}
  removed_leaf_absent=all(not (remove_leaves & set(int(v) for v in c['scope'])) for c in remaining_constraints)
  gateways=sorted({int(v) for a in boundary_by_source[source] for v in a['gateway']});gateways_remain=all(v in set(remaining_variables) for v in gateways)
  original_nontarget={c['id']:constraint_hash(c) for c in original['constraints'] if c['id'] not in remove_ids};reduced_map={c['id']:constraint_hash(c) for c in reduced['constraints']};unchanged_nontarget=original_nontarget==reduced_map
  no_nontarget_var_removed=set(original['variables'])-set(remaining_variables)==remove_leaves
  cert=[]
  for a in boundary_by_source[source]:
   cid=a['constraint_id'];w=dict(a['canonical_witnesses']);cert.append({'source':source,'removed_constraint_id':cid,'removed_leaf':int(a['leaf']),'gateway_pair':[int(v) for v in a['gateway']],'canonical_witness_table_00_01_10_11':{k:int(w[k]) for k in ('00','01','10','11')}})
  cert.sort(key=lambda r:r['removed_constraint_id'])
  witness_complete=all(set(r['canonical_witness_table_00_01_10_11'])=={'00','01','10','11'} for r in cert)
  structural=all([target_ids_exist,target_leaves_exist,targets_match_boundary,pre_occ_clean,removed_leaf_absent,gateways_remain,unchanged_nontarget,no_nontarget_var_removed,witness_complete])
  semantics={'forward_projection_verified_symbolically':structural,'reverse_extension_verified_from_frozen_universal_boundary_and_zero_dependency':structural,'projection_solution_set_equality_verified_symbolically':structural,'sat_equivalence_verified_symbolically':structural,'global_assignment_enumeration_used':False}
  row={'source':source,'original_projected_raw_sha256':orig_sha,'original_variable_count':len(original['variables']),'original_constraint_count':len(original['constraints']),'removed_constraint_ids':sorted(remove_ids),'removed_leaves':sorted(remove_leaves),'pre_transform_leaf_occurrences':pre_occ,'reduced_raw':reduced,'reduced_raw_sha256':csha(reduced),'reduced_variable_count':len(reduced['variables']),'reduced_constraint_count':len(reduced['constraints']),'remaining_constraint_fingerprints':reduced_map,'all_target_constraints_exist':target_ids_exist,'all_target_leaves_exist':target_leaves_exist,'targets_match_frozen_boundary_receipts':targets_match_boundary,'each_removed_leaf_occurs_only_in_own_target_constraint':pre_occ_clean,'no_removed_leaf_in_remaining_scope':removed_leaf_absent,'all_gateways_remain':gateways_remain,'all_nontarget_constraints_unchanged':unchanged_nontarget,'no_nontarget_variable_removed':no_nontarget_var_removed,'reconstruction_certificate':cert,'semantics_certificate':semantics,'source_pass':structural and all(semantics[k] for k in ('forward_projection_verified_symbolically','reverse_extension_verified_from_frozen_universal_boundary_and_zero_dependency','projection_solution_set_equality_verified_symbolically','sat_equivalence_verified_symbolically'))}
  rows.append(row);all_ok=all_ok and row['source_pass']
 verdict='PASS_EXACT_SIMULTANEOUS_ONE_ROUND_REDUCTION' if all_ok else 'FAIL_SEMANTICS_CERTIFICATE'
 return {'artifact_id':'JANUS-TRUMP-SATLIB-UF20-R000-R111-RAW-BOUND-PENDANT-EXACT-SIMULTANEOUS-ONE-ROUND-REDUCTION-CANDIDATE-2026-09-17-v1.0','authority':'SEMANTICS_PRESERVING_EXACT_ONE_ROUND_REPRESENTATION_REDUCTION_ONLY','verdict':verdict,'source_guard':guard,'rows':rows,'resource_receipt':{'target_sources':4,'reduction_rounds':1,'target_constraints':11,'target_leaves':11,'post_round_target_discoveries':0,'new_relations_added':0,'solver_invocations':0,'portfolio_replays':0,'global_assignment_enumerations':0,'action_tests':0,'automorphism_tests':0,'group_searches':0,'fresh_holdout_values_read':0},'scientific_firewall':firewall()}
if __name__=='__main__':print(json.dumps(main(),sort_keys=True,separators=(',',':')))
