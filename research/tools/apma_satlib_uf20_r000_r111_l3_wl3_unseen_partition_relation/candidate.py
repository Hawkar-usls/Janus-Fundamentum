from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from research.tools.apma_satlib_uf20_r000_r111_projected_core_replay import projection_identity
from research.tools.apma_satlib_uf20_r000_r111_projected_signature_ablation import replay as frozen_s3
from research.tools.apma_satlib_uf20_r000_r111_residual_local_invariant_falsifier import candidate as frozen_l3

ROOT = Path(__file__).resolve().parents[3]
PREREG = ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_L3_WL3_UNSEEN_PARTITION_RELATION_EXECUTION_PREREGISTRATION_2026-09-17.json'
REVIEW = ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_L3_WL3_UNSEEN_PARTITION_RELATION_EXECUTION_PREREGISTRATION_REVIEW_2026-09-17.json'
SOURCE_FREEZE = ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_UNSEEN_SOURCE_ACQUISITION_FREEZE_RESULT_2026-09-17.json'
SELECTION = ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_L3_WL3_UNSEEN_SOURCE_EXTENSION_SELECTION_PREREGISTRATION_2026-09-17.json'
EXPECTED = {
    PREREG:'3a7078d1787126df42faa183784e751cf00d2aa5',
    REVIEW:'c63ea31d65b4d26449fb6591077df620eef0151b',
    SOURCE_FREEZE:'ae26cc59e754f73476bfb903331f1c4c1d946bdc',
    SELECTION:'9679bed3017df016002a10aa45ba249df198baa4',
    ROOT/'research/tools/apma_satlib_uf20_r000_r111_projected_signature_ablation/replay.py':'2edad57e6017cb34bf797313e4451c1ce014900b',
    ROOT/'research/tools/apma_satlib_uf20_r000_r111_residual_local_invariant_falsifier/candidate.py':'4ec02d6d42e6cad7d91f16b1acfdcbe51dbd65df',
    ROOT/'research/tools/apma_satlib_uf20_r000_r111_projected_core_replay/projection_identity.py':'2ef48e73974a5f43d3f4fb4809ebd0c09c0f5be4',
}
ORDER=('UF20_06','UF20_07','UF20_08','UF20_09','UF20_010')
SOURCES={
 'UF20_06':ROOT/'research/source_data/SATLIB_UF20_06_2026-09-17.cnf',
 'UF20_07':ROOT/'research/source_data/SATLIB_UF20_07_2026-09-17.cnf',
 'UF20_08':ROOT/'research/source_data/SATLIB_UF20_08_2026-09-17.cnf',
 'UF20_09':ROOT/'research/source_data/SATLIB_UF20_09_2026-09-17.cnf',
 'UF20_010':ROOT/'research/source_data/SATLIB_UF20_010_2026-09-17.cnf',
}


def blob(path:Path)->str:
    data=path.read_bytes();return hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()

def csha(obj:Any)->str:
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()

def formula_sha(clauses:list[tuple[int,int,int]])->str:
    data=''.join(' '.join(str(x) for x in c)+' 0\n' for c in clauses).encode('ascii')
    return hashlib.sha256(data).hexdigest()

def refines(p:list[list[int]],q:list[list[int]])->bool:
    qsets=[set(c) for c in q]
    return all(any(set(c)<=d for d in qsets) for c in p)

def relation(l3:list[list[int]],s3:list[list[int]])->dict[str,Any]:
    a=refines(l3,s3);b=refines(s3,l3)
    if a and b:label='EQUAL'
    elif a:label='L3_STRICTLY_FINER_THAN_S3'
    elif b:label='S3_STRICTLY_FINER_THAN_L3'
    else:label='INCOMPARABLE'
    return {'L3_refines_S3':a,'S3_refines_L3':b,'relation':label}

def guard()->dict[str,Any]:
    pre=json.loads(PREREG.read_text()); review=json.loads(REVIEW.read_text()); freeze=json.loads(SOURCE_FREEZE.read_text())
    binds={str(p.relative_to(ROOT)):blob(p)==sha for p,sha in EXPECTED.items()}
    source_binds={n:blob(SOURCES[n])==pre['bound_sources'][n]['git_blob'] for n in ORDER}
    canonical_binds={}
    for n in ORDER:
        clauses=projection_identity.parse(SOURCES[n])
        canonical_binds[n]=formula_sha(clauses)==pre['bound_sources'][n]['canonical_formula_sha256']
    checks={
      'authority_bindings':all(binds.values()),'source_git_blob_bindings':all(source_binds.values()),'canonical_formula_bindings':all(canonical_binds.values()),
      'prereg_status':pre.get('status')=='FROZEN_BEFORE_ANY_UNSEEN_PROJECTED_L3_OR_S3_VALUE_COMPUTATION',
      'review_authorized':review.get('verdict')=='PASS_PREREGISTRATION_CLEAN__AUTHORIZED_TO_IMPLEMENT_AND_EXECUTE_ONCE',
      'source_freeze_pass':freeze.get('verdict')=='PASS_UNSEEN_SOURCE_ACQUISITION_AND_DUAL_MIRROR_FORMULA_FREEZE',
      'sources_exact':tuple(pre.get('bound_sources',{}).keys())==ORDER,
    }
    return {'ok':all(checks.values()),'checks':checks,'bindings':binds,'source_git_blob_bindings':source_binds,'canonical_formula_bindings':canonical_binds}

