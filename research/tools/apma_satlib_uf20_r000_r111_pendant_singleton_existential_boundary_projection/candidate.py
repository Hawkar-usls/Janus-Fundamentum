from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path
from typing import Any

from research.tools.apma_satlib_uf20_r000_r111_projected_core_replay import projection_identity

ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PENDANT_SINGLETON_EXISTENTIAL_BOUNDARY_PROJECTION_PREREGISTRATION_2026-09-17.json'
REVIEW=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PENDANT_SINGLETON_EXISTENTIAL_BOUNDARY_PROJECTION_PREREGISTRATION_REVIEW_2026-09-17.json'
ALIGN=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_D2_D3_SINGLETON_ATTACHMENT_SCOPE_ALIGNMENT_RESULT_2026-09-17.json'
FRESH=ROOT/'research/TRUMP_SATLIB_UF20_SUCCESSOR_LOCAL_INVARIANT_FRESH_BLIND_SOURCE_ACQUISITION_RESULT_2026-09-17.json'
PROJECTION=ROOT/'research/tools/apma_satlib_uf20_r000_r111_projected_core_replay/projection_identity.py'
EXPECTED={PREREG:'1b1e2959bc238f18fa8f951876072f9f4c8f917f',REVIEW:'f44771b6f32c0837aea18bc4f03d2f74cf703c4b',ALIGN:'9442fca30db3e623c56a33d8fda6c3a1e3c1f624',FRESH:'3ee5a11808ea04326ec5141b0138bbba4ec56092',PROJECTION:'2ef48e73974a5f43d3f4fb4809ebd0c09c0f5be4'}
ORDER=('UF20_02','UF20_03','UF20_04','UF20_05')
SOURCES={
 'UF20_02':(ROOT/'research/source_data/SATLIB_UF20_02_2026-09-16.cnf','f924caaef0d868bf62b1658e83e030ad8daee865','cc181d11871a9907cd5024ef5f0951cb29b32c4ed378e06c48f432e20be580e6'),
 'UF20_03':(ROOT/'research/source_data/SATLIB_UF20_03_2026-09-16.cnf','8f3d15154515457281f49201b843f2a7134dfa9f','30beb0c870105dfbbf017c067298f3295fcb555130e045242fdacea9259eb97d'),
 'UF20_04':(ROOT/'research/source_data/SATLIB_UF20_04_2026-09-16.cnf','34ced5c169f967b2dc44ef5e42f2ee2c924813e1','db98a7a25397a7178df02e16e9f593fde432f9b07d3aa14b44d67dcd051069f3'),
 'UF20_05':(ROOT/'research/source_data/SATLIB_UF20_05_2026-09-16.cnf','3b04eff26ee37bdd0bc21b1066486974f92a2c9b','fd9c0c19089daf08e549ff3ab63c0c7203b61c03cce7c4bcce0778ca2fe4f3d6')}
BOUNDARY=((0,0),(0,1),(1,0),(1,1)); LEAF_VALUES=(0,1)

def blob(p:Path)->str:
 d=p.read_bytes();return hashlib.sha1(f'blob {len(d)}\0'.encode()+d).hexdigest()
def csha(obj:Any)->str:return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def guard():
 pre=json.loads(PREREG.read_text());review=json.loads(REVIEW.read_text());binds={str(p.relative_to(ROOT)):blob(p)==s for p,s in EXPECTED.items()};sb={n:blob(p)==sha for n,(p,sha,_) in SOURCES.items()}
 alignment=json.loads(ALIGN.read_text());count=sum(len(r['mappings']) for r in alignment['source_receipts'])
 checks={'authority_bindings':all(binds.values()),'source_bindings':all(sb.values()),'prereg_status':pre.get('status')=='FROZEN_BEFORE_ANY_EXISTENTIAL_BOUNDARY_RELATION_VALUE_COMPUTATION','review_authorized':review.get('verdict')=='PASS_PREREGISTRATION_CLEAN__AUTHORIZED_TO_IMPLEMENT_AND_EXECUTE_ONCE','target_sources_exact':tuple(pre['target_scope']['sources'])==ORDER,'attachment_count_exact':pre['target_scope']['attachment_count']==count==11,'boundary_order_exact':pre['boundary_projection_definition']['boundary_assignment_order']==[[0,0],[0,1],[1,0],[1,1]],'leaf_order_exact':pre['boundary_projection_definition']['leaf_value_order']==[0,1],'fresh_holdout_values_forbidden':pre['fresh_holdout_firewall']['formula_feature_partition_structural_boundary_or_solver_values_may_be_read_or_computed'] is False}
 return {'ok':all(checks.values()),'checks':checks,'bindings':binds,'source_bindings':sb}
