from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_L3_PARTITION_NOVELTY_TEN_SOURCE_TRANSFER_SYNTHESIS_PREREGISTRATION_2026-09-17.json'
REVIEW=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_L3_PARTITION_NOVELTY_TEN_SOURCE_TRANSFER_SYNTHESIS_PREREGISTRATION_REVIEW_2026-09-17.json'
ORIGINAL=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_L3_WL3_EXISTING_SIGNATURE_EQUIVALENCE_AUDIT_RESULT_2026-09-17.json'
BLIND=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_UNSEEN_FIVE_SOURCE_L3_VS_S0_S3_PARTITION_RELATION_MATRIX_RESULT_2026-09-17.json'
EXPECTED={
 PREREG:'b14aafe45b9140305601aaca327e890a90b5cf68',
 REVIEW:'ffda46d2443f41bba400b2b2ac7966b08a72e512',
 ORIGINAL:'971d7d98a86471e88bf33336da215171b2f8cdfe',
 BLIND:'24da02d77596a640fcb782f8aa12f088319c757b'}
ORIGINAL_ORDER=('UF20_01','UF20_02','UF20_03','UF20_04','UF20_05')
BLIND_ORDER=('UF20_06','UF20_07','UF20_08','UF20_09','UF20_010')
ALL_ORDER=ORIGINAL_ORDER+BLIND_ORDER
LABELS=('EQUAL','L3_STRICTLY_FINER_THAN_S3','S3_STRICTLY_FINER_THAN_L3','INCOMPARABLE')
ALIASES={
 'EQUAL':'EQUAL',
 'L3_STRICTLY_FINER_THAN_Sk':'L3_STRICTLY_FINER_THAN_S3',
 'Sk_STRICTLY_FINER_THAN_L3':'S3_STRICTLY_FINER_THAN_L3',
 'L3_STRICTLY_FINER_THAN_S3':'L3_STRICTLY_FINER_THAN_S3',
 'S3_STRICTLY_FINER_THAN_L3':'S3_STRICTLY_FINER_THAN_L3',
 'INCOMPARABLE':'INCOMPARABLE'}
ADDITIONAL={'L3_STRICTLY_FINER_THAN_S3','INCOMPARABLE'}

def blob(path:Path)->str:
 data=path.read_bytes();return hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()
def counts(labels:dict[str,str])->dict[str,int]:
 c=Counter(labels.values());return {k:int(c.get(k,0)) for k in LABELS}
def normalize(label:str)->str:
 if label not in ALIASES:raise ValueError(f'unrecognized frozen relation label: {label}')
 return ALIASES[label]
def guard()->dict[str,Any]:
 binds={str(p.relative_to(ROOT)):blob(p)==sha for p,sha in EXPECTED.items()}
 pre=json.loads(PREREG.read_text());review=json.loads(REVIEW.read_text())
 checks={
  'bindings':all(binds.values()),
  'prereg_status':pre.get('status')=='FROZEN_BEFORE_TRANSFER_COUNTS_ARE_SYNTHESIZED',
  'review_authorized':review.get('verdict')=='PASS_PREREGISTRATION_CLEAN__AUTHORIZED_TO_IMPLEMENT_AND_EXECUTE_ONCE',
  'canonical_labels_exact':tuple(pre['synthesis_contract']['canonical_labels'])==LABELS,
  'original_sources_exact':tuple(pre['pinned_results']['original_five_source_equivalence_audit']['sources'])==ORIGINAL_ORDER,
  'blind_sources_exact':tuple(pre['pinned_results']['blind_five_source_matrix']['sources'])==BLIND_ORDER,
  'no_partition_recomputation':pre['synthesis_contract']['no_partition_recomputation'] is True}
 return {'ok':all(checks.values()),'checks':checks,'bindings':binds}
