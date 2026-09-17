from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from research.tools.apma_satlib_uf20_r000_r111_projected_core_replay import projection_identity

ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_RAW_BOUND_PENDANT_EXISTENTIAL_BOUNDARY_PROJECTION_PREREGISTRATION_2026-09-17.json'
REVIEW=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_RAW_BOUND_PENDANT_EXISTENTIAL_BOUNDARY_PROJECTION_PREREGISTRATION_REVIEW_2026-09-17.json'
PARENT=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_RAW_BOUND_D2_D3_WITNESS_RECONSTRUCTION_RESULT_2026-09-17.json'
PROJECTION=ROOT/'research/tools/apma_satlib_uf20_r000_r111_projected_core_replay/projection_identity.py'
EXPECTED={PREREG:'49ae9b34872eae3fdfd31a49f85defb7df7d9fa8',REVIEW:'ecbe8a188f62c434b4436035fde30043c8c474c7',PARENT:'d91e82fa2e558bb2926cc42b5f4368af51ae9c10',PROJECTION:'2ef48e73974a5f43d3f4fb4809ebd0c09c0f5be4'}
ORDER=('UF20_02','UF20_03','UF20_04','UF20_05')
SOURCES={
 'UF20_02':(ROOT/'research/source_data/SATLIB_UF20_02_2026-09-16.cnf','f924caaef0d868bf62b1658e83e030ad8daee865','cc181d11871a9907cd5024ef5f0951cb29b32c4ed378e06c48f432e20be580e6'),
 'UF20_03':(ROOT/'research/source_data/SATLIB_UF20_03_2026-09-16.cnf','8f3d15154515457281f49201b843f2a7134dfa9f','30beb0c870105dfbbf017c067298f3295fcb555130e045242fdacea9259eb97d'),
 'UF20_04':(ROOT/'research/source_data/SATLIB_UF20_04_2026-09-16.cnf','34ced5c169f967b2dc44ef5e42f2ee2c924813e1','db98a7a25397a7178df02e16e9f593fde432f9b07d3aa14b44d67dcd051069f3'),
 'UF20_05':(ROOT/'research/source_data/SATLIB_UF20_05_2026-09-16.cnf','3b04eff26ee37bdd0bc21b1066486974f92a2c9b','fd9c0c19089daf08e549ff3ab63c0c7203b61c03cce7c4bcce0778ca2fe4f3d6')}
BOUNDARY=((0,0),(0,1),(1,0),(1,1)); LEAF=(0,1)

def blob(p:Path)->str:
 d=p.read_bytes();return hashlib.sha1(f'blob {len(d)}\0'.encode()+d).hexdigest()
