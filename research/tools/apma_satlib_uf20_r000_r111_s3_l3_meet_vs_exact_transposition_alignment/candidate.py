from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_S3_L3_MEET_VS_EXACT_TRANSPOSITION_ALIGNMENT_PREREGISTRATION_2026-09-17.json'
REVIEW=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_S3_L3_MEET_VS_EXACT_TRANSPOSITION_ALIGNMENT_PREREGISTRATION_REVIEW_2026-09-17.json'
MEET=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_S3_L3_FROZEN_PARTITION_MEET_ALIGNMENT_RESULT_2026-09-17.json'
SIGNED=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PROJECTED_CORE_SIGNED_RESIDUAL_EXACT_CERTIFICATE_RESULT_2026-09-16_v1.1.json'
SEALED=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PROJECTED_SIGNED_VS_SEALED_ORBIT_ALIGNMENT_RESULT_2026-09-16.json'
EXPECTED={
 PREREG:'4841a454d7804dc433e84dd2b2f96a486ea160f6',
 REVIEW:'f16879aba17c282b08f00cd8cee0c2a353d83eaa',
 MEET:'294525ee3a162c05100644245eff9afd0664431e',
 SIGNED:'1c2b7d35f970038616fa9f1decb20d67c88965f5',
 SEALED:'d20150284fef9926d828f9903a6b9f5c56c10b01'}
SOURCES=('UF20_01','UF20_02','UF20_03','UF20_04','UF20_05')

def blob(p:Path)->str:
 d=p.read_bytes();return hashlib.sha1(f'blob {len(d)}\0'.encode()+d).hexdigest()

def guard()->dict[str,Any]:
 bindings={str(p.relative_to(ROOT)):blob(p)==sha for p,sha in EXPECTED.items()}
 pre=json.loads(PREREG.read_text());review=json.loads(REVIEW.read_text())
 checks={
  'bindings':all(bindings.values()),
  'prereg_status':pre.get('status')=='FROZEN_BEFORE_ANY_CROSS_CERTIFICATE_ALIGNMENT_EXECUTION',
  'review_authorized':review.get('verdict')=='PASS_PREREGISTRATION_CLEAN__AUTHORIZED_TO_IMPLEMENT_AND_EXECUTE_ONCE',
  'sources_exact':tuple(pre.get('comparison_contract',{}).get('sources',()))==SOURCES}
 return {'ok':all(checks.values()),'checks':checks,'bindings':bindings}

def firewall():
 return {'P_VS_NP':'OPEN','GENERAL_SAT_IN_P':'NOT_PROVED','GENERAL_GT2_TRACTABILITY':'NOT_PROVED','CONNECTED_MIXED_CORE_SOLVED':'NO','ALIGNMENT_IMPLIES_HARDNESS':False,'ALIGNMENT_IMPLIES_TRACTABILITY':False,'MEET_IS_NEW_GENERAL_INVARIANT':False,'NEW_SOLVER_MECHANISM_LICENSED':False,'NEW_CARRIER_MECHANISM_LICENSED':False}

def main():
 g=guard()
 if not g['ok']:return {'verdict':'HALT_PINNED_AUTHORITY_OR_SCHEMA_DISAGREEMENT','source_guard':g,'scientific_firewall':firewall()}
 pre=json.loads(PREREG.read_text());meet=json.loads(MEET.read_text());signed=json.loads(SIGNED.read_text());sealed=json.loads(SEALED.read_text())
 try:
  meet_by={r['source']:r for r in meet['source_summary']};signed_by={r['source']:r for r in signed['source_receipt']}
  aw=sealed['aligned_witness'];panel_sealed=sealed['four_unadmitted_sources']
 except Exception:
  return {'verdict':'HALT_PINNED_AUTHORITY_OR_SCHEMA_DISAGREEMENT','source_guard':g,'scientific_firewall':firewall()}
 rows=[]
 for name in SOURCES:
  m=meet_by[name]['meet_non_singleton_classes'];s=signed_by[name];count=s['nonidentity_exact_signed_automorphism_count']
  if name=='UF20_01':
   w=s.get('unique_nonidentity_witness');pair=sorted({x for move in w['sigma_moves'] for x in move}) if w else None;eps=w['epsilon_flips'] if w else None
   sealed_cell=aw['sealed_orbit_cell']
   aligned=(m==[[7,10]] and count==1 and pair==[7,10] and eps==[] and sealed_cell==[7,10] and aw['signed_exact_pair']==[7,10] and aw['existing_exact_transposition_true_pair']==[7,10])
   rows.append({'source':name,'meet_non_singleton_classes':m,'signed_nonidentity_count':count,'signed_unique_pair':pair,'epsilon_flips':eps,'sealed_orbit_cell':sealed_cell,'alignment':'EXACT_FULL_ALIGNMENT' if aligned else 'MISMATCH','aligned':aligned})
  else:
   aligned=(m==[] and count==0 and name in panel_sealed['sources'] and panel_sealed['signed_nonidentity_automorphisms']==0 and panel_sealed['new_closure_from_signed_extension'] is False)
   rows.append({'source':name,'meet_non_singleton_classes':m,'signed_nonidentity_count':count,'sealed_panel_total_nonidentity':panel_sealed['signed_nonidentity_automorphisms'],'alignment':'EMPTY_VS_IDENTITY_ONLY_ALIGNMENT' if aligned else 'MISMATCH','aligned':aligned})
 expected=pre['a_priori_expected_alignment'];expect_ok=True
 for r in rows:
  expect_ok &= r['alignment']==expected[r['source']]['expected']
 all_aligned=all(r['aligned'] for r in rows) and expect_ok
 verdict=pre['a_priori_outcome_rules']['fully_aligned_verdict'] if all_aligned else pre['a_priori_outcome_rules']['mismatch_verdict']
 return {
  'artifact_id':'JANUS-TRUMP-SATLIB-UF20-R000-R111-S3-L3-MEET-VS-EXACT-TRANSPOSITION-ALIGNMENT-CANDIDATE-2026-09-17-v1.0',
  'authority':'DIAGNOSTIC_EXISTING_PARTITION_VS_EXISTING_EXACT_WITNESS_ALIGNMENT_ONLY__NO_NEW_FEATURE_ACTION_TEST_GROUP_SEARCH_SOLVER_CARRIER_ADAPTER_OR_QUOTIENT',
  'verdict':verdict,'source_guard':g,'rows':rows,'all_aligned':all_aligned,'no_new_explanatory_witness':all_aligned,
  'resource_receipt':{'sources_compared':5,'new_action_tests':0,'new_partition_computations':0,'solver_invocations':0,'portfolio_replays':0,'group_closure_computation':0,'group_searches':0,'new_feature_definitions':0,'new_graph_statistics':0,'new_solver_mechanisms':0,'new_carrier_mechanisms':0,'new_adapters':0,'new_quotients':0,'budget_raise':False},
  'scientific_firewall':firewall()}
if __name__=='__main__':print(json.dumps(main(),sort_keys=True,separators=(',',':')))
