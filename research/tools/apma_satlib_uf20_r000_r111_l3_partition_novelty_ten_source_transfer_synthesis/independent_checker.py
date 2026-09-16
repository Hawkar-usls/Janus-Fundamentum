from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_L3_PARTITION_NOVELTY_TEN_SOURCE_TRANSFER_SYNTHESIS_PREREGISTRATION_2026-09-17.json'
REVIEW=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_L3_PARTITION_NOVELTY_TEN_SOURCE_TRANSFER_SYNTHESIS_PREREGISTRATION_REVIEW_2026-09-17.json'
ORIGINAL=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_L3_WL3_EXISTING_SIGNATURE_EQUIVALENCE_AUDIT_RESULT_2026-09-17.json'
BLIND=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_UNSEEN_FIVE_SOURCE_L3_VS_S0_S3_PARTITION_RELATION_MATRIX_RESULT_2026-09-17.json'
EXPECTED={PREREG:'b14aafe45b9140305601aaca327e890a90b5cf68',REVIEW:'ffda46d2443f41bba400b2b2ac7966b08a72e512',ORIGINAL:'971d7d98a86471e88bf33336da215171b2f8cdfe',BLIND:'24da02d77596a640fcb782f8aa12f088319c757b'}
ORIGINAL_ORDER=('UF20_01','UF20_02','UF20_03','UF20_04','UF20_05')
BLIND_ORDER=('UF20_06','UF20_07','UF20_08','UF20_09','UF20_010')
ALL_ORDER=ORIGINAL_ORDER+BLIND_ORDER
LABELS=('EQUAL','L3_STRICTLY_FINER_THAN_S3','S3_STRICTLY_FINER_THAN_L3','INCOMPARABLE')
ALIASES={'EQUAL':'EQUAL','L3_STRICTLY_FINER_THAN_Sk':'L3_STRICTLY_FINER_THAN_S3','Sk_STRICTLY_FINER_THAN_L3':'S3_STRICTLY_FINER_THAN_L3','L3_STRICTLY_FINER_THAN_S3':'L3_STRICTLY_FINER_THAN_S3','S3_STRICTLY_FINER_THAN_L3':'S3_STRICTLY_FINER_THAN_L3','INCOMPARABLE':'INCOMPARABLE'}

def blob(path:Path)->str:
 data=path.read_bytes();return hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()
def normalize(label:str)->str:
 assert label in ALIASES,label;return ALIASES[label]
def count(labels:dict[str,str])->dict[str,int]:
 c=Counter(labels.values());return {k:int(c.get(k,0)) for k in LABELS}
def expected_payload():
 assert all(blob(p)==sha for p,sha in EXPECTED.items())
 pre=json.loads(PREREG.read_text());review=json.loads(REVIEW.read_text())
 assert pre['status']=='FROZEN_BEFORE_TRANSFER_COUNTS_ARE_SYNTHESIZED'
 assert review['verdict']=='PASS_PREREGISTRATION_CLEAN__AUTHORIZED_TO_IMPLEMENT_AND_EXECUTE_ONCE'
 original=json.loads(ORIGINAL.read_text());blind=json.loads(BLIND.read_text())
 o_raw=original['stage_summary']['S3']['relations_by_source'];assert tuple(o_raw)==ORIGINAL_ORDER
 b_raw={s:blind['relation_matrix'][s]['S3'] for s in BLIND_ORDER};assert tuple(b_raw)==BLIND_ORDER
 o={s:normalize(o_raw[s]) for s in ORIGINAL_ORDER};b={s:normalize(b_raw[s]) for s in BLIND_ORDER};combined={**o,**b};assert tuple(combined)==ALL_ORDER and len(combined)==10
 oc,bc,cc=count(o),count(b),count(combined)
 blind_additional=bc['L3_STRICTLY_FINER_THAN_S3']+bc['INCOMPARABLE'];transfer=blind_additional>=1
 verdict='VERDICT_FIRST_BLIND_HOLDOUT_TRANSFER_EVIDENCE_PRESENT__STILL_SCOPED_NO_GENERALIZATION' if transfer else 'VERDICT_NO_FIRST_BLIND_HOLDOUT_TRANSFER_EVIDENCE__L3_NON_GENERALIZED_UNDER_CURRENT_EVIDENCE'
 return o,b,combined,oc,bc,cc,blind_additional,transfer,verdict
def main(candidate_path:Path):
 c=json.loads(candidate_path.read_text().strip().splitlines()[-1]);o,b,combined,oc,bc,cc,blind_additional,transfer,verdict=expected_payload()
 assert c['original_panel_labels']==o and c['blind_holdout_labels']==b and c['combined_ten_source_labels']==combined
 assert c['original_panel_counts']==oc and c['blind_holdout_counts']==bc and c['combined_ten_source_counts']==cc
 assert c['blind_additional_discrimination_count']==blind_additional and c['first_blind_holdout_transfer_evidence']==transfer and c['verdict']==verdict
 assert c['original_uf20_03_scoped_fact_preserved'] is True
 rr=c['resource_receipt'];assert rr['frozen_input_results']==2 and rr['sources']==10 and rr['relation_labels_read']==10 and rr['partition_recomputations']==0
 assert rr['solver_invocations']==0 and rr['portfolio_replays']==0 and rr['action_tests']==0 and rr['automorphism_tests']==0 and rr['group_searches']==0 and rr['group_closure_computation']==0 and rr['new_feature_definitions']==0 and rr['new_graph_statistics']==0 and rr['new_solver_mechanisms']==0 and rr['new_carrier_mechanisms']==0 and rr['new_adapters']==0 and rr['new_quotients']==0
 sf=c['scientific_firewall'];assert sf['P_VS_NP']=='OPEN' and sf['GENERAL_SAT_IN_P']=='NOT_PROVED' and sf['CONNECTED_MIXED_CORE_SOLVED']=='NO' and sf['L3_GENERALIZES']=='NOT_PROVED'
 return {'verified':True,'candidate_imported':False,'verdict':verdict,'original_panel_counts':oc,'blind_holdout_counts':bc,'combined_ten_source_counts':cc,'blind_additional_discrimination_count':blind_additional,'first_blind_holdout_transfer_evidence':transfer,'sources_verified':10,'partition_recomputations':0}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--candidate-json',required=True);args=ap.parse_args();print(json.dumps(main(Path(args.candidate_json)),sort_keys=True,separators=(',',':')))
