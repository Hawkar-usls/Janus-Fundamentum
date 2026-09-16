from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from research.tools.apma_satlib_uf20_r000_r111_projected_core_replay import projection_identity
from research.tools.apma_satlib_uf20_r000_r111_projected_signature_ablation import replay as frozen_signatures
from research.tools.apma_satlib_uf20_r000_r111_residual_local_invariant_falsifier import candidate as frozen_l3

ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_UNSEEN_FIVE_SOURCE_L3_VS_S0_S3_PARTITION_RELATION_MATRIX_PREREGISTRATION_2026-09-17.json'
REVIEW=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_UNSEEN_FIVE_SOURCE_L3_VS_S0_S3_PARTITION_RELATION_MATRIX_PREREGISTRATION_REVIEW_2026-09-17.json'
LOCALIZATION=ROOT/'research/TRUMP_SATLIB_UF20_06_L3_COLLISION_EXISTING_S0_S3_COMPONENT_LOCALIZATION_RESULT_2026-09-17.json'
BLIND=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_L3_WL3_UNSEEN_PARTITION_RELATION_RESULT_2026-09-17.json'
EXPECTED={
 PREREG:'49183b8530f34e1eb84483f797e4760e5a9f85cd',
 REVIEW:'d3fe6839f430011ea5db96e3fdc9617aefd78891',
 LOCALIZATION:'2189b85416a1495d090e90768a55e1fcb1746a25',
 BLIND:'222d227e491df0a4ff03257d3f52a6e8be3cb6d9',
 ROOT/'research/tools/apma_satlib_uf20_r000_r111_projected_signature_ablation/replay.py':'2edad57e6017cb34bf797313e4451c1ce014900b',
 ROOT/'research/tools/apma_satlib_uf20_r000_r111_residual_local_invariant_falsifier/candidate.py':'4ec02d6d42e6cad7d91f16b1acfdcbe51dbd65df',
 ROOT/'research/tools/apma_satlib_uf20_r000_r111_projected_core_replay/projection_identity.py':'2ef48e73974a5f43d3f4fb4809ebd0c09c0f5be4'}
ORDER=('UF20_06','UF20_07','UF20_08','UF20_09','UF20_010')
STAGES=('S0','S1','S2','S3')
SOURCES={
 'UF20_06':ROOT/'research/source_data/SATLIB_UF20_06_2026-09-17.cnf',
 'UF20_07':ROOT/'research/source_data/SATLIB_UF20_07_2026-09-17.cnf',
 'UF20_08':ROOT/'research/source_data/SATLIB_UF20_08_2026-09-17.cnf',
 'UF20_09':ROOT/'research/source_data/SATLIB_UF20_09_2026-09-17.cnf',
 'UF20_010':ROOT/'research/source_data/SATLIB_UF20_010_2026-09-17.cnf'}

def blob(p:Path)->str:
 d=p.read_bytes();return hashlib.sha1(f'blob {len(d)}\0'.encode()+d).hexdigest()
def csha(obj:Any)->str:return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def formula_sha(clauses)->str:return hashlib.sha256(''.join(' '.join(map(str,c))+' 0\n' for c in clauses).encode('ascii')).hexdigest()
def refines(p:list[list[int]],q:list[list[int]])->bool:
 qsets=[set(c) for c in q];return all(any(set(c)<=d for d in qsets) for c in p)
def compare(l3:list[list[int]],sk:list[list[int]])->dict[str,Any]:
 a=refines(l3,sk);b=refines(sk,l3)
 if a and b:lab='EQUAL'
 elif a:lab='L3_STRICTLY_FINER_THAN_Sk'
 elif b:lab='Sk_STRICTLY_FINER_THAN_L3'
 else:lab='INCOMPARABLE'
 return {'L3_refines_stage':a,'stage_refines_L3':b,'relation':lab}
def guard()->dict[str,Any]:
 pre=json.loads(PREREG.read_text());review=json.loads(REVIEW.read_text())
 binds={str(p.relative_to(ROOT)):blob(p)==sha for p,sha in EXPECTED.items()}
 source_blobs={n:blob(SOURCES[n])==pre['bound_sources'][n]['git_blob'] for n in ORDER}
 canonical={n:formula_sha(projection_identity.parse(SOURCES[n]))==pre['bound_sources'][n]['canonical_formula_sha256'] for n in ORDER}
 checks={'authority_bindings':all(binds.values()),'source_git_blob_bindings':all(source_blobs.values()),'canonical_formula_bindings':all(canonical.values()),'prereg_status':pre.get('status')=='FROZEN_BEFORE_ANY_UNSEEN_S0_S1_S2_PARTITION_RELATION_VALUE_COMPUTATION','review_authorized':review.get('verdict')=='PASS_PREREGISTRATION_CLEAN__AUTHORIZED_TO_IMPLEMENT_AND_EXECUTE_ONCE','source_order':tuple(pre.get('bound_sources',{}).keys())==ORDER,'stage_order':tuple(pre.get('stages',()))==STAGES,'comparison_count':pre.get('comparison_count')==20}
 return {'ok':all(checks.values()),'checks':checks,'bindings':binds,'source_git_blob_bindings':source_blobs,'canonical_formula_bindings':canonical}
