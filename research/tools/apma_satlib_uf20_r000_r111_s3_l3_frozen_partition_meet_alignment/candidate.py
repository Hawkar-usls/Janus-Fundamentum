from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from research.tools.apma_satlib_uf20_r000_r111_projected_core_replay import projection_identity
from research.tools.apma_satlib_uf20_r000_r111_projected_signature_ablation import replay as ablation
from research.tools.apma_satlib_uf20_r000_r111_residual_local_invariant_falsifier import candidate as frozen_falsifier

ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_S3_L3_FROZEN_PARTITION_MEET_ALIGNMENT_PREREGISTRATION_2026-09-17.json'
REVIEW=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_S3_L3_FROZEN_PARTITION_MEET_ALIGNMENT_PREREGISTRATION_REVIEW_2026-09-17.json'
EQUIV_RESULT=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_L3_WL3_EXISTING_SIGNATURE_EQUIVALENCE_AUDIT_RESULT_2026-09-17.json'
EXPECTED={
 PREREG:'01b7a1f2da7956c5bab2734c39cda2f9703fac07',
 REVIEW:'9980a3da4f5634d681f2394b032ac840ef13aac9',
 EQUIV_RESULT:'971d7d98a86471e88bf33336da215171b2f8cdfe',
 ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PROJECTED_CORE_EXISTING_SIGNATURE_ABLATION_REPLAY_RESULT_2026-09-16.json':'b7ba5bd772c3092e0436dde8bd717dc28985983c',
 ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_RESIDUAL_LOCAL_INVARIANT_FALSIFIER_RESULT_2026-09-16.json':'954893935bee1d46a77c5f635086e0e278b05fac',
 ROOT/'research/tools/apma_satlib_uf20_r000_r111_projected_signature_ablation/replay.py':'2edad57e6017cb34bf797313e4451c1ce014900b',
 ROOT/'research/tools/apma_satlib_uf20_r000_r111_residual_local_invariant_falsifier/candidate.py':'4ec02d6d42e6cad7d91f16b1acfdcbe51dbd65df',
 ROOT/'research/tools/apma_satlib_uf20_r000_r111_projected_core_replay/projection_identity.py':'2ef48e73974a5f43d3f4fb4809ebd0c09c0f5be4',
}
SOURCES={
 'UF20_01':(ROOT/'research/source_data/SATLIB_UF20_01_2026-09-16.cnf','8330041b292e0501f8d74c1b1d32ca96c4498864'),
 'UF20_02':(ROOT/'research/source_data/SATLIB_UF20_02_2026-09-16.cnf','f924caaef0d868bf62b1658e83e030ad8daee865'),
 'UF20_03':(ROOT/'research/source_data/SATLIB_UF20_03_2026-09-16.cnf','8f3d15154515457281f49201b843f2a7134dfa9f'),
 'UF20_04':(ROOT/'research/source_data/SATLIB_UF20_04_2026-09-16.cnf','34ced5c169f967b2dc44ef5e42f2ee2c924813e1'),
 'UF20_05':(ROOT/'research/source_data/SATLIB_UF20_05_2026-09-16.cnf','3b04eff26ee37bdd0bc21b1066486974f92a2c9b'),
}

def blob(p:Path)->str:
 d=p.read_bytes();return hashlib.sha1(f'blob {len(d)}\0'.encode()+d).hexdigest()
def csha(obj:Any)->str:return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()

def guard():
 bindings={str(p.relative_to(ROOT)):blob(p)==s for p,s in EXPECTED.items()};sources={n:blob(p)==s for n,(p,s) in SOURCES.items()}
 pre=json.loads(PREREG.read_text());review=json.loads(REVIEW.read_text())
 checks={'bindings':all(bindings.values()),'source_bindings':all(sources.values()),'prereg_status':pre.get('status')=='FROZEN_BEFORE_ANY_PARTITION_MEET_EXECUTION','review_authorized':review.get('verdict')=='PASS_PREREGISTRATION_CLEAN__AUTHORIZED_TO_IMPLEMENT_AND_EXECUTE_ONCE'}
 return {'ok':all(checks.values()),'checks':checks,'bindings':bindings,'source_bindings':sources}

def meet(p:list[list[int]],q:list[list[int]])->list[list[int]]:
 out=[]
 for a in p:
  sa=set(a)
  for b in q:
   x=sorted(sa.intersection(b))
   if x:out.append(x)
 out.sort(key=lambda c:(c[0],len(c),c));return out

def nontriv(p):return [c for c in p if len(c)>1]

