from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from research.tools.apma_satlib_uf20_r000_r111_projected_core_replay import projection_identity
from research.tools.apma_satlib_uf20_r000_r111_projected_signature_ablation import replay as frozen_signatures
from research.tools.apma_satlib_uf20_r000_r111_residual_local_invariant_falsifier import candidate as frozen_l3

ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/'research/TRUMP_SATLIB_UF20_06_L3_COLLISION_EXISTING_S0_S3_COMPONENT_LOCALIZATION_PREREGISTRATION_2026-09-17.json'
REVIEW=ROOT/'research/TRUMP_SATLIB_UF20_06_L3_COLLISION_EXISTING_S0_S3_COMPONENT_LOCALIZATION_PREREGISTRATION_REVIEW_2026-09-17.json'
UNSEEN=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_L3_WL3_UNSEEN_PARTITION_RELATION_RESULT_2026-09-17.json'
SOURCE=ROOT/'research/source_data/SATLIB_UF20_06_2026-09-17.cnf'
EXPECTED={
 PREREG:'21d3f7ceb52caff3ba0b5a3378942c811ddd9c86',
 REVIEW:'0e1a98ff1a469f1b62b99b2caf9e35b9e936279d',
 UNSEEN:'222d227e491df0a4ff03257d3f52a6e8be3cb6d9',
 SOURCE:'42d6feffa98dc1a213e019f28cf6bc7ddf94c0bf',
 ROOT/'research/tools/apma_satlib_uf20_r000_r111_projected_signature_ablation/replay.py':'2edad57e6017cb34bf797313e4451c1ce014900b',
 ROOT/'research/tools/apma_satlib_uf20_r000_r111_residual_local_invariant_falsifier/candidate.py':'4ec02d6d42e6cad7d91f16b1acfdcbe51dbd65df',
 ROOT/'research/tools/apma_satlib_uf20_r000_r111_projected_core_replay/projection_identity.py':'2ef48e73974a5f43d3f4fb4809ebd0c09c0f5be4'}
TARGET=(12,16)
LEVELS=('S0','S1','S2','S3')
COMPONENTS=('degree','positive_literal_count','negative_literal_count','eight_relation_incidence_vector','sorted_neighbor_degrees')

def blob(p:Path)->str:
 d=p.read_bytes();return hashlib.sha1(f'blob {len(d)}\0'.encode()+d).hexdigest()
def csha(obj:Any)->str:return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def formula_sha(clauses)->str:return hashlib.sha256(''.join(' '.join(map(str,c))+' 0\n' for c in clauses).encode('ascii')).hexdigest()
def components_from_s3(s3):
 return {'degree':s3[0],'positive_literal_count':s3[1],'negative_literal_count':s3[2],'eight_relation_incidence_vector':list(s3[3]),'sorted_neighbor_degrees':list(s3[4])}
def serialize_tuple(value):
 if isinstance(value,tuple):return [serialize_tuple(x) for x in value]
 return value
def first_split(values):
 for level in LEVELS:
  if values['12'][level]!=values['16'][level]:return level
 return None
def firewall():
 return {'P_VS_NP':'OPEN','GENERAL_SAT_IN_P':'NOT_PROVED','GENERAL_GT2_TRACTABILITY':'NOT_PROVED','CONNECTED_MIXED_CORE_SOLVED':'NO','L3_GENERALIZES':'NOT_PROVED','PAIR_12_16_AUTOMORPHISM_STATUS':'NOT_TESTED_AND_NOT_AUTHORIZED_HERE','LOCALIZATION_IMPLIES_HARDNESS':False,'LOCALIZATION_IMPLIES_TRACTABILITY':False}
def guard():
 binds={str(p.relative_to(ROOT)):blob(p)==sha for p,sha in EXPECTED.items()};pre=json.loads(PREREG.read_text());review=json.loads(REVIEW.read_text());unseen=json.loads(UNSEEN.read_text());clauses=projection_identity.parse(SOURCE)
 receipt=next(r for r in unseen['source_receipts'] if r['source']=='UF20_06')
 checks={
  'bindings':all(binds.values()),
  'prereg_status':pre.get('status')=='FROZEN_BEFORE_ANY_TARGET_SIGNATURE_VALUE_RECOMPUTATION',
  'review_authorized':review.get('verdict')=='PASS_PREREGISTRATION_CLEAN__AUTHORIZED_TO_IMPLEMENT_AND_EXECUTE_ONCE',
  'target_exact':tuple(pre['target']['variables'])==TARGET and pre['target']['frozen_L3_class']==[12,16],
  'source_formula_sha256':formula_sha(clauses)==pre['pinned_authorities']['UF20_06_source']['canonical_formula_sha256'],
  'unseen_receipt_pair':receipt['L3_partition']==[[1],[3],[4],[5],[6],[7],[8],[9],[10],[11],[12,16],[13],[14],[15],[17],[18],[19],[20]],
  'unseen_relation':receipt['relation']=='S3_STRICTLY_FINER_THAN_L3'}
 return {'ok':all(checks.values()),'checks':checks,'bindings':binds}