def one(name:str,path:Path,pre:dict[str,Any])->dict[str,Any]:
 clauses=projection_identity.parse(path);raw,_=projection_identity.normalize_projection(name,clauses);raw_sha=csha(raw)
 if raw_sha!=pre['bound_sources'][name]['projected_raw_sha256']:
  return {'source':name,'status':'HALT_PROJECTED_RAW_BINDING_FAILURE','projected_raw_sha256':raw_sha}
 selected=frozen_signatures.projected_clauses(path);feats=frozen_signatures.features(raw,selected)
 stage_partitions={s:frozen_signatures.partition(feats,s) for s in STAGES}
 V,edges,l3_raw=frozen_l3.source_scope_projection(name,path)
 if l3_raw!=raw_sha or V!=raw['variables']:
  return {'source':name,'status':'HALT_FROZEN_IMPLEMENTATION_PROJECTION_DISAGREEMENT','projected_raw_sha256':raw_sha,'l3_raw_sha256':l3_raw}
 l3sig=frozen_l3.l3(V,edges);l3_partition,_=frozen_l3.partition(l3sig)
 relations={s:compare(l3_partition,stage_partitions[s]) for s in STAGES}
 return {'source':name,'status':'AUDITED','projected_raw_sha256':raw_sha,'projected_variable_count':len(raw['variables']),'projected_constraint_count':len(raw['constraints']),'L3_partition':l3_partition,'L3_partition_sha256':csha(l3_partition),'stage_partitions':stage_partitions,'stage_partition_sha256':{s:csha(stage_partitions[s]) for s in STAGES},'relations':relations}
def firewall():return {'P_VS_NP':'OPEN','GENERAL_SAT_IN_P':'NOT_PROVED','GENERAL_GT2_TRACTABILITY':'NOT_PROVED','CONNECTED_MIXED_CORE_SOLVED':'NO','L3_GENERALIZES':'NOT_PROVED','PARTITION_MATRIX_IMPLIES_HARDNESS':False,'PARTITION_MATRIX_IMPLIES_TRACTABILITY':False,'NEW_SOLVER_MECHANISM_LICENSED':False,'NEW_CARRIER_MECHANISM_LICENSED':False}
def main()->dict[str,Any]:
 g=guard()
 if not g['ok']:return {'verdict':'HALT_AUTHORITY_OR_SOURCE_BINDING_FAILURE','source_guard':g,'scientific_firewall':firewall()}
 pre=json.loads(PREREG.read_text());rows=[one(n,SOURCES[n],pre) for n in ORDER]
 if any(r.get('status')!='AUDITED' for r in rows):return {'verdict':'HALT_PROJECTED_RAW_OR_IMPLEMENTATION_BINDING_FAILURE','source_guard':g,'rows':rows,'scientific_firewall':firewall()}
 allowed=set(pre['comparison_contract']['labels'])
 comparisons=sum(len(r['relations']) for r in rows)
 if comparisons!=20 or any(x['relation'] not in allowed for r in rows for x in r['relations'].values()):return {'verdict':'HALT_PARTITION_RELATION_MATRIX_LABEL_FAILURE','rows':rows,'scientific_firewall':firewall()}
 additional=[r['source'] for r in rows if r['relations']['S3']['relation'] in {'L3_STRICTLY_FINER_THAN_Sk','INCOMPARABLE'}]
 verdict='PASS_SCOPED_UNSEEN_L3_ADDITIONAL_DISCRIMINATION_BEYOND_S3_PRESENT' if additional else 'PASS_UNSEEN_HOLDOUT_NO_L3_ADDITIONAL_DISCRIMINATION_BEYOND_S3'
 return {'artifact_id':'JANUS-TRUMP-SATLIB-UF20-R000-R111-UNSEEN-FIVE-SOURCE-L3-VS-S0-S3-PARTITION-RELATION-MATRIX-CANDIDATE-2026-09-17-v1.0','authority':'DIAGNOSTIC_EXISTING_PARTITION_RELATION_MATRIX_ONLY__NO_NEW_FEATURE_GRAPH_STATISTIC_ACTION_TEST_GROUP_SEARCH_SOLVER_CARRIER_ADAPTER_OR_QUOTIENT','verdict':verdict,'source_guard':g,'rows':rows,'s3_additional_discrimination_sources':additional,'resource_receipt':{'sources':5,'existing_stages':4,'partition_comparisons':comparisons,'solver_invocations':0,'portfolio_replays':0,'action_tests':0,'automorphism_tests':0,'group_searches':0,'group_closure_computation':0,'new_feature_definitions':0,'new_graph_statistics':0,'new_solver_mechanisms':0,'new_carrier_mechanisms':0,'new_adapters':0,'new_quotients':0,'budget_raise':False},'scientific_firewall':firewall()}
if __name__=='__main__':print(json.dumps(main(),sort_keys=True,separators=(',',':')))