def source_row(name,path,expected_raw):
 clauses=projection_identity.parse(path);raw,_=projection_identity.normalize_projection(name,clauses);raw_sha=csha(raw)
 if raw_sha!=expected_raw:return {'source':name,'status':'PROJECTED_RAW_BINDING_FAILURE','observed_raw_sha256':raw_sha}
 feats=ablation.features(raw,ablation.projected_clauses(path));s3=ablation.partition(feats,'S3')
 V,edges,l3sha=frozen_falsifier.source_scope_projection(name,path)
 if l3sha!=raw_sha:return {'source':name,'status':'FROZEN_PARTITION_RAW_DISAGREEMENT','s3_raw_sha256':raw_sha,'l3_raw_sha256':l3sha}
 l3sig=frozen_falsifier.l3(V,edges);l3,_=frozen_falsifier.partition(l3sig);m=meet(s3,l3)
 return {'source':name,'status':'AUDITED','raw_sha256':raw_sha,'S3_partition':s3,'S3_non_singleton_classes':nontriv(s3),'L3_partition':l3,'L3_non_singleton_classes':nontriv(l3),'meet_partition':m,'meet_partition_sha256':csha(m),'meet_non_singleton_classes':nontriv(m),'meet_all_singleton':all(len(c)==1 for c in m)}

def firewall():return {'P_VS_NP':'OPEN','GENERAL_SAT_IN_P':'NOT_PROVED','GENERAL_GT2_TRACTABILITY':'NOT_PROVED','CONNECTED_MIXED_CORE_SOLVED':'NO','MEET_IS_NEW_GENERAL_INVARIANT':False,'MEET_IMPLIES_HARDNESS':False,'MEET_IMPLIES_TRACTABILITY':False,'MEET_LICENSES_SOLVER':False,'NEW_SOLVER_MECHANISM_LICENSED':False,'NEW_CARRIER_MECHANISM_LICENSED':False}

def main():
 g=guard()
 if not g['ok']:return {'verdict':'HALT_BINDING_OR_PARTITION_RECOMPUTATION_DISAGREEMENT','source_guard':g,'scientific_firewall':firewall()}
 pre=json.loads(PREREG.read_text());eq=json.loads(EQUIV_RESULT.read_text());rows=[source_row(n,p,pre['frozen_projected_raw_sha256'][n]) for n,(p,_) in SOURCES.items()]
 if any(r['status']!='AUDITED' for r in rows):return {'verdict':'HALT_BINDING_OR_PARTITION_RECOMPUTATION_DISAGREEMENT','source_guard':g,'rows':rows,'scientific_firewall':firewall()}
 by={r['source']:r for r in rows};key=eq['key_partition_receipts'];receipt_ok=True
 receipt_ok &= by['UF20_01']['L3_non_singleton_classes']==key['UF20_01']['L3_non_singleton_classes'] and by['UF20_01']['S3_non_singleton_classes']==key['UF20_01']['S3_non_singleton_classes']
 receipt_ok &= by['UF20_03']['S3_non_singleton_classes']==key['UF20_03']['S3_non_singleton_classes'] and by['UF20_03']['L3_non_singleton_classes']==[]
 for n in ('UF20_02','UF20_04','UF20_05'):receipt_ok &= by[n]['S3_non_singleton_classes']==[] and by[n]['L3_non_singleton_classes']==[]
 if not receipt_ok:return {'verdict':'HALT_BINDING_OR_PARTITION_RECOMPUTATION_DISAGREEMENT','source_guard':g,'rows':rows,'scientific_firewall':firewall()}
 rule=pre['a_priori_alignment_test'];control=(by['UF20_01']['meet_non_singleton_classes']==[rule['UF20_01_expected_only_non_singleton_meet_class']]);panel=all(by[n]['meet_all_singleton'] for n in ('UF20_02','UF20_03','UF20_04','UF20_05'))
 verdict=rule['pass_verdict'] if control and panel else rule['fail_verdict']
 return {'artifact_id':'JANUS-TRUMP-SATLIB-UF20-R000-R111-S3-L3-FROZEN-PARTITION-MEET-ALIGNMENT-CANDIDATE-2026-09-17-v1.0','authority':'DIAGNOSTIC_EXISTING_PARTITION_MEET_ONLY__NO_NEW_FEATURE_SOLVER_CARRIER_ADAPTER_QUOTIENT_OR_GROUP_SEARCH','verdict':verdict,'source_guard':g,'frozen_partition_receipts_verified':receipt_ok,'control_alignment_pass':control,'panel_alignment_pass':panel,'rows':rows,'resource_receipt':{'source_count':5,'partition_meets':5,'full_assignment_cube_enumerations':0,'solver_invocations':0,'group_searches':0,'new_feature_definitions':0,'new_graph_statistics':0,'new_solver_mechanisms':0,'new_carrier_mechanisms':0,'new_adapters':0,'new_quotients':0,'budget_raise':False},'scientific_firewall':firewall()}
if __name__=='__main__':print(json.dumps(main(),sort_keys=True,separators=(',',':')))