def one(name:str,path:Path)->dict[str,Any]:
    clauses=projection_identity.parse(path)
    raw,ordinals=projection_identity.normalize_projection(name,clauses)
    raw_sha=csha(raw)
    selected=[c for c in clauses if projection_identity.rid(c) in {'000','111'}]
    r000=sum(projection_identity.rid(c)=='000' for c in selected);r111=sum(projection_identity.rid(c)=='111' for c in selected)
    feats=frozen_s3.features(raw,selected)
    s3=frozen_s3.partition(feats,'S3')
    V,edges,l3_raw_sha=frozen_l3.source_scope_projection(name,path)
    if l3_raw_sha!=raw_sha or V!=raw['variables']:
        return {'source':name,'status':'HALT_FROZEN_IMPLEMENTATION_PROJECTION_DISAGREEMENT','candidate_raw_sha256':raw_sha,'l3_raw_sha256':l3_raw_sha}
    l3sig=frozen_l3.l3(V,edges);l3,l3map=frozen_l3.partition(l3sig)
    cmp=relation(l3,s3)
    return {
      'source':name,'status':'AUDITED','projected_raw_sha256':raw_sha,'projected_variables':raw['variables'],'projected_variable_count':len(raw['variables']),
      'projected_constraint_count':len(raw['constraints']),'selected_clause_ordinals':ordinals,'R000_count':r000,'R111_count':r111,
      'L3_partition':l3,'L3_partition_sha256':csha(l3),'L3_signature_map_sha256':l3map,
      'S3_partition':s3,'S3_partition_sha256':csha(s3),**cmp,
    }
def firewall():
    return {'P_VS_NP':'OPEN','GENERAL_SAT_IN_P':'NOT_PROVED','GENERAL_GT2_TRACTABILITY':'NOT_PROVED','CONNECTED_MIXED_CORE_SOLVED':'NO','L3_GENERALIZES':'NOT_PROVED','PARTITION_DIFFERENCE_IMPLIES_HARDNESS':False,'PARTITION_DIFFERENCE_IMPLIES_TRACTABILITY':False,'NEW_SOLVER_MECHANISM_LICENSED':False,'NEW_CARRIER_MECHANISM_LICENSED':False}
def main()->dict[str,Any]:
    g=guard()
    if not g['ok']:return {'verdict':'HALT_BINDING_OR_SOURCE_HASH_FAILURE','source_guard':g,'scientific_firewall':firewall()}
    pre=json.loads(PREREG.read_text());rows=[one(n,SOURCES[n]) for n in ORDER]
    if any(r.get('status')!='AUDITED' for r in rows):return {'verdict':'HALT_FROZEN_IMPLEMENTATION_PROJECTION_DISAGREEMENT','source_guard':g,'rows':rows,'scientific_firewall':firewall()}
    allowed=set(pre['comparison_contract']['labels'])
    if any(r['relation'] not in allowed for r in rows):return {'verdict':'HALT_PARTITION_RELATION_LABEL_FAILURE','rows':rows,'scientific_firewall':firewall()}
    non_equal=[r['source'] for r in rows if r['relation']!='EQUAL']
    repeat=bool(non_equal)
    verdict='PASS_SCOPED_UNSEEN_REPEAT_EVIDENCE_L3_VS_S3_PARTITION_DIFFERENCE' if repeat else 'PASS_UNSEEN_HOLDOUT_ALL_L3_S3_PARTITIONS_EQUAL__NO_REPEAT_EVIDENCE_ON_THIS_HOLDOUT'
    return {
      'artifact_id':'JANUS-TRUMP-SATLIB-UF20-R000-R111-L3-WL3-UNSEEN-PARTITION-RELATION-CANDIDATE-2026-09-17-v1.0',
      'authority':'DIAGNOSTIC_ONE_SHOT_UNSEEN_PARTITION_RELATION_FALSIFIER_ONLY__NO_SOLVER_ACTION_TEST_GROUP_SEARCH_CARRIER_ADAPTER_OR_QUOTIENT',
      'verdict':verdict,'source_guard':g,'rows':rows,'non_equal_sources':non_equal,'scoped_repeat_evidence':repeat,
      'resource_receipt':{'sources':5,'partition_comparisons':5,'solver_invocations':0,'portfolio_replays':0,'action_tests':0,'group_searches':0,'group_closure_computation':0,'new_feature_definitions':0,'new_graph_statistics':0,'new_solver_mechanisms':0,'new_carrier_mechanisms':0,'new_adapters':0,'new_quotients':0,'budget_raise':False},
      'scientific_firewall':firewall()}
if __name__=='__main__':print(json.dumps(main(),sort_keys=True,separators=(',',':')))
