from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_S3_L3_MEET_VS_EXACT_TRANSPOSITION_ALIGNMENT_PREREGISTRATION_2026-09-17.json'
REVIEW=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_S3_L3_MEET_VS_EXACT_TRANSPOSITION_ALIGNMENT_PREREGISTRATION_REVIEW_2026-09-17.json'
MEET=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_S3_L3_FROZEN_PARTITION_MEET_ALIGNMENT_RESULT_2026-09-17.json'
SIGNED=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PROJECTED_CORE_SIGNED_RESIDUAL_EXACT_CERTIFICATE_RESULT_2026-09-16_v1.1.json'
SEALED=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PROJECTED_SIGNED_VS_SEALED_ORBIT_ALIGNMENT_RESULT_2026-09-16.json'
EXPECTED={PREREG:'4841a454d7804dc433e84dd2b2f96a486ea160f6',REVIEW:'f16879aba17c282b08f00cd8cee0c2a353d83eaa',MEET:'294525ee3a162c05100644245eff9afd0664431e',SIGNED:'1c2b7d35f970038616fa9f1decb20d67c88965f5',SEALED:'d20150284fef9926d828f9903a6b9f5c56c10b01'}
SOURCES=('UF20_01','UF20_02','UF20_03','UF20_04','UF20_05')

def blob(p):
 d=p.read_bytes();return hashlib.sha1(f'blob {len(d)}\0'.encode()+d).hexdigest()

def independently_extract():
 pre=json.loads(PREREG.read_text());review=json.loads(REVIEW.read_text());meet=json.loads(MEET.read_text());signed=json.loads(SIGNED.read_text());sealed=json.loads(SEALED.read_text())
 assert pre['status']=='FROZEN_BEFORE_ANY_CROSS_CERTIFICATE_ALIGNMENT_EXECUTION'
 assert review['verdict']=='PASS_PREREGISTRATION_CLEAN__AUTHORIZED_TO_IMPLEMENT_AND_EXECUTE_ONCE'
 meet_by={r['source']:r for r in meet['source_summary']};signed_by={r['source']:r for r in signed['source_receipt']}
 assert set(meet_by)==set(SOURCES) and set(signed_by)==set(SOURCES)
 aw=sealed['aligned_witness'];panel=sealed['four_unadmitted_sources'];rows=[]
 for name in SOURCES:
  cells=meet_by[name]['meet_non_singleton_classes'];sr=signed_by[name];count=sr['nonidentity_exact_signed_automorphism_count']
  if name=='UF20_01':
   w=sr['unique_nonidentity_witness'];moves=w['sigma_moves'];moved=sorted(set(sum((list(x) for x in moves),[])))
   ok=(cells==[[7,10]] and count==1 and moved==[7,10] and w['epsilon_flips']==[] and aw['source']=='UF20_01' and aw['signed_exact_pair']==[7,10] and aw['epsilon_flips']==[] and aw['sealed_orbit_cell']==[7,10] and aw['existing_exact_transposition_true_pair']==[7,10])
   rows.append({'source':name,'meet_non_singleton_classes':cells,'signed_nonidentity_count':count,'signed_unique_pair':moved,'epsilon_flips':w['epsilon_flips'],'sealed_orbit_cell':aw['sealed_orbit_cell'],'alignment':'EXACT_FULL_ALIGNMENT' if ok else 'MISMATCH','aligned':ok})
  else:
   ok=(cells==[] and count==0 and name in panel['sources'] and panel['signed_nonidentity_automorphisms']==0 and panel['new_closure_from_signed_extension'] is False)
   rows.append({'source':name,'meet_non_singleton_classes':cells,'signed_nonidentity_count':count,'sealed_panel_total_nonidentity':panel['signed_nonidentity_automorphisms'],'alignment':'EMPTY_VS_IDENTITY_ONLY_ALIGNMENT' if ok else 'MISMATCH','aligned':ok})
 expected=pre['a_priori_expected_alignment'];all_aligned=all(r['aligned'] and r['alignment']==expected[r['source']]['expected'] for r in rows)
 verdict=pre['a_priori_outcome_rules']['fully_aligned_verdict'] if all_aligned else pre['a_priori_outcome_rules']['mismatch_verdict']
 return rows,all_aligned,verdict

def main(candidate_path):
 bindings={str(p.relative_to(ROOT)):blob(p)==sha for p,sha in EXPECTED.items()};assert all(bindings.values()),bindings
 c=json.loads(candidate_path.read_text().strip().splitlines()[-1]);rows,all_aligned,verdict=independently_extract()
 assert c['rows']==rows,(c['rows'],rows);assert c['all_aligned']==all_aligned;assert c['no_new_explanatory_witness']==all_aligned;assert c['verdict']==verdict
 rr=c['resource_receipt'];assert rr=={'sources_compared':5,'new_action_tests':0,'new_partition_computations':0,'solver_invocations':0,'portfolio_replays':0,'group_closure_computation':0,'group_searches':0,'new_feature_definitions':0,'new_graph_statistics':0,'new_solver_mechanisms':0,'new_carrier_mechanisms':0,'new_adapters':0,'new_quotients':0,'budget_raise':False}
 sf=c['scientific_firewall'];assert sf['P_VS_NP']=='OPEN' and sf['GENERAL_SAT_IN_P']=='NOT_PROVED' and sf['CONNECTED_MIXED_CORE_SOLVED']=='NO'
 return {'verified':True,'candidate_imported':False,'verdict':verdict,'all_aligned':all_aligned,'no_new_explanatory_witness':all_aligned,'sources_verified':5,'rows':rows}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--candidate-json',required=True);args=ap.parse_args();print(json.dumps(main(Path(args.candidate_json)),sort_keys=True,separators=(',',':')))