def coordinate_map(scope:list[int],leaf:int,gateway:list[int]):
 roles={leaf:'LEAF',gateway[0]:'GATEWAY_0',gateway[1]:'GATEWAY_1'}
 return [{'scope_index':i,'variable':int(v),'role':roles[int(v)]} for i,v in enumerate(scope)]
def full_tuple(scope:list[int],leaf:int,gateway:list[int],b:tuple[int,int],z:int):
 a={leaf:z,gateway[0]:b[0],gateway[1]:b[1]};return tuple(int(a[int(v)]) for v in scope)
def one_attachment(raw:dict[str,Any],mapping:dict[str,Any]):
 by_id={r['id']:r for r in raw['constraints']};cid=mapping['constraint_id'];assert cid in by_id
 c=by_id[cid];scope=[int(v) for v in c['scope']];leaf=int(mapping['singleton_variable']);gateway=sorted(int(v) for v in mapping['gateway_pair']);assert scope==[int(v) for v in mapping['scope']];assert set(scope)==set([leaf]+gateway) and len(scope)==3 and len(gateway)==2
 occurrence_count=sum(leaf in [int(v) for v in r['scope']] for r in raw['constraints']);allowed_set={tuple(int(x) for x in t) for t in c['allowed']};table_sha=csha({'scope':scope,'allowed':c['allowed']});checks=[];boundary=[];witnesses={};tests=0
 for b in BOUNDARY:
  trials=[];first=None
  for z in LEAF_VALUES:
   ft=full_tuple(scope,leaf,gateway,b,z);ok=ft in allowed_set;tests+=1;trials.append({'leaf_value':z,'full_scope_tuple':list(ft),'allowed':ok})
   if ok and first is None:first=z
  accepted=first is not None
  checks.append({'boundary_tuple':list(b),'tested_leaf_values':trials,'accepted':accepted,'canonical_leaf_witness':first})
  if accepted:boundary.append(list(b));witnesses[''.join(map(str,b))]=first
 card=len(boundary);outcome='UNIVERSAL_BOUNDARY_RELATION_4_OF_4' if card==4 else 'PROPER_NONEMPTY_BOUNDARY_RELATION' if card>0 else 'EMPTY_BOUNDARY_RELATION'
 return {'constraint_id':cid,'scope':scope,'allowed_table_sha256':table_sha,'leaf_variable':leaf,'leaf_projected_constraint_occurrence_count':occurrence_count,'gateway_order':gateway,'scope_coordinate_map':coordinate_map(scope,leaf,gateway),'boundary_checks':checks,'boundary_relation':boundary,'boundary_relation_cardinality':card,'canonical_reconstruction_witnesses':witnesses,'membership_tests':tests,'outcome':outcome}