def csha(o:Any)->str:return hashlib.sha256(json.dumps(o,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def scope_tuple(scope,leaf,gateway,b,z):
 a={leaf:z,gateway[0]:b[0],gateway[1]:b[1]};return tuple(int(a[int(v)]) for v in scope)
def one(raw,m):
 byid={r['id']:r for r in raw['constraints']};cid=m['constraint_id'];assert cid in byid;c=byid[cid]
 scope=[int(v) for v in c['scope']];expected_scope=[int(v) for v in m['actual_scope']];leaf=int(m['leaf_variable']);gateway=sorted(int(v) for v in m['gateway_pair'])
 assert scope==expected_scope and set(scope)==set([leaf]+gateway) and len(scope)==3
 occ=sum(leaf in [int(v) for v in r['scope']] for r in raw['constraints'])
 allowed={tuple(int(x) for x in t) for t in c['allowed']};checks=[];rel=[];witness={};tests=0
 for b in BOUNDARY:
  trials=[];first=None
  for z in LEAF:
   ft=scope_tuple(scope,leaf,gateway,b,z);ok=ft in allowed;tests+=1;trials.append({'leaf_value':z,'full_scope_tuple':list(ft),'allowed':ok})
   if ok and first is None:first=z
  accepted=first is not None;checks.append({'boundary_tuple':list(b),'trials':trials,'accepted':accepted,'canonical_leaf_witness':first})
  if accepted:rel.append(list(b));witness[''.join(map(str,b))]=first
 card=len(rel);out='UNIVERSAL_BOUNDARY_RELATION_4_OF_4' if card==4 else 'PROPER_NONEMPTY_BOUNDARY_RELATION' if card else 'EMPTY_BOUNDARY_RELATION'
 return {'constraint_id':cid,'actual_scope':scope,'leaf_variable':leaf,'gateway_pair':gateway,'leaf_projected_constraint_occurrence_count':occ,'allowed_table_sha256':csha({'scope':scope,'allowed':c['allowed']}),'boundary_checks':checks,'boundary_relation':rel,'boundary_relation_cardinality':card,'canonical_reconstruction_witnesses':witness,'membership_tests':tests,'outcome':out}
def firewall():return {'P_VS_NP':'OPEN','GENERAL_SAT_IN_P':'NOT_PROVED','GENERAL_GT2_TRACTABILITY':'NOT_PROVED','CONNECTED_MIXED_CORE_SOLVED':'NO','LOCAL_BOUNDARY_TRANSPARENCY_IMPLIES_GLOBAL_TRACTABILITY':False,'LOCAL_BOUNDARY_TRANSPARENCY_IMPLIES_HARDNESS':False}
def main():
 binds={str(p.relative_to(ROOT)):blob(p)==h for p,h in EXPECTED.items()};sb={n:blob(p)==h for n,(p,h,_) in SOURCES.items()};pre=json.loads(PREREG.read_text());rev=json.loads(REVIEW.read_text());parent=json.loads(PARENT.read_text());maps={r['source']:r['mappings'] for r in parent['source_receipts']}
 checks={'bindings':all(binds.values()),'source_bindings':all(sb.values()),'parent_verdict':parent.get('verdict')=='COMMON_FOUR_EXACT_RAW_BOUND_ALIGNMENT','review_authorized':rev.get('verdict')=='PASS_PREREGISTRATION_CLEAN__AUTHORIZED_TO_IMPLEMENT_AND_EXECUTE_ONCE','attachment_count':sum(len(maps[n]) for n in ORDER)==11,'old_alignment_forbidden':pre['target_scope']['old_alignment_rows_may_be_used'] is False}
 guard={'ok':all(checks.values()),'checks':checks,'bindings':binds,'source_bindings':sb}
 if not guard['ok']:return {'verdict':'HALT_FROZEN_AUTHORITY_OR_SOURCE_BINDING_FAILURE','source_guard':guard,'scientific_firewall':firewall()}
 rows=[]
 for name in ORDER:
  path,_,expected_raw=SOURCES[name];raw,_=projection_identity.normalize_projection(name,projection_identity.parse(path));rawsha=csha(raw)
  if rawsha!=expected_raw:return {'verdict':'HALT_PROJECTED_RAW_BINDING_FAILURE','source':name,'observed':rawsha,'expected':expected_raw,'source_guard':guard,'scientific_firewall':firewall()}
  rows.append({'source':name,'projected_raw_sha256':rawsha,'attachments':[one(raw,m) for m in maps[name]]})
 aa=[a for r in rows for a in r['attachments']];out=Counter(a['outcome'] for a in aa)
 overall='AT_LEAST_ONE_EMPTY' if out['EMPTY_BOUNDARY_RELATION'] else 'ALL_ELEVEN_UNIVERSAL' if out['UNIVERSAL_BOUNDARY_RELATION_4_OF_4']==11 else 'MIXED_OR_PROPER'
 unique=all(a['leaf_projected_constraint_occurrence_count']==1 for a in aa);univ=all(a['boundary_relation_cardinality']==4 for a in aa);theorem=overall=='ALL_ELEVEN_UNIVERSAL' and unique and univ
 return {'artifact_id':'JANUS-TRUMP-SATLIB-UF20-R000-R111-RAW-BOUND-PENDANT-EXISTENTIAL-BOUNDARY-PROJECTION-CANDIDATE-2026-09-17-v1.0','authority':'DIAGNOSTIC_EXACT_LOCAL_EXISTENTIAL_BOUNDARY_RELATION_AUDIT_ONLY__CORRECTED_RAW_BOUND_LINEAGE','verdict':overall,'source_guard':guard,'rows':rows,'outcome_counts':{k:int(out.get(k,0)) for k in ('UNIVERSAL_BOUNDARY_RELATION_4_OF_4','PROPER_NONEMPTY_BOUNDARY_RELATION','EMPTY_BOUNDARY_RELATION')},'local_semantics_theorem':{'applicable':overall=='ALL_ELEVEN_UNIVERSAL','all_leaf_unique_occurrence_premises_verified':unique,'all_boundary_relations_universal_verified':univ,'symbolic_projection_equivalence_verified':theorem,'statement':'FOR_EACH_TARGET_ATTACHMENT_F=C(x,u,v)_AND_H(Y),x_NOT_IN_VARS(H),UNIVERSAL_EXISTS_x_C_IMPLIES_FOR_EVERY_y:EXISTS_x_F(x,y)_IFF_H(y)','deletion_applied':False},'resource_receipt':{'attachments':len(aa),'boundary_assignments':len(aa)*4,'table_membership_tests':sum(a['membership_tests'] for a in aa),'maximum_table_membership_tests':88,'superseded_old_alignment_rows_read':0,'attachment_deletions':0,'projected_raw_modifications':0,'fresh_holdout_values_read':0,'solver_invocations':0,'portfolio_replays':0,'component_solution_attempts':0,'action_tests':0,'automorphism_tests':0,'group_searches':0},'scientific_firewall':firewall()}
if __name__=='__main__':print(json.dumps(main(),sort_keys=True,separators=(',',':')))