def main()->dict[str,Any]:
 g=guard()
 if not g['ok']:return {'verdict':'HALT_FROZEN_RESULT_BINDING_FAILURE','source_guard':g,'scientific_firewall':firewall()}
 original=json.loads(ORIGINAL.read_text());blind=json.loads(BLIND.read_text())
 o_raw=original['stage_summary']['S3']['relations_by_source']
 b_raw={s:blind['relation_matrix'][s]['S3'] for s in BLIND_ORDER}
 if tuple(o_raw.keys())!=ORIGINAL_ORDER or tuple(b_raw.keys())!=BLIND_ORDER:
  return {'verdict':'HALT_TEN_SOURCE_COVERAGE_FAILURE','source_guard':g,'observed_original_sources':list(o_raw),'observed_blind_sources':list(b_raw),'scientific_firewall':firewall()}
 o={s:normalize(o_raw[s]) for s in ORIGINAL_ORDER};b={s:normalize(b_raw[s]) for s in BLIND_ORDER};combined={**o,**b}
 if tuple(combined.keys())!=ALL_ORDER or len(combined)!=10:
  return {'verdict':'HALT_TEN_SOURCE_COVERAGE_FAILURE','source_guard':g,'scientific_firewall':firewall()}
 oc=counts(o);bc=counts(b);cc=counts(combined)
 blind_additional=sum(bc[k] for k in ADDITIONAL)
 transfer=blind_additional>=1
 verdict='VERDICT_FIRST_BLIND_HOLDOUT_TRANSFER_EVIDENCE_PRESENT__STILL_SCOPED_NO_GENERALIZATION' if transfer else 'VERDICT_NO_FIRST_BLIND_HOLDOUT_TRANSFER_EVIDENCE__L3_NON_GENERALIZED_UNDER_CURRENT_EVIDENCE'
 return {
  'artifact_id':'JANUS-TRUMP-SATLIB-UF20-R000-R111-L3-PARTITION-NOVELTY-TEN-SOURCE-TRANSFER-SYNTHESIS-CANDIDATE-2026-09-17-v1.0',
  'authority':'DIAGNOSTIC_CROSS_RESULT_TRANSFER_SYNTHESIS_ONLY__NO_NEW_PARTITION_VALUE_FEATURE_GRAPH_STATISTIC_ACTION_TEST_GROUP_SEARCH_SOLVER_CARRIER_ADAPTER_OR_QUOTIENT',
  'verdict':verdict,
  'source_guard':g,
  'original_panel_labels':o,
  'blind_holdout_labels':b,
  'combined_ten_source_labels':combined,
  'original_panel_counts':oc,
  'blind_holdout_counts':bc,
  'combined_ten_source_counts':cc,
  'blind_additional_discrimination_count':blind_additional,
  'first_blind_holdout_transfer_evidence':transfer,
  'original_uf20_03_scoped_fact_preserved':o.get('UF20_03')=='L3_STRICTLY_FINER_THAN_S3',
  'resource_receipt':{'frozen_input_results':2,'sources':10,'relation_labels_read':10,'partition_recomputations':0,'solver_invocations':0,'portfolio_replays':0,'action_tests':0,'automorphism_tests':0,'group_searches':0,'group_closure_computation':0,'new_feature_definitions':0,'new_graph_statistics':0,'new_solver_mechanisms':0,'new_carrier_mechanisms':0,'new_adapters':0,'new_quotients':0},
  'scientific_firewall':firewall()}
def firewall():return {'P_VS_NP':'OPEN','GENERAL_SAT_IN_P':'NOT_PROVED','GENERAL_GT2_TRACTABILITY':'NOT_PROVED','CONNECTED_MIXED_CORE_SOLVED':'NO','L3_GENERALIZES':'NOT_PROVED','ZERO_OF_FIVE_BLIND_PROVES_IMPOSSIBILITY':False,'TRANSFER_COUNTS_ARE_POPULATION_FREQUENCY_ESTIMATE':False}
if __name__=='__main__':print(json.dumps(main(),sort_keys=True,separators=(',',':')))