def firewall():return {'P_VS_NP':'OPEN','GENERAL_SAT_IN_P':'NOT_PROVED','GENERAL_GT2_TRACTABILITY':'NOT_PROVED','CONNECTED_MIXED_CORE_SOLVED':'NO','LOCAL_BOUNDARY_TRANSPARENCY_IMPLIES_GLOBAL_TRACTABILITY':False,'LOCAL_BOUNDARY_TRANSPARENCY_IMPLIES_HARDNESS':False,'LOCAL_BOUNDARY_TRANSPARENCY_IMPLIES_GLOBAL_CLOSURE':False}
def main():
 g=guard()
 if not g['ok']:return {'verdict':'HALT_FROZEN_AUTHORITY_OR_SOURCE_BINDING_FAILURE','source_guard':g,'scientific_firewall':firewall()}
 align=json.loads(ALIGN.read_text());maps={r['source']:r['mappings'] for r in align['source_receipts']};rows=[];total_tests=0
 for name in ORDER:
  path,_,expected_raw=SOURCES[name];raw,_=projection_identity.normalize_projection(name,projection_identity.parse(path));raw_sha=csha(raw)
  if raw_sha!=expected_raw:return {'verdict':'HALT_PROJECTED_RAW_BINDING_FAILURE','source':name,'observed':raw_sha,'expected':expected_raw,'source_guard':g,'scientific_firewall':firewall()}
  attachments=[one_attachment(raw,m) for m in maps[name]];total_tests+=sum(a['membership_tests'] for a in attachments);rows.append({'source':name,'projected_raw_sha256':raw_sha,'attachments':attachments})
 all_attachments=[a for r in rows for a in r['attachments']];outcomes=Counter(a['outcome'] for a in all_attachments)
 if outcomes['EMPTY_BOUNDARY_RELATION']>0:overall='AT_LEAST_ONE_EMPTY'
 elif outcomes['UNIVERSAL_BOUNDARY_RELATION_4_OF_4']==11:overall='ALL_ELEVEN_UNIVERSAL'
 else:overall='MIXED_OR_PROPER'
 theorem_premises=all(a['leaf_projected_constraint_occurrence_count']==1 and a['boundary_relation_cardinality']==4 for a in all_attachments)
 theorem={'applicable':overall=='ALL_ELEVEN_UNIVERSAL','all_leaf_unique_occurrence_premises_verified':all(a['leaf_projected_constraint_occurrence_count']==1 for a in all_attachments),'all_boundary_relations_universal_verified':all(a['boundary_relation_cardinality']==4 for a in all_attachments),'symbolic_projection_equivalence_verified':overall=='ALL_ELEVEN_UNIVERSAL' and theorem_premises,'statement':'FOR_EACH_TARGET_ATTACHMENT_F=C(x,u,v) AND H(Y),x_NOTIN_VARS(H),UNIVERSAL_EXISTS_x_C_IMPLIES_FOR_EVERY_y:EXISTS_x_F(x,y)_IFF_H(y)','deletion_applied':False}
 return {'artifact_id':'JANUS-TRUMP-SATLIB-UF20-R000-R111-PENDANT-SINGLETON-EXISTENTIAL-BOUNDARY-PROJECTION-CANDIDATE-2026-09-17-v1.0','authority':'DIAGNOSTIC_EXACT_LOCAL_EXISTENTIAL_BOUNDARY_RELATION_AUDIT_ONLY__NO_GLOBAL_SOLVER_COMPONENT_SOLVING_ACTION_AUTOMORPHISM_GROUP_SEARCH_CARRIER_ADAPTER_OR_QUOTIENT','verdict':overall,'source_guard':g,'rows':rows,'outcome_counts':{k:int(outcomes.get(k,0)) for k in ('UNIVERSAL_BOUNDARY_RELATION_4_OF_4','PROPER_NONEMPTY_BOUNDARY_RELATION','EMPTY_BOUNDARY_RELATION')},'overall_outcome':overall,'local_semantics_theorem':theorem,'resource_receipt':{'attachments':len(all_attachments),'boundary_assignments':len(all_attachments)*4,'table_membership_tests':total_tests,'maximum_table_membership_tests':88,'attachment_deletions':0,'projected_raw_modifications':0,'fresh_holdout_values_read':0,'global_solver_invocations':0,'portfolio_replays':0,'component_solution_attempts':0,'action_tests':0,'automorphism_tests':0,'group_searches':0,'group_closure_computation':0,'new_solver_mechanisms':0,'new_carrier_mechanisms':0,'new_adapters':0,'new_quotients':0},'scientific_firewall':firewall()}
if __name__=='__main__':print(json.dumps(main(),sort_keys=True,separators=(',',':')))