def main():
 g=guard()
 if not g['ok']:return {'verdict':'HALT_FROZEN_AUTHORITY_BINDING_FAILURE','source_guard':g,'scientific_firewall':firewall()}
 pre=json.loads(PREREG.read_text());clauses=projection_identity.parse(SOURCE);raw,_=projection_identity.normalize_projection('UF20_06',clauses);raw_sha=csha(raw)
 if raw_sha!=pre['pinned_authorities']['UF20_06_projected_raw_sha256']:
  return {'verdict':'HALT_FROZEN_PARTITION_OR_SIGNATURE_RECOMPUTATION_DISAGREEMENT','source_guard':g,'observed_projected_raw_sha256':raw_sha,'scientific_firewall':firewall()}
 selected=frozen_signatures.projected_clauses(SOURCE);feats=frozen_signatures.features(raw,selected)
 values={str(v):{level:serialize_tuple(feats[v][level]) for level in LEVELS} for v in TARGET}
 V,edges,l3_raw_sha=frozen_l3.source_scope_projection('UF20_06',SOURCE)
 l3sig=frozen_l3.l3(V,edges);l3_partition,_=frozen_l3.partition(l3sig);l3_class_12=next(c for c in l3_partition if 12 in c);l3_class_16=next(c for c in l3_partition if 16 in c)
 if l3_raw_sha!=raw_sha or l3_class_12!=[12,16] or l3_class_16!=[12,16]:
  return {'verdict':'HALT_FROZEN_PARTITION_OR_SIGNATURE_RECOMPUTATION_DISAGREEMENT','source_guard':g,'l3_raw_sha256':l3_raw_sha,'l3_class_12':l3_class_12,'l3_class_16':l3_class_16,'scientific_firewall':firewall()}
 comp={str(v):components_from_s3(feats[v]['S3']) for v in TARGET}
 equality={name:comp['12'][name]==comp['16'][name] for name in COMPONENTS}
 split=first_split(values)
 if split is None:
  verdict='HALT_FROZEN_PARTITION_OR_SIGNATURE_RECOMPUTATION_DISAGREEMENT';diff=[]
 else:
  stage_components={'S0':['degree'],'S1':['degree','positive_literal_count','negative_literal_count'],'S2':['degree','positive_literal_count','negative_literal_count','eight_relation_incidence_vector'],'S3':list(COMPONENTS)}[split]
  prev_components=[] if split=='S0' else {'S1':['degree'],'S2':['degree','positive_literal_count','negative_literal_count'],'S3':['degree','positive_literal_count','negative_literal_count','eight_relation_incidence_vector']}[split]
  diff=[name for name in stage_components if not equality[name] and name not in prev_components]
  if not diff:
   diff=[name for name in stage_components if not equality[name]]
  verdict={'S0':'FIRST_SPLIT_AT_S0_EXISTING_DEGREE_COMPONENT','S1':'FIRST_SPLIT_AT_S1_EXISTING_SIGN_COUNT_COMPONENTS','S2':'FIRST_SPLIT_AT_S2_EXISTING_RELATION_INCIDENCE_COMPONENT','S3':'FIRST_SPLIT_AT_S3_EXISTING_NEIGHBOR_DEGREE_COMPONENT'}[split]
 return {
  'artifact_id':'JANUS-TRUMP-SATLIB-UF20-06-L3-COLLISION-EXISTING-S0-S3-COMPONENT-LOCALIZATION-CANDIDATE-2026-09-17-v1.0',
  'authority':'DIAGNOSTIC_EXISTING_SIGNATURE_COMPONENT_LOCALIZATION_ONLY__NO_NEW_FEATURE_GRAPH_STATISTIC_ACTION_TEST_GROUP_SEARCH_SOLVER_CARRIER_ADAPTER_OR_QUOTIENT',
  'verdict':verdict,'source_guard':g,'projected_raw_sha256':raw_sha,'target_variables':[12,16],'frozen_L3_class_verified':[12,16],
  'signature_values':values,'component_values':comp,'component_equalities':equality,'first_split_stage':split,'first_split_differing_existing_components':diff,
  'resource_receipt':{'sources':1,'target_variables':2,'existing_signature_stages':4,'solver_invocations':0,'portfolio_replays':0,'action_tests':0,'automorphism_tests':0,'group_searches':0,'group_closure_computation':0,'new_feature_definitions':0,'new_graph_statistics':0,'new_solver_mechanisms':0,'new_carrier_mechanisms':0,'new_adapters':0,'new_quotients':0,'budget_raise':False},
  'scientific_firewall':firewall()}
if __name__=='__main__':print(json.dumps(main(),sort_keys=True,separators=(',',':')))
